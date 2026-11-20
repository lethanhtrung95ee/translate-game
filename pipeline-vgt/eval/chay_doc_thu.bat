@echo off
chcp 65001 >nul
cd /d %~dp0..
echo Dich 4 canh bang cau hinh moi (van phong nguoi dung + xung ho theo dong + bible da duyet), de nguoi dung doc mu. ~$3 quy doi, ~10 phut.
python -m vgt eval --case cs_adult_tho_map100_ev26p0 --case cs_cam_xuc_map124_ev5p6 --case zh_giong_may_owen --case xung_ho_trum_phong_giam --nhan doc_thu --cham || goto loi
for /f "delims=" %%f in ('dir /b /o-d eval\ket_qua\*_doc_thu.json') do (set F=%%f & goto co)
:co
python -m vgt eval-doc eval\ket_qua\%F: =% --out eval\ket_qua\doc_thu_data.json || goto loi
echo Xong. Bao Claude.
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
