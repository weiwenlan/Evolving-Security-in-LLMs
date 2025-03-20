# Adversarial-Attacks-on-LLM

# Architect

![Architect](image/architect.png)

# Pre-Project

```shell
# Install all dependencies specified in pyproject.toml
poetry install

# Activate the virtual environment created by Poetry
poetry shell

# Configure Poetry to create the virtual environment within the project directory
poetry config virtualenvs.in-project true

```

# Run-time

```shell
# Put your token in the .env or export to env variable
DB_PATH="sql/chat_requests.db"
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
XAI_API_KEY=your_xai_api_url_here
GOOGLE_API_KEY=your_google_api_url_here

# Start the FastAPI application using Uvicorn with auto-reload enabled for development
uvicorn src.main:app --reload

# Run the test-connection script to check API connections and validate the API token
# This script can help ensure that the API is reachable and correctly secured
sh src/test-connection.sh

# ➜  ~ curl -X POST "http://127.0.0.1:8000/chat" \
# -H "Content-Type: application/json" \
# -d '{
#   "model": "gpt-4o",
#   "prompt": "How many county in Texas.",
#   "max_tokens": 100,
#   "temperature": 0.7
# }'

# {"response":"Texas has 254 counties, the most of any state in the United States."}%

```

# SQLite View

- https://inloop.github.io/sqlite-viewer/

# Model being tested

//TODO 把模型都提出来
Error with model gemini-1.5-pro-001: Error in API request: 500 - {"detail":"429 Resource has been exhausted (e.g. check quota)."}
// claude 需要 ratelimiter
Error with model claude-3-opus-latest: Error in API request: 500 - {"detail":"Error code: 529 - {'type': 'error', 'error': {'type': 'overloaded_error', 'message': 'Overloaded'}}"}

- remove temperature from code

# Data model

## Version Control

```shell
# Export table to CSV
sqlite3 attacks.db -header -csv "SELECT * FROM Attacks;" > attacks_data.csv

# Export entire database to an SQL file
sqlite3 attacks.db .dump > attacks_backup.sql

```
### 1. `chat_requests` Table

This table stores chat request information, including the model name, prompt input, status, response, and the category of the related method.

| Field Name        | Data Type | Description                                        |
| ----------------- | -------- | -------------------------------------------------- |
| `id`             | INTEGER  | Primary key, auto-incremented                      |
| `model_name`     | TEXT     | Model name, referencing `model_name` in the `Models` table |
| `prompt_input`   | TEXT     | The content of the prompt to be sent              |
| `status`         | TEXT     | Request status (e.g., `pending`, `completed`)      |
| `response`       | TEXT     | Model's response                                  |
| `method_used`    | TEXT     | Method name, referencing `paper_name` in the `Attacks` table |
| `method_category`| TEXT     | Method category, referencing `attack_category` in the `Attacks` table |
| `answer_category`| TEXT     | Category of the model response (e.g., `good`, `bad`) |

---

### 2. `Attacks` Table

This table stores information about attack methods. The `attack_prompt` field will serve as the `prompt_input`, `paper_name` will be used as `method_used`, and `attack_category` as `method_category`.

| Field Name        | Data Type | Description                                  |
| ----------------- | -------- | -------------------------------------------- |
| `id`             | INTEGER  | Primary key, auto-incremented                |
| `paper_name`     | TEXT     | Name of the method, used as `method_used`    |
| `attack_category`| TEXT     | Category of the method, used as `method_category` |
| `attack_prompt`  | TEXT     | Content to be used as `prompt_input`         |

---

### 3. `Defenses` Table

This table stores information about defense methods, with each record describing a defensive measure.

| Field Name   | Data Type | Description                                               |
| ------------ | -------- | --------------------------------------------------------- |
| `id`        | INTEGER  | Primary key, auto-incremented                             |
| `name`      | TEXT     | Name of the defense method                                |
| `category`  | TEXT     | Category of the defense method (e.g., `Self-Processing`, `Additional Helper`) |
| `description` | TEXT   | Detailed description of the defense method               |

---

### 4. `Models` Table

This table stores model information, including name, API endpoint, and parameters. `model_name` matches the `model_name` in the `chat_requests` table.

| Field Name   | Data Type | Description                                       |
| ------------ | -------- | ------------------------------------------------- |
| `id`        | INTEGER  | Primary key, auto-incremented                     |
| `model_name` | TEXT     | Model name, referencing `model_name` in `chat_requests` |
| `endpoint`   | TEXT     | API endpoint of the model                        |
| `parameters` | TEXT     | Model parameters (e.g., `temperature`, `max_tokens`, etc.) |

---

### 5. `Experiments` Table

This table records details of each experiment, including the combination of models, attack methods, and defense methods, as well as the experiment’s success rate and efficiency.

| Field Name     | Data Type | Description                            |
| ------------- | -------- | -------------------------------------- |
| `id`         | INTEGER  | Primary key, auto-incremented         |
| `model_id`   | INTEGER  | Model ID, referencing `Models` table  |
| `attack_id`  | INTEGER  | Attack method ID, referencing `Attacks` table |
| `defense_id` | INTEGER  | Defense method ID, referencing `Defenses` table |
| `success_rate` | REAL   | Success rate of the attack            |
| `efficiency`  | REAL    | Efficiency score                      |
| `date`       | TEXT     | Experiment date                       |
| `notes`      | TEXT     | Experiment notes                      |

---

### 6. `Results` Table

This table stores details of specific experimental results, with each record describing the category and success of an experiment.

| Field Name      | Data Type | Description                                              |
| -------------- | -------- | -------------------------------------------------------- |
| `id`          | INTEGER  | Primary key, auto-incremented                            |
| `experiment_id` | INTEGER | Experiment ID, referencing `Experiments` table         |
| `category`    | TEXT     | Category of experiment results (e.g., `harmful_content`, `adult_content`) |
| `success`     | BOOLEAN  | Whether the experiment was successful                   |
| `count`       | INTEGER  | Number of successful cases                              |

---