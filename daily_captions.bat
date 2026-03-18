@echo off
REM Daily caption generator — called by Windows Task Scheduler
REM Generates 3 caption videos and copies them to Google Drive

cd /d "C:\Users\antod\OneDrive\Bureau\Variator"
python daily_captions.py >> daily_captions.log 2>&1
