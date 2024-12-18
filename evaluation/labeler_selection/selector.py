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

def openai_moderation_process(label:str):
    if label == 1:
        return 1
    elif label == 0:
        return 0
    else:
        return -1

def calculate_metrics(cm):
    # tn, fp, fn, tp = cm.ravel()
    tp, fn, fp, tn = cm.ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return accuracy, precision, recall, f1_score

def get_all_evaluations(df: pd.DataFrame):
    # Map binary_label to 0 (safe) and 1 (unsafe)
    df['ground_truth'] = df['ground_truth'].map({'safe': 0, 'unsafe': 1})

    # Map gpt_evaluation to binary values
    df['gpt4o_pred'] = df['gpt-4o_evaluation'].apply(gpt_label_process)

    # Map gpt_evaluation to binary values
    df['gpt4o_mini_pred'] = df['gpt-4o-mini_evaluation'].apply(gpt_label_process)

    # Map roberta_evaluation to binary values
    df['roberta_pred'] = df['roberta_evaluation'].apply(roberta_label_process)

    # Map gpt_evaluation to binary values
    df['llama_pred'] = df['meta-llama/Meta-Llama-3.1-8B-Instruct_evaluation'].apply(gpt_label_process)

    df['openai_pred'] = df['openai_moderation_evaluation'].apply(openai_moderation_process)
    df['llama_guard_pred'] = df['llama_guard_evaluation'].apply(roberta_label_process)
    df['gpt4o_mini_no_sysprompt_pred'] = df['gpt-4o-mini_no_sysprompt_evaluation'].apply(gpt_label_process)
    df['gpt-4o-mini_improved_pred'] = df['gpt-4o-mini_improved_evaluation'].apply(gpt_label_process)
    df['llama31_70B_pred']=df['llama31_70B_evaluation'].apply(roberta_label_process)

    valid_rows = df[(df['ground_truth'].isin([0, 1])) & 
                    (df['gpt4o_pred'].isin([0, 1])) & 
                    (df['gpt4o_mini_pred'].isin([0, 1])) & 
                    (df['roberta_pred'].isin([0, 1])) &
                    (df['llama_pred'].isin([0, 1])) &
                    (df['openai_pred'].isin([0, 1])) & 
                    (df['llama_guard_pred'].isin([0, 1]))]

    # super_invalid_rows = df[(df['ground_truth'].isin([0, 1])) & 
    #                         (df['gpt4o_pred']==-1) & 
    #                         (df['gpt4o_mini_pred']==-1) & 
    #                         (df['llama_pred']==-1)]
    # super_invalid_rows.to_excel('super_invalid_rows.xlsx', index=False)

    # false_negative_rows = df[(df['ground_truth']==1) & 
    #                 (df['gpt4o_pred']==0) & 
    #                 (df['gpt4o_mini_pred']==0) & 
    #                 (df['roberta_pred']==0)]

    invalid_rows = df[~df.index.isin(valid_rows.index)] 
    # invalid_rows.to_excel('invalid_rows.xlsx', index=False)
    # false_negative_rows.to_excel('false_negative_rows.xlsx', index=False)
    print("Invalid rows:")
    print(invalid_rows)

    # Compute confusion matrices
    x = 100000
    roberta_cm = confusion_matrix(valid_rows['ground_truth'][:x], valid_rows['roberta_pred'][:x], labels=[1, 0] )
    gpt4o_cm = confusion_matrix(valid_rows['ground_truth'][:x], valid_rows['gpt4o_pred'][:x], labels=[1, 0])
    gpt4omini_cm = confusion_matrix(valid_rows['ground_truth'][:x], valid_rows['gpt4o_mini_pred'][:x], labels=[1, 0])
    llama_cm = confusion_matrix(valid_rows['ground_truth'][:x], valid_rows['llama_pred'][:x], labels=[1, 0])
    openai_cm = confusion_matrix(valid_rows['ground_truth'][:x], valid_rows['openai_pred'][:x], labels=[1, 0])
    llama_guard_cm = confusion_matrix(valid_rows['ground_truth'][:x], valid_rows['llama_guard_pred'][:x], labels=[1, 0])

    # Function to calculate performance metrics
    
    # Compute metrics for GPT-4 and Roberta
    roberta_metrics = calculate_metrics(roberta_cm)
    gpt4o_metrics = calculate_metrics(gpt4o_cm)
    gpt4omini_metrics = calculate_metrics(gpt4omini_cm)
    llama_metrics = calculate_metrics(llama_cm)
    openai_metrics = calculate_metrics(openai_cm)
    llama_guard_metrics = calculate_metrics(llama_guard_cm)

    # Create a comparison table
    metrics_df = pd.DataFrame({
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
        'Roberta': roberta_metrics,
        'OpenAI': openai_metrics,
        'Llama Guard': llama_guard_metrics,
        'GPT-4o': gpt4o_metrics,
        'GPT-4o-mini': gpt4omini_metrics,
        'Meta-Llama': llama_metrics      
    })

    # Display results
    print("\nConfusion Matrix for Roberta:")
    print(roberta_cm)
    print("\nConfusion Matrix for OpenAI:")
    print(openai_cm)
    print("\nConfusion Matrix for Llama Guard:")
    print(llama_guard_cm)
    print("\nConfusion Matrix for GPT-4:")
    print(gpt4o_cm)
    print("\nConfusion Matrix for GPT-4o-mini:")
    print(gpt4omini_cm) 
    print("\nConfusion Matrix for Meta-Llama:")
    print(llama_cm)
    print("\nPerformance Comparison:")
    print(metrics_df)

