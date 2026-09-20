@echo off
setlocal
cd /d "%~dp0"

echo [1/4] Creating virtual environment...
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 python -m venv .venv
)
if not exist ".venv\Scripts\python.exe" (
    echo Could not create a Python virtual environment.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo [2/4] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

if not exist "vendor\ffmpeg.exe" (
    echo.
    echo WARNING: vendor\ffmpeg.exe was not found.
    echo The app will only process audio/video if FFmpeg is available in Windows PATH.
    echo To embed FFmpeg, copy ffmpeg.exe and optionally ffprobe.exe into vendor\ then run again.
    echo.
)

echo [3/4] Building one-file Windows executable...
python -m PyInstaller --noconfirm --clean YouTubeDownloaderAR.spec
if errorlevel 1 (
    echo PyInstaller build failed.
    pause
    exit /b 1
)

echo [4/4] Build complete:
dist\YouTubeDownloaderAR.exe
pause
