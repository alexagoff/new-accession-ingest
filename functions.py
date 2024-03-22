##########################################
# functions.py                           #
#                                        #
# functions used by new_accesions and    #
# update_repos programs.                 #
# functions in file:                     #
# jsonpost                               #
# new_event                              #
# new_resource                           #
# accupdate                              #
# latest_id1                             #
# repo_exists                            #
# accget_jsondata                        #
# match_dates                            #
# find_inputs                            #
##########################################

import json
from aspace_sess import client
import re


# function to create a new accession (post) with data from a jsonData variable
def jsonpost(x):
    ''' This function posts a new accession filled with data.
    input: x, jsondata - a jsondata object 
    output: res_object, json file - the response to posting on aspace
    '''
    url = '/repositories/2/accessions'
    response = client.post(url, json=x)
    res_object = response.json()

    return res_object

def new_event(x):
    ''' This function posts a new event to Aspace.
    input: x, jsondata - a jsondata object 
    output: res_object, json file - the response to posting
    '''
    url = '/repositories/2/events'
    response = client.post(url, json=x)
    res_object = response.json()

    return res_object

def new_resource(x):
    ''' This function posts a new resource to Aspace.
    input: x, jsondata - a jsondata object 
    output: res_object, json file - the response to posting
    '''
    url = '/repositories/2/resources'
    response = client.post(url, json=x)
    res_object = response.json()

    return res_object

def accupdate(loc, x):
    ''' This function updates an item with new jsonData information.
    input: loc, the url e.g. (/repositories/2/item_type/4454)
           x, jsondata - a jsondata object
    output: res_object, json file - the response to posting on aspace
    '''
    url = loc
    response = client.post(url, json=x)
    res_object = response.json()

    return res_object

# function to see ID_1 of latest 5 accessions
def latest_id1(curr_yr):
    ''' This function finds the latest ID_1 number for new_accessions.py.
    input: curr_yr, str - string of the current year
    output: latest_id, str - the ID_1 
    errors:
        (-2, res_object) - error happens when there was an error when using the 
                           'get' API. 
        -1 - error happens when the previous 5 ID_1's were not in order sequentially
    '''
    url = 'repositories/2/accessions'
    # finding last id number (on uri)
    response = client.get(url, params={"all_ids": True})
    res_object = response.json()

    if "error" in res_object:
        return -2, res_object
    
    # not looping through just doing it manually for now
    response1 = client.get(url+"/"+str(res_object[-1]))
    response2 = client.get(url+"/"+str(res_object[-2]))
    response3 = client.get(url+"/"+str(res_object[-3]))
    response4 = client.get(url+"/"+str(res_object[-4]))
    response5 = client.get(url+"/"+str(res_object[-5]))
    res_obj1 = response1.json()
    res_obj2 = response2.json()
    res_obj3 = response3.json()
    res_obj4 = response4.json()
    res_obj5 = response5.json()

    # if the last 5 accessions are not in the current year:
    if (res_obj1["id_0"] != curr_yr[-2:]) and (res_obj2["id_0"] != curr_yr[-2:]) and (res_obj3["id_0"] != curr_yr[-2:]) and (res_obj4["id_0"] != curr_yr[-2:]) and (res_obj5["id_0"] != curr_yr[-2:]):
        latest_id = "001"
    # else, count the id_1 numbers
    else:
        tmplist = [res_obj5, res_obj4, res_obj3, res_obj2, res_obj1]
        latest_id = 0
        for resobj in tmplist:
            # only checking id_1's of current year
            if resobj["id_0"] == curr_yr[-2:]:
                latest = int(resobj["id_1"])
                # if its not one greater, return error
                if ((latest_id+1) != latest) and (latest_id != 0): 
                    return -1
                latest_id = latest
        
        latest_id+=1
        tmp = ""
        if 100 <= latest_id:
            tmp = str(latest_id)
        if 10 <= latest_id < 100:
            tmp = "0" + str(latest_id)
        elif latest_id < 10:
            tmp = "00" + str(latest_id)
        latest_id = tmp

    return latest_id

# check if repository exists with info from an accession
def repo_exists(name, identifier):
    ''' This function identifies if a resource exists matching the keywords from an 
    accession.
    input: name, str - the title of an accession
           identifier, str - the identifier (like 'coll 122') of an accession
    output: (title, identifier, uri, total_hits, found_issues)
            title, str - the title of the found repository
            identifier, str - the found repo identifier
            uri, str - the found collection uri
            total_hits, int(?) - the amount of found matching repositories
            found_issues, bool - True if only searched with title because a valid 
                            coll identifier couldn't be found from 'identifier' string.
    errors: -2 - this error happens when there is no valid name input or no valid name
                  and identifier input
            -1 - if 'get' API doesn't work when searching name + identifier or just name
            (0, found_issues) - happens when search was successful but there were no matches

    '''
    found_issues = False # to check for errors in "name" and "identifier" fields.
    if (str(name).lower() != "nan") and (str(identifier).lower() != "nan"):
        # extracting only something like "coll 188" 
        patternmatch = re.findall(r"[a-zA-Z]{2,4}\s\s?\d{3}", identifier)
        if len(patternmatch) == 0:
            finder = name
            found_issues = True
        else:
            finder = name + " " + patternmatch[0]

    elif (str(name).lower() != "nan") and (str(identifier).lower() == "nan"):
        finder = name
    # if theres no collection name or no name and no identifier
    else:
        return -2

    url = 'repositories/2/search?q=' + str(finder) + "&page=1&type[]=resource"
    response = client.get(url)
    res_object = response.json()  
    if "error" in res_object:
        return -1  

    elif res_object["total_hits"] == 0:
        return 0, found_issues
    #print(res_object["results"][0]["json"].loads()["title"])
    return res_object["results"][0]["title"], res_object["results"][0]["identifier"], res_object["results"][0]["uri"][1:], res_object["total_hits"], found_issues
    
