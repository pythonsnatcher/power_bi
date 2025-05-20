import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "../data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "player_dim.csv")

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

LEAGUE_ID = 10  # Change as needed
SEASON = 2025

players = []

# API endpoint: /players?league={league}&season={season}
url = f"https://api-football-v1.p.rapidapi.com/v3/players"
params = {"league": LEAGUE_ID, "season": SEASON}

response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json().get("response", [])

for entry in data:
    player_info = entry.get("player", {})
    stats = entry.get("statistics")[0] if entry.get("statistics") else {}

    team_info = stats.get("team", {}) if stats else {}

    players.append({
        "PlayerID": player_info.get("id"),
        "PlayerName": player_info.get("name"),
        "TeamID": team_info.get("id"),
        "Nationality": player_info.get("nationality"),
        "Position": stats.get("games", {}).get("position") if stats else None,
        "DateOfBirth": player_info.get("birth", {}).get("date") if player_info.get("birth") else None,
        "Height": player_info.get("height"),
        "Weight": player_info.get("weight"),
    })

df_new = pd.DataFrame(players)
print(f"\n✔️ Fetched {len(df_new)} players from API.")

# Deduplication helper function (convert row to tuple)
def row_to_tuple(row):
    keys = ["PlayerID", "PlayerName", "TeamID", "Nationality", "Position", "DateOfBirth", "Height", "Weight"]
    return tuple(row[key] if key in row else None for key in keys)

new_set = set(row_to_tuple(row) for _, row in df_new.iterrows())

# Load existing players if file exists
existing_set = set()
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    existing_set = set(row_to_tuple(row) for _, row in df_existing.iterrows())

# Combine sets to deduplicate
combined_set = existing_set.union(new_set)

# Convert back to DataFrame
all_keys = ["PlayerID", "PlayerName", "TeamID", "Nationality", "Position", "DateOfBirth", "Height", "Weight"]
df_combined = pd.DataFrame([dict(zip(all_keys, t)) for t in combined_set], columns=all_keys)

# Sort by PlayerID for consistent ordering
df_combined.sort_values("PlayerID", inplace=True)

# User menu
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
