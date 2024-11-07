import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration values from environment variables
db_path = os.getenv("DB_PATH")

# Establish a connection to the database
def get_connection():
    return sqlite3.connect(db_path)

# Create all necessary tables
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create chat_requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            actual_text TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            response TEXT,
            model_used TEXT,
            completed_at TEXT
        )
    """)
    
    # Create Attacks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT
        )
    ''')

    # Create Defenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Defenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT
        )
    ''')

    # Create Models table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parameters TEXT,
            provider TEXT
        )
    ''')

    # Create Experiments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER,
            attack_id INTEGER,
            defense_id INTEGER,
            success_rate REAL,
            efficiency REAL,
            date TEXT,
            notes TEXT,
            FOREIGN KEY (model_id) REFERENCES Models(id),
            FOREIGN KEY (attack_id) REFERENCES Attacks(id),
            FOREIGN KEY (defense_id) REFERENCES Defenses(id)
        )
    ''')

    # Create Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            category TEXT,
            success BOOLEAN,
            count INTEGER,
            FOREIGN KEY (experiment_id) REFERENCES Experiments(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database and all tables created successfully.")
