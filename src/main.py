import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import anthropic
# from fastchat.model import load_model

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
LLAMA_API_URL = os.getenv("LLAMA_API_URL")

app = FastAPI()

# Define a request model
class ChatRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 150
    temperature: float = 0.7

# Load FastChat models (assuming they are available locally or accessible)
# llama_model = load_model('llama')

@app.post("/chat")
async def chat(request: ChatRequest):
    model = request.model.lower()
    prompt = request.prompt
    max_tokens = request.max_tokens
    temperature = request.temperature

    try:
        if model in ["gpt-4o", "gpt-3.5-turbo"]:
            # Send request to OpenAI API
            if not OPENAI_API_KEY:
                raise HTTPException(status_code=500, detail="OpenAI API key not configured.")
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return {"response": response.choices[0].message['content'].strip()}

        elif model == "claude-3-5-sonnet":
            # Send request to Claude API using anthropic library
            if not CLAUDE_API_KEY:
                raise HTTPException(status_code=500, detail="Claude API key not configured.")
            
            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            response = client.completions.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens_to_sample=max_tokens,
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:"
            )
            return {"response": response['completion'].strip()}

        elif model == "llama":
            # Use FastChat to interact with LLaMA model
            if 'llama_model' not in globals():
                raise HTTPException(status_code=500, detail="LLaMA model not loaded.")
            response = llama_model.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return {"response": response}

        else:
            raise HTTPException(status_code=400, detail="Model not supported. Use 'gpt-4o', 'gpt-3.5-turbo', 'claude-3-5-sonnet', or 'llama'.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application using Uvicorn or any ASGI server
# Example: `uvicorn main:app --reload`
