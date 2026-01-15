import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    ADMIN_SECRET_KEY = os.getenv('ADMIN_SECRET_KEY', os.urandom(24).hex())
    
    # Database
    DB_PATH = os.getenv('DB_PATH', 'exam.db')
    
    # Session
    SESSION_LIFETIME = int(os.getenv('SESSION_LIFETIME', 3600))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate Limiting
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))
    
    # Performance
    SQLITE_PRAGMAS = {
        'journal_mode': 'WAL',
        'synchronous': 'NORMAL',
        'cache_size': 10000
    }
