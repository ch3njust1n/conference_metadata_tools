'''
'''
import os
import urllib
import logging
import configparser
from time import time
from datetime import date
from itertools import product

from tqdm import tqdm

import scrape.metadata as md
import scrape.utils as utils
import scrape.updater as updater


def convert_bool(val):
	if val.lower() in ['true', 't', '1']:
		return True
	elif val.lower() in ['false', 'f', '0']:
		return False
	else:
		raise Exception('Invalid boolean value')


def main():
	start_time = time()
	config = configparser.ConfigParser(allow_no_value=True)
	config.read('config.ini')
	cfg = config['DEFAULT']

	name = cfg['conference']
	year = cfg['year']
	save_dir = cfg['save_dir']
	log_level = cfg['log_level']
	use_checkpoint = convert_bool(cfg['use_checkpoint'])
	task = cfg['task'].lower()
 
	if not task in {'update', 'scrape'}:
		raise ValueError(f'Task {task} is not supported')
 
	if not os.path.isdir(save_dir):
		os.makedirs(save_dir, exist_ok=True) 
  
	if not os.path.isdir('temp') or not os.path.isdir('temp/failed'):
		os.makedirs('temp/failed', exist_ok=True)
  
	if not os.path.isdir('temp/logs'):
		os.makedirs('temp/logs', exist_ok=True)
  
	logname = f'temp/logs/{name}{year}-{utils.unix_epoch()}.log'
 
	print(f'log file: {logname}')
  
	logging.basicConfig(
	 	level=utils.log_level(log_level), 
		filename=logname,
	 	filemode='w', 
	  	format='%(name)s - %(levelname)s - %(message)s'
	)

	if task == 'scrape':
		metadata = md.conference(name, year, logname).accepted_papers(use_checkpoint)
		utils.save_json(save_dir, f'{name}_{year}', metadata)

	elif task == 'update':
		
		supported_api = 'https://raw.githubusercontent.com/ch3njust1n/conference_metadata/main/api/conferences.txt'
		conferences = [line.decode('utf-8').strip() for line in urllib.request.urlopen(supported_api)] # TODO: make programmatic with * for all
		years = range(1970, date.today().year + 1) # TODO: make programmatic with * for all
		prod = list(product(conferences, years))
  
		cache_dir = '.cache'
  
		if not os.path.exists(cache_dir):
			os.makedirs(cache_dir)
  
		with tqdm(total=len(prod)) as pbar:
			for name, yr in prod:
				manager = updater.Updater(name, yr, logname, cache_dir)
				manager.update('abstract') # TODO: make programmable later
				pbar.update(1)
 
	print('total time: ', time() - start_time)
	

if __name__ == '__main__':
	main()