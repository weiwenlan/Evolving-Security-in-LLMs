import os 
import json
import warnings
import argparse
from tqdm.auto import tqdm
from dotenv import load_dotenv
from fastchat.model import add_model_args
from huggingface_hub import InferenceClient
from urllib3.exceptions import NotOpenSSLWarning

from helpers.model_configs import *
from helpers.get_experiment_tools import *
load_dotenv()

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

def defense_generation(attack_prompts: list, experiment_table, defense_type: str, defense_model:str) -> list:
	results = [] # llama guard response message
	client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))

	for attack in tqdm(attack_prompts):
		request_id, model_id, attack_id, defense_id, attack_timestamp, defense_timestamp, attacked_prompt, attacked_response, attacked_result, evaluate_status, defensed_response, defensed_result, defensed_status = (
			attack['request_id'], attack['model_id'], attack['attack_id'], attack['defense_id'], attack['attack_timestamp'], attack['defense_timestamp'], attack['attacked_prompt'], attack['attacked_response'], attack['attacked_result'], attack['evaluate_status'], attack['defensed_response'], attack['defensed_result'], attack['defensed_status'])
		
		if defense_type == "pre-generation":
			messages = format_message(attacked_prompt, "", "input")
		elif defense_type == "post-generation":
			messages = format_message("", attacked_response, "response")
		elif defense_type == "both-generation":
			messages = format_message(attacked_prompt, attacked_response, "both")

		completion = client.chat.completions.create(
			model=defense_model, 
			messages=messages, 
			max_tokens=2000
		)

		attack['defensed_response'] = completion.choices[0].message['content'].split("\n")[2:3][0]
		attack['defensed_status'] = "completed"
		attack['defense_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		# update the database
		experiment_table.update_one_line(attack)

def main(args):
	# step 0: params config 
	db_path = args.db_path
	defense_model=MODELS['llama-guard-3-8b']['model_path']
	defense_type="both-generation" # also post-generation / both-generation

	# step 1: start the attack database and get all the attack prompts 
	attack_prompts = get_experiments(db_path, args.defense_method)

	# step 1.5: start the experiment table class
	experiment_table = ExperimentDatabase(db_path)

	# step 2: start the defense generation
	defense_generation(attack_prompts, experiment_table, defense_type, defense_model)

	# step 3: close the database connection
	experiment_table.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="llama guard defenses.")
	args = parser.parse_args()
	main(args)

