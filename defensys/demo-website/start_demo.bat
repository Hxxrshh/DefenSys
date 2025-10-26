@echo off
echo ========================================
echo   DefenSys Demo Vulnerable Website
echo ========================================
echo.
echo WARNING: This contains intentional vulnerabilities!
echo DO NOT expose to the internet!
echo.
echo Installing dependencies...
pip install Flask Werkzeug

echo.
echo Starting demo website on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py
