# SCUA New Accession Ingest Process Development

Working files and outlines for creating automating new accessions in ArchivesSpace.

[Workflow](https://uoregon.sharepoint.com/:u:/s/O365_SCUAprocessing/ES8hGWg_DoJEkE4B2ViETJ4B7sYGi2O9DMJI8LQb5HFwIQ?e=uI8MBR)

-------------------------------------------------------
how to use:

- create a config.py file using the template from config_example.txt, 
  updating with your own information 
- you will need the pandas module, so if you haven't installed it already,
  you can by following the instructions here https://pandas.pydata.org/docs/getting_started/install.html
- go onto UO vpn
- make sure the new accession intake form that you want to run is ordered by ID number! (smallest to largest)
- run check_existing_accessions.py 
  - do either:
    - python check_existing_accessions.py ~/path/to/csv (e.g. ~/Desktop/folder/input.csv) with form.csv input
    - python check_existing_accessions.py (without argument) if path to form.csv is manually entered in check_existing_accessions.py (line 33).
  - output: one csv of 'yes' and one of 'no's if repositories connected to accession(s) already exist. Both sent to Alexa. 
            Also two logs of errors and updates
- run new_accessions.py
  - do either:
    - python new_accessions.py ~/path/to/csv ~/path/to/csv (e.g. ~/Desktop/folder/yes_input.csv ~/Desktop/folder/no_input.csv) with 'yes' and 'no' csv's as the arguments.
    - python new_accessions.py (no arguments) if paths to csvs are already manually entered in new_accessions.py.
  - output: logs in the out file as well as updating aspace with information (add more)
- check out/log and out/output_existing.csv 
