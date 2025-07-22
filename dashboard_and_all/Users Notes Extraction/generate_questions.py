import sys
import os
import re
import json
from huggingface_hub import InferenceClient

HF_TOKEN = "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" #This key will be obsolete soon, use your own hugging face api
MODEL = "mistralai/Mistral-7B-Instruct-v0.3"


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate questions from a document or text.')
    parser.add_argument('file', nargs='?', help='Path to the document file (txt, pdf, docx)')
    parser.add_argument('--text', help='Direct text input (overrides file if provided)')
    args = parser.parse_args()

    if args.text:
        passage = args.text
        output_path = os.path.join('jsons', 'generated.json')
    elif args.file:
        # Use extract_text.py logic for file extraction
        import os
        ext = os.path.splitext(args.file)[1].lower()
        if ext == '.pdf':
            import PyPDF2
            with open(args.file, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                passage = ''
                for page in reader.pages:
                    passage += page.extract_text() or ''
        elif ext == '.docx':
            import docx
            doc = docx.Document(args.file)
            passage = '\n'.join([p.text for p in doc.paragraphs])
        elif ext == '.txt':
            with open(args.file, 'r', encoding='utf-8') as f:
                passage = f.read()
        else:
            print('Unsupported file type:', ext)
            sys.exit(1)
        input_filename = os.path.basename(args.file)
        base, _ = os.path.splitext(input_filename)
        output_path = os.path.join('jsons', f'{base}.json')
    else:
        print('Usage: python generate_questions.py <textfile> or --text "some text"')
        sys.exit(1)

    prompt = (
        "Based on the following text, generate all quiz questions and their answers from the text. "
        "Output ONLY a valid JSON array of objects, each in the format: "
        '{"question": "This is the question", "answer": "This is the answer"}.\n'
        "If there is more than one answer, concatenate them into a single string separated by ' and ' in the 'answer' field. Do not use arrays for answers.\n"
        "If the answer you produce is part of the text in the question remove it from the text in the question"
        "Do not output a question without an answer"
        "Do not include any comments, explanations, or extra text—just the JSON array.\n"
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
    import json, re
    def clean_json_output(text):
        # Remove comments
        text = re.sub(r'//.*', '', text)
        # Extract all JSON objects
        objects = re.findall(r'{[^{}]*}', text, re.DOTALL)
        if objects:
            json_str = '[{}]'.format(','.join(objects))
            # Remove trailing commas before closing brackets
            json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
            try:
                qa_list = json.loads(json_str)
                # Normalize answer field to always be a string
                for qa in qa_list:
                    ans = qa.get('answer')
                    if isinstance(ans, list):
                        qa['answer'] = ' and '.join(str(a) for a in ans)
                    elif ans is not None:
                        qa['answer'] = str(ans)
                return qa_list
            except Exception as e:
                print(f'Error parsing cleaned JSON: {e}')
                return []
        else:
            print('Could not parse JSON objects from model output.')
            return []
    try:
        qa_list = clean_json_output(result)
    except Exception as e:
        print(f'Error parsing JSON: {e}')
        qa_list = []
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_list, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(qa_list)} questions to {output_path}")

if __name__ == '__main__':
    main() 