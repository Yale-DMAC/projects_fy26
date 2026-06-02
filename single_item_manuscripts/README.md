# Single-Item Manuscripts
Last updated on 12/16/2025 by Kylene Hutchinson.

| Start Date | End Date | Contributors | Informed Stakeholders |
| ---------- | -------- | ------------ | --------------------- |
| 09/19/2024 | 12/10/2025 | Kylene Hutchinson | Alicia Detelich, Todd Fell, Gabby Redwine, Hannelore Segers  |

# Overview
## Problem Statement
The Metadata Steering Committee has updated cataloging standards for single item manuscripts, changing coding in the Leader field from position 06 p and position 07 c (PC) to position 06 t and position 07 m (TM). All cataloging for single item manuscripts will reflect this change, but the change needs to be retroactively applied to existing data.
## Goals
- Identify and create a list of single item manuscripts bib numbers who have the LDR 06-07 = PC
- Change the LDR field of PC to TM
- Update 008 field date and date type fields
- Remove 006s that begin with t
- Add 655_7|a Manuscripts. |2 lcgft
- Add 665s for Academic Thesis and Sammelbands as needed
- Update 008 29-31 and 33 if they are blank
- Add any missing RDA fields
- Remove 079 field if it exists in the 035.
# Background
After the reorganization of Beinecke and Manuscripts into Special Collections Technical Services, single-item manuscripts have been re-routed to the Bibliographic Description Unit (BDU), which has resulted in a need to update cataloging documentation. Members of UDAG identified non-standard coding of single-item manuscript materials, and the Metadata Steering Committee has announced new cataloging practices to meet the national standards and best practices.

The original coding of PC has led to a 006t being added to every single-item manuscript, a process that would be unnecessary under the proposed TM. The majority of these items are not mixed materials or collections, so the PC coding is incorrect.

The project was expanded past its initial update of the LDR field to update, add, and fix fields that were commonly found to have errors within the selected records.

No consistent cataloging was used to easily identify these records. Instead, we narrowed a list down as far as we safely could, then catalogers reviewed the list to weed out bibs and give us our final list.

# Process
See [bib_report.py](bib_report.py), [findingaid_filter.drl](findingaid_filter.drl), [single_item_manuscripts.py](single_item_manuscripts.py), [008_update.drl](008_update.drl), and [852t_update.drl](852t_update.drl)

- Run [bib_report.py](bib_report.py) to create a file for catalogers to manually review and weed out
- Create an Itemized set in Alma from the report after Catalogers finish weeding out records.
- Filter the set using [findingaid_filter.xslx](findingaid_filter.xslx)
- Export set as a binary mrc file.
- Run [singleitemmanuscripts.py](singleitemmanuscripts.py) on the mrc file.
- Create an Itemized set in Alma from the 773 list created.
- Export the 773 set's items, and the original set's items as a csv
- From the csv create two text files from the two csvs. One containing holding record ids and the other item PIDs. Only include Item PIDs that are a copy 0
- Import updated mrc file into Alma, overlay existing records but not creating new records.
- Run [008_update.drl](008_update.drl) on the imported records to update the 008 after the LDR has been adjusted.
- Create itemized sets for Holding Records and Item Records.
- Run the Change Item Record job on the Item set, updating copy status to 1
- Run the Change Holding Records job on the Holdings set, run the norm rule of [852t_update.drl](852t_update.drl)

# Notes
| Date | Highlight | Notes |
| ---- | --------- | ----- |
| 09/05/2024 | Requested | Todd submitted a request for this project to be worked on. |
| 09/19/2024 | Assigned | Alicia forwarded the request to SCMS and requested I work on it. |
| 09/26/2024 | Outreach | Reached out to Todd to ask questions about identifying records. |
| 09/27/2024 | Meeting | Met with Todd, Alicia, and Hannelore to discuss this project. I submitted a spreadsheet of data based on initial identification efforts for Todd, Gabby, and Hannelore to review. |
| 10/07/2024 | Meeting | Met again to discuss, this time Gabby was in attendance. New raw data was offered based on filtering suggestions from BDU. |
| 12/13/2024 | Outreach | Todd reached out to Alicia and I to let us know that the trio was still reviewing the data and hoped to have better information by January. |
| 02/24/2025 | Meeting | Met with Todd, Hannelore, and Gabby to discuss the progress they made in identifying records since our last meeting. Requested they make a list of exactly what they want done to the data depending on what condition. |
| 03/04/2025 | Meeting | Met again the BDU trio to discuss this topic and review the conditions list. |
| 03/31/2025 | Testing | I ran a test on the sample set provided using the conditions list. Initial error found in which the LDR numbers were off and caused the 008 to vanish, this is fixed upon fixing LDR. |
| 04/04/2025 | Testing | Ran the fixed test on a new batch of test records. No issues found. Tried sorting the records so the 650 field would appear next to the other 65xs but this sorted the 5xxs which was undesired. |
| 04/24/2025 | Testing | Voyager Test was reset the previous week. After remaking the rules in GDC, they were re-run on the 100 prior test records and the new 65 test records in the test enirovment. |
| 05/06/2025 | Hold | Todd and I made the decision to wait until after the Alma migration to update these records. |
| 08/29/2025 | Meeting | Met with Todd, Gabby, Hannelore, Alison Clemens, and Alicia to discuss impacts on discovery. |
| 09/09/2025 | Meeting | Met to review reports exploring the impact on discovery of changing single item manuscripts to TM |
| 11/05/2025 | Meeting | Met to dicuss new changes and updates being requested. |
| 11/10/2025 | Testing | Tested the updates in Alma Test environment and passed off to BDU for review. |
| 11/19/2025 | Testing | Applied further requested updates in Alma Test. |
| 12/09/2025 | Production | Ran process through Alma Production with no detected errors. |

# Review

## Data Details
35,573 records have a PC LDR.
	15,726 of these records have a 655
	5,182 of these records have a 655 manuscript
	4,068 records have a dcrmmss 040e
	21,263 records do not have a dacs 040e
		9,406 records have a Date Type of S
			3,073 records have a dcrmmss 040e
			5,057 records have a appm 040e
			1,275 records have other 040e
	19,702 records have a 006t
		10,716 records have a Date Type of s
	
85,130 records have a TM LDR.
	21,022 of these records have a 655

## Communication
| Name             | Position                                                           | Notes                                                                                                       |
| ---------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| Todd Fell        | Associate Director, Bibliographic Description                      | - Requested Remediation Project<br>- Provided information about cataloging used to assist in identification<br>- Head of BDU unit that manually weeded out bibs, reviewed results and requested changes |
| Alicia Detelich  | Assistant Director of Special Collection Metadata Services         | - Assigned Project<br>- Acted as Advisor |
| Hannelore Segers | Early Materials Cataloger, Special Collections Technical Services  | Part of BDU unit that manually weeded out bibs, reviewed results and requested changes |
| Gabriela Redwine | Catalog/Metadata Librarian, Special Collections Technical Services | Part of BDU unit that manually weeded out bibs, reviewed results and requested changes |
| Alison Clemens | Director of Access Services and Operations, Beinecke | Advised on impacts to discovery |
## Results
13,992 bibliographic records were updated. 12,200 holding records were updated. 12,709 item records updated.