def get_one_evaluation(labeler: str, df: pd.DataFrame):
    df['ground_truth'] = df['ground_truth'].map({'safe': 0, 'unsafe': 1})
    if 'gpt' in labeler or 'meta-llama' in labeler or 'Instruct' in labeler:
        df['pred'] = df[labeler].apply(gpt_label_process)
    elif 'roberta' in labeler or 'llama_guard' in labeler:
        df['pred'] = df[labeler].apply(roberta_label_process)
    elif 'openai' in labeler:
        df['pred'] = df[labeler].apply(openai_moderation_process)
    valid_rows= df[(df['ground_truth'].isin([0, 1])) & (df['pred'].isin([0, 1]))]
    invalid_rows = df[~df.index.isin(valid_rows.index)]
    print("Invalid rows:")
    print(invalid_rows)

    false_negative_rows = df[(df['ground_truth']==1) & (df['pred']==0)]
    false_positive_rows = df[(df['ground_truth']==0) & (df['pred']==1)]
    false_negative_rows.to_excel(f'{labeler}_false_negative_rows.xlsx', index=False)
    false_positive_rows.to_excel(f'{labeler}_false_positive_rows.xlsx', index=False)

    cm = confusion_matrix(valid_rows['ground_truth'], valid_rows['pred'], labels=[1, 0])
    metrics = calculate_metrics(cm)
    print("\nConfusion Matrix:")
    print(cm)

    metrics_df = pd.DataFrame({
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
        labeler: metrics
    })

    print("\nPerformance Comparison:")
    print(metrics_df)


# gpt-4o_evaluation
# gpt-4o-mini_evaluation
# roberta_evaluation
# openai_moderation_evaluation
# llama_guard_evaluation
# meta-llama/Meta-Llama-3.1-8B-Instruct_evaluation
# gpt-4o-mini_no_sysprompt_evaluation
# gpt-4o-mini_improved_evaluation
# llama31_70B_evaluation
# gpt-3.5-turbo_improved2_evaluation
# gpt-4o_improved2_evaluation
# gpt-4o-mini_improved2_evaluation
# gpt-4o_improved2_haha_evaluation
# Meta-Llama-3.1-70B-Instruct_improved2_evaluation
get_one_evaluation('Meta-Llama-3.1-70B-Instruct_improved2_evaluation', df)
# get_all_evaluations(df)


