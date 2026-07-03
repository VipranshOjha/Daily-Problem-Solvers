@echo off
echo Creating Release Package...
call build.bat
mkdir Release
copy dist\Full-Page-Screenshot.exe Release\
copy README.md Release\
copy LICENSE Release\
echo Release package created in Release/ folder.
pause
