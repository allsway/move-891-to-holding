#!/usr/bin/python
import requests
import sys
import csv
import ConfigParser
import logging
import xml.etree.ElementTree as ET

# Returns the API key
def get_key():
	return config.get('Params', 'apikey')

# Returns the Alma API base URL
def get_base_url():
	return config.get('Params', 'baseurl')

# Returns the location mapping file, taken from the Alma Migration Form
def get_location_mapping():
	return config.get('Params', 'locations')
	


"""
	Read in bib record XML export from Alma
"""
def read_bibs(bib_records):
	bibs = ET.parse(bib_records)
	print bibs


#config = ConfigParser.RawConfigParser()
#config.read(sys.argv[1])

bib_recs = sys.argv[1]
read_bibs(bib_recs)










