from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import csv
import io
import logging
from contextlib import contextmanager
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='admin_static', static_url_path='')
app.secret_key = Config.ADMIN_SECRET_KEY
app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE
app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
app.config['PERMANENT_SESSION_LIFETIME'] = Config.SESSION_LIFETIME
CORS(app, supports_credentials=True, origins=['http://localhost:5001', 'http://127.0.0.1:5001'])

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

def validate_input(value, max_length=100):
    """Validate and sanitize user input"""
    if not value or not isinstance(value, str):
        return None
    return value.strip()[:max_length]

def admin_required(f):
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
def index():
    return send_from_directory('admin_static', 'admin_login.html')

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        username = validate_input(data.get('username'), 50)
        password = validate_input(data.get('password'), 100)
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Invalid input'}), 400
        
        with get_db() as conn:
            admin = conn.execute('SELECT * FROM users WHERE username = ? AND role = "admin"', 
                                 (username,)).fetchone()
            
            if admin and admin['password'] == hash_password(password):
                # Regenerate session
                session.clear()
                session.permanent = True
                session['admin_id'] = admin['id']
                session['admin_username'] = admin['username']
                
                logger.info(f"Admin {username} logged in")
                return jsonify({'success': True})
        
        logger.warning(f"Failed admin login attempt for username: {username}")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/logout', methods=['POST'])
@admin_required
def admin_logout():
    logger.info(f"Admin {session.get('admin_username')} logged out")
    session.clear()
    return jsonify({'success': True})

