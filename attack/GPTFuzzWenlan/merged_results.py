import sqlite3
import os
import glob
import argparse

# 创建合并的 SQLite 数据库表
def create_output_table(conn, table_name):
    cursor = conn.cursor()
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
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
def merge_database(file_pattern, merged_database, table_name):
    # 创建合并数据库连接
    conn_merged = sqlite3.connect(merged_database)
    create_output_table(conn_merged, table_name)
    cursor_merged = conn_merged.cursor()

    # 遍历所有符合模式的 SQLite 数据库文件
    for file_path in glob.glob(file_pattern):
        print(f"Processing file: {file_path}")
        conn_source = sqlite3.connect(file_path)
        cursor_source = conn_source.cursor()

        # 获取当前文件的表名
        cursor_source.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%';
        """)
        tables = cursor_source.fetchall()

        # 遍历每个表并将数据插入到新数据库中
        for table in tables:
            table_name = table[0]
            print(f"  Processing table: {table_name}")
            
            # 检查是否包含所需的字段
            cursor_source.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor_source.fetchall()]
            required_columns = {"prompt", "response", "parent", "result", "timestamp"}
            if not required_columns.issubset(set(columns)):
                print(f"  Skipping table: {table_name} (missing required columns)")
                continue

            # 读取数据（忽略 id 列）
            cursor_source.execute(f"SELECT prompt, response, parent, result, timestamp FROM {table_name}")
            rows = cursor_source.fetchall()

            # 插入数据到合并数据库的新表中
            cursor_merged.executemany(f"INSERT INTO {table_name} (prompt, response, parent, result, timestamp) VALUES (?, ?, ?, ?, ?)", rows)
            conn_merged.commit()

        conn_source.close()

    print(f"All databases have been merged into the SQLite table: {table_name}")
    conn_merged.close()

# 主函数
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple SQLite databases into one.")
    parser.add_argument("--file-pattern", type=str, default="results-gpt-*.db", help="Pattern to match SQLite database files.")
    parser.add_argument("--merged-database", type=str, default="merged_results.db", help="Name of the output merged SQLite database.")
    parser.add_argument("--table-name", type=str, default="merged_table", help="Name of the table in the merged database.")
    args = parser.parse_args()

    merge_database(
        file_pattern=args.file_pattern,
        merged_database=args.merged_database,
        table_name=args.table_name
    )
