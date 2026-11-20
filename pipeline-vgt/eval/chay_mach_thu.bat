@echo off
chcp 65001 >nul
cd /d %~dp0..
echo THU BOI CANH KICH (02/11) tren 4 canh mau CURSED ARMOR V2: bien kich truong viet "mach toi day" cho 4 canh,
echo dich lai 4 canh + cham, roi xuat du lieu doc mu so voi ban doc_thu2. Uoc tinh ~$5-6 quy doi, ~15-20 phut.
if not exist eval\ket_qua\*_doc_thu2.json (
  echo Chua co ket qua doc_thu2: doi eval\chay_sua_v2.bat chay xong roi chay lai file nay.
  pause
  exit /b 1
)
set C=--case cs_adult_tho_map100_ev26p0 --case cs_cam_xuc_map124_ev5p6 --case zh_giong_may_owen --case xung_ho_trum_phong_giam
python -m vgt mach projects\cursed_armor_v2 %C% || goto loi
python -m vgt eval-chup-lai projects\cursed_armor_v2 --game cursed_armor_v2 %C% || goto loi
python -m vgt eval %C% --nhan doc_thu3_mach --cham || goto loi
python -m vgt eval-doc doc_thu3_mach --so-voi doc_thu2 --out eval\ket_qua\doc_mach_data.json || goto loi
echo Xong. Bao Claude.
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
