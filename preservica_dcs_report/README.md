# Preservica DCS Report
Last updated on 12/16/2025 by Kylene Hutchinson.

| Start Date | End Date | Contributors | Informed Stakeholders |
| ---------- | -------- | ------------ | --------------------- |
| 07/30/2025 | 12/15/2025 | Kylene Hutchinson | Anu Paul |

# Overview
## Problem Statement
Create a unique report that can be used to identify archival objects that have a DCS digital object without a Preservica object and vice versa.
## Goals
- Create a reusable Archives Space Report that identifies digital object counts based on their file url
- Add the ability to filter by call number
- Include Archives at Yale url, the archival object uri, and the Collection Title and container statement.
# Background
All DCS items are required to all have a preservica link. This report is intended to allow DSCA to better identify archival objects missing one of the two objects.
Digital Special Collections and Access (DSCA) was previously using "translation missing:reports.preservica_access_requests" report but needs something more specific.


# Process
See [en.yml](en.yml) and [preservica_dcs_report.rb](preservica_dcs_report.rb)

- Write SQL code that returns Archives at Yale url, Repository name and id, Collection Title, container statement (e.g. 'Box 3'), call number, Archival Object Title, counts of Preservica, DCS, and Aviary digital objects attached to the archival object, A list of Digital Object titles and uris, and Archival Object Uri.
- Add parameters that allow for the user to restrict by call number or not.
- Add to front end's en.yml

# Notes
| Date | Highlight | Notes |
| ---- | --------- | ----- |
| 07/30/2025 | Requested | Request Received by ServiceNow |
| 08/12/2025 | Assigned | Request Assigned to Kylene |
| 09/30/2025 | Review | Submitted example report for review to Anu |
| 11/06/2025 | Follow Up | Contacted Anu about the Example Report and she asked to meet |
| 11/14/2025 | Meeting | Met with Anu to discuss the report and what exactly she would like to be in the report |
| 11/19/2025 | Review | Sent an updated version of the example report |
| 12/03/2025 | Review | Anu and I discussed some more details about the report |
| 12/15/2025 | Review | Submitted updated examples to match Anu's specifications. She gave the go ahead to push to test. |

# Review

## Communication
| Name             | Position                                                           | Notes                                                                                                       |
| ---------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| Anu Paul         | Associate Director for Digital Content Services, Digital Special Collections and Access | Requested and reviewed reports. |
## Results
Report was approved and pushed for the next update.