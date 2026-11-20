@echo off
chcp 65001 >nul
cd /d "%~dp0"
set ANTHROPIC_API_KEY=
echo === Buoc 1: cai dat va kiem tra ===
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1
if errorlevel 1 (echo Setup loi. Xem thong bao o tren. & pause & exit /b 1)
where claude >nul 2>nul
if errorlevel 1 (echo Chua co Claude Code. Cai tai https://code.claude.com/docs/en/setup roi chay lai file nay. & pause & exit /b 1)
echo.
echo === Buoc 2: chon viec ===
echo   1 = Lam tiep mot game dang do (chon game)
echo   2 = Dich game moi / lam tiep game dich bang cach moi (Claude tu dich theo docs\prompt_dich_*.md)
echo   3 = Bao loi sau khi choi thu mot game (anh chup trong projects\^<game^>\bao_loi\)
echo   4 = Nang cap he thong vgt (theo CHECKPOINT.md chung)
set /p CHON=Chon 1-4 roi Enter: 
if "%CHON%"=="2" goto MOI
if "%CHON%"=="4" goto HETHONG
if "%CHON%"=="1" goto CHONGAME
if "%CHON%"=="3" goto CHONGAME
echo Khong hop le. & goto HET

:CHONGAME
echo.
python -m vgt list
set GAME=
set /p SO=Chon so thu tu cua game roi Enter: 
for /f "tokens=1,2" %%a in ('python -m vgt list --plain') do if "%%a"=="%SO%" set GAME=%%b
if "%GAME%"=="" (echo Khong co game so %SO%. & goto HET)
if "%CHON%"=="3" goto LOI
claude "Lam tiep game %GAME%: doc CLAUDE.md, roi projects\%GAME%\CHECKPOINT.md muc Viec tiep theo va lam theo. CHI lam game nay, khong dong vao game khac."
goto HET

:MOI
set /p GAME=Dan duong dan thu muc game (hoac ten game, khong can ngoac kep) roi Enter: 
set /p LON=Game co noi dung 18+ khong? Go c hoac k roi Enter: 
set PR=docs\prompt_dich_thuong.md
if /i "%LON%"=="c" set PR=docs\prompt_dich_18.md
claude "Doc %PR% va lam dung theo do (bo qua quy trinh vgt run trong CLAUDE.md). Game can dich: %GAME%. Ngon ngu dich: tieng Viet. Lam viec trong projects\TEN-GAME\ (ten ngan khong dau) (tu tao neu chua co). Neu da co HANDOFF.md o do thi doc va lam tiep dung cho do. Giu so ban giao HANDOFF.md theo khung docs\tham_khao\LOM_HANDOFF_mau.md, cap nhat sau moi lo de phien sau lam tiep. Khong sua game goc; ban Viet hoa giao o ..\Ten game\ voi CAI_VIETHOA.bat (sao luu roi cai) va GO_VIETHOA.bat (go). Cu lam lien tuc, khong hoi lai."
goto HET

:LOI
claude "Nguoi dung choi thu game %GAME% va bao loi: doc anh + ghi chu trong projects\%GAME%\bao_loi\. Tra tung loi ve dong trong project.db, sua bang pipeline (khong sua tay hang loat), MOI LOI LA MOT LOAI LOI: lam du 6 buoc docs/lessons/README.md muc 5b (tim goc, chan chung cho moi game, them vao bo de eval, chay bo de, quet lai moi game dang lam bang vgt quet/term/xung-ho, ghi bai hoc), apply lai va kiem chung. Lam theo CLAUDE.md. CHI lam game nay."
goto HET

:HETHONG
claude "Doc CHECKPOINT.md, muc Prompt cho phien tiep theo (nang cap he thong), va lam theo."

:HET
pause
