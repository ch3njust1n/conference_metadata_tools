'''
Updates metadata

9/29/2022
'''

import json
import logging
import urllib
from urllib.error import URLError
from http.client import InvalidURL

import scrape.utils as utils
from scrape.paperswithcode import PapersWithCode


class Metadata(object):
	def __init__(self, conference, year, logname):
		self.logname = logname
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
 	'''
	def update_abstract(self):
		metadata = self.get_metadata()
		
		for i, data in enumerate(metadata):
			title = data['title']
			
			try:
				src = PapersWithCode(title, self.logname)
				metadata[i]['abstract'] = src.abstract
			except (URLError, InvalidURL) as e:
				self.log.debug(f'{self.conference}-{self.year}-{title}')

		if metadata:
			utils.save_json('./temp/output', f'{self.conference}_{self.year}', metadata)


		
class Updater(object):
	def __init__(self, conference, year, logname):
		self.conference = conference
		self.year = year
		self.logname = logname
		self.metadata = Metadata(conference, year, logname)
		
	
	'''
	inputs:
	property (str) Metadata property to update
 	'''
	def update(self, property):
		if property == 'abstract':
			self.metadata.update_abstract()