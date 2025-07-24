from PyQt6.QtCore import Qt
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QFileDialog
from backend.dashboard.notepad_db import init_db, add_file_to_db, get_all_files, delete_file_from_db
from assets import icons
from theming.theme import theme
import subprocess
import sys
import os


class FileRow(QFrame):
    def __init__(self, filename : str, delete_file, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setMinimumHeight(56)
        self.setStyleSheet(f'background-color: {theme.background.name()}; border-radius: 12px;')
        file_row = QHBoxLayout(self)
        file_row.setContentsMargins(0, 0, 10, 0)
        file_row.setSpacing(0)
        
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("QCheckBox { margin-left: 12px; margin-right: 8px; } QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; background: "+theme.background_alternative.name()+"; border: 1.5px solid " + theme.background.name() + "; } QCheckBox::indicator:checked { background: " + theme.primary.name() + ";}")
        self.checkbox.setVisible(False);
        file_row.addWidget(self.checkbox)
        
        file_label = QLabel(filename)
        file_label.setStyleSheet('color: #fff; font-size: 16px; font-weight: bold; padding-left: 18px; background: transparent; border: none;')
        file_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        file_row.addWidget(file_label)
        file_row.addStretch(1)
        
        def get_icon(path : str) -> QSvgWidget:
            icon = QSvgWidget(path)
            icon.setFixedSize(24, 24)
            icon.setStyleSheet('background: transparent; border: none')
            return icon

        edit_icon = get_icon(icons.get_path('edit.svg'))
        edit_icon.setStyleSheet('background: transparent; border: none; margin-right: 18px;')
        file_row.addWidget(edit_icon)
        file_row.addSpacing(10)
        
        self.delete_icon = get_icon(icons.get_path('delete.svg'))
        self.delete_icon.mousePressEvent = lambda e, fn=filename: delete_file(fn)
        file_row.addWidget(self.delete_icon)

        self.setLayout(file_row)


class DashboardFiles(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.file_rects : list[FileRow] = []
        self.file_checkboxes = []
        self.file_list_layout = QVBoxLayout()
        self.setLayout(self.file_list_layout);
        self.file_list_layout.setSpacing(5)
        self.search_query = None;
        self.selected_files = set()
        self.selection_mode = False
    
    def open_add_file_dialog(self, event=None):
        file_path, _ = QFileDialog.getOpenFileName(self, "Add a Document", "", "Documents (*.pdf *.docx *.txt *.csv)")
        if file_path:
            print(f"Selected file: {file_path}")
            self.generate_questions_and_save(file_path)

    def generate_questions_and_save(self, file_path):
        import json
        import os
        import re
        import requests
        # File extraction logic
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                passage = ''
                for page in reader.pages:
                    passage += page.extract_text() or ''
        elif ext == '.docx':
            import docx
            doc = docx.Document(file_path)
            passage = '\n'.join([p.text for p in doc.paragraphs])
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                passage = f.read()
        else:
            print('Unsupported file type:', ext)
            return
        input_filename = os.path.basename(file_path)
        base, _ = os.path.splitext(input_filename)
        json_filename = f"{base}.json"
        jsons_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../jsons"))
        os.makedirs(jsons_dir, exist_ok=True)
        json_path = os.path.join(jsons_dir, json_filename)
        # DeepSeek API call
        HF_TOKEN = ""  # Use your own token
        API_URL = "https://router.huggingface.co/v1/chat/completions"
        prompt = (
            "Based on the following text, generate all quiz questions and their answers from the text. "
            "Output ONLY a valid JSON array of objects, each in the format: "
            '{"question": "This is the question", "answer": "This is the answer"}.\n'
            "If there is more than one answer, concatenate them into a single string separated by ' and ' in the 'answer' field. Do not use arrays for answers.\n"
            "If the answer you produce is part of the text in the question remove it from the text in the question. "
            "Do not output a question without an answer. "
            "Do not include any comments, explanations, or extra text—just the JSON array.\n"
            f"Text:\n{passage}\n"
        )
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
        }
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "model": "deepseek-ai/DeepSeek-R1:novita"
        }
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            result = data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[ERROR] AI question generation failed: {e}")
            return
        def clean_json_output(text):
            text = re.sub(r'//.*', '', text)
            objects = re.findall(r'{[^{}]*}', text, re.DOTALL)
            if objects:
                json_str = '[{}]'.format(','.join(objects))
                json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
                try:
                    qa_list = json.loads(json_str)
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
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(qa_list, f, indent=2, ensure_ascii=False)
        add_file_to_db(json_filename)
        self.refresh_file_list()

    def on_search_text_changed(self, text):
        self.search_query = text
        self.refresh_file_list()

    def refresh_file_list(self):
        self.file_rects.clear()
        self.file_checkboxes.clear()

        while self.file_list_layout.count():
            item = self.file_list_layout.takeAt(0)
            if not item:
                continue;
            widget = item.widget()
            if widget:
                widget.deleteLater()
        file_names = get_all_files()
        
        # Filter files by search query
        if self.search_query:
            file_names = [fn for fn in file_names if self.search_query in fn.lower()]

        for filename in file_names:
            file_rect = FileRow(filename, self.delete_file);
            self.file_rects.append(file_rect)
            self.file_list_layout.addWidget(file_rect)

        # self.files_layout.addLayout(self.file_list_layout)

    def delete_file(self, filename):
        import os;
        delete_file_from_db(filename)
        file_path = os.path.join('jsons', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        self.refresh_file_list()

    def enter_selection_mode(self):
        self.selection_mode = True
        self.selected_files.clear()
        for i, file in enumerate(self.file_rects):
            file.checkbox.setVisible(True)
            file.checkbox.setChecked(False)
        self.update()

    def exit_selection_mode(self):
        self.selection_mode = False
        self.selected_files.clear()
        for i, file in enumerate(self.file_rects):
            file.checkbox.setVisible(False)
            file.checkbox.setChecked(False)
        self.update()

    def select_all_files(self):
        for i, file in enumerate(self.file_rects):
            file.checkbox.setChecked(True)
        self.update()

    def delete_selected_files(self):
        file_names = get_all_files()
        for idx, file in enumerate(self.file_rects):
            if file.checkbox.isChecked():
                filename = file_names[idx]
                self.delete_file(filename)
        self.exit_selection_mode()

    def toggle_select_all_files(self):
        file_count = len(self.file_rects)
        all_selected = all(file.checkbox.isChecked() for file in self.file_rects) and file_count > 0
        for file in self.file_rects:
            file.checkbox.setChecked(not all_selected)

        self.update()
