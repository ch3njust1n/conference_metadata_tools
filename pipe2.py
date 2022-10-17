'''
TODO: Merge this into main and refactor as a full pipeline
'''

import json
import numpy as np
from time import perf_counter
from difflib import SequenceMatcher
from collections import defaultdict
from itertools import product

from tqdm import tqdm
from pprint import pprint

import scrape.utils as utils
from scrape.parse.extractor import OCRExtractor

from pdf2image import convert_from_path, pdfinfo_from_path


def similarity(a, b):
	return SequenceMatcher(None, a, b).ratio()

def main():
	start_time = perf_counter()
	filename = '/Volumes/SG-2TB/ijcai/ijcai-1979.pdf'
	model = OCRExtractor(target_section='Title')
	titles = set()
 
	with open('temp/output/ijcai1979.json', 'r') as file:
		data = json.load(file)
		titles = {p['title'].lower().strip() for p in data}
  
	pairs = defaultdict(list)
	index = defaultdict(list)
 
	info = pdfinfo_from_path(filename, userpw=None, poppler_path=None)
	maxPages = info["Pages"]
	images = []

	for page in range(1, maxPages+1, 10) : 
		images.extend(convert_from_path(filename, dpi=200, first_page=page, last_page = min(page+10-1,maxPages)))

	total = len(images)
 
	print(f'Saving pages')
	for i, img in tqdm(enumerate(images)):
		img.save(f'/Volumes/SG-2TB/ijcai/pages/{i}.jpg', 'JPEG')
	
	pages = 608
	for i in tqdm(range(pages)):
		pairs[i].extend(model.extract(f'/Volumes/SG-2TB/ijcai/pages/{i}.jpg'))
  
	utils.save_json('./temp/output', 'pageIndex-0', pairs)

	for i in range(len(pairs)):
		
		candidates = [' '.join(st.split()).lower() for st in pairs[i]]
		page_scores = defaultdict(int)
  
		for a, b in product(candidates, titles):
			page_scores[(a,b)] = similarity(a, b)
		
		try:
			key = max(page_scores, key=lambda key: page_scores[key])
			score = page_scores[key]
			print(key, score)
			ground_truth = key[0]
			if score >= 0.9: index[i] = ground_truth
		except ValueError as e:
			continue

	# Dictionary with keys as page numbers and values as paper titles
	# Use this dictionary to split the monolithic pdf into individual papers
	pprint(index)
 
	utils.save_json('./temp/output', 'pageIndex', index)
	print(f'time elapsed: {perf_counter() - start_time} seconds')

if __name__ == "__main__":
	main()