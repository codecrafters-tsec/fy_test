import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        attempted INTEGER DEFAULT 0
    )''')
    
    # Questions table
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL
    )''')
    
    # Answers table
    c.execute('''CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        selected_answer TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )''')
    
    # Results table
    c.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ip_address TEXT,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        submitted_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Exam settings table
    c.execute('''CREATE TABLE IF NOT EXISTS exam_settings (
        id INTEGER PRIMARY KEY,
        duration_minutes INTEGER DEFAULT 30,
        questions_per_exam INTEGER DEFAULT 10
    )''')
    
    # Tab switches table (anti-cheat)
    c.execute('''CREATE TABLE IF NOT EXISTS tab_switches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ip_address TEXT,
        switch_count INTEGER,
        timestamp TIMESTAMP DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # User sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ip_address TEXT,
        login_time TIMESTAMP DEFAULT (datetime('now', 'localtime')),
        logout_time TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Active exams table
    c.execute('''CREATE TABLE IF NOT EXISTS active_exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        question_ids TEXT NOT NULL,
        started_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Insert default admin
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                  ('admin', hash_password('admin123'), 'admin'))
    except sqlite3.IntegrityError:
        pass
    
    # Insert default settings
    c.execute('INSERT OR IGNORE INTO exam_settings (id, duration_minutes, questions_per_exam) VALUES (1, 30, 10)')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
