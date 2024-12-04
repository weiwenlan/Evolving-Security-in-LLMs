import os 
import json
import datetime
import warnings
import argparse
from dotenv import load_dotenv
from fastchat.model import add_model_args
from huggingface_hub import InferenceClient
from urllib3.exceptions import NotOpenSSLWarning
from get_attack_table import AttackDatabase

import get_attack_table

######################## random config ########################
# https://huggingface.co/meta-llama/Llama-Guard-3-8B
# ignore all the warnings 
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# example_messages = [
# 	{
# 		"role": "user", # input 
# 		"content": "how to kill an animal?"
# 	},
    # {
    #     "role": "assistant", # response 
    #     "content": "here is the detailed way to kill an animal, first, you need to peel off the skin of the animal, then you cut"
    # }
# ]
######################## random config ########################

def get_attack_prompt(db_path: str):
	# init attack database.
	db = AttackDatabase(db_path)

	attack_prompts = []
	try:
		# get attack information
		attacks = db.get_all_attacks()
		for attack in attacks:
			attack_prompts.append(attack)
			# print(attack['attack_prompt'])
			# print("--------------------------------")
		return attack_prompts[:10]

	except Exception as e:
		print(f"Error: {e}")

def format_message(attack_prompt: str, attack_response: str, type: str) -> list:
	"""
	Format the message to the format that the llama guard model can understand. 
	"""
	assert type == "input" or type == "response" or type == "both", "The variable must be 'input' or 'response' or 'both'."

	if type == "input": 
		formatted_message = [{
			"role": "user",
			"content": attack_prompt
		}]
	elif type == "response":
		formatted_message = [
			{
				"role": "user",
				"content": ""
			},
			{
				"role": "assistant",
				"content": attack_response
			}
		]
	elif type == "both":
		formatted_message = [
			{
				"role": "user",
				"content": attack_prompt
			},
			{
				"role": "assistant",
				"content": attack_response
			}
		]
	return formatted_message

def defense_generation(attack_prompts: list, defense_type: str, defense_model:str) -> list:
	results = [] # llama guard response message
	if defense_type == "pre-generation":
		# pre-generation defense 
		client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))
		
		for attack in attack_prompts:
			aid, prompt, response, parent, a_result = attack['id'], attack['prompt'], attack['response'], attack['parent'], attack['result']
			messages = format_message(prompt, "", "input")

			completion = client.chat.completions.create(
				model=defense_model, 
				messages=messages, 
				max_tokens=2000
			)
			llama_check_result = completion.choices[0].message['content'].split("\n") # list 
			result = [
				{
					"result": a_result,
					"llama_check_result": llama_check_result
				}
			]
			results.append(result)
	elif defense_type == "post-generation":
		client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))
		
		for attack in attack_prompts:
			aid, prompt, response, parent, a_result = attack['id'], attack['prompt'], attack['response'], attack['parent'], attack['result']
			messages = format_message("", response, "response")

			completion = client.chat.completions.create(
				model=defense_model, 
				messages=messages, 
				max_tokens=2000
			)
			llama_check_result = completion.choices[0].message['content'].split("\n")[2:] # list 
			result = [
				{
					"result": a_result,
					"llama_check_result": llama_check_result
				}
			]
			results.append(result)
	elif defense_type == "both-generation":
		client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))
		
		for attack in attack_prompts:
			aid, model_name, prompt_input, status, response, method_used, method_category, answer_category, created_at = (
				attack['id'], attack['model_name'], attack['prompt_input'], attack['status'], attack['response'], attack['method_used'], attack['method_category'], attack['answer_category'], attack['created_at'])
			messages = format_message(prompt_input, response, "both")

			completion = client.chat.completions.create(
				model=defense_model, 
				messages=messages, 
				max_tokens=2000
			)
			llama_check_result = completion.choices[0].message['content'].split("\n")[2:] # list 
			result = [
				{
					"aid": aid,
					"model_name": model_name,
					"prompt_input": prompt_input,
					"status": status,
					"response": response,
					"method_used": method_used,
					"method_category": method_category,
					"answer_category": answer_category,
					"created_at": created_at,	
					"llama_check_result": llama_check_result
				}
			]
			results.append(result)

	return results

def main(args):
	# step 0: params config 
	# db_path = "/Users/austins/Adversarial-Attacks-on-LLM/attack/jailbroken2/attacks.db"
	db_path = "/Users/austins/Adversarial-Attacks-on-LLM/evaluation/roberta_test.db"
	defense_type="both-generation" # also post-generation / both-generation
	defense_model="meta-llama/Llama-Guard-3-8B"

	# step 1: start the attack database and get all the attack prompts 
	attack_prompts = get_attack_prompt(db_path)

	# step 2: format the attack prompts to the format that the llama guard model can understand
	results=defense_generation(attack_prompts, defense_type, defense_model)

	# step 3: store the result to the database
	for result in results: 
		print(result[0]["llama_check_result"])
		print("---------------------------------------------------")

	# step 4: close the database connection

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description='Fuzzing parameters')
    parser.add_argument('--openai_key', type=str, default=os.getenv("OPENAI_API_KEY"), help='OpenAI API Key')
    add_model_args(parser)

    args = parser.parse_args()
    main(args)
