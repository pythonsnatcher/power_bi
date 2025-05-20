import sqlite3
import pandas as pd
import os

# Folder with CSVs
DATA_FOLDER = "data"
DB_NAME = "football_data.sqlite"

# Inference function for SQL types
def infer_sql_type(series):
    if pd.api.types.is_integer_dtype(series):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(series):
        return "REAL"
    else:
        return "TEXT"

# Connect to the SQLite DB
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Process each CSV file
for filename in os.listdir(DATA_FOLDER):
    if filename.endswith(".csv"):
        table_name = os.path.splitext(filename)[0]
        file_path = os.path.join(DATA_FOLDER, filename)
        print(f"\n📄 Processing {filename} -> table: {table_name}")

        # Read the CSV
        df = pd.read_csv(file_path)

        # Drop table if it exists
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"Dropped table {table_name}")

        # Create table based on inferred schema
        col_defs = []
        for col in df.columns:
            sql_type = infer_sql_type(df[col])
            col_defs.append(f'"{col}" {sql_type}')
        create_stmt = f"CREATE TABLE {table_name} ({', '.join(col_defs)});"
        cursor.execute(create_stmt)
        print(f"✅ Created table: {table_name}")

        # Insert data
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"📥 Inserted {len(df)} rows into {table_name}")

# Finish
conn.commit()
conn.close()
print(f"\n✅ All tables inserted into {DB_NAME}")
