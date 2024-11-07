import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration values from environment variables
db_path = os.getenv("DB_PATH")

# Create a database connection
def create_connection(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to generate test requests
def generate_test_requests():
    conn = create_connection(db_path)
    cursor = conn.cursor()

    # Join Models and Attacks to generate a set of test requests
    cursor.execute('''
        SELECT 
            Models.model_name,
            Attacks.paper_name AS method_used,
            Attacks.attack_category AS method_category,
            Attacks.attack_prompt AS prompt_input
        FROM 
            Models
        JOIN 
            Attacks ON 1=1  -- Cartesian product to test each model with each attack
    ''')

    # Fetch all combinations of model and attack
    test_data = cursor.fetchall()
    
    # Insert each combination as a new request in chat_requests
    for data in test_data:
        model_name, method_used, method_category, prompt_input = data
        cursor.execute('''
            INSERT INTO chat_requests (model_name, prompt_input, status, method_used, method_category, answer_category)
            VALUES (?, ?, 'pending', ?, ?, 'unknown')
        ''', (model_name, prompt_input, method_used, method_category))
    
    conn.commit()
    conn.close()
    print("Test requests generated successfully in chat_requests table.")

if __name__ == "__main__":
    generate_test_requests()
