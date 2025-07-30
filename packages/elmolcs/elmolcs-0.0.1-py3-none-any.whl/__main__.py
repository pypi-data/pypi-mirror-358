# elmolcs Copyright (C) 2023 Anthony Jeseněk
import os
root = os.path.dirname(__file__)
from elmolcs import reader

''' The reader has useful routines to parse and identify electron-molecule reactions.
Its architecture is flexible but not robust

It uses molecular and atomic data contained in constants.Constants to complete the information missing in the header of each reaction 

If you use a target which has missing data in constants.Constants, the reader will most likely crash and explain why

It is up to the user to provide the adequate data missing to the constants module to load reactions

For a robust reader, please use the bolos.parser from bolos on https://pypi.org/project/bolos/

'''


if __name__=='__main__':

	# -----------  Cross sections -------------

	''' targets may be : ['N2', 'O2', 'NO', 'Ar', 'O', 'N']
	 	databases may be : 
	 		'iaa' : the complete IAA database in numerical format
	 		'iaa*' : the complete IAA database in analytical format (where possible)
	 		others : 
	 			- name of a LXCat database:
	 				>>> 'phelps', 'ist', 'biagi', 'itikawa', 'hayashi', 'bsr' (depending on the availability of the database for each of the targets)
	 			- name of a type of collision for raw data:
	 				>>> 'elastic', 'total' (includes ionisation as well) or 'excitation'
	'''

	# dictionary per process kind (elastic, vibrational, ionisation, ...) in capital letters
	O2_kind2process = reader.loadCS('O2','iaa')
	for k, ps in O2_kind2process.items():
		print(k)
		for p in ps: print('\t'+p['final'])

	# list of all processes
	N2cs = reader.readCS(target='N2',db='iaa*')
	for c in N2cs: 
		print(c['kind'],c['subkind'],c['final'],'ΔE = %s eV'%c['threshold'])
	Arcs = reader.readCS('Ar','hayashi')
	for c in Arcs:
		print(c['final'],len(c['data']))



	# explicit path to file
	rawcs = reader.parsecs(os.path.join(reader.root,'cs','Cross section.txt'),minrow=3) 
	# if you do not to use minrow = 3 (the minimum number of rows in a table), 
	# the table reader routine might detect spurious numerical tables in the header of each rotational process

	csfile = reader.parsecs(os.path.join(reader.root,'cs','N2','others','Cross section (phelps).e-N2'))  
	# of course this will not always be problematic, but will depend on the header format of each process

	# Data containing object :
	csdata = reader.CS_Data('N2',['biagi','total'])
	csdata.add_database('O2','excitation')
	csdata.add_database('Ar','elastic')

	cs,err = csdata.select(['N2','Ar'],db=['Kitajima','Szmytkowski','Panajotović']) # pandas DataFrames : cross sections, absolute errors/uncertainties
	procs = csdata.select('O2',kind='EXCITATION',final=['LB','SR','a1Δg'],table=False) # list of processes

	# get your unicode ready : Σ Π Δ (for diatomic molecular symmetries - projection of the electron momentum on the internuclear axis)

	# ---------------------- Differential Cross sections --------------------

	# tuple : elastic , {state: inelastic}   of DCS objects
	# IAA database (only elastic)
	NO_ela,_ = reader.loadDCS('NO','iaa') 

	# Experimental database
	Ar_ela,Ar_inel = reader.loadDCS('Ar','') 
	O2_ela,O2_inel = reader.loadDCS('O2','raw')

	for k,p in O2_inel.items():
		print(k, p.data.columns) # pandas DataFrames

	print(O2_ela.ordata[10]) # All DCS measurements at 10 eV
	for s in Ar_ela.ordata[100]: print(s['source'],s['norm2pi']*1e20)

	# list of separate DCS (as they appear in the file)
	N2_dcs = reader.readDCS('N2','')

	# explicit path to file
	Ar_bsr = reader.parsediff(os.path.join(reader.root,'dcs','Ar','DCS(theory).e-Ar'))

	# ------------------- Miscellaneous --------------------
	# pandas DataFrame objects

	# Optical oscillator strengths:
	oos_Ar = reader.readOOS('Ar')

	# Franck-condon Factors
	fcf_NO = reader.readFC('NO')

	# predissociation rates
	pd_N2 = reader.readPD('N2')












