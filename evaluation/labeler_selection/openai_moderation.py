import os
import csv
import argparse
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv
import logging
import time
import openai

# Load environment variables (e.g., OpenAI API Key)
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.WARNING)

def evaluate_moderation(response_text, max_trials=3, failure_sleep_time=5):
    """
    Queries the OpenAI Moderation API to evaluate a response.

    Args:
        response_text (str): The model response to be evaluated.
        max_trials (int): Maximum retry attempts in case of failure.
        failure_sleep_time (int): Time (seconds) to wait before retrying.

    Returns:
        dict: Moderation API result with "flagged" status and category labels.
    """
    for attempt in range(max_trials):
        try:
            moderation_result = openai.Moderation.create(input=response_text)
            categories = moderation_result["results"][0]["categories"]
            flagged = moderation_result["results"][0]["flagged"]

            # Return structured evaluation
            return {
                "flagged": flagged,
                "categories": categories
            }
        except Exception as e:
            logging.warning(f"Moderation API request failed: {e}. Retrying {attempt + 1}/{max_trials}")
            time.sleep(failure_sleep_time)

    return {"error": "Failed to evaluate response after multiple retries."}

def main(args):
    """
    Reads input data, evaluates responses using OpenAI Moderation API, and saves results to a CSV file.

    Args:
        args (argparse.Namespace): Command-line arguments.
    """

    # Load input data
    file_path = args.file
    data = pd.read_excel(file_path)

    # Generate output CSV filename
    output_csv_path = f"openai_moderation_results.csv"

    # Create CSV file and write header
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ground_truth", "binary_gpt_response"])

    # Process responses and append results to CSV
    with open(output_csv_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        for index, row in tqdm(data.iterrows(), total=len(data), desc="Processing responses"):
            ground_truth = row['ground_truth']
            model_response = row['model_response']
            
            # Get moderation evaluation
            moderation_result = evaluate_moderation(model_response)
            binary_label = 1 if 'unsafe' in ground_truth else 0
            # Extract relevant fields
            flagged = moderation_result.get("flagged", "N/A")
            binary_openai_response = 1 if flagged else 0

            # Write result to CSV
            writer.writerow([binary_label, binary_openai_response])

    print(f"Processing completed. Results saved to: {output_csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate model responses using OpenAI Moderation API.")

    parser.add_argument(
        "--file",
        type=str,
        default="labeler_evaluation_set.xlsx",
        help="Path to the input Excel file."
    )

    args = parser.parse_args()
    main(args)
