import sqlite3
import os

def init_db(db_path='files.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_file_to_db(filename, db_path='files.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO files (filename) VALUES (?)', (filename,))
    conn.commit()
    conn.close()

def get_all_files(db_path='files.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT filename FROM files')
    files = [row[0] for row in c.fetchall()]
    conn.close()
    return files

def delete_file_from_db(filename, db_path='files.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM files WHERE filename = ?', (filename,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Example usage
    init_db()
    add_file_to_db('example.pdf')
    print(get_all_files())
    delete_file_from_db('example.pdf')
    print(get_all_files()) 