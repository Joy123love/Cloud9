import os
import requests

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# The specific question and correct answer
target_question = "4. If it takes 5 men to dig 5 holes in 5 hours, how many men does it take to dig 100 holes in 100 hours?"
correct_answer = "20 men - each man digs 1 hole in 5 hours."

user_answer = input(f"{target_question}\nYour answer: ")

prompt = (
    f"Question: {target_question}\n"
    f"User's answer: {user_answer}\n"
    f"Correct answer: {correct_answer}\n"
    "Is the user's answer correct? Reply only Yes or No and a brief explanation if needed."
)

response = query({
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "model": "mistralai/Mistral-7B-Instruct-v0.2:featherless-ai"
})

print(response["choices"][0]["message"]["content"])