@echo off
cd /d "%~dp0"
set ANTHROPIC_API_KEY=
echo === Buoc 1: cai dat va kiem tra ===
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1
if errorlevel 1 (echo Setup loi. Xem thong bao o tren. & pause & exit /b 1)
where claude >nul 2>nul
if errorlevel 1 (echo Chua co Claude Code. Cai tai https://code.claude.com/docs/en/setup roi chay lai file nay. & pause & exit /b 1)
echo === Buoc 2: mo Claude Code ===
claude "Doc PROMPT_PHIEN_DAU.md va lam theo dung nhiem vu trong do."
pause
