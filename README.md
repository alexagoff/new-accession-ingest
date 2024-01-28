# SCUA New Accession Ingest Process Development

Working files and outlines for creating automating new accessions in ArchivesSpace.

[Workflow](https://uoregon.sharepoint.com/:u:/s/O365_SCUAprocessing/ES8hGWg_DoJEkE4B2ViETJ4B7sYGi2O9DMJI8LQb5HFwIQ?e=uI8MBR)

# Description:
This program creates accessions, posts them onto Aspace, and creates corresponding repositories
or updates existing repositories with new accssions.
It has two parts: 
- new_accessions.py: goes through lines of an input csv of new acceession forms 
and creates a json file for each line, then posting a new accession to Aspace
from each json file and checking if a corresponding repository exists in Aspace. 

- update_repositories.py:

IMPORTANT NOTES:
- The title/column header line on the input .csv file must all be on the first line/one line! If its spread into two lines the program will error.
- Start and end only relate to the range of ID's (not lines) that will run. If start = 166 and end = 168, then only 166, 167 and 168 will run. This applies *even if the csv is unordered by ID number*.

-------------------------------------------------------
How To Use:
-----------
- create a config.py file using the template from config_example.txt, 
  updating with your own information 
- you will need the pandas module, so if you haven't installed it already,
  you can by following the instructions here https://pandas.pydata.org/docs/getting_started/install.html
- you will need to install openpyxl if you intend to use .xlsx file as input instead of .csv for new_accessions.py
- go onto UO vpn
- run new_accessions.py ('input' can be .csv or .xlsx type)
  - do either:
    - python new_accessions.py ~/path/to/input (e.g. ~/Desktop/folder/input)
    - python new_accessions.py (without argument) if path to input is manually entered in new_accessions.py (line 15).
  - output: posted_accessions.csv, stored in the out folder. Also two logs of errors and updates in out/new_accessions_logs.
- run update_repos.py
  - do either: ('input' can only be .csv type)
    - python update_repos.py ~/path/to/input.csv (e.g. ~/Desktop/folder/input.csv)
    - python update_repos.py (no arguments) if paths to csv is already manually entered in update_repos.py.
  - output: logs in out/update_repos_logs.
