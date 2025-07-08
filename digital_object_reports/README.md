# TITLE
Last updated on 07/08/2025 by Kylene Hutchinson.

| Start Date | End Date | Contributors | Informed Stakeholders |
| ---------- | -------- | ------------ | --------------------- |
| 05/30/2025 | 07/08/2025 | Kylene Hutchinson | Stephen Goeman |

# Overview
## Problem Statement
We need to be able to identify digital objects with URL's that indicate that it is a photo negative. The existing reports in ArchivesSpace do not return digital object urls.

## Goals
- Create a Report that display's the Digital Object's URL.
- Make said report usable in ArchivesSpace's reports.
- Clean up old Vufind Objects

# Background
A long time ago, Beinecke staff created photonegs of collection material and mailed them to requesting patrons—these were some of our earliest facsimiles. The decision was made to not migrate these photonegs to DCS as they are not preservation-quality images. However, some of these photonegs were attached to finding aids.


# Process
See [digital_object_report.sql](digital_object_report.sql), [digital_object_links_report.rb](digital_object_links_report.rb), [en.yml](en.yml), [_oid.html.erb](_oid.html.erb), [_parent.html.erb](_parent.html.erb), and [_url.html.erb](_url.html.erb)
- Write [SQL query](digital_object_report.sql) to pull Digital Objects with file URLs
    - Create CSV file and submit to DCSA for review
- Delete necessary digital objects
- Write ArchivesSpace Report in ruby
    - Create [model report](digital_object_links_report.rb)
    - Add necessary paramaters ([oid](_oid.html.erb), [parent id](_parent.html.erb), and [url](_url.html.erb)) to report to allow for more robust querying from users.
    - Update [en.yml](en.yml)

# Notes
| Date | Highlight | Notes |
| ---- | --------- | ----- |
| 06/09/2025 | Assigned | Alicia assigned the project in Service Now |
| 06/23/2025 | Contact | Reached out to Stephen for clearer details on what he was looking for in a report. |
| 06/23/2025 | Sent File | Since writing a report in ArchivesSpace was secondary to Stephen's current project, I wrote a SQL query and created a csv report and submitted it to Stephen. Stephen was having issues accessing the Service Now Ticket so we continued communication in Teams and Outlook. |
| 06/25/2025 | Updated Request | Stephen reviewed the report and was able to identify 16 digital objects that needed deleting. |
| 06/26/2025 | Test Deletion | The 16 objects were deleted in the test environment. |
| 07/01/2025 | Deletion | The 16 objects were deleted in the production environment. |
| 07/01/2025 | Report Creation | The Report was written for ArchivesSpace integration. Testing in the development environment to follow. |
| 07/07/2025 | Testing | Tested Report in development environment |
| 07/08/2025 | Submitted | Submitted custom report pull request in github. |

# Review

## Data Details
 - 16 digital objects with vufind URLs identified.
    - 8 of which were orphaned digital objects, not attached to any archival object or resource.

## Communication
| Name | Position | Notes |
| ---- | -------- | ----- |
| Alicia Detelich  | Assistant Director of Special Collection Metadata Services, Special Collections Technical Services | Assigned Project |
| Stephen Goeman |  Digital Production Manager, Digital Special Collections and Access Department, Beinecke Library | Requested Report Tool |

## Results
- Report sent to Stephen Goeman was approved
- Deleted 16 digital objects identified by Stephen Goeman
- Created Report Tool for Digital Objects in ArchviesSpace, submitted to be added in future update.

# References

- [ServiceNow ticket](https://yale.service-now.com/it?id=it_ticket&table=sc_req_item&sys_id=86947f4293b5a29026f5bbcd1dba1093)
