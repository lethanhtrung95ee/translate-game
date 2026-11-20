@echo off
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path \"%~dp0..\goc\*\" -DestinationPath \"%~dp0..\goc.zip\" -Force" > "%~dp0nen_log.txt" 2>&1
