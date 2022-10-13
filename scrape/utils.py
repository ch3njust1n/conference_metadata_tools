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
url    (string) BeautifulSoup element
tag    (string) Tag type
prop   (string) Property contained in tag
substr (string) Substring of property

outputs:
tags   (list) List of bs4.element.Tag objects with specific properties containing substrings
'''
def get_tags(url, tag, prop, substr):
	page = urllib.request.urlopen(url)
	html = BeautifulSoup(page.read(), 'html.parser', from_encoding='utf-8')
	return [t[prop] for t in html.find_all(tag, href=True) if substr in t[prop]]


'''
Get years for completed conferences

inputs:
conf (string) Name of the conference

outputs:
years (set) Years completed
'''
def load_cached_years(conf):
    try:
        api = f"https://github.com/ch3njust1n/conference_metadata/tree/main/api/{conf}"
        resp = urllib.request.urlopen(api)
        soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
        files = [link.text for link in soup.find_all('a') if link.text.endswith('.json')]
        
        return {re.search(r'\d{4}', file).group() for file in files}
    except Exception as e:
        return set()



'''
inputs:
parts (list) List of URL paths

outputs:
url (string) Complete URL
'''
def join_url(parts):
    return '/'.join(p.strip('/') for p in parts)


'''
'''
def capitalize_hyphenated(name):
    return ('-'.join([i.capitalize() for i in name.split('-')])).title()


'''
Format authors list

inputs:
authors (str) Author names separated by commas

outputs:
authors (list) List of dicts of author information
'''
def format_auths(authors):
    res = []

    for a in authors:
        a = a.split()
        res.append({
            'given_name': capitalize_hyphenated(' '.join(a[:-1]).capitalize()),
            'family_name': capitalize_hyphenated(a[-1]).title() if len(a) > 1 else '',
            'institution': None
        })

    return res

'''
Detect if a string contains numbers 00 - 99

input:
string (str) String containing numbers

output:
result (bool) True if string contains numbers 00 - 99
'''
def has_two_digits(string):
    pattern = r"\D\d\d\D"
    result = re.search(pattern, string)
    return result != None


'''
Extracts any two digit number from a string

input:
text (str) String containing numbers

output:
year (str) Full year
'''
def get_two_digit_year(text):
    regex = r"\D(\d\d)\D"
    matches = re.finditer(regex, text)
    for match in matches:
        year = match.group(1)
        if int(year) > 22:
            return f'19{year}'
        else:
            return f'20{year}'


'''
Extracts any four digit number from a string

input:
text (str) String containing numbers

output:
year (str) Full year
'''
def get_four_digit_year(text):
    regex = r"\D(\d\d\d\d)\D"
    matches = re.finditer(regex, text)
    for match in matches:
        return match.group(1)
