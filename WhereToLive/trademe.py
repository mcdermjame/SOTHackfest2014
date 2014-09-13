CACHE_TIME = 3600 # in seconds
CACHE_DIR = "trademecache"

import trademe_key

URLBASE = "https://api.tmsandbox.co.nz" if trademe_key.SANDBOX else "https://api.trademe.co.nz"
import urllib2
import os.path
import time
import json

def _geturl(path):
	"""GETs the specified path (which should start with /) under URLBASE, and returns the response body."""
	headers = {}
	if trademe_key.OAUTH_TOKEN != "":
		headers['Authorization'] = 'OAuth oauth_consumer_key="'+trademe_key.CONSUMER_KEY+'", oauth_token="'+trademe_key.OAUTH_TOKEN+'", oauth_signature_method="PLAINTEXT", oauth_signature="'+trademe_key.CONSUMER_SECRET+'&'+trademe_key.OAUTH_TOKEN_SECRET+'"'
	else:
		headers['Authorization'] = 'OAuth oauth_consumer_key="'+trademe_key.CONSUMER_KEY+'", oauth_signature_method="PLAINTEXT", oauth_signature="'+trademe_key.CONSUMER_SECRET+'&"'
		
	try:
		request = urllib2.Request(URLBASE+path, None, headers)
		conn = urllib2.urlopen(request)
		data = conn.read()
		conn.close()
	except urllib2.HTTPError as e:
		print(e.read())
		raise
	return data
	
def _checkcachefile(filename):
	"""Returns True if the specified file (in the cache directory) exists and was modified recently
	(within CACHE_TIME seconds)."""
	fullpath = CACHE_DIR + "/" + filename
	if not os.path.exists(fullpath):
		return False
	staleness = time.time() - os.path.getmtime(fullpath)
	return staleness < CACHE_TIME

def _readcachefile(filename):
	with open(CACHE_DIR+"/"+filename, "r") as f:
		return f.read()

def _writecachefile(filename, data):
	with open(CACHE_DIR+"/"+filename, "w") as f:
		f.write(data)
	
def _getcachedurl(path, cachefilename):
	"""Returns the content of the specified URL, cached in CACHE_DIR/cachefilename. If the cache file was
	written recently, the URL will not be accessed."""
	
	if _checkcachefile(cachefilename):
		return _readcachefile(cachefilename)
	
	data = _geturl(path)
	_writecachefile(cachefilename, data)
	return data

_locality_data = None
def get_localities():
	"""
	Returns the TradeMe locality/district/suburb list.
	Example of format (in Python dictionary/list notation, which also corresponds to JSON):
		[
			{
				"LocalityId": 9,
				"Name": "Northland",
				"Districts": [
					{
						"DistrictID": 1,
						"Name": "Far North",
						"Suburbs": [
							{
								"SuburbID": 2129,
								"Name": "Ahipara",
								"AdjacentSuburbs": [2129]
							},
							... other suburbs in district...
						]
					},
					... other districts in locality...
				]
			},
			... other localities (regions)...
		]
	
	Note: the special locality with ID 100 means "all localities" and contains no districts
	"""
	global _locality_data
	if _locality_data is None:
		_locality_data = json.loads(_getcachedurl("/v1/Localities.json", "Localities.json"))
	return _locality_data

_job_categories = None
def get_job_categories():
	"""
	Returns the job categories list.
	Example format:
		[
			{
				"Name": "Accounting",
				"Code": "5001",
				"SubCategories": [
					{
						"Name": "Accountants",
						"Code": "5002",
						"SubCategories": []
					},
					... other sub-categories...
				]
			},
			... other top-level categories...
		]
	Note: Subcategories can have subsubcategories and so on, but currently none do.
	"""
	global _job_categories
	if _job_categories is None:
		_job_categories = json.loads(_getcachedurl("/v1/Categories/Jobs.json", "JobCategories.json"))
		
		# Change 'SubCategories': None to 'SubCategories': []
		def fix_subcategories(category):
			if category['SubCategories'] == None:
				category['SubCategories'] = []
			else:
				for subcat in category['SubCategories']:
					fix_subcategories(subcat)
		for category in _job_categories:
			fix_subcategories(category)
		
	return _job_categories
	

print(repr(get_job_categories()))