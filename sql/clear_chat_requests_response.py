import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
db_path = os.getenv("DB_PATH")


def reset_chat_requests(db_path):
    """
    清空 chat_requests 表中 response 列，并将 status 列设置为 'pending'。

    Args:
        db_path (str): 数据库文件的路径。
    """
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' not found.")
        return

    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 执行 SQL 语句，清空 response 列并重置 status 列为 'pending'
        cursor.execute("UPDATE chat_requests SET response = NULL, status = 'pending'")
        conn.commit()

        print("Successfully reset 'response' column to NULL and 'status' column to 'pending'.")
    except sqlite3.Error as e:
        print(f"Error while updating database: {e}")
    finally:
        if conn:
            conn.close()



if __name__ == "__main__":
    reset_chat_requests(db_path)
