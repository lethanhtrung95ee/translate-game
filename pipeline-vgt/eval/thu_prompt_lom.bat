@echo off
chcp 65001 >nul
cd /d %~dp0..
echo THU CACH MOI tren LEGEND OF MORTAL: Opus dich canh dau chuong 8 (42 cau) theo docs\prompt_dich_thuong.md,
echo dung ho so xung ho/thuat ngu cua ban LoM, roi so mu voi ban LoM dang co. ~$0,5 quy doi, ~5 phut.
python tools\thu_prompt_cap.py --cap projects\_thu\lom_cap.json --canh "_S0801_01_" --ho-so projects\_thu\lom_ho_so_muc5.md --prompt docs\prompt_dich_thuong.md --ten lom_pm || goto loi
echo Xong. Bao Claude.
pause
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
