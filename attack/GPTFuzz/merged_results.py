import sqlite3
import glob
import argparse

# 创建合并的 SQLite 数据库表
def create_output_table(conn):
    cursor = conn.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS merged_table (
            prompt TEXT,
            response TEXT,
            parent TEXT,
            result TEXT,
            timestamp TEXT
        );
    """
    cursor.execute(create_table_query)
    conn.commit()

# 合并单个数据库
def merge_database(file_pattern, merged_database):
    # 创建合并数据库连接
    conn_merged = sqlite3.connect(merged_database)
    create_output_table(conn_merged)
    cursor_merged = conn_merged.cursor()

    # 遍历所有符合模式的 SQLite 数据库文件
    for file_path in glob.glob(file_pattern):
        print(f"Processing file: {file_path}")
        try:
            conn_source = sqlite3.connect(file_path)
            cursor_source = conn_source.cursor()

            # 检查 chat_responses 表是否存在
            cursor_source.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' AND name='chat_responses';
            """)
            if cursor_source.fetchone() is None:
                print(f"  Skipping file: {file_path} (no 'chat_responses' table)")
                conn_source.close()
                continue

            # 获取数据并插入到目标表
            cursor_source.execute("SELECT prompt, response, parent, result, timestamp FROM chat_responses")
            rows = cursor_source.fetchall()
            cursor_merged.executemany("""
                INSERT INTO merged_table (prompt, response, parent, result, timestamp) 
                VALUES (?, ?, ?, ?, ?)
            """, rows)
            conn_merged.commit()

            conn_source.close()
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    print("All databases have been merged into the table 'merged_table'")
    conn_merged.close()

# 主函数
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple SQLite databases into one.")
    parser.add_argument("--file-pattern", type=str, default="results-gpt-*.db", help="Pattern to match SQLite database files.")
    parser.add_argument("--merged-database", type=str, default="merged_results.db", help="Name of the output merged SQLite database.")
    args = parser.parse_args()

    merge_database(
        file_pattern=args.file_pattern,
        merged_database=args.merged_database
    )
