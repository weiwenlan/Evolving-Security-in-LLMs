#!/bin/bash

# 定义要运行的 Python 文件
python_file="wenlan_change.py"

# 检查是否传入 --model 参数
if [ -z "$1" ]; then
    echo "Error: Please provide a model name using --model <model_name>"
    exit 1
fi

# 获取 --model 参数的值
model_name=$1

# 运行次数
num_runs=10

# 循环运行 Python 文件
for i in $(seq 1 $num_runs)
do
    echo "Running $python_file with --model $model_name, iteration $i/$num_runs..."
    python $python_file --model "$model_name"

    # 检查退出状态
    if [ $? -ne 0 ]; then
        echo "Error in iteration $i"
        break
    fi
done
