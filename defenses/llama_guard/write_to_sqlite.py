import time
import sqlite3

def create_table(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # 创建表，包含五个列
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {db_path} (
            aid INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_name TEXT,
            attack_category TEXT,
            attack_prompt TEXT,
            llama_check_result TEXT
        )
    ''')
    connection.commit()
    connection.close()

# 调用函数创建表

db_path = f'llama_guard_{time.strftime("%d_%H_%M", time.localtime())}'
create_table(db_path)