# Expired Access Notes Report
Last updated on 07/08/2025 by Kylene Hutchinson.

| Start Date | End Date | Contributors | Informed Stakeholders |
| ---------- | -------- | ------------ | --------------------- |
| 11/19/2024 | 07/08/2025 | Kylene Hutchinson | Alicia Detelich, Michael Lotstein |

# Overview
## Problem Statement
Access restriction Notes in ArchivesSpace eventually expire and traditionally Alicia would run a report for archivists to review and manually make changes to. There was a request for this report to be run by users in ArchivesSpace on demand.
## Goals
- Create a custom report in ArchivesSpace 
    - Search specific dates
    - Search certain keywords in call numbers
# Background
This project took almost a year to complete due to complex issues involving setting up a development environment, changes in equipment, and needing a second tester to do the same. As a result it sat on the backburner for quite some time despite the actual code being written.

# Process
See [expired_access_notes.rb](expired_access_notes.rb), [en.yml](en.yml)
- Create a ruby script for the model that querys the SQL database and adds in parameters
    - Include to and from date parameters that allow a user to search before or after dates or in a range of dates
    - Allow for keyword searching of the call numbers
    - Edit the Identifier array into something usable in csv format using json extracts and concat
- Update the en.yml with new report info.
- Submit a pull request to YaleArchivesSpace:add_report

# Notes
| Date | Highlight | Notes |
| ---- | --------- | ----- |
| 11/19/2024 | Report | Submitted a excel sheet of expired notes to Michael Lotstein |
| 11/21/2024 | Report | submitted excel sheets for other repositories to Scott Libson, Adrienne Pruitt, Stephen Naron, and Megan Rinn|
| 11/22/2024 | Dev Environment Setup | Began trying to set up a local development of ArchivesSpace on my device |
| 01/27/2025 | Dev Environment Setup | Indexing finally completed and a local dev envrionment is set up on my device |
| 02/04/2025 | Review Request | Asked Alicia to review the ruby script when it failed to export properly as a csv, but suceeded in all other formats. |
| 07/07/2025 | Resumed diagnosing | After a long break I resumed trying to identify the issue. |
| 07/08/2025 | Submitted | Was able to identify and fix the issue. Submitted a pull request on github.|

# Review
## Communication
| Name | Position | Notes |
| ---- | -------- | ----- |
| Alicia Detelich  | Assistant Director of Special Collection Metadata Services, Special Collections Technical Services | Assigned Project |
| Michael Lotstein |  University Archivist | Requested Report Tool |
| Scott Libson | Special Collections Librarian, Divinity School | Given expired notes to review |
| Adrienne Pruitt | Archivist, Arts Library Special Collections | Given expired notes to review |
| Stephen Naron | Director of the Fortunoff Video Archive | Given expired notes to review |
| Megan Rinn | Archivist for Yale Center for British Art | Given expired notes to review |

## Results
Submitted custom report to YaleArchivesSpace:add_report in a pull request.

# References

- List of relevant links
