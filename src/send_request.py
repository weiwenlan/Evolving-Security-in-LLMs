import sqlite3
import requests
import json
import time
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get configuration values from environment variables
db_path = os.getenv("DB_PATH")
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
    """
    Update the status, response, and sent_at timestamp of a chat request in the database.

    Args:
        conn: Database connection object.
        request_id: ID of the request.
        status: New status ('completed' or 'rejected').
        response: Response message or error details (default: None).
    """
    cursor = conn.cursor()
    # Get the current timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update the record
    cursor.execute("""
        UPDATE attacked_requests
        SET status = ?, response = ?, sent_at = ?
        WHERE id = ?
    """, (status, response, current_time, request_id))
    
    # Commit the changes
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
        # Return error details instead of raising an exception
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
            # Handle API error, update status to 'rejected'
            error_message = f"Error {result['error_code']}: {
                result['error_message']}"
            update_request_status(conn, request_id, 'rejected', error_message)
            print(f"Rejected request ID {request_id}: {error_message}")
        else:
            # Handle successful response
            update_request_status(conn, request_id, 'completed', result)
            print(f"Processed request ID {request_id} successfully.")
    except Exception as e:
        # Handle unexpected errors, update status to 'rejected'
        error_message = f"Unexpected error: {str(e)}"
        update_request_status(conn, request_id, 'rejected', error_message)
        print(f"Rejected request ID {request_id}: {error_message}")

# Main function to process pending requests without multithreading


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
    # Process requests sequentially
    for request in pending_requests:
        try:
            process_request(chat_endpoint, request, conn)
        except Exception as e:
            print(f"Error during request processing: {str(e)}")

    conn.close()


# Main function to process pending requests with multithreading
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

    # ThreadPoolExecutor to process requests concurrently
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [
            executor.submit(process_request, chat_endpoint, request, conn)
            for request in pending_requests
        ]

        # Optionally, wait for all futures to complete
        for future in as_completed(futures):
            try:
                future.result()  # To handle exceptions raised by threads
            except Exception as e:
                print(f"Error during thread execution: {str(e)}")

    conn.close()


if __name__ == "__main__":
    process_pending_requests()
