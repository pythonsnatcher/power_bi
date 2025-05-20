import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")
if not API_KEY:
    raise ValueError("Please set API_FOOTBALL_KEY in your .env file.")

# Hardcoded variables
SEASON = 2025
LEAGUE_ID = 351
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "fixture_dim.csv")

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}
PARAMS = {
    "season": SEASON,
    "league": LEAGUE_ID
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fetch data from API
resp = requests.get("https://api-football-v1.p.rapidapi.com/v3/fixtures",
                    headers=HEADERS, params=PARAMS)
resp.raise_for_status()
payload = resp.json().get("response", [])

rows = []
for entry in payload:
    fixture = entry.get("fixture", {})
    league = entry.get("league", {})
    teams = entry.get("teams", {})

    rows.append({
        "FixtureID": fixture.get("id"),
        "Date": fixture.get("date"),
        "Timestamp": fixture.get("timestamp"),
        "VenueID": fixture.get("venue", {}).get("id"),
        "HomeTeamID": teams.get("home", {}).get("id"),
        "AwayTeamID": teams.get("away", {}).get("id"),
        "Status": fixture.get("status", {}).get("short"),
        "Round": league.get("round"),
        "LeagueID": league.get("id"),
        "Season": league.get("season")
    })

df_new = pd.DataFrame(rows)
print(f"\n✔️ Fetched {len(df_new)} fixtures.")

# Deduplication helper function
def row_to_tuple(row):
    keys = ["FixtureID", "Date", "Timestamp", "VenueID", "HomeTeamID", "AwayTeamID",
            "Status", "Round", "LeagueID", "Season"]
    return tuple(row[key] if key in row else None for key in keys)

new_set = set(row_to_tuple(row) for _, row in df_new.iterrows())

# Load existing data if exists
existing_set = set()
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    existing_set = set(row_to_tuple(row) for _, row in df_existing.iterrows())

# Combine sets to deduplicate
combined_set = existing_set.union(new_set)

# Convert back to DataFrame
all_keys = ["FixtureID", "Date", "Timestamp", "VenueID", "HomeTeamID", "AwayTeamID",
            "Status", "Round", "LeagueID", "Season"]
df_combined = pd.DataFrame([dict(zip(all_keys, t)) for t in combined_set], columns=all_keys)

# Sort by FixtureID for consistent order
df_combined.sort_values("FixtureID", inplace=True)

# User menu
print("\nOptions:\n1. Display top 100 rows\n2. Save to CSV")
#choice = input("Enter choice (1 or 2): ")
choice = "2"


if choice == "1":
    print(df_combined.head(100))
elif choice == "2":
    df_combined.to_csv(OUTPUT_FILE, index=False)
    print(f"📁 Saved to {OUTPUT_FILE}")
else:
    print("❌ Invalid choice.")
