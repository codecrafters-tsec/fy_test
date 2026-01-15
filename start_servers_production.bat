@echo off
echo ========================================
echo   MCQ Exam System - PRODUCTION MODE
echo   Optimized for 150+ Concurrent Users
echo ========================================
echo.

echo Checking if database exists...
if not exist exam.db (
    echo Database not found. Initializing...
    py init_db.py
    echo.
)

echo.
echo Installing production server (Waitress)...
py -m pip install waitress
echo.

echo Starting production servers...
echo.
echo Student Portal: http://localhost:5000
echo Admin Panel: http://localhost:5001
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    goto :found
)
:found
echo Your Local IP: %IP%
echo Students should access: http://%IP%:5000
echo Admin should access: http://%IP%:5001
echo.
echo Optimized for 150+ concurrent users
echo Press Ctrl+C to stop servers
echo.

start "Student Portal (Production)" cmd /k py -c "from waitress import serve; from app import app; print('Student Portal running on port 5000 (8 threads)'); serve(app, host='0.0.0.0', port=5000, threads=8)"
start "Admin Panel (Production)" cmd /k py -c "from waitress import serve; from admin_app import app; print('Admin Panel running on port 5001 (4 threads)'); serve(app, host='0.0.0.0', port=5001, threads=4)"

echo Both servers started in production mode!
pause
