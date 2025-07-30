# -*- coding: utf-8 -*-
"""
Created on Wed May 18 16:14:05 2022

Copyright (C) 2023 
@author: Anthony Jeseněk

The reader has useful routines to parse and identify electron-molecule reactions.
Its architecture is flexible but not robust

It uses molecular and atomic data contained in constants.Constants to complete the information missing in the header of each reaction 

If you use a target which has missing data in constants.Constants, the reader will most likely crash and explain why

It is up to the user to provide the adequate data missing to the constants module to load reactions

For a robust reader, please use the `bolos.parser` from `bolos` on https://pypi.org/project/bolos/

"""


# Parsing routines for reading collision files 

__version__ = '0.0.1'
__all__ = ['loadCS','loadDCS','readCS','readDCS','readPD','readOOS','readFC','CS_Data']

import os
import numpy as np
import scipy as sp
import pandas as pd
import numba as nb
from datetime import datetime
import re
from . import filehandler
import uncertainties
from uncertainties import unumpy
import collections
import warnings
import logging
from . import cscoll
from . import constants as co
from sortedcontainers import SortedList, SortedDict, SortedSet

class DefaultDict(collections.defaultdict): # Default dictionary whose factory takes key into account
    def __missing__(self, key):
        if self.default_factory:
            dict.__setitem__(self, key, self.default_factory(key))
            return self[key]
        else:
            collections.defaultdict.__missing__(self, key)

SPECIES = 'SPECIES'
PROCESS = 'PROCESS'
COMMENT = 'COMMENT'
PARAM = 'PARAM.'
COLUMNS = 'COLUMNS'

RE_PARTIAL = re.compile(r'\((.*)[^X]\)')

a0 = co.a0
me = co.me
ma = co.ma
eV = co.eV
keV = 1e3*eV

o = 1e-20 # A² 
O = 4*np.pi*a0**2
Ryd = 0.01361 # keV
header = '{1:s}\n{0:s} -> {0:s}{4:s}\n {2:.5e} \nSPECIES: e / {0:s}\nPROCESS: E + {0:s} -> E + {0:s}{4:s}, {3:s}\nPARAM.: {5:s}\nCOMMENT: {1:s} {3:s} : {0:s}{4:s}  | based on {7:s} \nUPDATED: {8:s}\nCOLUMNS: {6:s}\n'
headertabata = '{1:s}\n{0:s} -> {0:s}{4:s}\n {2:.5f} \nSPECIES: e / {0:s}\nPROCESS: E + {0:s} -> E + {0:s}{4:s}, {3:s}\nPARAM.: Eth = {2:.5f} eV, {5:s}\nCOMMENT: {1:s} {3:s} : {4:s}  | Tabata et al. (2006) \nUPDATED: %s\nCOLUMNS: {6:s}\n'%str(datetime(2006,4,26))
HEADER = {0:'%s',1:'%s','SPECIES': 'e / %s','PROCESS': 'e + {0:s} -> e + {0:s}{1:s}','PARAM.':'%s','COMMENT':'%s','UPDATED':'%s','COLUMNS': '%s'}
# (specie, kind, threshold, subkind, final, params, columns, source, updated)

filenames = {'cs':'Cross section','dcs':'DCS','oos':'Optical Oscillator Strengths','fcf':'Franck-Condon Factors','pd':'Predissociation Ratios'}
base = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
ROOT = os.path.join(base,'Data')

def readFC(target): # Franck-Condon Factor
    filepath= os.path.join(ROOT,'fcf',filenames['fcf']+'.e-'+target)
    fctab = filehandler.TableHandler.readtable(filepath,NA=filehandler.NA)[0].set_index("v'")
    if('Ek' in fctab.columns): 
        gnd = 'X'+co.Constants.GND_MOLC[target]
        fctab.rename(columns={'Ek':(gnd,'Ek')},inplace=True)
    fctab.columns = pd.MultiIndex.from_tuples(fctab.columns)
    fctab.columns = fctab.columns.set_levels(map(stateStandard,fctab.columns.levels[0]),level=0)
    return fctab

tarFC = DefaultDict(readFC)

def readOOS(target): # Optical Oscillator Strength
    filepath = os.path.join(ROOT,'oos',filenames['oos']+'.e-'+target)
    oos = filehandler.TableHandler.readtable(filepath,sep=',',index=True,numeric=False,NA=filehandler.NA)[0]
    return oos

def readPD(target): # predissociation branching ratio
    pdfile = os.path.join(ROOT,'fcf',filenames['pd']+'.e-'+target)
    if os.path.exists(pdfile):
        e_pd = pd.read_csv(pdfile)#filehandler.TableHandler.readtable(pdfile,sep=',',index=True)[0]
    else:
        csfile = os.path.join(ROOT,'cs',target,filenames['cs']+'.e-'+target)
        cs = parsecs(csfile,key='pd',skip=True)
        e_pd = pd.DataFrame({c['final']:c['param']['η_pd'] for c in cs},index=['η_pd'])
        filehandler.writetable(pdfile,e_pd,sep=',')
    return e_pd

def readCS(target,db=None,**kwargs):
    ''' Returns a list of [ CS processes ]
    Args:
        target (str) : symbol of the target atom/molecule
        db (str) : datena keyword'''
    filepath = os.path.join(ROOT,'cs',target,'')
    if db is None or db.lower() in ('x','iaa'): # This is the IAA database from tables (default)
        filename = filenames['cs']+'.txt'
        file = os.path.join(ROOT,'cs',filename)
        return [c for c in parsecs(file,key=r'(\s|^)'+target+r'(\s|$)',minrow=3,regex=True,**kwargs) if c['target']==target]
    elif db.lower() in ('iaa*'): # This is the IAA database with analytical CS
        filename = filenames['cs']+'.e-'+target
    elif(db.lower() in ('elastic','total','excitation','analytic','vib','rot')): # this is a collection
        filename = filenames['cs']+' %s.e-'%db+target
        filepath += 'others'+os.sep
    else: # this is another database
        filename = filenames['cs']+' (%s).e-'%db+target
        if db!='short':
            filepath += 'others'+os.sep
    file = filepath+filename
    return parsecs(file,key=target,minrow=3,**kwargs)

def readDCS(target,db=None,**kwargs):
    ''' Returns a list of [ DCS processes ]'''
    filepath = os.path.join(ROOT,'dcs',target,'')
    if db is None or db.lower() in ('x','iaa'):
        filename = filenames['dcs']+'.e-'+target
    elif db.lower() in ('exp','raw','',):
        filename = 'Diff cross section'+'.e-'+target
    else:
        filename = filenames['dcs']+'(%s).e-'%db+target
    file = filepath+filename
    return parsediff(file,**kwargs)

def loadCS(target,db=None,**kwargs):
    ''' Returns a dictionary of lists:
        { kind : [ processes ]} '''
    processes = readCS(target,db,**kwargs)
    procs = collections.defaultdict(list)
    for p in processes:
        kind = p['kind']
        if p['subkind'] in ('VIBRATIONAL', 'ROTATIONAL'):
            kind = p['subkind']
        procs[kind].append(p)
    return procs

def loadDCS(target,db=None,**kwargs):
    ''' Return DCS_Data objects : 
        tuple : Elastic DCS, Inelastic = {name : DCS} '''
    elast = DCS_Data(target,'ELASTIC')
    inel = {}
    processes = readDCS(target,db,**kwargs)
    for i,process in enumerate(processes):
        # try:
        if(process['kind']=='ELASTIC'): 
            elast.extend(process)
        else:
            if(process['state'] not in inel): inel[process['state']] = DCS_Data(target,'INELASTIC',process['state'])
            inel[process['state']].extend(process)
        # except Exception as ex:
        #     logging.debug("Unknown process name %s" % process["kind"])
        #     logging.debug(str(ex))
    elast.build()
    for state,dcs in inel.items():
        dcs.build()
    return elast,inel

def closest(node, nodes, value=False):
    nodes = np.asarray(nodes)
    deltas = nodes - node
    dist_2 = np.einsum('i,i->i', deltas, deltas)
    index = np.argmin(dist_2)
    if(value): return nodes[index]
    else: return index

