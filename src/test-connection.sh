curl -X POST "http://127.0.0.1:8000/chat" \
-H "Content-Type: application/json" \
-d '{
  "model": "gpt-4o",
  "prompt": "How many county in Texas.",
  "max_tokens": 100,
  "temperature": 0.7
}'
