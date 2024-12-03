import sqlite3
import os

def get_attacks_from_db(db_path):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"The database file 'attacks.db' does not exist in directory: {source_db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all rows from the Attacks table
    # cursor.execute("SELECT * FROM Attacks")
    cursor.execute("SELECT * FROM Attacks LIMIT 20;")
    rows = cursor.fetchall()

    # Fetch column names
    column_names = [description[0] for description in cursor.description]

    conn.close()

    # Convert rows to a list of dictionaries
    return [dict(zip(column_names, row)) for row in rows]

def inject_attacks_to_db(destination_db_path, attacks):
    """
    Injects the given data into the 'Attacks' table of the destination database.

    Args:
        destination_db_path (str): Path to the destination database.
        attacks (list[dict]): Data to be inserted into the Attacks table.
    """
    if not os.path.exists(destination_db_path):
        raise FileNotFoundError(f"The destination database does not exist at: {destination_db_path}")
    
    conn = sqlite3.connect(destination_db_path)
    cursor = conn.cursor()

    # Insert each attack into the Attacks table
    for attack in attacks:
        cursor.execute('''
            INSERT INTO Attacks (paper_name, attack_category, attack_prompt)
            VALUES (?, ?, ?)
        ''', (attack['paper_name'], attack['attack_category'], attack['attack_prompt']))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    source_db_path = "attack/jailbroken2/attacks.db"  # Directory containing the source attacks.db
    destination_db_path = "sql/chat_requests.db"  # Path to the destination database

    try:
        # Step 1: Extract data from the source database
        attacks = get_attacks_from_db(source_db_path)
        print(f"Extracted {len(attacks)} rows from the source database.")

        # Step 2: Inject data into the destination database
        inject_attacks_to_db(destination_db_path, attacks)
        print(f"Successfully injected data into the destination database.")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
