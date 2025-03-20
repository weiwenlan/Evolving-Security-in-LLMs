import sqlite3
import json

# 文件路径
file_path = "renellm_jailbreak.json"

# 数据库路径
db_path = "renellm_jailbreak.db"
table_name = "merged_data"

# 读取 JSON 文件
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)  # 解析 JSON 文件

# 检查 JSON 是否是一个数组
if not isinstance(data, list):
    raise ValueError("JSON 文件的顶层结构不是数组。")

# 连接 SQLite 数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建表（如果不存在）
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idx INTEGER,
    original_harm_behavior TEXT,
    rewritten_prompt TEXT,
    nested_prompt TEXT,
    claude2_output TEXT,
    rewrite_track TEXT,
    model_label TEXT,
    evolution_count INTEGER,
    operation_functions TEXT,
    time_cost REAL
);
"""
cursor.execute(create_table_query)

# 插入 JSON 数据到 SQLite 表
for item in data:
    insert_query = f"""
    INSERT INTO {table_name} (
        idx,
        original_harm_behavior,
        rewritten_prompt,
        nested_prompt,
        claude2_output,
        rewrite_track,
        model_label,
        evolution_count,
        operation_functions,
        time_cost
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    cursor.execute(insert_query, (
        item.get("idx"),
        item.get("original_harm_behavior"),
        item.get("rewritten_prompt"),
        item.get("nested_prompt"),
        item.get("claude2_output"),
        json.dumps(item.get("rewrite_track")),  # 转换为 JSON 字符串存储
        item.get("model_label"),
        item.get("evolution_count"),
        json.dumps(item.get("operation_functions")),  # 转换为 JSON 字符串存储
        item.get("time_cost"),
    ))

# 提交更改并关闭连接
conn.commit()
conn.close()

print(f"数据已成功插入到 {table_name} 表中！")
