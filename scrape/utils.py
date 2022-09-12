'''
'''
import os
import re
import json
import logging
from time import time
import urllib.request
from bs4 import BeautifulSoup, Tag

'''
Save json data

inputs:
filename (str)  Name of output file
data     (list) JSON object
'''
def save_json(save_dir, filename, data):
	
	if not os.path.isdir(save_dir):
		os.makedirs(save_dir, exist_ok=True)

	with open(os.path.join(save_dir, filename+'.json'), 'w', encoding='utf-8') as file:
		json.dump(data, file, ensure_ascii=False, indent=4)


'''
Clean temp directory
'''
def clean_temp():
    
    files = os.listdir('temp')
    [os.remove(f) for f in files]
    
    
'''
Assumes log file names are formatted as <conference_name><year>-<unix_epoch>.json

inputs:
conference (string) Conference name
year       (year)   Year of the conference
directory  (string) Temp directory path

outputs:
latest_log (string) Filename of the latest log
'''
def get_latest_log(conference, year, directory='temp'):
    
    return sorted([f for f in os.listdir(directory) if f.startswith(f'{conference}{year}')])[-1]
    

'''
'''
def log_level(level):
    level = level.lower()
    
    if level == 'debug':   return logging.DEBUG
    if level == 'info':    return logging.INFO
    if level == 'warning': return logging.WARNING
    if level == 'error':   return logging.ERROR
    if level == 'critcal': return logging.CRITICAL
    
    return ''


'''
Return Unix Epoch time in milliseconds
'''
def unix_epoch():
    decimals = len(str(time()).split('.'))
    return int(time() * 10**decimals)


'''
inputs:
html   (bs4.element.Tag) BeautifulSoup element
tag    (string)          Tag type
prop   (string)          Property contained in tag
substr (string)          Substring of property

outputs:
tags   (list) List of bs4.element.Tag objects with specific properties containing substrings
'''
def get_tags(html, tag, prop, substr): 
    return [t[prop] for t in html.find_all(tag) if substr in t[prop]]


'''
Get years for completed conferences

inputs:
conf (string) Name of the conference

outputs:
years (set) Years completed
'''
def load_cached_years(conf):
    api = f"https://github.com/ch3njust1n/conference_metadata/tree/main/api/{conf}"
    resp = urllib.request.urlopen(api)
    soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
    files = [link.text for link in soup.find_all('a') if link.text.endswith('.json')]
    
    return {re.search(r'\d{4}', file).group() for file in files}


'''
inputs:
parts (list) List of URL paths

outputs:
url (string) Complete URL
'''
def join_url(parts):
    return '/'.join(p.strip('/') for p in parts)
