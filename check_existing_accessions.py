''' 
this is the first part in the development picture. This scans over 
all of the new accession forms and checks if the accession already 
exist in aspace and outputs a csv of 'yes' and 'no''s. These can be
resource records, events, server updates, gifts and general applications.
'''

import json 
import csv
import os 
import functions
import sys
from datetime import date 
import pandas as pd
import find_id1
import shutil

# getting today's year
todays_date = date.today() 
str_year = str(todays_date.year)

''' this is a possible way to turn .xlsx to .csv:
  import  jpype     
  import  asposecells     
  jpype.startJVM() 
  from asposecells.api import Workbook
  workbook = Workbook("input.xlsx")
  workbook.save("Output.csv")
  jpype.shutdownJVM()
'''

# edit line below to manually enter a .csv 
filename = './New Accession Intake Form copy.csv' 
if len(sys.argv) > 1:
    filename = sys.argv[1]
csvOutyes = "./out/accessions_yes.csv"
csvOutno = "./out/accessions_no.csv"

outy = open(csvOutyes, 'w')
outn = open(csvOutno, 'w')
yes_writer = csv.writer(outy)
no_writer = csv.writer(outn)


# columns of first row - right now I'm writing them out manually
usecols = ["ID","Start time","Completion time","Email","Name","Collection name:","New or addition?","Donor or vendor name:","Date of donation/purchase:","Creator (if different from donor):","Estimated creation dates:","Descriptive summary of content:","Estimated physical extent (linear feet):","Estimated digital extent (MB):","Number and type of containers (e.g. 2 record storage boxes):","Legal restrictions or donor restrictions specified in the gift agreement?","Preservation concerns?","Please select gift agreement (or invoice) status:","Optional: attach gift agreement or invoice here","Have the materials been delivered to Knight Library?","Where is the collection currently located? (Room 38, Room 303, mailbox, etc)","Collection identifier (e.g. Coll 100, for additions only):"]
df = pd.read_csv(filename, names=usecols)


# curr id_1 number
id_1 = find_id1.main()
id_1 += 1 

# going through each line of form, if blank then == 'NaN'/'nan'
for index, row in df.iterrows():
    # if first line (column headers)
    if row["ID"] == "ID" and row["Start time"] == "Start time":
        yes_writer.writerow(row)
        no_writer.writerow(row)
        continue

    # copying old .json template to new .json file that we are editing
    shutil.copy('jsontemplate.json', 'newaccession.json')
    
    # getting json Data from template
    jsonData = None
    with open("jsontemplate.json", "r") as file:
        jsonData = json.load(file)
    
    # updating information with info from .csv and id_1 num
    for name in jsonData:  
        if name == "accession_date":
            jsonData[name] = str_year+'-'+str(todays_date.month)+'-'+str(todays_date.day)
        if name == "id_0":
            jsonData[name] = str_year[-2:]
        elif name == "id_1":
            jsonData[name] = id_1
            id_1+=1 # one more accession added
        elif name == "id_2":
            jsonData[name] = "M"
    
    # copying to new .json file
    with open("newaccession.json", "w") as file:
        json.dump(jsonData, file, indent = 4 ) 
    
    break
'''  

    #print(row["Start time"])

    

outy.close()
outn.close()


        # if the row has a collection identifier section
        #if ident_index < len(row):
        #    print(i, row[3], row[ident_index])
    #   store info (in variables) if found type of accession
    #   functions.accessions_exist(stuff, curSession)
    #   if yes:
    #       writer.writerow(stuff)
    #   if no:
    #       writer.writerow(stuff)

# send notification with output.csv to Alexa (through email?)
'''