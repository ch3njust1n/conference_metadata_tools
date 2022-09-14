'''
'''
import os
import sys
import time
import logging

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from scrape import utils
from tqdm import tqdm

class ICLR(object):
	def __init__(self, year, logname):
		self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'scrape/chromedriver'))
		self.log = logging.getLogger(logname)
		self.year = str(year)
		self.base = ''
		self.titles = set()
		self.proceedings_urls = {
			'2013': ['https://iclr.cc/archive/2013/conference-proceedings.html'],
			'2014': ['https://iclr.cc/archive/2014/conference-proceedings/'],
			'2015': ['https://iclr.cc/archive/www/doku.php%3Fid=iclr2015:accepted-main.html'],
			'2016': ['https://iclr.cc/archive/www/doku.php%3Fid=iclr2016:accepted-main.html'],
			'2017': ['https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:conference_posters.html'],
			'2018': [
				'https://openreview.net/group?id=ICLR.cc/2018/Conference',
				'https://openreview.net/group?id=ICLR.cc/2018/Workshop'
			],
			'2019': [
				'https://openreview.net/group?id=ICLR.cc/2019/Conference',
				'https://openreview.net/group?id=ICLR.cc/2019/Workshop'
			],
			'2020': [
				'https://openreview.net/group?id=ICLR.cc/2020/Conference',
				'https://openreview.net/group?id=ICLR.cc/2020/Workshop'
			],
			'2021': [
				'https://openreview.net/group?id=ICLR.cc/2021/Conference',
				'https://openreview.net/group?id=ICLR.cc/2021/Workshop'
			],
			'2022': [
				# 'https://openreview.net/group?id=ICLR.cc/2022/Conference',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/DGM4HSD',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/DLG4NLP',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/MLDD',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/AfricaNLP',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/GPL',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/PAIR2Struct',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/EmeCom',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/DL4C',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/Cells2Societies',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/GTRL',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/ALOE',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/GMS',
				'https://openreview.net/group?id=ICLR.cc/2022/Workshop/OSC'
			]
		}


	'''
	outputs:
	pages (int) Number of pages
	'''
	def get_page_count(self):
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		pagination_xpath = '/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[2]/nav/ul'
		pagination_bar = self.driver.find_element(By.XPATH, pagination_xpath)
		return len(pagination_bar.find_elements(By.TAG_NAME, 'li')) - 4


	'''
	inputs:
 
	outputs:
 	'''
	def extract_metadata(self, section):
		oral_submissions_class = 'note '
		oral_submissions_id = section

		# total_pages = self.get_page_count()
		total_pages = 20
		self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)

		self.log.debug(f'{section} has {total_pages} pages')
		proceedings = []
  
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

		# TODO: Not entering this loop for workshops
		for page in range(total_pages):
			submission_section = self.driver.find_element(By.ID, oral_submissions_id)
			submission_list = submission_section.find_elements(By.CLASS_NAME, oral_submissions_class)
			total_submissions = len(submission_list)
			
			self.log.debug(f'{total_submissions} on page {page}')

			for i in range(1, total_submissions+1):
				try:
					title_xpath = f'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[3]/ul/li[{i}]/h4/a[1]'
					title = self.driver.find_element(By.XPATH, title_xpath).text.strip()
					
					if not title in self.titles:
						self.titles.add(title)
      
						author_xpath = f'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[3]/ul/li[{1}]/div[1]'
						pdf_xpath = f'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[3]/ul/li[{i}]/h4/a[2]'
						authors = self.driver.find_element(By.XPATH, author_xpath)
						pdf = self.driver.find_element(By.XPATH, pdf_xpath) 

						proceedings.append({
							"title": title,
							"authors": extract_authors(authors.text),
							"url": pdf.get_property('href')
						})

				except Exception as e:
					self.log.debug(f'page: {page}\tpaper: {i}\t{e}')

			# Add 4 to account for both left arrows in pagination
			if page < total_pages - 1:
				try:
					self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
					nav_xpath = f'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[2]/nav/ul/li[{page+4}]/a'
					self.driver.find_element(By.XPATH, nav_xpath).click()
					self.driver.execute_script("window.scrollTo(0, 0);")
				except Exception as e:
					break

		return proceedings
		

	'''
	Get all accepted papers from NIPS. In some cases, the name of the final submission is different
	from the name of the paper on Arxiv. May need to use binary classifier for these cases.

	inputs:

	outputs:
	papers (list) List of dicts of accepted papers with keys as the paper title and value as the authors.
	'''
	def accepted_papers(self, use_checkpoint=True):
		
		proceedings = []
		conf_links = self.proceedings_urls[self.year]

		if isinstance(conf_links, str): 
			conf_links = [conf_links]
   
   
		sections = {
			'poster-submissions': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[1]/ul/li[4]/a'
			],
			'spotlight-submissions': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[1]/ul/li[3]/a'
			],
			'oral-submissions': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[1]/ul/li[2]/a'
			],
			'accept--poster-': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[1]/ul/li[3]/a',
				'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[3]'
          	],
			'accept--oral-': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[1]/ul/li[2]/a',
				'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[2]'
			],
			'accept': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[2]',
				'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[4]',
				'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[3]'
			],
			'accept-oral-': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[2]'
			],
			'accept-poster-': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[3]'
			],
			'accept--best-paper-': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[2]'
			],
			'accept--spotlight-': [
       			'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[3]',
				'/html/body/div[1]/div[3]/div/div/main/div/div[3]/div/div[2]/div[2]'
          	]
		} 

		with tqdm(total=len(sections) * len(conf_links)) as pbar:
			for i, link in enumerate(conf_links):
				self.log.debug(f'============================\n{link}\n============================\n')
		
				if i == 0:
					self.driver.get(link)
				else:
					self.driver.switch_to_window(self.driver.window_handles[-1])
					self.driver.get(link)


				delay = 10

				# TODO: If the tab is empty, this will block indefinitely. Need to figure out a better solution.
				search_field_xpath = '//*[@id="paper-search-input"]'
				try:
					wait = WebDriverWait(self.driver, delay)
					wait.until(EC.element_to_be_clickable((By.XPATH, search_field_xpath)))
				except TimeoutException:
					self.log.debug(f'timeout: {link}')


				for tab_id, tab_xpath in sections.items():
					
					# Move to the top of the page
					self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
					time.sleep(3)

					try:
						# Click on tab
						for xpath in tab_xpath:
							tab = self.driver.find_element(By.XPATH, xpath)
							if tab.text.lower() != 'reject':
								tab.click()
								proceedings.extend(self.extract_metadata(tab_id))
					except Exception as e:
						self.log.debug(f'Error getting {link}')
						self.log.debug(e)
      
					pbar.update(1)

		self.log.debug(f'total": {len(proceedings)}')
		utils.save_json(f'./iclr', f'iclr_{2022}', proceedings)