#!/bin/bash

# 第一次运行，指定第一个 db_path 和输出文件
nohup python defenses.py --defense_method smooth_llm --db_path "/Users/austins/Adversarial-Attacks-on-LLM/sql/cipherChat_llama3.18b_500_chat_requests.db" > cipherchat.txt 2>&1 &

# 第二次运行，指定第二个 db_path 和输出文件
nohup python defenses.py --defense_method llama_guard --db_path "/Users/austins/Adversarial-Attacks-on-LLM/sql/GPTFuzz_llama3.1_8b_500_chat_requests.db" > gptfuzzer.txt 2>&1 &

echo "Both processes started. Check output1.txt and output2.txt for logs."

