# 🚀 DEPLOYMENT GUIDE - SECURE VERSION

## ⚠️ CRITICAL: Run Setup First

```bash
# Run this ONCE before first use
setup.bat
```

This will:
- ✅ Install all dependencies
- ✅ Generate secure random secret keys
- ✅ Create .env configuration file
- ✅ Initialize database

## 🔐 Security Checklist

### 1. Change Default Admin Password
```
1. Login to admin panel: http://localhost:5001
2. Username: admin
3. Password: admin123
4. IMMEDIATELY change this password!
```

### 2. Verify .env File
Check that `.env` contains random keys (NOT the defaults):
```
SECRET_KEY=<long random hex string>
ADMIN_SECRET_KEY=<different long random hex string>
```

### 3. Protect Sensitive Files
Never share or commit:
- ❌ `.env` file
- ❌ `exam.db` database
- ❌ Log files

## 🎯 Quick Start

### Development Mode
```bash
start_servers.bat
```

### Production Mode (150+ users)
```bash
start_servers_production.bat
```

## 📊 What's Fixed

### Security Improvements ✅
- ✅ Secure random secret keys (not hardcoded)
- ✅ Input validation on all endpoints
- ✅ IP address validation
- ✅ Session regeneration on login
- ✅ Database connection pooling with context managers
- ✅ SQL injection protection (already had this)
- ✅ Comprehensive error logging

### Code Quality ✅
- ✅ Proper exception handling
- ✅ No connection leaks
- ✅ Logging for all critical actions
- ✅ Configuration management
- ✅ Race condition protection

### Performance ✅
- ✅ Context managers for auto-commit/rollback
- ✅ Optimized database pragmas
- ✅ Proper resource cleanup

## 📝 Logs

All actions are now logged:
- Student logins/logouts
- Exam submissions
- Admin actions
- Tab switch violations
- Errors and warnings

Check console output for real-time logs.

## 🔄 Updating Existing Installation

If you already have the system running:

```bash
# 1. Backup your database
copy exam.db exam.db.backup

# 2. Run setup
setup.bat

# 3. Restart servers
```

Your existing data will be preserved.

## 🆘 Troubleshooting

### "Module 'config' not found"
```bash
# Make sure config.py exists
# Re-run setup.bat
```

### "Module 'dotenv' not found"
```bash
py -m pip install python-dotenv
```

### Database locked errors
```bash
# Stop all servers first
# Delete exam.db-shm and exam.db-wal
# Restart servers
```

## 📞 Support

Everything should work exactly as before, just more secure!

If something breaks:
1. Check logs in console
2. Verify .env file exists
3. Ensure all dependencies installed
4. Try fresh setup with setup.bat
