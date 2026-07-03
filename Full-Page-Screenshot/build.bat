@echo off
echo Building Full-Page-Screenshot...
call "..\\.venv\\Scripts\\activate.bat"
pyinstaller --clean Full-Page-Screenshot.spec
echo Build complete. Executable is in the dist/ folder.
pause
