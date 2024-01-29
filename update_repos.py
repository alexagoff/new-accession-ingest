import json 
import csv
import os 
#import functions
import sys
#import time
#from datetime import date 
#import datetime
import pandas as pd
#import re

# edit line below to manually enter a .csv 
filename = './out/posted_accessions.csv' 
if len(sys.argv) > 1:
    filename = sys.argv[1]
events = "./out/update_repos_logs/events_created.txt"
app = "./out/update_repos_logs/applications_parsed.txt"
server = "./out/update_repos_logs/server_updates.txt"

eventslog = open(events, "a")
applog = open(app, "a")
serverlog = open(server, "a")


def main():
    df = pd.read_csv(filename)

    for index, row in df.iterrows():
        # if a matching repository was found for this row
        if row["Repo Found?"] == "Yes":
            # get the json body for this accession
            url = row["Created Accession URI:"]
            response = client.get(url)
            print(response)
        # if no matching repository was found
        else:
            pass      
    return 0

if __name__ == "__main__":
    eventslog.close()
    applog.close()
    serverlog.close()
    main()

# work on "yes" on the second section if done with this..
# for the event record, do Executing program and SCUA api calls as the other one -->"role":"executing_program", "linked_records":"ref":*resource uri*

# next step:
# for the yes column, link the created accession and resource record
# you need to edit the accession to do this (only) 
# do get find json body
# post to that accession URI 
# "related_resources" and make {"ref":resource uri} object in the array 
# then after posting, create an event (in teams chat is an example)
# use the teams chat as a template (linked_agents dont touch)
# uri should be blank, leave repository alone, populate date:expression:begin == todays date, date_type=single, label = agent_relation, jsonmodel_type = date, everything else can be blank
# created_by->user_status are blank suppressed shoudl be false
# then post this new event
