
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
import time
from datetime import date 
import datetime
import pandas as pd
import shutil
import re


# edit line below to manually enter a .csv 
filename = './test2.csv' 
if len(sys.argv) > 1:
    filename = sys.argv[1]
csvOutyes = "./out/accessions_yes.csv"
csvOutno = "./out/accessions_no.csv"
err = "./out/new_accessions_logs/errorlog.txt"
app = "./out/new_accessions_logs/applog.txt"

err_true = True
app_true = True
if not os.path.exists(err):
    err_true = False
if not os.path.exists(app):
    app_true = False

errorlog = open(err, "a")
applog = open(app, "a")
outy = open(csvOutyes, 'w')
outn = open(csvOutno, 'w')
yes_writer = csv.writer(outy)
no_writer = csv.writer(outn)

# writing first lines of app and err logs if new
if err_true == False:
    errorlog.write("line #'s and ID #'s are reffering to input csv lines.\n")
if app_true == False:
    applog.write("line #'s and ID #'s are reffering to input csv lines.\n")

# getting today's date
todays_date = date.today() 
str_year = str(todays_date.year)
str_month = str(todays_date.month)
str_day = str(todays_date.day)


def find_inputs():
    ''' this function takes inputs dictating the constraints of what 
    ID's in the input csv will be run.

    Input: none
    output:
        x = the lower constraint x <= lowest ID #
        y = the higher constraint y >= highest ID #
    '''
    x = 0
    y = 0

    print("\nThis program runs any amount of *consecutive* IDs on an inputted 'new accessions' form file.\n\n   ----->  If start = 150 and end = 151, only ID # 150 and 151 will be ran.\n")
    while(1):
        begin = input("\nStart ID: ")
        if not begin.strip().isdigit():
            print("please enter a number containing characters 1-9.")
        else:
            x = int(begin.strip())
            break
        
    while(1):
        endd = input("\nEnd ID: ")
        if not endd.strip().isdigit():
            print("please enter a number containing characters 1-9.")
        elif int(endd.strip()) < int(begin.strip()):
            print("ending ID must be greater or equal to beginning ID.")
        else:
            y = int(endd.strip())
            break
    print("\n\n")

    return x, y


