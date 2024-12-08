import os
import torch
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import argparse
from dotenv import load_dotenv

import lib.perturbations as perturbations
import lib.defenses as defenses
import lib.attacks as attacks
import lib.language_models as language_models
import lib.model_configs as model_configs
from lib.llm import LlamaLLM

load_dotenv()

import warnings

warnings.filterwarnings("ignore")


def main(args):

    # step 1: Create output directories
    os.makedirs(args.results_dir, exist_ok=True)
    
    # step 2: Instantiate the targeted LLM
    target_model = args.target_model
    huggingface_model_path=model_configs.MODELS[target_model]['model_path']
    model = LlamaLLM(huggingface_model_path, os.getenv("HUGGINGFACE_API_KEY"))
    # config = model_configs.MODELS[args.target_model]
    # target_model = language_models.LLM(
    #     model_path=config['model_path'],
    #     tokenizer_path=config['tokenizer_path'],
    #     conv_template_name=config['conversation_template'],
    #     device='cuda:0'
    # )

    # step 3: Create attack instance, used to create prompts
    attack = vars(attacks)[args.attack](
        logfile=args.attack_logfile,
        target_model=target_model
    )

    # Create SmoothLLM instance
    defense = defenses.SmoothLLM(
        target_model=model,
        pert_type=args.smoothllm_pert_type,
        pert_pct=args.smoothllm_pert_pct,
        num_copies=args.smoothllm_num_copies
    )

    # model.generate("how are you doing today?")
    jailbroken_results = []
    for i, prompt in tqdm(enumerate(attack.prompts)):
        output = defense(prompt)
        jb = defense.is_jailbroken(output)
        jailbroken_results.append(jb)

    print(jailbroken_results)

    # Save results to a pandas DataFrame
    summary_df = pd.DataFrame.from_dict({
        'Number of smoothing copies': [args.smoothllm_num_copies],
        'Perturbation type': [args.smoothllm_pert_type],
        'Perturbation percentage': [args.smoothllm_pert_pct],
        'JB percentage': [np.mean(jailbroken_results) * 100],
        'Trial index': [args.trial]
    })
    summary_df.to_pickle(os.path.join(
        args.results_dir, 'summary.pd'
    ))
    print(summary_df)


if __name__ == '__main__':
    torch.cuda.empty_cache()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--results_dir',
        type=str,
        default='./results'
    )
    parser.add_argument(
        '--trial',
        type=int,
        default=0
    )

    # Targeted LLM
    parser.add_argument(
        '--target_model',
        type=str,
        default='llama3-8b',
        choices=['llama3-8b', 'llama3-70b']
    )

    # Attacking LLM
    parser.add_argument(
        '--attack',
        type=str,
        default='Jailbroken',
        choices=['GCG, GPTfuzzer', 'Jailbroken', 'Multilingual']
    )
    parser.add_argument(
        '--attack_logfile',
        type=str,
        default='data/jailbroken/llama_jailbroken.json'
    )

    # SmoothLLM
    parser.add_argument(
        '--smoothllm_num_copies',
        type=int,
        default=5,
    )
    parser.add_argument(
        '--smoothllm_pert_pct',
        type=int,
        default=10
    )
    parser.add_argument(
        '--smoothllm_pert_type',
        type=str,
        default='RandomSwapPerturbation',
        choices=[
            'RandomSwapPerturbation',
            'RandomPatchPerturbation',
            'RandomInsertPerturbation'
        ]
    )

    args = parser.parse_args()
    main(args)