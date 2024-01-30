import json 
import csv
import os 
import functions
import sys
#import time
from datetime import date 
import datetime
import pandas as pd
#import re

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
    now = datetime.datetime.now()
    errlog.write("\n--------------" + str(now) + "--------------\n")
    applog.write("\n--------------" + str(now) + "--------------\n")
    eventslog.write("\n--------------" + str(now) + "--------------\n")
    serverlog.write("\n--------------" + str(now) + "--------------\n")

    df = pd.read_csv(filename)
    # going through lines of input csv
    for index, row in df.iterrows():
        # if a matching repository was found for this row
        if row["Repo Found?"] == "Yes":
            # get the json body for this accession
            foundjson = functions.accget_jsondata(row["Created Accession URI:"])
            with open("horoscope_data.json", "w") as file:
                json.dump(foundjson, file)
            # if error in 'get' 
            if "error" in foundjson:
                errlog.write("ID " + str(row["ID"]) + ": Error in using 'get' API.\n")
                errlog.write("\t\t" + str(foundjson) + "\n")

        # if no matching repository was found
        else:
            pass     

        break 
    return 0

if __name__ == "__main__":
    main()
    eventslog.close()
    applog.close()
    serverlog.close()
    errlog.close()

# work on "yes" on the second section if done with this..
# for the event record, do Executing program and SCUA api calls as the other one -->"role":"executing_program", "linked_records":"ref":*resource uri*

# next step:
# for the yes column, link the created accession and resource record
# you need to edit the accession to do this (only) 
# do get find json body done
# post to that accession URI  done
# "related_resources" and make {"ref":resource uri} object in the array 
# then after posting, create an event (in teams chat is an example)
# use the teams chat as a template (linked_agents dont touch)

# to make an event:
# get template from teams chat
# {linked_records:ref:} is resource URI
# in date: {expression:} and date:{begin:} both todays date yyyy-0M-0D or yyyy-mm-dd
# uri should be blank, leave repository alone, populate date:expression:begin == todays date, date_type=single, label = agent_relation, jsonmodel_type = date, everything else can be blank
# suppressed shoudl be false
# then post this new event

# after making event , pull resource record and how to change this new record after getting is in notes.json
