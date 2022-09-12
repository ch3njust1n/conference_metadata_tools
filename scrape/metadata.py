from api.neurips import NeurIPS
from api.icml import ICML
from api.pmlr import PMLR
from api.iclr import ICLR
from api.acl import *
from api.cvf import CVF

def conference(name, year, logname):
	name = name.lower()

	if name in ['neurips', 'nips']: return NeurIPS(year, logname)
	if name in ['icml']: return ICML(year, logname)
	if name in ['iclr']: return ICLR(year, logname)
	if name in ['pmlr']: return PMLR(year, logname)
	if name in ['cvf']: return CVF(year, logname)
	# convert string to class object as in datapipe
	
	return None