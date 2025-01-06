import sqlite3
import os
import random
import argparse

def get_attacks_from_db(db_path, sample_size=500):
    """
    从源数据库中随机抽取指定数量的行。

    Args:
        db_path (str): 源数据库路径。
        sample_size (int): 要抽取的行数。

    Returns:
        list[dict]: 抽取的攻击数据，每行是一个字典。
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"The database file '{db_path}' does not exist.")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有数据
    cursor.execute("SELECT * FROM Attacks")
    rows = cursor.fetchall()

    # 获取列名
    column_names = [description[0] for description in cursor.description]

    conn.close()

    # 随机抽取 sample_size 行
    sampled_rows = random.sample(rows, min(len(rows), sample_size))

    # 将行数据转换为字典列表
    return [dict(zip(column_names, row)) for row in sampled_rows]

def inject_attacks_to_db(destination_db_path, attacks):
    """
    将数据插入到目标数据库的 Attacks 表。

    Args:
        destination_db_path (str): 目标数据库路径。
        attacks (list[dict]): 要插入的数据。
    """
    if not os.path.exists(destination_db_path):
        raise FileNotFoundError(f"The destination database does not exist at: {destination_db_path}")
    
    conn = sqlite3.connect(destination_db_path)
    cursor = conn.cursor()

    # 插入数据
    for attack in attacks:
        cursor.execute('''
            INSERT INTO Attacks (paper_name, attack_category, attack_prompt)
            VALUES (?, ?, ?)
        ''', (attack['paper_name'], attack['attack_category'], attack['attack_prompt']))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="从源数据库抽取数据并注入到目标数据库")
    parser.add_argument("--source-db-path", type=str, required=True, help="源数据库路径")
    parser.add_argument("--target-db-path", type=str, required=True, help="目标数据库路径")
    parser.add_argument("--sample-size", type=int, default=500, help="抽取的行数（默认500行）")
    args = parser.parse_args()

    try:
        # 从源数据库抽取数据
        attacks = get_attacks_from_db(args.source_db_path, sample_size=args.sample_size)
        print(f"从源数据库抽取了 {len(attacks)} 行数据。")

        # 将数据插入到目标数据库
        inject_attacks_to_db(args.target_db_path, attacks)
        print(f"成功将数据插入到目标数据库。")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"发生错误: {e}")
