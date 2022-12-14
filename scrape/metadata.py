from scrape.neurips import NeurIPS
from scrape.icml import ICML
from scrape.pmlr import PMLR
from scrape.iclr import ICLR
from scrape.acl import *
from scrape.cvf import CVF
from scrape.mlsys import MLSYS
from scrape.ijcai import IJCAI

def conference(name, year, logname):
	name = name.lower()

	if name in ['neurips', 'nips']: return NeurIPS(year, logname)
	if name in ['icml']: return ICML(year, logname)
	if name in ['iclr']: return ICLR(year, logname)
	if name in ['pmlr']: return PMLR(year, logname)
	if name in ['cvf']: return CVF(year, logname)
	if name in ['mlsys', 'mlsystem', 'mlsystems']: return MLSYS(year, logname)
	if name in ['ijcai']: return IJCAI(year, logname)
	# convert string to class object as in datapipe
	
	return None