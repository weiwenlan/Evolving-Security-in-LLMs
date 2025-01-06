import sqlite3
import requests
import json
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import argparse
from tqdm import tqdm  # Import tqdm for progress bar

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Process pending chat requests.")
    parser.add_argument("--db-path", required=True, help="Path to the SQLite database.")
    return parser.parse_args()

# Parse arguments
args = parse_arguments()
db_path = args.db_path  # Read the database path from command-line arguments

# Load environment variables from .env file
load_dotenv()

# Get configuration values from environment variables
chat_endpoint = os.getenv("CHAT_ENDPOINT")

# Create a database connection
def create_connection(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

# Function to get pending chat requests from the database
def get_pending_requests(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, model_name, prompt_input FROM attacked_requests WHERE status = 'pending'")
    return cursor.fetchall()

# Function to update the status and response of a chat request
def update_request_status(conn, request_id, status, response=None):
    cursor = conn.cursor()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        UPDATE attacked_requests
        SET status = ?, response = ?, sent_at = ?
        WHERE id = ?
    """, (status, response, current_time, request_id))
    conn.commit()

# Function to send requests to the FastAPI chat endpoint
def send_chat_request(endpoint, model_name, prompt):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "prompt": prompt
    }
    response = requests.post(endpoint, headers=headers,
                             data=json.dumps(payload))
    if response.status_code == 200:
        return response.json().get("response")
    else:
        return {
            "error_code": response.status_code,
            "error_message": response.text
        }

# Worker function to process a single request
def process_request(endpoint, request, conn):
    request_id, model_name, prompt = request
    try:
        result = send_chat_request(endpoint, model_name, prompt)
        if isinstance(result, dict) and "error_code" in result:
            error_message = f"Error {result['error_code']}: {result['error_message']}"
            update_request_status(conn, request_id, 'rejected', error_message)
        else:
            update_request_status(conn, request_id, 'completed', result)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        update_request_status(conn, request_id, 'rejected', error_message)

# Main function to process pending requests sequentially with a progress bar
def process_pending_requests():
    conn = create_connection(db_path)
    if conn is None:
        print("Error! Cannot create database connection.")
        return

    pending_requests = get_pending_requests(conn)
    if not pending_requests:
        print("No pending requests found.")
        conn.close()
        return

    # Add a progress bar
    for request in tqdm(pending_requests, desc="Processing requests", unit="request"):
        try:
            process_request(chat_endpoint, request, conn)
        except Exception as e:
            print(f"Error during request processing: {str(e)}")

    conn.close()

# Main function to process pending requests with multithreading and a progress bar
def process_pending_requests_multithreaded():
    conn = create_connection(db_path)
    if conn is None:
        print("Error! Cannot create database connection.")
        return

    pending_requests = get_pending_requests(conn)
    if not pending_requests:
        print("No pending requests found.")
        conn.close()
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_request, chat_endpoint, request, conn)
            for request in pending_requests
        ]

        # Add a progress bar for multithreaded processing
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Processing requests", unit="request"):
            pass

    conn.close()

if __name__ == "__main__":
    process_pending_requests()
