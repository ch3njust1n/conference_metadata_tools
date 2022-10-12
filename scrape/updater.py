'''
Updates metadata

9/29/2022
'''

import os
import sys
import json
import logging
import urllib
import inspect
from urllib.error import URLError
from http.client import InvalidURL

# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir) 

import scrape.utils as utils
from scrape.paperswithcode import PapersWithCode
from scrape.parse.pdfparser import extract_abstract


class Metadata(object):
	def __init__(self, conference, year, logname, cache_dir=''):
		self.logname = logname
		self.cache_dir = cache_dir
		self.conference = conference		
		self.year = str(year)
		self.conf = {
			frozenset({'nips', 'neurips'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/neurips',
			frozenset({'icml'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/icml',
			frozenset({'aistats'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/aistats',
			frozenset({'acml'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/acml',
			frozenset({'corl'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/corl',
			frozenset({'uai'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/uai',
			frozenset({'cvpr'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/cvpr',
			frozenset({'iccv'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/iccv',
			frozenset({'wacv'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/wacv',
			frozenset({'iclr'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/iclr',
			frozenset({'mlsys', 'mlsystems', 'mlsystem'}): 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/mlsys'
		}
		
		self.repo = None
  
		for c in self.conf.keys():
			if self.conference in c:
				self.repo = self.conf[c]
				break

		if not self.repo:
			raise ValueError(f'Conference {conference} not supported.')


	'''
	Get meta data of accepted papers from pseudo-api

	outputs:
	data (list) List of dicts of paper meta data
	'''
	def get_metadata(self):

		url = '/'.join([self.repo, f'{self.conference}_{self.year}.json'])
  
		try:
			with urllib.request.urlopen(url) as file:
				return json.loads(file.read().decode())
		except urllib.error.HTTPError:
			return []


	'''
	Update metadata and save
 
	inputs:
	use_cache (bool) If True, will use extract from cached pdf
 	'''
	def update_abstract(self, use_cache=False):
		metadata = self.get_metadata()
		
		for i, data in enumerate(metadata):
			title = data['title']
			
			try:
				pwc = PapersWithCode(title, self.logname)
				abstract = pwc.extract_abstract()
				
				if not abstract and use_cache:
					pdf_path = f"{os.path.join(self.cache_dir, data['title'].lower().replace(' ', '-'))}.pdf"
					abstract = pdfparser.extract_abstract(pdf_path, self.logname)
	 
				metadata[i]['abstract'] = abstract
					
			except (URLError, InvalidURL) as e:
				self.log.debug(f'{self.conference}-{self.year}-{title}')

		if metadata:
			utils.save_json('./temp/output', f'{self.conference}_{self.year}', metadata)


		
class Updater(object):
	def __init__(self, conference, year, logname, cache_dir=''):
		self.conference = conference
		self.year = year
		self.logname = logname
		self.metadata = Metadata(conference, year, logname, cache_dir)
		self.index = {}
  
		if cache_dir:
			self.build_index()
  
  
	def build_index(self):
		self.index = { hash(f) for f in os.listdir(self.cache_dir) }
		
	
	'''
	inputs:
	property (str) Metadata property to update
 	'''
	def update(self, property):
		if property == 'abstract':
			self.metadata.update_abstract()