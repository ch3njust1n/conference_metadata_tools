'''
'''
import json
import datetime
import urllib.request
from urllib.error import URLError, HTTPError
from multiprocessing import Process, Manager, cpu_count
from threading import Thread

from tqdm import tqdm
from bs4 import BeautifulSoup
from colorama import Fore, Style

class NeurIPS(object):
	def __init__(self, year, logname):
		self.year = str(year)
		self.base = f'https://papers.nips.cc'


	'''
	Format the pdf url

	inputs:
	hash_id (str) Paper hash

	outputs:
	url (str) Formatted URL for given paper
	'''
	def format_pdf_url(self, hash_id):

		return '/'.join([self.base, 'paper', self.year, 'file', hash_id])+'-Paper.pdf'


	'''
	outputs:
	url (str) Formatted url for conference proceedings page
	'''
	def get_proceedings_url(self):

		return f'{self.base}/paper/{self.year}'


	'''
	Build a collection of the proceedings meta data

	inputs:
	proceedings (multiprocessing.Manager.list) List for collecting meta data
	errors      (multiprocessing.Manager.list) List for collecting errors
	title 		(str)						   Paper title
	authors		(list) 						   List of authors
	url 		(str) 						   URL to paper's meta data
	'''
	def build_proceedings(self, proceedings, errors, title, authors, url):

		hash_id = url.split('/')[-1].split('-')[0]
		paper_url = self.format_pdf_url(hash_id)
		metadata_url = ''

		try:
			resp = urllib.request.urlopen(url)
			soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='iso-8859-1')

			metadata_url = f'https://papers.nips.cc/paper/{self.year}/file/{hash_id}-Metadata.json'
			
			with urllib.request.urlopen(metadata_url) as file:
				data = json.loads(file.read())
				proceedings.append({'title': data['title'], 'authors': data['authors'], 'award': data['award'], 
					'hash': hash_id, 'url': paper_url})

		except Exception as e:
			record = {'title': title, 'authors': authors, 'award': [], 'hash': hash_id, 'url': paper_url}
			errors.append(record)
			proceedings.append(record)
			

	'''
	Replace each paper with their NeurIPS meta data.

	inputs:
	papers (list) List of dicts of papers

	outputs:
	papers (list) List of dicts of papers updated with meta data
	'''
	def get_source_metadata(self, papers):

		print('collecting meta data...')

		def batch(iterable, size=1):
			l = len(iterable)
			for i in range(0, l, size):
				yield iterable[i:min(i + size, l)]

		manager = Manager()
		proceedings, errors = manager.list(), manager.list()

		pbar = tqdm(total=len(papers))

		for block in batch(papers, 100):
			procs = [Thread(target=self.build_proceedings, args=(proceedings, errors, p['title'], p['authors'], p['href'],)) for p in block]
				
			for p in procs: p.start()
			for p in procs: p.join()

			pbar.update(len(block))

		pbar.close()

		num_errs = len(errors)

		if num_errs > 0: 
			print(f'\n{Fore.RED}{num_errs}errors{Style.RESET_ALL}:')
			# for i in range(len(errors)): print(f"{i+1} {errors[i]['title']}\n{errors[i]['url']}\n")

		return list(proceedings)


	'''
	Format authors list

	inputs:
	authors (str) Author names separated by commas

	outputs:
	authors (list) List of dicts of author information
	'''
	def format_auths(self, authors):
		res = []

		for a in authors.split(', '):
			a = a.split(' ')
			res.append({
				'given_name': a[:-1],
				'family_name': a[-1] if len(a) > 1 else '',
				'institution': None
			})

		return res


	'''
	Get list of papers from proceedings page
	
	outputs:
	papers (dict) Key is paper's title and value is dict of paper's metadata
	'''
	def proceedings(self):

		resp = urllib.request.urlopen(self.get_proceedings_url())
		soup = BeautifulSoup(resp.read(), 'html.parser')
		tags = soup.find_all('li')
		
		papers = {}

		for t in tags:
			atag = t.find('a')
			if atag['href'].startswith('/paper'):
				papers[atag.text] = {'title': atag.text, 'href': ''.join([self.base, atag['href']]), 'authors': self.format_auths(t.find('i').text)}

		return papers


	'''
	This should only be called when the conference has not occurred yet, but accepted papers were released. In this window,
	NeurIPS has not posted the meta data yet.

	outputs:
	authors (list) List of dicts of authors name and affiliation
	'''
	def pre_proceedings(self):

		def neurips_authors(pre_authors):
			'''
			In some cases, authors lists may differ. Either author(s) are missing or there 
			are extra the order may also differ
			'''
			authors = []

			for auth in pre_authors.split(' · '):
				auth = auth.split('(')
				affiliation = auth[-1][:-1]
				name = auth[0].strip().split()

				authors.append({
					'given_name': ' '.join(name[:-1]),
					'family_name': name[-1] if len(name) > 1 else '',
					'institution': affiliation
				})

			return authors


		now = datetime.datetime.now()

		pre_url = f'https://nips.cc/Conferences/{now.year}/AcceptedPapersInitial'
		pro_url = self.get_proceedings_url()

		resp = urllib.request.urlopen(pre_url)
		soup = BeautifulSoup(resp.read(), 'html.parser')
		main = soup.find('main', {'id': 'main'})
		accepted = main.find_all('div')[-1].find_all('p')
		papers, proceedings = [], self.proceedings()

		for p in accepted[2:]:
			title = p.find('b').text
			authors = neurips_authors(p.find('i').text)
			href, hash_id = '', ''

			try:
				href = proceedings[title]['href']
				hash_id = href.split('/')[-1].split('-')[0]
			except KeyError:
				pass

			papers.append({'title': title, 'url': self.format_pdf_url(hash_id), 'authors': authors, 'award': [], 'hash': hash_id})

		return papers

	
	'''
	Get all accepted papers from NIPS. In some cases, the name of the final submission is different
	from the name of the paper on Arxiv. May need to use binary classifier for these cases.

	outputs:
	papers (list) List of dicts of accepted papers with keys as the paper title and value as the authors.
	'''
	def accepted_papers(self, use_checkpoint=True):

		now = datetime.datetime.now()

		if now.year == int(self.year):
			return self.pre_proceedings()
		else: 
			return self.get_source_metadata(list(self.proceedings().values()))