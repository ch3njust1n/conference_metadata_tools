'''
'''
import logging
import urllib.request
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import defaultdict
from scrape import utils
from scrape.batcher import batch_thread

class ICLR(object):
	def __init__(self, year, logname):
		self.year = str(year)
		self.base = f'https://dblp.org/db/conf/iclr/iclr{year}.html'
		self.workshop_base = f'https://dblp.org/db/conf/iclr/iclr{year}w.html'
		self.failed = defaultdict(list)
		self.log = logging.getLogger(logname)

		self.workshops = {
			'2019': [
				'https://dblp.org/db/conf/iclr/drlsp2019.html',
				'https://dblp.org/db/conf/iclr/dgs2019.html',
				'https://dblp.org/db/conf/iclr/rml2019.html'
			],
			'2018': [
				'https://dblp.org/db/conf/iclr/iclr2018w.html'
			],
			'2017': [
				'https://dblp.org/db/conf/iclr/iclr2017w.html'
			],
			'2015': [
				'https://dblp.org/db/conf/iclr/iclr2015w.html'
			],
			'2014': [
				'https://dblp.org/db/conf/iclr/iclr2014w.html'
			],
			'2013': [
				'https://dblp.org/db/conf/iclr/iclr2013w.html'
			]
		}


	def get_bibtex(self, url):
		resp = urllib.request.urlopen(f'https://dblp.org/rec/conf/iclr/{url}.html?view=bibtex')
		soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
		bibtex = soup.find('div', {'id': 'bibtex-section'}).text
		url = [t for t in bibtex.split(',') if 'url' in t][0]
		id = url.split('=')[-1].strip()[:-1].replace('\\', '')
		return f'https://openreview.net/pdf?id={id}'


	def format_metadata(self, paper):
		try:
			title = paper.find('cite', {'class': 'data tts-content'}).find('span', {'class': 'title'}).text
			authors = [span.text for span in paper.find('cite', {'class': 'data tts-content'}).find_all('span', {'itemprop': 'author'})]
			return {
				'url': self.get_bibtex(paper['id'].split('/')[-1]),
				'title': title,
				'authors': utils.format_auths(authors)
			}
		except Exception as e:
			self.log.debug(e)


	def get_metadata(self, url):
		resp = urllib.request.urlopen(url)
		soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
		tags = soup.find_all('ul', {'class': 'publ-list'})
		
		papers = [tag for papers in tags for tag in papers.find_all('li', {'class': 'entry inproceedings'})]
		
		return batch_thread(papers, self.format_metadata)


	def accepted_papers(self, use_checkpoint=True):
		urls = [self.base]
		
		if self.year in self.workshops:
			urls.extend(self.workshops[self.year])
		
		metadata = []

		for url in urls:
			metadata.extend(self.get_metadata(url))

		utils.save_json('./temp/output', f'iclr{self.year}-{utils.unix_epoch()}', metadata)
