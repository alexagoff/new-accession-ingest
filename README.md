# SCUA New Accession Ingest Process Development

Working files and outlines for creating automating new accessions in ArchivesSpace.

[Workflow](https://uoregon.sharepoint.com/:u:/s/O365_SCUAprocessing/ES8hGWg_DoJEkE4B2ViETJ4B7sYGi2O9DMJI8LQb5HFwIQ?e=uI8MBR)

-------------------------------------------------------
how to use:

- create a config.py file using the template from config_example.txt, 
  updating with your own information 
- run check_existing_accessions.py to output a csv of 'yes' or 'no's to 
  check if accession(s) from form(s) already exist. this outputs a .csv in out/output_existing.csv
- run new_accessions.py, optionally enter "name".csv as an argument
  (in this case, edit file inputcsv path, line 29).
  python3 new_accessions.py 
  or
  python3 new_accessions.py input.csv 
  this outputs logs in the out file as well as updating aspace with information
- check out/log and out/output_existing.csv 