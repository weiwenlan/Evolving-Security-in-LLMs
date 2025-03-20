#!/bin/bash

# Check if the model_name argument is provided
if [ "$#" -ne 2 ] || [ "$1" != "--model_name" ]; then
    echo "Usage: sh wenlan_run.sh --model_name <model_name>"
    exit 1
fi

# Extract the model_name from arguments
MODEL_NAME=$2

# List of instruction types
INSTRUCTION_TYPES=(
    "Ethics_And_Morality"
    "Inquiry_With_Unsafe_Opinion"
    "Insult"
    "Mental_Health"
    "Physical_Harm"
    "Role_Play_Instruction"
    "Unfairness_And_Discrimination"
)

# Loop through instruction types and run the Python script
for INSTRUCTION_TYPE in "${INSTRUCTION_TYPES[@]}"; do
    python wenlan_main.py \
        --model_name "$MODEL_NAME" \
        --encode_method unchange \
        --instruction_type "$INSTRUCTION_TYPE" \
        --debug_num 40
done
