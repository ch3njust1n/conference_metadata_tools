'''
TODO: Merge this into main and refactor as a full pipeline
'''

import json
import numpy as np
from difflib import SequenceMatcher
from collections import defaultdict
from itertools import product

from tqdm import tqdm
from pprint import pprint

import scrape.utils as utils
from scrape.parse.extractor import OCRExtractor

from pdf2image import convert_from_path


def similarity(a, b):
	return SequenceMatcher(None, a, b).ratio()

def main():
	model = OCRExtractor(target_section='Title')
	titles = set()
 
	with open('temp/output/ijcai1979.json', 'r') as file:
		data = json.load(file)
		titles = {p['title'].lower().strip() for p in data}
  
	index = defaultdict(list)
	images = convert_from_path('/Volumes/SG-2TB/ijcai/ijcai-1979.pdf')
	
	for i, img in tqdm(enumerate(images)):
		index[i].extend(model.extract(np.array(img)))

	for i in tqdm(range(len(index))):
		page_scores = defaultdict(int)
		candidates = [' '.join(st.split()).lower() for st in index[i]]
  
		for a, b in product(candidates, titles):
			page_scores[(a,b)] = similarity(a, b)
		
		index[i] = max(page_scores, key=lambda key: page_scores[key])[1]

	# Dictionary with keys as page numbers and values as paper titles
    # Use this dictionary to split the monolithic pdf into individual papers
	pprint(index)
 
	utils.save_json('./output', 'pageIndex', index)

if __name__ == "__main__":
	main()