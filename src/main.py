import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import anthropic
import google.generativeai as genai
from ratelimit import limits, sleep_and_retry
from huggingface_hub import InferenceClient

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Rate limit configuration for Claude API
RATE_LIMIT_CALLS = 5  # number of calls allowed
RATE_LIMIT_PERIOD = 5  # period in seconds

app = FastAPI()


class ChatRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 512


@sleep_and_retry
@limits(calls=RATE_LIMIT_CALLS, period=RATE_LIMIT_PERIOD)
def send_claude_request(model, prompt, max_tokens, system_prompt):
    # Send request to Claude API using anthropic library
    if not CLAUDE_API_KEY:
        raise HTTPException(
            status_code=500, detail="Claude API key not configured.")
    # https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return response.content[0].text


@app.post("/chat")
async def chat(request: ChatRequest):
    model = request.model
    prompt = request.prompt
    max_tokens = request.max_tokens
    system_prompt = getattr(request, "system_prompt",
                            "You are a helpful assistant.")

    try:
        if model in ["chatgpt-4o-latest", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o"]:
            # Send request to OpenAI API
            if not OPENAI_API_KEY:
                raise HTTPException(
                    status_code=500, detail="OpenAI API key not configured.")
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content":  system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
            )
            return {"response": response.choices[0].message['content'].strip()}

        elif model in ["claude-3-5-sonnet-20241022", "claude-3-sonnet-20240229", "claude-3-5-haiku-20241022", "claude-3-haiku-20240307", "claude-3-opus-latest"]:
            # Send request to Claude API using anthropic library with rate limiting
            return {"response": send_claude_request(model, prompt, max_tokens, system_prompt)}

        elif model in ["gemini-1.5-flash-8b-001", "gemini-1.5-flash-001", "gemini-1.5-pro-001"]:
            # Send request to Google Generative AI
            if not GOOGLE_API_KEY:
                raise HTTPException(
                    status_code=500, detail="Google API key not configured.")

            generative_model = genai.GenerativeModel(
                model_name=model,
                system_instruction=[
                    system_prompt,
                ],
            )
            response = generative_model.generate_content(prompt)
            return {"response": response.text.strip()}

        elif model in ["meta-llama/Llama-3.2-3B-Instruct"]:
            client = InferenceClient(api_key=HUGGINGFACE_API_KEY)
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
            return completion.choices[0].message.content

        else:
            raise HTTPException(
                status_code=400, detail="Model not supported. Use 'gpt-4o', 'gpt-3.5-turbo', 'claude-3-5-sonnet', or 'gemini-1.5-flash'.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application using Uvicorn or any ASGI server
# Example: `uvicorn main:app --reload`