class CS_Data:

    indexer = '%s.%s:%s-%d'

    def __init__(self,target=None,db=None,**kwargs):
        self.targets = SortedSet()
        self.databases = SortedSet()
        self.tarbase = {}
        cols = pd.MultiIndex.from_tuples([],names=['target','source','state'])
        self.data = pd.DataFrame(columns=cols,index=np.empty(0)) # MultiIndex column structure : (target, database/source, filt)
        self.error = pd.DataFrame(columns=cols,index=np.empty(0)) # MultiIndex column structure : (target, database/source, filt)
        self.data.index.name = 'Energy'
        self.error.index.name = 'Energy'
        self.idx = pd.DataFrame(index=['idx'],columns=cols,dtype=str) # indexer for processes
        self.processes = {}
        if(target and db):
            if(type(target) is str): target = [target]
            if(type(db) is str): db= [db]
            for tar in target:
                for d in db:
                    try:
                        self.add_database(tar,d,**kwargs)
                    except FileNotFoundError as e:
                        logging.warning(e)

    def add_database(self,target,db,skip=False,**kwargs):
        db = db.lower()
        processes = readCS(target,db,skip=skip)
        filt = {k:v for k,v in kwargs.items() if k in processes[0]} # Filter for keyword values
        self.add(processes,db=db,filt=filt)
        self.targets.add(target)
        self.tarbase[(target,db)] = processes
        if(not db.lower() in ['elastic','momentum','total','excitation','vib','rot','attachment','effective','#misc']): self.databases.add(db) # collision type is not considered a database

    def add(self,processes,db='#misc',filt={}):
        data = []
        error = []
        for i,p in enumerate(processes):
            if(filt):
                skip = False
                for k,v in filt.items(): # Filter out processes whose p[k] != v
                    if(p[k]!=v):
                        skip = True
                        break                    
                if(skip): continue
            if(db.lower() in ('elastic','momentum','total','excitation','analytic','vib','rot','attachment','effective','#misc')): ref = findsource(p['source'],abbrev=True,default=p['source'])
            else:
                p['source'] = db.capitalize()
                ref = db
            target = p['target']
            if(p['kind'] in ('ELASTIC','TOTAL')): key = (target,ref,p['subkind']) 
            else: key = (target,ref,p['final']) 
            if (key in self.idx.columns): # This key should be unique !
                logging.warning('duplicate CS for %s'%(str(key)))
                ref += str(i)
                p['source'] = ref
                key = (target,ref,key[-1])
            data.append(p['data']['CS'].rename(key))
            if 'Error' in p['data']:
                error.append(p['data']['Error'].rename(key))
            else: error.append(pd.Series(np.nan,index=p['data'].index,name=key))
            # self.data = self.data.join(p['data']['CS'].rename(key),how='outer')
            # self.error = self.error.join(p['data']['Error'].rename(key),how='outer')
            idx = self.__class__.indexer%(key+(i,))
            self.idx[key] = idx
            self.processes[idx] = p
            assert not np.any(p['data'].index.duplicated()), 'Not unique index for %s : %s \t [%s] \n It is : %s'%(db,p['process'],p['comment'],str(p['data'].index[p['data'].index.duplicated()]))
        self.data = pd.concat([self.data]+data,axis=1,join='outer').sort_index()
        self.error = pd.concat([self.error]+error,axis=1,join='outer').sort_index()

    def select(self,target=[],db=[],final=[],table=True,incl=True,**kwargs):
        ''' Select data for given target, database (source), and final state
        Parameters:
        ----------
            target : str or list[str] - molecular or atomic targets
            db : str or list[str] - databases or sources
            final : str or list[str] - final excitation/ ionisation states of a transition, can be a sum of states : 'A3Σ + B3Π'
            tabelenda : bool - yield directly cross-section values and errors ? (default = True)
            incl : bool - include (default) or exclude given database and source names ?
        Returns
        -------
            cs and errors if table 
            list of processes otherwise
        '''
        tabelenda = table
        if(type(target) is str and target in self.targets): target = [target]
        elif(not target): target = list(self.targets)
        else: assert set(self.targets).issuperset(target), '%s not loaded, please load them beforehand'%str(target)
        if(not db): db = slice(None,None)
        elif(incl and type(db) is str and db in self.databases): pass
        else:
            if(type(db) is str): db = [db]
            if(incl): # include all source given
                sources = [d for d in db if d not in self.databases]
                # dbfilt = sourcefilter(sources)
                for s in sources: # necessary to preserve order
                    dbfilt = sourcefilter([s])
                # for i,s in enumerate(sources.copy()):
                #     sources[i] = db[db.index(s)] = re.sub(r'\(\?\<?[=!].*\)','',s) # get rid of             
                    for d in self.data.columns.levels[1]:
                        if(not (bool(dbfilt(d))^incl)): db.insert(db.index(s),d)
                for s in sources: db.remove(s)               
            else: # Exclude: Take all sources except those in the db given
                dbfilt = sourcefilter(db)
                db.clear()                
                for d in self.data.columns.levels[1]:
                    if(not (bool(dbfilt(d))^incl)): db.append(d)
        # else: assert set(self.databases).issuperset(db), '%s databases not loaded, please load beforehand'%str(db)
        key = (target,db)
        if(type(final)==str):
            if (' + ' in final): 
                finals = tuple(final.split(' + '))
                if (final not in self.data.columns.levels[2]):
                    final = finals
                else: final = (final,)+finals        
                key+=(final,)
                res,err = self.data.loc[:,key].dropna(axis=0,how='all').sum(axis=1,level=1,skipna=False),self.error.loc[:,key].dropna(axis=0,how='all').sum(axis=1,level=1,skipna=False)
                if not tabelenda:
                    protoproc = self.processes[self.idx.loc[:,key].iat[0,0]]
                    proc = []
                    for k,t in res.items():
                        p = protoproc.copy()
                        p['final'] = final
                        p['source'] = k
                        p['data'] = pd.concat((t,err[k]),axis=1,ignore_index=False,keys=['CS','Error']).dropna()
                        proc.append(p)
                    return proc
                else: return res,err
            elif final not in self.data.columns.levels[2]: 
                fin = [c for c in self.data.columns.levels[2].unique() if re.search(final,c)]
                if not fin: raise KeyError('State %s for %s not loaded'%(target,final))
                final = fin
        if(final): key+= (final,)
        if(kwargs): 
            res = []
            for i in self.idx.loc['idx',key]:
                proc = self.processes[i]
                prenenda = True
                for k,w in kwargs.items():
                    if(type(w) in (list,tuple)): w = '|'.join(w) # regex for choices
                    if(not re.fullmatch(w,proc[k])): # does not match selection criteria
                        prenenda=False
                        break
                if(prenenda):
                    if tabelenda:
                        ind = self.idx[self.idx==i].loc['idx'].dropna().index 
                        src = ind.get_level_values('source')[0]
                        fin = ind.get_level_values('state')[0]
                        res.append((src,fin))
                    else: res.append(proc)
            if tabelenda:
                key = list(key)
                src, fin = map(list,zip(*res))
                if type(key[1])!=list: key[1] = src
                else: key[1] = key[1]+src
                if len(key)==2: key.append(fin) 
                elif type(key[2]!=list): key[2] = fin
                else: key[2] = key[2]+fin
                key = tuple(key)
                return self.data.loc[:,key].dropna(axis=0,how='all'),self.error.loc[:,key].dropna(axis=0,how='all')
            else: return res
        else:
            if(tabelenda): return self.data.loc[:,key].dropna(axis=0,how='all'),self.error.loc[:,key].dropna(axis=0,how='all')
            else: return [self.processes[i] for i in self.idx.loc['idx',key]]

class DCS_Data:

    cols = ['Angle','Energy','DCS','Error']

    def _fitprior(d): # Best candidate has : lowest (relative) error, greater angular span and more data points and more recent
        return np.mean(d['err']/d['dsc'])/(d['theta'][-1]-d['theta'][0])**2/len(d['theta'])/(d['year']-1950)

    def __init__(self,target,kind,state='X'):
        # self.predata = SortedList(key=lambda o : o['data'][0,1])#np.ndarray.__getitem__(o,(0,1)))
        self.predata = []
        self.target = target
        self.kind = kind
        self.state = state
        self.data = np.array([])
        self.error = np.array([])
        self.ordata = SortedDict()
        self.errors = {}
        self.comments = []
        self.energies = SortedSet()

    def __getitem__(self,coord):
        return self.data[coord]

    def extend(self,dico):
        self.normalised = False
        data = np.array(dico['data'])
        if(not data.shape[1]==4):
            errors = np.array(dico['errors'])
            if(not errors.shape or len(errors) in (1,len(data))):
                errs = np.array(data[:,-1]*errors)[:,np.newaxis]
                data = np.hstack((data,errs))
            else: # more than one set of errors
                data = np.column_stack((data,np.zeros(len(data))))
                energies = set()
                ierr=-1
                for i,e in enumerate(data[:,1]):
                    if(e not in energies):
                        energies.add(e)
                        ierr+=1
                    data[i,3] = data[i,2]*errors[min(ierr,len(errors)-1)]    
            # if(not np.isscalar(errors) and errors.shape and len(errors)!=len(data)): 
            #     if(len(errors)>0): error = errors[0]
            #     else: error = 0.25 # Standard error percentage if error not specified
            # else: 
        dic = dico.copy()
        dic['data'] = data
        self.predata.append(dic)

    def separateEk(self,data):
        dat = pd.DataFrame(data,columns=self.cols)
        assert(all(dat[['Angle','Energy']].duplicated()==False)), 'Table has duplicate values ! \n %s'%str(dat[dat[['Angle','Energy']].duplicated()])
        energies = SortedSet(dat['Energy'])
        subs = [dat[dat['Energy']==Ek].values for Ek in energies]
        return energies,subs

    def build(self,cross_section=None):
        if(len(self.predata)==0): raise RuntimeError("No data for "+self.target+' '+self.kind+", using elastic instead")
        self.ordata.clear()
        multi,series = [],[]
        serr = []
        integ = []
        for base in self.predata:
            # try: source = findsource(base['comment'])
            # except KeyError: 
            #     logging.warning('Unknown source for %s @ %s'%(base.get('process',base['target']),base.get('param.','E='%base['data'][0,1])))
            #     source = '#Unknown# '
            for Ek,data in zip(*self.separateEk(base['data'])):
                df = self.unfold(data,cross_section)
                # self.angles.update(data[:,0])
                df['source'] = base['source']
                df['year'] = base['year']
                df['subkind'] = base['subkind']
                df['state'] = base['state']
                if(df['year'] is None): df['year'] = 1960
                srcbrev = findsource(base['source'],abbrev=True)
                multi.append((Ek,srcbrev))
                series.append(pd.Series(data[:,2],index=data[:,0]))
                serr.append(pd.Series(data[:,3],index=data[:,0]))
                mult = pd.MultiIndex.from_product([['ICS','MTCS'],[srcbrev],['val','err']])
                integ.append(pd.DataFrame([[df['norm2pi'],df['errcs'],df['mtcs'],df['errmt']]],index=[Ek],columns=mult))
                self.ordata.setdefault(Ek,SortedList(key=DCS_Data._fitprior)).add(df)
        self.energies.update(self.ordata.keys())
        multi = pd.MultiIndex.from_tuples(multi,names=['Energy','Source'])
        if(multi.nunique()!=len(multi)): 
            mask = multi.duplicated()
            raise RuntimeError('Duplicated values for %s'%str(multi[mask]))
        self.data = pd.concat(series,axis=1,keys=multi).sort_index(axis=1,level=0).sort_index(axis=0)
        self.error = pd.concat(serr,axis=1,keys=multi).sort_index(axis=1,level=0).sort_index(axis=0)
        self.ics = pd.concat(integ,axis=0).sort_index(axis=0)

    def rebuild(self):
        for Ek in list(self.ordata.keys()):
            if(Ek not in self.data.columns.levels[0]):
                del self.ordata[Ek]
            else:
                for d in self.ordata[Ek][:]:
                    key = (Ek,d['source'])
                    if(key not in self.data.columns):
                        self.ordata[Ek].remove(d)
                    else:
                        angs = self.data[key].dropna().index
                        if(len(d['theta'])!=len(angs)):
                            select = np.isin(d['theta'],angs)
                            for s in ['theta','dsc','err']:
                                d[s] = d[s][select]

    @classmethod
    def unfold(cls,data,cross_section=None):
        dheta,Ek,dsc,err = data.T
        theta = dheta*co.deg2rad
        assert all(Ek==Ek[0]), 'Mixed data occurred at different energies'
        Ek = Ek[0]
        err0 = err==0
        if np.any(err0): # Do not allow to have zero uncertainty
            err[err0] = np.median(err[~err0]/dsc[~err0])*dsc[err0] 
        if(cross_section): cs_n = cross_section(Ek)
        else: cs_n = None
        ycos =  np.hstack((0,dsc*np.sin(theta)*np.cos(theta),0))
        x = np.hstack((0,theta,np.pi))
        y = np.hstack((0,dsc*np.sin(theta),0))    
        tot = sp.integrate.trapezoid(y,x)
        totcos = sp.integrate.trapezoid(ycos,x)
        errcs = (0.5*(np.sin(theta[0])*dsc[0]*theta[0]+np.sin(theta[-1])*dsc[-1]*(np.pi-theta[-1])))**2+np.mean(err)**2
        errcs = np.sqrt((errcs/tot)**2+np.mean(err/dsc)**2)*errcs
        errmt = 0.5*(np.sin(theta[0])*dsc[0]*theta[0]*(1-np.cos(theta[0]))+np.sin(theta[-1])*dsc[-1]*(np.pi-theta[-1])*(1-np.cos(theta[-1])))
        errmt = np.sqrt((errmt/tot)**2+np.mean(err/dsc)**2)*errmt
        return {'theta':dheta,'dsc':dsc,'Ek':Ek,'err':err,'cs':cs_n,'errcs':errcs*2*np.pi,'norm':tot,'norm2pi':tot*(2*np.pi),'cos_m':totcos/tot,'mtcs':(tot-totcos)*(2*np.pi),'errmt':errmt*2*np.pi}

    @staticmethod
    def integrate(theta,dsc,cumulative=False,scheme = sp.integrate.trapezoid): # Never integrate in cosine space !        
        if(0 not in theta and np.pi not in theta):
            x = np.hstack((0,theta,np.pi))
            y = np.hstack((0,dsc*np.sin(theta)*2*np.pi,0))        
        else:
            x = theta
            y = dsc*np.sin(theta)*2*np.pi
        if(cumulative): 
            I = sp.integrate.cumtrapezoid(y,x,initial=0)
            return I[1:-1]/I[-1] # same size as input theta
        else: return scheme(y,x)

    def cum_cross_section_at(self,Ek,lexo = 0,rexo = 0,scheme = sp.integrate.trapezoid): # Never integrate in cosine space !
        Ek = closest(Ek,self.energies,value=True)
        res = []
        for d in self.ordata[Ek]:
            theta = d['theta']*co.deg2rad
            y = DCS_Data.integrate(theta,d['dsc'],cumulative=True)
            res.append({'x':theta, 'y':y, 'Ek':Ek,'source':d['source']})
        return res

    def hide(self,percentage, energy_row = False, energy_range = (0,np.inf)):
        if(not hasattr(self,'full_data')): self.full_data = self.data.copy()
        if(not hasattr(self,'full_ordata')): self.full_ordata = {Ek:[d.copy() for d in l] for Ek,l in self.ordata.items()}
        ind = self.data.columns.levels[0]
        self.data = self.data[ind[ind.to_series().between(*energy_range)]]
        if(not energy_row and percentage!=0):
            mask = np.random.rand(*self.data.values.shape)
            mask[self.data.isna()]=0
            thres = np.percentile(mask[~self.data.isna()],100-percentage,interpolation='lower')
            mask[mask<thres]=False # Do not mask values whithin range
            mask = mask.astype(bool) # mask all other values
            self.data = self.data.mask(mask)
        else: self.data = self.data.sample(frac=percentage,axis=1)
        self.rebuild()

    def ratio(self,Eks,source,ref):
        if(not np.array(Eks).shape): Eks = [Eks]
        filt = sourcefilter([source,ref])
        for Ek in Eks:
            exps = list(filter(filt,self.data.xs(Ek,level=0,axis=1).columns))
            if(len(exps)==2):
                if(ref in exps[1]): 
                    r = exps[1]
                    s = exps[0]
                else: 
                    r = exps[0]
                    s = exps[1]
                ratio = (self.data.loc[:,(Ek,r)]/self.data.loc[:,(Ek,s)]).dropna()
                print(Ek, ratio.mean(),ratio, findsource(r,abbrev=True), findsource(s,abbrev=True))        

    def unhide(self):
        self.data = self.full_data.copy()
        self.ordata = {Ek:SortedList([d.copy() for d in l],key=DCS_Data._fitprior) for Ek,l in self.full_ordata.items()}

