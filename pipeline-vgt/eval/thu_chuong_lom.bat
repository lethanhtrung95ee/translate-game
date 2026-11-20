@echo off
chcp 65001 >nul
cd /d %~dp0..
echo THU LEGEND OF MORTAL (huong C): bible rieng chuong 8 (363 cau), chi dao + dich lai canh dau chuong (42 cau)
echo bang luong moi, roi so voi ban dich cu. Khong dong vao game. Uoc tinh ~$3 quy doi, ~10-15 phut.
python tools\thu_chuong.py --cap projects\_thu\lom_cap.json --chuong "Story/[A-Z]_S08" --canh "_S0801_01_" --ten lom_s08 || goto loi
echo Xong. Bao Claude.
pause
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
