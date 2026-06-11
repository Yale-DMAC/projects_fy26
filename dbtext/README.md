# DBText Migration
Last updated on 06/04/2026 by Kylene Hutchinson.

| Start Date | End Date | Contributors | Informed Stakeholders |
| ---------- | -------- | ------------ | --------------------- |
| 01/15/2025 | 05/11/2026 | Kylene Hutchinson | Michael Rush, Alicia Detelich |

# Overview
## Problem Statement
DBText database is being retired. Records in DBText databases need to be migrated to ArchivesSpace.
## Goals
- Export DBText records as XML
- Map XML fields to ArchivesSpace fields
- Clean up and Normalize Records
- Create Top Containers, Events, Subjects, Agents, etc.
- Create Accession Records
# Background
The DBText database contained historical acquisitions information as records. This database is several decades old and has inconsistent data and field usage. Due to the state of the data in these records and the number of records, it was impossible to identify all issues. Due to the way ArchviesSpace validation works, it took many months to address all the clean up issues.

Due to the fact that there were multiple databases with different mapping needs, the focus was placed on creating a singular tool that used yaml files and individual normalization scripts. After selecting the database you wish to migrate, the tool runs a normalization process over it depending on that database's needs and turns the XML into an organized json file. From there the migration process occurs, refering to the database's yaml file for mapping specifications. It adds the Top Containers, Events, Subjects, and Agents, then creates an Accession record to attach them all to.

There was issues not only with Record IDs being duplicates of exisiting records in ArchivesSpace, but of being duplicates of other records in the XML file. ArchivesSpace does not allow for duplicate record IDs and will reject the record. To address this we included the database name and record number in the ID3 field. This gives an added bonus of being able to easily and quickly match with the XML records if we need to for future clean up projects.

# Process
See [migrator.py](/dbtext_migrator/migrator.py), [Normalize Folder](/dbtext_migator/normalize), [Mapping Folder](/dbtext_migrator/mapping), and [Connection YAML](/dbtext_migrator/connections/conn.yml)
- Export DBText database as an XML record.
- Create a normalization python script that processes and cleans up XML record, and add it to [Normalize Folder](/dbtext_migrator/normalize).
- Create a mapping yaml and add it to the [Mapping Folder](/dbtext_migrator/mapping).
- Add your connection information to the [Connection YAML](/dbtext_migrator/connections/conn.yml)
- Run [migration.py](/dbtext_migrator/migrator.py).
- Select Database name, select folder to save csv files to, and select the xml file to pull records from.
- Based on your database selection the associated yaml and normalization python script will be select and run on the XML file.
- Subjects, Agents, and Top Containers will be created during the first progress bar.
- Accession records will created in the second progress bar, and the records created in the first progress bar will be attached to the accession record as appropriate.
- Two csv records will be created in the folder you selected recording all records created and any errors that occur separately.

# Notes

| Date | Highlight | Notes |
| ---- | --------- | ----- |
| 2024 | Requested | Mike Rush requested this project be performed. Alicia was on leave during this time and new SCMS staff was being onboarded so addressing it was delayed. |
| 01/15/2025 | Assigned | Alicia assigned this project to Kylene. |
| 03/03/2025 - 06/2025  | Meetings | Meet over this time period to discuss how the migration will be handled and the work flow. |
| 03/20/2025 | Files Received | Mike Rush provided XML files and Migration Mapping Guides. |
| 06/2025 - 10/2025 | Testing | Testing of Code was performed over time during this time period. |
| 11/06/2025 - 11/07/2025 | CatMSS and Deposit Migration | CatMSS and Deposit were migrated to ArchivesSpace production. |
| 12/08/2025 - 01/21/2026 | CatACQ Testing | Final Testing for CatACQ migration in Test was done during this time period. Winter break occurred during this time. |
| 01/22/2026 - 02/10/2026 | CatACQ Migration | CatACQ was migrated to ArchivesSpace production. |
| 02/17/2026 - 04/16/2026 | ACQ Testing | Final Testing for ACQ migration in Test was done during this time period. Massive delay occurred due to hardware failure and waiting on a replacement. |
| 04/20/2026 - 04/30/2026 | ACQ Migration | ACQ Database was migrated to ArchivesSpace production. |
| 05/11/2026 | Completed | Mike Rush approved the final database migration the project is considered completed. Staff were given paths to submit any identified issues in the future. |

# Review

## Data Details
Deposit - 282 records
CATMSS - 3,189 records
CATACQ - 168,044 records
ACQ - 41,192 records

## Communication
| Name | Position | Notes |
| --- | --- | --- |
| Alicia Detelich | Head of Special Collections Metadata Services, SCTS | Assigned, advised, and approved of process. |
| Michael Rush | Operation Strategist, Public Services and Operations | Requested Migration, Exported XML records, Created Mapping plan and identified some clean up issues, helped reviewed testing for errors, and approved of results. | 
## Results
Deposit and CatMSS databases migrated smoothly before the October deadline. However, CatACQ and ACQ databases contained a huge number of records with normalization issues that took several more months to find and address. Final database was migrated at the end of April, 6 months past the initial deadline. Minimal errors were found and addressed but it is expected more will be found over time due to the inconsistent practices in DBText.
Future clean up projects include cleaning up the messy agent and subject records that migrated with these records.