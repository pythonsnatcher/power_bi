import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

API_KEY     = os.getenv("API_FOOTBALL_KEY")
if not API_KEY:
    raise ValueError("Please set API_FOOTBALL_KEY in your .env file.")

FIXTURE_FILE = os.getenv("FIXTURE_FILE", "data/fixture_dim.csv")
OUTPUT_DIR   = os.getenv("OUTPUT_DIR", "../data")
OUTPUT_FILE  = os.path.join(OUTPUT_DIR, "statistics_dim.csv")

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

# Read fixture IDs
if not os.path.exists(FIXTURE_FILE):
    raise FileNotFoundError(f"{FIXTURE_FILE} not found.")

fixtures_df = pd.read_csv(FIXTURE_FILE)
fixture_ids = fixtures_df["FixtureID"].dropna().astype(int).tolist()

print(f"📋 Found {len(fixture_ids)} fixtures")

rows = []
for fixture_id in fixture_ids:
    try:
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
        params = {"fixture": fixture_id}
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        time.sleep(1)

        stat_data = resp.json().get("response", [])
        for team_stats in stat_data:
            team_id = team_stats["team"]["id"]
            stats = team_stats["statistics"]
            time.sleep(1)

            row = {"FixtureID": fixture_id, "TeamID": team_id}
            for stat in stats:
                key = stat["type"].replace(" ", "_").replace("%", "Percent")
                row[key] = stat["value"]
                time.sleep(1)
            rows.append(row)
        print(f"✔️ Fetched stats for fixture {fixture_id}")

    except Exception as e:
        print(f"⚠️ Skipped fixture {fixture_id} due to error: {e}")

df_new = pd.DataFrame(rows)

# Deduplicate and merge with existing data
def row_to_tuple(row):
    return tuple(row[col] if col in row else None for col in sorted(row.keys()))

new_set = set(row_to_tuple(row) for _, row in df_new.iterrows())

existing_set = set()
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    existing_set = set(row_to_tuple(row) for _, row in df_existing.iterrows())

combined_set = existing_set.union(new_set)
all_columns = sorted({key for row in rows for key in row.keys()} | {"FixtureID", "TeamID"})
df_combined = pd.DataFrame([dict(zip(all_columns, t)) for t in combined_set], columns=all_columns)

df_combined.sort_values(by=["FixtureID", "TeamID"], inplace=True)

# Save or display
print("\nOptions:\n1. Display all rows\n2. Save to CSV")
choice = 2

if choice == 1:
    print(df_combined)
elif choice == 2:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_combined.to_csv(OUTPUT_FILE, index=False)
    print(f"📁 Saved to {OUTPUT_FILE}")
else:
    print("❌ Invalid choice.")
