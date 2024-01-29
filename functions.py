import json
from login_materials import config
from asnake.client import ASnakeClient
from aspace_sess import client
import re # for repo_exists


# function to create a new accession (post) with data from a jsonData variable
def jsonpost(x):
    ''' This function posts a new accession filled with data.
    input: x, jsondata - a jsondata object 
    output: res_object, json file - the response to posting on aspace
    '''
    url = '/repositories/2/accessions'
    payload = json.dumps(x)
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
    ''' This function identifies if a repository exists matching the keywords from an 
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
        patternmatch = re.findall("[a-zA-Z]{2,4}\s\s?\d{3}", identifier)
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
    
    return res_object["results"][0]["title"], res_object["results"][0]["identifier"], res_object["results"][0]["uri"], res_object["total_hits"], found_issues
    