def match_dates(match_string):
    ''' attempts to find begin and end date from "estimated creation date" string.
    Right now it only will detect 4 number years just to make sure mistakes aren't made.
    if theres a year like "19" or "80", it will return 0. 
    
    input: str, the string from the csv column "Estimated creation dates:"
    output: list, a list [start, end] of the starting and ending date in the timeframe. 
            
    Errors: If date could not be found from the patterns, then returns 0.
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


def fill_data(pandas_csv, start_num, end_num, id_1_num):
    ''' this function fills a json file for each line from 
    the input csv. 
    For each json file that has been filled it
    calls post_and_check to attempt to post the data and check if a 
    correlating repository exists. 
    
    Input:
        pandas_csv: file, the input csv
        start_num, end_num: int, the constraints for what ID's to run
        id_1_num: int, the starting id_1 number
    Output: 
        lines_looped: int, the amount of lines in the input csv that were parsed
        run_list: list, the row ID's of the lines in the csv that were parsed
        errors_list: list, the row ID's of lines in the csv that gave 'post' or 'get' errors
    '''
    ex = open("testacc_num.txt", 'r')
    curr_acc = int(ex.read())
    ex.close()

    run_list = []
    errors_list = []
    lines_looped = 0
    extents_message = ""


    # going through each line of csv
    for index, row in pandas_csv.iterrows():
        # checking if start_num < visiting < end_num
        if int(row["ID"]) < start_num:
            continue
        
        elif int(row["ID"]) > end_num:
            continue
        
        run_list.append(int(row["ID"]))
        # copying old .json template to new .json file that we are editing
        #shutil.copy('jsontemplate.json', 'newaccession.json')
        
        # getting jsonData from template .json file
        jsonData = None
        found_dates = "No"

        with open("jsontemplate.json", "r") as file:
            jsonData = json.load(file)
        
        # going through each line of .json file 
        # filling out with info from current line of csv
        for name in jsonData:  

            # commented out because testing with title as "API TEST"
            #if (name == "title") and ((row["Collection name:"]).lower() != "nan"):
            #    jsonData[name] = row["Collection name:"]
            if name == "title":
                jsonData[name] = 'NEW ROUND TEST ACCESIONS ' + str(curr_acc)
                curr_acc+=1
            
            elif name == "content_description":
                if (str(row["Descriptive summary of content:"])).lower() != "nan":
                    jsonData[name] = row["Descriptive summary of content:"]
            
            elif name == "condition_description":
                if (str(row["Preservation concerns?"])).lower() == "yes":
                    jsonData[name] = "Curator indicated presence of preservation concerns."

            elif name == "provenance":
                if (str(row["Donor or vendor name:"])).lower() != "nan":
                    if str(row["Acquisition type?:2"]).lower() != "nan":
                        jsonData[name] = str(row["Acquisition type?:2"]) + " of " + str(row["Donor or vendor name:"]) + ", "+ str(row["Year of donation/purchase:"])[-4:] + "."
                    else:
                        jsonData[name] = "Gift/Purchase/Transfer of " + str(row["Donor or vendor name:"]) + ", "+ str(row["Year of donation/purchase:"])[-4:] + "."

            elif name == "accession_date":
                strdate = str_day
                strmonth = str_month
                if int(str_day) < 10:
                    strdate = "0" + str_day
                if int(str_month) < 10:
                    strmonth = "0" + str_month
                jsonData[name] = str_year+'-'+str_month+'-'+strdate
            
            elif name == "restrictions_apply":
                if (str(row["Legal restrictions or donor restrictions specified in the gift agreement?"])).lower() == "yes":
                    jsonData[name] = True
            
            elif name == "id_0":
                #jsonData[name] = str_year[-2:] commented out for testing files
                jsonData[name] = "25"
            
            elif name == "id_1":
                jsonData[name] = id_1_num
                # increasing id_1
                tmp_id_1 = int(id_1_num) + 1
                if 10 <= tmp_id_1 < 999:
                    id_1_num = "0" + str(tmp_id_1)
                elif tmp_id_1 < 10:
                    id_1_num = "00" + str(tmp_id_1)
            
            elif name == "id_2":
                if row["Curatorial area?"] == "Visual Materials":
                    jsonData[name] = "P"
                elif row["Curatorial area?"] == "Manuscripts":
                    jsonData[name] = "M"
                elif row["Curatorial area?"] == "University Archives":
                    jsonData[name] = "A"
                # default to M
                else:
                    jsonData[name] = "M"
            
            elif name == "general_note":
                jsonData[name] = "Record created by API ingest in "+str_year+"--not yet reviewed for accuracy."

            elif name == "acquisition_type":
                if (str(row["Acquisition type?:2"])).lower() != "nan":
                    jsonData[name] = (str(row["Acquisition type?:2"])).lower()
      
            elif name == "resource_type":
                if (str(row["Resource type?"])).lower() != "nan":
                    jsonData[name] = (str(row["Resource type?"])).lower()
       
            elif name == "extents":
                # if its a physical item 
                if ((str(row["Estimated physical extent (linear feet):"])).lower() != "nan"):
                    # if the string is just a numerical character
                    if str(row["Estimated physical extent (linear feet):"]).replace('.', '', 1).isdigit() == True:
                        if float((row["Estimated physical extent (linear feet):"]).replace('.', '', 1)) != 0:
                            jsonData[name][0]["number"] = str(row["Estimated physical extent (linear feet):"])
                            jsonData[name][0]["extent_type"] = "linear feet"
                            jsonData[name][0]["physical_details"] = row["Number and type of containers (e.g. 2 record storage boxes):"]
                            jsonData[name][0]["portion"] = "whole"
                    # if the string is a valid non-numerical string (something like str(int) + 'linear feet')
                    elif ("linear feet" in str(row["Estimated physical extent (linear feet):"]).lower()) or ("linear foot" in str(row["Estimated physical extent (linear feet):"]).lower()) or (" lf" in str(row["Estimated physical extent (linear feet):"]).lower()) or (" ft" in str(row["Estimated physical extent (linear feet):"]).lower()):
                        patterns = re.findall("\d\d?\,?\d?\d?\d?\.?\d?\d?\d?", str(row["Estimated physical extent (linear feet):"])) 
                        if len(patterns) > 0:
                            if float(patterns[0]) != 0:
                                jsonData[name][0]["number"] = patterns[0]
                                jsonData[name][0]["extent_type"] = "linear feet"
                                jsonData[name][0]["physical_details"] = row["Number and type of containers (e.g. 2 record storage boxes):"]
                                jsonData[name][0]["portion"] = "whole"
                # if its a digital item 
                if (str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])).lower() != "nan": 
                    # if its just a numerical string
                    if str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).replace('.', '', 1).isdigit() == True:
                        if float(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]) != 0:
                            # if its also a valid physical item
                            if jsonData[name][0]["number"] != "":
                                # creating new dict item
                                copy1 = jsonData[name][0].copy()
                                jsonData[name].append(copy1)
                                jsonData[name][1]["number"] = str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])
                                jsonData[name][1]["extent_type"] = "megabyte(s)"
                                # if two types, physical details for both are none
                                jsonData[name][1]["physical_details"] = ""
                                jsonData[name][0]["physical_details"] = ""
                                # making both portions partial
                                jsonData[name][0]["portion"] = "part"
                                jsonData[name][1]["portion"] = "part"
                            # if its only digital
                            else:
                                jsonData[name][0]["number"] = str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])
                                jsonData[name][0]["extent_type"] = "megabyte(s)"
                                jsonData[name][0]["physical_details"] = str(row["Number and type of containers (e.g. 2 record storage boxes):"])
                                jsonData[name][0]["portion"] = "whole"
                    # if its a valid non-numerical string (something like str(int) + "MB")
                    elif (" mb" in str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).lower()) or ("megabytes" in str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).lower()) or ("megabyte" in str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).lower()):
                        patterns = re.findall("\d\d?\,?\d?\d?\d?\.?\d?\d?\d?", str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]))
                        if len(patterns) > 0:
                            if float(patterns[0]) != 0:
                                # if its also a valid physical item
                                if jsonData[name][0]["number"] != "":
                                    # creating new dict item
                                    copy1 = jsonData[name][0].copy()
                                    jsonData[name].append(copy1)
                                    jsonData[name][1]["number"] = str(patterns[0])
                                    jsonData[name][1]["extent_type"] = "megabyte(s)"
                                    # if two types, physical details for both are none
                                    jsonData[name][1]["physical_details"] = ""
                                    jsonData[name][0]["physical_details"] = ""
                                    # making both portions partial
                                    jsonData[name][0]["portion"] = "part"
                                    jsonData[name][1]["portion"] = "part"
                                # if its only digital
                                else:
                                    jsonData[name][0]["number"] = str(patterns[0])
                                    jsonData[name][0]["extent_type"] = "megabyte(s)"
                                    jsonData[name][0]["physical_details"] = str(row["Number and type of containers (e.g. 2 record storage boxes):"])
                                    jsonData[name][0]["portion"] = "whole"

                # if neither could be filled (physical or digital)
                if jsonData[name][0]["number"] == "":
                    extents_message = "Neither Physical or digital extents are valid. Physical: '" + str(row["Estimated physical extent (linear feet):"]) + "', Digital: '" + str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]) + "'"
            
            elif name == "dates":
                jsonData[name][0]["expression"] = str(row["Estimated creation dates:"])
                # making string into estimated begin and end dates
                begin_end = match_dates(str(row["Estimated creation dates:"]))
                if begin_end != 0:
                    found_dates = "Yes"
                    if len(begin_end)==2:
                        jsonData[name][0]["begin"] = begin_end[0]
                        jsonData[name][0]["end"] = begin_end[1]
                        jsonData[name][0]["date_type"] = "inclusive"
                    elif len(begin_end)==1:
                        jsonData[name][0]["begin"] = begin_end[0]
                        jsonData[name][0]["date_type"] = "single"
                # could not separate into start and end dates
                else:
                    jsonData[name][0]["date_type"] = "inclusive"  
                    errorlog.write("ID " + str(row["ID"]) + ": Unable to match date.\n")
        
        # copying to new .json file - not necessary, just post it onto aspace. 
        with open("newaccession.json", "w") as file:
            json.dump(jsonData, file, indent = 4 ) 

        # checking if it won't be able to post because of 'extents'field
        if extents_message != "":
            errorlog.write("ID " + str(row["ID"]) + ": " + extents_message + "\n")
        errors_list, id_1_num = post_and_check(jsonData, row, found_dates, errors_list, int(id_1_num))
        
        # making id_1 a str again
        tmp_id_1 = id_1_num
        if 10 <= tmp_id_1 < 999:
            id_1_num = "0" + str(tmp_id_1)
        elif tmp_id_1 < 10:
            id_1_num = "00" + str(tmp_id_1)
        
        time.sleep(1)
        extents_message = ""
        lines_looped +=1
        
    # *TEST* writing the number of tests already done in testacc_num.txt
    f = open('testacc_num.txt', 'w')
    f.seek(0)
    f.write(str(curr_acc))
    f.truncate()
    f.close()

    return lines_looped, run_list, errors_list


def post_and_check(tmpjson, curr_row, found_tf, curr_errors, curr_id):
    ''' this function posts a jsonData variable of an accession into Aspace and checks if the
    repository connected to the accession exists. This function also writes to the 
    output "yes" and "no" csv's as well as the output logs. 

    Input:
        tmpjson: Dict/json(?), jsonData (contents of a .json file)
        curr_row: Sequence, the current row contents from the input csv
        found_tf: str, "Yes" or "No" whether a date was found from the input date string
        curr_errors: list, a list of ID's of the row's with errors.
        curr_id: int, the current id_1 number.
    Output:
        curr_errors: list, updated curr_errors
        curr_id: int, updated id_1 number (if there was issues posting, subtract 1)
    '''
    # post jsonData to Aspace
    returned_out = functions.jsonpost(tmpjson)

    # couldn't post
    if "error" in returned_out:
        curr_id-=1
        curr_errors.append(curr_row["ID"])
        #curr_acc -= 1 # can get rid of this after testing
        errorlog.write("ID " + str(curr_row["ID"]) + ": Unable to post. Error message below:\n")
        errorlog.write("\t\t" + str(returned_out) + "\n")
    # posted successfully
    else:
        accession_uri = returned_out['uri']
        applog.write("ID " + str(curr_row["ID"]) + ": Posted new accession with URI " + str(accession_uri) + ".\n")

        # checking if repository relating to accession exists
        repo_true = functions.repo_exists(curr_row["Collection name:"], curr_row["Collection identifier (e.g. Coll 100, for accruals only):"])

        # right now I have it so that the only time it doesn't write to the output csv's is if there is an 
        # error using the "get" method. 

        # if there was no error in "get" API
        if repo_true != -1:
            tmprow = curr_row.tolist()
            tmprow.append(found_tf)
            tmprow.append(str(accession_uri))

            # if repo was able to search 
            if type(repo_true) == tuple:
                # if > 0 found:
                if len(repo_true) == 5:
                    colltitle, collident, colluri, totalhits, foundissues = repo_true
                    tmprow.append(str(totalhits))
                    tmprow.append(str(colltitle))
                    tmprow.append(str(collident))
                    tmprow.append(str(colluri))
                    yes_writer.writerow(tmprow)
                # if totalhits == 0
                elif len(repo_true) == 2:
                    totalhits, foundissues = repo_true
                    tmprow.append(str(totalhits))
                    no_writer.writerow(tmprow)
                # if errors in coll name or coll id
                if foundissues == True:
                    errorlog.write("ID " + str(curr_row["ID"]) + ": Repo searched with only collection name. Error in collection identifier.\n")

            # if error in coll name or coll id and couldn't search repo
            else:
                errorlog.write("ID " + str(curr_row["ID"]) + ": Unable to search for a repo. Insufficient information (collection name or identifier).\n")
                tmprow.append("0")
                no_writer.writerow(tmprow)

        # if using "get" failed (system error)
        else:
            curr_errors.append(curr_row["ID"])
            errorlog.write("ID " + str(curr_row["ID"]) + ": Error in trying to use 'get' to find repo. Error message below:\n")
            errorlog.write("\t\t" + str(repo_true) + "\n")

    return curr_errors, curr_id

# work on "yes" on the second section if done with this..
# for the event record, do Executing program and SCUA api calls as the other one -->"role":"executing_program", "linked_records":"ref":*resource uri*

def main():
    ''' Program to go through lines of an input csv of new acceession forms 
    and create a json file for each line, then posting a new accession to aspace
    from each file and checking if corresponding repositories exist. 

    Errors: exit with failure if id_1 number can't be found.  
    '''
    # input loop for asking user what ID they would like to start and end on. 
    retstartend = find_inputs()
    start, end = retstartend

    df = pd.read_csv(filename)

    # writing new column headers to output csv's
    data_top = list(df.head())
    data_top.append("Found Dates? (extracted from estimated creation dates)") # if begin and end could be extracted from "Estimated creation dates:"
    data_top.append("Created Accession URI:")
    data_top.append("Number of found results:") # if repo for accession exists n>0
    data_top.append("Found Collection Title:") # the title of existing collection of first match 
    data_top.append("Found Collection Identifier:") # if repo exists
    data_top.append("Found Collection URI (of first match):") # if repo exists
    yes_writer.writerow(data_top)
    no_writer.writerow(data_top)

    now = datetime.datetime.now()
    errorlog.write("\n--------------" + str(now) + "--------------\n")
    applog.write("\n--------------" + str(now) + "--------------\n")

    # finding id_1 number -- newest ID_1 in 2023 is supposed to be 84 (running testing will messs this up.)
    id_1 = functions.latest_id1("2025") # supposed to be (str_year) as parameter but testing with something else.
    
    # if you would like to manually enter id_1 write the string here:
    # id_1 = "030" 

    tmp = ""
    # an error in 'get' API is the only time latest_id1 returns a tuple type
    if type(id_1) == tuple:
        tmp = id_1
        id_1 = id_1[0]
    # if finding id didn't work
    if id_1 == -1 or id_1 == -2: 
        print("Error finding id_1 from last five accessions. Can not run--check errorlog.txt\n")
        if id_1 == -1:
            errorlog.write("Error finding id_1 from last five accessions. The last five id_1's from this year were not in consecutive order.\n")
        if id_1 == -2:
            errorlog.write("Error finding id_1 from last five accessions. Using 'get' method failed. Error message below:\t\t" + str(tmp[1]) + "\n")
        exit(1)

    final_returns = fill_data(df, start, end, id_1)
    lines_looped, run_list, errorlis = final_returns

    if lines_looped == 0:
        print("\nUnable to run! start and end ID number might not be valid.\n")
    else:
        run_list.sort()
        if len(errorlis) != 0:
            print("\nRan program successfully!\n\tLook for more information on this run in accessions_no.csv, accessions_yes.csv, errorlog.txt and applog.txt.\n\n\tRAN ID's:", run_list, "\n\tERROR ID's (not on output csv's):", errorlis, "\n")
        else:
            print("\nRan program successfully!\n\tLook for more information on this run in accessions_no.csv, accessions_yes.csv, errorlog.txt and applog.txt.\n\n\tRAN ID's:", run_list, "\n\tNo errors in posting or getting.\n")
    
    return 0


# running main without calling it
if __name__ == "__main__":
    main()
    outy.close()
    outn.close()
    errorlog.close()
    applog.close()
