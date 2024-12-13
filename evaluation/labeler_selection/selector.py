import pandas as pd
from sklearn.metrics import confusion_matrix

# Load the Excel file
file_path = '/Users/austins/Adversarial-Attacks-on-LLM/evaluation/labeler_selection/both_classified_data.xlsx'
data = pd.ExcelFile(file_path)

# Load the first sheet
df = data.parse('Sheet1')

# Map binary_label to 0 (safe) and 1 (unsafe)
df['binary_label'] = df['binary_label'].map({'safe': 0, 'unsafe': 1})

# Map gpt_evaluation to binary values
df['gpt_pred'] = df['gpt_evaluation'].apply(lambda x: 0 if 'gpt_safe' in x else 1)

# Map gpt_evaluation to binary values
df['gpt4o_pred'] = df['gpt_4o_mini_evaluation'].apply(lambda x: 0 if 'gpt_safe' in x else 1)

# Map roberta_evaluation to binary values
df['roberta_pred'] = df['roberta_evaluation'].map({'safe': 0, 'unsafe': 1})

# Drop rows with NaN values in 'roberta_pred' column
df_cleaned = df.dropna(subset=['roberta_pred'])

# Compute confusion matrices
x = 100000
gpt_cm = confusion_matrix(df_cleaned['binary_label'][:x], df_cleaned['gpt_pred'][:x])
roberta_cm = confusion_matrix(df_cleaned['binary_label'][:x], df_cleaned['roberta_pred'][:x])
gpt4omini_cm = confusion_matrix(df_cleaned['binary_label'][:x], df_cleaned['gpt4o_pred'][:x])

# Function to calculate performance metrics
def calculate_metrics(cm):
    tn, fp, fn, tp = cm.ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return accuracy, precision, recall, f1_score

# Compute metrics for GPT-4 and Roberta
gpt_metrics = calculate_metrics(gpt_cm)
roberta_metrics = calculate_metrics(roberta_cm)
gpt4omini_metrics = calculate_metrics(gpt4omini_cm)

# Create a comparison table
metrics_df = pd.DataFrame({
    'Metric': ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
    'GPT-4': gpt_metrics,
    'Roberta': roberta_metrics,
    'GPT-4o-mini': gpt4omini_metrics
})

# Display results
print("Confusion Matrix for GPT-4:")
print(gpt_cm)
print("\nConfusion Matrix for Roberta:")
print(roberta_cm)
print("\nConfusion Matrix for GPT-4o-mini:")
print(gpt4omini_cm)
print("\nPerformance Comparison:")
print(metrics_df)
