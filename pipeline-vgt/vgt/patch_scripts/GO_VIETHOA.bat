@echo off
rem Go Viet hoa: tra lai file goc tu _backup.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0_viethoa\vgt_patch.ps1" -Mode uninstall -Game "%~1"
pause
