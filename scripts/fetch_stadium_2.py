import os
import requests
import pandas as pd
from dotenv import load_dotenv

from other.fetch_team import choice

load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "../data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "stadium_dim.csv")

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

LEAGUE_ID = 351
SEASON = 2025

url = f"https://api-football-v1.p.rapidapi.com/v3/teams?league={LEAGUE_ID}&season={SEASON}"
response = requests.get(url, headers=headers)
response.raise_for_status()
data = response.json()

# Collect new stadiums from API
stadiums = []
for team_entry in data.get("response", []):
    venue = team_entry.get("venue", {})
    if venue and venue.get("id") is not None:
        stadiums.append({
            "VenueID": venue.get("id"),
            "Name": venue.get("name"),
            "City": venue.get("city"),
            "Capacity": venue.get("capacity"),
            "Surface": venue.get("surface"),
            "Address": venue.get("address")
        })

df_new = pd.DataFrame(stadiums)
print(f"\n✔️ Fetched {len(df_new)} stadiums from API.")

# Deduplication helper function (convert rows to tuples for set comparison)
def row_to_tuple(row):
    keys = ["VenueID", "Name", "City", "Capacity", "Surface", "Address"]
    return tuple(row[key] if key in row else None for key in keys)

new_set = set(row_to_tuple(row) for _, row in df_new.iterrows())

# Load existing stadium data if any
existing_set = set()
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    existing_set = set(row_to_tuple(row) for _, row in df_existing.iterrows())

# Combine and deduplicate
combined_set = existing_set.union(new_set)

# Convert back to DataFrame
all_keys = ["VenueID", "Name", "City", "Capacity", "Surface", "Address"]
df_combined = pd.DataFrame([dict(zip(all_keys, t)) for t in combined_set], columns=all_keys)

# Sort by VenueID for consistent ordering
df_combined.sort_values("VenueID", inplace=True)

# User menu
print("\nOptions:\n1. Display top 100 rows\n2. Save to CSV\n")

choice = "2"

if choice == "1":
    print(df_combined.head(100))
elif choice == "2":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_combined.to_csv(OUTPUT_FILE, index=False)
    print(f"📁 Data saved to {OUTPUT_FILE}")
else:
    print("❌ Invalid choice.")
