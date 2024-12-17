import pandas as pd
from sklearn.metrics import confusion_matrix

# Load the Excel file
file_path = '/Users/austins/Adversarial-Attacks-on-LLM/evaluation/labeler_selection/labeler_evaluation_set.xlsx'
data = pd.ExcelFile(file_path)

# Load the first sheet
df = data.parse('Sheet1')

def gpt_label_process(label:str):
    if "gpt_safe" in label:
        return 0
    elif "gpt_unsafe" in label:
        return 1
    else:
        return -1

def roberta_label_process(label:str):
    if 'unsafe' in label:
        return 1
    elif 'safe' in label:
        return 0
    else:
        return -1

# Map binary_label to 0 (safe) and 1 (unsafe)
df['ground_truth'] = df['ground_truth'].map({'safe': 0, 'unsafe': 1})

# Map gpt_evaluation to binary values
df['gpt4o_pred'] = df['gpt-4o_evaluation'].apply(gpt_label_process)

# Map gpt_evaluation to binary values
df['gpt4o_mini_pred'] = df['gpt-4o-mini_evaluation'].apply(gpt_label_process)

# Map roberta_evaluation to binary values
df['roberta_pred'] = df['roberta_evaluation'].apply(roberta_label_process)

valid_rows = df[(df['ground_truth'].isin([0, 1])) & 
                (df['gpt4o_pred'].isin([0, 1])) & 
                (df['gpt4o_mini_pred'].isin([0, 1])) & 
                (df['roberta_pred'].isin([0, 1]))]

false_negative_rows = df[(df['ground_truth']==1) & 
                (df['gpt4o_pred']==0) & 
                (df['gpt4o_mini_pred']==0) & 
                (df['roberta_pred']==0)]

invalid_rows = df[~df.index.isin(valid_rows.index)] 
# invalid_rows.to_excel('invalid_rows.xlsx', index=False)
false_negative_rows.to_excel('false_negative_rows.xlsx', index=False)
print("Invalid rows:")
print(invalid_rows)

# Compute confusion matrices
x = 100000
roberta_cm = confusion_matrix(valid_rows['ground_truth'][:x], valid_rows['roberta_pred'][:x])
gpt4o_cm = confusion_matrix(valid_rows['ground_truth'][:x], valid_rows['gpt4o_pred'][:x])
gpt4omini_cm = confusion_matrix(valid_rows['ground_truth'][:x], valid_rows['gpt4o_mini_pred'][:x])

# Function to calculate performance metrics
def calculate_metrics(cm):
    tn, fp, fn, tp = cm.ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return accuracy, precision, recall, f1_score

# Compute metrics for GPT-4 and Roberta
roberta_metrics = calculate_metrics(roberta_cm)
gpt4o_metrics = calculate_metrics(gpt4o_cm)
gpt4omini_metrics = calculate_metrics(gpt4omini_cm)

# Create a comparison table
metrics_df = pd.DataFrame({
    'Metric': ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
    'Roberta': roberta_metrics,
    'GPT-4o': gpt4o_metrics,
    'GPT-4o-mini': gpt4omini_metrics
})

# Display results
print("\nConfusion Matrix for Roberta:")
print(roberta_cm)
print("Confusion Matrix for GPT-4:")
print(gpt4o_cm)
print("\nConfusion Matrix for GPT-4o-mini:")
print(gpt4omini_cm)
print("\nPerformance Comparison:")
print(metrics_df)
