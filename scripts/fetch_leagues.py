from dotenv import load_dotenv
import os
import requests
import pandas as pd

# Load .env
load_dotenv()

API_KEY     = os.getenv("API_FOOTBALL_KEY")
if not API_KEY:
    raise ValueError("Please set API_FOOTBALL_KEY in your .env file.")

SEASON      = int(os.getenv("FOOTBALL_SEASON", "2025"))
OUTPUT_DIR  = os.getenv("OUTPUT_DIR", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "league_dim.csv")

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}
PARAMS = {"season": SEASON}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fetch and normalize
resp = requests.get("https://api-football-v1.p.rapidapi.com/v3/leagues",
                    headers=HEADERS, params=PARAMS)
resp.raise_for_status()
payload = resp.json().get("response", [])

rows = []
for entry in payload:
    league = entry["league"]
    rows.append({
        "LeagueID":   league["id"],
        "LeagueName": league["name"],
        "Season":     SEASON
    })

# Save minimal dimension
pd.DataFrame(rows).to_csv(OUTPUT_FILE, index=False)
print(f"Saved {len(rows)} leagues → {OUTPUT_FILE}")
