import os
import csv
import openai
import random
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up your API key
openai.api_key = os.getenv("OPENAI_API_KEY")


# Expanded list of topics
subjects = [
    "technology", "history", "philosophy", "nature", "mathematics", "art", "social issues", 
    "psychology", "literature", "education", "health", "environment", "culture", "astronomy", 
    "physics", "biology", "artificial intelligence", "programming", "entrepreneurship", "economics", 
    "politics", "music", "movies", "gaming", "mental health", "travel", "food", "futurism", 
    "architecture", "engineering", "chemistry", "ecology", "ethics", "religion", "law", "anthropology", 
    "geography", "fashion", "medical technology", "tech ethics", "global warming", "data science", 
    "cybersecurity", "autonomous vehicles", "blockchain", "virtual reality", "quantum computing", 
    "bioengineering", "linguistics", "educational technology", "social equity", "career development"
]

# Expanded list of question templates
question_templates = [
    "Can you explain why {} is an important topic?",
    "What are some unique perspectives about {}?",
    "How would you describe {} in simple terms?",
    "Why is {} crucial for the future of society?",
    "What specific impacts does {} have on our daily lives?",
    "Can you recommend books or resources on {}?",
    "What are the main challenges currently faced in {}?",
    "What would happen if we ignored {}?",
    "How has {} evolved over time?",
    "What are the primary future directions for {}?",
    "What are common misconceptions about {}?",
    "How is {} defined from a philosophical perspective?",
    "If you were an expert, how would you explain {} to children?",
    "What are the key research questions in {}?",
    "What are the common controversies surrounding {}?",
    "From an ethical perspective, is {} controversial?",
    "How can the impact of {} be measured?",
    "Which countries lead the world in {}?",
    "How does {} affect the global economy?",
    "What profound impacts might {} have on human civilization?",
    "What new technologies could revolutionize {}?",
    "What role does {} play in education?",
    "How do you envision the future of {}?",
    "What little-known facts about {} might surprise people?",
    "How does {} affect mental health?",
    "Which artists or works are associated with {}?",
    "If we fully mastered {}, how would the world change?",
    "What innovations have changed the state of {}?",
    "What advice would you give to better understand {}?",
    "What is the historical background of {}?",
    "What revolutionary discoveries have been made in {}?",
    "What are the most likely breakthroughs in {}?",
    "Which movies or books explore the topic of {}?",
    "How does {} shape culture and society?",
    "What are the unresolved challenges in {}?",
    "What lessons does {} offer for current social issues?",
    "How does {} intersect with other disciplines?"
]

# Generate random questions
def generate_random_question():
    subject = random.choice(subjects)
    template = random.choice(question_templates)
    return template.format(subject)

# Call OpenAI API to generate answers
def ask_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}],
            max_tokens=200
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# Main program: Call the API 945 times
import csv
from tqdm import tqdm  # 导入 tqdm 库

def main():
    total_combinations = len(subjects) * len(question_templates)
    print(f"Total unique question combinations: {total_combinations}")

    # 打开 CSV 文件，准备写入
    with open("openai_questions_and_answers.csv", "w", encoding="utf-8", newline="") as csvfile:
        # 创建 CSV 写入器
        csv_writer = csv.writer(csvfile)
        # 写入表头
        csv_writer.writerow(["Question", "Answer"])

        # 使用 tqdm 创建一个进度条
        with tqdm(total=945, desc="Processing Questions", unit="question") as pbar:
            for i in range(945):
                question = generate_random_question()
                answer = ask_openai(question)

                # 立即写入到 CSV 文件
                csv_writer.writerow([question, answer])
                
                pbar.update(1)  # 每次处理完一个问题，进度条更新

    print("All questions and answers have been saved to openai_questions_and_answers.csv.")


if __name__ == "__main__":
    main()
