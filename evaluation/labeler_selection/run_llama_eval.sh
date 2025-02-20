#!/bin/bash

# 定义参数
FILE="labeler_evaluation_set.xlsx"
SYSTEM_PROMPTS=("basic" "detailed")
MODELS=("")
BASE_URL=""

# 创建一个日志目录（可选）
mkdir -p logs

# 遍历所有组合
for PROMPT in "${SYSTEM_PROMPTS[@]}"; do
    for MODEL in "${MODELS[@]}"; do
        echo "Running evaluation with system_prompt: $PROMPT and model: $MODEL"
        python llama_evaluation.py --file "$FILE" --system_prompt "$PROMPT" --model "$MODEL" --base_url "$BASE_URL" > "logs/eval_${PROMPT}_${MODEL//\//-}.log" 2>&1 &
    done
done

# 等待所有后台进程完成
wait

echo "All evaluations completed."

