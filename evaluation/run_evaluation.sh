#!/bin/bash

# Define the db paths and output file names
declare -A db_paths=(
    # [cipher]="/Users/austins/Adversarial-Attacks-on-LLM/data/500/cipherChat_llama3.18b_500_chat_requests.db"
    [gptfuzz0]="/Users/austins/Adversarial-Attacks-on-LLM/data/500/GPTFuzz_llama3.1_8b_500_chat_requests.db"
    [jailbroken1]="/Users/austins/Adversarial-Attacks-on-LLM/data/500/jailbroken_llama3.1_8b_500_chat_requests.db"
    [renellm2]="/Users/austins/Adversarial-Attacks-on-LLM/data/500/reNeLLM_llama3.1_8b_500_chat_requests.db"

)

# Loop through each db_path
for key in "${!db_paths[@]}"; do
    echo "Processing key: $key"  # Debugging: print the key
    db_path="${db_paths[$key]}"
    output_file="output_${key}.txt"

    echo "Running gpt_label.py with db_path: $db_path" | tee "$output_file"
    python gpt_label.py --db_path "$db_path" >> "$output_file" 2>&1

    if [ $? -eq 0 ]; then
        echo "Execution for $key completed successfully." | tee -a "$output_file"
    else
        echo "Execution for $key failed. Check details above." | tee -a "$output_file"
    fi

done

echo "All tasks completed."
