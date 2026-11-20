@echo off
chcp 65001 >nul
cd /d %~dp0..
echo Bo de kiem tra chung: chay cau hinh hien tai (prompt v3 + chuan 18+ chung), co kiem dinh vien cham.
python -m vgt eval --nhan chuan18 --cham || goto loi
echo Xong. Bao Claude doc eval\ket_qua.
pause
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
