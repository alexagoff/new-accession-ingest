import json 
import csv
import os 
import functions
import sys
from datetime import date 
import datetime
import pandas as pd

# log for when I post new updates accessions, updated resources, updates events

# edit line below to manually enter a .csv 
filename = './out/posted_accessions.csv' 
if len(sys.argv) > 1:
    filename = sys.argv[1]
events = "./out/update_repos_logs/events_created.txt"
app = "./out/update_repos_logs/applications_parsed.txt"
server = "./out/update_repos_logs/server_updates.txt"
err = "./out/update_repos_logs/found_errors.txt"

eventslog = open(events, "a")
applog = open(app, "a")
serverlog = open(server, "a")
errlog = open(err, "a")

def main():
    now = str(datetime.datetime.now())
    errlog.write("\n--------------" + str(now) + "--------------\n")
    applog.write("\n--------------" + str(now) + "--------------\n")
    eventslog.write("\n--------------" + str(now) + "--------------\n")
    serverlog.write("\n--------------" + str(now) + "--------------\n")

    successful_runs = []
    errors_runs = []

    df = pd.read_csv(filename)
    # going through lines of input csv
    for index, row in df.iterrows():
        # trying to only run ID 169
        if str(row["ID"]) != '169':
            continue
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
                            found_resource["collection_management"]["processing_status"] = "New material recieved"
                            post_rec = functions.accupdate('/'+row["Found Collection URI (of first match):"], found_resource)
                            if "error" in post_rec:
                                errlog.write("ID " + str(row["ID"]) + ": Error in using posting edited and linked resource.\n")
                                errlog.write("\t\t" + str(post_rec) + "\n")
                                errors_runs.append(str(row["ID"]))
                            # everything ran successfully!
                            else:
                                successful_runs.append(str(row["ID"]))

        # if no matching repository was found
        else: 
            pass
            # notes
            #   create a new resource record (create_resource_record template in teams)
            #   populate new resource record with:
            #       the things to change are in hashtags
            #       id_0 has to be row["Found Collection Identifier"] number 
            #       extents is the same logic as "extents" in new_accessions.py

    # terminal message
    print("RAN ID's:", successful_runs, "\n\tERROR ID's:", errors_runs, "\n") 
    
    return 0

if __name__ == "__main__":
    main()
    eventslog.close()
    applog.close()
    serverlog.close()
    errlog.close()
