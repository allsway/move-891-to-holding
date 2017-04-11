# move-891-to-holding
For a set of bib records created in Alma, this moves the bib record 891 MARC field contents to the holding record 853 prediction pattern field in Alma.  

#### config.txt
A configuration file that stores your API key, base API URL and yout location mapping file. 
```
[Params]
apikey: apikey 
baseurl: host
location: default_location
```

#### update_891.py
Takes as arguments:
- the configuration file with the settings listed above
- an XML file of bib records that are associated with holdings that require prediction patterns.  This is the default Alma export bib records in XML format file.  

Creates:
- Updated holding records, with the addition of an 853 prediction pattern field for any holding in the location {default_location} that doesn't already contain an 853 field.  

Run as `python ./update_891.py {config.txt} {bib_records.xml}`

#### Example
A bib record has the following 891 fields:
```
891	20 |9 853 |8 1 |a v. |b no. |u 10 |v r |i (year) |j (month) |w 10 |x 01/02
891	41 |9 863 |8 1.1 |a 22 |b 1 |i 2003 |j 01/02
891	20 |9 853 |8 2 |a v. |b no. |u 9 |v r |i (year) |j (month) |w m |x 01/02 |y cm01/02,05/06,09/10
891	41 |9 863 |8 2.1 |a 24 |b 1 |i 2005 |j 01/02
891	20 |9 853 |8 3 |a v. |b no. |u 8 |v r |i (year) |j (month) |w m |x 01/02 |y cm01/02,03/04,06/07,11/12
891	41 |9 863 |8 3 |a 31-34 |b 1-8 |i 2012-2015 |j 01/02-11/12
891	20 |9 853 |8 4 |a v. |b no. |u 7 |v r |i (year) |j (month) |w m |x 01/02 |y cm01/02,03/04,06/07,08/09,11/12
891	41 |9 863 |8 4 |a 35 |b 1 |i 2016 |j 01/02
 ```
 This script will select
 - The 891 field with a corresponding 853 field
 - Of the 891 $9 853 fields, it will select the 891 field with the highest $8.  
 
 The result:
  `891	20 |9 853 |8 4 |a v. |b no. |u 7 |v r |i (year) |j (month) |w m |x 01/02 |y cm01/02,03/04,06/07,08/09,11/12` will be added to your holding record at location `location`. 
