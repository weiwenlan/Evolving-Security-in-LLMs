import sqlite3
import pandas as pd

def csv_to_sqlite(csv_file, db_name="attacks.db"):
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Add fixed columns paper_name and attack_category
    df['paper_name'] = 'multilingual'
    df['attack_category'] = 'template'

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the Attacks table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- Auto-increment primary key
            idx INTEGER,
            paper_name TEXT NOT NULL,
            attack_category TEXT,
            attack_prompt TEXT,
            language TEXT,
            tags TEXT,
            original_id INTEGER
        )
    ''')

    # Iterate over each row in the CSV file and insert into the SQLite database
    for index, row in df.iterrows():
        # Iterate over each language column (zh, it, vi, etc.)
        for lang in ['zh', 'it', 'vi', 'ar', 'ko', 'th', 'bn', 'sw', 'jv']:
            attack_prompt = row[lang]
            language = lang
            tags = row['tags']
            original_id = row['id']

            # Insert data into the Attacks table
            cursor.execute('''
                INSERT INTO Attacks (
                    paper_name, attack_category, attack_prompt, language, tags, original_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                row['paper_name'],  # multilingual
                row['attack_category'],  # template
                attack_prompt,
                language,
                tags,
                original_id
            ))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Example usage
csv_to_sqlite("MultiJail Data.csv")
