
from google.protobuf.struct_pb2 import Value
from google.protobuf import json_format
from google.cloud import aiplatform
from huggingface_hub import InferenceClient
from transformers import pipeline
import openai
import logging
import time
import concurrent.futures
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import replicate
import os


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

        if model_path not in ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o']:
            raise ValueError(
                'OpenAI model path should be gpt-3.5-turbo or gpt-4-turbo or gpt-4o')
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


class LlamaLLM(LLM):
    def __init__(self, model_path, api_key, system_message=None):
        super().__init__()

        self.model_path = model_path
        self.system_message = system_message if system_message is not None else "You are a helpful assistant."

        # Initialize the text generation pipeline
        try:
            self.client = InferenceClient(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Failed to load model {model_path}. Error: {e}")

    def generate(self, prompt, temperature=0.7, max_tokens=512, max_trials=3, failure_sleep_time=5):
        for attempt in range(max_trials):
            try:
                # Prepare the input message format
                messages = [
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt},
                ]

                # Call the generation pipeline
                response = self.client.chat.completions.create(
                    model=self.model_path, messages=messages, max_tokens=max_tokens, temperature=temperature)
                # Assumes response contains 'generated_text'
                return response.choices[0].message.content
            except Exception as e:
                logging.warning(f"Model generation failed: {
                                e}. Retry {attempt + 1}/{max_trials}")
                time.sleep(failure_sleep_time)

        # Return a default message if all retries fail
        return "Failed to generate response."


class ReplicateLLM(LLM):
    def __init__(self, model_path, api_key, system_prompt=None):
        super().__init__()
        os.environ['REPLICATE_API_TOKEN'] = api_key
        self.model_path = model_path
        self.system_prompt = system_prompt if system_prompt is not None else "You are a helpful assistant."

    def generate(self, prompt, temperature=0.7, max_tokens=512, max_trials=3, failure_sleep_time=5):
        for attempt in range(max_trials):
            try:
                # Prepare the input message format
                messages = {
                    "top_p": 1,
                    "system_prompt": self.system_prompt,
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    "min_new_tokens": -1
                }
                response = replicate.run(
                    self.model_path,
                    input=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                return response
            except Exception as e:
                logging.warning(f"Model generation failed: {
                                e}. Retry {attempt + 1}/{max_trials}")
                time.sleep(failure_sleep_time)

        # Return a default message if all retries fail
        return "Failed to generate response."


class VertexLLM:
    def __init__(self, model_path, project, endpoint_id, location, system_prompt=None):

        self.project = project
        self.model_path = model_path
        self.endpoint_id = endpoint_id
        self.location = location
        self.api_endpoint = f"{location}-aiplatform.googleapis.com"
        self.client_options = {"api_endpoint": self.api_endpoint}
        self.client = aiplatform.gapic.PredictionServiceClient(
            client_options=self.client_options)
        self.system_prompt = system_prompt if system_prompt else "You are a helpful assistant."

    def generate(self, prompt, max_tokens=1024, temperature=0.7, n=1, max_trials=3, failure_sleep_time=5):

        # 构建完整的 Prompt
        full_prompt = f"### Human: \n {
            self.system_prompt} \n Question:{prompt}\n### Assistant: \n"

        # 构建实例输入
        instances = [
            {
                "prompt": full_prompt,
                "n": n,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        ]
        instances_proto = [
            json_format.ParseDict(instance, Value()) for instance in instances
        ]

        # 获取 Endpoint 路径
        endpoint = self.client.endpoint_path(
            project=self.project, location=self.location, endpoint=self.endpoint_id)

        # 调用模型并处理响应
        for attempt in range(max_trials):
            try:
                response = self.client.predict(
                    endpoint=endpoint, instances=instances_proto)
                prediction_str = response.predictions[0]
                output_index = prediction_str.find("Output:")
                if output_index != -1:
                    return prediction_str[output_index + len("Output:"):].strip()
                return prediction_str.strip()
            except Exception as e:
                logging.warning(f"Vertex prediction failed: {
                                e}. Retry {attempt + 1}/{max_trials}")
                time.sleep(failure_sleep_time)

        # 返回默认响应，如果所有尝试均失败
        return "Failed to generate response."

class VertexHuggingFaceLLM:
    def __init__(self, model_path, project, endpoint_id, location, system_prompt=None):

        self.project = project
        self.model_path = model_path
        self.endpoint_id = endpoint_id
        self.location = location
        self.api_endpoint = f"{location}-aiplatform.googleapis.com"
        self.client_options = {"api_endpoint": self.api_endpoint}
        self.client = aiplatform.gapic.PredictionServiceClient(
            client_options=self.client_options)
        self.system_prompt = system_prompt if system_prompt else "You are a helpful assistant."

    def generate(self, prompt, max_tokens=1024, temperature=0.7, n=1, max_trials=3, failure_sleep_time=5):

        # 构建完整的 Prompt
        full_prompt = f"### Human: \n {
            self.system_prompt} \n Question:{prompt}\n### Assistant: \n"

        # 构建实例输入
        instances = [
            {
                "inputs": full_prompt,
                "parameters": {
                    "max_tokens": max_tokens
                }
            }
        ]
        instances_proto = [
            json_format.ParseDict(instance, Value()) for instance in instances
        ]

        # 获取 Endpoint 路径
        endpoint = self.client.endpoint_path(
            project=self.project, location=self.location, endpoint=self.endpoint_id)

        # 调用模型并处理响应
        for attempt in range(max_trials):
            try:
                response = self.client.predict(
                    endpoint=endpoint, instances=instances_proto)
                prediction_str = response.predictions
                return prediction_str[0]
            except Exception as e:
                logging.warning(f"Vertex prediction failed: {
                                e}. Retry {attempt + 1}/{max_trials}")
                time.sleep(failure_sleep_time)

        # 返回默认响应，如果所有尝试均失败
        return "Failed to generate response."
    
class MistralLLM:
    def __init__(self, model_path=None, base_url=None, system_message=None, api_key=None):

        self.model_path = model_path
        self.base_url = base_url
        self.system_message = system_message if system_message is not None else "You are a helpful assistant."
        try:
            if self.model_path not in ["mistralai/Mistral-7B-Instruct-v0.1"]:
                self.client = InferenceClient(
                    model=self.model_path,
                    api_key=api_key)
            else:
                self.client = InferenceClient(
                    base_url=self.base_url,
                    api_key=api_key)
        except Exception as e:
            raise ValueError(f"Failed to load model {model_path}. Error: {e}")

    def generate(self, prompt, max_tokens=1024, temperature=0.7, n=1, max_trials=3, failure_sleep_time=5):

        for attempt in range(max_trials):
            try:

                # Prepare the input message format
                messages = [
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt},
                ]

                # Call the generation pipeline
                response = self.client.chat.completions.create( 
                    messages=messages, 
                    max_tokens=max_tokens, 
                    temperature=temperature)
                # Assumes response contains 'generated_text'
                return response.choices[0].message.content
            except Exception as e:
                logging.warning(f"Model generation failed: {e}. Retry {attempt + 1}/{max_trials}")
                time.sleep(failure_sleep_time)

        # Return a default message if all retries fail
        return "Failed to generate response."