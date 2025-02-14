import os 
import sys
import argparse
 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from goal_prioritization.system_prompt_main import main as goal_main
from llama_guard.serverless_llama_guard import main as guard_main
from smooth_llm.smooth_llm_main import main as smooth_main
from smooth_llm.smooth_llm_goal import main as smooth_goal_main

def run_all(args):
    if args.defense_method == 'goal_prioritization':       
        print("*****Running Goal Prioritization...")
        goal_main(args) 
    elif args.defense_method == 'llama_guard':
        print("*****Running Llama Guard...")
        guard_main(args)
    elif args.defense_method == 'smooth_llm':
        print("*****Running Smooth-llm...")
        smooth_main(args) 
    elif args.defense_method == 'smooth_llm_goal':
        print("*****Running Smooth-llm with goal prioritization...")
        smooth_goal_main(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="all LLM-related defenses.")
    parser.add_argument(
        '--defense_method', 
        type = str,
        
        default = 'smooth_llm_goal',
        choices = ['goal_prioritization', 'llama_guard', 'smooth_llm', 'smooth_llm_goal'],
        help = 'Specify the defense method to run with.'
    )
    parser.add_argument(
        '--target_model',
        type=str,
        default='llama31-8b',
        choices=['llama31-8b', 'llama31-70b', 'gpt-3.5-turbo', 'gpt-4-turbo', 'vicuna7b15', 'vicuna13b15', 'vicuna7b11', 'vicuna13b11', 'llama2-70b-hf', 'llama2-7b-hf', 'mistral7b-01', 'mistral7b-02', 'mistral7b-03', 'mistral12b-nemo'],
        help='Specify the target model to run with.'
    )

    parser.add_argument(
        "--db_path",
        type=str,
        default="/Users/austins/Adversarial-Attacks-on-LLM/data/500/evaluated/austin.db",
        help="Path to the experiments database."
    )

    args = parser.parse_args()

    run_all(args)