class DDCS_Data:

    def __init__(self,target):
        self.target = target
        self.predata = []

    def extend(self,dico):
        self.predata.append(dico)

    def build(self):
        if(len(self.predata)==0): raise RuntimeError("No DDCS data for "+self.target)
        multi,tabs = [],[]
        err = []
        for base in self.predata:
            # try: source = findsource(base['comment'])
            # except KeyError: 
            #     logging.warning('Unknown source for %s @ %s'%(base.get('process',base['target']),base.get('param.','E='%base['data'][0,1])))
            #     source = '#Unknown# '
            tabs.append(base['data'])
            shape = base['data'].shape
            e = base['errors']
            if(e.shape):
                if(len(e)==shape[0]): e = e.reshape((len(e),1))
            err.append(base['data']*e)
            E0 = base['param']['E0']
            Ek = base['data'].columns
            src = findsource(base['source'],abbrev=True)
            multi.append((E0,src))
            # for Ek,data in zip(*self.separateEk(base['data'])):
            #     # df = self.unfold(data,cross_section)
            #     # self.angles.update(data[:,0])
            #     df['source'] = base['source']
            #     df['year'] = base['year']
            #     df['subkind'] = base['subkind']
            #     df['state'] = base['state']
            #     if(df['year'] is None): df['year'] = 1960

            #     series.append(pd.Series(data[:,2],index=data[:,0]))
            #     serr.append(pd.Series(data[:,3],index=data[:,0]))
            #     self.ordata.setdefault(Ek,SortedList(key=DCS_Data._fitprior)).add(df)
        # self.energies.update(self.ordata.keys())
        multi = pd.MultiIndex.from_tuples(multi,names=['Primary','Source'])
        if(multi.nunique()!=len(multi)): 
            mask = multi.duplicated()
            raise RuntimeError('Duplicated values for %s'%str(multi[mask]))
        self.data = pd.concat(tabs,axis=1,keys=multi,sort=True).sort_index(axis=1,level=0)
        self.error = pd.concat(err,axis=1,keys=multi,sort=True).sort_index(axis=1,level=0)     

def cut(Eth,*c): # elementary functions from Tabata et al. (2006)
    c1,c2,c3,c4 = c[:4]
    c24 = c2+c4
    c1*=o
    if(len(c)==6):
        c5,c6 = c[4:6]
        c26 = c2+c6
        @nb.njit
        def f3(x):
            x = x/keV-Eth
            x[x<0] = 0 # zero values for energies below threshold
            return c1*(x/Ryd)**c2/(1+(x/c3)**c24+(x/c5)**c26)
        return f3
    else:
        @nb.njit
        def f2(x):
            x = x/keV-Eth
            x[x<0] = 0 # zero values for energies below threshold
            return c1*(x/Ryd)**c2/(1+(x/c3)**(c24))
        return f2

def sig(i,Eth,c,asymp=1): # analytical fits from Tabata et al. (2006)
    Eth/=keV
    if (i in (1,5)):
        f = cut(Eth,*c)
    elif(i==2):
        f1,f2 = cut(Eth,*c[:4]),cut(Eth,*c[4:7],c[3])
        f = lambda x: f1(x)+f2(x)
    elif(i==3):
        f1,f2 = cut(Eth,*c[:4]),cut(Eth,*c[4:])
        f = lambda x: f1(x)+f2(x)
    elif(i==4):
        f1,f2,f3 = cut(Eth,*c[:4]),cut(Eth,*c[4:8]),cut(Eth,*c[8:])
        f = lambda x: f1(x)+f2(x)+f3(x)
    elif(i==6):
        f1,f2 = cut(Eth,*c[:6]),cut(Eth,*c[6:])
        f = lambda x: f1(x)+f2(x)
    elif(i==7):
        c1,c2,c3,c4 = c
        c1*=o
        def f(x):
            x = x/keV
            return c1*np.log(x/Eth+c2)/(Eth*x*(1+(c3/(x-Eth))**c4))
    f.i = i
    f.param = c
    f.Eth = Eth*keV
    return f

states = {r'\Sigma':'Σ',r'\Pi':'Π',r'\Delta':'Δ',r'\Phi':'Φ'}
regstate = re.compile(r'[A-Za-z]?[\'\"]?\d{1,2}[SPDFΣΔΠΦ]_?[ug]?\^?[+\-°]?')
regmolcstate = re.compile(r'[A-Za-z][\'\"]?\d{1,2}[ΣΔΠΦ]_?[ug]?\^?[+\-]?')
regorbcore = re.compile(r'(\(?(?:\d[spdfσπδϕ]\d?)+\)?(?:\d[SPDFΣΔΠΦ](?:\d(?:/2)?)?[o°]?))?(\(?(?:[n\d][spdfσπδϕ][\d\'"]?(?![spdf]))+\)?)(\[\d(?:/2)?\])?(\d?[SPDFΣΔΠΦ])?((?<!\()\d(?:\/2)?(?!\)))?([o°])?')
regorbexc = re.compile(r'(\(?(?:[n\d][spdfσπδϕ][\d\'"]?(?![spdf]))+\)?)(\[\d(?:/2)?\])?(\d?[SPDFΣΔΠΦ])?((?<!\()\d(?:\/2)?(?!\)))?\^?[o°]?')
regatomstate = re.compile(r'(\(?(?:[n\d][spdfσπδϕ][\d\'"]?(?![spdf]))+\)?)(\[\d(?:\/2)?\])?(\d?[SPDFΣΔΠΦ])?((?<!\()\d(?:\/2)?(?!\)))?\^?[o°]?')
regUstate = re.compile(r'[A-Za-z]?[\'\"]?\d{1,2}(?i:[SPDFΣΔΠΦ]){1,2}_?[ug]?\^?[+\-°]?') # unlabelled states
regtrans = re.compile(r'[A-Za-z][\'\"]?\d{1,2}(?i:[SPDFΣΔΠΦ])?_?[ug]?\^?[+\-°]?')
regrot = re.compile(r'[Jj]\s*=\s*\d+\s*((=>|->?)\s*[\dH]+)?')
regrot_ = re.compile(r'[Jj]\s*=?\s*\d+\s*((=>|->?)\s*[\dH]+)?')
regvib = re.compile(r'[Vv]\s*=\s*\d+\s*((=>|->?)\s*[\dH]+)?')
regvib_ = re.compile(r'[Vv]\s*=?\s*(\d+)\s*(?:(?:=>|->?)\s*([\dH]+))?')
SPDF = str.maketrans('SPDF','ΣΠΔΦ')

def stateStandard(s,molc=True,strict=True):
    s = s.strip()   
        # s = re.sub(r'\s+.?=\d+->?\d+','',s) # remove all vibrational mention
    s = s.replace('singlet','1').replace('doublet','2').replace('triplet','3').replace('quadruplet','4').replace('quartet','4').replace('quintet','5')
    s = s.replace('!',"'").replace('′',"'").replace("''",'"')
    s = s.replace('_','') # Could be a separator
    if(molc):
        s = re.sub(r'\s*(?=.=)',':',s) # for rot or vib
        s = re.sub(r'(?<=\d)(=>|->?)(?=\d)','->',s) # standard arrow
        s = re.sub(r'(?<!\^)-(?=\w+)','',s) # Remove ambiguity due to dash (could be minus sign or just a separator)
        # s = s.replace('!',"'").replace('′',"'").replace("''",'"')
        s = re.sub(r'\\?prim?e?',"'",s,flags=re.IGNORECASE)
        s = re.sub(r'\(?\\?sigm?a?\)?','Σ',s,flags=re.IGNORECASE)
        s = re.sub(r'\(?\\?pi\)?','Π',s,flags=re.IGNORECASE)
        s = re.sub(r'\(?\\?delt?a?\)?','Δ',s,flags=re.IGNORECASE)
        s = re.sub(r'\(?\\?phi\)?','Φ',s,flags=re.IGNORECASE)
        if(not strict): # allow [SPDF] -> [Σ,Π,Δ,Φ] translation
            s = s.translate(SPDF)
    else:
        # s = re.sub(r'(?<=\d[spdf]\d)|(?<=\d[spdf]\d)\s')
        s = re.sub(r'(?<!\^)-(?=\w+)','',s) # Remove ambiguity due to dash (could be minus sign or just a separator)
        s = s.replace('o','°').replace('e','') # "e" for "even" is implicit for atoms
        s = re.sub(r'\((\d(?:/2)?)\)',r'[\1]',s) # K value in squared brackets
        s = re.sub(r'(?<!\()((?:[n\d][spdf][\d\'"]?(?![spdfSPDF]))+)(?=[^\)])',r'(\1)',s) # electronic configuration in parenthesis
    s = s.replace('^','')
    s = re.sub(r'(?<!\s\+)\s+(?!\+\s)','',s) # remove white spaces that are not between + signs
    # if(bare):
    #   s = re.sub(r'_?[ug]','',s)
    return s

def rotStandard(s,strict=True): # transform into J=\d->\d format
    s = s.replace('j','J').replace('_',' ')
    s = re.sub(r'(?<!\w)J\s*(?=\d(?!\d{2}))','J=',s) # Avoid Journal abbrev and year e.g. J 1984
    s = re.sub(r'(?<=\d)(=>|->?)(?=\d)','-',s)
    s = re.sub(r'(?<=-)J=(?=\d)','',s) # replace J=0-J=2 by J=0-2
    s = re.sub(r'(?<==)(?=\d+$)','0-',s)    
    return s.replace(' ','')

def vibStandard(s,strict=True): # transform into v=\d->\d format
    s = s.replace('V','v').replace('_',' ')
    if strict:
        s = re.sub(r'(?<!\w)v\s*(?==)','v',s)
    else:
        s = re.sub(r'(?<!\w)v\s*(?=\d)','v=',s)
    s = re.sub(r'(?<=\d)\s*(=>|->?)\s*(?=\d)','-',s)
    s = re.sub(r'\s*-\s*v=(?=\d)','-',s) # replace v=0-v=2 by v=0-2
    s = re.sub(r'(?<==)(?=\d+([^-]|$))','0-',s)
    return s.replace(' ','')

