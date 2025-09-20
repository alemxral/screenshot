@echo off
REM Caps Lock LED Blinker - Easy launcher
REM Usage: blink.bat <number> or blink.bat <answer>

if "%1"=="" (
    echo.
    echo 💡 Caps Lock LED Blinker
    echo ========================
    echo.
    echo Usage:
    echo   blink.bat ^<number^>     # Blink N times ^(1-20^)
    echo   blink.bat ^<answer^>     # Blink for quiz answer ^(A=1, B=2, etc.^)
    echo.
    echo Examples:
    echo   blink.bat 3             # Blink 3 times
    echo   blink.bat B             # Blink 2 times ^(answer B^)
    echo.
    pause
    goto :eof
)

python blink_caps.py %1
