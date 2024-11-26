
import openai
import logging
import time
import concurrent.futures
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT


class LLM:
    def __init__(self):
        self.model = None
        self.tokenizer = None

    def generate(self, prompt):
        raise NotImplementedError("LLM must implement generate method.")

    def predict(self, sequences):
        raise NotImplementedError("LLM must implement predict method.")


class ClaudeLLM(LLM):
    def __init__(self,
                 model_path='claude-instant-1.2',
                 api_key=None
                ):
        super().__init__()
        
        if len(api_key) != 108:
            raise ValueError('invalid Claude API key')
        
        self.model_path = model_path
        self.api_key = api_key
        self.anthropic = Anthropic(
            api_key=self.api_key
        )

    def generate(self, prompt, max_tokens=512, max_trials=1, failure_sleep_time=1):
        
        for _ in range(max_trials):
            try:
                completion = self.anthropic.completions.create(
                    model=self.model_path,
                    max_tokens_to_sample=300,
                    prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
                )
                return [completion.completion]
            except Exception as e:
                logging.warning(
                    f"Claude API call failed due to {e}. Retrying {_+1} / {max_trials} times...")
                time.sleep(failure_sleep_time)

        return [" "]
    
    def generate_batch(self, prompts, max_tokens=512, max_trials=1, failure_sleep_time=1):
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.generate, prompt, max_tokens,
                                       max_trials, failure_sleep_time): prompt for prompt in prompts}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        return results

class OpenAILLM(LLM):
    def __init__(self,
                 model_path,
                 api_key=None,
                 system_message=None
                ):
        super().__init__()

        if model_path not in ['gpt-3.5-turbo', 'gpt-4']:
            raise ValueError(
                'OpenAI model path should be gpt-3.5-turbo or gpt-4')
        openai.api_key = api_key
        self.model_path = model_path
        self.system_message = system_message if system_message is not None else "You are a helpful assistant."

    def generate(self, prompt, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=5):
        for _ in range(max_trials):
            try:
                results = openai.ChatCompletion.create(
                    model=self.model_path,
                    messages=[
                        {"role": "system", "content": self.system_message},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return [results.choices[i].message.content for i in range(n)]
            except Exception as e:
                logging.warning(
                    f"OpenAI API call failed due to {e}. Retrying {_+1} / {max_trials} times...")
                time.sleep(failure_sleep_time)

        return [" " for _ in range(n)]

    def generate_batch(self, prompts, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=5):
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.generate, prompt, temperature, max_tokens, n,
                                       max_trials, failure_sleep_time): prompt for prompt in prompts}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        return results
