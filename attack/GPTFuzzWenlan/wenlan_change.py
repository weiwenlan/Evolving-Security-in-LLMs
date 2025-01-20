import pandas as pd
from gptfuzzer.llm import OpenAILLM
from gptfuzzer.utils.predict import RoBERTaPredictor
from gptfuzzer.fuzzer.selection import MCTSExploreSelectPolicy
from gptfuzzer.fuzzer.mutator import (
    MutateRandomSinglePolicy, OpenAIMutatorCrossOver, OpenAIMutatorExpand,
    OpenAIMutatorGenerateSimilar, OpenAIMutatorRephrase, OpenAIMutatorShorten)
from gptfuzzer.fuzzer import GPTFuzzer
import random

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")


# Load OpenAI Model
openai_model_path = 'gpt-4-turbo'
openai_model = OpenAILLM(
    openai_model_path, OPENAI_API_KEY)

# Load Llama Model
from gptfuzzer.llm import LlamaLLM
huggingface_model_path = "meta-llama/Llama-2-7b-chat-hf"
huggingface_model = LlamaLLM(
    huggingface_model_path, HUGGINGFACE_API_KEY)


# from gptfuzzer.llm import VertexLLM
# project = os.getenv("VERTEX_PROJECT")
# endpoint_id = os.getenv("VERTEX_ENDPOINT_ID")
# location = os.getenv("VERTEX_LOCATION")
# vertex_model = VertexLLM(
#         model_path="vicuna-7b-v1.5",
#         project=project,
#         endpoint_id=endpoint_id,
#         location=location,
#         system_prompt="You are a helpful assistant."
#     )

from gptfuzzer.llm import VertexHuggingFaceLLM
project = os.getenv("VERTEX_PROJECT")
endpoint_id = os.getenv("VERTEX_ENDPOINT_ID")
location = os.getenv("VERTEX_LOCATION")
vertex_huggingface_model = VertexHuggingFaceLLM(
        model_path="vicuna-7b-v1.1",
        project=project,
        endpoint_id=endpoint_id,
        location=location,
        system_prompt="You are a helpful assistant."
    )

# Predictor model, we will add more predictor model in the future
roberta_model = RoBERTaPredictor('hubert233/GPTFuzz', device='mps')

# jailbreak template dataset used in GPTFuzzer, we are now testing other datasets and will add new datasets in the future
seed_path = 'datasets/prompts/GPTFuzzer.csv'
initial_seed = pd.read_csv(seed_path)['text'].tolist()

question_path = 'datasets/questions/question_list.csv'
questions_set = pd.read_csv(question_path)['text'].tolist()  # 100 questions
selected_questions = random.choices(questions_set, k=100)

### target model
target_model = vertex_huggingface_model
mutate_model = openai_model
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
    rate_limit= 10,
)


fuzzer.run()
