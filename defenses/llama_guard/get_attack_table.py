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

# # for reference only
# class SQLiteHandler:
#     def __init__(self, db_path="llama_guard.db"):
#         """
#         Initialize the SQLiteHandler with the database path and ensure the table exists.

#         Args:
#             db_path (str): Path to the SQLite database file.
#         """
#         self.db_path = db_path
#         self._ensure_table()

#     def _ensure_table(self):
#         """
#         Ensure the chat_responses table exists in the database.
#         """
#         connection = sqlite3.connect(self.db_path)
#         cursor = connection.cursor()
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS llama_guard (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing ID
#                 prompt TEXT,                           -- Prompt text
#                 response TEXT,                         -- Single response text
#                 parent INTEGER,                        -- Parent ID (can be NULL if root)
#                 result TEXT                            -- Single result value
#             )
#         ''')
#         connection.commit()
#         connection.close()

#     def insert_responses(self, prompt, responses, parent, results):
#         """
#         Insert multiple rows into the chat_responses table.

#         Args:
#             prompt (str): The input prompt.
#             responses (list): A list of response strings.
#             parent (int): The parent ID (or None for root-level prompts).
#             results (list): A list of result values corresponding to the responses.

#         Raises:
#             ValueError: If `responses` and `results` lists have different lengths.
#         """
#         if len(responses) != len(results):
#             raise ValueError("The length of `responses` and `results` must match.")

#         connection = sqlite3.connect(self.db_path)
#         cursor = connection.cursor()

#         # Insert each response-result pair as a separate row
#         for response, result in zip(responses, results):
#             cursor.execute('''
#                 INSERT INTO chat_responses (prompt, response, parent, result)
#                 VALUES (?, ?, ?, ?)
#             ''', (prompt, response, parent, result))

#         connection.commit()
#         connection.close()
#         print(f"Inserted {len(responses)} rows into chat_responses.")
