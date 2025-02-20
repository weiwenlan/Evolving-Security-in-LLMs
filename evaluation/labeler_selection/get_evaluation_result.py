import pandas as pd
import argparse
import os
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

def calculate_metrics(cm):
    """
    计算混淆矩阵的指标，包括 Accuracy, Precision, Recall, F1 Score。
    
    Args:
        cm (numpy.ndarray): 混淆矩阵
    
    Returns:
        tuple: (accuracy, precision, recall, f1_score)
    """
    tp, fn, fp, tn = cm.ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return accuracy, precision, recall, f1

def process_csv(csv_path):
    """
    读取 CSV 计算混淆矩阵和性能指标。
    
    Args:
        csv_path (str): CSV 文件路径
    
    Returns:
        None
    """
    if not os.path.exists(csv_path):
        print(f"❌ 错误: 文件 '{csv_path}' 未找到。请检查文件路径。")
        return

    # 读取 CSV
    df = pd.read_csv(csv_path)

    # 确保数据包含所需的列
    required_columns = ["binary_ground_truth", "binary_gpt_response"]
    for col in required_columns:
        if col not in df.columns:
            print(f"❌ 错误: CSV 文件缺少所需列 '{col}'，请检查文件格式。")
            return

    # 过滤掉无效 (-1) 的数据
    valid_df = df[df["binary_gpt_response"] != -1]

    print('invalid rows', len(df) - len(valid_df))

    # 获取 Ground Truth 和 预测值
    y_true = valid_df["binary_ground_truth"]
    y_pred = valid_df["binary_gpt_response"]

    # 计算混淆矩阵
    cm = confusion_matrix(y_true, y_pred, labels=[1, 0])

    # 计算性能指标
    accuracy, precision, recall, f1 = calculate_metrics(cm)

    # 打印结果
    print("\n✅ 混淆矩阵:")
    print(pd.DataFrame(
        cm, 
        index=["实际正例 (1)", "实际负例 (0)"], 
        columns=["预测正例 (1)", "预测负例 (0)"]
    ))

    print("\n📊 评估指标:")
    print(f"🎯 Accuracy: {accuracy:.4f}")
    print(f"🎯 Precision: {precision:.4f}")
    print(f"🎯 Recall: {recall:.4f}")
    print(f"🎯 F1 Score: {f1:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="计算混淆矩阵和模型性能指标")

    parser.add_argument(
        "--csv",
        type=str,
        default="/Users/austins/Adversarial-Attacks-on-LLM/evaluation/labeler_selection/Meta-Llama-3.1-8B-Instruct_detailed.csv",
        help="输入 CSV 文件路径"
    )

    args = parser.parse_args()
    process_csv(args.csv)
