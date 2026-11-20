"""Chèn bước cài font 'VH Clannad SS' vào CAI_VIETHOA.bat do vgk patchkit tạo. Dùng: python3 them_font_bat.py patch/viethoa"""
import sys, os
p = os.path.join(sys.argv[1], 'CAI_VIETHOA.bat')
s = open(p, 'rb').read().decode('cp1252')
nl = '\r\n' if '\r\n' in s else '\n'
old = 'echo Go bo: chay GO_VIETHOA.bat' + nl
assert old in s and 'font_ok' not in s
add = old + nl.join([
    'rem Cai font chu Viet "VH Clannad SS" cho tai khoan nay (game chi dung font da cai)',
    'if exist "%LOCALAPPDATA%\\Microsoft\\Windows\\Fonts\\VHClannadSS.ttf" goto :font_ok',
    'powershell -NoProfile -ExecutionPolicy Bypass -Command "(New-Object -ComObject Shell.Application).Namespace(0x14).CopyHere(\'%GAME%\\VHClannadSS.ttf\', 0x14)" >>"%LOG%" 2>&1',
    ':font_ok',
    'echo Font chu Viet: VH Clannad SS. Neu chu hien sai: vao Setting ^> Font Settings, chon "VH Clannad SS", bam OK.',
    ''])
open(p, 'wb').write(s.replace(old, add, 1).encode('cp1252'))
print('đã chèn bước cài font')
