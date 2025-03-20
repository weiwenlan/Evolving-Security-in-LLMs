#!/bin/bash

# Source database path
SOURCE_DB_PATH="./attacks.db"

# Model list (id and name from the image)
MODELS=(
  "11 mistralai/Mistral-7B-Instruct-v0.1"
  "12 mistralai/Mistral-7B-Instruct-v0.2"
  "13 mistralai/Mistral-7B-Instruct-v0.3"
  "14 mistralai/Mistral-Nemo-Instruct-2407"
)

# Loop through models and generate commands for each
for MODEL in "${MODELS[@]}"; do
  # Extract model ID and original model name
  MODEL_ID=$(echo $MODEL | awk '{print $1}')
  MODEL_NAME=$(echo $MODEL | awk '{print $2}')
  
  # Create sanitized database name
  DB_NAME="jailbroken_$(echo $MODEL_NAME | tr '[:upper:]' '[:lower:]' | tr '/-' '__')_chat_requests_500.db"
  
  # Create table
  python ../../sql/create_table.py --db-path ./${DB_NAME}
  
  # Insert data from source database
  python sample_insert.py --target-db-path ./${DB_NAME} --source-db-path ${SOURCE_DB_PATH}
  
  # Generate pending requests
  python ../../sql/generate_pending_request.py --db-path ./${DB_NAME} --model-id ${MODEL_ID} --model-name ${MODEL_NAME}
  
  # Generate experiment table
  python generate_experiment_table.py --db-path ./${DB_NAME}
done
