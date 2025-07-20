import sys
import os
import re
import json
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

def parse_qa_pairs(text):
    qa_pairs = re.findall(r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)', text, re.DOTALL)
    return [{"question": q.strip(), "answer": a.strip()} for q, a in qa_pairs]

def main():
    if len(sys.argv) < 2:
        print('Usage: python generate_questions.py <textfile>')
        sys.exit(1)
    if not HF_TOKEN:
        print('Please set the HF_TOKEN environment variable.')
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        passage = f.read()
    prompt = (
        "Based on the following text, generate 5 quiz questions and their answers. "
        "Format your response exactly as:\n"
        "Q: <question 1>? A: <answer 1>\n"
        "Q: <question 2>? A: <answer 2>\n"
        "Q: <question 3>? A: <answer 3>\n"
        "Q: <question 4>? A: <answer 4>\n"
        "Q: <question 5>? A: <answer 5>\n"
        f"Text:\n{passage}\n"
    )
    client = InferenceClient(api_key=HF_TOKEN)
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    result = completion.choices[0].message.content
    print("RAW OUTPUT:\n", result)
    qa_list = parse_qa_pairs(result)
    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(qa_list, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(qa_list)} questions to questions.json")

if __name__ == '__main__':
    main() 