# Question Management
@app.route('/api/admin/questions', methods=['GET'])
@admin_required
def get_questions():
    try:
        with get_db() as conn:
            questions = conn.execute('SELECT * FROM questions').fetchall()
        return jsonify({
            'success': True,
            'questions': [dict(q) for q in questions]
        })
    except Exception as e:
        logger.error(f"Get questions error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/questions', methods=['POST'])
@admin_required
def add_question():
    try:
        data = request.json
        question = validate_input(data.get('question'), 500)
        option_a = validate_input(data.get('option_a'), 200)
        option_b = validate_input(data.get('option_b'), 200)
        option_c = validate_input(data.get('option_c'), 200)
        option_d = validate_input(data.get('option_d'), 200)
        correct = data.get('correct_answer')
        
        if not all([question, option_a, option_b, option_c, option_d, correct]):
            return jsonify({'success': False, 'message': 'Invalid input'}), 400
        
        if correct not in ['A', 'B', 'C', 'D']:
            return jsonify({'success': False, 'message': 'Invalid answer'}), 400
        
        with get_db() as conn:
            conn.execute('''INSERT INTO questions 
                            (question, option_a, option_b, option_c, option_d, correct_answer) 
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (question, option_a, option_b, option_c, option_d, correct))
        
        logger.info(f"Admin {session['admin_username']} added question")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Add question error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/questions/<int:qid>', methods=['PUT'])
@admin_required
def update_question(qid):
    try:
        data = request.json
        question = validate_input(data.get('question'), 500)
        option_a = validate_input(data.get('option_a'), 200)
        option_b = validate_input(data.get('option_b'), 200)
        option_c = validate_input(data.get('option_c'), 200)
        option_d = validate_input(data.get('option_d'), 200)
        correct = data.get('correct_answer')
        
        if not all([question, option_a, option_b, option_c, option_d, correct]):
            return jsonify({'success': False, 'message': 'Invalid input'}), 400
        
        if correct not in ['A', 'B', 'C', 'D']:
            return jsonify({'success': False, 'message': 'Invalid answer'}), 400
        
        with get_db() as conn:
            conn.execute('''UPDATE questions SET 
                            question = ?, option_a = ?, option_b = ?, 
                            option_c = ?, option_d = ?, correct_answer = ? 
                            WHERE id = ?''',
                         (question, option_a, option_b, option_c, option_d, correct, qid))
        
        logger.info(f"Admin {session['admin_username']} updated question {qid}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Update question error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/questions/<int:qid>', methods=['DELETE'])
@admin_required
def delete_question(qid):
    try:
        with get_db() as conn:
            conn.execute('DELETE FROM questions WHERE id = ?', (qid,))
        logger.info(f"Admin {session['admin_username']} deleted question {qid}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Delete question error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

# Student Management
@app.route('/api/admin/students', methods=['GET'])
@admin_required
def get_students():
    try:
        with get_db() as conn:
            students = conn.execute('SELECT id, username, attempted FROM users WHERE role = "student"').fetchall()
        return jsonify({
            'success': True,
            'students': [dict(s) for s in students]
        })
    except Exception as e:
        logger.error(f"Get students error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/students', methods=['POST'])
@admin_required
def add_student():
    try:
        data = request.json
        username = validate_input(data.get('username'), 50)
        password = validate_input(data.get('password'), 100)
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Invalid input'}), 400
        
        with get_db() as conn:
            try:
                conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                             (username, hash_password(password), 'student'))
                logger.info(f"Admin {session['admin_username']} added student {username}")
                return jsonify({'success': True})
            except sqlite3.IntegrityError:
                return jsonify({'success': False, 'message': 'Username already exists'}), 400
    except Exception as e:
        logger.error(f"Add student error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/students/<int:sid>', methods=['DELETE'])
@admin_required
def delete_student(sid):
    try:
        with get_db() as conn:
            conn.execute('DELETE FROM users WHERE id = ? AND role = "student"', (sid,))
        logger.info(f"Admin {session['admin_username']} deleted student {sid}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Delete student error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

# Exam Settings
@app.route('/api/admin/settings', methods=['GET'])
@admin_required
def get_settings():
    try:
        with get_db() as conn:
            settings = conn.execute('SELECT * FROM exam_settings WHERE id = 1').fetchone()
        return jsonify({
            'success': True,
            'settings': dict(settings)
        })
    except Exception as e:
        logger.error(f"Get settings error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/settings', methods=['PUT'])
@admin_required
def update_settings():
    try:
        data = request.json
        duration = int(data.get('duration_minutes', 30))
        questions = int(data.get('questions_per_exam', 10))
        
        if duration < 1 or questions < 1:
            return jsonify({'success': False, 'message': 'Invalid values'}), 400
        
        with get_db() as conn:
            conn.execute('UPDATE exam_settings SET duration_minutes = ?, questions_per_exam = ? WHERE id = 1',
                         (duration, questions))
        
        logger.info(f"Admin {session['admin_username']} updated settings")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Update settings error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

# Results Management
@app.route('/api/admin/results', methods=['GET'])
@admin_required
def get_results():
    try:
        with get_db() as conn:
            results = conn.execute('''SELECT u.username, r.ip_address, r.score, r.total_questions, r.submitted_at 
                                      FROM results r 
                                      JOIN users u ON r.user_id = u.id 
                                      ORDER BY r.score DESC, r.submitted_at ASC''').fetchall()
        return jsonify({
            'success': True,
            'results': [dict(r) for r in results]
        })
    except Exception as e:
        logger.error(f"Get results error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/results/export', methods=['GET'])
@admin_required
def export_results():
    try:
        with get_db() as conn:
            results = conn.execute('''SELECT u.username, r.ip_address, r.score, r.total_questions, 
                                      ROUND(r.score * 100.0 / r.total_questions, 2) as percentage,
                                      r.submitted_at 
                                      FROM results r 
                                      JOIN users u ON r.user_id = u.id 
                                      ORDER BY r.score DESC, r.submitted_at ASC''').fetchall()
            
            tab_switches = conn.execute('''SELECT u.username, t.ip_address, MAX(t.switch_count) as max_switches
                                           FROM tab_switches t
                                           JOIN users u ON t.user_id = u.id
                                           GROUP BY u.username, t.ip_address
                                           ORDER BY max_switches DESC''').fetchall()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Rank', 'Username', 'IP Address', 'Score', 'Total Questions', 'Percentage', 'Submitted At'])
        
        for idx, r in enumerate(results, 1):
            writer.writerow([idx, r['username'], r['ip_address'], r['score'], r['total_questions'], 
                            f"{r['percentage']}%", r['submitted_at']])
        
        writer.writerow([])
        writer.writerow(['TAB SWITCHES'])
        writer.writerow(['Username', 'IP Address', 'Max Switches'])
        for t in tab_switches:
            writer.writerow([t['username'], t['ip_address'], t['max_switches']])
        
        logger.info(f"Admin {session['admin_username']} exported results")
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=exam_results.csv'
        }
    except Exception as e:
        logger.error(f"Export results error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/tab-switches', methods=['GET'])
@admin_required
def get_tab_switches():
    try:
        with get_db() as conn:
            results = conn.execute('''SELECT u.username, t.ip_address, MAX(t.switch_count) as max_switches, COUNT(*) as total_entries
                                      FROM tab_switches t
                                      JOIN users u ON t.user_id = u.id
                                      GROUP BY u.username, t.ip_address
                                      ORDER BY max_switches DESC''').fetchall()
        return jsonify({
            'success': True,
            'tab_switches': [{'username': r['username'], 'ip_address': r['ip_address'], 
                             'max_switches': r['max_switches'], 'total_entries': r['total_entries']} for r in results]
        })
    except Exception as e:
        logger.error(f"Get tab switches error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/sessions', methods=['GET'])
@admin_required
def get_sessions():
    try:
        with get_db() as conn:
            sessions = conn.execute('''SELECT u.username, s.ip_address, s.login_time, s.logout_time, s.is_active
                                       FROM user_sessions s
                                       JOIN users u ON s.user_id = u.id
                                       ORDER BY s.login_time DESC''').fetchall()
        return jsonify({
            'success': True,
            'sessions': [dict(s) for s in sessions]
        })
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
