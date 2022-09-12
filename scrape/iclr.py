'''
'''
import datetime
import urllib.request

from bs4 import BeautifulSoup

class ICLR(object):
	def __init__(self, year, logname):
		self.year = str(year)
		self.base = ''
		self.proceedings_urls = {
			'2013': 'https://iclr.cc/archive/2013/conference-proceedings.html',
			'2014': 'https://iclr.cc/archive/2014/conference-proceedings/',
			'2015': 'https://iclr.cc/archive/www/doku.php%3Fid=iclr2015:accepted-main.html',
			'2016': 'https://iclr.cc/archive/www/doku.php%3Fid=iclr2016:accepted-main.html',
			'2017': 'https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:conference_posters.html',
			'2018': {
				'poster': 'https://openreview.net/group?id=ICLR.cc/2018/Conference',
				'workshop': 'https://openreview.net/group?id=ICLR.cc/2018/Workshop'
			},
			'2019': {
				'poster': 'https://openreview.net/group?id=ICLR.cc/2018/Conference',
				'workshop': 'https://openreview.net/group?id=ICLR.cc/2018/Workshop'
			},
		}


	'''
	Get all accepted papers from NIPS. In some cases, the name of the final submission is different
	from the name of the paper on Arxiv. May need to use binary classifier for these cases.

	outputs:
	papers (list) List of dicts of accepted papers with keys as the paper title and value as the authors.
	'''
	def accepted_papers(self, use_checkpoint=True):

		now = datetime.datetime.now()

		resp = urllib.request.urlopen(self.proceedings_urls[self.year])
		soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='iso-8859-1')
		for i in soup.find_all('span'):
			print(i.text)

		if now.year == int(self.year):
			pass