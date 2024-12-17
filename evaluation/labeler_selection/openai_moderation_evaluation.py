import os
import argparse
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Set up your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def main(args):
    # Load the file
    file_path = args.file
    data = pd.read_excel(file_path)

    # Define the evaluation function using OpenAI Moderation API
    def evaluate_moderation(response_text):
        try:
            moderation_result = openai.Moderation.create(input=response_text)
            categories = moderation_result["results"][0]["categories"]
            flagged = moderation_result["results"][0]["flagged"]

            # Combine the results into a structured output
            evaluation = {
                "flagged": flagged,
                "categories": categories
            }
            return evaluation
        except Exception as e:
            return {"error": str(e)}

    # Add new columns for evaluation
    data["flagged"] = None
    data["categories"] = None
    data["error"] = None

    # Evaluate each response
    for index, row in tqdm(data.iterrows(), total=len(data), desc="Evaluating responses"):
        result = evaluate_moderation(row["model_response"])
        if "error" in result:
            data.at[index, "error"] = result["error"]
        else:
            data.at[index, "flagged"] = result["flagged"]
            data.at[index, "categories"] = ", ".join(
                [f"{k}: {v}" for k, v in result["categories"].items()]
            )

    # Save the updated data back to the same file
    data.to_excel(file_path, index=False)

    print(f"Moderation evaluation completed and saved to: {file_path}")


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
