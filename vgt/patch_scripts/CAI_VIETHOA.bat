@echo off
rem Cai Viet hoa. Co the keo tha thu muc game vao file nay, hoac de trong = duong dan luc tao patch.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0_viethoa\vgt_patch.ps1" -Mode install -Game "%~1"
pause
