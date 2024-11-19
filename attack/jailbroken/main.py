import pandas as pd
import sqlite3
import os
from pathlib import Path

# Get the directory of the current script
current_dir = Path(__file__).parent

# Define CSV file path as being in the same directory as this script
file_path = current_dir / 'data.csv'

# Define SQLite database path TODO DB path 没改
db_path = current_dir / 'attacks.db'

# Check if the CSV file exists
if not os.path.exists(file_path):
    print(f"The file {file_path} does not exist. Please check the path.")
else:
    # Read the CSV file
    try:
        data = pd.read_csv(file_path)

        # Check if the required columns exist
        required_columns = ['goal']
        missing_columns = [col for col in required_columns if col not in data.columns]

        if missing_columns:
            print(f"The following required columns are missing in the CSV file: {', '.join(missing_columns)}")
        else:
            # Connect to SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create the Attacks table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Attacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_name TEXT NOT NULL,
                    attack_category TEXT,
                    attack_prompt TEXT
                )
            ''')

            # Insert data into the database, setting default values for paper_name and attack_category
            for _, row in data.iterrows():
                cursor.execute('''
                    INSERT INTO Attacks (paper_name, attack_category, attack_prompt)
                    VALUES (?, ?, ?)
                ''', ("jailbroken", "template", row['goal']))

            # Commit and close the connection
            conn.commit()
            conn.close()
            print("Data has been successfully inserted into the SQLite database with updated values.")

    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
