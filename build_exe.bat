@echo off
echo Building PyAutoGUI executable...
cd /d "c:\Users\pc\screenshot"

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build the executable with necessary options for PyAutoGUI
pyinstaller --onefile --windowed --hidden-import pyautogui --hidden-import keyboard --hidden-import pycaw --hidden-import comtypes --hidden-import git --hidden-import ctypes.wintypes --add-data "requirements.txt;." screenshot.py

echo Build complete! Check the 'dist' folder for screenshot.exe