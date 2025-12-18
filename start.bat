@echo off

set BASE=%~dp0

call "%BASE%venv\Scripts\activate.bat"
python "%BASE%whisper-tranny.py"

pause
