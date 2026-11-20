@echo off
chcp 65001 >nul
cd /d %~dp0..
echo THU LUONG MOI (02/11) tren 2 canh: canh cau hon + canh 18+ (Trum phong giam).
echo 1) bien kich truong viet CHI DAO CANH moi, 2) dich gia OPUS, 3) dich gia SONNET, 4) du lieu doc mu A/B.
echo Uoc tinh ~$3 quy doi, ~15 phut.
set C=--case cs_cam_xuc_map124_ev5p6 --case xung_ho_trum_phong_giam
python -m vgt mach projects\cursed_armor_v2 %C% --force || goto loi
python -m vgt eval-chup-lai projects\cursed_armor_v2 --game cursed_armor_v2 %C% || goto loi
python -m vgt eval %C% --cau-hinh eval\cau_hinh\dich_opus.yaml --nhan luong_moi_opus --cham || goto loi
python -m vgt eval %C% --cau-hinh eval\cau_hinh\dich_sonnet.yaml --nhan luong_moi_sonnet --cham || goto loi
python -m vgt eval-doc luong_moi_sonnet --so-voi luong_moi_opus --out eval\ket_qua\doc_ab_data.json || goto loi
echo Xong. Bao Claude.
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
