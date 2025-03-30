import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


print("📦 All loaded env variables:")
for k, v in os.environ.items():
    if "FILTER" in k.upper():
        print(f"{k} = {v}")

SOURCE_CSV = os.getenv("SOURCE_CSV", "source.csv")
DEST_CSV = os.getenv("DEST_CSV", "clickup_ready.csv")
RELEASE_FILTER = os.getenv("RELEASE_FILTER", "all").lower().strip()

# Validate RELEASE_FILTER value
if RELEASE_FILTER not in ("released", "all"):
    raise ValueError(f"❌ Invalid RELEASE_FILTER in .env: '{RELEASE_FILTER}'. Use 'released' or 'all'.")

print(f"🔧 RELEASE_FILTER is set to: '{RELEASE_FILTER}'")

# Optional: toggle for debug output
DEBUG = True

# Target headers for ClickUp CSV
target_headers = [
    "Task Name", "Priority", "ID", "Assignee", "Responsible Resource",
    "Start Date", "Sprints", "Due Date", "Comment Count", "Dependencies",
    "Stream", "SH Fundamental", "LC Phase", "Aimed Outcome", "Link to Deliverable",
    "Topic", "Topic NEW", "Guidance", "Lists", "Outcome old",
    "Work Streams LAN", "Description"
]

# Mapping: output column -> input column (or None if blank)
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

def is_released(status: str) -> bool:
    """Normalize and check if status equals 'released'."""
    cleaned = status.strip().strip('"[]\'').lower()
    if DEBUG:
        print(f"🔍 Checking Release Status: raw='{status}' → normalized='{cleaned}'")
    return cleaned == "released"

def transform_csv(source_path, dest_path):
    skipped_path = "skipped_rows.csv"

    with open(source_path, mode='r', encoding='utf-8-sig') as infile, \
         open(dest_path, mode='w', newline='', encoding='utf-8') as outfile, \
         open(skipped_path, mode='w', newline='', encoding='utf-8') as skipfile:

        reader = csv.DictReader(infile, quotechar='"')
        reader.fieldnames = [f.strip().strip('"') for f in reader.fieldnames]
        writer = csv.DictWriter(outfile, fieldnames=target_headers)
        writer.writeheader()
        skip_writer = csv.DictWriter(skipfile, fieldnames=reader.fieldnames)
        skip_writer.writeheader()

        for row in reader:
            row = {k.strip().strip('"'): v.strip() for k, v in row.items()}
            release_status = row.get("Release Status", "")
            row_id = row.get("ID", "N/A")

            if DEBUG:
                print(f"\n🧾 Row ID {row_id} - Raw Release Status: '{release_status}'")

            if RELEASE_FILTER == "released" and not is_released(release_status):
                if DEBUG:
                    print("⛔ Skipping (not released)")
                skip_writer.writerow(row)
                continue

            raw_lc_phase = row.get("LC Phase", "")
            if raw_lc_phase.startswith("[") and raw_lc_phase.endswith("]"):
                cleaned = raw_lc_phase.strip("[]")
                lc_phases = [p.strip().strip('"').strip("'") for p in cleaned.split(",") if p.strip()]
            else:
                lc_phases = [raw_lc_phase.strip()] if raw_lc_phase.strip() else [""]

            for phase in lc_phases:
                new_row = {}
                for target_col in target_headers:
                    source_col = column_mapping.get(target_col)
                    if source_col:
                        value = row.get(source_col, "")
                        new_row[target_col] = phase if source_col == "LC Phase" else value
                    else:
                        new_row[target_col] = ""
                writer.writerow(new_row)
                if DEBUG:
                    print(f"✅ Writing row for LC Phase: '{phase}'")

    print(f"\n✅ Done! Output: {dest_path}")
    print(f"📤 Skipped rows (not released): {skipped_path}")

if __name__ == "__main__":
    transform_csv(SOURCE_CSV, DEST_CSV)