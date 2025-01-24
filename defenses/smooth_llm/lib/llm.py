
from transformers import pipeline
import openai
import logging
import os
import time
import concurrent.futures
from huggingface_hub import InferenceClient
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


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

        if model_path not in ['gpt-3.5-turbo', 'gpt-4-turbo']:
            raise ValueError(
                'OpenAI model path should be gpt-3.5-turbo or gpt-4-turbo')
        openai.api_key = api_key
        self.model_path = model_path
        self.system_message = system_message if system_message is not None else "You are a helpful assistant."

    def __call__(self, prompt, temperature=0, max_tokens=512, n=1, max_trials=3, failure_sleep_time=5):
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
                return [results.choices[i].message.content for i in range(n)][0]
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

from huggingface_hub import InferenceClient


class LlamaLLM(LLM):
    """
    LlamaLLM class for using a remote LLaMA-3 model via API.
    """
    def __init__(self, model_path, api_key, system_message=None):
        """
        Initialize the LlamaLLM with API configuration.
        
        Args:
            model_path (str): The model identifier (e.g., "meta-llama/Llama-3").
            api_key (str): Your Hugging Face API key.
            system_message (str, optional): The system message to guide the assistant's behavior.
        """
        super().__init__()
        self.model_path = model_path
        # self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.system_message = system_message if system_message is not None else "You are a helpful assistant."
        # self.llama = pipeline("text-generation", model=model_path)

        # Initialize the text generation pipeline
        try:
            self.client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))
        except Exception as e:
            raise ValueError(f"Failed to load model {model_path}. Error: {e}")

    # def __call__(self, batch, max_new_tokens=100):
    def __call__(self, prompt, temperature=0.7, max_tokens=512, max_trials=3, failure_sleep_time=5):
        """
        Generate text using the remote LLaMA-3 model.

        Args:
            prompt (str): The user input.
            temperature (float): Sampling temperature for generation diversity.
            max_tokens (int): Maximum number of tokens to generate.
            max_trials (int): Number of retries on failure.
            failure_sleep_time (int): Seconds to wait between retries.

        Returns:
            str: The generated response or a failure message.
        """
        for attempt in range(max_trials):
            try:

                # Prepare the input message format
                messages = [
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt},
                ]

                # Call the generation pipeline
                response = self.client.chat.completions.create( 
                    model=self.model_path,
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

class VertexLLM:
    def __init__(self, target_model, system_prompt=None):

        self.project = os.getenv("VERTEX_PROJECT")
        # self.model_path = model_path
        self.endpoint_id = os.getenv("VERTEX_ENDPOINT_ID")
        self.location = os.getenv("VERTEX_LOCATION")
        self.api_endpoint = f"{self.location}-aiplatform.googleapis.com"
        self.client_options = {"api_endpoint": self.api_endpoint}
        self.client = aiplatform.gapic.PredictionServiceClient(
            client_options=self.client_options)
        self.system_prompt = system_prompt if system_prompt else "You are a helpful assistant."

        # make sure that is the model we want to use.
        assert target_model == os.getenv("VERTEX_MODEL")

    def __call__(self, prompt, max_tokens=1024, temperature=0.7, n=1, max_trials=3, failure_sleep_time=5):

        full_prompt = f"### Human: \n {self.system_prompt} \n Question:{prompt}\n### Assistant: \n"

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

        endpoint = self.client.endpoint_path(
            project=self.project, location=self.location, endpoint=self.endpoint_id)

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
                logging.warning(f"Vertex prediction failed: {e}. Retry {attempt + 1}/{max_trials}")
                time.sleep(failure_sleep_time)

        return "Failed to generate response."


class MistralLLM(LLM):
    """
    A class for interacting with the Mistral AI model. can be both inference api or inference endpoint
    """
    def __init__(self, model_path=None, base_url=None, system_message=None):
        """

        """
        super().__init__()
        self.model_path = model_path
        self.base_url = base_url
        self.system_message = system_message if system_message is not None else "You are a helpful assistant."
        # warning: base_url won't work if model is set, https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client
        try:
            if self.model_path: # when using inference api, like mistral nemo/v0.2/v0.3
                print("using mistral model: ", self.model_path)
                self.client = InferenceClient(
                    model=self.model_path,
                    api_key=os.getenv("HUGGINGFACE_API_KEY"))
            elif not self.model_path and self.base_url: # for mistral v0.1 
                print("using mistral v0.1 model: ", self.base_url)
                self.client = InferenceClient(
                    base_url=self.base_url,
                    api_key=os.getenv("HUGGINGFACE_API_KEY"))
        except Exception as e:
            raise ValueError(f"Failed to load model {model_path}. Error: {e}")

    # def __call__(self, batch, max_new_tokens=100):
    def __call__(self, prompt, temperature=0.7, max_tokens=1024, max_trials=3, failure_sleep_time=5):
        """
        Generate text using the remote LLaMA-3 model.

        Args:
            prompt (str): The user input.
            temperature (float): Sampling temperature for generation diversity.
            max_tokens (int): Maximum number of tokens to generate.
            max_trials (int): Number of retries on failure.
            failure_sleep_time (int): Seconds to wait between retries.

        Returns:
            str: The generated response or a failure message.
        """
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