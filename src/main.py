import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import anthropic
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI()

# Define a request model
class ChatRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 150
    temperature: float = 0.7

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

        elif model == "grok":
            # Send request to Grok API using OpenAI library
            if not XAI_API_KEY:
                raise HTTPException(status_code=500, detail="XAI API key not configured.")
            
            client = openai.OpenAI(
                api_key=XAI_API_KEY,
                base_url="https://api.x.ai/v1",
            )
            response = client.ChatCompletion.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return {"response": response.choices[0].message['content'].strip()}

        elif model == "gemini-1.5-flash":
            # Send request to Google Generative AI
            if not GOOGLE_API_KEY:
                raise HTTPException(status_code=500, detail="Google API key not configured.")
            
            generative_model = genai.GenerativeModel('gemini-1.5-flash')
            response = generative_model.generate_content(prompt)
            return {"response": response.text.strip()}

        else:
            raise HTTPException(status_code=400, detail="Model not supported. Use 'gpt-4o', 'gpt-3.5-turbo', 'claude-3-5-sonnet', 'grok', or 'gemini-1.5-flash'.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application using Uvicorn or any ASGI server
# Example: `uvicorn main:app --reload`
