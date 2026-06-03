# Goobi Export Report
Last updated on [DATE] by [NAME].

| Start Date | End Date | Contributors | Informed Stakeholders |
| ---------- | -------- | ------------ | --------------------- |
| 03/26/2026 | 04/14/2026 | Kylene Hutchinson | Stephen Goeman |

# Overview
## Problem Statement
Not all of the instances were appearing in a Goobi Export report. DSCA has requested a Goobi Export type report that includes the missing slides.
## Goals
- Include all of the typical data from the Goobi Export (aspace_uri; refID; callNumber; container(Box); the missing slide number; item_barcode; hostTitle; hostDate; sourceNote; title; date; physDesc; note; abstract; aspace_barcode; pubType; collection; useOPAC; opacName; yaleRestriction; yaleUse; yaleOwner; extentDigitization; digitizationNote)
- Ensure the missing instances are being added to the report.
# Background
Was able to pull the Goobi report ruby code to figure out what the issue was and adapt it to SQL. Turns out the instances were only looking for those with a folder type so the slides were being skipped. Was able to fix that in the SQL. Also fixed the breadcrumbs issue in the sourceNote and removed any unnecessary fields (many fields were set to always return NULL).

# Process
See [report.sql](report.sql).
- Run [report.sql](report.sql).

# Notes
| Date | Highlight | Notes |
| ---- | --------- | ----- |
| 03/26/2026 | Submitted | Ticket submitted to ServiceNow |
| 04/13/2026 | Assigned | Ticket assigned to Kylene |
| 04/14/2026 | Completed | Report Submitted and Approved |

# Review

## Communication
| Name | Position | Notes |
| --- | --- | --- |
| Stepehen Goeman | Digital Production Manager, DSCA | Submitted Ticket, Approved Results |
## Results
Report completed without incident.

