from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import random
import os
import logging
from contextlib import contextmanager
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = Config.SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = Config.SESSION_LIFETIME
CORS(app, supports_credentials=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@contextmanager
def get_db():
    conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        for pragma, value in Config.SQLITE_PRAGMAS.items():
            conn.execute(f'PRAGMA {pragma}={value}')
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

def get_client_ip():
    # For LAN deployment, prioritize server-detected IP (local network IP)
    server_ip = request.environ.get('REMOTE_ADDR', request.remote_addr)
    
    # Check custom header (from client-side detection)
    client_ip = request.headers.get('X-Client-IP')
    
    # If client sent public IP but server sees local IP, use local IP
    if server_ip and server_ip != '127.0.0.1':
        if validate_ip(server_ip):
            return server_ip
    
    # Fallback to client-detected IP
    if client_ip and client_ip != 'server-detected' and validate_ip(client_ip):
        return client_ip
    
    # Check proxy headers
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
        if validate_ip(ip):
            return ip
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip and validate_ip(real_ip):
        return real_ip
    
    return server_ip or 'unknown'

def validate_ip(ip):
    """Basic IP validation"""
    if not ip or not isinstance(ip, str):
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except (ValueError, AttributeError):
        return False

def validate_input(value, max_length=100):
    """Validate and sanitize user input"""
    if not value or not isinstance(value, str):
        return None
    return value.strip()[:max_length]

@app.route('/')
def index():
    return send_from_directory('static', 'login.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = validate_input(data.get('username'), 50)
        password = validate_input(data.get('password'), 100)
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Invalid input'}), 400
        
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ? AND role = "student"', 
                                (username,)).fetchone()
            
            if user and user['password'] == hash_password(password):
                if user['attempted'] == 1:
                    logger.warning(f"User {username} attempted to login after exam completion")
                    return jsonify({'success': False, 'message': 'You have already attempted the exam'}), 403
                
                # Regenerate session
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                session.permanent = True
                
                # Log session
                conn.execute('INSERT INTO user_sessions (user_id, ip_address) VALUES (?, ?)',
                             (user['id'], get_client_ip()))
                
                logger.info(f"User {username} logged in from {get_client_ip()}")
                return jsonify({'success': True})
        
        logger.warning(f"Failed login attempt for username: {username}")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/exam/start', methods=['GET'])
def start_exam():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    try:
        with get_db() as conn:
            # Check if already attempted
            user = conn.execute('SELECT attempted FROM users WHERE id = ?', 
                                (session['user_id'],)).fetchone()
            if user['attempted'] == 1:
                return jsonify({'success': False, 'message': 'Already attempted'}), 403
            
            # Check if exam already started
            existing = conn.execute('SELECT question_ids FROM active_exams WHERE user_id = ?',
                                    (session['user_id'],)).fetchone()
            
            if existing:
                # Resume existing exam
                question_ids = existing['question_ids'].split(',')
                questions_data = conn.execute(f'SELECT * FROM questions WHERE id IN ({existing["question_ids"]})').fetchall()
            else:
                # Get exam settings
                settings = conn.execute('SELECT * FROM exam_settings WHERE id = 1').fetchone()
                
                # Get random questions
                all_questions = conn.execute('SELECT * FROM questions').fetchall()
                
                if len(all_questions) < settings['questions_per_exam']:
                    return jsonify({'success': False, 'message': 'Not enough questions in database'}), 400
                
                selected_questions = random.sample(list(all_questions), settings['questions_per_exam'])
                question_ids = [str(q['id']) for q in selected_questions]
                
                # Store in database
                conn.execute('INSERT INTO active_exams (user_id, question_ids) VALUES (?, ?)',
                             (session['user_id'], ','.join(question_ids)))
                questions_data = selected_questions
            
            questions = []
            for q in questions_data:
                questions.append({
                    'id': q['id'],
                    'question': q['question'],
                    'options': {
                        'A': q['option_a'],
                        'B': q['option_b'],
                        'C': q['option_c'],
                        'D': q['option_d']
                    }
                })
            
            settings = conn.execute('SELECT * FROM exam_settings WHERE id = 1').fetchone()
            logger.info(f"User {session['user_id']} started exam")
            
            return jsonify({
                'success': True,
                'questions': questions,
                'duration': settings['duration_minutes']
            })
    except Exception as e:
        logger.error(f"Exam start error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/exam/submit', methods=['POST'])
def submit_exam():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    try:
        data = request.json
        answers = data.get('answers', {})
        
        with get_db() as conn:
            # Get exam questions from database
            active_exam = conn.execute('SELECT question_ids FROM active_exams WHERE user_id = ?',
                                       (session['user_id'],)).fetchone()
            
            if not active_exam:
                return jsonify({'success': False, 'message': 'Exam not started'}), 400
            
            # Double-check if already attempted
            user = conn.execute('SELECT attempted FROM users WHERE id = ?', 
                                (session['user_id'],)).fetchone()
            if user['attempted'] == 1:
                return jsonify({'success': False, 'message': 'Already attempted'}), 403
            
            # Calculate score
            score = 0
            question_ids = active_exam['question_ids'].split(',')
            
            for qid in question_ids:
                question = conn.execute('SELECT correct_answer FROM questions WHERE id = ?', 
                                        (int(qid),)).fetchone()
                selected = answers.get(qid, '')
                
                # Save answer
                conn.execute('INSERT INTO answers (user_id, question_id, selected_answer) VALUES (?, ?, ?)',
                             (session['user_id'], int(qid), selected))
                
                if selected == question['correct_answer']:
                    score += 1
            
            # Save result
            conn.execute('INSERT INTO results (user_id, ip_address, score, total_questions) VALUES (?, ?, ?, ?)',
                         (session['user_id'], get_client_ip(), score, len(question_ids)))
            
            # Mark as attempted
            conn.execute('UPDATE users SET attempted = 1 WHERE id = ?', (session['user_id'],))
            
            # Delete active exam
            conn.execute('DELETE FROM active_exams WHERE user_id = ?', (session['user_id'],))
            
            logger.info(f"User {session['user_id']} submitted exam. Score: {score}/{len(question_ids)}")
            
            return jsonify({
                'success': True,
                'score': score,
                'total': len(question_ids)
            })
    except Exception as e:
        logger.error(f"Exam submission error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        if 'user_id' in session:
            with get_db() as conn:
                conn.execute('''UPDATE user_sessions SET logout_time = datetime('now', 'localtime'), is_active = 0 
                                WHERE user_id = ? AND is_active = 1''', (session['user_id'],))
            logger.info(f"User {session['user_id']} logged out")
        session.clear()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Logout error: {e}")
        session.clear()
        return jsonify({'success': True})

@app.route('/api/tab-switch', methods=['POST'])
def log_tab_switch():
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    
    try:
        data = request.json
        count = data.get('count', 1)
        
        with get_db() as conn:
            conn.execute('INSERT INTO tab_switches (user_id, ip_address, switch_count) VALUES (?, ?, ?)',
                         (session['user_id'], get_client_ip(), count))
        
        logger.warning(f"Tab switch detected: User {session['user_id']}, Count: {count}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Tab switch logging error: {e}")
        return jsonify({'success': False}), 500

@app.route('/api/tab-switch-count')
def get_tab_switch_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    
    try:
        with get_db() as conn:
            result = conn.execute('SELECT MAX(switch_count) FROM tab_switches WHERE user_id = ?',
                                  (session['user_id'],)).fetchone()
        return jsonify({'count': result[0] if result[0] else 0})
    except Exception as e:
        logger.error(f"Tab switch count error: {e}")
        return jsonify({'count': 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
