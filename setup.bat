@echo off
echo ========================================
echo   MCQ Exam System - Setup Script
echo ========================================
echo.

echo [1/3] Installing dependencies...
py -m pip install -r requirements.txt
echo.

echo [2/3] Generating secure secret keys...
py -c "import os; print('SECRET_KEY=' + os.urandom(24).hex())" > .env.tmp
py -c "import os; print('ADMIN_SECRET_KEY=' + os.urandom(24).hex())" >> .env.tmp
echo DB_PATH=exam.db >> .env.tmp
echo SESSION_LIFETIME=3600 >> .env.tmp
echo MAX_LOGIN_ATTEMPTS=5 >> .env.tmp
echo RATE_LIMIT_WINDOW=60 >> .env.tmp

if exist .env (
    echo .env file already exists. Backup created as .env.backup
    copy .env .env.backup >nul
)
move /Y .env.tmp .env >nul
echo Secure keys generated in .env file
echo.

echo [3/3] Initializing database...
py init_db.py
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo IMPORTANT: Your secure keys are in .env file
echo Default admin credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo CHANGE THE ADMIN PASSWORD IMMEDIATELY!
echo.
pause
