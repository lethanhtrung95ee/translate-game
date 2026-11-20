@echo off
chcp 65001 >nul
cd /d %~dp0..
echo Sua theo gop y 02/11 tren CURSED ARMOR V2 (co sao luu): (1) bien tap truong ra thuat ngu + ap ten nguoi dung chot,
echo (2) chot lai xung ho (han che 'toi'), (3) quet loi chung, (4) dich lai 4 canh mau cho anh doc. ~$10 quy doi, ~30 phut.
python -m vgt thuat-ngu projects\cursed_armor_v2 || goto loi
python -m vgt xung-ho projects\cursed_armor_v2 --duyet || goto loi
python -m vgt quet projects\cursed_armor_v2 || goto loi
python -m vgt eval-chup-lai projects\cursed_armor_v2 --game cursed_armor_v2 || goto loi
python -m vgt eval --case cs_adult_tho_map100_ev26p0 --case cs_cam_xuc_map124_ev5p6 --case zh_giong_may_owen --case xung_ho_trum_phong_giam --nhan doc_thu2 --cham || goto loi
echo Xong. Bao Claude.
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
