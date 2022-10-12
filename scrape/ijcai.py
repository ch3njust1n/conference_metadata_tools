'''
'''
import os
import re
import sys
import json
import logging
import urllib.request
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm
from pprint import pprint

import scrape.utils as utils
from bs4 import BeautifulSoup
from scrape.batcher import batch_process
from urllib.error import HTTPError

class IJCAI(object):
	def __init__(self, year, logname):
		self.year = str(year)
		self.base = f'https://www.ijcai.org/proceedings' #/year-vol e.g. /1991-1 
		self.failed = defaultdict(list)
		self.log = logging.getLogger(logname)
		self.start_year = 1969


	'''
 	'''
	def capitalize_hyphenated(self, name):
		return ('-'.join([i.capitalize() for i in name.split('-')])).title()


	'''
	Format authors list

	inputs:
	authors (str) Author names separated by commas

	outputs:
	authors (list) List of dicts of author information
	'''
	def format_auths(self, authors):
		res = []

		for a in authors.split(','):
			a = a.strip().split()
			res.append({
				'given_name': self.capitalize_hyphenated(' '.join(a[:-1]).capitalize()),
				'family_name': self.capitalize_hyphenated(a[-1]).title() if len(a) > 1 else '',
				'institution': None
			})

		return res
		
	
	def accepted_papers(self, use_checkpoint=True, kw=''):
		for year in tqdm(range(self.start_year, datetime.today().year)):
			try:
				resp = urllib.request.urlopen(f'{self.base}/{year}')
				soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
				s = soup.find_all('ul')
				print(s)
			except HTTPError as e:
				self.log.debug(f'{self.base}/{year} does not exist')
			print(f'{self.base}/{year}')
			break