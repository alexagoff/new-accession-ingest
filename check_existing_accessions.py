''' 
this is the first part in the development picture. This scans over 
all of the new accession forms and checks if the accession already 
exist in aspace and outputs a csv of 'yes' and 'no''s. These can be
resource records, events, server updates, gifts and general applications.

DONT_EDIT.txt holds the ID (not the line in the csv) of the last accession from "New Accession Intake Form.csv" that was created.
you don't need to interact with this file, unless you want to update the last ID that was run (if you did one manually, etc). 
(if DONT_EDIT.txt = 160, it will run ID's: 161, 162, 163, ...)
'''

''' this is a possible way to turn .xlsx to .csv:
  import  jpype     
  import  asposecells     
  jpype.startJVM() 
  from asposecells.api import Workbook
  workbook = Workbook("input.xlsx")
  workbook.save("Output.csv")
  jpype.shutdownJVM()
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



# getting today's date
todays_date = date.today() 
str_year = str(todays_date.year)
str_month = str(todays_date.month)
str_day = str(todays_date.day)

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



def match_dates(match_string):
    ''' attempts to find begin and end date from "estimated creation date" string.
    Right now it only will detect 4 number years just to make sure mistakes aren't made.
    if theres a year like "19" or "80", it will return 0. 
    
    input: the string from the csv column "Estimated creation dates:"
    output: If successfully removed, then return a list [start, end]. 
            If date could not be found from the patterns, then returns 0.
    '''
    # regex patterns 
    pattern1 = "\d{4}'?\s?s.*\d{4}'?\s?s" 
    pattern2 = "\d{4}'?\s?s.*\d{4}"
    pattern3 = "\d{4}.*\d{4}'?\s?s"
    pattern4 = "\d{4}.*\d{4}"
    pattern5 = "\d{1,2}\s?\-\-?\s?[a-zA-Z]+\s?\-\-?\s?\d{4}"
    pattern6 = "[a-zA-Z]+\s?\-+\s?\d{4}"
    pattern7 = "\d{4}'?\s?s"
    pattern8 = "\d{4}"

    # if adding new patterns, the ORDER of these patterns is important! it goes from 
    # largest match to smallest (largest being like 2000s-3000s and smallest being just a four digit number)
    patterns_list = [pattern1, pattern2, pattern3, pattern4,
                        pattern5, pattern6, pattern7, pattern8]
    
    months_list = ["january", "february", "march", "april", "may", "june", "july",
                        "august", "september", "october", "november", "december", "jan", 
                        "feb", "mar", "apr", "jun", "jul", "aug", "sept", "sep", "oct", "nov", "dec"]

    found = False
    for pattern in patterns_list:
        find_list = re.findall(pattern, match_string)
        if len(find_list)>0:
            found = True
            # XXXXs-XXXXs or XXXX-XXXXs
            if (pattern == pattern1) or (pattern == pattern3):
                new_list = re.findall(pattern8, find_list[0])
                # if its "2020s"
                if new_list[-1][:3] == str_year[:3]:
                    return [new_list[0], str_year] 
                return [new_list[0], new_list[-1][:3]+'9'] 
            # XXXXs-XXXX or XXXX-XXXX
            elif (pattern == pattern2) or (pattern == pattern4):
                return [str(find_list[0])[:4], str(find_list[0])[-4:]]
            # form 8-Nov-2019 or Nov-2019
            elif (pattern == pattern5) or (pattern == pattern6):
                test_month = re.findall("[a-zA-Z]+", find_list[0])
                # if the first letters aren't a month
                if test_month[0].lower() not in months_list:
                    return 0
                return [str(find_list[0])[-4:]]
            # XXXXs
            elif pattern == pattern7:
                new_year = re.findall("\d{4}", str(find_list[0]))
                if new_year[0][:3] == str_year[:3]:
                    return [new_year[0][:3], str_year] 
                return [new_year[0][:3]+'0', new_year[0][:3]+'9']
            # XXXX
            elif pattern == pattern8:
                return [find_list[0]]
    
    # if match_string didn't match any of the patterns
    if found == False:
        return 0
    
# make a log after running this that writes the errors and created accessions (like first project)
# make another column for the # of results found for looking up item

def main():
    ''' main loop going through lines of new form input CSV. Creates new .json file
    for every new accession form, fills it with information and then posts it onto 
    Aspace. 
    '''
    #usecols = ["ID","Start time","Completion time","Email","Name","Collection name:","New or addition?","Donor or vendor name:","Date of donation/purchase:","Creator (if different from donor):","Estimated creation dates:","Descriptive summary of content:","Estimated physical extent (linear feet):","Estimated digital extent (MB):","Number and type of containers (e.g. 2 record storage boxes):","Legal restrictions or donor restrictions specified in the gift agreement?","Preservation concerns?","Please select gift agreement (or invoice) status:","Optional: attach gift agreement or invoice here","Have the materials been delivered to Knight Library?","Where is the collection currently located? (Room 38, Room 303, mailbox, etc)","Collection identifier (e.g. Coll 100, for additions only):"]
    df = pd.read_csv(filename)
    print(df)

    # writing new column headers to output csv's
    data_top = list(df.head())
    data_top.append("Found Dates? (extracted from estimated creation dates)") # if begin and end could be extracted from "Estimated creation dates:"
    data_top.append("Number of found results (if collection exists):") # if repo for accession exists n>0
    data_top.append("Found Collection Title:") # the title of existing collection of first match 
    data_top.append("Found Collection Identifier:") # if repo exists
    data_top.append("Found Collection URI (of first match):") # if repo exists
    data_top.append("Created Accession URI:")
    yes_writer.writerow(data_top)
    no_writer.writerow(data_top)

    # curr id_1 number
    id_1 = find_id1.main()
    id_1 += 1 

    ex = open("example.txt", "w")
    ex2 = open("exampleans.txt", "w")
    # going through each line of form, if blank then == 'NaN'/'nan'
    for index, row in df.iterrows():
        # if this ID has already been visited--ignore
        if int(row["ID"]) < curr_num:
            continue
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
                jsonData[name] = str_year+'-'+str_month+'-'+str_day
            if name == "id_0":
                jsonData[name] = str_year[-2:]
            elif name == "id_1":
                jsonData[name] = id_1
                id_1+=1 # one more accession added
            elif name == "id_2":
                jsonData[name] = "M"
            # publish is always FALSE
            elif name == "content_description":
                if (row["Descriptive summary of content:"]).lower() != "nan":
                    jsonData[name] = row["Descriptive summary of content:"]
            elif name == "condition_description":
                # EDIT: with what alexa says on teams
                if (row["Preservation concerns?"]).lower() == "yes":
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
                # making string into estimated begin and end dates
                begin, end = None
                begin_end = match_dates(row["Estimated creation dates:"])
                if begin_end != 0:
                    if len(begin_end)==2:
                        begin = begin_end[0]
                        end = begin_end[1]
                    elif len(begin_end)==1:
                        begin = begin_end[0]
                # could not separate into start and end dates
                else:
                    pass
                
                # date_type -- "inclusive" , unless theres only a begin date its "single" (if theres only one date its begin type)
                   

            # if extents, if estimated pysical extent in csv is filled out then "number" = estimated physical...  then do extent_type "linear feet" then get number and type of contaniers and make physical_details in .json = number and type , if its estimated digital extent then "number" = estimated digital and "extend_type" = "megabyte(s)" and populate physical details too with number and type if only digital is filled out but if both are filled out then physical details is blank:: if there were physical and digital then make two objects (dictionaries) in the "extents" list and make "portion" = "partial"
            # if collection management, then processing status = "Unprocessed"
            # make the test title "TEST FILE ACCESSION FROM API"

        # copying to new .json file - just post it onto aspace. 
        with open("newaccession.json", "w") as file:
            json.dump(jsonData, file, indent = 4 ) 
        
        # after posting, check if resource exists by:
            # collection identifier key in csv. If its populated check it. do regex to remove any () after. ONly pull something like "Col 188"
            # collection name: search this up too. 
            # if collection identifier and colletion name are both filled out combine the two " name + identifier "
            # 'repositories/2/search?q=' + str(x) + "&page=1&type[]=resource" --- str(x) is either of the things above
            
            # when searching the resource record:
                # total_hits is number of results ( if == 0 then don't fill out bottom 3 )
                # Collection Title: is results[0][title]
                # Colleciton identifier: is results[0][identifier]
                # Collection URI: is results[0][uri]

        # make id_0 = 2025 for testing
        # make id_1 = 001 for testing (but it will end up being 001 with my code anyways)
        # new CSV columns::: curatorial area: if Manuscripts id_2 = M , Visual Materials = P, University Archives = A; "resource type": resource_type = lowercase resoure type; Aquisition type: aquisition_type = lowercase aquisition type (change the values in the CSV to make sure Gift, Purchase and Transfer work)
        break
        '''
    return 0

    # check if already posted onto Aspace()
        

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

# running main without calling it
if __name__ == "__main__":
    main()
    outy.close()
    outn.close()
