# TREC Monthly Data Processing Workflow

This document outlines the standard operating procedure for processing the monthly TREC (Texas Real Estate Commission) license holder data to update Jointly's growth profiles.

## 1. System Rules & Logic
To maintain data integrity, the following rules must be applied during every update:
- **Filtering:** Focus exclusively on "Broker Company" entities with an "Active" status.
- **Agent Attribution:** Calculate "Active Sales Agent" counts by mapping the agent's `Related License Number` to the broker's `License Number`. 
- **Monthly Snapshot:** Always label the agent count with the current month and year (e.g., "March 2026").
- **Targeting:** For individual Markdown profiles, only process brokerages with **5 to 10 active agents**.
- **Organization:** Store profiles in `00.companies/brokerages/profiles/profiles-tier-[1|3]/[A-Z]/` using slugified filenames.

## 2. Monthly Execution Prompt
When a new CSV is received (e.g., `Broker_and_Sales_Agent_License_Holder_Information_20260405.csv`), provide the following directive to the AI:

> **TREC Data Update Directive:**
> 1. Process the new CSV at `@00.companies/brokerages/source/trec/[NEW_FILENAME].csv`.
> 2. Update the master summary CSV: `@00.companies/brokerages/output/summaries/active_broker_companies_profile_[YYYYMMDD].csv`.
> 3. Update/Create individual Markdown profiles in `@00.companies/brokerages/profiles/profiles-tier-1/` or `@00.companies/brokerages/profiles/profiles-tier-3/` for all companies with **5 to 10 active agents**.
> 4. Use the month and year from the filename for the agent count label (e.g., "April 2026").
> 5. **Preserve Research Notes:** If a Markdown file already exists, do NOT overwrite the `Research Notes` section; only update the `Broker Company Profile` and `Sales Force` statistics.

## 3. Automation Script Logic (Python)
The following script logic is used to perform the extraction and file generation:

```python
import csv
import os
import re
from collections import defaultdict

input_file = "00.companies/brokerages/source/trec/Broker_and_Sales_Agent_License_Holder_Information_20260305.csv"
base_dir = "00.companies/brokerages/profiles/profiles-tier-3" # Or profiles-tier-1

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

# 1. Count active agents per broker
agent_counts = defaultdict(int)
with open(input_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["Status"] == "Active" and row["License Type"] == "Sales Agent":
            broker_license = row["Related License Number"]
            if broker_license:
                agent_counts[broker_license] += 1

# 2. Extract active broker companies and update profiles
with open(input_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["Status"] == "Active" and row["License Type"] == "Broker Company":
            agents = agent_counts.get(row["License Number"], 0)
            if 5 <= agents <= 10:
                name = row["Full Name"].strip() or ("Unknown Broker " + row["License Number"])
                
                # Alphabetical Subfolder
                first_char = name[0].upper() if name[0].isalpha() else "0-9"
                target_dir = os.path.join(base_dir, first_char)
                if not os.path.exists(target_dir): os.makedirs(target_dir)
                
                file_path = os.path.join(target_dir, f"{slugify(name)}.md")
                
                # Logic to preserve Research Notes would go here (reading existing file)
                # ...
```
