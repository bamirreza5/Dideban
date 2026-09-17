@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/5] Creating virtual environment...
    python -m venv .venv
)

echo [2/5] Installing dependencies...
call ".venv\Scripts\activate.bat"
python -m pip install --disable-pip-version-check -r requirements.txt

echo [3/5] Applying database migrations...
python manage.py migrate

echo [4/5] Creating idempotent demo data...
python manage.py seed_demo

echo [5/5] Starting Dideban CRM at http://127.0.0.1:8000/
echo Demo username: demo
echo Demo password: Demo12345!
python manage.py runserver
endlocal

