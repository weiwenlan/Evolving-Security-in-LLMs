import os
import json
import sqlite3
from datetime import datetime

# only open the database onece and get all the attack requests
def get_experiments_with_defense(db_path:str):
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        print("experiment database connection established.")

        query = """
            SELECT 
                * 
            FROM 
                Experiments
            WHERE 
                defensed_status='completed'
            """

        # and evalute_status!='completed'
        cursor.execute(query)
        rows = cursor.fetchall()

        print("the total number of this experiment is ", len(rows))
        return [{
                    "request_id": row[0],
                    "model_id": row[1], 
                    "attack_id": row[2], 
                    "defense_id": row[3],
                    "attack_timestamp": row[4], 
                    "defense_timestamp": row[5],
                    "attacked_prompt": row[6], 
                    "attacked_response": row[7], 
                    "attacked_result": row[8],
                    "evaluate_status": row[9],
                    "defensed_response": row[10],
                    "defensed_result": row[11],
                    "defensed_status": row[12]
                } for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the connection is closed
        if connection:
            connection.close()
            print("Database connection closed.")
            print("---------------------------------")

# only open the database once but update one line at a time.
class ExperimentResultDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def _ensure_table(self):
        """
        Ensure the all experiment table exists in the database.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        table_name = "Experiments"

        try:
            # check whether the table exists
            cursor.execute(f'''
                SELECT name 
                FROM {table_name}
            ''')

            result = cursor.fetchone()
            if result is None:
                raise ValueError(f"Table '{table_name}' does not exist in the database.")
        finally:
            # close the connection 
            connection.close()

    def update_result(self, row: list):
        query = """
                    UPDATE Experiments
                    SET 
                        attacked_result = ?,
                        evaluate_status = ?,
                        defensed_result = ?
                    WHERE 
                        id = ?
                """
        self.cursor.execute(query, (
            row['attacked_result'], 
            row['evaluate_status'], 
            row['defensed_result'], 
            row['request_id']
        ))

        self.connection.commit()

    def close(self):
        self.connection.close()
        print("Database connection closed.")
