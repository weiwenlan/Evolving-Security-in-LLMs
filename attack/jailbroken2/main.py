import json
import sqlite3

def process_jsonl_file(jsonl_file, db_file):
    # Connect to the SQLite database
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_name TEXT,
            attack_category TEXT,
            attack_prompt TEXT
        )
    ''')

    # Open and process the JSONL file line by line
    with open(jsonl_file, 'r') as file:
        for line in file:
            try:
                # Parse the JSON object from the line
                json_object = json.loads(line)
                
                # Extract data from the 'request' field
                for item in json_object.get("request", []):
                    if item.get("sender") == "environment":
                        # Insert data into the database
                        cursor.execute('''
                            INSERT INTO Attacks (paper_name, attack_category, attack_prompt)
                            VALUES (?, ?, ?)
                        ''', (
                            "jailbroken",  # Example fixed value for paper_name
                            "template",    # Example fixed value for attack_category
                            item.get("content")
                        ))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue

    # Commit and close the database connection
    connection.commit()
    connection.close()

    print("Data has been successfully stored in the database.")

# Use the function with the specified JSON and database file paths
json_file_path = 'responses.jsonl'  # Replace with the path to your JSON file
db_file_path = 'attacks.db'      # Replace with the path to your SQLite database
process_jsonl_file(json_file_path, db_file_path)
