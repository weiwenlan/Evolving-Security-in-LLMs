import sqlite3
import os
import re
import argparse

# 创建输出数据库的表结构
def create_output_table(output_conn):
    cursor = output_conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merged_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            args TEXT,
            prompt TEXT,
            decoded_prompt TEXT,
            response TEXT,
            decoded_response TEXT,
            toxicity_score TEXT,
            timestamp TEXT
        )
    """)
    output_conn.commit()

# 提取文件名中的 category
def extract_category(file_name):
    match = re.search(r"data_(.*?)_", file_name)
    if match:
        return match.group(1).replace("-", "_")  # 替换文件名中的 "-" 为 "_"
    return "unknown"

# 合并单个数据库
def merge_db(input_db, category, output_conn):
    input_conn = sqlite3.connect(input_db)
    input_cursor = input_conn.cursor()
    output_cursor = output_conn.cursor()

    # 获取所有数据
    input_cursor.execute("SELECT args, prompt, decoded_prompt, response, decoded_response, toxicity_score, timestamp FROM Conversations")
    rows = input_cursor.fetchall()

    # 插入到输出数据库，并添加 category
    for row in rows:
        output_cursor.execute("""
            INSERT INTO merged_data (category, args, prompt, decoded_prompt, response, decoded_response, toxicity_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (category, *row))

    output_conn.commit()
    input_conn.close()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Merge multiple SQLite databases into one.")
    parser.add_argument('--input-path', type=str, default="./saved_results/gpt-4-turbo", help='Path to the folder containing .db files')
    parser.add_argument('--output-db', type=str, default="merged_results.db", help='Path to the output merged database file')
    return parser.parse_args()

# 主函数
def main():
    args = parse_arguments()
    input_folder = args.input_path  # 使用命令行参数指定的输入路径
    output_db = args.output_db      # 使用命令行参数指定的输出数据库路径

    # 打开输出数据库连接
    output_conn = sqlite3.connect(output_db)
    create_output_table(output_conn)

    # 遍历文件夹中的所有 .db 文件
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".db"):
            file_path = os.path.join(input_folder, file_name)
            category = extract_category(file_name)
            print(f"Merging {file_name} with category: {category}")
            merge_db(file_path, category, output_conn)

    output_conn.close()
    print(f"All databases have been merged into {output_db}")

if __name__ == "__main__":
    main()
