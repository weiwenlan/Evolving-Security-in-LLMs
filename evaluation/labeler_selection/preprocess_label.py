import pandas as pd


file_path = 'final_labeled_data.xlsx'  # 替换为你的文件路径
data = pd.read_excel(file_path)

# 标准化列名
data.columns = ['response', 'label']

# 定义处理函数
def process_label(label):
    label_lower = label.lower()
    if 'yes' in label_lower:
        binary_label = 'unsafe'
    elif 'no' in label_lower:
        binary_label = 'safe'
    else:
        binary_label = 'unknown'  # 针对未定义的情况
    return binary_label

def extract_numbers(label):
    # 从标签中提取数字 (1, 2, 3)
    numbers = [str(num) for num in [1, 2, 3] if str(num) in label]
    return ','.join(numbers) if numbers else ''

# 创建新列
data['binary_label'] = data['label'].apply(process_label)
data['numbers'] = data['label'].apply(extract_numbers)

# 保留必要列并按要求顺序排列
processed_data = data[['response', 'label', 'binary_label', 'numbers']]

# 保存处理后的数据到新的 Excel 文件
output_path = 'processed_labeled_data.xlsx'  # 替换为你需要保存的路径
processed_data.to_excel(output_path, index=False)

print(f"处理后的文件已保存为: {output_path}")
