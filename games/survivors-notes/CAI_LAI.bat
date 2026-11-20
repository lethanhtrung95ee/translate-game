@echo off
chcp 65001 >nul
echo.| call "%~dp0patch\survivors-notes-vi\CAI_VIETHOA.bat" > "%~dp0cai_lai_log.txt" 2>&1
(goto) 2>nul & del "%~f0"
