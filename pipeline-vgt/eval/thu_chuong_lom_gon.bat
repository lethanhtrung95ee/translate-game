@echo off
chcp 65001 >nul
cd /d %~dp0..
echo THU LAI LEGEND OF MORTAL chuong 8, canh dau: bible moi (xung ho theo the loai vo hiep) + dich gia GON
echo (khong chong luat van phong), so voi ban cu. Khong dong vao game. ~$2 quy doi, ~10 phut.
python tools\thu_chuong.py --cap projects\_thu\lom_cap.json --chuong "Story/[A-Z]_S08" --canh "_S0801_01_" --ten lom_s08_gon --cau-hinh eval\cau_hinh\dich_gon.yaml || goto loi
echo Xong. Bao Claude.
pause
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
