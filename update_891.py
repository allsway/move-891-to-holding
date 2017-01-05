#!/usr/bin/python
import requests
import sys
import csv
import configparser
import logging
import collections
import xml.etree.ElementTree as ET

# Returns the API key
def get_key():
	return config.get('Params', 'apikey')

# Returns the Alma API base URL
def get_base_url():
	return config.get('Params', 'baseurl')

def get_periodical_loc():
	return config.get('Params', 'location')
	

"""
	Return holding API url
"""
def get_holding_url(mms_id,holding_id):
	return get_base_url() + "bibs/" + mms_id + '/holdings/' + holding_id + '?apikey=' + get_key()
	
		
"""
	Gets all subfields from the 891 highest indicator, $9 = 853
"""
def get_marc_elements(datafield):
	new_subfields = {}
	indicator = datafield.find('subfield[@code="8"]').text
	for subfields in datafield.findall('subfield'):
		if subfields.attrib['code'] != '9':
			new_subfields[subfields.attrib['code']] = subfields.text
	print (sorted(new_subfields.items()))
	return sorted(new_subfields.items())

"""
	Get the holding data that you will post back to the Alma API
	How do we choose which holding we are going to add the prediction pattern to?
	Options:
		- Just add it to each holding.  
		- Add it based on location (can camupuses provide the location of their active holdings?)
		- Pick the one with an associated order record? Not retrievable through the API
"""
def get_holding(records):
	for holdings in records.findall('./datafield[@tag="852"]'):
		if holdings.find('subfield[@code="c"]').text == get_periodical_loc():
			return holdings.find('subfield[@code="8"]').text
			
			
"""
	Creates the 853 datafield element and appends all subfields from the 891 field to the 853 holding field
"""
def add_853_field(record,new_subfields):
	marc_853 = ET.Element('datafield')
	marc_853.set("tag","853")	
	for key,value in new_subfields:
		sub = ET.SubElement(marc_853,'subfield')
		sub.set('code', key)
		sub.text = value
	record.append(marc_853)


"""
	Gets holding data form the Alma API, calls add_853_field, and posts updated holding with added 853 field
"""
def create_853_field(url,new_subfields):
	response = requests.get(url)
	if response.status_code != 200:
		return None
	print (response.content)
	holding = ET.fromstring(response.content)
	if holding.find('record/datafield[@tag="853"]') is not None:
		logging.info("853 already in holding record: " + url)
		return None
	record = holding.findall('record')[0]
	add_853_field(record,new_subfields)
	headers = {"Content-Type": "application/xml"}
	print (ET.tostring(holding))
	r = requests.put(url,data=ET.tostring(holding),headers=headers)
	print (r.content)
	if r.status_code == 200:
		logging.info('')

	
"""
	Returns the matching datafield for the 891 field that has a highest indicators 
"""
def get_best_891_field(records):
	subfield_val = 0
	max_datafield = None
	for datafield in records.findall('./datafield[@tag="891"]'):
		subfield_9 = datafield.find('subfield[@code="9"]')
		if subfield_9.text == "853":
			# get max $8 field
			if int(datafield.find('subfield[@code="8"]').text) > subfield_val:
				subfield_val = int(datafield.find('subfield[@code="8"]').text)
				max_datafield = datafield
	if max_datafield is not None:
		print (max_datafield.find('subfield[@code="8"]').text)
	return max_datafield
	

"""
	Read in bib record XML export from Alma
"""
def read_bibs(bib_records):
	tree = ET.parse(bib_records)
	for records in tree.findall('record'):
		# Get bib record MMS ID 
		mms_id = records.find('./controlfield[@tag="001"]').text
		print(mms_id)
		rec = get_best_891_field(records)
		if rec is not None:
			new_subfields = get_marc_elements(rec)
			holding_id = get_holding(records)
			url = get_holding_url(mms_id,holding_id)
			create_853_field(url,new_subfields)
		else:
			logging.info('No 891 field found in record: ' + mms_id)
				
				
logging.basicConfig(filename='status.log',level=logging.DEBUG)				
config = configparser.ConfigParser()
config.read(sys.argv[1])

bib_recs = sys.argv[2]
read_bibs(bib_recs)












