''' 
this is the first part in the development picture. This scans over 
all of the new accession forms and checks if the accession already 
exist in aspace and outputs a csv of 'yes' and 'no''s. These can be
resource records, events, server updates, gifts and general applications.

DONT_EDIT.txt holds the ID (not the line in the csv) of the last accession from "New Accession Intake Form.csv" that was created.
you don't need to interact with this file, unless you want to update the last ID that was run (if you did one manually, etc). 
The code will only run lines below the number in DONT_EDIT.txt so be careful what you input!
(if DONT_EDIT.txt = 160, it will run ID's: 161, 162, 163, ...)
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
import re

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

# the current accession # from file we're on
curr_n = open("DONT_EDIT.txt", 'r') # change value in DONT_EDIT.txt !!
curr_num = int(curr_n.read())
curr_num+=1

# columns of first row - right now I'm writing them out manually
usecols = ["ID","Start time","Completion time","Email","Name","Collection name:","New or addition?","Donor or vendor name:","Date of donation/purchase:","Creator (if different from donor):","Estimated creation dates:","Descriptive summary of content:","Estimated physical extent (linear feet):","Estimated digital extent (MB):","Number and type of containers (e.g. 2 record storage boxes):","Legal restrictions or donor restrictions specified in the gift agreement?","Preservation concerns?","Please select gift agreement (or invoice) status:","Optional: attach gift agreement or invoice here","Have the materials been delivered to Knight Library?","Where is the collection currently located? (Room 38, Room 303, mailbox, etc)","Collection identifier (e.g. Coll 100, for additions only):"]
df = pd.read_csv(filename, names=usecols, skiprows=range(1,curr_num))
print(df)


# curr id_1 number
id_1 = find_id1.main()
id_1 += 1 
ex = open("example.txt", "w")
ex2 = open("exampleans.txt", "w")

# going through each line of form, if blank then == 'NaN'/'nan'
for index, row in df.iterrows():
    # if first line (column headers)
    if row["ID"] == "ID" and row["Start time"] == "Start time":
        yes_writer.writerow(row)
        no_writer.writerow(row)
        continue
    poop = str(row["Estimated creation dates:"])
    ex.write(str(poop))
    ex.write("\n")

    space_len = 30 - len(str(poop))
    pattern4 = "\d{2,4}'?\s?s\s?\-\s?\d{2,4}'?\s?s" 
    pattern = "\d{2,4}'?s\s?\-+\s?\d{2,4}"
    pattern1 = "\d{2,4}\s?\-+\s?\d{2,4}'?s"
    pattern2 = "\d{2,4}\s?\-+\s?\d{2,4}"
    pattern8 = "(\d{2}\s?\-?\s?(th|TH|Th)\s?\-?\s?(century|Century|CENTURY))"
    pattern3 = "\d{1,2}\-[a-zA-Z]+\-\d{2,4}"
    pattern5 = "[a-zA-Z]+\-+\d{2,4}"
    pattern6 = "\d{4}'?s"
    pattern7 = "\d{4}"

    if re.findall(pattern8, poop):
        print(str(((re.findall(pattern8, poop))[0])[0]))
    # in format like '2020s-2023s' or '2020's-20203's' or '90 s-80 s'
    if len(re.findall(pattern4, poop))>0:
        ex2.write(poop+space_len*' '+str(re.findall(pattern4, poop)))
        ex2.write("\n")
    # in format somewhat '2019s-2023' or '2019's-2023'
    elif len(re.findall(pattern, poop))>0: 
        ex2.write(poop+space_len*' '+str(re.findall(pattern, poop)))
        ex2.write("\n")
    # in format somewhat 2019-2023s' or '2019-2023's'
    elif len(re.findall(pattern1, poop))>0: 
        ex2.write(poop+space_len*' '+str(re.findall(pattern1, poop)))
        ex2.write("\n")
    # in format somewhat '2019-2023'
    elif len(re.findall(pattern2, poop))>0: 
        ex2.write(poop+space_len*' '+str(re.findall(pattern2, poop)))
        ex2.write("\n")
    # in format like "19th Century" or "19th-century"
    elif len(re.findall(pattern8, poop))>0:
        ex2.write(poop+space_len*' '+str(((re.findall(pattern8, poop))[0])[0]))
        ex2.write("\n")
    # in format somewhat '5-feb-22' or '5-feb-2022'
    elif len(re.findall(pattern3, poop))>0:
        ex2.write(poop+space_len*' '+str(re.findall(pattern3, poop)))
        ex2.write("\n")
    # in format like 'feb-96' or 'feb-1996
    elif len(re.findall(pattern5, poop))>0:
        ex2.write(poop+space_len*' '+str(re.findall(pattern5, poop)))
        ex2.write("\n")
    # in format like '2010s' or '2010's'
    elif len(re.findall(pattern6, poop))>0:
        ex2.write(poop+space_len*' '+str(re.findall(pattern6, poop)))
        ex2.write("\n")
    # in format like "2010"
    elif len(re.findall(pattern7, poop))>0:
        ex2.write(poop+space_len*' '+str(re.findall(pattern7, poop)))
        ex2.write("\n")
    # if its a just a word or nothing
    else:
        ex2.write(poop)
        ex2.write("\n")
    '''
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
        # publish yes/no
        elif name == "content_description":
            if (row["Descriptive summary of content:"]).lower() != "nan":
                jsonData[name] = row["Descriptive summary of content:"]
        elif name == "condition_description":
            # EDIT: with what alexa says 
            if (row["Legal restrictions or donor restrictions specified in the gift agreement?"]).lower() == "yes":
                jsonData[name] = "Alexa's note on yes conditions"
            else:
                jsonData[name] = ""
        elif name == "provenance":
            if (row["Donor or vendor name:"]).lower() != "nan":
                jsonData[name] = "Gift/purchase of " + row["Donor or vendor name:"] + ", "+ row["Date of donation/purchase:"][-4:] + "."
        # is this and the condition_description the same
        elif name == "restrictions_apply":
            if row["Legal restrictions or donor restrictions specified in the gift agreement?"]).lower() == "yes":
                jsonData[name] = "yes"
        elif name == "dates":
            jsonData[name]["expression"] = row["Estimated creation dates:"]
            # making string into estimated start and end dates
            tmpdate = row["Estimated creation dates:"]


            # add another definition for start date and end dates     

    
    # copying to new .json file
    with open("newaccession.json", "w") as file:
        json.dump(jsonData, file, indent = 4 ) 
    
    break
    '''

outy.close()
outn.close()

'''

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
