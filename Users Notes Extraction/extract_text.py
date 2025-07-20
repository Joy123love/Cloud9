import sys
import os

# PDF extraction
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
# DOCX extraction
try:
    import docx
except ImportError:
    docx = None

def extract_text_from_pdf(path):
    if not PyPDF2:
        raise ImportError('PyPDF2 is not installed')
    with open(path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def extract_text_from_docx(path):
    if not docx:
        raise ImportError('python-docx is not installed')
    doc = docx.Document(path)
    return '\n'.join([p.text for p in doc.paragraphs])

def extract_text_from_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(path)
    elif ext == '.docx':
        return extract_text_from_docx(path)
    elif ext == '.txt':
        return extract_text_from_txt(path)
    else:
        raise ValueError('Unsupported file type: ' + ext)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python extract_text.py <file>')
        sys.exit(1)
    path = sys.argv[1]
    text = extract_text(path)
    print(text) 