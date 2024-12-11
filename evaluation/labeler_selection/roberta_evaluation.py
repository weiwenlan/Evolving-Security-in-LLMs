from transformers import RobertaForSequenceClassification, RobertaTokenizer
import torch
from tqdm import tqdm
import pandas as pd

class Predictor:
    def __init__(self, path):
        self.path = path

    def predict(self, sequences):
        raise NotImplementedError("Predictor must implement predict method.")


class RoBERTaPredictor(Predictor):
    def __init__(self, path, device='cuda'):
        super().__init__(path)
        self.device = device
        self.model = RobertaForSequenceClassification.from_pretrained(
            self.path).to(self.device)
        self.tokenizer = RobertaTokenizer.from_pretrained(self.path)

    def predict(self, sequences):
        inputs = self.tokenizer(sequences, padding=True, truncation=True,
                                max_length=512, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)

        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        _, predicted_classes = torch.max(predictions, dim=1)
        predicted_classes = predicted_classes.cpu().tolist()
        return predicted_classes
    

def classify_responses_and_append(file_path, predictor, output_path):
    """
    Reads an Excel file containing 'gpt_evaluation' column, adds a new column
    for RoBERTa's predictions, and saves the updated file.

    Args:
        file_path (str): Path to the input Excel file.
        predictor (Predictor): Instance of a predictor class (e.g., RoBERTaPredictor).
        output_path (str): Path to save the updated Excel file.
    """
    # Load the Excel file
    data = pd.read_excel(file_path)

    # Check if the required columns exist
    if 'response' not in data.columns or 'gpt_evaluation' not in data.columns:
        raise ValueError("The input file must contain 'response' and 'gpt_evaluation' columns.")

    # Initialize a list to store results
    roberta_results = []

    # Add tqdm for progress tracking
    for response in tqdm(data['response'], desc="Classifying responses with RoBERTa"):
        if pd.notnull(response):  # Ensure response is not NaN
            # Predict the category (0: safe, 1: unsafe)
            result = predictor.predict([response])[0]  # Predict returns a list, take the first item
            result = "safe" if result == 0 else "unsafe"
            roberta_results.append(result)
        else:
            roberta_results.append(None)  # Append None if the response is NaN

    # Add the results to a new column
    data['roberta_evaluation'] = roberta_results

    # Save the updated data to a new Excel file
    data.to_excel(output_path, index=False)
    print(f"Updated file saved to: {output_path}")


if __name__ == "__main__":
    # Initialize the predictor
    predictor = RoBERTaPredictor('hubert233/GPTFuzz', device='cpu')

    # Path to the input Excel file (with GPT labels)
    input_file_path = "/Users/austins/Adversarial-Attacks-on-LLM/evaluation/response_evaluation_with_tqdm.xlsx"  # Replace with your GPT-labeled file path

    # Path to save the updated Excel file
    output_file_path = "/Users/austins/Adversarial-Attacks-on-LLM/evaluation/final_classified_data.xlsx"

    # Process the responses
    classify_responses_and_append(input_file_path, predictor, output_file_path)
