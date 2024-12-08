import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration values from environment variables
db_path = os.getenv("DB_PATH")

# Establish a connection to the database


def get_connection():
    # Ensure the directory for the database file exists
    if db_path and not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))

    # If the database file does not exist, it will be created automatically
    if not os.path.exists(db_path):
        open(db_path, 'w').close()  # Create an empty file

    return sqlite3.connect(db_path)


# model_names = ["chatgpt-4o-latest", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4-turbo", "claude-3-5-sonnet-20241022", "claude-3-sonnet-20240229", "claude-3-5-haiku-20241022",
#                "claude-3-haiku-20240307", "claude-3-opus-latest", "gemini-1.5-flash-8b-001", "gemini-1.5-flash-001", "gemini-1.5-pro-001"]

model_names = ["meta-llama/Llama-3.1-8B-Instruct",
               "meta-llama/Llama-3.1-70B-Instruct"]


# Create all necessary tables
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Create attacked_requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attacked_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prompt_input TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            response TEXT,
            method_used TEXT,
            method_category TEXT,
            answer_category TEXT,
            sent_at TIMESTAMP
        )
    """)

    # Create Attacks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_name TEXT NOT NULL,
            attack_category TEXT,
            attack_prompt TEXT
        )
    ''')

    # Create Defenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Defenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT
        )
    ''')

    # Create Models table (includes API configuration parameters)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL
        )
    ''')

    # Create Experiments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Experiments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id INTEGER,
        attack_id INTEGER,
        defense_id INTEGER,
        attack_timestamp TEXT, 
        defense_timestamp TEXT,
        attacked_prompt TEXT, 
        attacked_response TEXT,
        attacked_result TEXT,
        evaluate_status TEXT, 
        defensed_response TEXT,
        defensed_result TEXT, 
        defensed_status TEXT, 
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

    cursor.executemany('''
        INSERT INTO Models (model_name) VALUES (?)
    ''', [(model_name,) for model_name in model_names])

    defenses = [
        ("no defense", None),
        ("llama guard", "detection"),
        ("system prompt", "prompt-engineering"),
        ("smoothllm", "denoise"),
        ("placeholder1", "placeholder1"),
        ("placeholder2", "placeholder2")
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO Defenses (name, category)
        VALUES (?, ?)
    ''', defenses)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database and all tables created successfully.")
