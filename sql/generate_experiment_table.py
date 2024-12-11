from datetime import datetime

def populate_experiments(conn):
    """
    Populate the experiments table by combining attack data with all defense models,
    and map answer_category to attacked_result, including model_id.

    Args:
        conn: Database connection object.
    """
    cursor = conn.cursor()

    try:
        # Fetch all completed attacks with their answer_category and model_id
        cursor.execute("""
            SELECT id, model_id, prompt_input, response, answer_category, sent_at
            FROM attacked_requests
            WHERE status = 'completed'
        """)
        attacks = cursor.fetchall()

        # Fetch all defense models
        cursor.execute("SELECT id, name, category FROM Defenses")
        defenses = cursor.fetchall()

        # Prepare the current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Populate the experiments table
        for attack in attacks:
            attack_id, model_id, attacked_prompt, attacked_response, attacked_result, attack_timestamp = attack

            for defense in defenses:
                defense_id, defense_name, defense_category = defense

                # Insert into experiments table
                cursor.execute("""
                    INSERT INTO Experiments (
                        model_id,
                        attack_id,
                        defense_id,
                        attack_timestamp,
                        attacked_prompt,
                        attacked_response,
                        attacked_result,
                        defensed_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model_id,
                    attack_id,
                    defense_id,
                    attack_timestamp or current_time,
                    attacked_prompt,
                    attacked_response,
                    attacked_result,
                    "pending"
                ))

        # Commit the transaction
        conn.commit()
        print(f"Successfully populated experiments table with {len(attacks) * len(defenses)} entries.")

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()

    finally:
        # Close the database cursor
        cursor.close()

import sqlite3

# Run the main function
if __name__ == "__main__":
    # Path to your SQLite database
    db_path = "sql/chat_requests.db"

    # Establish a database connection
    try:
        conn = sqlite3.connect(db_path)
        print("Database connection established.")

        # Call the function to populate experiments
        populate_experiments(conn)

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()
            print("Database connection closed.")