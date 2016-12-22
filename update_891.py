#!/usr/bin/python
import requests
import sys
import csv
import configparser
import logging
import xml.etree.ElementTree as ET

# Returns the API key
def get_key():
	return config.get('Params', 'apikey')

# Returns the Alma API base URL
def get_base_url():
	return config.get('Params', 'baseurl')
	

"""
	Return holding API url
"""
def get_holding_url(mms_id,holding_id):
	return get_base_url() + "bibs/" + mms_id + '/holdings/' + holding_id + '?apikey=' + get_key()


"""
	Return element with the max indicator 
"""
def get_max_ind(element,ind):
	indicators = []
	for marc_891 in element:
		for subfield in marc_891.findall('subfield[@code="9"]'):
			if subfield.text == "853":
				indicators.append(marc_891.attrib[ind])
	return max(indicators)
	
		
"""
	Gets all subfields from the 891 highest indicator, $9 = 853
"""
def get_marc_elements(rec):
	new_subfields = {}
	indicator = rec.find('subfield[@code="8"]').text
	subfields = ['8', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','t','u','v','w','x','y','z']
	for subfield in subfields:
		search_string = 'subfield[@code="' + subfield + '"]'
		if rec.find(search_string) is not None:
			new_subfields[subfield] = rec.find(search_string).text
	print (new_subfields)
	return new_subfields

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
		if holdings.find('subfield[@code="c"]').text == 'pru':
			print (holdings.find('subfield[@code="8"]').text)
			return holdings.find('subfield[@code="8"]').text
			
			
"""
	Creates the 853 datafield element and appends all subfields from the 891 field to the 853 holding field
"""
def add_853_field(record,new_subfields):
	marc_853 = ET.Element('datafield')
	marc_853.set("tag","853")	
	for key,value in new_subfields.items():
		sub = ET.SubElement(marc_853,'subfield')
		sub.set('code', key)
		sub.text = value
	record.append(marc_853)


"""

"""
def create_853_field(url,new_subfields):
	# make call to alma API
	response = requests.get(url)
	if response.status_code != 200:
		return None
	print (response.content)
	holding = ET.fromstring(response.content)
	if holding.find('record/datafield[@tag="853"]') is not None:
		print ("853 already in holding record")
		return None
	record = holding.findall('record')[0]
	add_853_field(record,new_subfields)
	print (ET.tostring(holding))
	
	
"""
	Returns the marching datafield for the 891 field that has a highest indicators 
"""
def get_best_891_field(records):
	marc_891s = records.findall('./datafield[@tag="891"]')
	max_indicator_1 = get_max_ind(marc_891s,'ind1')
	max_indicator_2 = get_max_ind(records.findall('./datafield[@tag="891"][@ind1="' + max_indicator_1 + '"]'),'ind2')
	print (max_indicator_2)
	for subfield in records.findall('./datafield[@tag="891"]/subfield[@code="9"]'):
		if subfield.text == "853":
			rec = records.find('./datafield[@tag="891"][@ind1="' + max_indicator_1 + '"][@ind2="' + max_indicator_2 + '"]')
		return rec
	

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
		new_subfields = get_marc_elements(rec)
		holding_id = get_holding(records)
		url = get_holding_url(mms_id,holding_id)
		create_853_field(url,new_subfields)
				
				
config = configparser.ConfigParser()
config.read(sys.argv[1])

bib_recs = sys.argv[2]
read_bibs(bib_recs)












