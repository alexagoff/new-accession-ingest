'''
this file is a helper for running check_existing_accessions.py
this code finds the number of accessions created this year. 

you don't need to interact with this file by running it, it's called by 
check_existing_accessions.py
'''

import csv
import os 
import sys
import pandas as pd
import re
from datetime import date 

# getting today's year
todays_date = date.today() 
str_year = str(todays_date.year)


def main():
    # edit line below to manually enter a .csv 
    filename = './New Accession Intake Form copy.csv' 
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    # should it be "Completion time" or "Date of donation/purchase" ?
    df = pd.read_csv(filename)

    id_amnt = 0

    for index, row in df.iterrows():
        date = row["Completion time"]
        # using regex to find date
        pattern = "\d{1,2}\/\d{1,2}\/\d{2,4}"
        date_string = re.findall(pattern, date) # in format ['xx/xx/xx']
        # splitting the date and only getting the year
        year = date_string[0].split("/")[-1]
        # if str_year == year or if last two digits of str_year == year
        if (str_year == str(year)) or (str_year[-2:] == str(year)):
            id_amnt+=1

    return (id_amnt)