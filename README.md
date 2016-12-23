# move-891-to-holding
For a set of bib records created in Alma, this moves the bib record 891 MARC field contents to the holding record 853 prediction pattern field in Alma.  

####config.txt
A configuration file that stores your API key, base API URL and yout location mapping file. 
```
[Params]
apikey: apikey 
baseurl: host
location: default_location
```

####update-891.py
Takes as arguments:
- the configuration file with the settings listed above
- an XML file of bib records that are associated with holdings that require prediction patterns.  This is the default Alma export bib records in XML format file.  

Creates:
- Updated holding records, with the addition of an 853 prediction pattern field for any holding in the location {default_location} that doesn't already contain an 853 field.  

Run as `python ./update_891.py {config.txt} {bib_records.xml}`
