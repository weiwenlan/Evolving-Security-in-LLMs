import pandas as pd


file_path = 'final_labeled_data.xlsx'  
data = pd.read_excel(file_path)

data.columns = ['response', 'label']

def process_label(label):
    label_lower = label.lower()
    if 'yes' in label_lower:
        binary_label = 'unsafe'
    elif 'no' in label_lower:
        binary_label = 'safe'
    else:
        binary_label = 'unknown' 
    return binary_label

def extract_numbers(label):
    numbers = [str(num) for num in [1, 2, 3] if str(num) in label]
    return ','.join(numbers) if numbers else ''

data['binary_label'] = data['label'].apply(process_label)
data['numbers'] = data['label'].apply(extract_numbers)

processed_data = data[['response', 'label', 'binary_label', 'numbers']]

output_path = 'processed_labeled_data.xlsx'  
processed_data.to_excel(output_path, index=False)

print(f"processed file is : {output_path}")
