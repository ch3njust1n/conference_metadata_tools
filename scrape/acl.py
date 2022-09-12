'''
12.26.2020
TODO:
1. Add the rest of the ACL and Non-ACL venues
2. Create ACL_Anthology API. Refer to neurips.py for API.

'''
import json
import datetime
import urllib.request
from urllib.error import URLError, HTTPError
from multiprocessing import Process, Manager, cpu_count
from threading import Thread

from tqdm import tqdm
from colorama import Fore, Style


class ACL_Anthology(object):
	def __init__(self, year, logname):
		self.year = year
		self.base = 'https://www.aclweb.org/anthology'


	def format_pdf_url(self):
		pass


	def build_proceedings(self):
		pass


	def get_source_metadata(self):
		pass


	def accepted_papers(self, use_checkpoint=True):
		pass


class AACL(ACL_Anthology):
	def __init__(self, year):
		super().__init__(year)


class ACL(ACL_Anthology):
	def __init__(self, year):
		super().__init__(year)


class ANLP(ACL_Anthology):
	def __init__(self, year):
		super().__init__(year)


class CL(ACL_Anthology):
	def __init__(self, year):
		super().__init__(year)


class CoNLL(ACL_Anthology):
	def __init__(self, year):
		super().__init__(year)


class EACL(ACL_Anthology):
	def __init__(self, year):
		super().__init__(year)
