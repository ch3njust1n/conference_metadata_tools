'''
'''
import os
import sys
import logging
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains

from pprint import pprint
from scrape import utils

class ICLR(object):
	def __init__(self, year, logname):
		self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'scrape/chromedriver'))
		self.log = logging.getLogger(logname)
		self.year = str(year)
		self.base = ''
		self.proceedings = defaultdict(dict)
		self.proceedings_urls = {
			'2013': 'https://iclr.cc/archive/2013/conference-proceedings.html',
			'2014': 'https://iclr.cc/archive/2014/conference-proceedings/',
			'2015': 'https://iclr.cc/archive/www/doku.php%3Fid=iclr2015:accepted-main.html',
			'2016': 'https://iclr.cc/archive/www/doku.php%3Fid=iclr2016:accepted-main.html',
			'2017': 'https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:conference_posters.html',
			'2018': {
				'main': 'https://openreview.net/group?id=ICLR.cc/2018/Conference',
				'workshop': 'https://openreview.net/group?id=ICLR.cc/2018/Workshop'
			},
			'2019': {
				'main': 'https://openreview.net/group?id=ICLR.cc/2019/Conference',
				'workshop': 'https://openreview.net/group?id=ICLR.cc/2019/Workshop'
			},
			'2020': {
				'main': 'https://openreview.net/group?id=ICLR.cc/2020/Conference',
				'workshop': 'https://openreview.net/group?id=ICLR.cc/2020/Workshop'
			},
			'2021': {
				'main': 'https://openreview.net/group?id=ICLR.cc/2021/Conference',
				'workshop': 'https://openreview.net/group?id=ICLR.cc/2021/Workshop'
			},
			'2022': {
				'main': 'https://openreview.net/group?id=ICLR.cc/2022/Conference',
				'workshop': 'https://openreview.net/group?id=ICLR.cc/2022/Workshop'
			}
		}


	'''
	outputs:
	pages (int) Number of pages
	'''
	def get_page_count(self):
		pagination_xpath = '//*[@id="oral-submissions"]/nav/ul'
		pagination_bar = self.driver.find_element(By.XPATH, pagination_xpath)
		
		# ignore nav buttons
		return len(pagination_bar.find_elements(By.TAG_NAME, 'li')) - 4


	'''
	inputs:
 
	outputs:
 	'''
	def extract_metadata(self):
		oral_submissions_class = 'note '
		oral_submissions_id = 'oral-submissions'
		total_pages = self.get_page_count()
  
		def extract_authors(authors):
			result = []

			for fullname in authors.split(','):
				fullname = fullname.strip().split()

				result.append({
					"given_name": ' '.join(fullname[:-1]),
					"family_name": fullname[-1],
					"institution": ''
				})

			return result

		for page in range(total_pages):
			submission_section = self.driver.find_element(By.ID, oral_submissions_id)
			submission_list = submission_section.find_elements(By.CLASS_NAME, oral_submissions_class)
			total_submissions = len(submission_list)
			print(f'{total_submissions} on page {page}')

			for i in range(1, total_submissions+1):
				try:
					title = self.driver.find_element(By.XPATH, f'//*[@id="oral-submissions"]/ul/li[{i}]/h4/a[1]').text.strip()
					authors = self.driver.find_element(By.XPATH, f'//*[@id="oral-submissions"]/ul/li[{i}]/div[1]')
					pdf = self.driver.find_element(By.XPATH, f'//*[@id="oral-submissions"]/ul/li[{i}]/h4/a[2]')
					
					if title not in self.proceedings:
						self.proceedings[title] = {
							"title": title,
							"authors": extract_authors(authors.text),
							"url": pdf.get_property('href')
						}
				except Exception as e:
					self.log.debug(f'page: {page}\tpaper: {i}\t{e}')

			# Add 4 to account for both left arrows in pagination
			if page < total_pages - 1:
				self.driver.find_element(By.XPATH, f'//*[@id="oral-submissions"]/nav/ul/li[{page+4}]/a').click()
		

	'''
	Get all accepted papers from NIPS. In some cases, the name of the final submission is different
	from the name of the paper on Arxiv. May need to use binary classifier for these cases.

	inputs:

	outputs:
	papers (list) List of dicts of accepted papers with keys as the paper title and value as the authors.
	'''
	def accepted_papers(self, use_checkpoint=True):

		url = self.proceedings_urls['2022']['main']
		sections = ['oral-submissions', 'spotlight-submissions', 'poster-submissions']

		for sect in sections:
			self.driver.get('#'.join([url, sect]))
			delay = 500

			search_field_xpath = '//*[@id="paper-search-input"]'
			wait = WebDriverWait(self.driver, delay)
			wait.until(EC.element_to_be_clickable((By.XPATH, search_field_xpath)))

			self.extract_metadata()

		# Convert to JSON format
		self.proceedings = [{ 'title': key, 'authors': val['authors'], 'url': val['url']} for key, val in self.proceedings.items()]
		print(f'total: {len(self.proceedings)}')
  
		utils.save_json(f'./iclr', f'iclr_{2022}', self.proceedings)