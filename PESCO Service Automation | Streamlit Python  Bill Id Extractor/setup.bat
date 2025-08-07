@echo off
setlocal
title ⚡ PESCO Bill Extractor Setup
echo ====================================================
echo ⚡ Updating and Launching App
echo ====================================================

:: --- CONFIG ---
set REPO_URL=https://github.com/OzairKhan1/DataScrapper.git
set REPO_NAME=DataScrapper
set DEST_PATH=%~dp0%REPO_NAME%
set PY_EXE=python

:: --- STEP 1: Ensure Git is available ---
echo 🛠 Checking Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git not found. Installing Git...
    curl -L -o git-installer.exe https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe
    start /wait git-installer.exe /VERYSILENT /NORESTART
    echo 🔁 Git installed. Please rerun this script.
    pause
    exit /b
)

:: --- STEP 2: Clone or Update Repo ---
if not exist "%DEST_PATH%" (
    echo 📥 Cloning repository...
    git clone %REPO_URL%
) else (
    echo 🔁 Updating repository...
    cd /d "%DEST_PATH%"
    git reset --hard
    git clean -fd
    git pull
)

cd /d "%DEST_PATH%"

:: --- STEP 3: Check Python ---
echo 🛠 Checking Python...
%PY_EXE% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing...
    curl -L -o python-installer.exe https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    echo 🔁 Python installed. Please rerun this script.
    pause
    exit /b
)

:: --- STEP 4: Create Virtual Environment if Missing ---
if not exist "venv" (
    echo 📦 Creating virtual environment...
    %PY_EXE% -m venv venv
)

call venv\Scripts\activate

:: --- STEP 5: Install Dependencies Only If Changed ---
echo 🔍 Checking requirements...
set REQ_HASH_FILE=venv\req_hash.txt
certutil -hashfile requirements.txt SHA256 > tmp_hash.txt
for /f "tokens=2 delims= " %%i in ('findstr /i /c:"SHA256" tmp_hash.txt') do set CURRENT_HASH=%%i
if exist "%REQ_HASH_FILE%" (
    set /p SAVED_HASH=<%REQ_HASH_FILE%
) else (
    set SAVED_HASH=none
)

if "%CURRENT_HASH%" neq "%SAVED_HASH%" (
    echo 📦 Installing or updating dependencies...
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    echo %CURRENT_HASH% > %REQ_HASH_FILE%
) else (
    echo ✅ Requirements unchanged. Skipping install.
)
del tmp_hash.txt

:: --- STEP 6: Clean Previous State ---
echo 🧹 Cleaning up old processes and cache...
taskkill /f /im streamlit.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
if exist "__pycache__" rd /s /q __pycache__

:: --- STEP 7: Launch Streamlit App ---
echo 🚀 Launching Streamlit app...
start "" streamlit run DataScrapper.py

exit /b
