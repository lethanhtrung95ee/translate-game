# Trich tep chu (ks/js/json/html/css/txt/tjs/md/csv) tu app.asar cua game HOME vao WORK\goc
$ErrorActionPreference = 'Stop'
$asar = 'C:\Users\letha\Downloads\[Hentai]\[Ryuugames] RY-RJ01556529_V0.0.5_EN\HOME\resources\app.asar'
$out  = 'C:\Games\Viet hoa game\home\goc'
$exts = @('.ks','.js','.json','.html','.htm','.css','.txt','.tjs','.md','.csv','.xml')
$fs = [System.IO.File]::OpenRead($asar)
$br = New-Object System.IO.BinaryReader($fs)
$null = $br.ReadUInt32(); $hsize = $br.ReadUInt32(); $null = $br.ReadUInt32(); $jlen = $br.ReadUInt32()
$json = [System.Text.Encoding]::UTF8.GetString($br.ReadBytes($jlen))
[System.IO.File]::WriteAllText("$out\..\asar_header.json", $json)
$base = 8 + $hsize
$hdr = $json | ConvertFrom-Json
$list = New-Object System.Collections.Generic.List[string]
function Walk($node, $prefix) {
  foreach ($p in $node.files.PSObject.Properties) {
    $rel = if ($prefix) { "$prefix/$($p.Name)" } else { $p.Name }
    $v = $p.Value
    if ($v.files) { Walk $v $rel; continue }
    if ($rel -like 'node_modules/*') { continue }
    $ext = [System.IO.Path]::GetExtension($rel).ToLower()
    if ($exts -notcontains $ext) { continue }
    $dst = Join-Path $out ($rel -replace '/', '\')
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($dst)) | Out-Null
    $fs.Position = $base + [int64]$v.offset
    [System.IO.File]::WriteAllBytes($dst, $br.ReadBytes([int]$v.size))
    $list.Add("$rel`t$($v.size)")
  }
}
New-Item -ItemType Directory -Force $out | Out-Null
Walk $hdr ''
$fs.Close()
[System.IO.File]::WriteAllLines("$out\..\trich_xong.txt", $list)
