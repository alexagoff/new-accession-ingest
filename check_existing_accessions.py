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

''' this is a possible way to turn .xlsx to .csv:
  import  jpype     
  import  asposecells     
  jpype.startJVM() 
  from asposecells.api import Workbook
  workbook = Workbook("input.xlsx")
  workbook.save("Output.csv")
  jpype.shutdownJVM()
'''

# new accession numbers -- you actually don't need this!
newid = functions.latest_accession() + 1

# edit line below to manually enter a .csv 
formInFilePath = './shelfread_input_test_data.csv' 
if len(sys.argv) > 1:
    formInFilePath = sys.argv[1]
csvOutyes = "./out/accessions_yes.csv"
csvOutno = "./out/accessions_no.csv"

# open form file
with open(formInFilePath, 'r') as file:
    # output lists
    out_yes = open(csvOutyes, 'w')
    out_no = open(csvOutno, 'w')
    yes_writer = csv.writer(out_yes)
    no_writer = csv.writer(out_no)

    # I need to split this some other way because there are newlines inside of 
    # the data as well as commas. Maybe use pandas?
    data = file.read()
    dataArray = data.split('\n')
    # finding index location of collection identifier in row in .csv
    firstrow = dataArray[0]
    ident_index = firstrow.index("Collection identifier (e.g. Coll 100, for additions only):")

    # parse through form lines, looking for keywords
    for i in range(1, (len(dataArray))):
        row = dataArray[i].split(',')
        
        print(i, row)
        
        # if the row has a collection identifier section
        if ident_index < len(row):
            print(i, row[3], row[ident_index])
    #   store info (in variables) if found type of accession
    #   functions.accessions_exist(stuff, curSession)
    #   if yes:
    #       writer.writerow(stuff)
    #   if no:
    #       writer.writerow(stuff)

# send notification with output.csv to Alexa (through email?)

out_yes.close()
out_no.close()
