'''
Updates metadata

9/29/2022
'''

import os
import json
import logging
import urllib
from urllib.error import URLError
from http.client import InvalidURL

import redis
import scrape.utils as utils
from scrape.paperswithcode import PapersWithCode
from parse import pdfparser


class Metadata(object):
	def __init__(self, conference, year, logname, cache_dir=''):
		self.logname = logname
		self.log = logging.getLogger(logname)
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
			title = data['title'].lower().replace(' ', '-')
			author = data['authors'][0]['family_name'].lower()
			filename = f'{self.year}-{author}-{title}'
			urls = data['url'] if isinstance(data['url'], list) else [data['url']]

			try:
				pwc = PapersWithCode(title, self.logname)
				abstract = pwc.extract_abstract()
				
				if not abstract and use_cache:
					temp = '/Volumes/SG-2TB/library/temp'
					if not os.path.exists(temp):
						os.makedirs(temp)
					save_path = os.path.join(temp, filename)
     
					for i, link in enumerate(urls):
						try:
							with urllib.request.urlopen(link) as resp, open(temp, 'wb') as out:
								save_name = f'{save_path}_{i}.pdf' if i > 0 else f'{save_path}.pdf'
								file, _ = urllib.request.urlretrieve(link, save_name)
						except InvalidURL as e:
							self.log.debug(f'{e} - {filename}')
					abstract = pdfparser.extract_abstract(save_path, self.conference, self.logname)
     
					self.log.info(abstract)
	 
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
		self.cache_dir = cache_dir
		self.metadata = Metadata(conference, year, logname, cache_dir)
  
		if cache_dir:
			self.index = redis.Redis(host='localhost', port=6379)
			self.build_index()
  
  
	def build_index(self):
		for f in os.listdir(self.cache_dir):
			self.index.set(hash(f), os.path.join(self.cache_dir, f))
		
	
	'''
	inputs:
	property  (str)  Metadata property to update
	use_cache (bool) If True, default to saved papers to extract data
 	'''
	def update(self, property, use_cache=False):
		if property == 'abstract':
			self.metadata.update_abstract(use_cache)