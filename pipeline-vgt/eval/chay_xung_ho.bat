@echo off
chcp 65001 >nul
cd /d %~dp0..
echo Danh gia xung ho 01/11: (1) bien tap truong duyet xung ho tren BAN SAO v2, (2) chup lai bo de, (3) bo de x 2 lan. Uoc ~$20 quy doi, ~60 phut.
python -m vgt xung-ho projects\_ab\xh_duyet --duyet || goto loi
copy /Y eval\cases\*.json projects\_ab\xh_duyet\cases_cu\ >nul 2>&1
python -m vgt eval-chup-lai projects\_ab\xh_duyet --game cursed_armor_v2 || goto loi
python -m vgt eval --cau-hinh eval\cau_hinh\C_xh.yaml --nhan C_lan1 --cham || goto loi
python -m vgt eval --cau-hinh eval\cau_hinh\C_xh.yaml --nhan C_lan2 --cham || goto loi
python -m vgt eval-tonghop A_lan B_lan C_lan
echo Xong. Bao Claude doc eval\ket_qua\tong_hop.md.
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
