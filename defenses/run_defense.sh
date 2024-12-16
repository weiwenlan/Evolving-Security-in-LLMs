methods=("llama_guard" "goal_prioritization") 

db_paths=(
    "/Users/austins/Adversarial-Attacks-on-LLM/data/500/llama31-70b/cipherChat_llama3.1_70b_chat_requests_500.db"
    "/Users/austins/Adversarial-Attacks-on-LLM/data/500/llama31-70b/GPTFuzz_llama3.1_70b_chat_requests_500.db"
    "/Users/austins/Adversarial-Attacks-on-LLM/data/500/llama31-70b/jailbroken_llama_3.1_70b_chat_requests_500.db"
    "/Users/austins/Adversarial-Attacks-on-LLM/data/500/llama31-70b/reNeLLM_llama3.1_70b_chat_requests_500.db"
)

# db_paths=(
#       "/Users/austins/Adversarial-Attacks-on-LLM/data/500/gpt-3.5-turbo/cipherChat_gpt3.5_chat_requests_500.db"
# )

# target_model='gpt-3.5-turbo'
target_model='llama31-70b'

for method in "${methods[@]}"; do
  echo "Starting method: $method"
  for db_path in "${db_paths[@]}"; do
    db_name=$(basename "$db_path")
    output_file="${method}_${db_name}_${target_model}.txt"
    nohup python defenses.py --defense_method "$method" --db_path "$db_path" --target_model "$target_model" > "$output_file" 2>&1 &
    echo "Started $method on $db_path, output saved to $output_file"
  done
  wait
  echo "All tasks for method $method completed."
done

echo "All methods completed for all files."
