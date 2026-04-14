@echo off
REM Build script for creating Windows executable

REM Add uv to PATH
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

echo Installing dependencies...
uv sync --group dev

echo Building executable...
uv run pyinstaller easy-ecoc.spec

echo.
echo Build complete! Executable is located at: dist\Easy-eCoC.exe
pause
