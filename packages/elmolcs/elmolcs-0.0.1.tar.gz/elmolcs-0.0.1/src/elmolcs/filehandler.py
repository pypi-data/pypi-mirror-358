# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 12:02:47 2018

Copyright (C) 2023 
@author: Anthony Jeseněk
"""

import csv
import re
import logging
import warnings
import numpy as np
import pandas as pd
import uncertainties
import functools
from datetime import datetime


# regex look for non-ASCII character : [^\x00-\x7F]

fileformats = {}

# NA = '(?<!e)[-–]{1,3}(?![.0-9])'
NA = '-−–—'
regNA = r'(^|(?<=\s))[%s]{1,3}(?=$|\s)' # Also match at beginning or end of string
regextypes = {float:r'[+-]?((?:\d+\.?\d*)|(?:\d*\.?\d+))(?:e[+-]\d+)?',int:r'[+-]?\d+',str:'.*'}

def writetable(file,table,sep='\t',header='',line='-',**kwargs):
    ''' Writes a table (DataFrame, Series or array object) into a `csv' file.
    The separator (sep), header and beginning and ending line strings can be specified 
    as well as any keyword arguments taken by the `to_csv' routine of pandas objects or 
    the `savetxt' routine of numpy. The format with a header would be as follows:

    <Header of the table>           -> header
    ------------------------        -> line * len(header)
    0.0\t0.0                        -> table with sep = '\t'
    ...

    0.0\t0.0
    ------------------------        -> line * len(header)
    '''
    if(kwargs.pop('mkdir',False)): buildpath(file)
    line*=len(header.strip().split('\n')[-1]) if header!=''!=line else 0
    if(header!=''!=line and header[-1]!='\n'):header+='\n'    
    if(type(table) in (pd.DataFrame,pd.Series)):
        index = kwargs.pop('index',type(table) is pd.Series) 
        with open(file,'wt+') as wfile: wfile.write(header+line+'\n')
        table.to_csv(file,sep=sep,index=index,na_rep='—',**kwargs,mode='a')
    else:
        columns = kwargs.pop('columns','')
        if columns: header+= ' | '.join(columns)+'\n'
        fmt = kwargs.pop('fmt','%g') 
        np.savetxt(file,table,fmt=fmt,header=header+line,footer=line,delimiter=sep,comments='',**kwargs)
    with open(file,'at') as wfile: wfile.write(line) # finish line of table

class TableHandler:
    ''' Reads a file and tries to find anything that looks like a table (preferable more than one row and more than one column)
    Takes anything that precedes the numerical values as the header of the table (explanatory notes, columns, units.) 
    It also tries to identify the column titles and their units'''

    colsep = [',',';','\t',' '] # Separators used in table
    metasep = [':','=',';'] # Separators used for rows in information header
    headsep = [',','|',';','\t',' '] # Separators used in column header
    strip = ' \t\n#'
    renum = '[+-]?([0-9]*[.])?[0-9]+(e?[-+]?[0-9]+)?'
    reunit = r'[A-Z]{1,3}\^?[+-]?\d?'
    re_unit = re.compile('(%s)?'%regextypes[float]+r'\s+(%s)([\*/\.](%s))*(?!\w)'%(reunit,reunit),flags=re.IGNORECASE)

    def __init__(self,fname):
        self.fname

    @classmethod
    def writetable(cls,*args,**kwargs): writetable(*args,**kwargs)

    @classmethod
    def readtable(cls,file,format=None,key='',sep='undefined',skip='#',NA=None,regex=False,index=False,numeric=True,codec='utf8',multi=False,minrow=1): # TODO test for general table file
        ''' Read all tables in file with 

        Parameters
        ----------
        format : str (None) - format of file, if None then guesses from the extension, if 'txt' then parses as a text, if str then parses the text in the 'file' as the content of the table
        key : str, callable - if given, searches for tables that have the key in their header
        sep : str - separation marker between columns
        skip : str, callable - if skip is one character : skips all lines that start with that character
                                elif skip is a string : skips all lines that contain skip
                                elif skip is callable : skips all lines that return True
        NA : str - special character(s) (or regex) for non-assigned values (blank cells in table)
        regex : bool (False) - interpret key as a regular expression
        index : bool, int, str (False) - automatically attribute index to the column (first if True, .iloc[index] if integer or [index] if string) 
        numeric: bool - does the table contain only numbers ?
        multi : bool - are the indexes and columns multi ? 
        minrow: int - minimal number of rows in table (1) '''
        if(type(key)is list or type(key) is dict): # this is inefficient, but the user has the choice to use a regex key if wanted
            return {k:cls.readtable(file,format,k,sep,skip,NA,regex,index,numeric,multi) for k in key}
        else: assert not key.isnumeric(), 'Cannot use a numeric key for finding a table !'
        if(skip is None or skip==''): skiprow = lambda s: False
        elif(type(skip) is str):
            if(len(skip)==1): # One character comment
                skiprow = lambda s: (skip == s.strip()[:1])
            else: # Interpreted as anti-key 
                if(regex): skiprow = lambda s: re.search(skip,s) is not None
                else: skiprow = lambda s: skip in s
        else: 
            if(skip('0')): skiprow = lambda s: skip(s) and not s.strip()[:1].isnumeric() # Should not skip numerical values ! 
            else: skiprow = skip
        if key:
            if(regex): start = lambda s: re.search(key,s)
            else: start = lambda s: s.lstrip().startswith(key) or key in s and not str.isnumeric(s.strip()[0])
        else: start = lambda s: s.strip()!='' #and not str.isnumeric(s.strip()[0])
        if(NA in ('+','-')): NA = regNA%NA
        elif(NA == '.'): NA = r'(?<![0-9])\.+(?![0-9])'
        elif type(NA) in (list,tuple): NA = regNA%(''.join(map(str,NA)))
        elif type(NA) is str and not NA.startswith(regNA[:10]): NA = regNA%NA
        if(index): index = cls.assign_index(index)
        if format is None: # guess the format from file extension
            if ('.' in file): format = file.partition('.')[2]
        if(format=='csv'):
            with open(file,'r') as rf:
                reader = csv.reader(rf,delimiter=',')
                reading = True
                while reading:
                    row = next(reader)
                    if(len(row)==1 and str.isnumeric(row[0])):
                        rows = int(row[0])
                        fields = next(reader)
                        array = []
                        for i in range(rows):
                            row = next(reader)
                            row = [float(r) for r in row if r!='']
                            array.append(row)
                        reading = False
                        return pd.DataFrame(array,columns=fields)
        elif(format==str): # Table is directly input as a string
            rf = io.StringIO(file)
            return cls.parsetable(rf,key=key,start=start,sep=sep,skip=skiprow,NA=NA,index=index,numeric=numeric,multi=multi,minrow=minrow)
        else:
            with open(file,'rt',encoding=codec) as rf:
                return cls.parsetable(rf,key=key,start=start,sep=sep,skip=skiprow,NA=NA,index=index,numeric=numeric,multi=multi,minrow=minrow)

    @classmethod
    def parsetable(cls,reader,key='',**kwargs):
        tables = []
        index = kwargs.pop('index',False)
        searching=True
        while searching:
            try:
                tab = cls.findtable(reader,**kwargs)
                if index: index(tab)
                tables.append(tab)
            except StopIteration: searching=False
            except KeyError as k:
                raise KeyError("Couldn''t find any corresponding index in %s "%tab.header+str(k))
            except ValueError:
                raise ValueError("Problem encountered above line : %s"%next(reader))
            # except Exception as e: logging.warning(str(e)+'\n above this row :\n'+next(rf))
        if len(tables)==0: 
            raise RuntimeError('No Table found'+(' with %s'%key if key!='' else ''))
        return tables

    @classmethod
    def findtable(cls,reader,start,stop=None,skip=lambda s: s.strip()[:1]=='#',sep='undefined',NA=None,numeric=True,multi=False,minrow=1):
        if(stop is None): stop= lambda s: not cls.isnum(s,NA=NA,sep=sep,numeric=numeric)
        header,tab,sep = cls.findheader(reader,start,skip,sep=sep,NA=NA,numeric=numeric,multi=multi,minrow=minrow)
        # if sep=='undefined': sep = cls.scanformat(tab[-1],cls.colsep)
        fields = list(header.pop(True))
        units = list(header.pop(False))
        table = [cls.parsenum(r,sep,NA,numeric=numeric) for r in tab[:-1]]
        row = tab[-1]
        while not stop(row):
            table.append(cls.parsenum(row,sep,NA,numeric=numeric))
            try: 
                row = next(reader).strip()
                while skip(row): # comment-interrupted table
                    row = next(reader).strip()
            except StopIteration: logging.warning('Table ended abruptly at the end of file'); break
        if(row=='' or row==row[0]*len(row)): pass # this should always be the type of row that marks the end of a table
        else: logging.warning('Stopped table at non conventional row:\n%s'%row)
        if(multi): fields = pd.MultiIndex.from_tuples(fields)
        pdtab = pd.DataFrame(data=table,columns=fields)
        with warnings.catch_warnings(record=True) as w: # we assign these attributes as a convenient way to pass them onward...
            pdtab.header = header 
            pdtab.units = units
        return pdtab
    
    @classmethod        
    def findheader(cls,reader,head,skip=lambda s: s.lstrip()[:1]=='#',sep=None,NA=None,numeric=True,multi=False,minrow=1):
        # stripping only right end of lines is order to keep initial spacing for columns, this might be important when detecting the name of the columns aligned on multiple rows
        istab = functools.partial(cls.isnum,sep=sep,numeric=numeric) # Allow tabs \t to be treated as separators different from white spaces
        row = next(reader).rstrip() # using .rstrip() is to avoid discarding space which may serve as a separator in tables
        while not row or skip(row): row = next(reader).rstrip() # do not permit empty strings or don't waste time for non interesting rows
        found = head(row)
        comment = [row]
        tab = []
        stopped = found and istab(row,NA=NA) # if numerical value is found, table starts
        while not stopped:
            row = next(reader).rstrip()
            # while not header(row): # Not finding any relevant table 
            while row and skip(row): row = next(reader).rstrip()
            if not row: # Important to reset table
                comment.clear()
                found = False # Table interrupted
                row = next(reader).rstrip()        
                while skip(row) or row=='': row = next(reader).rstrip()    
            comment.append(row)
            if not (found or head(row)): continue
            elif (not found): found = True # Header identified
            if not istab(row,NA=NA): continue # Keep recording header
            else: # Peek ahead
                rownew = next(reader).rstrip()
                if(not rownew): continue # empty string, search interrupted
                else: 
                    while skip(rownew):
                        rownew = next(reader).rstrip()
                if(istab(rownew,NA=NA,prev=row)): # Only way out of the loop
                    # n = len(rownew.split(cls.scanformat(rownew,cls.colsep)))
                    # n = len(row.split(sep))
                    # if(n==len(rownew.split(sep))):
                    tab.append(row)
                    if minrow>1:     
                        valid = len(tab)==minrow-1
                        while len(tab)<minrow-1:
                            tab.append(rownew)
                            rownew = next(reader).rstrip()
                            valid = istab(rownew,NA=NA,prev=tab[-1])  
                            if not valid:
                                break
                        if not valid: 
                            comment.extend(tab)
                            tab.clear()
                            continue # not long enough
                    stopped = True # Definitely found table with two numerical values
                    comment[-1] = rownew # replace last row
                elif(len(comment)>1 and len(rownew)>3 and rownew.lstrip().startswith(comment[-2][:len(rownew)])): # Identified symmetric separator -> also considered as a table
                    try:
                        if(sep=='undefined'): l,r = cls.partrow(row, cls.colsep,split=str.split)
                        else: l,r = cls.partrow(row, sep, split=str.split)
                    except: continue
                    if(len(l)==1): continue # no columns identified
                    stopped = True # This seems like a one-line table !
                else: # Was not numerical
                    comment.append(rownew)
                    continue # False alarm, continue looking for header
        tab.append(comment.pop()) # Releasing first numerical value : i.e. 'row'
        if('#' in row): row = row[:row.find('#')] # comments
        if sep=='undefined': sep = cls.scanformat(row,cls.colsep)
        n = len(row.split(sep)) # number of identified columns
        if(len(comment)==0): return {True:range(n),False:('?',)*n},tab,sep # No header for this table
        com = comment[-1].strip(cls.strip) # remove comments or tab or whatever space
        if(len(com)<=1 or (com[1:-1]==com[1]*(len(com)-2))): comment.pop() # skipping separator
        comment,header = comment[:-3],comment[-3:]
        fields = cls.findfields(header,n)
        comment+=header
        header = {}
        for r in comment:
            srow,msep = cls.partrow(r,cls.metasep,post=r'\s|_')
            if(msep not in cls.metasep): header[msep] = ''
            else:
                k,v = srow[0].strip(),srow[-1].strip()
                if(k+v!=''): # disinterested in empty strings and avoid overwritting continued comment
                    if(k in header): header[k] += '\n'+v
                    else: header[k] = v 
        if(len(fields)==0): 
            if(comment):
                logging.warning('Couldn\'t identify %d columns from : %s'%(n,comment[-1]))
            else: logging.warning('Couldn\'t identify %d columns for row : %s'%(n,tab))
            header[True] = range(n)
            header[False] = ('?',)*n
        else:
            #cls.partrow(fields,cls.headsep,split=str.split)
            if(multi): header[True],header[False] = zip(*[cls.multilabel_unit(*c) for c in fields])
            else: header[True],header[False] = zip(*[cls.label_unit(*c) for c in fields])
        return header,tab,sep

    @classmethod
    def findfields(cls,header,n): # TODO raise problem when n columns cannot be identified clearly
        ''' From a header list of strings, try to distinguish n columns. The columns can be scattered across multiple rows.'''
        coms = []        
        seeking = True
        headsep = cls.headsep
        l = max(len(h) for h in header)
        i=len(header)
        splitter = str.split
        low = 0
        while i>0 and seeking:
            org = header.pop()
            i-=1 # number of rows unprocessed
            com = cls.partrow(org.lstrip('#'),cls.metasep,parts=2,post=r'\s|_')[0][-1]#.strip() do not strip otherwise length matching problems might occur for multiple lines
            if(len(com)<n): # Cannot withhold n column fields
                if(len(com)>0): header.append(org)
                seeking=False # Stop looking for fields
                break
            elif(len(com)!=l): # Add spaces so that 
                com = com+(' '*(l-len(com)))
            upp = len(com)//n
            s,sep = cls.partrow(com,headsep,split=splitter,parts=n)
            m=len(s)
            if(len(coms)==0 or headsep[0] not in cls.headsep): # Give a chance only when conventional separator was not found
                if(m!=n): 
                    s = cls.parsecol(*s) # try to subdivide columns
                    m = len(s)
                while m!=n and low<upp:# and sep in headsep: # either low or upp will shrink their interval
                    if(m<n): upp-=1 # Too few parts, must reduce length of splitter
                    else: low+=1 # Too many parts, must augment length of splitter
                    sep = ' {%d,%d}\t*'%(low,upp)
                    s = re.split(sep,com)
                    m=len(s)
            if(m==n): 
                if len(sep)>1: splitter = lambda l,r: re.split(r,l) # regular expression found for splitter
                coms.append(s)#[_.strip(cls.strip) for _ in s])
                headsep = [sep] # All presupposed column rows should bear identical same separator semantics 
            else:
                seeking=False 
                header.append(org)
        return list(zip(*reversed(coms))) # (Eventual) units ought to appear last in row order

    def parsenum(row,sep,NA,typed=float,numeric=True):
        if('#' in row): row = row[:row.find('#')].strip()
        if(NA is not None and NA!=sep): 
            if sep: NA = NA[:-1]+'|'+sep+')' # allow nan to be directly followed by sep
            row = re.sub(NA,'np.nan',row) # important to use np.nan otherwise will force casting to object!
        res = []
        for r in row.split(sep):
            if('%'in r): # relative uncertainty
                if('(' in r):
                    i,j = r.find('('),r.rfind(')')
                    v = typed(eval(r[:i]))
                    perc = r[i+1:j].replace('%','')
                    if('+' in perc or '-' in perc): # asymmetric uncertainties 
                        p,m = [float(f) for f in perc.split('/')]
                        p = 0.01*max(abs(p),abs(m)) # -> take the highest of both
                    else: p = 0.01*float(perc)
                    res.append(uncertainties.ufloat(v,p*v))
                else:
                    raise ValueError('Unable to process relative uncertainty in %s from %s'%(r,row))
            elif('±' in r or (r[0]!='(' and '(' in r)): res.append(uncertainties.ufloat_fromstr(r))
            elif('j' in r): #complex
                res.append(complex(eval(r)))
            else: 
                try: 
                    res.append(typed(eval(r)))
                except:
                    if not numeric: res.append(r.strip())
                    else: raise ValueError('Could not read %s in line %s'%(r,row))
                # if(numeric and type(res[-1]) is not typed):
                #     raise TypeError('Incorrect type for value %s in line %s'%(r,row))
        return res
        # return [uncertainties.ufloat_fromstr(r) if('±' in r or ('(' in r and r[0]!='(')) else eval(r) for r in row.split(sep)]
        # else: return [eval(r) for r in row.split(sep)]

    def partrow(row,seps,split = str.partition,parts=None,post=''):
        '''Try various row partitions according to the splitting method provided in the priority set by the order of separators and that yield a partition closest to n parts
        Arguments:
            row : str - row to split
            seps : list[str] - separators to try
            split : fn(row,sep) - a splitting function for the row and a separator
            parts : float or None - if provided, find separator whose partition reaches at the closest the target number of parts 
            post : str - 'regex' expression that should follow the separator
        Returns : list[str] - the partition found'''
        counts = {}
        if(post):
            if(split==str.partition):maxsplit = 1
            elif parts is None: maxsplit = 0
            else: maxsplit = parts
            split = lambda r,s : re.split(s+'(?=%s)'%post,r,maxsplit=maxsplit)
        for s in seps:
            if(s is None): 
                res = split(row,s)
                if parts is None or len(res)==parts: return res,s 
            elif(s in row):
                counts[s] = row.count(s)
                if(parts is None or counts[s]==parts-1): return split(row,s),s
        d = dict(sorted(counts.items(), key=lambda item: -item[1])) # lowest last so that eventually subcolumns may be found
        if(len(d)!=0): 
            s = d.popitem()[0]
            return split(row,s),s
        else: return [row],row # undividable row

    def parsecol(*cols,subcol=':'):
        labels = []
        for s in cols:
            if(subcol in s): # Multi-Index
                cs = s.split(subcol)
                ss = cs[0].rsplit(maxsplit=1)
                arch = ss[0].strip()
                if(len(ss)==2): cs[0] = ss[1].strip()
                else: 
                    cs[0] = arch
                    arch = cols.index(s)
                for c in (cs):
                    labels.append((arch,c))
                    # l,u = TableHandler.label_unit(c)
                    # labels.append((arch,l))
                    # units.append(u)
            else:labels.append(s)
            # else:
            #     l,u = TableHandler.label_unit(s)
            #     labels.append(l)
            #     units.append(u)
        return labels

    def label_unit(*cols): # distinguishes the pair of label and units in a list of column names
        if(len(cols)==1 and type(cols[0])is tuple): return TableHandler.multilabel_unit(*cols[0])
        label,unit = [],''
        for s in cols:
            s = s.strip(TableHandler.strip)
            if(s==''): continue
            u1,u2 = s.find('('),s.rfind(')')
            if(u1>=u2): # No parenthesis
                # ss = s.strip().split(maxsplit=1)#
                ss = re.split(r'(?<!\s[+-])\s+(?![+-]\s)',s,1) # avoid splitting expressions with plusses and minusses

                label.append(ss[0].strip())
                # if len(ss)==1: return ss[0],''
                if(len(ss)==2): 
                    try: unit = TableHandler.re_unit.search(ss[1]).group()
                    except AttributeError: 
                        unit = ''
                        label = [s.strip()]
                # else: return ss
            else: 
                label.extend((unit,s[:u1].strip()))
                unit=s[u1+1:u2].strip()
        return ' '.join([l for l in label if l!='']),unit

    def multilabel_unit(*cols):
        label,unit = list(cols[:-1]),''
        s = cols[-1]
        s = s.strip()
        if(s!=''):            
            u1,u2 = s.find('('),s.rfind(')')
            if(u1>=u2): # No parenthesis
                ss = s.split(maxsplit=1)#re.split('[ \t]+',s.strip(),1)
                label.append(ss[0])
                # if len(ss)==1: return ss[0],''
                if(len(ss)==2): unit = ss[1]
                # else: return ss
            else: 
                label.append(s[:u1].strip())
                unit=s[u1+1:u2].strip()
        return tuple(label),unit

    def assign_index(index):
        if(index is True): index = 0
        if(type(index) is int): return lambda t: t.set_index(t.columns[index],inplace=True)
        else: return lambda t: t.set_index(index,inplace=True)

    @classmethod
    def isnum(cls,row,NA=None,sep=None,prev=None,numeric=True):
        if('#' in row): row = row[:row.find('#')].strip()
        if(numeric):
            if(re.search('[a-df-ik-z]',row,flags=re.IGNORECASE)): return False # has letters ! can only contain 'e' (exponent) of 'j' (complex)
            row = row.strip()
            if(NA is None): na = False
            else: na = re.match(NA,row) and (re.search(TableHandler.renum,row) is not None)
            isnum = len(row)!=0 and (row[0].isnumeric() or na or (re.match(r'\(?'+TableHandler.renum+r'\)?',row)) is not None)
        else:
            # if(sep=='undefined'):
            #     try: sep = cls.scanformat(row,cls.colsep)
            #     except RuntimeError: return False
            isnum = len(row)!=0 and '\t' in row
        if(prev is None or not isnum): return isnum
        else: # Has row the same structure as prev ? (i.e. same number of columns, same separator ?)
            # if('#' in row): row = row[:row.find('#')].strip()
            if('#' in prev): prev = prev[:prev.find('#')].strip()
            if(sep == 'undefined'): 
                try: sep = cls.scanformat(row,cls.colsep)
                except RuntimeError: return False
            n = len(row.split(sep))
            nn = len(prev.split(sep))
            if(n==nn): return n
            else: return 0

    def scanformat(row,seps): # searches for the first separator in seps for row
        for s in seps:
            if(s in row): 
                if(s in [' ','\t']): return None
                else: return s
        raise RuntimeError('Data format in "%s", could not be understood'%row)

csheader = 'ELASTIC\n{0:s}\n {1:.5f} \nSPECIES: e / {0:s}\nPROCESS: E + {0:s} -> E + {0:s}, Elastic\nPARAM.: ??\nCOMMENT: {2:s}\nUPDATED: {3:s}\nCOLUMNS: Energy (eV) | Cross section (1e-20 m2)\n'
dcsheader = 'SPECIES: e / {0:s}\nPROCESS: E + {0:s} -> E + {0:s}, Elastic\nPARAM.: E = {1:s} eV\nCOMMENT: {2:s}\nUPDATED: {4:s}\nCOLUMNS: Angle (deg) | {3:s} ({5:s})\n'
excheader = 'EXCITATION\n{0:s}\n {1:.5f} \nSPECIES: e / {0:s}\nPROCESS: E + {0:s} -> E + {0:s}*({1:.3f}eV), Excitation\nPARAM.: {1:.5f} eV\nCOMMENT: {2:s}\nUPDATED: {3:s}\nCOLUMNS: Energy (eV) | Cross section (m2)\n'
headers={'DCS':dcsheader,'CS':csheader,'EXC':excheader}
# def get_header(which,target,energies,comment):
#     header = headers[which]
#     if(energies)
#     header.format(target,)

def get_dcs_header(target,energies,comment,dcsunit='1e-20 m2/sr',date=datetime.now().replace(microsecond=0)):
    if(hasattr(energies,'__len__')):
        Ektup = '(%s)'%(','.join(map(lambda s: format(s,'g'),energies)))
        Ekcol = ' | '.join(map(lambda s: '%g eV'%s,energies))
        return dcsheader.format(target,Ektup,comment,Ekcol,str(date),dcsunit)
    else:
        Ekcol = '%g (eV) | Differential Cross section'
        return dcsheader.format(target,'%g'%energies,comment,Ekcol,str(date),dcsunit)

def findsep(s,exc=''):
    d = {}
    for c in s:
        if(not c.isnumeric() and c not in exc):
            d[c] = d.get(c,0)+1
    if(len(d)==0 ): return None #or max(d.values())==1
    else:
        return sorted(d.items(), key=lambda item: item[1]-item[0].isspace())[-1][0]

def findtype(s,typed=float,forgive=False):
    try: return typed(s)
    except: 
        if forgive: return eval(re.search(regextypes[typed],s).group())
        else: raise RuntimeError('%s could not be identified as %s'%(s,typed))

def finditer(s,typed=float,forgive=False): # Find list of values from type, separated by a separator
    elem = regextypes[typed]
    if(',' in s): 
        match = re.search(r'(\(|\[)?({0:s}\s?,\s?)*{0:s}(\)|\])?'.format(elem),s) 
        # match = re.findall(r'{0:s}'.format(elem),s)
        if(match):    
            m = match.group()
            try: # ensure that a tuple or a list is returned
                if(',' in m): return eval(m)
                else: return (eval(m),)
            except: pass
    else: return list(map(typed,re.findall(elem,s)))
    sep = findsep(s,'.')
    l = s.split(sep)
    # try:
    return list(map(lambda e: findtype(e,typed,forgive),l))
    # except e:
    #     raise RuntimeError('Could not find iterable')

