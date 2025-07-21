STYLES = {
    "titleText": """
        QLabel {
            font-size: 36px;
            font-weight: bold;
           
            color: #ffffff;
            qproperty-alignment: 'AlignCenter';
        }
    """,

    "normalText": """
        QLabel {
           
            font-size: 16px;
            line-height: 28px;
            color: #ffffff;
            qproperty-wordWrap: true;
            qproperty-alignment: 'AlignCenter';
        }
    """,

    "button": """
        QPushButton {
            font-size: 14px;
            width: 170px;
            background: transparent;
            color: #fdfefe;
            border-radius: 25px;
            border: 1px solid white;
            padding: 15px;
        }
        QPushButton:hover {
            background-color: #e8e8e8;
            color: dimgray;
        }
        QPushButton:pressed {
            background-color: #d9d9d9;
            color: dimgray;
        }
    """,

    "mainbutton": """
        QPushButton {
            font-size: 14px;
            width: 200px;
            margin-top: 20px;
            background: #3AB19B;
            color: #FDFEFE;
            border-radius: 25px;
            border: 1px solid #49B7A3;
            padding: 15px;
        }
        QPushButton:hover {
            background-color: #3396B5;
            color: white;
        }
        QPushButton:pressed {
            background-color: #2d7a6c;
            color: white;
        }
    """,

    "buttonCircle": """
        QPushButton {
            background: transparent;
            border: 1px solid #878787;
            border-radius: 30px;
            padding: 15px;
            margin-right: 8px;
            margin-left: 8px;
        }
        QPushButton:hover {
            background-color: #d9d9d9;
        }
        QPushButton:pressed {
            background-color: #c4c4c4;
        }
    """,

    "textHint": """
        QLabel {
            font-size: 14px;
            color: #acb0af;
            margin-left: 10px;
        }
    """,

    "textBox": """
        QLineEdit, QPlainTextEdit {
            font-size: 14px;
            color: #878787;
            border: none;
            margin-left: 10px;
        }
    """,

    "imgClose": """
        QLabel {
            width: 30px;
            height: 30px;
            margin-top: 13px;
            margin-right: 13px;
        }
        QLabel:hover {
            transform: scale(1.1); /* won't work in QSS, may need animation or event handler */
        }
    """
}
