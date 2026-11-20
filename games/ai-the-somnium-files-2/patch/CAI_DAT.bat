@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
rem Cai ban Viet hoa moi cho AI: The Somnium Files 2 (thay ban Viet hoa cu neu dang cai)
if not exist "viethoa\CAI_VIETHOA.bat" (
  tar -xf "viethoa.zip"
  if errorlevel 1 ( echo Khong giai nen duoc viethoa.zip & pause & exit /b 1 )
)
set "GAME="
set /p GAME=<"viethoa\game_path.txt"
if not exist "%GAME%\" ( echo Khong thay thu muc game: %GAME% & pause & exit /b 1 )
set "SA=%GAME%\AI_TheSomniumFiles2_Data\StreamingAssets"
set "OLD=C:\Games\Viet hoa game\AITSF2_backup"
if not exist "%GAME%\_viethoa_backup\" if exist "%OLD%\Text_en\Const" (
  echo Dang tra game ve ban goc ^(go ban Viet hoa cu^)...
  robocopy "%OLD%\Text_en" "%SA%\Text\en" /E /NFL /NDL /NJH /NJS >nul
  copy /Y "%OLD%\fonts_assets_all_86c91588c854d4650066f54a35e9777b.bundle" "%SA%\aa\StandaloneWindows64\" >nul
)
call "viethoa\CAI_VIETHOA.bat"
