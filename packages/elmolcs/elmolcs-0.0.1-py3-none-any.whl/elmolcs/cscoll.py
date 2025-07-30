# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 13:23:26 2022

Copyright (C) 2023 
@author: Anthony Jeseněk
"""

# Analytical expressions for cross sections 

import numpy as np
import numba as nb
import pandas as pd
from scipy.interpolate import interp1d
import functools
import re
from . import filehandler
from . import constants as co

hyperlogparam = {'N2':(-1.56,1.68,2.,1.35,-9.7), 'O2': (-1.07,0.6,1.4,0.8,-5.3)}
target2acos = {'N2':0.6052,'O2':0.5677,'NO':0.6039,'Ar':0.4533,'O':0.4875,'N':0.5546} # Fit from 10 keV to 1 GeV of average cosine 
target2amtcs = {'N2':0.417,'O2':0.3986,'NO':0.241,'Ar':0.303,'O':0.3944,'N':0.417}  # Fit from 10 keV to 1 GeV of momentum transfer CS (see IntDCS.py @ # Fit screening parameters for 1-term SRY) for O : fitted from Cox&Bonham (1967)
target2amtcs_low = {'N2':0.322,'O2':0.282,'NO':0.293,'Ar':0.193,'O':0.314,'N':0.358} # Fit from 10 eV to 1 GeV - // -

def to_latex(s,frac=True):
    s = s.replace('beta',r'\beta').replace('theta','\theta').replace('mu',r'\mu').replace('alpha',r'\alpha')
    s = s.replace('**','^')
    s = s.replace('*','').replace('np.log',r'\ln').replace('np.','\\')
    s = re.sub(r'(?<=[a-z])(\d)',r'^\1',s)
    s = re.sub(r'(?<![a-z])eta',r'\\eta',s)
    s = re.sub(r'\[([^\[\]]*)\]',r'_\1',s)
    s = re.sub(r'\(((?:[^()]*\([^()]*\)[^()]*)+)\)',r'\\left(\1\\right)',s)
    s = s.replace('0.5','/2')
    if frac:
        s = s.replace('1/',r'\dfrac{1}')
    return s
    
Ryd = co.Ryd
mc2 = co.me*co.c**2
Ryd_= Ryd/mc2
MeV = co.MeV
keV = co.keV
eV = co.eV
O = 4*np.pi*co.a0**2
o = 1e-20 # A² 
ach_ = co.alpha*co.c*co.h_

@nb.njit
def Ek2k_wave(Ek):
    Ek_ = Ek/mc2
    return Ek_*np.sqrt(1+2/Ek_)/co.alpha

@nb.njit
def lnBm(Ek,B): # Correct = 1/Ni § Ni (1/(ε2+B)² + (ε2+B)/(ε0-ε2)³) ln(ε2+B) dε2 in ln(#/Rydberg)
    B_ = B/Ryd
    Ek_B = Ek/B
    Em = (Ek+B)/Ryd*0.5
    # Ni = 1/B_ + 0.5/Ek_*(1-B_/Ek_)-2/(Ek_+B_)
    Ni = 1 + 0.5/Ek_B*(1-1/Ek_B)-2/(Ek_B+1)
    # lnBm = 1/B_+np.log(B_)*(1/B_+0.5/Ek_*(1-B/Ek)) + 0.5/Ek_-3/(Ek_+B_)-np.log(Em)/Em + np.log(Ek/B)/(4*Em)
    lnBm = 1+np.log(B_)*(1+0.5/Ek_B*(1-1/Ek_B)) + 0.5/Ek_B-3/(Ek_B+1)-2*np.log(Em)/(Ek_B+1) + np.log(Ek/B)/(4*(Ek_B+1))
    return lnBm/Ni
    #np.exp(lnBm)*Ryd
@nb.njit
def Cd(Ek,B,Q): # Dipole log coeff correction
    l_Q = 1/Q
    return (2*(np.log(B/Ryd)-lnBm(Ek,B)) +1-l_Q + (5*l_Q-3)*np.log(2))

@nb.njit
def interf(Ek,W,B): # cos(1/v ln((ε2+B)/(ε0-ε2)) = cos(1/v ln tan(θ) ) Interference term in Mott's scattering cross section
    return np.cos(np.sqrt(Ryd/(Ek+B))*np.log((W+B)/(Ek-W)))
@nb.njit
def interfrel(Ek,W,B):
    g = 1+(Ek+B)/mc2
    beta = np.sqrt(1-1/g**2)
    return np.cos(co.alpha/beta*((g+1)/(2*g**2))**0.25*np.log((W+B)/(Ek-W)))

def ensurepos(B,U,N,Q):
    B_ = B/mc2
    beta2 = 1-1/(1+B_)**2
    D = Cd(MeV,B,Q)
    Beta = np.log(beta2/(1-beta2))-beta2-np.log(2*B_)

class Ionisation:

    def loadBUN(target,idx=slice(None,None),transposed=False,revert=False):
        orb = co.Constants.ORB_MOLC[target]
        B,U,N = np.array(orb['B']),np.array(orb['U']),np.array(orb['N'])
        if revert: idx = slice(None,None,-1)
        if(transposed):
            return B[idx,None],U[idx,None],N[idx,None]
        else:
            return B[idx],U[idx],N[idx]            

    def Moller(Ek,Ek_minion = keV):
        if(Ek<=Ek_minion):
            print('Moller scattering under relativistic limit, higher errors induced : D_Ek = ', (Ek_minion-Ek)*eV, ' eV' )
            Ek_minion = Ek*0.999
        gamma = Ek/mc2 + 1
        v_c = np.sqrt(gamma**2-1)/gamma
        kappa = 2*np.pi*co.r_0e**2*mc2/v_c**2
        sigma_i = kappa*(1/Ek_minion - 1/(Ek-Ek_minion) + 0.5*(Ek-2*Ek_minion)/(mc2+Ek)**2 + mc2*(mc2+2*Ek)/(Ek*(mc2+Ek)**2) * np.log(Ek_minion/(Ek-Ek_minion)))
        return sigma_i

    def Moller_bind(Ek,B,N=2):
        Ek_ = Ek/mc2
        B_ = B/mc2
        Ek_B = Ek/B
        beta_k2 = 1-1/(1+Ek_)**2

        norm = O*co.alpha**2*N*Ryd/B/beta_k2 # Bethe norm
        if Ek<B: return 0
        else: return norm*(1-1/Ek_B - (np.log(Ek_B)*(1+2*Ek_)/(Ek_B+1)-B_**2*(Ek_B-1)/2)/(1+Ek_)**2)

    def dOpal(W,Ek,B,Bnorm=1):
        if(np.isscalar(B)): 
            B = np.array([B])
            Bnorm = np.array([1])
        if(np.isscalar(Ek)): Ek = np.array([[Ek]])
        if(np.isscalar(W)): W = np.array([[[W]]])
        W = W.reshape(1,len(W),1)
        Ek = Ek.reshape(len(Ek),1,1)
        terms = np.pi*co.e**4*Bnorm/(Ek*(B+W)**2)
        return np.sum(terms,axis=-1)

    @nb.vectorize(['float64(float64,float64,float64)'])#,'(n),(),()->(n)')
    def _w_Opal(Ek,B,E0):
        Ek_ = (Ek-B)/(2*E0)
        return 0.5*E0*np.log(1+Ek_**2)/np.arctan(Ek_)
    @nb.jit
    def w_Opal(Ek,B,E0):
        res = Ionisation._w_Opal(Ek,B,E0)
        res[Ek<B] = 0 # np.nan will not allow to compute the stopping power for lower value
        return res

    def genRBEQ(target,Q,shells=False,BUN=None):
        if(BUN is None):
            B,U,N = Ionisation.loadBUN(target,transposed=True)
        else: 
            B,U,N = BUN
            B = B.reshape((B.size,1))
            U = U.reshape((U.size,1))
            N = N.reshape((N.size,1))
        Q = np.array(Q)
        if Q.shape: Q = Q.reshape((Q.size,1))
        Bm = np.min(B)
        norm = Ionisation.RBEB_norm
        B_ = B/mc2
        BU_ = B_+U/mc2
        # beta_u2 = 1-1/(1+U/mc2)**2
        # beta_b2 = 1-1/(1+B_)**2
        # beta_ub2 = beta_u2+beta_b2
        D = Cd(MeV,B,Q)
        N_2B = N/(2*B_)
        log2B = np.log(2*B_)#-D
        @nb.njit(['float64[:,:](float64[:])'])
        def _rbeb(Ek):
            # pre,Ek_B,Ek_1,B2,Beta = _RBEB(Ek,B,U,N)
            Ek_ = Ek/mc2
            mask = Ek_>B_
            Ek_B = Ek/B 
            beta_k2 = 1-1/(1+Ek_)**2
            beta2 = 1-1/(1+Ek_+BU_)**2
            pre = mask*N_2B/beta2
            Beta = np.log(beta_k2/(1-beta_k2))-beta_k2-log2B+D#Cd(Ek,B,Q)
            B2 = (B_/(1+Ek_+B_))**2
            Ek_1 = (1+2*(Ek_+B_))/((1+Ek_B)*(1+Ek_+B_)**2)

            # res = pre*((Q*0.5*Beta*(1-4/(Ek_B+1)**2)) + (2-Q)*(1-1/Ek_B - np.log(Ek_B)*Ek_1+B2*(Ek_B-1)/2)) # unsymmetrised version
            res = pre*((Q*0.5*Beta*(1-1/Ek_B**2)) + (2-Q)*(1-1/Ek_B - np.log(Ek_B)*Ek_1+B2*(Ek_B-1)/2)) # symmetrised version
            # res[np.isnan(res)] = 0
            return res
        if shells:
            # @nb.jit not faster with numba
            def rbeb(Ek):
                nonzero = Ek>Bm
                res = np.zeros((len(B),len(Ek)))
                if(np.any(nonzero)):
                    cs = _rbeb(Ek[nonzero])
                    cs[cs<0] = 0
                    cumcs = np.cumsum(cs,axis=0)
                    res[:,nonzero] = cumcs/cumcs[[-1],:]
                return res
            wrap = rbeb
        else:
            @nb.njit(['float64[:](float64[:])'])
            def rbeb(Ek):
                return norm*_rbeb(Ek).sum(axis=0)
            def wrap(Ek): # avoid futile calculations when not ionisable
                # Ek[Ek==0] = eV
                nonzero = Ek>Bm
                res = np.zeros(Ek.shape)
                if(np.any(nonzero)):
                    res[nonzero] = rbeb(Ek[nonzero])
                return res           
        return wrap

    # Convention : [orbitals, energies, secondary] or  [B, Ek, W]

    def RBE(Ek,B,U=np.array([[0]]),N=np.array([[2]]),Q=1,orbital='sum',absolute=True,io=1,bad=False,**kwargs): # Relativistic Binary Encounter Bethe model (Kim et al. 2000)
        ''' RBE model Cross Section for ionisation
        Parameters:
            Ek : Energies (eV)
            B : Orbital binding energies (eV) [array] 
            U : Orbital kinetic energy (eV) [array]
            N : Orbital occupation number [array]
            Q : Quadrupole coefficient
            orbital : output 'sum','cum' or any index array
            absolute : if True returns absolute norm, if False returns relative to norm
            io : iota value in [0.5,1] for energy sharing in binary encounter '''
        if(np.array(Q).shape): Q = Q.reshape((Q.size,1))
        if not io: res = Ionisation._RBEB(Ek,B.reshape((B.size,1)),U.reshape((U.size,1)),N.reshape((N.size,1)),Q)[0]
        elif(bad): 
            res,pre,Ek_B,Ek_1,B2,Beta,a = Ionisation._RBEQ(Ek,B.reshape((B.size,1)),U.reshape((U.size,1)),N.reshape((N.size,1)),Q)
            Beta += -Cd(MeV,B,Q)+Cd(Ek,B,Q)
            res = pre*((Q*0.5*Beta*(1-1/Ek_B**2)) + (2-Q)*(1-1/Ek_B - np.sin(a*np.log(Ek_B))/a*Ek_1+B2*(Ek_B-1)/2))
        elif io==1: res = Ionisation._RBEQ(Ek,B.reshape((B.size,1)),U.reshape((U.size,1)),N.reshape((N.size,1)),Q)[0]
        else: res = Ionisation._RBE(Ek,B.reshape((B.size,1)),U.reshape((U.size,1)),N.reshape((N.size,1)),Q,io,**kwargs)[0]
        res[np.isnan(res)] = 0
        if absolute: norm = Ionisation.RBEB_norm
        else: 
            norm = np.sum(res,axis=0,keepdims=True)
            norm[norm!=0] = 1/norm[norm!=0]
        if(orbital=='sum'):
            return norm * np.sum(res,axis=0)
        elif(orbital=='cumsum'):
            cs = np.cumsum(norm*res,axis=0)
            return cs#/cs[:,[-1]]
        else:
            if(orbital=='all'): orbital = slice(None,None)
            return norm * res[orbital,:]

    def BEB(Ek,B,U,N,Q=1):
        Ek_B = Ek/B
        return O*N*(Ryd/B)**2/(Ek_B+U/B+1)*(Q*np.log(Ek_B)/2*(1-1/Ek_B**2)+(2-Q)*(1-1/Ek_B-np.log(Ek_B)/(Ek_B+1)))

    RBEB_norm = O*co.alpha**4

    # @nb.vectorize(['(float64,float64,float64,float64,float64)'],'(n),(m),(m),(m),(p)')
    # @nb.njit
    def _RBEQ_aux(Ek,B,U,N,Q,W=np.array([])): # Relativistic Binary Encounter Bethe model (Kim et al. 2000)
        Ek = np.array(Ek)
        if(not Ek.shape): Ek = np.array([[Ek]])
        if(np.isscalar(W)): 
            W = np.asarray([[[W]]])
            lenW = 1
        elif(len(W.shape)==2):
            assert W.shape[0] == len(Ek)
            lenW = W.shape[1]
        else: lenW = len(W)
        Ek = Ek.reshape((1,len(Ek))+(lenW!=0)*(1,))
        
        if(lenW>0):
            if(len(W.shape)==1): W = W.reshape(1,1,W.size)
            elif(len(W.shape)==2): W = W.reshape(1,*W.shape)
            w = W/B
            res = Ionisation._RBEQ(Ek,B,U,N,Q)
            return res+(w,)#(norm,pre,Ek_B,Ek_1,B2,Beta,w)
        else: 
            return Ionisation._RBEQ(Ek,B,U,N,Q)

    # @nb.njit(['UniTuple(float64[:,:],7)(float64[:],float64[:,:],float64[:,:],int32[:,:],float64)',
    #           'UniTuple(float64[:,:],7)(float64[:],float64[:,:],float64[:,:],float64[:,:],float64)',
    #           'UniTuple(float64[:,:],7)(float64[:],float64[:,:],float64[:,:],float64[:,:],float64[:,:])',
    #           'UniTuple(float64[:,:],7)(float64[:],float64[:,:],float64[:,:],int32[:,:],float64[:,:])',
    #           'UniTuple(float64[:,:],7)(float64[:,:],float64[:,:],float64[:,:],int32[:,:],float64)',
    #           'UniTuple(float64[:,:,:],7)(float64[:,:,:],float64[:,:,:],float64[:,:,:],int32[:,:,:],float64)',])
    @nb.njit
    def _RBEB(Ek,B,U,N,Q): # This is the original RBEB model with inaccuracies
        mask = Ek>B
        
        Ek_ = Ek/mc2
        Ek_B = Ek/B
        B_ = B/mc2
        beta_u2 = 1-1/(1+U/mc2)**2
        beta_b2 = 1-1/(1+B_)**2
        beta_k2 = 1-1/(1+Ek_)**2
        pre = mask*(N/((beta_k2+beta_u2+beta_b2)*2*B_))
        
        Beta = np.log(beta_k2/(1-beta_k2))-beta_k2-np.log(2*B_)
        B2 = (B_/(1+Ek_/2))**2
        Ek_1 = (1+2*Ek_)/((1+Ek_B)*(1+Ek_/2)**2)

        res = pre*((Q*0.5*Beta*(1-1/Ek_B**2)) + (2-Q)*(1-1/Ek_B - np.log(Ek_B)*Ek_1+B2*(Ek_B-1)/2)) # Kim et al. introduced a non-justified symmetrisation of the dipole term
        # res = pre*((Q*0.5*Beta*(1-4/(Ek_B+1)**2)) + (2-Q)*(1-1/Ek_B - np.log(Ek_B)*Ek_1+B2*(Ek_B-1)/2)) # correct unsymmetrised version
        # res[np.isnan(res)] = 0
        return (res,pre,Ek_B,Ek_1,B2,Beta,Ek_1)

    # @nb.njit(['UniTuple(float64[:,:],7)(float64[:],float64[:,:],float64[:,:],int32[:,:],float64[:,:])',
    #           'UniTuple(float64[:,:],7)(float64[:],float64[:,:],float64[:,:],int32[:,:],float64)',
    #           'UniTuple(float64[:,:],7)(float64[:],float64[:,:],float64[:,:],float64[:,:],float64[:,:])',
    #           'UniTuple(float64[:,:],7)(float64[:],float64[:,:],float64[:,:],float64[:,:],float64)',
    #           'UniTuple(float64[:,:],7)(float64[:,:],float64[:,:],float64[:,:],int32[:,:],float64[:,:])',
    #           'UniTuple(float64[:,:,:],7)(float64[:,:,:],float64[:,:,:],float64[:,:,:],int32[:,:,:],float64)',
    #           'UniTuple(float64[:,:,:],7)(float64[:,:,:],float64[:,:,:],float64[:,:,:],int32[:,:,:],float64[:,:,:])',
    #           'UniTuple(float64[:,:,:],7)(float64[:,:,:],float64[:,:,:],float64[:,:,:],float64[:,:,:],float64[:,:,:])'])
    @nb.njit
    def _RBEQ(Ek,B,U,N,Q): # about two times faster than _RBEB_aux
        mask = Ek>B
        
        Ek_ = Ek/mc2
        Ek_B = Ek/B
        B_ = B/mc2
        # beta_u2 = 1-1/(1+U/mc2)**2
        # beta_b2 = 1-1/(1+B_)**2
        beta2 = 1-1/(1+Ek_)**2
        gamma = (1+Ek_+U/mc2+B_)
        beta_a2 = 1-1/gamma**2
        pre = mask*(N/((beta_a2)*2*B_))
        D = Cd(MeV,B,Q)
        Beta = np.log(beta2/(1-beta2))-beta2-np.log(2*B_)+D
        B2 = (B_/gamma)**2
        Ek_1 = (2*gamma-1)/((1+Ek_B)*gamma**2)
        # l_vrel = co.alpha/np.sqrt(beta_a2)*((gamma+1)/(2*gamma**2))**0.25
        l_vrel=1

        res = pre*((Q*0.5*Beta*(1-1/Ek_B**2)) + (2-Q)*(1-1/Ek_B - np.log(Ek_B)*Ek_1+B2*(Ek_B-1)/2)) # symmetrisation of the dipole term
        # res = pre*((Q*0.5*Beta*(1-1/Ek_B**2)) + (2-Q)*(1-1/Ek_B - np.sin(l_vrel*np.log(Ek_B))/l_vrel*Ek_1+B2*(Ek_B-1)/2)) # symmetrisation of the dipole term and interference
        # res = pre*((Q*0.5*Beta*(1-4/(Ek_B+1)**2)) + (2-Q)*(1-1/Ek_B - np.log(Ek_B)*Ek_1+B2*(Ek_B-1)/2)) # unsymmetrised version
        # res[np.isnan(res)] = 0
        return (res,pre,Ek_B,Ek_1,B2,Beta,l_vrel)

    def _RBE(Ek,B,U,N,Q,io=1,nd=2,sym=True,interf=1): # about two times faster than _RBEB_aux
        ''' io : parameter for energy partition
            nd : exponent of differential DOS '''
        mask = Ek>B
        
        Ek_ = Ek/mc2
        Ek_B = Ek/B
        B_ = B/mc2
        beta_u2 = 1-1/(1+U/mc2)**2
        beta_b2 = 1-1/(1+B_)**2
        beta_k2 = 1-1/(1+Ek_)**2
        pre = mask*(N/((beta_k2+beta_u2+beta_b2)*2*B_))
        if type(interf) in [float,int]:
            l_vrel = 1 
            phi = interf*np.log((Ek_B-(1-io))/io)
        else:
            l_vrel = co.alpha/np.sqrt(beta_k2+beta_b2+beta_u2)
            phi = np.sin(l_vrel*np.log((Ek_B-(1-io))/io))/l_vrel
        
        Beta = np.log(beta_k2/(1-beta_k2))-beta_k2-np.log(2*B_)
        B2 = (B_/(1+Ek_))**2 
        Ek_1 = (1+2*Ek_)/((1+Ek_B)*(1+Ek_)**2) 

        if sym: res = pre*((Q*(nd-1)/nd*Beta*(1-1/Ek_B**nd)) + (2-Q)*(1-io/(Ek_B-(1-io)) - io*phi*Ek_1+B2*(Ek_B-1)/2)) # symmetrised version
        else: res = pre*((Q*(nd-1)/nd*Beta*(1-(2/(Ek_B+1))**nd)) + (2-Q)*(1-io/(Ek_B-(1-io)) - io*phi*Ek_1+B2*(Ek_B-1)/2)) # unsymmetrised version
        res[np.isnan(res)] = 0
        return (res,pre,Ek_B,Ek_1,B2,Beta,l_vrel)

    def dRBEQ(W,Ek,B,U=np.array([0]),N=np.array([2]),Q=1,orbital='sum',normed=True,relative=False,primary=False):
        ''' Singly differential cross section of impact ionisation
        Parameters:
        -----------
            W : array[float] - Electron secondary energy
            Ek : array[float] - Electron primary energy
            B : array[float] - Binding energy of orbital
            U : kinetic energy of orbital
            N : orbital occupation number (does not have to be integer)
            Q : Ni/N ionisation dipole oscillator strength ratio (to discrete excitations)
            orbital : 'all', index list, slice or 'sum'
            normed : absolute value of DCS (default) ? or normalised ?
            relative : is W given in relative units to (Ek-B/2) ? (no)
            primary : are the energies of the primary electron to be included in the normalistion ? (no)
        Returns:
        --------
            SDCS matrix array [orbital, Ek, W] shape
        '''
        if(relative): 
            if(orbital=='sum'): W = np.multiply.outer((Ek-min(B))/2,W) # [Ek, W] shape
            else: W = np.multiply.outer(np.subtract.outer(Ek,B).T/2,W) # [B, Ek, W] shape
        if(np.array(Q).shape): Q = Q.reshape((Q.size,1,1))
        B = B.reshape((B.size,1,1))
        norms,pre,Ek_B,Ek_1,B2,Beta,a,w = Ionisation._RBEQ_aux(Ek,B,U.reshape((U.size,1,1)),N.reshape((N.size,1,1)),Q,W)
        if primary: # include primary energies > (Ek-B)/2
            primask = (w>(Ek_B-1)*0.5+1e-9)&(w<=(Ek_B-1))
            w[primask] = ((Ek_B-1)-w)[primask]
        res = np.asarray(w<=(Ek_B-1)*0.5+1e-9,dtype=float) # fight against roundoff errors
        # gamma = (1+(Ek+U.reshape((U.size,1,1)))/mc2+B_)
        # beta_a2 = 1-1/gamma**2
        # phi = np.cos(a*np.log((w+1)/(Ek_B-w)))
        #Q = Ni/N
        df_dw = Q*(1/(w+1)**2+(w+1)/(Ek_B-w)**3) # symmetrised dipole
        # df_dw = Q/(w+1)**2 # original dipole term
        mask = res>0
        # division by B ensures that we have § dσ/dε dε = σ instead of in dw (reduced secondary energy w = ε/B)
        res[mask] = ((Beta*df_dw/(w+1) + (2-Q)*(1/(w+1)**2 + 1/(Ek_B-w)**2 + B2 - (1/(w+1)+1/(Ek_B-w))*Ek_1))/B)[mask] 
        res[res<0] = 0
        if normed: norm = Ionisation.RBEB_norm
        if(orbital=='sum'):
            if(not normed): 
                norm = np.sum(norms,axis=0) 
                norm[norm!=0] = 1/norm[norm!=0]
            return norm*np.sum(pre*res,axis=0)
        else:
            if(orbital=='all'): orbital = slice(None,None)
            if(not normed):
                norm = norms
                norm[norm!=0] = 1/norm[norm!=0]
            # else: norm = norm #*pre[orbital,:,:] #[orbital,np.arange(res.shape[1]),:]
            return norm*(pre*res)[orbital,:,:] #np.arange(res.shape[1]),:]

    def cumRBEQ(W,Ek,B,U=np.array([0]),N=np.array([2]),Q=1,orbital='sum',normed=False,relative=False):
        if(relative): # Distinguish case when orbitals are summed and when they are separate
            if(orbital=='sum'): W = np.multiply.outer((Ek-min(B))/2,W) # [Ek, W] shape
            else: W = np.multiply.outer(np.subtract.outer(Ek,B).T/2,W) # [B, Ek, W] shape
        if(np.array(Q).shape): Q = Q.reshape((Q.size,1,1))
        norms,pre,Ek_B,Ek_1,B2,Beta,a,w = Ionisation._RBEQ_aux(Ek,B.reshape((B.size,1,1)),U.reshape((U.size,1,1)),N.reshape((N.size,1,1)),Q,W)
        # w[w>(Ek_B-1)*0.5] = (Ek_B-1)*0.5
        c1 = Beta/2*Q*(1-1/(w+1)**2 + 1/(Ek_B-w)**2-1/Ek_B**2) # Latter term comes from symmetrised version
        c2 = (1-1/(w+1) + 1/(Ek_B-w)-1/Ek_B) + w*B2
        c3 = (np.log((w+1)*Ek_B/(Ek_B-w)))*Ek_1
        # c3 = (np.sin(a*np.log((w+1)*Ek_B/(Ek_B-w)))/a)*Ek_1
        # res = pre.copy()
        res = pre*(c1+(2-Q)*(c2-c3))
        neg = res<0
        if np.any(neg): 
            # This is due to too strong Cd coef which gives a negative CS near threshold for some partial CS
            # We correct this by taking a uniform distribution in secondary energies which is the default shape near threshold
            res[neg] = np.abs((w/w[...,[-1]]*norms)[neg])
            norms = np.abs(norms)
        # res[res<0] = 0
        # norms = pre*((Q*0.5*Beta*(1-4/(Ek_B+1)**2)) + (2-Q)*(1-1/Ek_B - np.log(Ek_B)*Ek_1+B2*(Ek_B-1)/2)) # correct unsymmetrised version
        if normed: norm = Ionisation.RBEB_norm
        res[res>norms] = (norms*(res>norms))[res>norms]
        if(orbital=='all'): orbital = slice(None,None)
        if(type(orbital) is str):
            if(not normed):
                norm = np.__dict__[orbital](norms,axis=0)
                norm[norm!=0] = 1/norm[norm!=0]
            return norm*np.__dict__[orbital](res,axis=0)
        else:
            if(not normed):
                norm = norms[orbital,:,:]#,np.arange(res.shape[1]),:]
                norm[norm!=0] = 1/norm[norm!=0]
            return norm*res[orbital,:,:]#,np.arange(res.shape[1]),:] # so that each orbital is correctly selected for each energy

    def w_RBEQ(Ek,B,U=np.array([0]),N=np.array([2]),Q=1,orbital='sum'): # average secondary electron energy, checked
        B = B.reshape((B.size,1))
        if(np.array(Q).shape): Q = Q.reshape((Q.size,1))
        norm,pre,Ek_B,Ek_1,B2,Beta,a = Ionisation._RBEQ(Ek,B.reshape((B.size,1)),U.reshape((U.size,1)),N.reshape((N.size,1)),Q)
        # norm = pre*((Q*0.5*Beta*(1-1/Ek_B**2)) + (2-Q)*(1-1/Ek_B - np.log(Ek_B)*Ek_1+B2*(Ek_B-1)/2)) # symmetrisation of the dipole term and interference
        # w_mean = pre*B*((2-Q)*((2+(1+2*Ek_)/(1+Ek_/2)**2)*np.log((Ek_B+1)/2) - (1+(1+2*Ek_)*Ek_B/((1+Ek_B)*(1+Ek_/2)**2))*np.log(Ek_B)) + 0.5*(Ek_B-1)**2*(0.25*(2-Q)*B_**2/(1+Ek_/2)**2 + Q*Beta/(Ek_B*(Ek_B+1))))
        loss = pre*B*(Q*(1+0.5/Ek_B*(1-1/Ek_B)-2/(Ek_B+1))*Beta + (2-Q)*(np.log((Ek_B+1)**2/(4*Ek_B)) + 1 - 1/Ek_B + B2*0.5*((Ek_B+1)**2/4-1) - np.log(2*Ek_B/(1+Ek_B))*Ek_1*(1+Ek_B)))
        if(orbital=='sum'):
            w_mean = np.sum(loss-B*norm,axis=0)
            cs = np.sum(norm,axis=0) # cs = Ionisation.RBEB(Ek,B,U,N,orbital='sum')
        else:
            w_mean = loss-B*norm
            cs = norm
        # w_mean = np.sum(pre*B*((2-Q)*((2+Ek_1*(Ek_B+1))*np.log((Ek_B+1)/2) - (1+Ek_1*Ek_B)*np.log(Ek_B)) + 0.5*(Ek_B-1)**2*(0.25*(2-Q)*B2 + Q*Beta/(Ek_B+1)**2)),axis=0)
        # wm = cs.copy()
        cs[cs>0] = w_mean[cs>0]/cs[cs>0]
        return cs

    def B_RBEQ(n,B,N,Q): # -n th moment in dipole oscillator strength distribution : § df/dW  * 1/W^n dW
        return N*Q/((n+1)*(0.5*B/Ryd)**(n+1))

    def M_RBEQ(B,N,Q): return Q*N*Ryd/(2*B) # Checked
    def lnc_RBEQ(B,N,Q): return (3*(1-Q)+(5-3*Q)*np.log(2))/Q - np.log(4*B/Ryd) # Checked

Ionisation.RBEB = functools.partial(Ionisation.RBE,io=False)
            
class Excitation:

    def genexc(Eth,asymp,c,eq=''):
        if(asymp==0 or 'a' in eq): return Excitation.genA(Eth,c,eq)
        else: return Excitation.genF(Eth,asymp,c,eq)

    def genA(Eth,c,eq='a',rel=True):
        c1,c2,c3,c4 = c[:4]
        if(len(c)==5): Eth = c[4] # adjusted threshold
        Eth*=eV
        m = Eth/Ryd        
        p0 = O*c1/(m*c4)
        p2 = c2
        p3 = 4*m*c3
        p4 = c4
        if(len(c)==6): # 'a6' or fln6
            c5,c6 = c[4:6]
            p0 = O*c1/(m*c4)
            p6 = c6/m
            e = c5*c4+1
            @nb.njit
            def allowexc(Ek):
                x = (Ek/Eth-1)
                x[x<0]=0
                return p0*((x+1)**c5-1)**c4/(x+p2)**e*(np.log(p3*(x+1))+p6/(x+p2))
        else:
            if(rel): # relativistic
                @nb.njit
                def allowexc(Ek):
                    gamma2 = (1+Ek/mc2)**2
                    beta2 = (1-1/gamma2)
                    beta2[Ek<=Eth] = 0
                    x = (0.5*mc2*beta2/Eth-1)
                    x[x<0]=0                    
                    return p0/(x+p2)*(np.log((x*p3*gamma2)**p4+1))#-beta2)
            else:
                @nb.njit
                def allowexc(Ek):
                    x = (Ek/Eth-1)
                    x[x<0]=0
                    return p0/(x+p2)*np.log((x*p3)**p4+1)

        return allowexc

    def genF(Eth,asymp,c,eq='f'):
        assert re.match(r'f\d?[lmo]?(\+fr)?',eq), 'Equation %s unknown in this database'%eq
        # if(eq=='f0m'):
        #     c = list(c)
        #     Eth = c.pop(2) # this is the effective threshold for the onset of the cross section
        Eth*=eV
        m = (Eth/Ryd)**asymp
        if eq=='f0m': # use eq f3 but with a shifted threshold
            c = list(c)
            Eth = c.pop(2)*eV 
        # if('l' in eq):
        #     c1,c2,c3,c4 = c
        #     e = c4*c3+asymp
        #     p0 = c1*O/m
        #     @nb.njit
        #     def forbidexc(Ek):
        #         x = (Ek/Eth-1)
        #         x[x<0]=0
        #         return p0*((x+1)**c3-1)**c4/(x**e+c2) # this ruined all my simulations !
        if(len(c)==3):
            c1,c2,c4 = c
            e = c4+asymp
            p0 = c1*O/m
            @nb.njit
            def forbidexc(Ek):
                x = (Ek/Eth-1)
                x[x<0]=0
                return p0*x**c4/(x+c2)**e
        elif(len(c)==4):
            c1,c2,c3,c4 = c
            if(c3==1): return Excitation.genF(Eth,asymp,(c1,c2,c4),eq='f3')                
            e = c4*c3+asymp
            p0 = c1*O/m
            if('l' in eq):
                @nb.njit
                def forbidexc(Ek):
                    x = (Ek/Eth-1)
                    x[x<0]=0
                    return p0*((x+1)**c3-1)**c4/((x/c2)**e+1)
            else:
                @nb.njit
                def forbidexc(Ek):
                    x = (Ek/Eth-1)
                    x[x<0]=0
                    return p0*((x+1)**c3-1)**c4/(x+c2)**e
        elif(len(c)==5):
            c1,c2,c3,c4,c5 = c
            p0 = O*c1/m * c5**c3
            e = c4+c3+asymp
            @nb.njit
            def forbidexc(Ek):
                x = (Ek/Eth-1)
                x[x<0]=0
                return p0*x**c4*((x/c5)**c3+1)/(x+c2)**e
        elif(len(c)==6):
            c1,c2,c3,c4,c5,c6 = c
            if(c3==1): return Excitation.genF(Eth,asymp,(c1,c2,c4,c5,c6),eq='f5o')
            p0 = O*c1/m * c5**c6
            e = c6+c4*c3+asymp
            @nb.njit
            def forbidexc(Ek):
                x = (Ek/Eth-1)
                x[x<0]=0
                return p0*((x+1)**c3-1)**c4*((x/c5)**c6+1)/(x+c2)**e
        elif(len(c)==7): # Resonance
            o,b,e,G , c1,c2,c4 = c
            r = e*eV
            g = e*2/G
            cos = np.cos(2*b)
            sin = np.sin(2*b)
            d = asymp+c4
            p0 = c1*O/m
            @nb.jit
            def forbidexc(Ek): # with resonance
                x = Ek/Eth-1
                x[x<0] = 0 # zero values for energies below threshold
                # X = 2*(x/eV-e)/G 
                X = g*(Ek/r-1)           
                return p0*x**c4/(x+c2)**d * (1 + o*(cos-sin*X)/(X**2+1))
        else:
            raise RuntimeError('Wrong number (%d) of parameters for %s'%(len(c),eq))
        return forbidexc
    
    def allowed(Ek,Eth,c): pass

    def forbidden(Ek,Eth,asymp,c): pass

class Elastic:    

    def mag(Ek,Z=1): # Relativistically correct for coulomb scattering : (Z/mc² γ β²)²
        E = Ek+mc2
        beta2 = 1-(mc2/E)**2
        return (Z/(beta2) * ach_/E)**2 # Greiner&Reinhardt (Quantum Electrodynamics 2009 - 3.39 pg. 89 [103/461])
        # p = co.me*gamma*v
        # return (Z*co.e**2/(4*np.pi*co.eps0*co.me*v**2))**2 # cf. Center (1954), Sakurai, Olsen, etc. factor 2 in denominator only for sin(theta/2) form
    def mag2pi(Ek,Z=1): return 2*np.pi*Elastic.mag(Ek,Z)

    # MERT momentum transfer : Morrison et al. (1997) eq.(19) but not precise enough

    def Low(Ek,A,c,a0,a2=0,Q=0): # MERT with A = scattering length and c = effective range radius
        # k = Ek2k_wave(Ek)
        Ek_ = Ek/Ryd # = k²
        C = (np.pi*a0/A)**2/8 + 8*a0/3*np.log(1.23*np.sqrt(a0)) + 2*np.pi*np.sqrt(a0)/3 * (A-a0/A) - A**2 + A*c 
        # return O*A**2*(1+2*np.pi*alpha/(3*A)*k + 8*alpha/3 * k**2*np.log(k) + C*k**2)
        return O*A**2 * (1 + 4/45*(Q/A)**2  + 2*np.pi/3 * (a0/A + a2*Q/(30*A**2))*np.sqrt(Ek_) + 4*a0/3 * Ek_*np.log(Ek_) + C*Ek_) # Morrison 1988 p. 105

    def LowMTCS(Ek,A,c,a0,a2=0,Q=0): # MERT for momentum transfer
        Ek_ = Ek/Ryd
        return O*A**2*(1+ 4*np.pi*a0/(5*A)*np.sqrt(Ek_) + 4*a0/3*Ek_*np.log(Ek_))

    def gen_Low(target,A,c):
        alpha = co.Constants.POL_MOLC[target]
        a0 = alpha[0]
        if(len(alpha)>1): a2 = alpha[1]
        else: a2 = 0
        Q = co.Constants.Q_MOLC.get(target,0)
        c0 = 1 + 4/45*(Q/A)**2
        c1 = 2*np.pi/3 * (a0/A + a2*Q/(30*A**2))
        c2 = (np.pi*a0/A)**2/8 + 8*a0/3*np.log(1.23*np.sqrt(a0)) + 2*np.pi*np.sqrt(a0)/3 * (A-a0/A) - A**2 + A*c 
        c2ln = 8*a0/3
        norm = O*A**2
        @nb.njit
        def elow(Ek):
            Ek_=Ek/Ryd
            return norm * (c0 + c1*np.sqrt(Ek_) + Ek_*(c2+c2ln*np.log(Ek_)) )
        return elow

    def fit_Born(Ek,A,b,c,D=0,d=0,rel=True): # Born approximation for fitting elastic scattering
        if rel: 
            # remember that screened potential gives a ((2 k.a)/( mc² γ β²))² /2 coefficient on the DCS
            # This results after calculation in a 2/v² = 2/( c² β²) dependence
            gamma2 = (1+(Ek+D*eV)/mc2)**2
            beta2 = 1-1/gamma2
            R_Ek = co.alpha**2/(beta2*gamma2)
            gR_Ek = co.alpha**2/(beta2)
        else: gR_Ek = R_Ek = 1/(Ek/Ryd+D)
        return O*A*gR_Ek*np.abs(1+b*R_Ek+c*R_Ek**2)

    def Born(Ek,A,B,C,D=0,rel=True): # Born expansion for elastic scattering from Inokuti&McDowell (1974) eq.(13)
        if rel: 
            # remember that screened potential gives a ((2 k.a)/( mc² γ β²))² /2 coefficient on the DCS
            # This results after calculation in a 2/v² = 2/( c² β²) dependence
            gamma2 = (1+(Ek+D*eV)/mc2)**2
            beta2 = 1-1/gamma2
            R_Ek = co.alpha**2/(beta2*gamma2)
            gR_Ek = co.alpha**2/(beta2)
        else: gR_Ek = R_Ek = 1/(Ek/Ryd+D)
        return np.pi*co.a0**2*gR_Ek*(A+B*R_Ek+C*R_Ek**2)

    def Bornln(Ek,A,B,C,a=0,rel=True): # Born expansion for elastic scattering from Inokuti&McDowell (1974) eq.(13)
        if rel: 
            # remember that screened potential gives a ((2 k.a)/( mc² γ β²))² /2 coefficient on the DCS
            # This results after calculation in a 2/v² = 2/( c² β²) dependence
            gamma2 = (1+Ek/mc2)**2
            beta2 = 1-1/gamma2
            R_Ek = co.alpha**2/(beta2*gamma2)
            gR_Ek = co.alpha**2/(beta2)
        else: 
            gR_Ek = R_Ek = 1/(Ek/Ryd)
        return np.pi*co.a0**2*gR_Ek*(A+B*R_Ek+C*R_Ek*np.log(1+4*a**2/R_Ek))

    def gen_Born(target,ABC=None,D=0): # Jain&Baduja(1992) eq.18
        if ABC is None: A,B,C,D = co.Constants.Born[target]
        else: A,B,C = ABC
        norm = np.pi*co.a0**2
        d = D*eV
        a2 = co.alpha**2
        def fn(Ek):
            # R_Ek = Ryd/Ek
            gamma2 = (1+(Ek+d)/mc2)**2
            beta2 = 1-1/gamma2
            gR_Ek = a2/beta2
            R_Ek = gR_Ek/gamma2
            return norm*gR_Ek*(A+B*R_Ek+C*R_Ek**2)
        return fn

    def gen_Mott_Relativistic(target): # See Quantum Electrodynamics, Greiner and Reinhardt, pg. 86 (103.pdf)
        Z = co.Constants.MOLCS[target]
        mZ = np.linalg.norm(Z)
        Z = Z[0]
        a = 1.195*(Z/(Z-1))**(2/3)/Z**(1/3) if Z!=1 else 0.885/(Z**(1/3)) # Berkes 1941 and Fermi radius
        def fn(Ek): # Verified
            k = Ek2k_wave(Ek)
            eta = 1/(2*k*a)**2
            beta2 = 1-1/(1+Ek/mc2)**2 # β² = 1-1/γ²
            return Elastic.mag2pi(Ek,mZ)*(1/(2*eta*(1+eta))-beta2*0.5*(np.log(1+1/eta)-1/(1+eta)))
        return fn

# 4π a0²/ε (A+B/ε+C/ε²)
# Born = {'N2':(32.079, -308.6, 3657, 10),'O2':(36.98,-318.028,1109.4,10),'NO':(32.27, -362.23, 1761.942, 2.34),'N':(13.782, -120.9, 883.5,  5.418),'O':(14.5364, -167.023, 2759.735, 10.563),'Ar':(62.22, -3500.5, 576343.86, 86.52)}

Bethe_Baluja = {'N2':(2.34,3.334),'O2':(4.4329,0.5782),'H2':(0.1386,29.151),'CO':(2.6813,2.5257)} # Baluja 1992
Born_Baluja = {'N2':(127.142,-1026.77,3901.234),'O2':(124.959,-629.306,-1981.92),'H2':(6.988,8.287,46.873),'CO':(125.671,-930.713,2444.26)}
Bethe_Liu = {'N2':(4.742,-0.36115)}  # Mtot², ln(Ctot) from Liu 1987
Born_Liu = {'N2':(122,-478.06,669.34)} # A,B,C 

Born_Bethe = {'N2':(0.4047,-413.093,53.137),'O2':(0.9867,-512.541,60.423),'H2':(-0.0484,-16.261,7.088),'CO':(0.3592,-446.945,55.607),'NO':(-29.44,0,-7.161,)} # Jain&Baluja (1992) table V

class Total:

    @classmethod
    def genTable(cls,targets):
        tab = [] # Mtot2, lnc, A, B, C, D
        for i,tar in enumerate(targets):
            if type(tar) is str: tot = cls(tar)
            elif(type(tar) is dict): 
                targets[i] = 'Air'
                tot = cls.create_mixture(tar)
            tab.append([tot.Mtot2,tot.lnCtot,tot.Z,tot.Be*co.Ryd/eV]+list(tot.ABC)+[tot.D])
        return pd.DataFrame(np.array(tab).T,index=(r'$\srm{M}{tot}^2$',r'$\ln\srm{c}{tot}$',r'$Z$',r'$\bar{B}$ (eV)',r'$\tilde{A}$',r'$\tilde{B}$',r'$\tilde{C}$',r'$K$'),columns=targets)

    def __init__(self,target,model='Present'):
        self.target = target
        self.Z = np.sum(co.Constants.MOLCS[target])
        orb = co.Constants.ORB_MOLC[target]
        self.Be = np.dot(orb['B'],orb['N'])/np.sum(orb['N'])/Ryd # Average Binding Energy of target
        self.D = 0
        if(model=='Baluja'):
            self.Mtot2,self.lnCtot = Bethe_Baluja[target]
            self.ABC = Born_Baluja[target]
        elif(model=='Liu'):
            self.Mtot2,self.lnCtot = Bethe_Liu[target]
            self.ABC = Born_Liu[target]
        else:
            self.Mtot2,self.lnCtot,self.gsum = co.Constants.Bethe.get(target,(1,1,-self.Z*0.75)) 
            coef = co.Constants.Born.get(target,(1,1,1,0))
            self.ABC = coef[:3]
            self.D = coef[-1]
        self.gsum = -self.Z*0.75 # Inokuti 1971 eq.(4.50)
        self.elastic = Elastic.gen_Born(target,ABC=self.ABC,D=self.D)
        self.l_4C = 1/(4*np.exp(self.lnCtot))
        # self._4C = (4*np.exp(self.lnCtot))
        self._C = 2*np.exp(self.lnCtot)/Ryd_
        self.scl = 1 # scaling used to match exactly at given point

    def __call__(self,Ek): # do not scale inelastic part
        return self.scl*self.elastic(Ek)+self.inelastic(Ek)

    @classmethod
    def genTotal(cls,target,Ek,cs,**kwargs):
        if(type(target) is dict): # this is a mixture
            tot = cls.create_mixture(target,**kwargs)
        else: tot = cls(target,**kwargs)
        tot.scl = (cs-tot.inelastic(Ek))/tot.elastic(Ek)
        return tot

    @classmethod
    def create_mixture(cls,comp,model='Present'):
        if len(comp)==1:
            return cls(list(comp.keys())[0],model=model)
        else:
            Mtot2 = MlnCtot = 0
            Z = gsum = ZlnB = 0
            ABC = np.array([0,0,0],dtype=float)
            D = 0
            for k,r in comp.items():
                t = cls(k,model=model)
                Mtot2 += t.Mtot2*r
                MlnCtot += t.Mtot2*t.lnCtot*r
                gsum += t.gsum*r
                Z += t.Z*r
                ZlnB += t.Z*np.log(t.Be)*r
                ABC += np.array(t.ABC)*r
                D += t.D*r
            tot = t
            tot.target = comp
            for a,v in zip(('Mtot2','gsum','Z','ABC','D','Be','lnCtot'),(Mtot2,gsum,Z,ABC,D,np.exp(ZlnB/Z),MlnCtot/Mtot2)):
                setattr(tot,a,v)
            tot.l_4C = 1/(4*np.exp(t.lnCtot))
            tot._C = 2*np.exp(t.lnCtot)/Ryd_
            tot.elastic = Elastic.gen_Born(tot.target,ABC=tot.ABC,D=tot.D)
            return tot 

    # def elastic(self,Ek): 
    #     # R_Ek = np.asarray(Ryd/Ek)
    #     R_Ek = np.asarray(2*Ryd_/(1-1/(1+mc2/Ek)**2)) # relativistically correct
    #     return 0.25*self.norm*R_Ek*np.dot(self.ABC,(np.ones(R_Ek.shape),R_Ek,R_Ek**2))

    def inelastic(self,Ek): # Inokuti 1971 eq.(4.55)
        # R_Ek = Ryd/Ek
        gamma2 = (1+Ek/mc2)**2
        beta2 = (1-1/gamma2)
        R_Ek = np.asarray(2*Ryd_/beta2) # relativistically correct
        # gamma_tot = self.Z*(-7/4 + np.log(self.Be*R_Ek)) 
        gamma_tot = self.gsum + self.Z*(np.log(self.Be*R_Ek)-1) # γtot =  Σ γ + Z (ln(B/ε) - 1) # Inokuti 1971 eqs. (4.52) & (4.46) 
        return O*R_Ek*(self.Mtot2*(np.log(beta2*gamma2*self._C)-beta2)+gamma_tot*R_Ek)

    def Liu(target): # Liu. 1987 - Phys. Rev. A 35.2
        Be = 240*1e3/(6.023*1e23)/Ryd # Average Binding Energy of N2
        Z = np.sum(co.Constants.MOLCS[target])
        A,B,C = (122,-478.06,669.34)
        norm = Total.norm
        def Total_CS(Ek):
            k0 = Ek/Ryd
            gamma_tot = Z*(-7/4 + np.log(Be/k0))
            elast = 0.25/k0*(A+B/k0+C/k0**2)
            inelast = 1/k0*(4.742*np.log(k0) + 4.8612 + gamma_tot/k0)
            return norm*(elast+inelast)
        return Total_CS

    def Born_Bethe(target): # Jain&Baduja 1992 
        a,b,c = co.Constants.Born_Bethe[target]
        norm = O
        def Total_CS(Ek):
            # R_Ek = Ryd/Ek
            gamma2 = (1+Ek/mc2)**2
            beta2 = (1-1/gamma2)
            R_Ek = 2*Ryd_/beta2 # relativistically correct
            return norm*R_Ek*(c+b*R_Ek-a*np.log(R_Ek))
        return Total_CS

    def Inelastic(target): # Jain & Baduja
        Mtot2,C = co.Constants.Bethe[target]
        l_4C = 1/(4*np.exp(C))
        norm = Total.norm
        def inelastic(Ek):
            R_Ek = Ryd/Ek
            return norm*R_Ek*(-Mtot2*np.log(R_Ek*l_4C))
        return inelastic

    def joint_Born_Bethe(self,target):
        M,lnc,g = co.Parameter.Bethe[target]
        A,B,C,D = co.Parameter.Born[target]
        Z = np.sum(co.Constants.MOLCS[target])
        a = M
        b = M*(lnc+np.log(2/cscoll.Ryd_)) + A/4
        c = -Z*0.75 + B/4
        return a,b,c