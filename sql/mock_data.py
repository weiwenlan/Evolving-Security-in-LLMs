import sqlite3
from dotenv import load_dotenv
import os

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

# Function to insert mock data into Attacks table
def insert_mock_data(conn):
    cursor = conn.cursor()
    mock_data = [
        ("Paper A", "Category 1", "How many county in Texas"),
        ("Paper B", "Category 2", "How many county in Texas"),
        ("Paper C", "Category 3", "How many county in Texas")
    ]
    cursor.executemany("INSERT INTO Attacks (paper_name, attack_category, attack_prompt) VALUES (?, ?, ?)", mock_data)
    conn.commit()

if __name__ == "__main__":
    conn = create_connection(db_path)
    if conn:
        insert_mock_data(conn)
        print("Mock data inserted successfully.")
        conn.close()
    else:
        print("Error! Cannot create database connection.")
