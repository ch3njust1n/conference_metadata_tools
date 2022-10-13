'''
'''
import re
import sys
import logging
import urllib.request
from collections import defaultdict
from tqdm import tqdm
from pprint import pprint

import scrape.utils as utils
from bs4 import BeautifulSoup, Tag
from scrape.batcher import batch_process

class CVF(object):
	def __init__(self, year, logname):
		self.year = str(year)
		self.base = f'https://openaccess.thecvf.com' 
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
		resp = urllib.request.urlopen('https://openaccess.thecvf.com/menu')
		soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
		tags = soup.find_all('div', {'id': 'content'})[0].find_all('dd')
		
		proceedings = []

		for t in tags:
			title = t.text.strip().split(',')[0]
			if kw.lower() in title.lower(): proceedings.append((title, re.search(r'\d{4}', title).group()))	
		
		return proceedings


	def extract_papers(self, url, title):
		page = urllib.request.urlopen(url)
		soup = BeautifulSoup(page.read(), 'html.parser', from_encoding='utf-8')
		count = 0
		proceedings = []
		paper = defaultdict()

		i = 0
		for tag in soup.find('dl').children:
			if isinstance(tag, Tag):
				atag = tag.find_all('a', href=True)[0]
				if 'back' in atag.text.lower() and '/'+title == atag['href']: 
					continue
				else:
					count = count % 3 + 1
					
					if count == 1:
						paper = defaultdict()
						paper["title"] = tag.text
					elif count == 2:
						authors = []
						
						for auth in tag.find_all('a'):
							auth = auth.text.split()
							authors.append({
								"given_name": ' '.join(auth[:-1]),
								"family_name": auth[-1],
								"institution": ''
							})

						paper["authors"] = authors
					elif count == 3:
						paper["url"] = [utils.join_url([self.base, link['href']]) for link in tag.find_all('a', href=True) if link['href'].endswith('.pdf')]
						proceedings.append(paper)


		return proceedings

	
	def accepted_papers(self, use_checkpoint=True, kw='wacv'):
		completed_years =  utils.load_cached_years(kw)
		proceedings = self.build_proceedings_list(kw=kw)

		for conf, year in tqdm(proceedings):
			if year in completed_years:
				continue
			
			title = conf.replace(' ','')
			conf_url =f"{self.base}/{title}"
			print(f'scraping {conf_url}')

			day_urls = utils.get_tags(conf_url, 'a', 'href', 'day=')

			if len(day_urls) > 0:
				if any(tag.endswith('day=all') for tag in day_urls):
					papers = self.extract_papers(conf_url+'?day=all', title)
					utils.save_json(f'./{kw}', f'{kw}_{year}', papers)
				else:
					papers = []

					for url in day_urls:
						if url.endswith('day=all'): continue
						url = url.split('?')[1]
						papers.extend(self.extract_papers(conf_url+'?'+url, title))

					utils.save_json(f'./{kw}', f'{kw}_{year}', papers)
			else:
				papers = self.extract_papers(conf_url, title)
				utils.save_json(f'./{kw}', f'{kw}_{year}', papers)