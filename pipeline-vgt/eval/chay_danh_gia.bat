@echo off
chcp 65001 >nul
cd /d %~dp0..
echo Danh gia 01/11: 21 case x (A: v3 khong 18+, B: v3 + 18+ + ap sua) x 2 lan. Uoc ~$30 quy doi, ~60-90 phut.
python -m vgt eval --cau-hinh eval\cau_hinh\A_v3.yaml --nhan A_lan1 --cham || goto loi
python -m vgt eval --cau-hinh eval\cau_hinh\B_v3_18_sua.yaml --nhan B_lan1 --cham || goto loi
python -m vgt eval --cau-hinh eval\cau_hinh\A_v3.yaml --nhan A_lan2 --cham || goto loi
python -m vgt eval --cau-hinh eval\cau_hinh\B_v3_18_sua.yaml --nhan B_lan2 --cham || goto loi
python -m vgt eval-tonghop A_lan B_lan
echo Xong. Bao Claude doc eval\ket_qua\tong_hop.md.
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
