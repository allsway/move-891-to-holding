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

# Returns the location that is used for periodicals - only holdings in this location will receive the 891 field.
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
    # subfield8 = datafield.find('subfield[@code="8"]').text
    for subfields in datafield.findall('subfield'):
        if subfields.attrib['code'] != '9':
            new_subfields[subfields.attrib['code']] = subfields.text
    print (new_subfields)
    return new_subfields

"""
    Get the holding data that you will post back to the Alma API
    How do we choose which holding we are going to add the prediction pattern to?
    Options:
        - Just add it to each holding.
        - Add it based on location (can camupuses provide the location of their active holdings?)
"""
def get_holding(holding):
    print(holding.find('subfield[@code="c"]').text)
    print("Periodical loc:" +  get_periodical_loc())
    #locations = get_periodical_loc().split(",")
    #for location in locations:
    #    if holdings.find('subfield[@code="c"]').text == location:
    print ("equal")
    return holding.find('subfield[@code="8"]').text


#Creates the 853 datafield element and appends all subfields from the 891 field to the 853 holding field
def add_853_field(record,new_subfields,prior):
    marc_853 = ET.Element('datafield')
    marc_853.set("tag","853")
    for key,value in new_subfields:
        sub = ET.SubElement(marc_853,'subfield')
        sub.set('code', key)
        sub.text = value
    record.insert(prior,marc_853)
    return record


"""
    Gets the current max $8 of the 853 fields in the *holding* record, so that new 853$8 can be incremented by 1.
"""
def return_max_subfield8(holding):
    subfield_8s = []
    for marc_853 in holding.findall('record/datafield[@tag="853"]'):
        for subfield in marc_853.findall('subfield[@code="8"]'):
            subfield_8s.append(subfield.text)
    return max(subfield_8s)

# <datafield ind1=" " ind2=" " tag="035">
# Return the element that should go right before our inserted 853 field
def find_prior_element(record):
    temp = 0
    for tag in record.findall('datafield'):
        if tag.attrib['tag'] <= '853':
            temp = tag.attrib['tag']
    # gets the element that should preceed our new 853 field
    prior_element = record.find('datafield[@tag="' + temp + '"]')
    # returns index of element right before 853 field
    return record.getchildren().index(prior_element) + 1


# Making holding put request with 853 from the bib record
def put_holding(url,holding):
    headers = {"Content-Type": "application/xml"}
#    print (ET.tostring(holding))
    r = requests.put(url,data=ET.tostring(holding),headers=headers)
    print ('Posted holding results: ')
    print (r.content)
    if r.status_code == 200:
        logging.info('Successfully added 853 to ' + url)
    else:
        logging.info('Failed to add 853 to ' + url)

#Gets holding data form the Alma API, calls add_853_field, and posts updated holding with added 853 field
def create_853_field(url,new_subfields):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    holding = ET.fromstring(response.content)
    if holding.find('record/datafield[@tag="853"]') is not None:
        logging.info("853 in holding record: " + url)
        max_subfield8 = return_max_subfield8(holding)
        new_subfields['8'] = str(float(max_subfield8.strip('"')) + 1)
    else:
        new_subfields['8'] = '1'
    new_subfields = sorted(new_subfields.items())
#    print (new_subfields)
    record = holding.findall('record')[0]
    prior = find_prior_element(record)
    record = add_853_field(record,new_subfields,prior)
    print (ET.tostring(record))
#    print (record.findall('datafield'))
    put_holding(url,holding)


# Returns the matching datafield for the 891 field that has a highest $8
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

# Read in bib record XML export from Alma
def read_bibs(bib_records):
    tree = ET.parse(bib_records)
    for records in tree.findall('record'):
        # Get bib record MMS ID
        mms_id = records.find('./controlfield[@tag="001"]').text
        print(mms_id)
        # MARC records will have multiple 891 fields.  Select the correct one:
        rec = get_best_891_field(records)
        # Provided that there is an 891 field in the bib record in the first place:
        if rec is not None:
            # get data from 891
            new_subfields = get_marc_elements(rec)
            # get the correct holding to add the 891 data to
            # for each holding
            for holding in records.findall('./datafield[@tag="852"]'):
                holding_id = get_holding(holding)
                print (holding_id)
                if holding_id is not None:
                    url = get_holding_url(mms_id,holding_id)
                    # add the 853 field to the holing, with the 891 subfields
                    create_853_field(url,new_subfields)
                else:
                    logging.info('No holding found in record: ' +  mms_id)
        else:
            logging.info('No 891 field found in record: ' + mms_id)


logging.basicConfig(filename='status.log',level=logging.DEBUG)
config = configparser.ConfigParser()
config.read(sys.argv[1])

bib_recs = sys.argv[2]
read_bibs(bib_recs)
