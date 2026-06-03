# Divinity Adhoc Update
Last updated on 06/02/2026 by Kylene Hutchinson.

| Start Date | End Date | Contributors | Informed Stakeholders |
| ---------- | -------- | ------------ | --------------------- |
| 02/27/2026 | 03/31/2026 | Kylene Hutchinson | Scott Libson |

# Overview
## Problem Statement
Divinity Library had updated their adhoc url and needed to update digital objects in ArchivesSpace to reflect this.
## Goals
- Create a Report of all digital objects with the old adhoc url
- Update the urls to reflect the new url.
# Background
Originally the ticket only requested a report but after the report it was requested we update the urls in ArchivesSpace as well.

# Process
See [adhoc_report.sql](adhoc_report.sql), [divinity_adhoc.py](divinity_adhoc.py)
- Run [adhoc_report.sql](adhoc_report.sql) to get a list of all digital objects.
- Create a csv with the digital object uri, and the url update.
- Run [divinity_adhoc.py](divinity_adhoc.py) to update digital objects.

# Notes
| Date | Highlight | Notes |
| ---- | --------- | ----- |
| 02/27/2026 | Ticket Submitted | Ticket Submitted to ServiceNow |
| 03/05/2026 | Assigned | Ticket assigned to Kylene. |
| 03/05/2026 | Report | Ran the report and submitted it to the ticket for review. |
| 03/19/2026 | Communication | Checked in with Scott to ensure he saw the report. He had difficulty accessing it so I mailed it to him directly. |
| 03/25/2026 | Request | Scott requested we expand the scope of the ticket to update the identified digital objects. He edited the report to have a column for new urls. |
| 03/26/2026 | Code | Began coding python script to update urls. |
| 03/31/2026 | Complete | Updated the digital object urls to the new adhoc url and reviewed by Scott. |

# Review
## Communication
| Name | Position | Notes |
| --- | --- | --- |
| Scott Libson | Special Collection Librarian, Divinity Library | Submitted Ticket, Reviewed Results. |
## Results
Report created and digital objects updated with no incident.
