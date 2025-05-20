import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")
OUTPUT_DIR  = os.getenv("OUTPUT_DIR", "../data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "team_dim.csv")

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

# Define league and season
LEAGUE_ID = 351  # Premier League (change as needed)
SEASON = 2024

# Fetch from API
url = f"https://api-football-v1.p.rapidapi.com/v3/teams?league={LEAGUE_ID}&season={SEASON}"
response = requests.get(url, headers=headers)
response.raise_for_status()
data = response.json()

# Extract team data
new_rows = []
for team_entry in data.get("response", []):
    team_info = team_entry.get("team", {})
    new_rows.append({
        "TeamID":    team_info.get("id"),
        "TeamName":  team_info.get("name"),
        "ShortName": team_info.get("code"),
        "Country":   team_info.get("country"),
        "Founded":   team_info.get("founded"),
        "National":  team_info.get("national")
    })

# Convert new rows to set
new_set = set(tuple(row.values()) for row in new_rows)

# Load existing data if present
existing_set = set()
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    existing_set = set(tuple(row) for row in df_existing[
        ["TeamID", "TeamName", "ShortName", "Country", "Founded", "National"]
    ].to_records(index=False))

# Combine both sets to remove duplicates
combined_set = existing_set.union(new_set)

# Create DataFrame from combined set
columns = ["TeamID", "TeamName", "ShortName", "Country", "Founded", "National"]
df_combined = pd.DataFrame(list(combined_set), columns=columns)

# Create UUID column (Country_TeamID)
df_combined["UUID"] = df_combined.apply(
    lambda row: f"{row['Country']}_{row['TeamID']}", axis=1
)

# Sort by TeamID
df_combined.sort_values("TeamID", inplace=True)

print(f"\n✔️ Fetched {len(new_set)} new teams.")
print(f"📁 Merged and deduplicated {len(combined_set)} total records.")

# Menu
print("\nOptions:\n1. Display top 100 rows\n2. Save to CSV\n")
choice = input("Enter choice (1 or 2): ")

if choice == "1":
    print(df_combined.head(100))
elif choice == "2":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_combined.to_csv(OUTPUT_FILE, index=False)
    print(f"📁 Data saved to {OUTPUT_FILE}")
else:
    print("❌ Invalid choice.")
