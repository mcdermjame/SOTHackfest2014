"""
Format of name-map.txt: each line is a TradeMe district name, followed by a comma, followed by a territorial authority name from the census.
"""

import csv
import sys
sys.path += ['WhereToLive']

import trademe

census_names = set()

with open('WhereToLive/censusdata/2013-mb-dataset-Total-New-Zealand-Individual-Part-1.csv', 'r') as f:
	r = csv.reader(f)
	header = r.next()
	while r.next()[0] != 'Total New Zealand':
		pass # skip over meshblocks
	while r.next()[0] != 'Total New Zealand':
		pass # skip over area units
	while r.next()[0] != 'Total New Zealand':
		pass # skip over wards
	
	# territorial authorities
	for line in r:
		if line[0] == 'Total New Zealand':
			# could process totals here
			break
		
		if line[0][3] != ' ':
			print(line)
			assert False
		
		census_names.add(line[0][4:])
	
	while r.next()[0] != 'Total New Zealand':
		pass # skip over regions
	
	"""# CMBs
	for line in r:
		if line[0] == 'Total Auckland Local Board':
			break
		
		if line[0][9] != ' ':
			print(line)
			assert False
		
		census_names.add(line[0][10:])"""

regions = trademe.get_localities()
trademe_names = set(district['Name'] for region in regions for district in region['Districts'])

mapped_tmnames = set()
mapped_csnames = set()

with open('WhereToLive/censusdata/name-map.txt', 'r') as f:
	for line in f:
		tmname, csname = line.replace('\n','').split(',')
		if tmname not in trademe_names:
			print('not valid: TM'+tmname)
		else:
			mapped_tmnames.add(tmname)
		if csname not in census_names:
			print('not valid: CS'+csname)
		else:
			mapped_csnames.add(csname)

mapped_csnames.add('Area Outside Territorial Authority')
mapped_csnames.add('Chatham Islands Territory')

if mapped_tmnames != trademe_names: print('Unmapped TradeMe names: '+repr(trademe_names - mapped_tmnames))
if mapped_csnames != census_names: print('Unmapped census names: '+repr(census_names - mapped_csnames))
