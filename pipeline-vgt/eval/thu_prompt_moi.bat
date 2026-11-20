@echo off
chcp 65001 >nul
cd /d %~dp0..
echo THU CACH MOI: Opus dich canh Trum phong giam (18+, 39 cau) theo docs\prompt_dich_18.md, khong luat vgt.
echo So mu voi ban vgt (luong_moi_v2). ~$1 quy doi, ~5 phut.
python tools\thu_prompt_moi.py --case xung_ho_trum_phong_giam --prompt docs\prompt_dich_18.md --nhan prompt_moi || goto loi
python -m vgt eval-doc prompt_moi --so-voi luong_moi_v2 --out eval\ket_qua\doc_pm_data.json || goto loi
echo Xong. Bao Claude.
pause
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
