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
from itertools import groupby

import scrape.utils as utils
from bs4 import BeautifulSoup
from urllib.error import HTTPError

from scrape.batcher import batch_thread
from scrape.utils import get_four_digit_year, get_two_digit_year, has_two_digits

class IJCAI(object):
	def __init__(self, year, logname):
		self.year = str(year)
		self.base = f'https://www.ijcai.org/proceedings' #/year-vol e.g. /1991-1
		self.index = f'https://dblp.org/db/conf/ijcai/index.html'
		self.failed = defaultdict(list)
		self.log = logging.getLogger(logname)
		self.start_year = 1969
  

	'''
	Group urls by year
 
	input:
	
	outputs:
	
 	'''
	def group_urls(self, data):
		def find_year(url):
			pattern = re.compile(r"\d{4}")
			years = pattern.findall(url)
			return url if not years else years[0]

		groups = []
		uniquekeys = []
		data = sorted(data, key=find_year)
		for k, g in groupby(data, find_year):
			groups.append(set(g))      # Store group iterator as a list
			uniquekeys.append(k)
   
		return groups
	
  
	'''
	Get all the proceeding links from the index page
 
	outputs:
	hrefs (list) List of hrefs to proceedings
 	'''
	def get_index(self):
		resp = urllib.request.urlopen(self.index)
		soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
		return [atag['href'] for atag in soup.find_all('a', href=True) if atag['href'].startswith('https://dblp.org/db/conf/ijcai/')]


	'''
	inputs:
	name (str) Name of title or author
 
	output:
	title (str) Capitalized and hyphenated title
 	'''
	def capitalize_hyphenated(self, name):
		return ('-'.join([i.capitalize() for i in name.split('-')])).title()


	'''
	inputs:
	year    (int)  Year of paper
	authors (list) List of dicts of authors
	title   (str)  Title of paper
 
	outputs:
	title (str) Formatted pdf filename
 	'''
	def format_title(self, year, authors, title):
		first_auth_lastname = authors[0]['family_name']
		return f'{year}-{first_auth_lastname}-{title.strip().lower()}.pdf'


	'''
	inputs:
	paper (bs4.Tag)
 
	outputs:
	
 	'''
	def format_metadata(self, paper, year):
		try:
			print(type(paper))
			citeTag = paper.find('cite', {'class': 'data tts-content'})
			title = citeTag.find('span', {'class': 'title'}).text
			authors = [span.text for span in citeTag.find_all('span', {'itemprop': 'author'})]
			authors =  utils.format_auths(authors)
			formatted_title = self.format_title(year, authors, title)
   
			return {
				'url': f'https://github.com/Lab784/library/blob/main/ijcai/{year}/{formatted_title}',
				'title': title,
				'authors': authors
			}
		except Exception as e:
			self.log.debug(e)


	def get_metadata(self, url, year):
		resp = urllib.request.urlopen(url)
		soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
		tags = soup.find_all('ul', {'class': 'publ-list'})
		papers = [tag for papers in tags for tag in papers.find_all('li', {'class': 'entry inproceedings'})]
		return batch_thread(papers, self.format_metadata, args=(year,))

	
	def accepted_papers(self, use_checkpoint=True, kw=''):
		urls = self.get_index()
		urls = self.group_urls(urls)
  
		proceeding_urls = defaultdict(list)

		for url_set in urls:
			for url in url_set:
				if has_two_digits(url):
					year = get_two_digit_year(url)
					proceeding_urls[year].append(url)
				else:
					year = get_four_digit_year(url)
					proceeding_urls[year].append(url)
			
		metadata = []
  
		for year, urls in proceeding_urls.items():
			for url in urls:
				metadata.extend(self.get_metadata(url, year))
				break
			break

		pprint(metadata)
		# utils.save_json('./temp/output', f'ijcai{self.year}-{utils.unix_epoch()}', metadata)