##############################################
# new_accessions.py                          #
# running specific ranges of ID's            #
#                                            #
# This file goes through new accessions and  #
# posts them onto Aspace as well as checking #
# if these accessions have related resources #
# on Aspace already.                         #
# output is out/posted_accessions.py         #
#                                            #
##############################################

import json 
import csv
import os 
import functions
import sys
import time
from datetime import date 
import datetime
import pandas as pd
import re

# CODE EVOLUTION: send output to alexa via email 

# edit line below to manually enter a .csv 
filename = '' 
if len(sys.argv) > 1:
    filename = sys.argv[1]
csvOut = "./out/posted_accessions.csv"
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
outy = open(csvOut, 'w', encoding="utf-8")
csv_writer = csv.writer(outy)

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
        run_list: list, the row ID's of the lines in the csv that had successful posts and gets
        errors_list: list, the row ID's of lines in the csv that gave 'post' or 'get' errors
        err_lis: list, the row ID's of the lines in the csv that had successful posts and gets but with errors
    '''
    run_list = [] # successful runs
    err_lis = [] # errors in successful runs
    errors_list = [] # error runs
    lines_looped = 0 # the amount of lines looped
    extents_message = ""

    # going through each line of csv
    for _, row in pandas_csv.iterrows():
        # checking if start_num < visiting < end_num
        if int(row["ID"]) < start_num:
            continue
        
        elif int(row["ID"]) > end_num:
            continue
        
        # getting jsonData from template .json file
        jsonData = None
        title_name = '' # stores title name 

        with open("./extra_materials/jsontemplate.json", "r") as file:
            jsonData = json.load(file)
        
        # going through each line of .json file 
        # filling out with info from current line of csv
        for name in jsonData:  
            # TESTING PURPOSES
            '''
            if name == "title":
                jsonData[name] = 'NEW ROUND TEST ACCESIONS'
                title_name = jsonData[name]
            
            '''
            # normal purposes
            if (name == "title") and ((row["Collection name:"]).lower() != "nan"):
                titlename = row["Collection name:"]
                # hard-code getting rid of possible parenthesis in title
                if '(' and ')' in titlename:
                    new_title = ''
                    start = False
                    for letter in titlename:
                        # out of the parenthesis
                        if start != True:
                            if letter == '(':
                                start = True
                            else:
                                new_title += letter
                        # in the parenthesis
                        else:
                            if letter == ')':
                                start = False
                    titlename = new_title
                title_name = titlename 
                jsonData[name] = titlename 
    
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
                jsonData[name] = str_year[-2:] # normal purposes
                #jsonData[name] = "25" # TESTING PURPOSES
            
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
                        if float(str(row["Estimated physical extent (linear feet):"]).replace('.', '', 1)) != 0:
                            jsonData[name][0]["number"] = str(row["Estimated physical extent (linear feet):"])
                            jsonData[name][0]["extent_type"] = "linear feet"
                            jsonData[name][0]["physical_details"] = row["Number and type of containers (e.g. 2 record storage boxes):"]
                            jsonData[name][0]["portion"] = "whole"
                    # if the string is a valid non-numerical string (something like str(int) + 'linear feet')
                    elif ("linear feet" in str(row["Estimated physical extent (linear feet):"]).lower()) or ("linear foot" in str(row["Estimated physical extent (linear feet):"]).lower()) or (" lf" in str(row["Estimated physical extent (linear feet):"]).lower()) or (" ft" in str(row["Estimated physical extent (linear feet):"]).lower()):
                        patterns = re.findall(r"\d\d?\,?\d?\d?\d?\.?\d?\d?\d?", str(row["Estimated physical extent (linear feet):"])) 
                        if len(patterns) > 0:
                            if float(patterns[0]) != 0:
                                jsonData[name][0]["number"] = patterns[0]
                                jsonData[name][0]["extent_type"] = "linear feet"
                                jsonData[name][0]["physical_details"] = row["Number and type of containers (e.g. 2 record storage boxes):"]
                                jsonData[name][0]["portion"] = "whole"
                # if its a digital item 
                if (str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])).lower() != "nan": 
                    # if its just a numerical string
                    if str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).replace('.', '', 1).isdigit() == True:
                        if float(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]) != 0:
                            # if its also a valid physical item
                            if jsonData[name][0]["number"] != "":
                                # creating new dict item
                                copy1 = jsonData[name][0].copy()
                                jsonData[name].append(copy1)
                                jsonData[name][1]["number"] = str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])
                                jsonData[name][1]["extent_type"] = "megabyte(s)"
                                # if two types, physical details for both are none
                                jsonData[name][1]["physical_details"] = ""
                                jsonData[name][0]["physical_details"] = ""
                                # making both portions partial
                                jsonData[name][0]["portion"] = "part"
                                jsonData[name][1]["portion"] = "part"
                            # if its only digital
                            else:
                                jsonData[name][0]["number"] = str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])
                                jsonData[name][0]["extent_type"] = "megabyte(s)"
                                jsonData[name][0]["physical_details"] = str(row["Number and type of containers (e.g. 2 record storage boxes):"])
                                jsonData[name][0]["portion"] = "whole"
                    # if its a valid non-numerical string (something like str(int) + "MB")
                    elif (" mb" in str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).lower()) or ("megabytes" in str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).lower()) or ("megabyte" in str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).lower()):
                        patterns = re.findall(r"\d\d?\,?\d?\d?\d?\.?\d?\d?\d?", str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]))
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
                    extents_message = "Could not fill extents value. Neither Physical or digital extents are valid. Physical: '" + str(row["Estimated physical extent (linear feet):"]) + "', Digital: '" + str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]) + "'"
            
            elif name == "dates":
                jsonData[name][0]["expression"] = str(row["Estimated creation dates:"])
                # making string into estimated begin and end dates
                begin_end = functions.match_dates(str(row["Estimated creation dates:"]), str_year)
                if begin_end != 0:
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

        # checking if it won't be able to post because of 'extents'field
        if extents_message != "":
            errorlog.write("ID " + str(row["ID"]) + ": " + extents_message + "\n")
        errors_list, run_list, id_1_num, err_lis = post_and_check(jsonData, row, errors_list, int(id_1_num), title_name, run_list, err_lis)

        # making id_1 a str again
        tmp_id_1 = id_1_num
        if 10 <= tmp_id_1 < 999:
            id_1_num = "0" + str(tmp_id_1)
        elif tmp_id_1 < 10:
            id_1_num = "00" + str(tmp_id_1)
        
        time.sleep(1)
        extents_message = ""
        lines_looped +=1

    return lines_looped, run_list, errors_list, err_lis


def post_and_check(tmpjson, curr_row, curr_errors, curr_id, namet, run_lis, err_lis):
    ''' this function posts a jsonData variable of an accession into Aspace and checks if the
    repository connected to the accession exists. This function also writes to the 
    output "yes" and "no" csv's as well as the output logs. 

    Input:
        tmpjson: Dict/json(?), jsonData (contents of a .json file)
        curr_row: Sequence, the current row contents from the input csv
        curr_errors: list, a list of ID's of the row's with errors.
        curr_id: int, the current id_1 number.
        namet: str, the current title name
        run_lis: list, the list of ID's of the successful rows.
        err_lis: list, the list of ID's of the successful rows but with errors.
    Output:
        curr_errors: list, updated curr_errors
        run_lis: list, updated run_lis
        curr_id: int, updated id_1 number (if there was issues posting, subtract 1)
        err_lis: list, updated err_lis
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
        accession_uri = returned_out['uri'][1:]
        applog.write("ID " + str(curr_row["ID"]) + ": Posted new accession with URI " + str(accession_uri) + ".\n")

        # checking if repository relating to accession exists
        repo_true = functions.repo_exists(namet, curr_row["Collection identifier (e.g. Coll 100, for accruals only):"])

        # right now I have it so that the only time it doesn't write to the output csv's is if there is an 
        # error using the "get" method. 

        # if there was no error in "get" API
        if repo_true != -1:
            tmprow = curr_row.tolist()
            tmprow.append(str(accession_uri))
            run_lis.append(curr_row["ID"])

            # if repo was able to search 
            if type(repo_true) == tuple:
                # if > 0 found:
                if len(repo_true) == 5:
                    colltitle, collident, colluri, totalhits, foundissues = repo_true
                    tmprow.append(str(totalhits))
                    tmprow.append(str(colltitle))
                    tmprow.append(str(collident))
                    tmprow.append(str(colluri))
                    tmprow.insert(0, "Yes")
                    csv_writer.writerow(tmprow)
                # if totalhits == 0
                elif len(repo_true) == 2:
                    totalhits, foundissues = repo_true
                    tmprow.append(str(totalhits))
                    tmprow.insert(0, "No")
                    csv_writer.writerow(tmprow)
                # if errors in coll name or coll id
                if foundissues == True:
                    errorlog.write("ID " + str(curr_row["ID"]) + ": Repo searched with only collection name. Error in collection identifier.\n")
                    err_lis.append(curr_row["ID"])

            # if error in coll name or coll id and couldn't search repo
            else:
                errorlog.write("ID " + str(curr_row["ID"]) + ": Unable to search for a repo. Insufficient information (collection name or identifier).\n")
                tmprow.append("0")
                tmprow.insert(0, "No")
                csv_writer.writerow(tmprow)
                err_lis.append(curr_row["ID"])

        # if using "get" failed (system error)
        else:
            curr_errors.append(curr_row["ID"])
            errorlog.write("ID " + str(curr_row["ID"]) + ": Error in trying to use 'get' to find repo. Error message below:\n")
            errorlog.write("\t\t" + str(repo_true) + "\n")

    return curr_errors, run_lis, curr_id, err_lis


