# Cai dat phu thuoc va kiem tra moi truong. Chay: powershell -ExecutionPolicy Bypass -File setup.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { Write-Host "Chua co Python. Cai tu https://www.python.org (tick 'Add to PATH')." -ForegroundColor Red; exit 1 }
python --version

python -m pip install --upgrade -r requirements.txt

$cc = Get-Command claude -ErrorAction SilentlyContinue
if (-not $cc) {
  Write-Host "Chua co Claude Code. Cai theo https://code.claude.com/docs/en/setup roi chay 'claude' de dang nhap." -ForegroundColor Yellow
} else {
  claude --version
  $auth = claude auth status 2>$null | Out-String
  if ($auth -match '"authMethod"\s*:\s*"claude.ai"') { Write-Host "Claude Code: dang nhap bang goi dang ky - OK" -ForegroundColor Green }
  else { Write-Host "Kiem tra dang nhap: chay 'claude' va dang nhap bang tai khoan Pro/Max (khong dung API key)." -ForegroundColor Yellow }
}

python -m unittest discover -s tests
Write-Host "Xong." -ForegroundColor Green