def analystate(S):
    ''' s = Spin multiplicity
        p = Parity u/g
        r = Reflection (Σ) +/-
        L = Orbital projection or Total momentum 
        M = Molecule ? Atom'''
    proprs = {'r':0}
    try: 
        s,L = re.findall(r'(\d)([ΣΠΔΦSPDF])',S)[-1]
        s = int(s)
    except IndexError:
        L = '?' 
        s = 0
    finally: proprs['s'] = s
    if(L in 'ΣΠΔΦ'): 
        proprs['M'] = True
        proprs['L'] = 'ΣΠΔΦ'.index(L)
        p = re.search('[ug]',S)
        if(p is not None): proprs['p'] = 1 if p.group()=='g' else -1
        else: proprs['p'] = 0
        if(L=='Σ'): proprs['r'] = 1 if '+' in S else -1 
    else: 
        proprs['M'] = False
        l,K,sL,J = regorbexc.search(S).groups()
        if(L in'SPDF'): proprs['L'] = 'SPDF'.index(L)
        if(J): proprs['J'] = eval(J)
        elif s==1: proprs['J'] = proprs['L']
        elif 'L' in proprs:
            spin = (s-1)/2
            if proprs['L']==0: proprs['J'] = spin
            else: 
                proprs['_J_'] = np.arange(abs(proprs['L']-spin),proprs['L']+spin+1) # J range
                proprs['J'] = -1
        else: proprs['J'] = -1
        if(K): proprs['K'] = eval(K[1:-1])
        else: proprs['K'] = proprs['J']-0.5 if "'" in S else proprs['J']+0.5
        # try: proprs['J'] = eval(re.search(r'(?<=[SPDF])\d(?:/2)?',S).group())
        # except AttributeError: proprs['J'] = float(re.findall(r'\d(?:/2)?',S)[-1])
        # try: proprs['K'] = eval(re.search(r'(?<=\[)\d(?:/2)?(?=\])',S).group())
        # except AttributeError: 
        # if(proprs['s']==0): proprs['s'] = 2*(proprs['J']-proprs['K']+0.5)+1
        proprs['l'] = 'spdf'.index(re.findall(r'(?<=[n\d])[spdf](?=[\d\'"]?\))',l)[-1]) # Last occupied orbital angular momentum
        proprs['p'] = -1 if ('o' in S) or ('°' in S) else 1
    return proprs    

def allowexc(s0,s1,default=None):
    ''' 0 - allowed
        1 - forbidden
        2 - doubly forbidden
        3 - spin forbidden '''
    try:
        p0 = analystate(s0)
        p1 = analystate(s1)
    except Exception as excp:
        if(default is not None): return default
        else: raise excp
    if(p0['s']!=p1['s']): return 3 # spin forbidden
    f = int(p0['p']*p1['p']>0) # if True, then parity does not change -> forbidden
    if(p0['M']): # Molecule
        
        if(p0['r']*p1['r']==-1): f = max(f,2) # Anti-Reflection produces type II forbidden transitions
        # a+= int(p0['r']!=p1['r']) # reflection must be conserved
        f+= int(abs(p0['L']-p1['L'])>1) # Angular momentum projection change > 1
    else:
        f = max(f,int(abs(p0['l']-p1['l'])>1)) # Parity of spherical harmonics (normally identical to the inversion parity)
        J0 = p0['J'] #if p0['J']!=-1 else p0.get('_J_',0)
        J1 = p1['J'] #if p1['J']!=-1 else p1.get('_J_',0)
        if J0!=-1!=J1: 
            ff = int(np.all(abs(J0-J1)>1) or np.all(J0+J1==0)) # Kinetic momentum change <= 1 and J=0->0 forbidden 
            # if((f | ff) and p0['s']!=p1['s']!=0): return 3 # spin forbidden 
        # elif(p0['s']!=p1['s']!=0): return 3 # spin forbidden 
        else: # not spin-forbidden multiplets
            J0 = p0.get('_J_',[J0])
            J1 = p1.get('_J_',[J1])
            # ff = abs(min(J1[-1]-J0[0],J0[-1]-J1[0]))>1  
            ff = int((J1[-1]+1<J0[0]) or (J0[-1]+1<J1[0])) # No overlap + 1
        f = ff | f
    return f

def gstate(S,target):
    if(target in co.Constants.ATOMS):
        try: g = gatom(S)
        except TypeError: g = 1
        except AttributeError: 
            logging.error('g undefined for %s(%s)'%(target,S))
            g = 1
        return g
    else: 
        try:
            g = int(next(re.finditer(r'\d(?=[ΣΠΔΦAB])',S)).group())
        except StopIteration: # Assume this is the ground state
            logging.warning('Assuming that the %s state of %s corresponds to its ground electronic state'%(S,target))
            gnd = co.Constants.GND_MOLC[target]
            try:
                g = int(next(re.finditer(r'\d(?=[ΣΠΔΦAB])',gnd)).group())
            except StopIteration: # Impossible to determine degeneracy
                logging.error('g undefined for %s(%s)'%(target,gnd))
                g = 1
        return g

def gatom(S):
    # print(S)
    if ' + ' in S: return np.sum(list(map(gatom,S.split(' + '))))
    l,K,sL,J = regorbexc.search(S).groups()
    if(J): return int(2*eval(J)+1)
    elif len(sL)==2: 
        s,L = sL
        return int(s)*(2*int('SPDF'.index(L))+1)
    else: return 1

def state_tolatex(s,nice=False): # 'nice' defines whether to use \prescript from amsmath
    s = re.sub(r'(?<!\s\+)\s+(?!\+\s)','',s) # remove white spaces that are not between + signs
    s = s.replace('°','o')
    if(nice):
        s = re.sub(r'"',r"^{\\prime\\prime}",s) # primes
        s = re.sub(r"'",r"^{\\prime}",s) # prime
        try:
            n,m,L,p,r = re.search(r'(.*)(\d)([ΣΠΔΦSPDFAB])([ug\d]?)([o+-]?)',s).groups()
            r = ('^'+r)*len(r)
            p = ('_'+p)*len(p)
            s = n+r'\,\prescript{%s}{}{%s}'%(m,L)+p+r
        except AttributeError:
            return s
    else:
        s = re.sub(r'"',"''",s) # quotes
        s = re.sub(r'(?<!_)(?=[ug])','_',s) # parity
        s = re.sub(r'(?<=[A-Za-zΣ])(?=[o+-])','^',s) # symmetry ! No spaces allowed before + !
        s = re.sub(r'(?<![\^=])(?=\d[ΣΠΔΦSPDFAB])','{}^',s) # spin degeneracy        
    s = re.sub(r'(?<=[spdf])(?=\d[^spdf])','^',s) # orbital occupation
    s = re.sub(r'(?<=[spdf])(?=\d[spdf])',r' ',s) # orbitals
    s = re.sub(r'(?<=[A-Za-z\'\"}])(?=\d)','_',s) # band index
    s = s.replace('->',r'\rightarrow')
    for l,r in states.items(): # for Greek letters
        s = s.replace(r,l)
    if s[0].isalpha() and not s[1].isalpha(): # Molecular band
        return s[0]+'$'+s[1:]+'$'
    else: return '$'+s+'$'

re_year = re.compile(r'(?<=\()?(?:19|18|20)\d{2}(?=\))?')
re_source = re.compile(r'((?:[A-Z]\.|[A-Za-zÀ-ÿĀ-ỿЀ-ԯ ,\-&\'\*])+)(\set al\.?\s+)?(\s[^\d]{4}[\w, .;:\-]*)?(?:[ \(]?((?:19|18|20)\d{2})\)?)([\w, .\-;:]*)')
re_author = re.compile(r'(?<=[A-Z]\.\s)?([A-Za-zÀ-ÿĀ-ỿЀ-ԯ\-&\'\*]{2,}\s?)+(?=[\s,]| [A-Z]|$)') # Discard single capital letters
def findsource(s,abbrev=False,default='?'):
    # if(abbrev): expr = re_source[:-2]
    # else: expr = re_source
    for sub in s.split('|'):
        res = re_source.search(sub.strip())
        if(res is not None): 
            if(abbrev):
                author, etal, jour, year, nal = res.groups()
                if(author.endswith(' et')): author += ' al' # BUGFIX : forgot the 'al' at the end
                # elif(etal): author += ' '+etal.strip()
                if(' et al' in author): 
                    etal = 'et al'
                    author = re.sub(r'\s*et al\s*\.?','',author)
                elif(not etal): etal = ''
                author = author.strip(',. \t\n')
                # authors = re.split(',|( and )',author)
                if(' and ' in author): _authors = author.split(' and ')
                elif(' & ' in author): _authors = author.split(' & ')
                else: _authors = author.split(',')
                authors = []
                for i,a in enumerate(_authors):
                    if(' journal 'in a.lower()): continue
                    a = re_author.search(a)
                    if(a): 
                        a = a.group().strip()
                        authors.append(a)
                        if('&' in a): break
                if(len(authors)>2 or etal): 
                    author = authors[0]
                    etal = ' et al'
                else: author = '&'.join(authors)
                if(abbrev=='short'): return '%s %d'%(author.strip(),eval(year))
                else: return '%s (%d)'%(author.strip()+etal,eval(year))
            else: return res.group().strip()
    if(re_year.search(s) is not None): return s.strip()
    else: return default

def findyear(s):
    year = re_year.search(s)
    if(year is None): return None
    else: return eval(year.group())

def sourcefilter(sources,incl=True,strict=False):
    if(callable(sources)): return sources
    elif(sources is True): return lambda s: s
    elif(isinstance(sources,collections.abc.Iterable)):
        joined = re.compile('|'.join(sources))
        if(strict): search = joined.match
        else: search = joined.search
        if(incl):
            def srcmatch(s):
                m = search(s)
                if(m is not None): return m.group()
                else: return ''
        else:
            def srcmatch(s):
                m = search(s)
                if(m is None): return s
                else: return ''
        return srcmatch
    else: return False

def splituncert(v,errdef=0):
    n = unumpy.nominal_values(v)
    s = unumpy.std_devs(v)
    if(errdef and np.any(s==0)):
        z = s==0
        if(np.isscalar(errdef) or errdef.ndim==0):
            s[z] = errdef*n[z]
        elif(len(errdef)==len(s)):
            s[z] = errdef[z]*n[z]
        else: raise RuntimeError('default errors should be scalar for\n%s',str(v))
    return n,s

RE_PARAM = re.compile(r'(?<![\(\[]) *,+ *(?![\]\)\d])|\s*[;:|]+\s*')
def splitparam(param,**vals):
    members = RE_PARAM.split(re.sub(r'(?<=[.\d])\s*,\s*(?=[.\d])',',',param),maxsplit=param.count('='))
    params = {}
    for member in members:
        if('='in member):
            n,v = re.split(' *= *',member,maxsplit=1)
            if(v.strip()==''): 
                logging.warning('Found empty parameter %s ... ignoring'%(n))
                params[n] = None
            elif(v[0]==v[-1]=='"' or v[0]==v[-1]=="'"): # This is meant to be a string
                params[n] = eval(v)
            elif('±' in v):
                params[n] = uncertainties.ufloat_fromstr(v)
            else: # could be anything else
                v = re.sub(r'(?<=\d)\s*(<?->?|&)\s*(?=\d)',',',v) # '<->' or '-' between two numbers expresses a range, '&' is simply stylistic for two numbers
                try: params[n] = co.Units.parseval(v,**vals)
                except NameError: params[n] = v # This parameter is a string
                except (SyntaxError,TypeError): params[n] = tuple(filehandler.finditer(v)) 
    return params

