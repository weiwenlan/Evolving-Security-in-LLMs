import pandas as pd
from gptfuzzer.llm import OpenAILLM, LlamaLLM, VertexHuggingFaceLLM, MistralLLM
from gptfuzzer.utils.predict import RoBERTaPredictor
from gptfuzzer.fuzzer.selection import MCTSExploreSelectPolicy
from gptfuzzer.fuzzer.mutator import (
    MutateRandomSinglePolicy, OpenAIMutatorCrossOver, OpenAIMutatorExpand,
    OpenAIMutatorGenerateSimilar, OpenAIMutatorRephrase, OpenAIMutatorShorten)
from gptfuzzer.fuzzer import GPTFuzzer
from dotenv import load_dotenv
import os
import random
import argparse

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
PROJECT = os.getenv("VERTEX_PROJECT")
ENDPOINT_ID = os.getenv("VERTEX_ENDPOINT_ID")
LOCATION = os.getenv("VERTEX_LOCATION")

# Command-line argument parsing
parser = argparse.ArgumentParser(
    description="Run GPTFuzzer with specified model")
parser.add_argument("--model", type=str, required=True,
                    help="Specify the model to use")
args = parser.parse_args()

# Initialize the target model based on the --model argument
if args.model in ["gpt-3.5-turbo", "gpt-4-turbo"]:
    print("Initializing OpenAI model...")
    target_model = OpenAILLM(args.model, OPENAI_API_KEY)

elif args.model in ["meta-llama/Llama-2-7b-chat-hf", "meta-llama/Llama-2-70b-chat-hf", "meta-llama/Llama-3.1-8B-Instruct", "meta-llama/Llama-3.1-70B-Instruct"]:
    print("Initializing Llama model...")
    target_model = LlamaLLM(args.model, HUGGINGFACE_API_KEY)

elif args.model in ["mistralai/Mistral-7B-Instruct-v0.1", "mistralai/Mistral-7B-Instruct-v0.2", "mistralai/Mistral-7B-Instruct-v0.3", "mistralai/Mistral-Nemo-Instruct-2407"]:
    print("Initializing Mistral model...")
    if args.model == "mistralai/Mistral-7B-Instruct-v0.1":
        target_model = MistralLLM(
            model_path=args.model, base_url="https://qhh7ky18tucco2by.us-east-1.aws.endpoints.huggingface.cloud/v1/", api_key="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")
    else:
        target_model = MistralLLM(
            model_path=args.model, api_key=HUGGINGFACE_API_KEY)

elif args.model in ["vicuna-7b-v1.5", "vicuna-13b-v1.5", "vicuna-7b-v1.1", "vicuna-13b-v1.1"]:
    print("Initializing Vertex HuggingFace model...")
    target_model = VertexHuggingFaceLLM(
        model_path=args.model,
        project=PROJECT,
        endpoint_id=ENDPOINT_ID,
        location=LOCATION,
        system_prompt="You are a helpful assistant."
    )
else:
    raise ValueError(f"Invalid model selection: {args.model}")

# Assuming OpenAI model for mutation
mutate_model = OpenAILLM("gpt-4-turbo", OPENAI_API_KEY)
# Predictor model
roberta_model = RoBERTaPredictor('hubert233/GPTFuzz', device='mps')

# Load datasets
seed_path = 'datasets/prompts/GPTFuzzer.csv'
initial_seed = pd.read_csv(seed_path)['text'].tolist()

question_path = 'datasets/questions/question_list.csv'
questions_set = pd.read_csv(question_path)['text'].tolist()
selected_questions = random.choices(questions_set, k=100)

# Initialize GPTFuzzer
fuzzer = GPTFuzzer(
    questions=selected_questions,
    initial_seed=initial_seed,
    target=target_model,
    predictor=roberta_model,
    mutate_policy=MutateRandomSinglePolicy([
        OpenAIMutatorCrossOver(mutate_model, temperature=0.0),
        OpenAIMutatorExpand(mutate_model, temperature=1.0),
        OpenAIMutatorGenerateSimilar(mutate_model, temperature=0.5),
        OpenAIMutatorRephrase(mutate_model),
        OpenAIMutatorShorten(mutate_model)],
        concatentate=True,
    ),
    select_policy=MCTSExploreSelectPolicy(),
    energy=1,
    max_jailbreak=100,
    max_query=500,
    rate_limit=10,
)

# Run the fuzzer
fuzzer.run()
