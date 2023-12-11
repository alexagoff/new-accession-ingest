# SCUA New Accession Ingest Process Development

Working files and outlines for creating automating new accessions in ArchivesSpace.

[Workflow](https://uoregon.sharepoint.com/:u:/s/O365_SCUAprocessing/ES8hGWg_DoJEkE4B2ViETJ4B7sYGi2O9DMJI8LQb5HFwIQ?e=uI8MBR)

# Description:
This program goes through lines of an input csv of new acceession forms 
and creates a json file for each line, then posting a new accession to Aspace
from each json file and checking if a corresponding repository exists in Aspace. 

This program outputs: 
accessions_no.csv -- the accessions that didn't find a corresponding repository.
acceessions_yes.csv -- the accessions that found a corresponding repository.
applog.txt -- a log of the new accessions created in Aspace.
errorrlog.txt -- a log of all of the errors found while running.


IMPORTANT NOTES:
- The title/column header line on the input .csv file must all be on the first line/one line! If its spread into two lines the program will error.
- The "start" and "end" inputs that you put in on check_existing_accessions.py can be any real number, so if the start number is < the actual start id, it will start at the lowest ID# and 
if start is > the largest id #, it won't run any id's. This is the same for "end".
- Start and end only relate to the range of ID's (not lines)that will run. If start = 166 and end = 168, then only 166, 167 and 168 will run. This goes even if the csv is unordered by ID number.

-------------------------------------------------------
How To Use:
-----------
- create a config.py file using the template from config_example.txt, 
  updating with your own information 
- you will need the pandas module, so if you haven't installed it already,
  you can by following the instructions here https://pandas.pydata.org/docs/getting_started/install.html
- go onto UO vpn
- run new_accessions.py 
  - do either:
    - python new_accessions.py ~/path/to/form.csv (e.g. ~/Desktop/folder/input.csv) with form.csv input
    - python new_accessions.py (without argument) if path to form.csv is manually entered in new_accessions.py (line 25).
  - output: accessions_no.csv and accessions_yes.csv if repositories connected to accession(s) already exist. Both sent to Alexa. Also two logs of errors and updates in out/new_accessoins_logs.
- run update_repositories.py
  - do either:
    - python update_repositories.py ~/path/to/csv ~/path/to/csv (e.g. ~/Desktop/folder/yes_input.csv ~/Desktop/folder/no_input.csv) with 'yes' and 'no' csv's as the arguments.
    - python update_repositories.py (no arguments) if paths to csvs are already manually entered in new_accessions.py.
  - output: logs in out/update_repos_logs 
- check out/log and out/output_existing.csv 
