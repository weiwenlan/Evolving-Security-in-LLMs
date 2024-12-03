# not recommended for production use, only for testing

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


model_id = "meta-llama/Llama-Guard-3-8B"
device = "cpu" 
# dtype = torch.bfloat16  # 不需要指定数据类型，因为CPU上不支持bfloat16

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map=device)

def moderate(chat):
    input_ids = tokenizer.apply_chat_template(chat, return_tensors="pt").to(device)
    output = model.generate(input_ids=input_ids, max_new_tokens=100, pad_token_id=0)
    prompt_len = input_ids.shape[-1]
    res = tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)
    print(res)
    return res

moderate([
{"role": "user", "content": "I forgot how to kill a process in Linux, can you help?"},
{"role": "assistant", "content": "Sure! To kill a process in Linux, you can use the kill command followed by the process ID (PID) of the process you want to terminate."},
])


