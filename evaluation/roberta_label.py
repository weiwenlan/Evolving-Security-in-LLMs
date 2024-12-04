from transformers import RobertaForSequenceClassification, RobertaTokenizer
import torch
from tqdm import tqdm


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
    

import sqlite3

def classify_responses(db_path, predictor):
    """
    Reads responses from the attacked_requests table, classifies them as safe (0) or unsafe (1),
    and updates the answer_category field with the classification results.

    Args:
        db_path (str): Path to the SQLite database file.
        predictor (Predictor): Instance of a predictor class (e.g., RoBERTaPredictor).
    """
    # Connect to the database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()



    try:
        # Select responses where answer_category is NULL and status is 'completed'
        cursor.execute('SELECT id, response FROM chat_requests WHERE answer_category IS "unknown" AND status = "completed"')
        rows = cursor.fetchall()
        print(f"Number of rows fetched: {len(rows)}")

        # Add tqdm for progress tracking
        for row in tqdm(rows, desc="Processing rows"):
            request_id, response = row
            if response:
                # Predict the category (0: safe, 1: unsafe)
                result = predictor.predict([response])[0]  # Predict returns a list, take the first item
                result = "safe" if result == 0 else "unsafe"

                # Update the answer_category in the database
                cursor.execute(
                    'UPDATE chat_requests SET answer_category = ? WHERE id = ?',
                    (result, request_id)
                )

        # Commit the changes to the database
        connection.commit()


    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()

    finally:
        # Close the database connection
        connection.close()


if __name__ == "__main__":
    # Initialize the predictor
    predictor = RoBERTaPredictor('hubert233/GPTFuzz', device='mps')

    # Path to the SQLite database
    db_path = "evaluation/roberta_test.db"

    # Process the responses
    classify_responses(db_path, predictor)

