# YCBA Instances
Last updated on 06/02/2026 by Kylene Hutchinson.

| Start Date | End Date | Contributors | Informed Stakeholders |
| ---------- | -------- | ------------ | --------------------- |
| 01/15/2026 | 05/20/2026 | Kylene Hutchinson |  Meg Rinn |

# Overview
## Problem Statement
YCBA had a resource who had notes instead of instances. Meg was attempting to fix this via an excel upload but was creating duplicate records.
## Goals
- Add Top containers to archival objects
- Remove instance notes
# Background
Original ticket was asking for help determining why the records were duplicating. It was determined Meg was using a method that ArchivesSpace couldn't handle properly. Once assessing the situation and identifying what she was attempting to achieve, I suggested letting us add the top containers for her.


# Process
See [ycba_instances.py](ycba_instances.py)
- Create a csv of uri, note text, top container indicator, child indicator, and grandchild indicator.
- Run [ycba_instances.py](ycba_instances.py) which reads the csv, creates a top container for unique indicators, pulls the existing archival object via api and saves a back up, and updates the object with a link to the relevant top container.

# Notes
| Date | Highlight | Notes |
| ---- | --------- | ----- |
| 01/15/2026 | Ticket Submitted | Ticket was submitted to ServiceNow |
| 03/02/2026 | Assigned | Ticket was assigned to Kylene |
| 03/02/2026 | Discussion | Kylene and Meg discussed the issue over several days and what the options were before settling on the method and creating the relevant csv |
| 03/10/2026 | Code | Initial Python code was created and tested on a small selection in Test. Asked for Meg's review. |
| 03/26/2026 | Communication | Meg requested something but I did not understand what she meant. We went back and forth on this for a month due to delays between her responses before we met over Zoom and we realized I had already done what was asked. | 
| 03/31/2026 | Testing | A full test in Test environment was performed. |
| 04/28/2026 | Hold | Meg would submit a new ticket for this job when YCBA was ready. |
| 05/08/2026 | Ticket Submitted | New ticket was submitted to ServiceNow. |
| 05/11/2026 | Assigned | Ticket was assigned to Kylene |
| 05/11/2026 | Discussion | Clarified with Meg that she wanted what was done in test in production. |
| 05/14/2026 | Update | Ran the process in production and had Meg review the results. She asked for a change to be made to how top containers were created. |
| 05/14/2026 | Update | Deleted the previously made top containers and reran the process with the change to top containers made. |
| 05/20/206 | Complete | Meg approved the final update and the ticket was closed. |

# Review
## Communication
| Name | Position | Notes |
| --- | --- | --- |
| Meg Rinn | Archivist, YCBA | Submitted Ticket, Clarified Details, Approved Results. |
## Results
Archival Objects were sucessfully updated in production. A change in the process was made after it was run in production which mean top containers did need to be deleted before the process ran again.

