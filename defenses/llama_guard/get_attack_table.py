"""
@deprecated
"""
import os
import sqlite3

class AttackDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()


    def _ensure_table(self):
        """
        Ensure the all attack table exists in the database.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        table_name = "chat_requests"

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
    
    def get_all_attacks(self):
        # query all the attacks 
        query = "SELECT * FROM chat_requests"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [{"id": row[0], "model_name": row[1], "prompt_input": row[2], "status": row[3], "response": row[4], "method_used": row[5], "method_category": row[6], "answer_category": row[7], "created_at": row[8]} for row in rows]

    def close(self):
        self.connection.close()