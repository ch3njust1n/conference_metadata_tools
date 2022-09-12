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

import scrape.utils as utils
from bs4 import BeautifulSoup
from scrape.batcher import batch_process

class ICML(object):
	def __init__(self, year, logname):
		self.year = str(year)
		self.base = f'https://icml.cc/Conferences/' 
		self.failed = defaultdict(list)
		self.log = logging.getLogger(logname)
  
  
	'''
 	'''
	def capitalize_hyphenated(self, name):
		return ('-'.join([i.capitalize() for i in name.split('-')])).title()


	'''
	'''
	def get_institutions(self, eventID):
		event_url = 'https://icml.cc/Conferences/2021/Schedule?showEvent='+str(eventID)
		resp = urllib.request.urlopen(event_url)
		soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
		tags = soup.find_all('button', {'class': 'btn'})
		

		'''
  		'''
		def get_number(string):
			return re.compile(r"\d+-\d+").findall(string)[0]

  
		'''
  		'''
		def remove_special_characters(string):
			return ' '.join(s for s in string.strip().split() if len(re.sub('[^A-Za-z0-9]+', '', s)) > 0)


		'''
		inputs:
		_id (int) Speaker ID
  
		outputs:
		data   (string) URL if failed and institution name if succeeded
  		'''
		def get_institution(author, _id):
			speaker_url = 'https://icml.cc/Conferences/2021/Schedule?showSpeaker='+_id
   
			try:
				resp = urllib.request.urlopen(speaker_url)
				soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
				return soup.find_all('h4')[0].text
			except Exception:
				if len(self.failed[eventID]) == 0:
					self.failed[eventID].append((author, _id))
     
				return speaker_url


		institutions = defaultdict()
  
		for t in tags:
			tag =  t.get('onclick')
			if tag and 'showSpeaker' in tag:
				author = self.capitalize_hyphenated(remove_special_characters(t.text))
				speaker_number = get_number(tag)
				institutions[author] = get_institution(author, speaker_number)

		return institutions


	'''
	'''
	def combine_institutions(self, authors, labs, _id):
		for i, auth in enumerate(authors):
			auth_name = ' '.join([auth['given_name'], auth['family_name']])
   
			try:
				authors[i]['institution'] = labs[auth_name]
			except:
				message = f'''
        			id: {_id}\tauthor: {auth_name}\n'
					{authors[i]}\n
					{labs}\n
				'''
				self.log.debug(message)
    
		return authors


	'''
	Format authors list

	inputs:
	authors (str) Author names separated by commas

	outputs:
	authors (list) List of dicts of author information
	'''
	def format_auths(self, authors):
		res = []

		for a in authors.split('·'):
			a = a.split()
			res.append({
				'given_name': self.capitalize_hyphenated(' '.join(a[:-1]).capitalize()),
				'family_name': self.capitalize_hyphenated(a[-1]).title() if len(a) > 1 else '',
				'institution': None
			})

		return res


	def restart(self):
		os.path.exists()


	'''
	inputs:
	use_checkpoint (bool) If True, use file in temp if it exists. Else start from scratch.
 
	outputs:
	papers (dict) Paper metadata
 	'''
	def accepted_papers(self, use_checkpoint=True):
		papers = {}
  
		if use_checkpoint:
			files = os.listdir('./temp')
			saved_temp_filename = ''
			temp_file_prefix = f'icml{self.year}'
			
			for f in files:
				if temp_file_prefix in f:
					saved_temp_filename = f
					break
			
			with open(os.path.join('temp', saved_temp_filename)) as saved_temp:
				papers = json.load(saved_temp)

		else:
			classname = 'maincard narrower poster'
			posters_url = ''.join([self.base, f'{self.year}/Schedule?type=Poster'])
			resp = urllib.request.urlopen(posters_url)
			soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
			tags = soup.find_all('div', {'class': classname})

			papers = []

			for t in tqdm(tags): 
				tag_id = t.get('id').split('_')[-1]
				title = t.find('div', {'class', 'maincardBody'}).text
				authors = t.find('div', {'class', 'maincardFooter'}).text
				papers.append({'id': tag_id, 'title': title, 'authors': self.format_auths(authors)})
	
			utils.save_json('./temp', f'icml{self.year}-{utils.unix_epoch()}', papers)
  
		def function(paper):
			labs = self.get_institutions(paper['id'])
			paper['authors'] = self.combine_institutions(paper['authors'], labs, paper['id'])
   
		batch_process(papers, function)
   
   
		utils.save_json('./temp/failed', f'icml{self.year}-{utils.unix_epoch()}', self.failed)
		
		return papers