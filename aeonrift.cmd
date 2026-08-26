@echo off
rem AEONRIFT Windows Command Prompt Wrapper
setlocal
set "SCRIPT_DIR=%~dp0"
python "%SCRIPT_DIR%aeonrift" %*
endlocal
