import os 
import sys
import argparse
 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from goal_prioritization.system_prompt_main import main as goal_main
# from llama_guard.guard_main import main as guard_main
# from smooth_llm.main import main as smooth_main

def run_all(args):

    if args.defense_method == 'goal_prioritization':       
        print("Running Goal Prioritization...")
        goal_main(args) 
    elif args.defense_method == 'llama_guard':
        print("Running Llama Guard...")
        guard_main(args)
    elif args.defense_method == 'smooth_llm':
        print("Running Smooth-llm...")
        smooth_main(args) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="all LLM-related defenses.")
    
    parser.add_argument(
        '--defense_method', 
        type = str,
        default = 'goal_prioritization',
        choices = ['goal_prioritization', 'llama_guard', 'smooth_llm'],
        help = 'Specify the defense method to run with.'
    )
    parser.add_argument(
        '--target_model',
        type=str,
        default='llama31-8b',
        choices=['llama31-8b', 'llama31-70b'],
        help='Specify the target model to run with.'
    )

    parser.add_argument(
        "--db_path", 
        type=str,
        default="/Users/austins/Adversarial-Attacks-on-LLM/sql/austin.db",
        help="Path to the experiments database."
    )

    args = parser.parse_args()

    run_all(args)
