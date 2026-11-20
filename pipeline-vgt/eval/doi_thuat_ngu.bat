@echo off
chcp 65001 >nul
cd /d %~dp0..
echo Doi thuat ngu tren CURSED ARMOR V2 (0 token, moi lenh tu sao luu). Tat phien dang dich v2 truoc.
echo 1) 淫魔 = Succubus  2) 小穴 = bướm (bo khe thịt), bo thang tu tuc rieng cua v2 trai chuan chung.
set P=projects\cursed_armor_v2
python -m vgt term %P% --src 淫魔將 --old "Tướng quỷ dâm" --new "Tướng Succubus" || goto loi
python -m vgt term %P% --src 淫魔之力 --old "sức mạnh quỷ dâm" --new "sức mạnh Succubus" || goto loi
python -m vgt term %P% --src 淫魔的戒指 --old "Nhẫn Quỷ Dâm" --new "Nhẫn Succubus" || goto loi
python -m vgt term %P% --src 淫魔契約書 --old "khế ước Quỷ Dâm" --new "khế ước Succubus" || goto loi
python -m vgt term %P% --src 淫魔 --old "quỷ dâm" --new "Succubus" || goto loi
python -m vgt term %P% --src 淫魔 --old "succubus" --new "Succubus" || goto loi
python -m vgt term %P% --src 小穴 --old "'khe thịt/lỗ nhỏ' (KHÔNG 'cô bé')" --new "'bướm'" || goto loi
python -m vgt term %P% --src 肉棒 --old " (Lilina e thẹn thì 'cái ấy')" --new "" || goto loi
python -m vgt term %P% --src 菊穴 --old "lỗ đít/hoa cúc" --new "lỗ đít/cửa sau" || goto loi
python -m vgt term %P% --src 小穴 --old "khe thịt" --new "bướm" || goto loi
findstr /c:"淫魔: Succubus" %P%\thuat_ngu_chot.yaml >nul || echo 淫魔: Succubus>> %P%\thuat_ngu_chot.yaml
echo Xong. Bao Claude.
exit /b 0
:loi
echo LOI - chup man hinh gui Claude.
pause
exit /b 1
