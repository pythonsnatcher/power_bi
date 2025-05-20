import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY     = os.getenv("API_FOOTBALL_KEY")
if not API_KEY:
    raise ValueError("Please set API_FOOTBALL_KEY in your .env file.")

FIXTURE_ID  = 1324901 # Change this in your .env
OUTPUT_DIR  = os.getenv("OUTPUT_DIR", "../data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "statistics_dim.csv")

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

# Fetch statistics for a single fixture
url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
params = {"fixture": FIXTURE_ID}

resp = requests.get(url, headers=HEADERS, params=params)
resp.raise_for_status()
stat_data = resp.json().get("response", [])

rows = []
for team_stats in stat_data:
    team_id = team_stats["team"]["id"]
    stats = team_stats["statistics"]

    row = {"FixtureID": FIXTURE_ID, "TeamID": team_id}
    for stat in stats:
        key = stat["type"].replace(" ", "_").replace("%", "Percent")
        row[key] = stat["value"]

    rows.append(row)

df_new = pd.DataFrame(rows)
print(f"\n✔️ Fetched {len(df_new)} statistics for fixture {FIXTURE_ID}")

# Prepare sets for deduplication
# Convert new rows to tuples (sorted keys for consistent ordering)
def row_to_tuple(row):
    # Sort keys to keep order consistent, then tuple of values
    return tuple(row[col] if col in row else None for col in sorted(row.keys()))

new_set = set(row_to_tuple(row) for _, row in df_new.iterrows())

# Load existing data if any
existing_set = set()
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    existing_set = set(row_to_tuple(row) for _, row in df_existing.iterrows())

# Combine and deduplicate
combined_set = existing_set.union(new_set)

# Rebuild DataFrame
all_columns = sorted({key for row in rows for key in row.keys()} | {"FixtureID", "TeamID"})
df_combined = pd.DataFrame([dict(zip(all_columns, t)) for t in combined_set], columns=all_columns)

# Sort by FixtureID then TeamID for readability
df_combined.sort_values(by=["FixtureID", "TeamID"], inplace=True)

# Menu
print("\nOptions:\n1. Display all rows\n2. Save to CSV")
choice = input("Enter choice (1 or 2): ")

if choice == "1":
    print(df_combined)
elif choice == "2":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_combined.to_csv(OUTPUT_FILE, index=False)
    print(f"📁 Saved to {OUTPUT_FILE}")
else:
    print("❌ Invalid choice.")
