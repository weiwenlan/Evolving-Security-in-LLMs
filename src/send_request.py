import sqlite3
import requests
import json
import time
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

# Function to get model details by model name
def get_model_details(conn, model_name):
    cursor = conn.cursor()
    cursor.execute("SELECT endpoint, parameters FROM Models WHERE model_name = ?", (model_name,))
    return cursor.fetchone()

# Function to get pending chat requests from the database
def get_pending_requests(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, model_name, attack_id FROM chat_requests WHERE status = 'pending'")
    return cursor.fetchall()

# Function to get the attack description to use as the prompt
def get_attack_description(conn, attack_id):
    cursor = conn.cursor()
    cursor.execute("SELECT attack_prompt FROM Attacks WHERE id = ?", (attack_id,))
    result = cursor.fetchone()
    return result[0] if result else None

# Function to update the status and response of a chat request
def update_request_status(conn, request_id, response, model_name):
    cursor = conn.cursor()
    cursor.execute("UPDATE chat_requests SET status = ?, response = ?, model_used = ?, completed_at = ? WHERE id = ?", 
                   ('completed', response, model_name, time.strftime('%Y-%m-%d %H:%M:%S'), request_id))
    conn.commit()

# Function to send requests to the FastAPI chat endpoint using configuration from Models table
def send_chat_request(conn, model_name, prompt):
    # Get model details from the Models table
    model_details = get_model_details(conn, model_name)
    if model_details is None:
        raise Exception(f"Model '{model_name}' not found in the database.")
    
    endpoint, parameters_json = model_details
    parameters = json.loads(parameters_json)

    # Construct the payload using model and API details
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "prompt": prompt,
        "parameters": parameters
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json().get("response")
    else:
        raise Exception(f"Error in API request: {response.status_code} - {response.text}")

# Main function to process pending requests
def process_pending_requests():
    conn = create_connection(db_path)
    if conn is None:
        print("Error! Cannot create database connection.")
        return

    pending_requests = get_pending_requests(conn)
    for request in pending_requests:
        request_id, model_name, attack_id = request
        try:
            # Get the attack description to use as the prompt
            prompt = get_attack_description(conn, attack_id)
            if prompt is None:
                raise Exception(f"Attack description for attack ID {attack_id} not found.")
            
            response = send_chat_request(conn, model_name, prompt)
            update_request_status(conn, request_id, response, model_name)
            print(f"Processed request ID {request_id} successfully.")
        except Exception as e:
            print(f"Failed to process request ID {request_id}: {str(e)}")

    conn.close()

if __name__ == "__main__":
    process_pending_requests()
