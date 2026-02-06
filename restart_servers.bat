@echo off
echo ============================================
echo RESTARTING SERVERS FOR GEMINI API KEY
echo ============================================
echo.
echo This script will help you restart the servers.
echo.
echo STEP 1: Stop the current servers
echo --------------------------------
echo 1. Go to the terminal running "python manage.py runserver"
echo 2. Press Ctrl+C to stop it
echo.
echo 3. Go to the terminal running "python manage.py process_tasks"
echo 4. Press Ctrl+C to stop it
echo.
echo STEP 2: Start the servers again
echo --------------------------------
echo.
echo Press any key when you're ready to start the backend server...
pause > nul

cd backend
start cmd /k "python manage.py runserver"

echo.
echo Backend server started in a new window!
echo.
echo Press any key to start the background worker...
pause > nul

start cmd /k "python manage.py process_tasks"

echo.
echo ============================================
echo SERVERS RESTARTED!
echo ============================================
echo.
echo Now run the test again:
echo   cd backend
echo   python test_dynamic_questions.py
echo.
echo You should see:
echo   Gemini Service Available: Yes
echo   (and NO errors about invalid API key)
echo.
pause
