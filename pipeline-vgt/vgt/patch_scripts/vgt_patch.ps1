# Cai / go Viet hoa. Tao boi vgt. Chi dong vao cac file trong vgt_patch.json.
# Cai: kiem tra file goc dung phien ban (sha256) -> sao luu vao _backup -> chep file dich -> kiem lai.
# Go:  tra file goc tu _backup, xoa file moi them -> kiem lai sha256 -> xoa _backup.
# hide (tuy chon): file goc phai cat vao _backup khi cai (vd WOLF .wolf khi patch la ban giai nen), tra lai khi go.
param(
    [Parameter(Mandatory = $true)][ValidateSet('install', 'uninstall')][string]$Mode,
    [string]$Game = '',
    [switch]$NoPrompt
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$m = Get-Content -LiteralPath (Join-Path $root 'vgt_patch.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$bk = Join-Path $root '_backup'
$hide = @()
if ($m.PSObject.Properties.Name -contains 'hide') { $hide = @($m.hide) }

function Get-Sha([string]$p) {
    if (Test-Path -LiteralPath $p -PathType Leaf) { return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower() }
    return $null
}
function Copy-To([string]$src, [string]$dst) {
    $d = Split-Path -Parent $dst
    if (-not (Test-Path -LiteralPath $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
    Copy-Item -LiteralPath $src -Destination $dst -Force
}
function Fail([string]$msg) { Write-Host "LOI: $msg" -ForegroundColor Red; exit 1 }

if (-not $Game) { $Game = $m.game_default }
$probe = $m.probe
if (-not $probe) { $probe = ($m.files | Where-Object { $_.orig } | Select-Object -First 1).path }
while (-not $probe -or -not (Test-Path -LiteralPath (Join-Path $Game $probe))) {
    if ($NoPrompt) { Fail "Khong thay game o: $Game" }
    Write-Host "Khong thay game o: $Game"
    $Game = (Read-Host 'Dan duong dan thu muc game (thu muc chua Game.exe)').Trim('"', ' ')
    if (-not $Game) { exit 1 }
}
Write-Host "Game: $Game"

if ($Mode -eq 'install') {
    if (Test-Path -LiteralPath $bk) { Write-Host 'Da cai Viet hoa roi (co _backup). Muon cai lai: chay GO_VIETHOA.bat truoc.'; exit 0 }
    $bad = @()
    foreach ($f in $m.files) {
        $cur = Get-Sha (Join-Path $Game $f.path)
        if ($cur -ne $f.orig -and $cur -ne $f.new) { $bad += $f.path }
    }
    foreach ($h in $hide) {
        if ((Get-Sha (Join-Path $Game $h.path)) -ne $h.orig) { $bad += $h.path }
    }
    if ($bad.Count) { Fail ("File goc khac phien ban patch, khong cai: " + ($bad[0..4] -join ', ')) }
    New-Item -ItemType Directory -Path $bk -Force | Out-Null
    foreach ($f in $m.files) {
        $g = Join-Path $Game $f.path
        if ($f.orig) { Copy-To $g (Join-Path $bk $f.path) }
    }
    foreach ($h in $hide) {
        $hb = Join-Path $bk $h.path
        Copy-To (Join-Path $Game $h.path) $hb
        if ((Get-Sha $hb) -ne $h.orig) { Fail "Sao luu loi: $($h.path)" }
        Remove-Item -LiteralPath (Join-Path $Game $h.path) -Force
    }
    foreach ($f in $m.files) { Copy-To (Join-Path (Join-Path $root 'files') $f.path) (Join-Path $Game $f.path) }
    foreach ($f in $m.files) {
        if ((Get-Sha (Join-Path $Game $f.path)) -ne $f.new) { Fail "Chep loi: $($f.path). Chay GO_VIETHOA.bat de tra lai." }
    }
    Write-Host "Da cai Viet hoa: $($m.files.Count) file. Ban goc luu o $bk" -ForegroundColor Green
}
else {
    if (-not (Test-Path -LiteralPath $bk)) { Write-Host 'Chua cai Viet hoa (khong co _backup).'; exit 0 }
    foreach ($f in $m.files) {
        $g = Join-Path $Game $f.path
        if ($f.orig) { Copy-To (Join-Path $bk $f.path) $g }
        elseif ((Get-Sha $g) -eq $f.new) { Remove-Item -LiteralPath $g -Force }
    }
    foreach ($h in $hide) { Copy-To (Join-Path $bk $h.path) (Join-Path $Game $h.path) }
    foreach ($f in $m.files) {
        if ((Get-Sha (Join-Path $Game $f.path)) -ne $f.orig) { Fail "Tra lai loi: $($f.path). Giu nguyen $bk, dung xoa." }
    }
    foreach ($h in $hide) {
        if ((Get-Sha (Join-Path $Game $h.path)) -ne $h.orig) { Fail "Tra lai loi: $($h.path). Giu nguyen $bk, dung xoa." }
    }
    # Xoa thu muc rong do patch tao (vd Data/BasicData khi game goc chi co .wolf)
    $dirs = $m.files | ForEach-Object { Split-Path -Parent (Join-Path $Game $_.path) } | Sort-Object -Unique -Descending
    foreach ($d in $dirs) {
        while ($d -and $d.Length -gt $Game.Length -and (Test-Path -LiteralPath $d) -and -not (Get-ChildItem -LiteralPath $d -Force | Select-Object -First 1)) {
            Remove-Item -LiteralPath $d -Force; $d = Split-Path -Parent $d
        }
    }
    Remove-Item -LiteralPath $bk -Recurse -Force
    Write-Host 'Da go Viet hoa, game ve nguyen ban.' -ForegroundColor Green
}
exit 0
