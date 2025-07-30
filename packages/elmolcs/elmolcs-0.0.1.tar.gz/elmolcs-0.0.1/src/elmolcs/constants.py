# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 18:36:21 2023

Copyright (C) 2023 
@author: Anthony Jeseněk

Module for sharing information : as for debugging instances bundles, output values, parameter inputs, constants, ...
"""
import numpy as np
from bidict import bidict
from aenum import NoAliasEnum
import re

# Physics

c = 299792458 # m/s - speed of light
sigma_r = 5.670373e-8 # W/m²K^4 - Stefan-Boltzman black body radiation constant
k_B = 1.380649e-23 # J/K - Boltzman statistical constant
eps0 = 8.854187817e-12 # F/m - vacuum permittivity
mu0 = 4*np.pi*1e-7 # H/m - vacuum permeability
alpha = 1/137.036 # fine structure constant
h = 6.62607015e-34 # Planck's constant
h_ = h/(2*np.pi) # Planck's reduced constant

# Particle
e = 1.602176634 * 10**(-19) # C - elementary charge
me = 9.1093837015 * 10**(-31) # kg - electron mass
ma = 1.660538921 * 10**(-27) # kg - atomic mass
r_0e = e**2/(4*np.pi*eps0*me*c**2) # m - electron classical radius
a0 = 4*np.pi*eps0*h_**2/(me*e**2) # m - Bohr's radius
Ryd = 13.605693122944*e # J - Rydberg

global keV, MeV, eV, GeV

µeV, meV, eV, keV, MeV, GeV = tuple(e * n for n in np.logspace(-6,9,6))
cm_1 = 100*c*h
percent = 0.01
deg2rad = np.pi/180

class Constants:

    I = (85.6 * eV) # J - mean ionisation energy in air

    MOLC_NAMES = bidict({'He':'Helium','Ne':'Neon','Ar':'Argon','O':'Oxygen','N':'Nitrogen','H':'Hydrogen','C':'Carbon','O2':'Dioxygen','N2':'Dinitrogen','NO':'Nitric Oxide','CO':'Carbon Monoxide','CO2':'Carbon dioxide','H2O':'Water','CH4':'Methane','NH3':'Ammonium','O3':'Ozone'})

    ATOMS = bidict({'H':1,'He':2,'C':6,'N':7,'O':8,'F':9,'Ne':10,'Ar':18,'Kr':36,'Xe':54})
    MOLCS = bidict({'H2':(1,1),'C2':(6,6),'N2':(7,7),'CO':(6,8),'O2':(8,8),'NO':(7,8),'H2O':(1,8,1),'CO2':(8,6,8),'O3':(8,8,8),'NO2':(8,7,8)})
    ORB_MOLC = {'H' : {'Z':1,'N':(1,),'B':(13.6057*eV,),'U':(13.6057*eV,)}, #https://physics.nist.gov/cgi-bin/Ionization/bun.php?Id=HI
                'H2': {'Z':2,'N':(2,),'B':(15.43*eV,),'U':(15.98*eV,)}, # K-shell average binding energy (Jolly et al. + Hwang et al. 1996)
                'He': {'Z':2,'N':(2,),'B':(24.587*eV,),'U':(39.51*eV,),'Q':0.8841}, # NIST + university of texas, one electron kinetic energy of the hamiltonian
                'C' : {'Z':6,'N':(2,2,1.3361,0.6639),'B':(308.304*eV,19.213*eV,11.786*eV,11.260*eV),'U':(437.156*eV,41.911*eV,34.1210*eV,34.107*eV)}, #https://physics.nist.gov/cgi-bin/Ionization/bun.php?Id=CI
                '_N' : {'Z':7,'N':(2,2,1.0025,1.9975),'B':(425.469*eV,25.828*eV,15.439*eV,14.5341*eV),'U':(598.726*eV,65.656*eV,51.094*eV,51.034*eV)}, #https://physics.nist.gov/cgi-bin/Ionization/bun.php?Id=NI
                'N' : {'Z':7,'N':(2,2,0.2,1,1.8),'B':(425.469*eV,25.828*eV,18.59*eV,16.43*eV,14.544*eV),'U':(598.726*eV,65.656*eV,51.1*eV,51.094*eV,51.034*eV)}, # Kim&Desclaux 2002 based on partial ionisations
                'N(2D)':{'Z':7,'N':(2,2,0.2,1,1.8),'B':(426.561*eV,26.253*eV, 16.20*eV, 14.05*eV, 12.16*eV), 'U':(603.371*eV,61.732*eV,49.833*eV,49.833*eV,49.340*eV)}, # Kim&Desclaux 2002
                '_O' : {'Z':8,'N':(2,2,1.6748,2.3252),'B':(562.878*eV,33.913*eV,16.603*eV,13.618*eV),'U':(796.189*eV,84.762*eV,68.505*eV,69.652*eV)}, #https://physics.nist.gov/cgi-bin/Ionization/bun.php?Id=OI
                'O' : {'Z':8,'N':(2,2,1.2,2,0.8),'B':(562.878*eV,33.913*eV,18.63*eV,16.932*eV,13.61*eV),'U':(796.189*eV,84.762*eV,70.8825*eV,68.505*eV,69.14*eV)}, # Kim&Desclaux 2002 based on partial ionisations
                'Ne': {'Z':10,'N':(2,2,6),'B':(0.8702*keV,48.5*eV,21.56*eV),'U':(1.262*keV, 141.87*eV, 32.784*eV)}, # Ionisation threshold on NIST others on https://www.webelements.com/neon/atoms.html and calculations from HF kinetic densities 
                '_N2': {'Z':7,'N':(4,2,2,4,2),'B':(0.4095*keV,41.72*eV,21*eV,17.07*eV,15.58*eV),'U':(0.6033*keV,71.13*eV,63.18*eV,44.3*eV,54.91*eV)}, # B = 15.581/ 12.072
                'N2': {'Z':7,'N':(4,2,2,4,2),'B':(0.4095*keV,37.3*eV,18.72*eV,16.74*eV,15.58*eV),'U':(0.6033*keV,71.13*eV,63.18*eV,44.3*eV,54.91*eV)}, # Lofthus&Krupenie(1977) p.198 (86/195) table 3 B = 15.581/ 12.072
                '_O2': {'Z':8,'N':(4,2,2,2,4,2),'B':(0.5438*keV,46.19*eV,29.82*eV,19.79*eV,19.64*eV,12.07*eV),'U':(0.7962*keV,79.73*eV,90.92*eV,71.84*eV,59.89*eV,84.88*eV)}, # K-shell average kinetic energy (Santos et al. 2003 )
                'O2': {'Z':8,'N':(4,2,2,2,4,2),'B':(0.5431*keV,40.33*eV,27.5*eV,20.3*eV,17.045*eV,12.07*eV),'U':(0.7962*keV,79.73*eV,90.92*eV,71.84*eV,59.89*eV,84.88*eV)}, # K-shell average kinetic energy (Santos et al. 2003 )
                'CO': {'Z':14,'N':(4,2,2,4,2),'B':(0.5425*keV,41.92*eV,21.92*eV,17.66*eV,14.01*eV),'U':(0.78*keV,79.63*eV,73.18*eV,54.3*eV,42.26*eV)}, # https://physics.nist.gov/cgi-bin/Ionization/table.pl?ionization=CO
                '_NO': {'Z':15,'N':(4,2,2,4,2,1),'B':(0.41*keV,43.7*eV,25.32*eV,18.49*eV,15.87*eV,9.26*eV),'U':(0.65*keV,76.55*eV,77.04*eV,55.37*eV,62.25*eV,65.27*eV)}, #https://physics.nist.gov/cgi-bin/Ionization/table.pl?ionization=NO
                'NO': {'Z':15,'N':(2,2,2,2,4,2,1),'B':(0.534*keV,0.401*keV,32.1*eV,21.848*eV,18.37*eV,15.73*eV,9.26*eV),'U':(0.7962*keV,0.6033*keV,76.55*eV,77.04*eV,55.37*eV,62.25*eV,65.27*eV)}, #https://physics.nist.gov/cgi-bin/Ionization/table.pl?ionization=NO
                'CO2': {'Z':22},
                'Ar': {'Z':18,'N':(2,2,6,2,6),'B':(3.203*keV,0.3263*keV,0.24913*keV,29.3*eV,15.76*eV),'U':(4.229*keV, 0.6831*keV, 0.651*keV, 103.5*eV/3, 78.03*eV/3)},  # https://www.webelements.com/argon/atoms.html and calculations from DHF Thakkar&Koga 2000
                'Kr': {'Z':36,'N':(2,2,6,2,6,2,6,10),'B':(14*eV,),'U':()}}
    GND_MOLC = {'N2':'1Σg+','O2':'3Σg-','H2':'1Σg+','Ar':'(3p6)1S0','NO':'2Π','CO':'1Σ+','CO2':'1Σg+','H2O':'1A1','CH4':'','NH3':'','O3':'1A1','NO2':'2A1','N2O':'','N':'(2p3)4S3/2°','O':'(2p4)3P2','C':'(2p2)3P0','F':'(2p5)2P3/2°','H':'(1s)2S','O2-':'2Πg','O-':'(2p5)2P','He':'(1s2)1S0','Ne':'(2p6)1S0','Kr':'(4p6)1S0'} 
    MASS_MOLC = {'N2':28.014,'O2':32,'NO':30,'CO':28,'H2':2,'He':4,'H':1,'Ar':39.948,'O':16,'N':14,'C':12,'F':19}
    SCATTLEN = {'H2':1.27,'Ar':-1.37,'He':1.19,'N2':0.44,'O2':0.3,'NO':0.75,'Ne':0.214,'O':0.63,'N':0.6,'Kr':-3.06,'Xe':-5.13} # Morrison 1988, Cross Section Data Inokuti (p.244 table 1), see also Zecca (1996) ; for Ar Kurokawa (2011) table IV, for N2 fitted 0.57 presently, for O : σ(0)=5 a0² from Zatsarinny 2006 fig.2 ; for NO: an eyed guess from Laporta 2022 with σ(ε=0)=3e-20 m². For N: MERT fit to Wang 2014 up to ε<0.01 eV (7 points only !)
    SCATTA1 = {'N2':358,'Ne':-1.66,'Ar':8.51,'Kr':12.8,'Xe':23.2} # O'Malley (1963) eq.(3.7) and Chang (1981) eq.(22) and Weyhreter (1987) table 5
    POL_MOLC = {'H2': (5.426,2.03,6.27),'N2':(11.74,3.131,25.12),'O2':(10.67,4.93),'CO2':(19.645,9.45),'CO':(13.15,2.61),'NO':(11.47217,3.78),'CO2':(19.644,9.45),'H2O':(9.785,),'Ar':(11.08,0,52.8),'He':(1.36,0,2.44),'Ne':(2.67,0,6.42),'Kr':(16.77,0,95.6),'Xe':(27.29,0,212),'H':(4.5,),'C':(11.27,),'N':(7.423,),'O':(5.412,)} # From Molecules and their Spectroscopic Properties pg 83. table 4.6 (92/222) and Padial&Norcross(1984) and Inokuti (1994) table 1 p.244 (257/497), and CRC Handbook of Chemistry p.10-189 & 10-199 For quadrupoles of noble gases see Reid&Wadehra (1994) # Hirschfelder Molecular
#Theory of Gases and Liquids  for O2: check Machado 1999 p.1200 , for H2: check Kolos&Wolniewicz(1967) table III p.1429
    OSC_POL_MOLC = {'Ar':(1.57,2.44),'O':(1.43,2.37),'N':(1.69,3.33),'H':(43/36,319/108,213/9),'N2':(1.47,2.4),'O2':(1.64,3.33),'NO':(2.1,5.13)} # for H : Drachman 1979 p.L701 (4/5), the rest : calculated
    ROT_MOLC = {k:v*cm_1 for k,v in {'H2':60.85,'N2':1.998,'O2':1.438,'NO':1.672,'CO':1.9313}.items()} # cm-1 From Molecules and their Spectroscopic Properties pg 83. table 2.1 (31/222) Conversion to eV : *100*c*h/eV
    VIB_MOLC = {k:v*cm_1 for k,v in {'H2':4401.2,'N2':2358.6,'O2':1580.2,'NO':1904.2,'CO':2169.8}.items()} # cm-1 From Molecules and their Spectroscopic Properties pg 83. table 2.1 (31/222) Conversion to eV : *100*c*h/eV
    DISS_MOLC = {'H2':4.48*eV,'N2':9.759*eV,'O2':5.116*eV, 'NO':6.534*eV} # Dissociation energies from Itikawa 1986/9 and Song 2020
    R_MOLC = {'H2':1.4011,'N2':2.0743,'O2':2.281,'NO':2.17464,'CO':2.1322,'Cl2':2.6456} # a0 in https://webbook.nist.gov
    Q_MOLC = {'H2':0.4922,'N2':-1.13,'O2':-0.29,'CO':-1.44,'NO':1.78} # Converted from Molecules and their Spectroscopic properties pg 81 (90/222) Conversion : statC*1e-30/(e*a0**2) and webbook for NO (Tejwani, G.D.T.; Golden, B.M.; Yeung, E.S., Pressure-broadened linewidths of nitric oxide, J. Chem. Phys., 1976, 65, 5110.)
    DIP_MOLC = {'NO':0.0625,'CO':0.0433,'H2O':0.729,'O3':0.21} # Converted from Molecules and their Spectroscopic properties pg 72 (81/222) Conversion : statC*1e-20/(e*a0) 
    EXC_MOLC = {'H2':(6.9*eV,11.183*eV,11.183*eV,11.183*eV),'N2':(6.17*eV,8.549*eV,12.5*eV,12.255*eV),'O2':(0.977*eV,4.262*eV,6.12*eV,8.15*eV),'CO':(6.006*eV,8.024*eV,8.024*eV,10.777*eV),'NO':(4.747*eV,5.484*eV,5.484*eV,5.484*eV),'CO2':(7*eV,32.55*eV),'H2O':(7*eV,11*eV)} # Threshold [0] First spin-allowed [1] First dipole-allowed [2] and First Rydberg state [3] Excitation energies : Gaseous Electronics & Jain&Baduja(1992)
    EXC_ATOM = {'H':(10.2*eV,)*4,'C':(1.264*eV,7.48*eV,7.95*eV,7.95*eV),'N':(2.384*eV,10.326*eV,10.326*eV,10.326*eV),'O':(1.97*eV,9.52*eV,9.52*eV,9.52*eV),'He':(19.82*eV,20.62*eV,21.22*eV,21.22*eV),'Ne':(16.62*eV,)*4,'Ar':( 11.55*eV,)*4,'Kr':(9.91*eV,)*4,'Xe':(8.31*eV,)*4} # from NIST spectra https://physics.nist.gov/PhysRefData/ASD/levels_form.html
    ION_ATOM = {'H':Ryd,'C': 11.2602880*eV,'N':14.53413*eV,'O': 13.618055*eV} # NIST ionisation energies https://physics.nist.gov/cgi-bin/ASD/ie.pl
    # H2 excitation avg != 4.87*eV
    ION_FIT = {'He':15.8*eV,'Ar':10.*eV,'H2':8.3*eV,'N2':13.*eV, 'O2':17.4*eV,'CO':14.2,'NO':13.6,'H2O':13.,'CO2':13.8} # Opal et al. (1971)
    
    #π a0²/ε (A+B/ε+C/ε²)
    Born = {'N2':(129.243,-270.926,74854.382,342.492) ,'O2': (148.738,-380.676,166556.802,412.32),'NO': (139.099,-295.974,24855.038,296.476),'N': (54.331,-110.502,4337.186,179.653),'O': (57.710,-116.203,8245.169,237.661),'Ar': (245.506,-529.708,4340222.695,1906.406)}
    Born_Bethe = {'N2':(0.4047,-413.093,53.137),'O2':(0.9867,-512.541,60.423),'H2':(-0.0484,-16.261,7.088),'CO':(0.3592,-446.945,55.607),'NO':(-29.44,0,-7.161,)}
    Bethe_incomplete = {'N2':(4.6962,0.4,0.042),'O2':(4.39837,-0.090,0),'NO':(4.29159,0.0765,0),'Ar':(4.331,-0.4,0),'N':(2.26086,0.3343,0),'O':(2.146,0.111,0)} # (M²,lnc,γ)
    Bethe_complete = {'N2':(4.6962,0.4,0.042),'O2':(4.522,-0.087,0),'NO':(5.192,0.06144,0),'Ar':(4.331,-0.4,0),'N':(2.26086,0.3343,0),'O':(2.425,0.085,0)}
    Bethe = Bethe_complete
    # For Ar: value 3 too low ! Values taken from Inokuti 1975 and Berkowitz p.84 (93/478) This is because we do not include many of the higher ~ 15 eV optically allowed electronic excitations
    AIR_COMP = {"N2":78.11 * percent, "O2":20.91 * percent, "Ar":0.98 * percent}
    AIR_STP = (2.547e25,288.15,101325) # N, T, p

for at,z in Constants.ATOMS.items(): # Include all single atoms as monatomic molecules
    Constants.MOLCS[at] = (z,)


class Unit:

    prepositions = {'p':1e-12,'n':1e-9,'µ':1e-6,'m':1e-3,'c':0.01,'d':0.1,'k':1e3,'M':1e6,'G':1e9}
    SUP = str.maketrans(".0123456789", "⋅⁰¹²³⁴⁵⁶⁷⁸⁹") 
    NUM = str.maketrans("⋅⁰¹²³⁴⁵⁶⁷⁸⁹", ".0123456789")

    def __init__(self,*args,**kwargs):
        if(len(args)==1): return self.__init1__(*args,**kwargs)
        else: return self.__init0__(*args,**kwargs)

    def __init0__(self,val,name, exp = 1):
        self.value = val
        self.__name__ = self.name = name
        self.__init1__({self:exp})
        if(self.value!=1): self._ref = Unit(1,name)
        else: self._ref = self

    def __init1__(self,unixp):
        self.unixp = unixp
        self.value = self.autovalue()
        self.eulav = 1/self.value
        self.__name__ = self.name = self.autoformat()
        if(self.value!=1): self._ref = Unit(1,self.__name__)
        else: self._ref = self

    def enhanced(self,**kwargs):
        u = Unit(val=kwargs.pop('val',self.value),name=kwargs.pop('name',self.__name__),exp=kwargs.pop('exp',1))
        return u

    def autovalue(self):
        val = 1
        for u,e in self.unixp.items():
            val *= u.value**e
        return val

    def autoformat(self):
        num = []
        den = []
        for u,e in self.unixp.items():
            if(e==1): num.append(u.__name__)
            elif(e==-1): den.append(u.__name__)
            elif(e>1): num.append(u.__name__+str(e).translate(Unit.SUP))
            elif(0<e<1): num.append(u.__name__+str(e).translate(Unit.SUP))
            elif(e<0): den.append(u.__name__+str(abs(e)).translate(Unit.SUP))
        if(len(num)==0): num = ['1']
        if(len(den)==0): return '.'.join(num)
        else: return '/'.join(('.'.join(num),'.'.join(den)))

    def format(self,value,fopt = '.3g',space=' '):
        if(np.isscalar(value)): return ("{0:%s}"%(fopt)).format(value/self)+space+str(self)
        elif(type(value)==np.ndarray): 
            fvec = np.vectorize(self.format)
            return fvec(value)
        elif(hasattr(value,'format')):
            return (value/self).format(fopt)+space+str(self)
        else:
            return type(value)(list(map(self.format,value)))

    def detect_unit(*values,unit,lim=1e6):
        values = np.array(values)
        if np.all(1/lim <= values/unit <= lim) and all(map(lambda v:len(str(np.round((v/unit)%1,decimals=6)))<=4,values)):
            return values/unit
        else: return values
        # else: return np.array(list(map(("{0:%s} %s"%(fopt,str(self))).format,value/self)))

    def __str__(self):
        expr = self.__name__
        # if(self.exp>1): expr += str(self.exp).translate(Unit.SUP)
        # elif(0<self.exp<1): expr += str(self.exp).translate(Unit.SUP)
        # elif(self.exp<0): expr = "1/"+self.name+str(abs(self.exp)).translate(Unit.SUP)
        return expr

    @classmethod
    def prepare(cls,expr): # Prepare expression so that eval(expr) gives directly a unit or a value
        alias = re_alias.finditer(expr)
        for a in alias:
            a = a.group()
            expr = expr.replace(a,unitalias[a])
        expr = expr.replace('^','**')
        expr = re.sub(r'\.\s*$','',expr) # remove ending point
        expr = re.sub(r'(?<!\d)\.(?!\d)|(?<=[A-Za-z]\d)\.','*',expr)
        expr = re.sub(r'(?<=\d)\s*(?=[A-Za-z])','*',expr) # separate values from units
        exp = re.search(r'([⋅⁰¹²³⁴⁵⁶⁷⁸⁹]+)',expr) # expr.translate(cls.NUM)
        if exp:
            exp = exp.groups()
            for e in exp:
                expr = expr.replace(e,'**'+e.translate(cls.NUM))
        # expr = re_unit_join.sub('Units.',expr) # Not needed, give the eval() function the namespace of the Unit members :))
        expr = re.sub(r'(?<=[A-Za-z])(?<=[01])?([2-9])(?!\w)',r'**\1',expr).replace('A**2','A2') # Exponents and glitch about Angström squared
        return expr

    @classmethod
    def parseval(cls,expr,**vals):
        expr = expr.strip()
        if(expr==''): return 1. # Unitless has unitary value
        elif(not re.search('[A-DF-Za-df-z]',expr)): # purely numeric ?
            try: return eval(expr,{},{})
            except: pass
        s = cls.prepare(expr)
        # s = re.sub(r'(?<=\d)\s*(?=[A-Za-z])','*',expr) # separate values from units
        try:
            # s = cls.prepare(expr)
            return eval(s,Units.__members__,vals)*1 # get only numerical value, no object
        except: pass
        
        # elif(',' in u): # multi-valued
        #     return tuple(cls.parseval(m, **vals) for m in expr.split(','))
        s,_,u = expr.rpartition(' ')
        u = u.strip()
        if(u in vals): u = vals[u]
        else: u = cls.parse(u,**vals)*1 # return a value
            
        # u = vals.get(u.strip(),cls.parse(u).value)
        if(not s): return u
        try:
            val = float(s)*u
        except ValueError: # Is multivalued (array, tuple, list,...)
            val = eval(s)
            if(u!=1): val = type(val)([v*u for v in val])
        return val

    @classmethod
    def parsevalunit(cls,expr):
        if(expr==''): return (1,Units.none) # Unitless has unitary value
        s = expr.split()        
        if(len(s)==1):
            s = s[0]
            try:
                return (eval(s),Units.none)
            except Exception:
                i = re.search('[A-z]',s).start()
                try: v = eval(s[:i])
                except: v = s[:i] if i!=0 else 1
                s = [v,s[i:]]
        u = cls.parse(s[1])
        try:
            val = float(s[0])
        except ValueError: # Is multivalued (array, tuple, list,...)
            val = eval(s[0])
        return (val,u)

    def parse(unit,**vals):
        """ Transform string argument into a Unit object"""
        if(unit==''): return Units.none # empty string means no units
        unit = Unit.prepare(unit)
        try:
            return eval(unit,Units.__members__,vals)
        except Exception:
            raise NameError('Unrecognised unit : '+unit)

    def splitunits(expr,parse=True,**vals):
        i = expr.rfind('(')
        e = expr.rfind(')')
        if(i!=e!=-1):
            un = expr[i+1:e]
            if parse: un = Unit.parseval(un,**vals)
            return expr[:i],un
        else:
            ex,_,un = expr.rpartition(' ')
            if parse: un = Unit.parseval(un,**vals)
            return ex,un

        # if unit[:2]=='1/':
        #     parsed=['1/']
        #     unit = unit[2:]
        # else: parsed = []
        # unit = unit.replace('^','**')
        # unit = unit.replace('.','*')
        # unit = unit.translate(Unit.NUM)
        # parsed.extend(re.split('(\W+)',unit))        
        # new = ''
        # i=0
        # while i < len(unit):
        #     inv = False
        #     if(unit[i].isalpha() or unit[i]==0): meth = lambda s: s.isalpha() or s=='0'
        #     elif(unit[i].isnumeric()): meth = str.isnumeric
        #     else: meth = lambda s: not(s.isalpha() or s.isnumeric())
        #     while i<len(unit) and meth(unit[i]):
        #         new += unit[i]
        #         i += 1
        #     parsed.append(new)
        #     new = ''
        # for i,s in enumerate(parsed):
        #     if s.isalnum() and not s.isnumeric() or s in unitalias:
        #         if s not in Units.__members__:
        #             if(s in unitalias): s = unitalias[s]
        #             else:
        #                 for num in re.finditer('[^*][2-9]+',s):
        #                     n = num.group()[1:]
        #                     s = re.sub(n,'**'+n,s,count=1)
        #         parsed[i] = 'Units.'+s
        #     elif s.isnumeric() and parsed[i-1]!='**':
        #         parsed[i] = '**'+s#.translate(Unit.NUM)
        # try:
        #     return eval(''.join(parsed))
        # except Exception:
        #     raise NameError('Unrecognised unit : '+unit)

    @property
    def ref(self):
        return self._ref

    @property
    def inv(self):
        # return Unit(1/self.value,"1/"+self.name,self.exp)
        unixp = self.unixp.copy()
        for u,e in unixp.items():
            unixp[u] = -e
        return Unit(unixp)

    def __pow__(self,pow):
        # return Unit(self.value**pow,self.name,self.exp*pow)
        unixp = self.unixp.copy()
        for u in unixp.keys():
            unixp[u] *= pow
        return Unit(unixp)

    def __add__(self,added):
        if(self is Units.none): return str(added) 
        return str(added)+' ('+str(self)+')'

    def __radd__(self,adder):
        if(self is Units.none or self.name==''): return str(adder)
        return str(adder)+' ('+str(self)+')'

    def __mul__(self,multed):
        if issubclass(multed.__class__,Unit):
            unixp = self.unixp.copy()
            for u2,e2 in multed.unixp.items():
                    unixp.__setitem__(u2,unixp.get(u2,0)+e2)
            return Unit(unixp)
            # if(self.name == multed.name):
            #     return Unit(self.value*multed.value,self.name,self.exp+multed.exp)
            # else:
            #     return Unit(self.value*multed.value,self.name+"."+multed.name)
        else:
            return self.value*multed

    def __rmul__(self,multer):
        if issubclass(multer.__class__,Unit):
            unixp = multer.unixp.copy()
            for u2,e2 in self.unixp.items():
                    unixp.__setitem__(u2,unixp.get(u2,0)+e2)
            return Unit(unixp)
            # return Unit(multer.value*self.value,multer.name+"."+self.name)
        else:
            return multer*self.value

    def __truediv__(self,divider):
        # print(self,'div')
        if issubclass(divider.__class__,Unit):
            unixp = self.unixp.copy()
            for u2,e2 in divider.unixp.items():
                    unixp.__setitem__(u2,unixp.get(u2,0)-e2)
            return Unit(unixp)
            # return Unit(self.value/divider.value,self.name+"/"+divider.name)
        else:
            return self.value/divider

    def __rtruediv__(self,divided):
        # print(self,divided,'rdiv')
        if issubclass(divided.__class__,Unit):
            unixp = divided.unixp.copy()
            for u2,e2 in self.unixp.items():
                    unixp.__setitem__(u2,unixp.get(u2,0)-e2)
            return Unit(unixp)
            # return Unit(divided.value/self.value,divided.name+"/"+self.name,self.exp)
        # elif (type(divided)==str):
        #     return Unit(float(divided)/self.value,divided+"/"+self.name,self.exp)
        else:
            return divided*self.eulav # for efficiency multiply by stored inverse

unitalias = {'degree':'deg','pi':str(np.pi),'π':str(np.pi)}
class Units(Unit,NoAliasEnum): #TODO : create primary Units and add later  derived units
    keV = keV
    MeV = MeV
    GeV = GeV
    eV = eV
    meV = meV
    µeV = µeV
    K = 1.
    hartree = 2*Ryd
    au = 1.,'a.u.'
    barn = 1e-28,'10^{-28} m²'
    A2 = 1e-20, 'Å²'
    a0 = a0, 'a₀'#'a_0' #
    km = 1000., 'km'
    bar = 1e5
    Torr= 101325/760
    m = 1., 'm'
    cm = 0.01, 'cm'
    mm = 0.001, 'mm'
    µm = 1e-6, 'µm'
    nm = 1e-9,'nm'
    s = 1., 's'
    sr = 1., 'sr'
    ms = 10.**(-3), 'ms'
    µs = 10.**(-6), 'µs'
    ns = 10.**(-9), 'ns'
    ps = 10.**(-12), 'ps'
    J = 1., 'J'
    kV = 1000., 'kV'
    kg = 1000., 'kg'
    Td = 1e-21
    V = 1., 'V'
    MV = 1e6,'MV'
    N = 1., 'N'
    deg = np.pi/180, ' ° '
    rad = 1, 'rad'
    number = 1., ' # '
    ratio = 1., 'ratio'
    norm = 1.,' Normalised '
    arb = 1.,' Arbitrary '
    rel = 1.,' Relative '
    none = 1.,''
    percent = percent,'%'

    def __init__(self,val,*args):
        self._amount = 1.
        self._base = val
        self.eulav = 1/val
        self.exp = 1
        self.unixp = {self:self.exp}
        if(len(args)>0 and ''!=args[0]!=self.name): # alias
            unitalias[args[0].strip()] = self.name
            self.__name__ = args[0]
        else: self.__name__ = self.name
        if(self._base!=1): self._ref = Unit(1,self.__name__)
        else: self._ref = self

    def __str__(self):
        return self.__name__

    @property
    def value(self):
        return self._amount*self._base

    @property
    def base(self):
        return self._base
    @property
    def amount(self):
        return self._amount
re_alias = re.compile('|'.join(map('({:s})'.format,unitalias.keys())))
# units = [u for u in Units.__members__]
# re_unit_join = re.compile('|'.join(list(map(lambda s: r'(?<!\w)(?=%s)'%s,units))))
