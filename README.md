# Adversarial-Attacks-on-LLM

poetry install
poetry shell 

poetry config virtualenvs.in-project true


# Data model
根据文档内容，您可以设计一个数据模型来存储实验数据和分析结果，使用 SQLite 数据库。这个模型可以包括以下表结构：

1. **Attacks 表**：存储每种攻击的基本信息
   - `id`: 主键，自增
   - `name`: 攻击的名称（例如 GPTFuzz, AutoDAN 等）
   - `category`: 攻击的类别（例如 Generative, Template, Training Gaps）
   - `description`: 攻击的详细描述

2. **Defenses 表**：存储每种防御方法的信息
   - `id`: 主键，自增
   - `name`: 防御的名称（例如 Smooth-LLM, LLMguard）
   - `category`: 防御的类别（例如 Self-Processing, Additional Helper, Input Permutation）
   - `description`: 防御方法的详细描述

3. **Models 表**：存储实验中使用的语言模型
   - `id`: 主键，自增
   - `name`: 模型名称（如 GPT-3.5-turbo, Vicuna, Llama）
   - `parameters`: 参数数量（如 7B, 13B）
   - `provider`: 模型提供商（如 OpenAI, Hugging Face）

4. **Experiments 表**：记录每次实验的具体信息
   - `id`: 主键，自增
   - `model_id`: 外键，引用 Models 表中的 id
   - `attack_id`: 外键，引用 Attacks 表中的 id
   - `defense_id`: 外键，引用 Defenses 表中的 id
   - `success_rate`: 攻击成功率（浮点数）
   - `efficiency`: 效率（浮点数）
   - `date`: 实验日期
   - `notes`: 其他实验备注

5. **Results 表**：记录实验的结果细节
   - `id`: 主键，自增
   - `experiment_id`: 外键，引用 Experiments 表中的 id
   - `category`: 实验结果类别（如 harmful_content, adult_content, illegal_activity 等）
   - `success`: 成功与否（布尔值）
   - `count`: 成功案例的数量

通过这种数据库设计，您可以轻松查询每种攻击和防御的成功率和效率，并根据模型、攻击、和防御的组合对实验结果进行分析。希望这个数据模型有助于您对实验数据的存储和管理！