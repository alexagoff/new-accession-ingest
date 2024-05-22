################################################
# update_repos.py                              #
# running all ID's                             #
#                                              #
# This file is ran after the new_accessions    #
# file. It goes through the posted_accesssions #
# file and connects accessions to existing or  #
# created resources.                           #
#                                              #
################################################

import json 
import re
import functions
from datetime import date 
import datetime
import pandas as pd

# edit line below to manually enter a .csv 
filename = './out/posted_accessions.csv' 
app = "./out/update_repos_logs/app_updates.txt"
err = "./out/update_repos_logs/found_errors.txt"

applog = open(app, "a")
errlog = open(err, "a")


def main():
    now = str(datetime.datetime.now())
    errlog.write("\n--------------" + str(now) + "--------------\n")
    applog.write("\n--------------" + str(now) + "--------------\n")
    

    successful_runs = []
    errors_runs = []

    df = pd.read_csv(filename)
    # going through lines of input csv
    for _, row in df.iterrows():
        # if a matching repository was found for this row
        if row["Resource Found?"] == "Yes":
            # get the json body for this accession
            foundjson = functions.accget_jsondata(row["Created Accession URI:"])
            # if error in 'get' 
            if "error" in foundjson:
                errlog.write("ID " + str(row["ID"]) + ": Error in using 'get' API to pull accession.\n")
                errlog.write("\t\t" + str(foundjson) + "\n")
                errors_runs.append(str(row["ID"]))
            else:
                # editing accession .json to make resource connection
                if not {"ref": '/' + row["Found Collection URI (of first match):"]} in foundjson["related_resources"]: # if its not already linked
                    foundjson["related_resources"].append({"ref": ('/'+row["Found Collection URI (of first match):"])})
                posting_new = functions.accupdate('/' + row["Created Accession URI:"], foundjson)
                # if error in posting
                if "error" in posting_new:
                    errlog.write("ID " + str(row["ID"]) + ": Error in posting linked accession.\n")
                    errlog.write("\t\t" + str(posting_new) + "\n")
                    errors_runs.append(str(row["ID"]))
                else:
                    applog.write("ID " + str(row["ID"]) + ": Succesfully updated accession " + str(row["Created Accession URI:"]) + ", linking it with resource " + str(row["Found Collection URI (of first match):"]) + ".\n")
                    # making an event
                    with open("./extra_materials/eventtemplate.json", "r") as file:
                        jsonData = json.load(file)
                    jsonData["linked_records"][0]["ref"] = ('/' + row["Found Collection URI (of first match):"])
                    # yyyy-0M-0D
                    jsonData["date"]["expression"] = str(now[:10])
                    jsonData["date"]["begin"] = str(now[:10])
                    post_event = functions.new_event(jsonData)
                    # if error in posting
                    if "error" in post_event:
                        errlog.write("ID " + str(row["ID"]) + ": Error in posting new event\n")
                        errlog.write("\t\t", str(post_event) + "\n")
                        errors_runs.append(str(row["ID"]))
                    else:
                        applog.write("ID " + str(row["ID"]) + ": Created an event.\n")
                        # pull/update resource record
                        found_resource = functions.accget_jsondata(row["Found Collection URI (of first match):"])
                        if "error" in found_resource:
                            errlog.write("ID " + str(row["ID"]) + ": Error in using 'get' API to pull resource.\n")
                            errlog.write("\t\t" + str(found_resource) + "\n")
                            errors_runs.append(str(row["ID"]))
                        else:
                            if "repository_processing_note" in found_resource:
                                found_resource["repository_processing_note"]+="| New Material Recieved"
                            else:
                                found_resource["repository_processing_note"] = "| New Material Recieved"
                            found_resource["finding_aid_status"] = "Revise description"
                            found_resource["user_defined"]["enum_1"] = "No digital records"
                            if (str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])).lower() != "nan": 
                                # if its just a numerical string
                                if str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).replace('.', '', 1).isdigit() == True:
                                    if float(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]) != 0:
                                        found_resource["user_defined"]["enum_1"] = "To be staged, no description"
                            if "collection_management" not in found_resource:
                                found_resource["collection_management"] = {
                                                        "rights_determined": False,
                                                        "processing_status": "Unprocessed",
                                                        "jsonmodel_type": "collection_management",
                                                        "external_ids": [],
                                                        "uri": "",
                                                        "repository": {
                                                            "ref": "/repositories/2"
                                                        }}
                            found_resource["collection_management"]["processing_status"] = "New material recieved"
                            post_rec = functions.accupdate('/'+row["Found Collection URI (of first match):"], found_resource)
                            if "error" in post_rec:
                                errlog.write("ID " + str(row["ID"]) + ": Error in using posting edited and linked resource.\n")
                                errlog.write("\t\t" + str(post_rec) + "\n")
                                errors_runs.append(str(row["ID"]))
                            # everything ran successfully!
                            else:
                                applog.write("ID " + str(row["ID"]) + ": Succesfully updated resource " + str(row["Found Collection URI (of first match):"])+"\n")
                                successful_runs.append(str(row["ID"]))

        # if no matching repository was found
        else: 
            # creating new resource record
            with open("./extra_materials/resourcetemplate.json", "r") as file:
                jsonData = json.load(file)
            # filling with data from csv
            jsonData["title"] = str(row["Collection name:"])
            jsonData["finding_aid_title"] = "Guide to the " + str(row["Collection name:"])
            jsonData["finding_aid_filing_title"] = str(row["Collection name:"])
            jsonData["finding_aid_status"] = "in_progress"
            jsonData["id_0"] = str(row["Found Collection Identifier:"])
            jsonData["related_accessions"][0]["ref"] = '/' + str(row["Created Accession URI:"])
            jsonData["notes"][0]["subnotes"][0]["content"] = "[Identification of item], " + str(row["Collection name:"]) + ", " + str(row["Found Collection Identifier:"]) +", Special Collections and University Archives, University of Oregon Libraries, Eugene, Oregon." 
            # acq info 
            found_accession = functions.accget_jsondata(row["Created Accession URI:"])
            if "error" in found_accession:
                errlog.write("ID " + str(row["ID"]) + ": Error in using 'get' to find Accession information, see message below.\n")
                errlog.write("\t\t" + str(found_accession) + "\n")
                errors_runs.append(str(row["ID"]))
            else:
                jsonData["notes"][2]["subnotes"][0]["content"] = str(found_accession["provenance"])
                jsonData["notes"][4]["subnotes"][0]["content"] = str(found_accession["content_description"])
                # 'extents' logic
                # if its a physical item 
                if ((str(row["Estimated physical extent (linear feet):"])).lower() != "nan"):
                    # if the string is just a numerical character
                    if str(row["Estimated physical extent (linear feet):"]).replace('.', '', 1).isdigit() == True:
                        if float(str(row["Estimated physical extent (linear feet):"]).replace('.', '', 1)) != 0:
                            jsonData["extents"][0]["number"] = str(row["Estimated physical extent (linear feet):"])
                            jsonData["extents"][0]["extent_type"] = "linear feet"
                            jsonData["extents"][0]["physical_details"] = row["Number and type of containers (e.g. 2 record storage boxes):"]
                            jsonData["extents"][0]["portion"] = "whole"
                    # if the string is a valid non-numerical string (something like str(int) + 'linear feet')
                    elif ("linear feet" in str(row["Estimated physical extent (linear feet):"]).lower()) or ("linear foot" in str(row["Estimated physical extent (linear feet):"]).lower()) or (" lf" in str(row["Estimated physical extent (linear feet):"]).lower()) or (" ft" in str(row["Estimated physical extent (linear feet):"]).lower()):
                        patterns = re.findall(r"\d\d?\,?\d?\d?\d?\.?\d?\d?\d?", str(row["Estimated physical extent (linear feet):"])) 
                        if len(patterns) > 0:
                            if float(patterns[0]) != 0:
                                jsonData["extents"][0]["number"] = patterns[0]
                                jsonData["extents"][0]["extent_type"] = "linear feet"
                                jsonData["extents"][0]["physical_details"] = row["Number and type of containers (e.g. 2 record storage boxes):"]
                                jsonData["extents"][0]["portion"] = "whole"
                # if its a digital item 
                if (str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])).lower() != "nan": 
                    # if its just a numerical string
                    if str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).replace('.', '', 1).isdigit() == True:
                        if float(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]) != 0:
                            # if its also a valid physical item
                            if jsonData["extents"][0]["number"] != "":
                                # creating new dict item
                                copy1 = jsonData["extents"][0].copy()
                                jsonData["extents"].append(copy1)
                                jsonData["extents"][1]["number"] = str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])
                                jsonData["extents"][1]["extent_type"] = "megabyte(s)"
                                # if two types, physical details for both are none
                                jsonData["extents"][1]["physical_details"] = ""
                                jsonData["extents"][0]["physical_details"] = ""
                                # making both portions partial
                                jsonData["extents"][0]["portion"] = "part"
                                jsonData["extents"][1]["portion"] = "part"
                            # if its only digital
                            else:
                                jsonData["extents"][0]["number"] = str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"])
                                jsonData["extents"][0]["extent_type"] = "megabyte(s)"
                                jsonData["extents"][0]["physical_details"] = str(row["Number and type of containers (e.g. 2 record storage boxes):"])
                                jsonData["extents"][0]["portion"] = "whole"
                    # if its a valid non-numerical string (something like str(int) + "MB")
                    elif (" mb" in str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).lower()) or ("megabytes" in str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).lower()) or ("megabyte" in str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]).lower()):
                        patterns = re.findall(r"\d\d?\,?\d?\d?\d?\.?\d?\d?\d?", str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]))
                        if len(patterns) > 0:
                            if float(patterns[0]) != 0:
                                # if its also a valid physical item
                                if jsonData["extents"][0]["number"] != "":
                                    # creating new dict item
                                    copy1 = jsonData["extents"][0].copy()
                                    jsonData["extents"].append(copy1)
                                    jsonData["extents"][1]["number"] = str(patterns[0])
                                    jsonData["extents"][1]["extent_type"] = "megabyte(s)"
                                    # if two types, physical details for both are none
                                    jsonData["extents"][1]["physical_details"] = ""
                                    jsonData["extents"][0]["physical_details"] = ""
                                    # making both portions partial
                                    jsonData["extents"][0]["portion"] = "part"
                                    jsonData["extents"][1]["portion"] = "part"
                                # if its only digital
                                else:
                                    jsonData["extents"][0]["number"] = str(patterns[0])
                                    jsonData["extents"][0]["extent_type"] = "megabyte(s)"
                                    jsonData["extents"][0]["physical_details"] = str(row["Number and type of containers (e.g. 2 record storage boxes):"])
                                    jsonData["extents"][0]["portion"] = "whole"

                # if neither could be filled (physical or digital)
                if jsonData["extents"][0]["number"] == "":
                    errlog.write("ID " + str(row["ID"]) + ": Neither Physical or digital extents are valid. Physical: '" + str(row["Estimated physical extent (linear feet):"]) + "', Digital: '" + str(row["Estimated digital extent (MB): Unit Converter: https://www.unitconverters.net/data-storage-converter.html"]) + "'")
                    errors_runs.append(row["ID"])
                else:
                    # 'dates' logic
                    jsonData["dates"][0]["expression"] = str(row["Estimated creation dates:"])
                    # making string into estimated begin and end dates
                    curr_year = date.today()
                    begin_end = functions.match_dates(str(row["Estimated creation dates:"]), str(curr_year.year))
                    if begin_end != 0:
                        if len(begin_end)==2:
                            jsonData["dates"][0]["begin"] = begin_end[0]
                            jsonData["dates"][0]["end"] = begin_end[1]
                            jsonData["dates"][0]["date_type"] = "inclusive"
                        elif len(begin_end)==1:
                            jsonData["dates"][0]["begin"] = begin_end[0]
                            jsonData["dates"][0]["date_type"] = "single"
                    # could not separate into start and end dates
                    else:
                        jsonData["dates"][0]["date_type"] = "inclusive"  
                        errlog.write("ID " + str(row["ID"]) + ": Unable to match date.\n")

                    # posting new resource to Aspace
                    posted_rec = functions.new_resource(jsonData)
                    if "error" in posted_rec:
                        errors_runs.append(row["ID"])
                        errlog.write("ID " + str(row["ID"]) + ": Unable to post new resource. Error message below:\n")
                        errlog.write("\t\t" + str(posted_rec) + "\n")
                    # posted successfully
                    else:
                        resource_uri = posted_rec['uri'][1:]
                        applog.write("ID " + str(row["ID"]) + ": Posted new resource with URI " + str(resource_uri) + ".\n")
                        successful_runs.append(row["ID"])

    # terminal message
    print("\nAll ID's have been run\n\tLook for more information on this run in out/update_repos_logs/app_updates.txt and out/update_repos_logs/found_errors.txt\n\n\tSUCCESSFUL IDs:", successful_runs, "\n\tERROR IDs:", errors_runs, "\n") 
    
    return 0

if __name__ == "__main__":
    main()
    applog.close()
    errlog.close()
