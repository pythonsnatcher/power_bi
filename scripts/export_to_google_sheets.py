import sqlite3
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
import requests
import tempfile

# --- Path to your downloaded credentials JSON ---
credentials_path = "/Users/snatch/PycharmProjects/power_bi_project/2_0/data/client_secret_141496264794-p7g2i6j81m5jagj70ig75e47b29ju5j0.apps.googleusercontent.com.json"

# --- Authenticate using the credentials file ---
gc = gspread.oauth(
    credentials_filename=credentials_path,
    authorized_user_filename="/Users/snatch/PycharmProjects/power_bi_project/2_0/data/authorized_user.json"
)

# --- Open spreadsheet by URL ---
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1fGHvWjDl8dR9JaRn0tes84BRbguJMGaHLrhhj4iJFmo/edit?usp=sharing")

# --- Delete all worksheets except the first ---
worksheets = spreadsheet.worksheets()
for ws in worksheets[1:]:
    spreadsheet.del_worksheet(ws)

# --- Load SQLite from GitHub (without saving to disk) ---
sqlite_url = "https://github.com/pythonsnatcher/power_bi/raw/main/football_data.sqlite"
response = requests.get(sqlite_url)
sqlite_bytes = response.content

with tempfile.NamedTemporaryFile(delete=False) as tmp:
    tmp.write(sqlite_bytes)
    tmp_path = tmp.name

conn = sqlite3.connect(tmp_path)

# --- Get all tables ---
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

# --- Export first table to existing first worksheet ---
first_table = tables[0]
df = pd.read_sql_query(f"SELECT * FROM {first_table}", conn)
first_ws = worksheets[0]
first_ws.clear()
first_ws.update_title(first_table[:100])
set_with_dataframe(first_ws, df)

# --- Export remaining tables to new worksheets ---
for table in tables[1:]:
    print(f"Exporting {table}...")
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    new_ws = spreadsheet.add_worksheet(title=table[:100], rows=max(len(df)+10, 100), cols=max(len(df.columns)+5, 20))
    set_with_dataframe(new_ws, df)

print("✅ All tables exported to Google Sheets.")
