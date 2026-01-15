import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_sample_data():
    conn = sqlite3.connect('exam.db')
    c = conn.cursor()
    
    # Sample questions
    questions = [
        ("What is the time complexity of binary search?", "O(n)", "O(log n)", "O(n^2)", "O(1)", "B"),
        ("Which data structure uses LIFO?", "Queue", "Stack", "Array", "Tree", "B"),
        ("What does HTML stand for?", "Hyper Text Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyperlinks and Text Markup Language", "A"),
        ("Which language is used for web apps?", "PHP", "Python", "JavaScript", "All of the above", "D"),
        ("What is the output of 2**3 in Python?", "6", "8", "9", "5", "B"),
        ("Which is not a programming language?", "Python", "Java", "HTML", "C++", "C"),
        ("What does CSS stand for?", "Cascading Style Sheets", "Computer Style Sheets", "Creative Style Sheets", "Colorful Style Sheets", "A"),
        ("Which symbol is used for comments in Python?", "//", "#", "/*", "<!--", "B"),
        ("What is the default port for HTTP?", "443", "8080", "80", "3000", "C"),
        ("Which is a NoSQL database?", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "C"),
        ("What does API stand for?", "Application Programming Interface", "Advanced Programming Interface", "Application Process Interface", "Automated Programming Interface", "A"),
        ("Which is not a JavaScript framework?", "React", "Angular", "Django", "Vue", "C"),
        ("What is Git used for?", "Version control", "Database management", "Web hosting", "Testing", "A"),
        ("Which HTTP method is used to update data?", "GET", "POST", "PUT", "DELETE", "C"),
        ("What does SQL stand for?", "Structured Query Language", "Simple Query Language", "Standard Query Language", "System Query Language", "A"),
    ]
    
    for q in questions:
        try:
            c.execute('''INSERT INTO questions 
                        (question, option_a, option_b, option_c, option_d, correct_answer) 
                        VALUES (?, ?, ?, ?, ?, ?)''', q)
        except sqlite3.IntegrityError:
            pass
    
    # Sample students
    students = [
        ("student1", "pass123"),
        ("student2", "pass123"),
        ("student3", "pass123"),
        ("student4", "pass123"),
        ("student5", "pass123"),
    ]
    
    for username, password in students:
        try:
            c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                     (username, hash_password(password), 'student'))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print("Sample data added successfully!")
    print("\nSample Students:")
    print("Username: student1, Password: pass123")
    print("Username: student2, Password: pass123")
    print("Username: student3, Password: pass123")
    print("Username: student4, Password: pass123")
    print("Username: student5, Password: pass123")

if __name__ == '__main__':
    add_sample_data()
