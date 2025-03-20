import sqlite3
import argparse
import random
import sys

def validate_model(target_conn, model_id, model_name):
    """
    验证目标数据库中是否存在给定的 model_id 和 model_name。

    Args:
        target_conn (sqlite3.Connection): 目标数据库连接。
        model_id (int): 模型ID。
        model_name (str): 模型名称。

    Returns:
        bool: 如果验证通过返回 True，否则返回 False。
    """
    cursor = target_conn.cursor()
    query = "SELECT COUNT(*) FROM models WHERE id = ? AND model_name = ?;"
    cursor.execute(query, (model_id, model_name))
    result = cursor.fetchone()
    return result[0] > 0

def sample_rows(rows, sample_size=500):
    """
    从数据中随机抽样。

    Args:
        rows (list): 源数据行列表。
        sample_size (int): 抽样数量。

    Returns:
        list: 抽样后的数据行列表。
    """
    if len(rows) <= sample_size:
        return rows
    return random.sample(rows, sample_size)

def main(args):
    # 连接到源数据库
    try:
        source_conn = sqlite3.connect(args.source_db_path)
        source_cursor = source_conn.cursor()
    except sqlite3.Error as e:
        print(f"无法连接到源数据库: {e}")
        return

    # 连接到目标数据库
    try:
        target_conn = sqlite3.connect(args.target_db_path)
        target_cursor = target_conn.cursor()
    except sqlite3.Error as e:
        print(f"无法连接到目标数据库: {e}")
        source_conn.close()
        return

    # 验证模型信息
    if not validate_model(target_conn, args.model_id, args.model_name):
        print(f"验证失败: 模型表中不存在 model_id={args.model_id} 且 model_name='{args.model_name}' 的记录。")
        source_conn.close()
        target_conn.close()
        sys.exit(1)

    print(f"验证成功: 模型表中存在 model_id={args.model_id} 且 model_name='{args.model_name}' 的记录。")

    # 从源数据库读取数据
    query_select = """
    SELECT prompt, response, parent, result, timestamp
    FROM merged_table; -- 替换为源表的名称
    """
    source_cursor.execute(query_select)
    rows = source_cursor.fetchall()

    # 随机抽样 500 条数据
    sampled_rows = sample_rows(rows, sample_size=500)

    # 将数据插入到目标数据库
    query_insert = """
    INSERT INTO attacked_requests 
    (id, model_id, model_name, prompt_input, status, response, method_used, method_category, answer_category, sent_at)
    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    for row in sampled_rows:
        prompt = row[0]
        response = row[1]
        result = row[3]
        timestamp = row[4]

        # 插入目标表
        target_cursor.execute(query_insert, (
            args.model_id,  # 从命令行获取的 model_id
            args.model_name,  # 从命令行获取的 model_name
            prompt,  # prompt_input
            'completed',  # status
            response,  # response
            'GPTFuzz',  # method_used
            'Genetic',  # method_category
            result,  # answer_category
            timestamp  # sent_at
        ))

    # 提交更改
    target_conn.commit()

    # 关闭连接
    source_conn.close()
    target_conn.close()

    print(f"成功从源数据库迁移 {len(sampled_rows)} 条数据到目标数据库！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="迁移数据并随机抽样 500 条记录。")
    parser.add_argument('--source-db-path', type=str, required=True, help='源数据库路径')
    parser.add_argument('--target-db-path', type=str, required=True, help='目标数据库路径')
    parser.add_argument('--model-id', type=int, required=True, help='模型ID')
    parser.add_argument('--model-name', type=str, required=True, help='模型名称')
    args = parser.parse_args()

    main(args)
