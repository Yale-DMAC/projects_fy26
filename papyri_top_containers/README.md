# Papyri Top Containers
Last updated on 08/14/2025 by Kylene Hutchinson.

| Start Date | End Date | Contributors | Informed Stakeholders |
| ---------- | -------- | ------------ | --------------------- |
| 07/22/2025 | 08/14/2025 | Kylene Hutchinson | Alicia Detelich |

# Overview
## Problem Statement
We were provided with a spreadsheet of information and asked to add top containers to existing archival objects.
## Goals
- Add restriction notes to archival objects as needed
- Create Top containers and link them to the appropriate Archival Object
- Add locations to Top Containers as needed

# Process
See [papyri_topcontainers.py](papyri_topcontainers.py), [250811_results.csv](250811_results.csv), [papyri_containers_and_restrictions.csv](papyri_containers_and_restrictions.csv)
- Read the CSV file and grab relevant columns from each row.
- Create a Top container if an identifier is provided, if blank then link the archival object to the previously created top container.
- Update Archival Object to attach top containers.
- Add restriction notes to top containers as needed.
- Manually create top containers for the one object that had 3 top container identifiers. Easier to do this manually for the single row than alter the code to account for it.

# Notes
| Date | Highlight | Notes |
| ---- | --------- | ----- |
| 07/22/2025 | Assigned | Project was assigned in Service Now |
| 08/05/2025 | Reviewed | Reviewed the project and began working on code. |
| 08/07/2025 | Tested | Did a test run in the test environment and spent the next few days spot checking for flaws |
| 08/11/2025 | Production | Ran in production and began spot checking. |
| 08/14/2025 | Manual | Manually added the one row with 3 top containers. |

# Review

## Data Details
- 6,911 records that need updating
- 6,239 top containers created
## Communication
| Name | Position | Notes |
| ---- | -------- | ----- |
| Alicia Detelich  | Assistant Director of Special Collection Metadata Services, Special Collections Technical Services | Assigned Project |
## Results
6,911 records updated successfully.
