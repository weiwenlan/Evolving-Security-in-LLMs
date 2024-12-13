#!/bin/bash

# # 第一次运行，指定第一个 db_path 和输出文件
# nohup python defenses.py --defense_method smooth_llm --db_path "/Users/austins/Adversarial-Attacks-on-LLM/data/500/jailbroken_llama3.1_8b_500_chat_requests.db" > jailbroken.txt 2>&1 &

# # 第二次运行，指定第二个 db_path 和输出文件
# nohup python defenses.py --defense_method smooth_llm --db_path "/Users/austins/Adversarial-Attacks-on-LLM/data/500/reNeLLM_llama3.1_8b_500_chat_requests.db" --model > renellm.txt 2>&1 &

#!/bin/bash

methods=("smooth_llm")

db_paths=(
    "/Users/austins/Adversarial-Attacks-on-LLM/data/500/jailbroken_llama3.1_8b_500_chat_requests.db"
    "/Users/austins/Adversarial-Attacks-on-LLM/data/500/reNeLLM_llama3.1_8b_500_chat_requests.db"
)

for method in "${methods[@]}"; do
  echo "Starting method: $method"
  for db_path in "${db_paths[@]}"; do
    db_name=$(basename "$db_path" .db)
    output_file="${method}_${db_name}.txt"
    nohup python defenses.py --defense_method "$method" --db_path "$db_path" > "$output_file" 2>&1 &
    echo "Started $method on $db_path, output saved to $output_file"
  done
  wait
  echo "All tasks for method $method completed."
done

echo "All methods completed for all files."
