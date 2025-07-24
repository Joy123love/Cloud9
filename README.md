# Cloud9 Setup Guide

## 1. Hugging Face API Token Setup

This project uses Hugging Face's API for AI-powered question generation and answer checking. You need a Hugging Face API token to use these features.

### Steps to Get Your Token
1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and log in or create a free account.
2. Click **New token**, give it a name, and select the `read` role.
3. Copy the generated token.

### Where to Paste Your Token
You need to paste your token in **two files**:

#### a. For Question Generation (AI in Dashboard)
- **File:** `Cloud9/Cloud9/application/src/dashboard/files.py`
- **Line:** Look for `HF_TOKEN = ""` (or similar) in the `generate_questions_and_save` method. Paste your token as the value, e.g.:
  ```python
  HF_TOKEN = "your_token_here"
  ```

#### b. For AI Answer Checking in Switch Runner Game
- **File:** `Cloud9/Cloud9/application/src/switch_runner/game.py`
- **Line:** Look for `HF_TOKEN = ""` (or similar) in the `ai_check_answer` method. Paste your token as the value, e.g.:
  ```python
  HF_TOKEN = "your_token_here"
  ```

---

## 2. Running the Project

### a. Install Requirements
Make sure you have Python 3.9+ and install the required packages:
```sh
pip install -r requirements.txt
```
(If you don't have a `requirements.txt`, install at least: `pygame`, `requests`, `huggingface_hub`, `PyPDF2`, `python-docx`)

### b. Start the Application
Navigate to the server directory and run the main file:
```sh
cd Cloud9/Cloud9/application/src
python main.py
```

### c. Log In or Use as Guest
- **To create an account or log in:** Use the login/signup screen that appears.
- **To use as guest:** Click the guest login option (if available) or leave credentials blank and proceed as guest.

---

## 3. Notes
- Make sure your `assets/`, `jsons/`, and other resource folders are in the correct locations as per the repo structure.
- If you encounter any issues with AI features, double-check your Hugging Face token and internet connection.

---

Enjoy using Cloud9! 