URLBASE = "http://api.tmsandbox.co.nz"
CACHE_TIME = 3600 # in seconds
CACHE_DIR = "trademecache"

import urllib2
import os.path
import time
import json

def _geturl(path):
	"""GETs the specified path (which should start with /) under URLBASE, and returns the response body."""
	conn = urllib2.urlopen(URLBASE+path)
	data = conn.read()
	conn.close()
	return data
	
def _checkcachefile(filename):
	"""Returns True if the specified file (in the cache directory) exists and was modified recently
	(within CACHE_TIME seconds)."""
	fullpath = CACHE_DIR + "/" + filename
	if not os.path.exists(fullpath):
		return False
	staleness = time.time() - os.path.getmtime(fullpath)
	return staleness < CACHE_TIME
	
def _getcachedurl(path, cachefilename):
	"""Returns the content of the specified URL, cached in CACHE_DIR/cachefilename. If the cache file was
	written recently, the URL will not be accessed."""
	cachepath = CACHE_DIR + "/" + cachefilename
	if _checkcachefile(cachefilename):
		with open(cachepath, "r") as f:
			return f.read()
	
	data = _geturl(path)
	with open(cachepath, "w") as f:
		f.write(data)
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
	

print(repr(get_localities()))