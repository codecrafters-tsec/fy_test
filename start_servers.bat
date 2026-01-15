@echo off
echo ========================================
echo   MCQ Exam System - Starting Servers
echo ========================================
echo.

echo Checking if database exists...
if not exist exam.db (
    echo Database not found. Initializing...
    py init_db.py
    echo.
)

echo.
echo Starting servers...
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
echo Press Ctrl+C to stop servers
echo.

start "Student Portal" cmd /k py app.py
start "Admin Panel" cmd /k py admin_app.py

echo Both servers started in separate windows!
pause
