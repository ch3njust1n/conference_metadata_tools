'''
'''
import os
import re
import sys
import json
import logging
import urllib.request
from collections import defaultdict
from tqdm import tqdm
from pprint import pprint

import scrape.utils as utils
from bs4 import BeautifulSoup
from scrape.batcher import batch_process

class PMLR(object):
	def __init__(self, year, logname):
		self.year = str(year)
		self.base = f'https://proceedings.mlr.press/' 
		self.failed = defaultdict(list)
		self.log = logging.getLogger(logname)


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


	def build_proceedings_list(self, kw):
		resp = urllib.request.urlopen(self.base)
		soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
		tags = soup.find_all('ul', {'class': 'proceedings-list'})

		proceedings = []

		for t in tags:
			proceedings.extend([title.strip().replace('\n', ' ') for title in t.text.split('Volume') if len(title) > 0])
		
		return [('Volume '+p, re.search(r'\d{4}', p).group()) for p in proceedings if len(p) > 0 and kw.lower() in p.lower()]
		
	
	def accepted_papers(self, use_checkpoint=True, kw='colt'):
		proceedings = self.build_proceedings_list(kw=kw)
		print(proceedings)
		confs = defaultdict()

		for conf, year in tqdm(proceedings):
			volume = conf.split()[1]
			if volume.startswith('R'): continue
			resp = urllib.request.urlopen(f'https://proceedings.mlr.press/v{volume}')
			soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
			tags = soup.find_all('div', {'class': 'paper'})
			
			papers = []

			for item in tqdm(tags):
				authors = item.find('p', {'class': 'details'}).find('span', {'class': 'authors'}).text.replace('\xa0', '')
				urls = [a['href'] for a in item.find('p', {'class': 'links'}).find_all('a', href=True) if a['href'].endswith('.pdf')][0]
	
				papers.append({
					'title': item.find('p', {'class': 'title'}).text,
					'authors': self.format_auths(authors),
					'url': urls
				})

			utils.save_json(f'./{kw}', f'{kw}_{year}', papers)
			# confs[f'icml{year}']

		# return confs