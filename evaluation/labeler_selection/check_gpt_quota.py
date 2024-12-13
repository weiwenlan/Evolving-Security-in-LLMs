import os
import openai
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# 调用 GPT-4 模型
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Give me a summary of the latest AI trends."}
    ],
    max_tokens=150  # 限制输出长度
)

# 输出模型的回复
print("Model Response:")
print(response['choices'][0]['message']['content'])