def sortproc_(proc,target):
    kind,_,final = proc.partition(':')
    if('excitation' in kind.lower() or 'inelastic' in kind.lower()): return dict(kind='EXCITATION',**sortexc(final,target,comment=kind,default=final))
    else:
        main,_,sec = kind.partition('_')
        g = (1,1) # state multiplicity
        if('dissoc'in main.lower()):
            sec = main.upper()
            main = 'EXCITATION'
            g = (1,2)
        if('ioni' in kind.lower()):
            main = 'IONIZATION'
            final = target+'+'+final
        return {'kind':main.upper(),'subkind':sec.upper(),'final':final,'g':g,'asymp':1}

def sortproc(kind,target,prod,comment,initial=None): # TODO correct g exc for vibrational excitations
    if(initial is None): gnd = 'X'+co.Constants.GND_MOLC[target]
    else: gnd = initial
    g0 = gstate(gnd,target)
    # if(',' in proc):
    #     proc,_,k = proc.rpartition(',')
    #     if('(' in proc and ')' not in proc): # The process was split in the middle of a parenthesis
    #         proc = proc+','+k # rebuild proc
    #         k = kind
    # else: k = kind
    # prod = re.split(r'->(?!\d)',proc,maxsplit=1)[-1].strip() # not confuse with transitions
    # prod = re.sub(r'E-?\s*\+','',prod,flags=re.IGNORECASE).strip() # Remove the primary electron in the reaction product
    # if(kind=='?'): kind = k.strip().upper()
    process = {'kind':kind,'g':(g0,g0),'final':gnd}
    if(kind=='ELASTIC'):
        # comment = comment.partition('|')[0]
        process.update(sortelast(prod+comment))
        # subkind = comment[:3] if comment[:3]!= 'ela' else '' # specify whether it is vib or rotationally elastic
        # process['final'] = gnd
    elif kind=='TOTAL': 
        if 'total' in prod.lower():
            process['subkind'] = 'TOTAL'
        else: process['subkind'] = ''#prod
        process['asymp'] = 1
    elif(kind.startswith('IONI')): # Ionisation
        if('partial' in (prod+comment).lower()): 
            process['subkind'] = 'PARTIAL' #process['final']!=target+'+' and not 'total' in comment.lower()
            prod = re.sub('partial','',prod,flags=re.IGNORECASE)
        elif('k-shell' in (prod+comment).lower()):
            process['subkind'] = 'K-shell'
            prod = re.sub('K-shell','',prod,flags=re.IGNORECASE)
        elif(prod!=target+'+' and not re.search('total|sum',(prod+comment),flags=re.IGNORECASE)): process['subkind'] = 'PARTIAL'
        else: 
            # prod = re.sub('total|sum','',prod,flags=re.IGNORECASE)
            prod = target+'+' # this is the total cross section anyway
            process['subkind'] = 'TOTAL'
        process['final'] = stateStandard(prod)
        process['asymp'] = 0 # Ionisation always comes with logarithmic tail
    elif(kind.startswith('ATT')): # Attachment
        process['final'] = stateStandard(prod)
        if('dissociative' in comment.lower() or target not in prod):
            process['subkind'] = 'DISSOCIATIVE'
        else:
            process['subkind'] = '3-BODY'
        process['asymp'] = 3 # attachment decreases very fast with energy
    elif(re.search(r' dissociation(?!\w)',prod+' '+comment,flags=re.IGNORECASE)):
        process['final'] = prod
        process['subkind'] = 'DISSOCIATION'
        process['kind'] = 'EXCITATION'
        process['g'] = (1,2)
        process['asymp'] = 0 # Usually comes with a logarithmic tail from optically allowed excitations
    elif(('('in prod) and (')' in prod)): # Excitation
        sub = prod[prod.find('(')+1:prod.rfind(')')].strip()
        process.update(sortexc(sub,target,comment=comment,default=sub,ini=gnd))
    elif(kind=='EXCITATION' or 'inelastic' in kind.lower()):
        process.update(sortexc(prod,target,comment=comment,default=prod,ini=gnd))
    else:
        process['subkind'] = ''
        process['asymp'] = 1
    return process

def grot(target,*j):
    j = np.array(j,dtype=int)
    g = 2*j+1
    if(target == 'N2'):
        g*=3
        g[j%2==0]*=2
    elif(target=='O2'):
        g[j%2==0]=0
    elif(target=='H2'):
        g[j%2==1]*=3
    return g

def sortexc(exc,target,comment='',default='?',ini=None):
    if(ini is None): gnd = 'X'+co.Constants.GND_MOLC[target]
    else: gnd = ini
    g0 = gstate(gnd,target)
    asymp = 1 # 1/ε
    full = exc+' | '+comment
    level = 0
    res = {}
    if('elastic' in full.lower() and not 'inelastic' in full.lower()): 
        res = sortelast(exc)
        res['g'] = (g0,g0)
        return res
    elif(target in co.Constants.ATOMS): 
        regstate = regorbcore # for atoms
        exc = exc.rpartition(':')[2]
        exc,_,comment = stateStandard(exc+' | '+comment,molc=False).partition('|')
        haselc = re.search(regstate,exc+' | '+comment)
        # if(not haselc): haselc = re.search(regorbcore,exc+' | '+comment)
        if ('electronic' in full.lower() or haselc):
            kind = 'ELECTRONIC'
            if('+' in exc and haselc): final = ' + '.join(list(''.join(r) for r in re.findall(regstate,exc)))
            elif haselc: final = ''.join(s for s in haselc.groups()[1:] if s) # get rid of core
            else: final = default
        else:
            final = default
            kind = 'ELECTRONIC'
        # g = 1+final.count('+') # count sum of energetically degenerate states
        try: g = gatom(final)
        except TypeError: g = 1
        except AttributeError: 
            logging.error('g undefined for %s(%s)'%(target,final))
            g = 1
    else: 
        regstate = regmolcstate # for molecules
        g = g0
        if ('rot' in full.lower()):
            kind = 'ROTATIONAL'
            res.update(sortrot(exc,target,comment,default,ini))
            final = res['trans']
            g0,g = g0*res['g'][0],g*res['g'][1]
        elif ('vib' in full.lower()):
            kind = 'VIBRATIONAL'
            res.update(sortvib(exc,target,comment,default,ini))
            final = res['trans']
        elif ('electronic' in full.lower()):
            kind = 'ELECTRONIC'
            elc = re.findall(regUstate,stateStandard(exc)) # allow unlabelled states
            if(elc): final = ' + '.join(elc)
            else: elc = re.findall(regstate,stateStandard(comment))
            if(elc): final = ' + '.join(elc)
            else: final = default
            g = np.prod(list(map(int,re.findall(r'\d(?=[ΣΠΔΦSPDF])',final))))
                # haselc = re.search(regtrans,stateStandard(exc))
                # if(haselc): final = haselc.group()
                # else: final = default
        else:
            g = 1
            kind = final = ''
            rot = sortrot(exc,target,comment,default,ini)
            if('final' in rot): 
                kind = 'ROT'+kind
                final = ','+rot['trans']
                res.update(rot)
                g0,g = res['g']                
            vib = sortvib(exc,target,comment,default,ini)
            if('final' in vib): 
                kind = kind[:-1]+'VIBR' # remove the 'T' from 'ROT'
                final = ':'+vib['trans']+final
            haselc = re.search(regstate,stateStandard(exc,strict=False)+' | '+stateStandard(comment))
            # if(not haselc):
            #     haselc = re.search(regstate,stateStandard(comment)) 
            #     if(not final and not haselc): final = '.'+exc
            if(haselc and 'X' not in haselc.group()): 
                kind += 'ONIC'
                final = '.'+haselc.group()+final
                g *= np.prod(list(map(int,re.findall(r'\d(?=[ΣΠΔΦSPDF])',final))))
            else:
                kind += 'ATIONAL'
            if kind=='ONIC': kind = 'ELECTR'+kind
            elif kind=='ATIONAL': 
                kind = '?'
                final = '.'+default
            final = final[1:]
    if(kind in ('ELECTRONIC','VIBRONIC')): 
        try: asymp = allowexc(gnd,final)
        except: logging.warning('Couldn\'t identify %s -> %s from %s'%(gnd,final,exc))
    res.update({'subkind':kind,'final':final,'g':(g0,g),'asymp':asymp})
    return res

def sortelast(exc):
    res = {'subkind':'INTEGRAL','final':'X','asymp':1} # Elastic cross section
    if(re.search('momentum|Qm',exc,flags=re.IGNORECASE)): res['subkind'] = 'MOMENTUM'
    elif(re.search('residual .* total',exc,flags=re.IGNORECASE)): res['subkind'] = 'RESIDUAL' # i.e. subtracted from total
    elif(re.search(r'Q([1-9])',exc,flags=re.IGNORECASE)): # Q0 = INTEGRAL 
        i = re.search(r'Q(\d)',exc,flags=re.IGNORECASE).groups()
        res['subkind'] = '%sst MOMENT'%i
    elif(re.search('viscosity|Qv',exc,flags=re.IGNORECASE)): res['subkind'] = 'VISCOSITY'
    elif(re.search('vibrationally',exc,flags=re.IGNORECASE)): res['subkind'] = 'VIBRATIONALLY'
    elif(re.search('rotationally',exc,flags=re.IGNORECASE)): 
        res['subkind'] = 'ROTATIONALLY'
        hasrot = re.search(regrot,rotStandard(exc))
        if(hasrot is not None): res['final'] = hasrot.group()
    elif(re.search('back',exc,flags=re.IGNORECASE)): res['subkind'] = 'BACKSCATT'
    return res

def sortrot(exc,target,comment,default,ini):
    hasrot = re.search(regrot,rotStandard(exc,strict=False))
    if not hasrot: 
        hasrot = re.search(regrot,rotStandard(comment,strict=True))
    if hasrot:
        trans = hasrot.group()
        j0,j =  list(map(lambda s: int(s.group()),re.finditer(r'\d+',trans)))
        g0,g = grot(target,j0,j)
        # g0,g = #(gj[0],g*gj[1])
        lev = co.Constants.ROT_MOLC[target]*(j0+1)*j0/eV
        return {'g':(g0,g),'final':'J=%d'%j,'initial':'%s:J=%d'%(ini,j0),'J':(j0,j),'trans':trans,'level':lev}
    else:
        return {'trans':rotStandard(default),'g':(1,1)}
    
def sortvib(exc,target,comment,default,ini):
    hasvib = re.search(regvib,vibStandard(exc,strict=False))
    if not hasvib:
        hasvib = re.search(regvib,vibStandard(comment,strict=True))
    if hasvib:
        trans = hasvib.group()  
        v = trans[2:].split('-')
        v0 = int(v[0])
        if len(v)==2: ve = int(v[1])
        else: ve = None # could be a vibrational dissociation
        # v0,ve = list(map(lambda s: int(s.group()),re.finditer(r'\d+',trans)))
        if(v0==0): lev = 0
        else: lev = pd.read_csv(os.path.join(ROOT,'vib','viblev.%s'%target),sep='\t',index_col=0,comment='#').at[v0,'Ev']#hw*v
        return {'final':'v=%s'%ve,'initial':'%s:v=%d'%(ini,v0),'trans':trans,'v':(v0,ve),'level':lev}    
    else:
        return {'trans':vibStandard(default)}
    
def filt(s):
    return re.match(r'Excitation:(?!N_2\^+)',s) is not None and ('=' not in s)

def loadfits(file,exc=True):
    tab = pd.read_csv(file,sep=r'\s{2,}').dropna(subset=['a_1'])
    if exc: tab = tab[tab['Process'].apply(filt)]
    tab['n'] = tab['n'].astype(int)
    tab['Eq.'] = tab['Eq.'].astype(int)
    exc = {p['Process']:sig(p['Eq.'],p['E_th']*keV,tuple(p['a_1':'a_12'])[:p['n']]) for i,p in tab.iterrows()}
    return exc

