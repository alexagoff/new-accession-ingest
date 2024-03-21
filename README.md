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
- The _all versions of new_accessions and update_repos run all ID's without being able to filter which ID's to run
- The title/column header line on the input .csv file must all be on the first line/one line! If its spread into two lines the program will error.
- Start and end only relate to the range of ID's (not lines) that will run. If start = 166 and end = 168, then only 166, 167 and 168 will run. This applies *even if the csv is unordered by ID number*.

-------------------------------------------------------
How To Use:
-----------
- in the folder login_materials, duplicate the file config.txt and rename it 'config.py', then replace the 'username' and 'password' sections with your own information in the new file.  
- you will need the pandas module, so if you haven't installed it already, you can by following the instructions here https://pandas.pydata.org/docs/getting_started/install.html
- you will need to also install asnake and regex if not installed already
- you will need to install openpyxl if you intend to use .xlsx file as input instead of .csv for new_accessions.py
- go onto UO vpn
- STEP 1: note--input can be .csv or .xlsx type
  - either run: 
    - terminal:
      - *python new_accessions.py ~/path/to/input* (e.g. ~/Desktop/folder/input)
      - *python new_accessions.py* (if path to input file is manually entered in line 26).
    - or the ▶ (run) button:
      - *new_accessions_all.py* (if path of input filel is manually entered in line 17).
  - output: posted_accessions.csv, stored in the out folder. Also two logs of errors and updates in out/new_accessions_logs.
- STEP 2: 
  - either run:
    - terminal: 
      - *python update_repos.py* 
    - or the ▶ (run) button:
      - *update_repos_all.py* 
  - output: logs in out/update_repos_logs.
