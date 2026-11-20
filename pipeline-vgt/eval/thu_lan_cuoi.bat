@echo off
chcp 65001 >nul
cd /d %~dp0..
echo THU LAN CUOI luong moi (chi dao co "lam ro" + dich gia Sonnet) tren 2 canh mau. ~$1,5 quy doi, ~10 phut.
set C=--case cs_cam_xuc_map124_ev5p6 --case xung_ho_trum_phong_giam
python -m vgt mach projects\cursed_armor_v2 %C% --force || goto loi
python -m vgt eval-chup-lai projects\cursed_armor_v2 --game cursed_armor_v2 %C% || goto loi
python -m vgt eval %C% --nhan luong_moi_v2 --cham || goto loi
python -m vgt eval-doc luong_moi_v2 --so-voi luong_moi_sonnet --out eval\ket_qua\doc_v2_data.json || goto loi
echo Xong. Bao Claude.
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
