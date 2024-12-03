import pandas as pd
from gptfuzzer.llm import OpenAILLM
from gptfuzzer.utils.predict import RoBERTaPredictor
from gptfuzzer.fuzzer.selection import MCTSExploreSelectPolicy
from gptfuzzer.fuzzer.mutator import (
    MutateRandomSinglePolicy, OpenAIMutatorCrossOver, OpenAIMutatorExpand,
    OpenAIMutatorGenerateSimilar, OpenAIMutatorRephrase, OpenAIMutatorShorten)
from gptfuzzer.fuzzer import GPTFuzzer
import random

openai_model_path = 'gpt-4'
openai_model = OpenAILLM(
    openai_model_path, "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")
# predictor model, we will add more predictor model in the future
roberta_model = RoBERTaPredictor('hubert233/GPTFuzz', device='mps')


# jailbreak template dataset used in GPTFuzzer, we are now testing other datasets and will add new datasets in the future
seed_path = 'datasets/prompts/GPTFuzzer.csv'
initial_seed = pd.read_csv(seed_path)['text'].tolist()

question_path = 'datasets/questions/question_list.csv'
questions_set = pd.read_csv(question_path)['text'].tolist()  # 100 questions
selected_questions = random.choices(questions_set, k=1)

fuzzer = GPTFuzzer(
    questions=selected_questions,
    initial_seed=initial_seed,
    target=openai_model,
    predictor=roberta_model,
    mutate_policy=MutateRandomSinglePolicy([
        OpenAIMutatorCrossOver(openai_model, temperature=0.0),
        OpenAIMutatorExpand(openai_model, temperature=1.0),
        OpenAIMutatorGenerateSimilar(openai_model, temperature=0.5),
        OpenAIMutatorRephrase(openai_model),
        OpenAIMutatorShorten(openai_model)],
        concatentate=True,
    ),
    select_policy=MCTSExploreSelectPolicy(),
    energy=1,
    max_jailbreak=10,
    max_query=500,
)

fuzzer.run()
