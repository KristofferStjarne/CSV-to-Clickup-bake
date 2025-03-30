import csv
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

SOURCE_CSV = os.getenv("SOURCE_CSV", "source.csv")
DEST_CSV = os.getenv("DEST_CSV", "clickup_ready.csv")

# Final cleaned headers (no "drop down", "text", "url", "users", "number", etc.)
target_headers = [
    "Task Name",
    "Priority",
    "ID",
    "Assignee",
    "Responsible Resource",
    "Start Date",
    "Sprints",
    "Due Date",
    "Comment Count",
    "Dependencies",
    "Stream",
    "SH Fundamental",
    "LC Phase",
    "Aimed Outcome",
    "Link to Deliverable",
    "Topic",
    "Topic NEW",
    "Guidance",
    "Lists",
    "Outcome old",
    "Work Streams LAN",
    "Description"
]

# Mapping from target -> source (None = leave blank)
column_mapping = {
    "Task Name": "Activity",
    "Priority": None,
    "ID": "ID",
    "Assignee": None,
    "Responsible Resource": None,
    "Start Date": None,
    "Sprints": None,
    "Due Date": None,
    "Comment Count": None,
    "Dependencies": None,
    "Stream": "Stream",
    "SH Fundamental": "Fundamental?",
    "LC Phase": "LC Phase",
    "Aimed Outcome": "Outcome",
    "Link to Deliverable": None,
    "Topic": "Topic",
    "Topic NEW": "Topic_NEW",
    "Guidance": "Guidance",
    "Lists": None,
    "Outcome old": None,
    "Work Streams LAN": "Stream",
    "Description": "Description"
}

def transform_csv(source_path, dest_path):
    with open(source_path, mode='r', encoding='utf-8-sig') as infile, \
         open(dest_path, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=target_headers)
        writer.writeheader()

        for row in reader:
            # Get and clean LC Phase
            raw_lc_phase = row.get("LC Phase", "")
            lc_phases = []

            if raw_lc_phase.startswith("[") and raw_lc_phase.endswith("]"):
                # Handle list format
                cleaned = raw_lc_phase.strip("[]")
                lc_phases = [p.strip().strip('"').strip("'") for p in cleaned.split(",") if p.strip()]
            else:
                # Single value
                lc_phases = [raw_lc_phase.strip()]

            for phase in lc_phases:
                new_row = {}
                for target_col in target_headers:
                    source_col = column_mapping.get(target_col)
                    if source_col:
                        value = row.get(source_col, "").strip()
                        if source_col == "LC Phase":
                            new_row[target_col] = phase
                        else:
                            new_row[target_col] = value
                    else:
                        new_row[target_col] = ""
                writer.writerow(new_row)

    print(f"✅ Transformation complete! Output written to '{dest_path}'")

if __name__ == "__main__":
    transform_csv(SOURCE_CSV, DEST_CSV)