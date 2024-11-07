import json
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
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
        if model == "openai":
            # Send request to OpenAI API
            if not OPENAI_API_KEY:
                raise HTTPException(status_code=500, detail="OpenAI API key not configured.")
            openai.api_key = OPENAI_API_KEY
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return {"response": response.choices[0].text.strip()}

        elif model == "claude":
            # Placeholder for sending request to Claude API (replace with actual API integration)
            if not CLAUDE_API_KEY:
                raise HTTPException(status_code=500, detail="Claude API key not configured.")
            # Example: Sending request to Claude's API
            response = "[Claude response to be implemented]"
            return {"response": response}

        elif model == "llama":
            # Use FastChat to interact with LLaMA model
            response = llama_model.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return {"response": response}

        else:
            raise HTTPException(status_code=400, detail="Model not supported. Use 'openai', 'claude', or 'llama'.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application using Uvicorn or any ASGI server
# Example: `uvicorn main:app --reload`
