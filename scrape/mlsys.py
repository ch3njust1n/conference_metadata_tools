'''
'''
import os
import re
import sys
import json
import logging
import urllib.request
from collections import defaultdict
from urllib.error import URLError
from http.client import InvalidURL

from tqdm import tqdm
from lxml import etree
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains

import scrape.utils as utils
from scrape.batcher import batch_process

class MLSYS(object):
	def __init__(self, year, logname):
		self.year = str(year)
		self.base = f'https://proceedings.mlsys.org/paper/{self.year}'
		self.failed = defaultdict(list)
		self.log = logging.getLogger(logname)
		c = os.path.join(os.getcwd(), 'scrape/chromedriver')
		self.driver = webdriver.Chrome(executable_path=c)
		self.website = self.driver.get(self.base)
		self.delay = 240
  
  
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

		for a in authors.split('·'):
			a = a.split()
			res.append({
				'given_name': self.capitalize_hyphenated(' '.join(a[:-1]).capitalize()),
				'family_name': self.capitalize_hyphenated(a[-1]).title() if len(a) > 1 else '',
				'institution': None
			})

		return res


	'''
	inputs:
	url       (str) URL to metadata
 
	outputs:
	metadata (dict) Paper metadata
 	'''
	def get_metadata(self, url):
		try:
			with urllib.request.urlopen(url) as file:
				return json.loads(file.read().decode())
		except urllib.error.HTTPError:
			return []

	'''
	inputs:
	use_checkpoint (bool) If True, use file in temp if it exists. Else start from scratch.
 
	outputs:
	papers (dict) Paper metadata
 	'''
	def accepted_papers(self, use_checkpoint=True):
		if use_checkpoint:
			files = os.listdir('./temp')
			saved_temp_filename = ''
			temp_file_prefix = f'mlsys{self.year}'
			
			for f in files:
				if temp_file_prefix in f:
					saved_temp_filename = f
					break
			
			with open(os.path.join('./temp', saved_temp_filename)) as saved_temp:
				papers = json.load(saved_temp)
		else:
			wait = WebDriverWait(self.driver, self.delay)
			papers = []
	
			i  = 1
			while 1:
				try:
					link_xpath = f'/html/body/div[2]/div/ul/li[{i}]/a'
					wait.until(EC.element_to_be_clickable((By.XPATH, link_xpath)))
	  
					el = self.driver.find_element(By.XPATH, link_xpath)
					href = el.get_attribute('href')
					file_hash = href.split('/')[-1].split('-')[0]

					el.click()
					wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/p[1]/a')))
	
					authors_xpath = f'/html/body/div[2]/div/p[2]/i'
					authors = self.driver.find_element(By.XPATH, authors_xpath).text
     
					abstract_xpath = f'/html/body/div[2]/div/p[4]'
					abstract = self.driver.find_element(By.XPATH, abstract_xpath).text
		
					if file_hash:
						papers.append({
							"title": el.title,
							"abstract": abstract,
							"authors": authors,
							"url": f'{self.base}/file/{file_hash}-Paper.pdf'
						})
      
					self.driver.execute_script("window.history.go(-1)")
		
					i += 1
				except Exception as e:
					break
  
			utils.save_json('./temp', f'mlsys_{self.year}', papers)
  
		return papers