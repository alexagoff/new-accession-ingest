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
- run check_existing_accessions.py 
  - do : python check_existing_accessions.py ~/path/to/csv (e.g. ~/Desktop/folder/input.csv) with form.csv input, or without argument if path to form.csv is manually entered in check_existing_accessions.py (line 33).
  - output: one csv of 'yes' and one of 'no's if repositories connected to accession(s) already exist. Both sent to Alexa. Both in out folder.
- run new_accessions.py, optionally enter "name".csv as an argument
  (in this case, edit file inputcsv path, line 33).
  python3 new_accessions.py 
  or
  python3 new_accessions.py input.csv 
  this outputs logs in the out file as well as updating aspace with information
- check out/log and out/output_existing.csv 