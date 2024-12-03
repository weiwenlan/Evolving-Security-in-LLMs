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

# def insert_results(db_path, results):
#     """
#     将 defense_generation 函数生成的结果插入到 SQLite 数据库中。

#     Args:
#         db_path (str): 数据库的路径。
#         results (list): defense_generation 生成的结果列表。
#     """
#     # 连接到数据库
#     connection = sqlite3.connect(db_path)
#     cursor = connection.cursor()

#     # 插入每个结果到表中
#     for result in results:
#         for item in result:  # 由于每个 result 可能是一个列表
#             cursor.execute('''
#                 INSERT INTO defense_results (aid, paper_name, attack_category, attack_prompt, llama_check_result)
#                 VALUES (?, ?, ?, ?, ?)
#             ''', (item['aid'], item['paper_name'], item['attack_category'], item['attack_prompt'], "\n".join(item['llama_check_result'])))

#     # 提交更改并关闭连接
#     connection.commit()
#     connection.close()
#     print(f"Inserted {len(results)} rows into defense_results.")

# # 调用函数将结果插入数据库
# results = defense_generation(attack_prompts, defense_type="pre-generation", defense_model="meta-llama/Llama-Guard-3-8B/v1")
# insert_results(db_path, results)