def main():
    ''' Program to go through lines of an input csv of new accession forms 
    and create a json file for each line, then posting a new accession to aspace
    from each file and checking if corresponding repositories exist. 

    Errors: exit with failure if id_1 number can't be found.  
    '''

    # checking if input file is .xlsx type
    global filename
    # if no file path inputted
    if filename == '':
        print("\nplease input a file path in line 26 or run the program with the file path as an argument:\n\te.g. python new_accessions.py ~/path/to/file\n")
        exit(1)
    # if input file is .xlsx type
    if (filename)[-4:] == 'xlsx':
        df1 = pd.read_excel(filename, sheet_name=0, header=0)
        df1.to_csv('./newfile.csv', index=False)
        filename = './newfile.csv'
    df = pd.read_csv(filename, encoding='mac_roman')

    # writing new column headers to output csv's
    data_top = list(df.head())
    data_top.insert(0, "Resource Found?")
    data_top.append("Created Accession URI:") 
    data_top.append("Number of found results:")
    data_top.append("Found Collection Title:") 
    data_top.append("Found Collection Identifier:") 
    data_top.append("Found Collection URI (of first match):")
    csv_writer.writerow(data_top)
    now = datetime.datetime.now()
    errorlog.write("\n--------------" + str(now) + "--------------\n")
    applog.write("\n--------------" + str(now) + "--------------\n")

    # finding id_1 number 
    #id_1 = functions.latest_id1("2025") # TESTING PURPOSES 
    id_1 = functions.latest_id1(str_year) # normal purposes

    tmp = ""
    # handling errors in finding id_1 below -- more info in functions.py
    if type(id_1) == tuple: # an error in 'get' API is the only time latest_id1 returns a tuple type
        tmp = id_1
        id_1 = id_1[0]
    if id_1 == -1 or id_1 == -2: 
        print("Error finding id_1 from last five accessions. Can not run--check errorlog.txt\n")
        if id_1 == -1:
            errorlog.write("Error finding id_1 from last five accessions. The last five id_1's from this year were not in consecutive order.\n")
        if id_1 == -2:
            errorlog.write("Error finding id_1 from last five accessions. Using 'get' method failed. Error message below:\n\t\t" + str(tmp[1]) + "\n")
        exit(1)
    
    # input loop for asking user what ID they would like to start and end on. 
    retstartend = functions.find_inputs("\nThis program runs any amount of *consecutive* IDs on an inputted 'new accessions' form file.\n\n   ----->  If start = 150 and end = 151, only ID # 150 and 151 will be ran.\n")
    start, end = retstartend

    # running program that fills and posts json data, updates csv and checks if repo exists
    final_returns = fill_data(df, start, end, id_1)
    lines_looped, run_list, errorlis, errlist = final_returns

    # print output statements
    if lines_looped == 0:
        print("\nUnable to run! start and end ID number might not be valid.\n")
    else:
        run_list.sort()
        if len(errorlis) != 0:
            print("\nAll ID's have been run\n\tLook for more information on this run in out/posted_accessions.csv, out/new_accessions_logs/errorlog.txt and out/new_accessions_logs/applog.txt.\n\n\tSUCCESSFUL IDs:", run_list, "\t successful ID's with errors:", errlist,"\n\tERROR IDs (not in posted_accessions):", errorlis, "\n")
            print("TODO : update 'Found Collection Indentifier' column in posted_accessions.csv\n\t\t--only for Accessions without a matching Resource\n")
        else:
            print("\nAll ID's have been run\n\tLook for more information on this run in out/posted_accessions.csv, out/new_accessions_logs/errorlog.txt and out/new_accessions_logs/applog.txt.\n\n\tSUCCESSFUL IDs:", run_list, "\t successful ID's with errors:", errlist,"\n\tAll Ran ID's in posted_accessions.\n")
            print("TODO : update 'Found Collection Indentifier' column in posted_accessions.csv\n\t\t--only for Accessions without a matching Resource\n")
    
    return 0


# running main without calling it
if __name__ == "__main__":
    main()
    # deleting temporary file if it exists
    if os.path.exists('./newfile.csv'):
        os.remove('./newfile.csv')
    outy.close()
    errorlog.close()
    applog.close()
