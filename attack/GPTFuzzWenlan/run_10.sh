#!/bin/bash

# 定义要运行的 Python 文件
python_file="wenlan_change.py"

# 运行次数
num_runs=10

# 循环运行 Python 文件
for i in $(seq 1 $num_runs)
do
    echo "Running $python_file, iteration $i/$num_runs..."
    python $python_file

    # 检查退出状态
    if [ $? -ne 0 ]; then
        echo "Error in iteration $i"
    fi
done
