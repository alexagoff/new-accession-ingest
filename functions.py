import json
from login_materials import config
from asnake.client import ASnakeClient
from aspace_sess import client


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

# function to create new accessions
def create_accession(x):
    url = '/repositories/2/accessions'
    response = client.post(url)
    res_object = response.json()
    
    return res_object

# update an accession that already exists
def update_accession(x):
    url = '/repositories/:repo_id/accessions/' + str(x)
    response = client.post(url)
    res_object = response.json()

    return res_object

# function to see ID of latest accession
def latest_accession():
    url = 'repositories/2/accessions'
    response = client.get(url, params={"all_ids": True})
    res_object = response.json()
    # return last ID number
    return res_object[-1]

# create function to add detailed info about a accession
def add_accessioninfo(x):
    url = 'repositories/2/accessions/search?q=' + str(x)
    response = client.get(url)
    res_object = response.json()
    # if barcode doesn't exist (in the runShelfread.py code, we'll never need this condition)
    if res_object['response']['numFound'] == 0:
        return 0
    uri_loc = (res_object['response']['docs'][0]['id']).replace('/repositories/2/top_containers/', '')
    
    return uri_loc
