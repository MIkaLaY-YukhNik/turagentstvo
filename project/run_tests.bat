@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
pip install pytest flask flask-babel python-dotenv werkzeug requests -q
python -m pytest tests\test_app.py -v --tb=short
pause

