@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0trich.ps1" > "%~dp0trich_log.txt" 2>&1