def loadproc(file,excl=['emission','production']):
    fits = loadfits(file,exc=False)
    processes = []
    target = file.split('.')[1].replace('e-','')
    for k,f in fits.items():
        proc = {'target':target,'comment':k}
        proc.update(sortproc_(k,target))
        if(proc['kind'].lower() in excl): continue
        proc['data'] = f.param
        proc['threshold'] = f.Eth/eV
        proc['iEq.'] = f.i
        proc['fit'] = f
        processes.append(proc)
    return processes

RE_ARROW = re.compile(r'<?->')

def writeproc_(file,proc): # Only for Tabata et al.
    with open(file,'at',encoding='utf8') as rf:
        for p in proc:
            final = p['final']
            if(final!=''):
                if(p['kind']=='IONIZATION'):
                    final='+'
                else:
                    final = '*(%s)'%p['final']
            chunk = headertabata.format(p['target'],p['kind'],p['threshold'],p['subkind'].capitalize(),final,p['param'],' | '.join(map(lambda i:'a'+str(i),range(1,len(p['data'])+1))))
            dat = ' \t'.join(map(lambda s :'%.3e'%s,p['data']))
            chunk += '-'*(len(dat)+5)+'\n'
            chunk+= dat+'\n'
            chunk+= '-'*(len(dat)+5)+'\n'*3
            rf.write(chunk)

def writeproc(file,proc,format='table'): # format = 'table' or 'param'
    with open(file,'at',encoding='utf8') as rf:
        for p in proc:
            final = p['final']
            if(final!=''):
                if(p['kind']=='IONIZATION'):
                    final='+'
                else:
                    final = '(%s)'%p['final']
                    if(p['final']!=co.Constants.GND_MOLC[p['target']]): # excited state
                        final = '*'+final
            param = p['param'].copy()
            param['Eth'] = '%g eV'%(p['threshold'])
            targetmass = co.Constants.MASS_MOLC[p['target']]
            pm = p['threshold'] if (p['threshold']!=0) else param.get('m/M',me/(targetmass*ma+me))
            param.pop('E',0)
            if('fitparams' in p):
                param.update(p['fitparams'])
            param = '; '.join(map(lambda t: '%s=%s'%t,param.items()))            
            if(format=='table'):
                if p['subkind'] == 'ROTATIONAL': #there is a special format for bolsig+
                    chunk = header.format(p['target'],'ROTATION',0,p['subkind'].capitalize(),final,param,' Energy (eV) | Cross Section (m2)',p['source'],str(datetime.today().date()))
                    chunk = chunk.replace('0.00000e+00','{0:.5f}    {1:d}\n{2:.5f}    {3:d}'.format(p['level'],p['g0'],p['level']+p['threshold'],p['gexc']))
                else:
                    chunk = header.format(p['target'],p['kind'],pm,p['subkind'].capitalize(),final,param,' Energy (eV) | Cross Section (m2)',p['source'],str(datetime.today().date()))
                dat = p['data'].iloc[:,:1].to_string(index=True,header=False,index_names=False)
            elif(format=='param'):
                c = p['fitparams']['c']
                chunk = header.format(p['target'],p['kind'],pm,p['subkind'].capitalize(),final,p['param'],' | '.join(map(lambda i:'a'+str(i+1),range(len(c)))),p['source'],str(datetime.today().date()))
                dat = ' \t'.join(map(lambda s :'%.3e'%s,c))
            chunk+= '-'*(len(dat.partition('\n')[0])+5)+'\n'
            chunk+= dat+'\n'
            chunk+= '-'*(len(dat.partition('\n')[0])+5)+'\n'*3
            rf.write(chunk)

def finderr(com,default=0.5,shape=()):
    errs = re.split('Errors? ?:',com,1,flags=re.IGNORECASE)
    if(len(errs)==1): return default
    else: 
        errs = errs[-1].split('|')[0].replace('%',' ').strip('. \n\t')
        alph = re.search('[A-z]',errs)
        if('ang' in errs): errs,_,ang = errs.partition(';') # discarding information about angular resolution for the time being
        if(alph): errs = errs[:alph.start()] # ignore descriptive trailing text
    if(re.search('[-–]',errs)): # Range of errors
        ini,fin = re.split('[-–]+',errs,maxsplit=1)
        try: 
            ini = eval(ini)
            if(type(ini) is tuple): ini = sum(ini)
        except: ini = filehandler.findtype(ini,float,True)
        try: 
            fin = eval(fin)
            if(type(fin) is tuple): fin = sum(fin)
        except: fin = filehandler.findtype(fin,float,True)
        if(shape):
            return 0.01*np.round(np.linspace(ini,fin,shape[0]))
        else: return (0.01*ini,0.01*fin)
    try: 
        errors = 0.01*np.array(eval(errs))
        if(not errors.shape): errors = [errors]
    except:
        try:
            errors = list(0.01*np.array(filehandler.finditer(errs)))
        except:
            errors = []
            if('#' in errs): errs = errs[:errs.find('#')].strip()
            sep = filehandler.findsep(errs,'.+')
            errs = errs.split(sep)
            for err in errs:
                err = err.strip().split()[0].replace('%','')
                # if('-' in err):
                #     err = err.split('-')[-1]
                try:
                    error = eval(err)*0.01
                    errors.append(error)
                except (ValueError, SyntaxError):pass
    if(len(errors)==0): return default
    elif(len(errors)==1): return errors[0]
    elif(shape and len(errors) not in shape): 
        logging.warning("Couldn't identify errors for :"+com)
        # else: errors = np.full(shape,errors[0])
    return errors

def parsecs(file,key='SPECIES',skip=True,**kwargs):
    logging.info('Reading : '+file)
    kwargs['regex']=True
    tables = filehandler.TableHandler.readtable(file,key=key,NA=filehandler.NA,index=True,**kwargs)
    processes = []
    for t in tables:
        if('@skip'in t.header or '#skip'in t.header): 
            if skip: continue
            else: t.header.pop('@skip')
        # elif(list(t.header.keys())[0] in ('VIBRATIONAL',)) : continue # Cannot treat such excitations for the time being
        try:
            processes.extend(parseproc(t))
        except Exception as ex:
            logging.error('Problem occurred with %s'%t.header)
            raise ex
    return processes

def parseparam(process,pm=None,headlines=[]):
    kind = process['kind']
    comment = process['comment']
    target = process['target']

    try: 
        pm = eval(pm,{},{})
        if(type(pm) is str): pm = None
    except (NameError,ValueError,SyntaxError): pm = None
    
    params = process.pop(PARAM.lower(),comment.rpartition(',')[0])
    if('#' in params): params = params[:params.rfind('#')].rstrip()    
    try:
        param = splitparam(params,eV=1,keV=1000,MeV=1000000) # eliminate eventual comment at the end of line
    except Exception as exc:
        if params not in comment:
            raise RuntimeError("Couldn't retrieve parameters from : %s"%params) from exc
        else: param = {} # this means that there are probably no parameters

    if(kind.startswith('ROTATION') or kind.startswith('VIBRATION')): 
        if kind.startswith('ROTATION'): process['subkind'] = 'ROTATIONAL'
        else: process['subkind'] = 'VIBRATIONAL'
        process['kind'] = 'EXCITATION' # Unified treatment sometimes the labelling varies "ROTATION" instead of "ROTATIONAL" as in Bolsig+
        if len(headlines)>=4: # Bolsig input with first row : kind; second row : process; third row : ini; fourth row : fin
            pm,pm2 = headlines[2:4]
            p1 = pm.strip().split()
            p2 = pm2.strip().split()
            if len(p1)==2==len(p2): # Level , grot
                param['g0'] = int(p1[1])
                param['g1'] = int(p2[1])
                param['E0'] = float(p1[0]) 
                param['E1'] = float(p2[0]) 
                param['E'] = param['E1']-param['E0']
    elif(kind in ('ELASTIC','MOMENTUM','TOTAL','EFFECTIVE')): # 'MOMENTUM' is elastic momentum transfer whereas 'EFFECTIVE' is total effective momentum transfer
        if(pm): param['m/M'] = float(pm)
        param['E'] = 0
    else: 
        if('E' in param): pass #param['E'] = np.array(param['E'])
        elif 'Eth' in param: param['E'] = param.pop('Eth')
        elif 'threshold' in param: param['E'] = param.pop('threshold')
        elif pm is not None: param['E'] = pm # At least identify threshold
        else: 
            thres = re.split('threshold',comment,flags=re.IGNORECASE,maxsplit=1)
            if(len(thres)==2):
                thres = re.search(filehandler.regextypes[float],thres[-1])
                if thres: 
                    param['E'] = float(thres.group())
            if('E' not in param): 
                logging.warning('No threshold found in %s for '%pm+comment)
                param['E'] = 0
        if(np.any(np.array(np.abs(param['E']))>1e9)): # If threshold is unphysical
            raise ValueError('Threshold units incorrect for %s, %s : %s'%(process.get('process',' '),process['source'],str(param['E'])))
    targetmass = co.Constants.MASS_MOLC.get(target,sum(co.Constants.MOLCS[target])*2)
    process['mass_ratio'] = param.setdefault('m/M',co.me/(targetmass*co.ma+co.me))
    process['param'] = param

    # print(param)

    return param

def parseheader(header):
    if(type(header) is str): header = header.split('\n')
    if(type(header) is list): 
        temp = {}
        for h in header:
            k,_,v = h.partition(':')
            temp[k] = v
        header = temp
    fullhead = (list(('%s:%s'%(k,v) if k!=v!='' else k) for k,v in header.items()))
    process = {k.lower():v for k,v in header.items() if k!=v!=''}
    process['comments'] = header
    headlines = ['' if (k!=v!='') else k for k,v in list(header.items())]
    kind, reaction, pm = headlines[:3]

    # Find kind 
    if(not kind.isupper() or not kind.isalpha()): 
        reaction, pm = kind,reaction
        kind = ''
    proc = process.setdefault('process',reaction) # prefer to extract from "process" row
    if(',' in proc):
        proc,_,k = proc.rpartition(',')
        if not kind: kind = k.strip().upper()
        if('(' in proc and ')' not in proc): # The process was split in the middle of a parenthesis
            proc = proc+','+k # rebuild proc
            k = kind
    elif (not proc): raise RuntimeError('Missing reaction identity in %s'%fullhead)
    else: k = kind
        # if(kind=='?'): kind = k.strip().upper()

        # try:
        #     coll,_,kind = process['process'].rpartition(',')
        #     kind = kind.upper().strip()
        #     if(not reaction): reaction = coll.strip()
        # except: raise RuntimeError('Cannot process table : \n',header)
    if(kind.startswith('MOMENTUM') or kind.startswith('RESIDUAL')): 
        kind = 'ELASTIC' # Unified treatment
        process['subkind'] = kind

    # Find reaction
    react = [s.strip() for s in  re.split(r'<?->(?!\d)',proc,maxsplit=1)] # not confuse with transitions
    ini = re.sub(r'((?<!\w)E-?\s*\+)+','',react[0],flags=re.IGNORECASE).strip() # Remove the primary electron in the reaction target
    prod = re.sub(r'((?<!\w)E-?\s*\+)+','',react[-1],flags=re.IGNORECASE).strip() # Remove the primary electron in the reaction product     
    
    target = process.get('species',ini).split('/')[-1].strip() # prefer to extract from "species" row    
    
    if(target not in ini): # Try retrieving target from ini instead
        if(ini in target): target,ini = ini,target # exchange them
        else:
            target = co.Constants.MOLC_NAMES.inv.get(target.capitalize(),None)
            if not target:
                raise RuntimeError('Unrecognised target %s, please consider adding its characteristics in the constants module'%target) 
            elif target not in ini: 
                raise RuntimeError('Inconsistent target %s in %s from %s'%(target,reaction,'\n'.join(fullhead)))
       
    if('(' in target and ')'==target[-1]): # excited state
        i = target.find('(')
        ini = target[i+1:-1]
        target = target[:i]
    elif('(' in ini and ')'==ini[-1]):
        i = ini.find('(')
        ini = ini[i+1:-1]        
    else:
        if('-'in target): # weird notation from some databases : ist 
            target = target.split('-')[0]
        if(target not in co.Constants.GND_MOLC):
            try:
                target = co.Constants.MOLC_NAMES.inv[target.capitalize()]
            except KeyError:
                raise RuntimeError('Unrecognised target %s, please consider adding its characteristics in the constants module'%target)     
        process['initial'] = co.Constants.GND_MOLC[target]

    process['kind'] = kind
    process['target'] = target
    process['product'] = prod
    comment = process.setdefault(COMMENT.lower(),'\n'.join(fullhead))
    source = findsource(comment,default=comment)
    if(source!=comment): comment.replace(source,'') # source has been already extracted from comment
    process['source'] = source
    process['comment'] = comment  

    # process params
    param = parseparam(process,pm,[h for h in headlines if h!=''])
    # process.update(parseparam(kind,param,pm,comment))

    # process initial state
    gnd = co.Constants.GND_MOLC[target]
    if('initial' not in process):
        if('X' in ini or ini in gnd): # Requires replacement of ground state
            process['initial'] = gnd
        elif regvib.match(ini): # This is a vibrational transition
            vi = int(regvib_.match(ini).groups()[0])
            process['initial'] = gnd+(':v=%d'%vi)*(vi!=0)
            param['level'] = pd.read_csv(os.path.join(ROOT,'vib','viblev.%s'%target),sep='\t',index_col=0).at[vi,'Ev']#hw*v
        elif regrot.match(ini): # This is a rotational transition
            Ji = int(regrot_.match(ini).groups()[0])
            process['initial'] = gnd+(':J=%d'%Ji)*(Ji!=0)
            param['level'] = co.Constants.ROT_MOLC[target]*Ji*(Ji+1)
        else:
            process['initial'] = stateStandard(ini,molc=target not in co.Constants.ATOMS)

    if(gnd!=process['initial'] and 'level' not in param):
        if 'E0' in param:
             param['level'] = param['E0']
        else: raise RuntimeError('Unspecified level for excited state %s : %s'%(process['target'],process['initial']))
    # else: 
    process['level'] = param.pop('level',0)  

    # process.update(sortproc('\n'.join(header.values()),process['target']))
    return process

