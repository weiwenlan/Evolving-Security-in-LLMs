# Evolving Security in LLMs

Code and experimental materials for **Evolving Security in LLMs: A Study of Jailbreak Attacks and Defenses**.

| Resource | Link |
| --- | --- |
| Published paper | [IEEE Xplore](https://ieeexplore.ieee.org/document/11467846) |
| Preprint | [arXiv:2504.02080](https://arxiv.org/abs/2504.02080) |

## Overview

This repository contains the attack, defense, and evaluation pipeline used to study jailbreak robustness in large language models. It includes implementations and experiment wrappers for multiple jailbreak methods, defense strategies, model APIs, and evaluation scripts.

The code is organized around three stages:

1. **Attack generation and execution**: run jailbreak methods against target LLMs and store model responses.
2. **Defense application**: apply safety defenses such as SmoothLLM, Llama Guard, goal prioritization, and helper-based defenses.
3. **Evaluation and analysis**: label responses, aggregate SQLite experiment tables, and compute attack/defense outcomes.

## Repository layout

```text
.
├── attack/                 # Jailbreak attack implementations and wrappers
│   ├── CipherChat/
│   ├── GPTFuzz/
│   ├── MasterKey/
│   ├── Multilingual/
│   ├── ReNeLLM/
│   ├── jailbroken/
│   └── jailbroken2/
├── data/                   # Experiment databases and sampled datasets
├── defenses/               # Defense implementations and defense runners
│   ├── goal_prioritization/
│   ├── helpers/
│   ├── llama_guard/
│   └── smooth_llm/
├── evaluation/             # Labeling, moderation, and result analysis scripts
├── image/                  # Architecture figures
├── sql/                    # SQLite table creation and aggregation utilities
└── src/                    # FastAPI model-query service
```

## Architecture

![Architecture](image/architect.png)

## Setup

Create a Python environment and install the dependencies required by the components you plan to run.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Some attack modules include their own dependency files:

```bash
python -m pip install -r attack/MasterKey/requirements.txt
python -m pip install -r attack/ReNeLLM/requirements.txt
```

The FastAPI model-query service imports the following packages:

```bash
python -m pip install fastapi uvicorn python-dotenv openai anthropic google-generativeai ratelimit huggingface-hub google-cloud-aiplatform
```

## Configuration

The model-query service reads API credentials from environment variables or a local `.env` file. Do not commit real API keys.

```bash
DB_PATH=sql/chat_requests.db
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
VERTEX_PROJECT=your_vertex_project
VERTEX_ENDPOINT_ID=your_vertex_endpoint_id
VERTEX_LOCATION=your_vertex_location
```

## Running the model-query service

Start the FastAPI service:

```bash
uvicorn src.main:app --reload
```

Send a test request:

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "prompt": "How many counties are in Texas?",
    "max_tokens": 100
  }'
```

Expected response shape:

```json
{
  "response": "..."
}
```

## Running experiments

Each attack and defense module contains its own entry points and helper scripts. Common starting points:

| Component | Example files |
| --- | --- |
| CipherChat | `attack/CipherChat/ADV_main.py`, `attack/CipherChat/ADV_run.sh` |
| GPTFuzz | `attack/GPTFuzz/ADV_change.py`, `attack/GPTFuzz/ADV_run_10.sh` |
| MasterKey | `attack/MasterKey/ADV_change.py`, `attack/MasterKey/masterkey_zeroshot.py` |
| Multilingual attacks | `attack/Multilingual/ADV_main.py` |
| ReNeLLM | `attack/ReNeLLM/ADV_renellm.py`, `attack/ReNeLLM/renellm.py` |
| Defenses | `defenses/run_defense.sh`, `defenses/defenses.py` |
| Evaluation | `evaluation/run_evaluation.sh`, `evaluation/gpt_label.py`, `evaluation/roberta_label.py` |

Several subdirectories are adapted from or build on existing jailbreak and defense methods. Check the corresponding subdirectory README and LICENSE files before running or redistributing a specific component.

## Data and results

Experiment inputs, generated responses, and labels are stored primarily as SQLite databases and text outputs.

| Path | Description |
| --- | --- |
| `data/full/` | Full experiment response databases |
| `data/500/` | Sampled experiment databases |
| `evaluation/result/` | Labeling outputs for attack experiments |
| `evaluation/combination_defense/` | Labeling outputs for combined defense experiments |
| `sql/` | Scripts for generating, cleaning, and aggregating experiment tables |

SQLite databases can be inspected with the command-line `sqlite3` tool or a browser viewer such as [SQLite Viewer](https://inloop.github.io/sqlite-viewer/).

Example export commands:

```bash
sqlite3 attacks.db -header -csv "SELECT * FROM Attacks;" > attacks_data.csv
sqlite3 attacks.db .dump > attacks_backup.sql
```

## Database schema

The main experiment pipeline uses SQLite tables with the following logical structure.

### `chat_requests`

Stores model requests and responses.

| Field | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Primary key |
| `model_name` | `TEXT` | Target model name |
| `prompt_input` | `TEXT` | Prompt sent to the model |
| `status` | `TEXT` | Request status, such as `pending` or `completed` |
| `response` | `TEXT` | Model response |
| `method_used` | `TEXT` | Attack or defense method name |
| `method_category` | `TEXT` | Method category |
| `answer_category` | `TEXT` | Evaluation label |

### `Attacks`

Stores attack prompts and attack metadata.

| Field | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Primary key |
| `paper_name` | `TEXT` | Attack method name |
| `attack_category` | `TEXT` | Attack category |
| `attack_prompt` | `TEXT` | Attack prompt used as input |

### `Defenses`

Stores defense method metadata.

| Field | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Primary key |
| `name` | `TEXT` | Defense method name |
| `category` | `TEXT` | Defense category |
| `description` | `TEXT` | Defense description |

### `Models`

Stores target model metadata.

| Field | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Primary key |
| `model_name` | `TEXT` | Model name referenced by `chat_requests` |
| `endpoint` | `TEXT` | Model endpoint |
| `parameters` | `TEXT` | Model parameters |

### `Experiments`

Stores experiment configurations.

| Field | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Primary key |
| `model_id` | `INTEGER` | Model ID |
| `attack_id` | `INTEGER` | Attack ID |
| `defense_id` | `INTEGER` | Defense ID |
| `success_rate` | `REAL` | Attack success rate |
| `efficiency` | `REAL` | Efficiency score |
| `date` | `TEXT` | Experiment date |
| `notes` | `TEXT` | Experiment notes |

### `Results`

Stores per-experiment result summaries.

| Field | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Primary key |
| `experiment_id` | `INTEGER` | Experiment ID |
| `category` | `TEXT` | Result category |
| `success` | `BOOLEAN` | Whether the experiment succeeded |
| `count` | `INTEGER` | Number of successful cases |

## Citation

If you use this repository, please cite the published paper:

```bibtex
@inproceedings{shang2025evolving,
  title = {Evolving Security in LLMs: A Study of Jailbreak Attacks and Defenses},
  author = {Shang, Zhengchun and Wei, Wenlan and Bai, Weiheng},
  year = {2025},
  url = {https://ieeexplore.ieee.org/document/11467846}
}
```

## Responsible use

This repository is intended for academic research and defensive evaluation of LLM safety. Do not use the attack code, prompts, or generated outputs to bypass safeguards in deployed systems or to cause harm.

## License

Some subdirectories include their own license files inherited from upstream methods. Review the license in each component before reuse.
