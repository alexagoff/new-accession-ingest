# SCUA New Accession Ingest Process Development

Working files and outlines for creating automating new accessions in ArchivesSpace.

[Workflow](https://uoregon.sharepoint.com/:u:/s/O365_SCUAprocessing/ES8hGWg_DoJEkE4B2ViETJ4B7sYGi2O9DMJI8LQb5HFwIQ?e=uI8MBR)

# Description:
This program creates accessions, posts them onto Aspace, and creates corresponding repositories
or updates existing repositories with new accssions.
It has two parts: 

- new_accessions.py: goes through lines of an input csv/xlsx of new acceessions
and creates a json file for each line, then posting a new accession to Aspace
from each json file and checking if a corresponding repository exists in Aspace. 

- update_repositories.py: goes through lines of the updated csv/xlsx of new
accessions, and links those accessions to either a new or existing resource.

Important Notes:
----------------
- The _all versions of new_accessions and update_repos run all ID's without being able to filter which ID's to run
- The column headers on the input .csv or .xlsx file for new_accessions must be on one line! If its spread into two lines the program will error.
- 'start' and 'end' only relate to the range of ID's (not lines) that will run. 
- IF TESTING new_accessions: go onto the file and 'Ctrl F' to find comments that say 'TESTING PURPOSES'. Uncomment the lines/blocks of code
  that it pertains to and comment out the lines/blocks of code that are by the comment that says 'nomal purposes'.

--------------------------------------------------------------------------------
Setup:
------
- you will need the following imports/modules:
  - python
  - pandas
  - ArchivesSnake
  - openpyxl (if you intend to use .xlsx as input for new_accessions.py)

Instructions for Use:
---------------------
- in the folder login_materials, create a new file 'config.py' that contains the same contents of the file 'config.py.example.txt'
but with your Aspace username and password in the corresponding fields. 
- go onto UO vpn
- STEP 1: note--input can be .csv or .xlsx type
  - either run: 
    - through terminal -- for processing a specific range of ID's:
      - *python new_accessions.py ~/path/to/input* (e.g. path could be ~/Desktop/foldered_materials/input.csv)
      - *python new_accessions.py* (if path to input file is manually entered in line 26).
    - or through the ▶ (run) button -- for running all ID's:
      - new_accessions_all.py (path of input file must be manually entered in line 26).
  - output: posted_accessions.csv, stored in the out folder. Also two logs of errors and updates in out/new_accessions_logs.
- STEP 2: 
  - either run:
    - through terminal -- for processing a specific range of ID's: 
      - *python update_repos.py* 
    - or through the ▶ (run) button -- for running all ID's:
      - update_repos_all.py 
  - output: logs in out/update_repos_logs.
