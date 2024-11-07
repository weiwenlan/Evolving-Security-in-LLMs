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
    cursor.execute("SELECT id, name, parameters, provider FROM Models WHERE name = ?", (model_name,))
    return cursor.fetchone()

# Function to get pending chat requests from the database
def get_pending_requests(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, model, actual_text FROM chat_requests WHERE status = 'pending'")
    return cursor.fetchall()

# Function to update the status and response of a chat request
def update_request_status(conn, request_id, response, model):
    cursor = conn.cursor()
    cursor.execute("UPDATE chat_requests SET status = ?, response = ?, model_used = ?, completed_at = ? WHERE id = ?", 
                   ('completed', response, model, time.strftime('%Y-%m-%d %H:%M:%S'), request_id))
    conn.commit()

# Function to send requests to the FastAPI chat endpoint
def send_chat_request(endpoint, model_name, prompt):
    # Get the model details from the database
    conn = create_connection(db_path)
    model_details = get_model_details(conn, model_name)
    conn.close()
    
    if model_details is None:
        raise Exception(f"Model '{model_name}' not found in the database.")
    
    model_id, name, parameters, provider = model_details

    # Construct the payload using model details
    url = f"{endpoint}/chat"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": name,
        "parameters": parameters,
        "provider": provider,
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json().get("response")
    else:
        raise Exception(f"Error in API request: {response.status_code} - {response.text}")

# Main function to process pending requests
def process_pending_requests(endpoint):
    conn = create_connection(db_path)
    if conn is None:
        print("Error! Cannot create database connection.")
        return

    pending_requests = get_pending_requests(conn)
    for request in pending_requests:
        request_id, model_name, actual_text = request
        try:
            response = send_chat_request(endpoint, model_name, actual_text)
            update_request_status(conn, request_id, response, model_name)
            print(f"Processed request ID {request_id} successfully.")
        except Exception as e:
            print(f"Failed to process request ID {request_id}: {str(e)}")

    conn.close()

if __name__ == "__main__":
    endpoint = "http://127.0.0.1:8000"
    process_pending_requests(endpoint)
