@echo off
echo Building Spotify executable...
cd /d "c:\Users\pc\screenshot"

REM Install PyInstaller if not already installed
python -m pip install --user pyinstaller
if errorlevel 1 (
	echo Failed to install/verify PyInstaller.
	exit /b 1
)

REM Build from Spotify.spec (name/icon are defined in the spec file)
python -m PyInstaller --noconfirm --clean Spotify.spec
if errorlevel 1 (
	echo Build failed.
	exit /b 1
)

echo Build complete! Check dist\Spotify\Spotify.exe