# extended_gpt_fuzzer.py

import sqlite3
import pandas as pd
import logging
import os
import openai
import time
from dotenv import load_dotenv
import concurrent.futures
# from gptfuzzer.llm import OpenAILLM, LocalVLLM, LocalLLM, PaLM2LLM, ClaudeLLM
# from gptfuzzer.utils.predict import RoBERTaPredictor
from gptfuzzer.fuzzer.mutator import (
    MutateRandomSinglePolicy, OpenAIMutatorCrossOver, OpenAIMutatorExpand,
    OpenAIMutatorGenerateSimilar, OpenAIMutatorRephrase, OpenAIMutatorShorten)
from gptfuzzer.fuzzer import GPTFuzzer
from gptfuzzer.fuzzer.selection import MCTSExploreSelectPolicy



class OpenAILLM:
    def __init__(self, model_path, api_key, system_message=None):

        # Set the API key
        openai.api_key = api_key
        
        # Validate model path
        supported_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o']
        if model_path not in supported_models:
            raise ValueError(f'OpenAI model path should be one of {supported_models}')
        
        self.model_path = model_path
        self.system_message = system_message or "You are a helpful assistant."

    def generate(self, prompt, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=5):
        for attempt in range(max_trials):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model_path,
                    messages=[
                        {"role": "system", "content": self.system_message},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=n,
                )
                return [choice['message']['content'].strip() for choice in response['choices']]
            except Exception as e:
                logging.warning(f"OpenAI API call failed due to {e}. Retrying {attempt + 1} / {max_trials} times...")
                time.sleep(failure_sleep_time)
        return [""] * n

    def generate_batch(self, prompts, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=5):
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.generate, prompt, temperature, max_tokens, n, max_trials, failure_sleep_time): prompt for prompt in prompts}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        return results




class ExtendedGPTFuzzer(GPTFuzzer):
    def __init__(self,
                 questions: 'list[str]',
                 initial_seed: 'list[str]',
                 mutate_policy: 'MutatePolicy',
                 select_policy: 'SelectPolicy',
                 target: str = 'LLM',
                 predictor: str = 'Predictor',
                 max_query: int = -1,
                 max_jailbreak: int = -1,
                 max_reject: int = -1,
                 max_iteration: int = -1,
                 energy: int = 1,
                 result_file: str = None,
                 generate_in_batch: bool = False,
                 ):

        # Call the constructor of the parent class to initialize
        super().__init__(questions, target, predictor, initial_seed, mutate_policy,
                         select_policy, max_query, max_jailbreak, max_reject,
                         max_iteration, energy, result_file, generate_in_batch)

        # Initialize the SQLite database to store generated prompts
        self.db_path = 'fuzzing_prompts.db'
        self._initialize_database()

    def _initialize_database(self):
        # Create SQLite database and table if it does not exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GeneratedPrompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iteration INTEGER,
                seed TEXT,
                mutated_prompt TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def _save_prompt(self, iteration, seed, mutated_prompt):
        # Save the generated prompt to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO GeneratedPrompts (iteration, seed, mutated_prompt)
            VALUES (?, ?, ?)
        ''', (iteration, seed, mutated_prompt))
        conn.commit()
        conn.close()

    def run(self):
        logging.info("Fuzzing started!")
        try:
            while not self.is_stop():
                # Select a seed prompt using the selection policy
                seed = self.select_policy.select()

                # Generate a mutated prompt based on the seed
                mutated_results = self.mutate_policy.mutate_single(seed)

                # Intercept and save the generated prompts before evaluation
                for mutated_prompt in mutated_results:
                    self._save_prompt(self.current_iteration,
                                      seed, mutated_prompt)
                
                self.current_iteration += 1

                # Evaluate the mutated prompts
                # self.evaluate(mutated_results)

                # Update the state with the results of the evaluation
                # self.update(mutated_results)

                # Log the current status of the fuzzing process
                # self.log()

        except KeyboardInterrupt:
            logging.info("Fuzzing interrupted by user!")

        logging.info("Fuzzing finished!")
        self.raw_fp.close()


def main():
    # Load initial seed prompts from CSV file
    initial_seed = pd.read_csv("./datasets/prompts/GPTFuzzer.csv",)['text'].tolist()
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")    
    print(OPENAI_API_KEY)
    # Initialize the target model and predictor
    openai_model = OpenAILLM('gpt-4o', OPENAI_API_KEY)    
    # roberta_model = RoBERTaPredictor('hubert233/GPTFuzz', device='cuda:1')

    # Define the questions
    train_data = pd.read_csv('./data.csv')
    questions = train_data['goal'].tolist()

    # Initialize the mutate policy
    mutate_policy = MutateRandomSinglePolicy([
        # For reproduction only
        OpenAIMutatorCrossOver(openai_model, temperature=0.0),
        OpenAIMutatorExpand(openai_model, temperature=0.0),
        OpenAIMutatorGenerateSimilar(openai_model, temperature=0.0),
        OpenAIMutatorRephrase(openai_model, temperature=0.0),
        OpenAIMutatorShorten(openai_model, temperature=0.0)
    ], concatentate=True)

    # Initialize the select policy
    select_policy = MCTSExploreSelectPolicy()
    ALL_PROMPTS = 10

    # Create an instance of the extended fuzzer
    fuzzer = ExtendedGPTFuzzer(
        questions=questions,
        # target=target_model,
        # predictor=roberta_model,
        initial_seed=initial_seed,
        mutate_policy=mutate_policy,
        select_policy=select_policy,
        # energy=1,
        # max_jailbreak=1,
        # max_query=10,
        # generate_in_batch=True,
        max_iteration=ALL_PROMPTS,  # 调整样本数量
    )
    # Run the fuzzing process
    fuzzer.run()

if __name__ == "__main__":
    main()