# get a jsondata item from an accession url
def accget_jsondata(x):
    '''This function gets a jsondata item from using the 'get' API on Aspace
    to find an item from a URL. 
    input: x, str - url string 
    output: res_object, json - json file found
    '''
    response = client.get(x)
    res_object = response.json()
    return res_object

# find date pattern from input
def match_dates(match_string, str_year):
    ''' attempts to find begin and end date from "estimated creation date" string.
    Right now it only will detect 4 number years just to make sure mistakes aren't made.
    if theres a year like "19" or "80", it will return 0. 
    
    input: match_string-str, the string from the csv column "Estimated creation dates:"
           year-str, the string of the current year  
    output: list, a list [start, end] of the starting and ending date in the timeframe. 
            
    Errors: If date could not be found from the patterns, then returns 0.
    '''
    # regex patterns 
    pattern1 = r"\d{4}'?\s?s.*\d{4}'?\s?s" 
    pattern2 = r"\d{4}'?\s?s.*\d{4}"
    pattern3 = r"\d{4}.*\d{4}'?\s?s"
    pattern4 = r"\d{4}.*\d{4}"
    pattern5 = r"\d{1,2}\s?\-\-?\s?[a-zA-Z]+\s?\-\-?\s?\d{4}"
    pattern6 = r"[a-zA-Z]+\s?\-+\s?\d{4}"
    pattern7 = r"\d{4}'?\s?s"
    pattern8 = r"\d{4}"

    # if adding new patterns, the ORDER of these patterns is important! it goes from 
    # most specific match to least specific (most specific being something that has to be like 2000s-3000s exactly and least specific just any four digit number)
    patterns_list = [pattern1, pattern2, pattern3, pattern4,
                        pattern5, pattern6, pattern7, pattern8]
    
    months_list = ["january", "february", "march", "april", "may", "june", "july",
                        "august", "september", "october", "november", "december", "jan", 
                        "feb", "mar", "apr", "jun", "jul", "aug", "sept", "sep", "oct", "nov", "dec"]

    # X stands for any integer
    # Y stands for any letter

    found = False
    # going through each regex pattern and seeing if theres a match with one of them
    for pattern in patterns_list:
        find_list = re.findall(pattern, match_string)
        # if theres a match with a regex pattern 
        # if there is a match, it will return and not keep looping
        if len(find_list)>0:
            found = True
            # matched with XXXXs-XXXXs or XXXX-XXXXs
            if (pattern == pattern1) or (pattern == pattern3):
                # extracting the two four digit numbers
                new_list = re.findall(r"\d{4}", find_list[0])
                # check first three characters of the last four digit number to see if its in this decade
                if new_list[-1][:3] == str_year[:3]:
                    # returns with ending at current year
                    return [new_list[0], str_year] 
                # returns with ending at last four digit number but with 9 at the end
                return [new_list[0], new_list[-1][:3]+'9'] 
            # matched with XXXXs-XXXX or XXXX-XXXX
            elif (pattern == pattern2) or (pattern == pattern4):
                # returns first four and last four characters of matched string
                return [str(find_list[0])[:4], str(find_list[0])[-4:]]
            # matched with form 8-YYY-2019 or YYY-2019
            elif (pattern == pattern5) or (pattern == pattern6):
                # extracting just the letter parts
                test_month = re.findall(r"[a-zA-Z]+", find_list[0])
                # if the letters part isn't a month its not valid
                if test_month[0].lower() not in months_list:
                    return 0
                # returning the last four characters
                return [str(find_list[0])[-4:]]
            # matched with XXXXs
            elif pattern == pattern7:
                # extracting just the year without 's'
                new_year = re.findall(r"\d{4}", str(find_list[0]))
                # check first three characters of the four digit number to see if its in this decade
                if new_year[0][:3] == str_year[:3]:
                    return [new_year[0][:3]+'0', str_year] 
                return [new_year[0][:3]+'0', new_year[0][:3]+'9']
            # matched with XXXX
            elif pattern == pattern8:
                return [find_list[0]]
    
    # if match_string didn't match any of the patterns
    if found == False:
        return 0

# find inputs for begin and end ID's
def find_inputs(string_print):
    ''' this function takes inputs dictating the constraints of what 
    ID's in the input csv will be run.

    Input: none
    output:
        x = the lower constraint x <= lowest ID #
        y = the higher constraint y >= highest ID #
    '''
    x = 0
    y = 0

    print(string_print)
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
