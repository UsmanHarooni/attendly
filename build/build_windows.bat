@echo off
REM Build the Windows one-file executable: build\build_windows.bat
REM Requires: Windows, Python 3.10+, and the venv from requirements.txt
cd /d "%~dp0.."

if not exist venv (
  py -m venv venv
  venv\Scripts\pip install -r requirements.txt
)
venv\Scripts\pip install pyinstaller

venv\Scripts\pyinstaller --noconfirm --clean --onefile --windowed --name FaceTrack ^
  --hidden-import cv2.face ^
  --add-data "assets;assets" ^
  --add-data "data/haarcascade_frontalface_default.xml;data" ^
  main.py

echo Done: dist\FaceTrack.exe
pause
