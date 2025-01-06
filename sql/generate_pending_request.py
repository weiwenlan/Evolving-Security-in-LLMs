import sqlite3
import argparse
import sys

# 创建数据库连接
def create_connection(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"数据库连接错误: {e}")
    return conn

# 验证输入的 model_id 和 model_name 是否存在于数据库的 Models 表中
def validate_model(conn, model_id, model_name):
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM Models WHERE id = ? AND model_name = ?;"
    cursor.execute(query, (model_id, model_name))
    result = cursor.fetchone()
    return result[0] > 0

# 生成 pending 请求
def generate_test_requests(db_path, model_id, model_name):
    conn = create_connection(db_path)
    if not conn:
        print("无法连接到数据库。")
        sys.exit(1)

    cursor = conn.cursor()

    # 验证输入的 model_id 和 model_name
    if not validate_model(conn, model_id, model_name):
        print(f"验证失败: 数据库中不存在 model_id={model_id} 且 model_name='{model_name}' 的记录。")
        conn.close()
        sys.exit(1)
    
    print(f"验证成功: 生成 {model_name} (ID: {model_id}) 的 pending 请求。")

    # 生成新的测试请求
    cursor.execute('''
        SELECT 
            ? AS model_id,
            ? AS model_name,
            Attacks.paper_name AS method_used,
            Attacks.attack_category AS method_category,
            Attacks.attack_prompt AS prompt_input
        FROM Attacks;
    ''', (model_id, model_name))

    test_data = cursor.fetchall()

    # 插入新请求到 attacked_requests 表
    for data in test_data:
        model_id, model_name, method_used, method_category, prompt_input = data
        cursor.execute('''
            INSERT INTO attacked_requests (model_id, model_name, prompt_input, status, method_used, method_category, answer_category)
            VALUES (?, ?, ?, 'pending', ?, ?, 'unknown');
        ''', (model_id, model_name, prompt_input, method_used, method_category))
    
    conn.commit()
    print("成功生成 pending 请求。")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="为指定的模型生成测试请求")
    parser.add_argument("--db-path", type=str, required=True, help="数据库路径")
    parser.add_argument("--model-id", type=int, required=True, help="模型 ID")
    parser.add_argument("--model-name", type=str, required=True, help="模型名称")

    args = parser.parse_args()

    generate_test_requests(
        db_path=args.db_path,
        model_id=args.model_id,
        model_name=args.model_name
    )
