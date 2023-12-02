# SCUA New Accession Ingest Process Development

Working files and outlines for creating automating new accessions in ArchivesSpace.

[Workflow](https://uoregon.sharepoint.com/:u:/s/O365_SCUAprocessing/ES8hGWg_DoJEkE4B2ViETJ4B7sYGi2O9DMJI8LQb5HFwIQ?e=uI8MBR)

# Description:
This program creates new accessions from input forms and organizes those new accessions into already existing or new repositories in Aspace. 
Check the "how to use" section for more information about how to run the program and the outputs of each program. 
Please also read the important notes section!!


IMPORTANT NOTES:
- check_existing_accessions.py runs ID's in chronological order. It will start at the ID of the form input one number greater than the number in DONT_EDIT.txt and create accessions for all ID form input numbers after that until the end of the form input csv. 
- for this reason, if there is ever a need to create a new accession record 
manually, please use the form input from the ID one larger than the number in DONT_EDIT.txt and edit DONT_EDIT.txt afterwards to be one larger.
- in the case that an accession is manually made and it was from the form input that was not and ID number one larger than the number in DONT_EDIT.txt, dont change the number in DONT_EDIT.txt. It will create a copy of the accession that was made manually, but will avoid missing form inputs. 

-------------------------------------------------------
how to use:

- create a config.py file using the template from config_example.txt, 
  updating with your own information 
- you will need the pandas module, so if you haven't installed it already,
  you can by following the instructions here https://pandas.pydata.org/docs/getting_started/install.html
- go onto UO vpn
- run check_existing_accessions.py 
  - NOTE: the title/column header line on the .csv file must all be on the first line! If its spread into two lines the program will error.
  - do either:
    - python check_existing_accessions.py ~/path/to/csv (e.g. ~/Desktop/folder/input.csv) with form.csv input
    - python check_existing_accessions.py (without argument) if path to form.csv is manually entered in check_existing_accessions.py (line 33).
  - output: one csv of 'yes' and one of 'no's if repositories connected to accession(s) already exist. Both sent to Alexa. Both in out folder.
- run new_accessions.py
  - do either:
    - python new_accessions.py ~/path/to/csv ~/path/to/csv (e.g. ~/Desktop/folder/yes_input.csv ~/Desktop/folder/no_input.csv) with 'yes' and 'no' csv's as the arguments.
    - python new_accessions.py (no arguments) if paths to csvs are already manually entered in new_accessions.py.
  - output: logs in the out file as well as updating aspace with information (add more)
- check out/log and out/output_existing.csv 