def parseproc(tab,renorm=True):
    processes = []
    process = parseheader(tab.header)
    kind = process['kind']
    param = process['param']
    target = process['target']
    comment = process['comment']

    units = [(u if u!='' else tab.units[-1]) for u in tab.units]
    scales = np.array([co.Unit.parseval(u,eV=1.,keV=1e3,MeV=1e6) for u in units])
    if(scales[0]!=1): tab.index *= scales[0] # energies in eV
    tab *= scales[-len(tab.columns):] # scale[0] could be hidden in index
    if('eV'in units[0]): scales[0] = eV # restore original value of energy unit
    process['units'] = scales  
    errors = np.array(finderr(comment,default=np.nan,shape=tab.values.squeeze().shape)) # Default = 50 percent of error !

    
    if(len(tab.columns)>1 and re.search('Energy|Ek',tab.index.name,flags=re.IGNORECASE) and not re.search('Error',tab.columns[-1],flags=re.IGNORECASE)): # Many different states across columns
        if(not errors.shape): errors = np.array([errors]*len(tab.columns)) # Scalar
        elif(errors.shape==tab.shape): errors = errors[0] # Errors along columns
        elif(len(errors)==len(tab)): errors = np.vstack([errors]*len(tab.columns)) # Errors along energies
        elif(len(errors)!=len(tab.columns)): raise RuntimeError('Inconsistent errors for \n\t'+'\n'.join(tab.header.values()))
        
        if(renorm):
            if ('renorm' in param): 
                tab*=np.array(param['renorm'])
                process['source'] = '*'+process['source'] # Show that they are renormalised
            elif 'Renormalised' in process['source']:
                process['source'] = process['source'].replace('Renormalised ','*')
        sub = tab.columns
        if(kind=='ELASTIC' or kind=='TOTAL'): param['E'] = (0,)*len(sub)
        elif(len(param['E'])!=len(sub)): raise RuntimeError('Inconsistent energy threholds for :\n\t'+'\n'.join(tab.header.values()))
        finals = []
        fullhead = (list(('%s:%s'%(k,v) if k!=v else k) for k,v in process['comments'].items()))
        for i,(s,u) in enumerate(zip(sub,units[1:])):
            col = tab.loc[:,[s]]
            proc = process.copy()
            proc['threshold'] = param['E'][i]
            proc['param'] = {'E':proc['threshold']}
            if(len(errors.shape)>1): proc['error'] = errors[i][~col.isna().squeeze()]
            else: proc['error'] = errors[i]                
            proc['data'],proc['error'] = gentab(col.dropna(),proc['error'])
            fullhead[-1] = 'COLUMNS: Ek (eV) | CS ({0}) | Error ({0})'.format(u)
            proc['comment'] = '\n'.join(fullhead).replace('*','*(%s)'%s)
            proc['units'] = np.array([scales[0],scales[i+1]])
            proc.update(sortproc(kind,target,s,process.get('subkind',process['process'])+' | '+comment,process['initial']))
            if(proc['final'] in finals): # This should be unique for the same source !
                proc['final'] = s.strip()
            finals.append(proc['final'])
            processes.append(proc)
    else: # single process
        process.update(sortproc(kind,target,process['product'],process.get('subkind',process['process'])+' | '+comment,process['initial']))
        if('asymp' in process['param']): process['asymp'] = process['param']['asymp']
        for k in process['param']:
            if(re.fullmatch(r'g|g1/g0',k)): # statistic weight
                g0 = process['g'][0]#gstate(co.Constants.GND_MOLC[target],target)
                g1 = int(np.round(process['param'][k]*g0)) if 'g1/g0' in k else process['param'][k]
                process['g'] = (g0,g1)
        if(renorm and 'renorm' in param): 
            renorm = np.array(param['renorm'])
            if renorm.shape: renorm = renorm[:,None]
            tab *= renorm
            process['source'] = '*'+process['source'] # Show that they are renormalised
        Ekloss = param['E']
        if('fcf' in param):
            if(param['fcf']=='file'): # load Franck-Condon Factors
                process['threshold'] = Ekloss
                try:
                    fcf = tarFC[target][process['final']].dropna()
                    Ek,FC = fcf['Ek'],fcf['FC']
                    process['FCF'] = np.column_stack((Ek,unumpy.nominal_values(FC))) # Standard format for FCF
                except KeyError:
                    raise RuntimeError('Franck-Condon factors for %s(%s) not in database, please include them'%(target,proc['final']))
            else:
                process['threshold'] = Ekloss[0]
                process['FCF'] = np.column_stack((Ekloss,param['fcf']))
        elif(np.isscalar(Ekloss)): process['threshold'] = Ekloss
        else: 
            process['threshold'] = Ekloss[0]
        process['comments'] = tab.header#comments
        process['error'] = errors
        if(tab.shape[0]<2 and not re.match('Energy',tab.index.name,flags=re.IGNORECASE)): # One-row data without energy in columns -> fitting parameters
            c = tab.reset_index().to_numpy().squeeze()
            process['cerr'] = unumpy.std_devs(c)
            c = unumpy.nominal_values(c)

            # try: 
            #     c,cerr = zip(*[(num.n,num.s) for num in c])
            #     process['cerr'] = cerr
            # except: pass
            if c[1]==0: 
                c = list(c)
                c[1] = 1e-20 # get rid of singularity at Ek = Eth for optically allowed excitations
                c = tuple(c)
            params = {'c':c,'asymp':process['asymp']}
            for k,v in process['param'].items():
                if(re.fullmatch('E(th)?',k.strip())):
                    if(hasattr(v,'__len__')): params['Eth'] = v[0]
                    else: params['Eth'] = v
                elif(re.match(r'(Eq\.?)|([Nn]o\.?)|i',k.strip())):
                    if(type(v) is str and v.isnumeric()): params['eq'] = int(v)
                    else: params['eq'] = v
            # process['fit'] = sig(**params)
            process['fit'] = cscoll.Excitation.genexc(**params) #sig(**params)
            process['fitparams'] = params
            process['data'] = params['c'] # parameters of fit
            if('a' in params['eq'] and params['asymp']!=0): raise ValueError('Optically allowed %s undetected'%(process['process']))
        elif kind == 'IONIZATION' and len(tab.columns)>=2 and 'RBE' in comment and 'B'==tab.index.name:
            tab = tab.reset_index()
            # tab['B']*=scales[0]
            B,U,N,Q = tab['B'].values*eV,tab['U'].values*eV,tab['N'].values,tab.get('Q',param.get('Q',1))
            process['data'] = tab
            if('Q' not in param and 'Q' not in tab): 
                logging.warning('Q value not specified for RBEQ model of %s , taking Q=1 by default'%target)
            else: 
                Q,param['Qerr'] = splituncert(Q)
            param['Q'] = Q
            process['fit'] = cscoll.Ionisation.genRBEQ(process['target'],Q,BUN=(B,U,N))
        else: # This is a table with Ek vs. CS
            process['data'],process['error'] = gentab(tab,process['error'],units[-1] in ('%','percent'))
        processes = [process]
    return processes

def gentab(tab,err=None,percent=False):
    if err is None: err = np.nan
    c = tab.columns[0]
    if(tab.dtypes[c].kind=='O'): # at least one element is an uncertainty object
        norm,std = splituncert(tab[c],err)
        # if(err.shape):
        #     if(len(err)==len(tab)): # percentage at each energy
        #         # e = tab[c]*err
        #         normstd = np.array(splituncert(tab[c],err))
        #         # i = list(tab[c])
        #         # normstd = np.array(list(zip(*tab[c].apply(lambda v:(v.n,v.s) if hasattr(v,'n') else (v,e[i.index(v)])))))
        #     else: raise RuntimeError('default errors should be scalar for\n%s',str(tab[c]))
        # else: normstd = np.array(list(zip(*tab[c].apply(lambda v:(v.n,v.s) if hasattr(v,'n') else (v,v*err)))))
        data = pd.DataFrame(np.column_stack((norm,std)),index=tab.index,columns=('CS','Error')) # Pandas style array
        # data = np.column_stack((tab.index,norm,std)) # Numpy style array
        mask = norm==0
        norm[mask] = 1
        e = np.median(err)
        err = std/norm 
        err[mask] = e
    elif(len(tab.columns)==2 and 'Error' in tab.columns[1].capitalize()):
        data = tab.rename(columns={c:'CS',tab.columns[1]:'Error'})#.to_numpy()
        if(percent): 
            err = data['Error'].values.copy()
            data['Error'] *= data['CS']
        else:
            err = (data['Error']/data['CS']).values
    else:
        data = tab.rename(columns={c:'CS'})#.to_numpy()
        if not np.all(np.isnan(err)):
            data['Error'] = data['CS']*err
    return data,err

def parserot(target,rot,DJ):
    raise NotImplementedError('Rotational CS creation not yet implemented, sorry !')

