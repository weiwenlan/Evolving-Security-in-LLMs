import sqlite3
import random
import argparse

def sample_and_insert(source_db_path, target_db_path, source_table_name, target_table_name, sample_size=1000):
    """
    从 `source_db_path` 的 `source_table_name` 表中抽取指定数量的行，并插入到 `target_db_path` 的 `target_table_name` 表中。

    Args:
        source_db_path: 源数据库路径。
        target_db_path: 目标数据库路径。
        source_table_name: 源表名。
        target_table_name: 目标表名。
        sample_size: 要抽取的行数（默认 1000）。
    """
    print("开始抽取数据并插入目标表...")

    # 连接到源数据库
    source_conn = sqlite3.connect(source_db_path)
    source_cursor = source_conn.cursor()

    # 连接到目标数据库
    target_conn = sqlite3.connect(target_db_path)
    target_cursor = target_conn.cursor()

    # 从源表中获取所有数据
    query_select = f"SELECT nested_prompt FROM {source_table_name};"
    source_cursor.execute(query_select)
    rows = source_cursor.fetchall()

    # 如果源表数据少于 sample_size，调整抽样大小
    actual_sample_size = min(len(rows), sample_size)
    print(f"从源表中找到 {len(rows)} 行，抽样大小设置为 {actual_sample_size}。")

    # 随机选择 sample_size 行
    sampled_rows = random.sample(rows, actual_sample_size)

    # 插入到目标表
    for row in sampled_rows:
        nested_prompt = row[0]  # 获取 nested_prompt 字段值
        query_insert = f"""
        INSERT INTO {target_table_name} (
            paper_name,
            attack_category,
            attack_prompt
        ) VALUES (?, ?, ?);
        """
        target_cursor.execute(query_insert, (
            "ReNeLLM",        # 固定值
            "Genetic",        # 固定值
            nested_prompt     # 从源表获取的 nested_prompt
        ))

    # 提交更改并关闭连接
    target_conn.commit()
    source_conn.close()
    target_conn.close()

    print(f"成功从 {source_table_name} 抽取 {actual_sample_size} 行数据并插入到 {target_table_name}！")

# 示例调用
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="抽取并迁移 SQLite 数据库中的数据")
    parser.add_argument("--source-db-path", type=str, required=False, default="attack/ReNeLLMWenlan/renellm_jailbreak.db",help="源数据库路径")
    parser.add_argument("--target-db-path", type=str, required=True, help="目标数据库路径")
    parser.add_argument("--source-table-name", type=str, default="merged_data", help="源表名")
    parser.add_argument("--target-table-name", type=str, default="Attacks", help="目标表名")
    parser.add_argument("--sample-size", type=int, default=500, help="要抽取的行数（默认 500）")

    args = parser.parse_args()

    sample_and_insert(
        source_db_path=args.source_db_path,
        target_db_path=args.target_db_path,
        source_table_name=args.source_table_name,
        target_table_name=args.target_table_name,
        sample_size=args.sample_size
    )
