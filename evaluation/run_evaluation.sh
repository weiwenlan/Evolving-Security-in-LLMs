#!/bin/bash

# Define the evaluation models and database paths
db_paths=(
    "/Users/austins/Adversarial-Attacks-on-LLM/data/500/evaluated/llama3-70b/cipherChat_llama3.1_70b_chat_requests_500.db"
    "/Users/austins/Adversarial-Attacks-on-LLM/data/500/evaluated/llama3-70b/GPTFuzz_llama3.1_70b_chat_requests_500.db"
)

evaluation_model="gpt-4o-mini"
label_evaluation='yes'
get_metrics='yes'

# Loop through each database path
for db_path in "${db_paths[@]}"; do
  db_name=$(basename "$db_path")
  output_file="${db_name}_label_output.txt"
  nohup python gpt_label.py \
    --evaluation_model "$evaluation_model" \
    --db_path "$db_path" \
    --label_evaluation "$label_evaluation" \
    --get_metrics "$get_metrics" > "$output_file" 2>&1 &
  echo "Started evaluation using $evaluation_model on $db_path, output saved to $output_file"
done
wait