def parsevib(target,elast,exc,deexc,cs_min=1e-26): 
    elast.rename(columns={'sigma':'CS','E':'Energy'},inplace=True)
    elast.index.name = 'Energy'
    elast['Error'] = 0.25*elast['CS']
    exc.rename(columns={'sigma':'CS','E':'Energy'},inplace=True)
    deexc.rename(columns={'sigma':'CS','E':'Energy'},inplace=True)
    gnd = 'X'+co.Constants.GND_MOLC[target]
    proc = {'kind':'ELASTIC','subkind':'VIBRATIONALLY','final':'(vib)','asymp':1,'g':(1,1),'target':target,'threshold':0,'mass_ratio':me/(co.Constants.MASS_MOLC[target]*ma+me),
            'initial':'(vib)','product':target+'(vib)','data':elast,'units':(eV,1),'source':'Laporta et al. (2014)','level':0}
    processes = [proc] # First process is always the vibrationally elastic 
    for i,ed in enumerate([exc,deexc]):
        if(i==0):pre=''
        else: pre='de'
        for g in ed.group.unique(): 
            vib = ed[ed.group==g]
            de = vib['dE'].median()
            if('v_f' in vib and 'v_i' in vib): final = 'v=%d-%d'%(vib['v_i'].unique()[0],vib['v_f'].unique()[0])
            else: final = 'vib'+'+-'[i]+str(g+1) # must be unique
            header = {'EXCITATION':'',target+' -> '+target+'(%s)'%final:'','%g'%de:'','SPECIES':'e / %s'%target,'PROCESS':'e + %s -> e + %s(%s)'%(target,target,final),'COMMENT':'Vibrational %sexcitation grouped from excited states | Laporta et al. (2014)'%pre}
            vib = vib.drop(columns=['dE','group','v_i','v_f'],errors='ignore').set_index('Energy')
            with warnings.catch_warnings(record=True) as w:
                vib.header = header
                vib.units = ['eV','m2']
            processes.extend(parseproc(vib))
    return processes

def parsediff(file,format='list',renorm=True,**kwargs):
    ''' Parse differential cross sections into the specified format 
    Parameters
    ----------
        file : str path to DCS file
        format : str - 'grid' or 'list' for DCS arranged in Angle x Energy grid or [Angle,Energy,DCS] list
    Returns:
    --------
        list of parse DCS data into specified format
    '''
    tables = filehandler.TableHandler.readtable(file,NA=filehandler.NA,**kwargs) # do not put angles as index because table might have to be stacked
    dico = []
    
    for t in tables:
        if('@skip'in t.header): continue
        d = parseheader(t.header)
        # d = {k.lower():v for k,v in t.header.items()}
        # line = t.header['PROCESS']
        # d['target'] = t.header['SPECIES'].split(' ')[-1].strip()
        # d['kind'] = line.split()[-1].strip().upper()
        # com = t.header.get('COMMENT','?')
        param = d['param']
        if d['source']!='?':
            d['year'] = findyear(d['source'])
            if renorm and 'renorm' in param: d['source'] = '*'+d['source']
        else:
            logging.warning('Unknown source for %s @ %s'%(d.get('process',d['target']),d.get('param.','E='%t.iloc[0,1])))
            d['source'] = '#Unknown#'
            d['year'] = None
        com = d['comment']
        d.update(sortproc(d['kind'],d['target'],d['product'],comment=com,initial=d['initial']))#''.join([el[1:-1] for el in re.findall('\(.*\)',line)])
        d['state'] = d['final']
        energy = param.get('E',[])

        if 'ROWS' in t.header and 'CELLS' in t.header: # special format for matrix-like table
            cols = t.header['COLUMNS']
            nc,_,cols = cols.partition('=')
            c,uc = co.Unit.splitunits(cols,deg=1,eV=1)
            r,ur = co.Unit.splitunits(t.header['ROWS'],deg=1,eV=1)
            cols = eval(c,{'np':np})*uc
            m,um = co.Unit.splitunits(t.header['CELLS'])
            scales = np.array([ur]+[um]*len(cols))
            t.columns = [r.strip()]+list(cols.astype(str)) # Ensures that all columns are of the same type
        else:
            units = []
            
            if 'integra' in t.columns[-1].lower() and t.units[-2]!='':
                defaultunit = t.units[-2]    
            else: defaultunit = t.units[-1]            
            for i,u in enumerate(t.units):
                if u=='':
                    if ('Energy' in t.columns[i] or 'Angle' in t.columns[i]): # for energies or angles
                        _,u = co.Unit.splitunits(t.columns[i],parse=False)
                    else: u = defaultunit
                units.append(u)
            # units = [(u if u!='' else co.Unit.t.units[-1]) for u in t.units]

            cols = []
            # preserve degs, eVs and keVs
            scales = np.array([co.Unit.parseval(u,deg=1,eV=1,keV=1000,MeV=1e6) for u in units])
        t *= scales[-len(t.columns):] # scale[0] could be hidden in index
        if('Angle' not in t.columns[0].capitalize()):#.startswith('Angle')): # Angles are columns !
            if(len(cols)): angs = cols
            else: 
                if('integra' in t.columns[-1].lower()): # last column gives integrated DCS 
                    integ = t.iloc[:,-1] # integral
                    d['Integrated'] = integ
                    t = t.iloc[:,:-1]
                angs = [co.Unit.parseval(a.split()[0],deg=1) for a in t.columns[1:]]
            tt = t.set_index(t.columns[0])
            tt.columns = angs
            t = tt.T.reset_index()
            t.columns = t.columns.astype(str) # Just in order to be searchable in the next section
        t.rename({t.columns[0]:'Angle'},axis=1,inplace=True)

        errors = finderr(com,default=0.25,shape=(len(t),len(t.columns)-1))
        if format=='list':
            # t = dcs_grid2list(t,energy)
            
            if(len(t.columns)==2): # Angle and DCS
                # t.reset_index(inplace=True)
                assert(np.isscalar(energy)), 'Multiple energies given %s for %s'%(str(energy),'\n'.join(t.header.values()))
                t.insert(1,'Energy',energy)
                if(renorm and 'renorm' in param): t.iloc[:,2:] *= np.array(param['renorm'])
                # t['Error'] = t.loc[:,t.columns[-1]]*errors
            elif 'Energy' in t.columns[1].capitalize(): # Angle, Energy, DCS
                if 'Energy' != t.columns[1]: t.rename(columns={t.columns[1]:'Energy'},inplace=True)
                if(renorm and 'renorm' in param): t.iloc[:,2:] *= np.array(param['renorm'])
                # t['Error'] = t.loc[:,t.columns[-1]]*errors
            elif(len(t.columns)==3 and 'Error' in t.columns[-1].capitalize()): # Angle, DCS, Error
                t.insert(1,'Energy',energy)
                if(renorm and 'renorm' in param): t.iloc[:,2:] *= np.array(param['renorm'])
            else:  # multiple energies
                if(type(energy) not in (tuple,list) or len(t.columns)-1!=len(energy)): energy = [None]*(len(t.columns)-1) # in case E is given as a range, it is forgiven, energies will be read individually
                else: energy = list(energy)
                    # try: float(t.columns[1].split()[0])
                    # except ValueError: 
                    #     tt = t.set_index('Angle').T
                for j,c in enumerate(t.columns[1:]):
                    Ek = None
                    try:
                        Ek = float(c.split()[0]) # Normally energy should be the first value in the column name
                    except IndexError: pass # when no number found
                    except ValueError:
                        if(energy[j]is None and 'eV' not in c): # These are not energies but a different final state !
                            energy[j] = Ek = sortproc(d['kind'],d['target'],c,d['comment'],d['initial'])['final']      
                        else: # try to find a number
                            try: # This is to check that the energy given is compatible with the one in the column
                                Ek = float(re.search(filehandler.regextypes[float]+r'\s*(?=eV)',c).group())
                            except AttributeError: pass 
                    finally:
                        if None!=energy[j]!=Ek: raise ValueError('Energy mismatch : %g!=%g for column %d in table :\n%s'%(Ek,energy[j],j,str(t)))
                        energy[j] = Ek
                if None in energy: raise ValueError('Could not identify energies for %s'%(t.columns[1+energy.index(None)]))
                t.columns = ['Angle']+energy
                t.columns.name = 'Energy'
                if(renorm and 'renorm' in param): 
                    t.iloc[:,1:] *= np.array(param['renorm'])
                t = t.set_index('Angle').stack().reset_index(name='DCS').sort_values(['Energy','Angle'],axis=0)
            # t.iloc[:,2]*=scale # only DCS
            if(not np.isscalar(t.iloc[0,-1])): # Contains uncertainties
                t.iloc[:,-1],errors = splituncert(t.iloc[:,-1])
                # errors = t.iloc[:,-1].apply(uncertainties.std_dev)
                # t.iloc[:,-1] = t.iloc[:,-1].apply(uncertainties.nominal_value)
                t.insert(len(t.columns),'Error',errors)
            # elif(len(t.columns)>3): t.iloc[:,3] *= co.Units.parseval(t.units[-1])
            else: d['errors'] = errors
            if(t['Energy'].dtype=='O'): # these are not energies but states !
                energy = param.get('E',[])
                for i,s in enumerate(t['Energy'].unique()):
                    dd = d.copy()
                    tt = t.loc[t['Energy']==s,:].copy()
                    tt.loc[:,'Energy'] = energy
                    dd['data'] = np.asarray(tt,dtype=float)
                    dd['final'] = dd['state'] = s
                    if(len(t.columns)==3):
                        dd['errors'] = d['errors'][i]
                    else:
                        del dd['errors']
                    dico.append(dd)
            else:
                d['data'] = np.asarray(t,dtype=float)
                dico.append(d)
        elif format=='grid':
            t = dcs_list2grid(t)
            d['errors'] = errors
            d['data'] = t
            dico.append(d)
    return dico

def dcs_grid2list(data,energy): # convert a Angle x Energy [DCS] table into a listing with [Angle,Energy,DCS] sorted by Energy
    for i in range(len(data.columns)-1,-2,-1): #Find whether single or multiple DCS
        if re.match('(Diff.*[ \t]+[cC]ross[ \t]+[sS]ection)|DCS',data.columns[i],flags=re.IGNORECASE):break
    scale = co.Units.parseval(data.units[i])
    if(len(data.columns)==2):
        # data.reset_index(inplace=True)
        assert(np.isscalar(energy)), 'Multiple energies given %s for %s'%(str(energy),'\n'.join(data.header.values()))
        data.insert(1,'Energy',energy)
    elif 'Energy' in data.columns[1].capitalize():
        if 'Energy' != data.columns[1]: data.rename(columns={data.columns[1]:'Energy'})
    else:  # multiple energies
        if(len(data.columns)-1!=energy): energy = [None]*(len(data.columns)-1)
        for j,c in enumerate(data.columns[1:]):
            try: energy[j] = float(c.split()[0]) # Normally energy should be the first value in the column name
            except ValueError: # Otherwise, look for a number
                try: energy[j] = float(re.search(filehandler.regextypes[float],c).group())
                except AttributeError: pass
            except IndexError: pass # when no number found
        if None in energy: raise ValueError('Could not identify energies for %s'%(data.columns[1+energy.index(None)]))
        data.columns = ['Angle']+energy
        data.columns.name = 'Energy'
        data.set_index('Angle').T.stack().reset_index(name='DCS')
    data.iloc[:,2]*=scale
    return data

def dcs_list2grid(data): # convert a listing with [Angle,Energy,DCS] into a Angle x Energy [DCS] table
    if 'Angle' in data.columns and 'Energy' in data.columns: 
        return data.pivot(index='Angle',columns='Energy')
    else:
        if 'Angle' in data.columns[0]:
            data.set_index(data.columns[0],inplace=True)
        if(data.columns.dtype=='O'): # str -> convert to floats
            data.columns = [float(c.split()[0]) for c in data.columns]
        return data

def check_dcs_table(data):
    units = list(data.units)
    if 'Angle' != data.index.name:
        if('Angle' not in data.index.name): raise RuntimeError('Angles not in table %s'%'\n'.join(data.header.values()))
        else: data.index.name,units[0] = 'Angle',data.index.split()[-1]
