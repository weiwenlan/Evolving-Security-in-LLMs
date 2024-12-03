import time
import requests
import json

# Assuming model names are in this list, you can replace it with actual model names
model_names = ["chatgpt-4o-latest", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4-turbo", "claude-3-5-sonnet-20241022", "claude-3-sonnet-20240229", "claude-3-5-haiku-20241022",
               "claude-3-haiku-20240307", "claude-3-opus-latest", "gemini-1.5-flash-8b-001", "gemini-1.5-flash-001", "gemini-1.5-pro-001"]
fixed_prompt = "How many counties are in Texas?"  # Fixed prompt

# Function to send request


def send_chat_request(model_name, prompt):
    # Construct the payload using model and API details
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 0.7
    }
    response = requests.post("http://127.0.0.1:8000/chat",
                             headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json().get("response")
    else:
        raise Exception(f"Error in API request: {
                        response.status_code} - {response.text}")

# Record the response time for each model
response_times = {}

for model_name in model_names:
    start_time = time.time()  # Record start time
    for _ in range(10):
        try:
            response = send_chat_request(model_name, fixed_prompt)
        except Exception as e:
            print(f"Error with model {model_name}: {e}")
            # If there's an error, set response time to None
            response_times[model_name] = None
            continue

    end_time = time.time()  # Record end time
    response_time = end_time - start_time
    response_times[model_name] = response_time

# Output the response time for each model
for model_name, response_time in response_times.items():
    if response_time is not None:
        print(f"Model '{model_name}' response time: {
              response_time:.2f} seconds")
    else:
        print(f"Model '{model_name}' response time: Error occurred")

# Save the response times to a JSON file
with open("response_times.json", "w") as json_file:
    json.dump(response_times, json_file, indent=4)
