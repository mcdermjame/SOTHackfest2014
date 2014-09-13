import csv
import sys
import json
import os.path
sys.path += ['WhereToLive']
import trademe

census_names = set()

# First: read all census data files, which contain the same rows but different columns,
# and combine them into a single dictionary {TAname: {header: data}}. Ignore all area types
# except for territorial authorities.

filenames = ["2013-mb-dataset-Total-New-Zealand-Family.csv",
"2013-mb-dataset-Total-New-Zealand-Household.csv",
"2013-mb-dataset-Total-New-Zealand-Individual-Part-1.csv",
"2013-mb-dataset-Total-New-Zealand-Individual-Part-2.csv",
"2013-mb-dataset-Total-New-Zealand-Individual-Part-3a.csv",
"2013-mb-dataset-Total-New-Zealand-Individual-Part-3b.csv",
"2013-mb-dataset-Total-New-Zealand-Dwelling.csv"]

dataByTA = {}

CONFIDENTIAL = 0
UNAVAILABLE = 0

if os.path.exists('WhereToLive/censusdata/combined.json'):
	with open('WhereToLive/censusdata/combined.json', 'r') as f:
		dataByTA = json.loads(f.read())
else:
	for filename in filenames:
		with open('WhereToLive/censusdata/'+filename, 'r') as f:
			r = csv.reader(f)
			header = r.next()
			for k in range(len(header)):
				header[k] = header[k].replace('\x96', '-')
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
					
				areaName = line[0][4:]
				
				if areaName not in dataByTA: dataByTA[areaName] = {}
				area = dataByTA[areaName]
				
				for k in range(3, len(line)):
					if line[k] == '..C':
						area[header[k]] = CONFIDENTIAL
					elif line[k] == '..':
						area[header[k]] = UNAVAILABLE
					elif line[k].find('.') < 0:
						area[header[k]] = int(line[k])
					else:
						area[header[k]] = float(line[k])

	with open('WhereToLive/censusdata/combined.json', 'w') as f:
		json.dump(dataByTA, f)

# Translate to TradeMe names
dataByDistrict = {}
seen_csnames = set()
with open('WhereToLive/censusdata/name-map.txt', 'r') as f:
	for line in f:
		trademe_name, census_name = line.replace('\n', '').split(',')
		if census_name not in seen_csnames:
			dataByDistrict[trademe_name] = dataByTA[census_name]
			seen_csnames.add(census_name)
		else:
			raise Exception('Multiple trademe districts correspond to '+census_name)
del seen_csnames

with open('WhereToLive/censusdata/columns.txt', 'w') as f:
	for header in sorted(dataByDistrict['Auckland City'].keys()):
		f.write(header+'\n')

# We want:
# Transportation data (how people get to work) (car/bus/cycle/walk)
# Average rent
# Age group
# Population

summaryDataByDistrict = {}
for district in dataByDistrict.keys():
	data = dataByDistrict[district]

	population = data['2013_Census_census_usually_resident_population_count(1)']
	
	census_night_population = float(data['2013_Census_census_night_population_count(2)'])

	mean_age = (
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_0-4_Years'] * 2 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_10-14_Years'] * 12 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_15-19_Years'] * 17 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_20-24_Years'] * 22 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_25-29_Years'] * 27 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_30-34_Years'] * 32 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_35-39_Years'] * 37 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_40-44_Years'] * 42 + 
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_45-49_Years'] * 47 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_5-9_Years'] * 7 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_50-54_Years'] * 52 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_55-59_Years'] * 57 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_60-64_Years'] * 62 +
		data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_65_years_and_Over'] * 75
	) / census_night_population
	
	cmt_bicycle = data['2013_Census_main_means_of_travel_to_work_for_the_employed_census_usually_resident_population_count_aged_15_years_and_over(1)_Bicycle']
	cmt_drove = data['2013_Census_main_means_of_travel_to_work_for_the_employed_census_usually_resident_population_count_aged_15_years_and_over(1)_Drove_a_Company_Car_Truck_or_Van'] \
		+ data['2013_Census_main_means_of_travel_to_work_for_the_employed_census_usually_resident_population_count_aged_15_years_and_over(1)_Drove_a_Private_Car_Truck_or_Van'] \
		+ data['2013_Census_main_means_of_travel_to_work_for_the_employed_census_usually_resident_population_count_aged_15_years_and_over(1)_Passenger_in_a_Car_Truck_Van_or_Company_Bus'] \
		+ data['2013_Census_main_means_of_travel_to_work_for_the_employed_census_usually_resident_population_count_aged_15_years_and_over(1)_Motor_Cycle_or_Power_Cycle']
	cmt_publictransport = data['2013_Census_main_means_of_travel_to_work_for_the_employed_census_usually_resident_population_count_aged_15_years_and_over(1)_Public_Bus'] \
		+ data['2013_Census_main_means_of_travel_to_work_for_the_employed_census_usually_resident_population_count_aged_15_years_and_over(1)_Train']
	cmt_walk = data['2013_Census_main_means_of_travel_to_work_for_the_employed_census_usually_resident_population_count_aged_15_years_and_over(1)_Walked_or_Jogged']
	cmt_total = float(cmt_bicycle + cmt_drove + cmt_publictransport + cmt_walk)
	
	summaryDataByDistrict[district] = {
		'population': population,
		'avg_rent': data['2013_Census_weekly_rent_paid_for_households_in_rented_occupied_private_dwellings(14)_Median_Weekly_Rent_Paid_($)(16)(18)'],
		'mean_age': mean_age,
		'agepct0': (data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_0-4_Years'] + data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_5-9_Years']) / census_night_population,
		'agepct1': (data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_10-14_Years'] + data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_15-19_Years']) / census_night_population,
		'agepct2': (data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_20-24_Years'] + data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_25-29_Years']) / census_night_population,
		'agepct3': (data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_30-34_Years'] + data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_35-39_Years']) / census_night_population,
		'agepct4': (data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_40-44_Years'] + data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_45-49_Years']) / census_night_population,
		'agepct5': (data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_50-54_Years'] + data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_55-59_Years']) / census_night_population,
		'agepct6': (data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_60-64_Years'] + data['2013_Census_age_in_five-year_groups_for_the_census_usually_resident_population_count(1)_65_years_and_Over']) / census_night_population,
		'commute_pct_bike': cmt_bicycle / cmt_total,
		'commute_pct_walk': cmt_walk / cmt_total,
		'commute_pct_publictransport': cmt_publictransport / cmt_total,
		'commute_pct_drive': cmt_drove / cmt_total,
	}
	print(district+' '+repr(summaryDataByDistrict[district]))
	

with open('WhereToLive/censusdata/summarydata.json', 'w') as f:
	json.dump(summaryDataByDistrict, f)

