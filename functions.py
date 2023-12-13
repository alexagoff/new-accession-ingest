import json
from login_materials import config
from asnake.client import ASnakeClient
from aspace_sess import client
import re # for repo_exists


#API to get the shelf from the barcode:
def get_shelf(x):
    ''' 
    input: barcode string
    output: shelf code string that barcode is at (in Aspace)
    errors: returns 0 when barcode doesn't exist in Aspace
    '''
    url = 'repositories/2/top_containers/search?q=' + str(x)
    response = client.get(url)
    res_object = response.json()
    
    # if barcode doesn't exist
    if res_object['response']['numFound'] == 0:
        return 0
    
    tmp = res_object['response']['docs'][0]["title"].split(",")
    shelf_code = "4SCUA"
    foundword = False

    # finding shelf code in tmp
    for phrase in tmp:
        if foundword == True:
            break
        # only parsing through the phrase where shelf code is
        if "4SCUA" in phrase:
            tmpword = "" # stores all letters of phrase
            add_num = False
            for letter in phrase:
                tmpword += letter
                # not adding to shelf_code until 4SCUA type confirmed
                if add_num == True:
                    if letter.isnumeric(): # if letter is a number still
                        shelf_code += letter
                elif "4SCUA" in tmpword:
                    add_num = True
            foundword = True

    return shelf_code

#API to get the barcodes in the 'x' shelf:
def get_barcodes(x):
    ''' 
    input: shelf code string
    output: barcode string(s) that are connected to shelf code (in Aspace)
    errors: returns 0 when shelf code doesn't exist 
    '''
    url = 'repositories/2/top_containers/search?q=' + str(x)
    response = client.get(url)
    res_object = response.json()
    
    if res_object['response']['numFound'] == 0:
        return 0
    retlist = []
    # going through all docs in shelf
    for item in res_object['response']['docs']:
        retlist.extend(item['barcode_u_sstr'])
    
    return retlist

# API to see if a shelf exists:
def shelf_exists(x):
    '''
    input: shelf code string
    outputs True/False if shelf exists in Aspace
    '''
    url = 'repositories/2/search?q=' + str(x) + "&page=1&type[]=location"
    response = client.get(url)
    res_object = response.json()
    # if there is no shelf in aspace
    if res_object['total_hits'] == 0:
        return False
    
    return True

# gets the shelf uri from a shelf string
def shelf_uri(x):
    ''' 
    input: shelf code string
    output: uri in form of 'location/434343' 
    errors: returns 0 when shelf code doesn't exist 
    '''
    # finding from searching in locations 
    url = 'repositories/2/search?q=' + str(x) + "&page=1&type[]=location"
    response = client.get(url)
    res_object = response.json()
    # if shelf doesn't exist (in the runShelfread.py code, we'll never need this condition)
    if res_object['total_hits'] == 0:
        return 0
    uri_loc = (json.loads(res_object['results'][0]['json'])['uri'])[1:]
    
    return uri_loc

# gets the barcode uri from a barcode string
def barcode_uri(x):
    ''' 
    input: barcode string
    output: uri number like '343434' 
    errors: returns 0 when barcode doesn't exist 
    '''
    url = 'repositories/2/top_containers/search?q=' + str(x)
    response = client.get(url)
    res_object = response.json()
    # if barcode doesn't exist (in the runShelfread.py code, we'll never need this condition)
    if res_object['response']['numFound'] == 0:
        return 0
    uri_loc = (res_object['response']['docs'][0]['id']).replace('/repositories/2/top_containers/', '')
    
    return uri_loc

# API to make barcode belong at shelfcode
def change_shelf(x, y):
    ''' 
    input: x = barcode string, y = shelfcode string
    output: True/False if was successfully changed
    '''
    url = "repositories/2/top_containers/batch/location"
    buri = barcode_uri(x)
    suri = config.aspacebaseurl + shelf_uri(y)

    response = client.post(url,
      params={ 'ids': [int(buri)],
               'location_uri': str(suri) })

    if response.json()['records_updated'] > 0:
        return True
    
    return False

# --------------------------------------------------------

# function to create a new accession (post) with data from a jsonData variable
def jsonpost(x):
    url = '/repositories/2/accessions'
    payload = json.dumps(x)
    response = client.post(url, json=x)
    res_object = response.json()

    return res_object


# function to see ID_1 of latest 5 accessions
def latest_id1(curr_yr):
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
    ''' this function returns a few different types...
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
    # if theres no collection name, no name or identifier, or just an identifier
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
    
