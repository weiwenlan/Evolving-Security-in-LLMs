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

# Function to generate test requests only for new models
def generate_test_requests():
    conn = create_connection(db_path)
    cursor = conn.cursor()

    # Find new models that are not in attacked_requests
    cursor.execute('''
        SELECT id, model_name
        FROM Models
        WHERE id NOT IN (SELECT DISTINCT model_id FROM attacked_requests)
    ''')
    
    new_models = cursor.fetchall()

    # If there are new models, join with Attacks and generate requests
    if new_models:
        for model_id, model_name in new_models:
            cursor.execute('''
                SELECT 
                    ? AS model_id,
                    ? AS model_name,
                    Attacks.paper_name AS method_used,
                    Attacks.attack_category AS method_category,
                    Attacks.attack_prompt AS prompt_input
                FROM Attacks
            ''', (model_id, model_name))
            
            test_data = cursor.fetchall()

            # Insert new requests into attacked_requests
            for data in test_data:
                model_id, model_name, method_used, method_category, prompt_input = data
                cursor.execute('''
                    INSERT INTO attacked_requests (model_id, model_name, prompt_input, status, method_used, method_category, answer_category)
                    VALUES (?, ?, ?, 'pending', ?, ?, 'unknown')
                ''', (model_id, model_name, prompt_input, method_used, method_category))
        
        conn.commit()
        print("Test requests generated successfully for new models in attacked_requests table.")
    else:
        print("No new models found to generate test requests.")
    
    conn.close()

if __name__ == "__main__":
    generate_test_requests()
