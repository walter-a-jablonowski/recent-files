@echo off
cd /d "G:\fld with\blanks\startup"
if not exist "file_sys_chg.py" (
  echo Error: file_sys_chg.py not found in %CD%
  pause
  exit /b 1
)

start /min python "file_sys_chg.py" "G:\fld with\blanks" "G:\fld with\blanks\recent_files.log"
if errorlevel 1 (
  echo Error running Python script
  pause
  exit /b 1
)
