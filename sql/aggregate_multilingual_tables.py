import sqlite3
import os
import random

def get_sampled_attacks(db_path, sample_size=100):
    """
    Extract a random sample of original_id groups and their associated records from the source database.

    Args:
        db_path (str): Path to the source database.
        sample_size (int): Number of unique original_id groups to sample.

    Returns:
        list[dict]: Extracted data as a list of dictionaries.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"The database file '{db_path}' does not exist.")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Step 1: Fetch all unique original_id values
    cursor.execute("SELECT DISTINCT original_id FROM Attacks")
    original_ids = [row[0] for row in cursor.fetchall()]

    # Step 2: Randomly sample a subset of original_id values
    sampled_original_ids = random.sample(original_ids, min(sample_size, len(original_ids)))

    # Step 3: Fetch all records with the sampled original_id values
    cursor.execute(f"""
        SELECT id, paper_name, attack_category, attack_prompt, original_id
        FROM Attacks
        WHERE original_id IN ({','.join('?' for _ in sampled_original_ids)})
    """, sampled_original_ids)
    rows = cursor.fetchall()

    # Fetch column names
    column_names = [description[0] for description in cursor.description]

    conn.close()

    # Convert rows to a list of dictionaries
    return [dict(zip(column_names, row)) for row in rows]

def inject_attacks_to_db(destination_db_path, attacks):
    """
    Inject the given data into the 'Attacks' table of the destination database.

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
            INSERT INTO Attacks (id, paper_name, attack_category, attack_prompt)
            VALUES (?, ?, ?, ?)
        ''', (attack['id'], attack['paper_name'], attack['attack_category'], attack['attack_prompt']))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    source_db_path = "attack/multilingual/attacks.db"  # Path to the source database
    destination_db_path = "sql/chat_requests.db"  # Path to the destination database

    try:
        # Step 1: Extract sampled data from the source database
        sampled_attacks = get_sampled_attacks(source_db_path, sample_size=100)
        print(f"Extracted {len(sampled_attacks)} rows based on 100 sampled original_id groups from the source database.")

        # Step 2: Inject data into the destination database
        inject_attacks_to_db(destination_db_path, sampled_attacks)
        print(f"Successfully injected data into the destination database.")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
