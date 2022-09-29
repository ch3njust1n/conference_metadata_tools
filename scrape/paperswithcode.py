'''
Justin Chen

9/29/2022
'''

import re
import logging
import urllib.request
from urllib.error import URLError
from http.client import InvalidURL

from bs4 import BeautifulSoup


class PapersWithCode(object):
	def __init__(self, title, logname):
		self.base = f"https://paperswithcode.com/paper/{self.format_title(title)}"
		self.log = logging.getLogger(logname)
		self.title = title
		self.abstract = self.extract_abstract__()
	
  
	'''
	inputs:
	title (str) Title fo papers
 
	outputs:
	formatted (str) Title in lowercase, without special characters and replaced spaces with dash
 	'''
	def format_title(self, title):
		return re.sub('[^A-Za-z0-9]+', ' ', title).lower().replace(' ', '-')
  
  
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


	'''
	Extract abstract
 
	outputs:
	abstract (str) Paper abstract
 	'''
	def extract_abstract__(self):
		try:
			resp = urllib.request.urlopen(self.base)
			soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
			abstract_section = soup.find('div', {'class': 'paper-abstract'})
			paragraphs = abstract_section.find_all('p')
   
			return max([p.text for p in paragraphs], key=len)

		except (URLError, InvalidURL) as e:
			self.log.debug(self.title)
   
		return ''
		