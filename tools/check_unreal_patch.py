"""Kiem offline pak mod Viet hoa Unreal (game Unreal chua co boot check: KHONG thay duoc choi thu).
Chay: python tools/check_unreal_patch.py projects/<game>
In DAT_OFFLINE khi: index pak hop le, moi culture du khoa nhu ban goc, khong con kana/kanji,
font thay phu het ky tu dung. Thoat 1 neu khong dat."""
import hashlib
import io
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vgt.adapters.unreal_locres import UnrealLocres  # noqa: E402
from vgt.pipeline import Project  # noqa: E402
from vgt.unreal.locres import Locres  # noqa: E402
from vgt.unreal.pak import PakReader, game_paks, pak_order  # noqa: E402


def main(proj: str) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = Project(Path(proj), log=lambda *a: None)
    rel = UnrealLocres.mod_pak(p.game, p.cfg)
    mod = p.patch_dir / "_viethoa" / "files" / rel
    raw = mod.read_bytes()
    _, _, ioff, isz = struct.unpack("<IIqq", raw[-221 + 17:-221 + 41])
    ok = hashlib.sha1(raw[ioff:ioff + isz]).digest() == raw[-221 + 41:-221 + 61]
    print(f"pak mod {mod} {len(raw)} byte, index sha1 {'dung' if ok else 'SAI'}")
    # E-unreal-002: mod phai co uu tien cao hon moi pak goc (khong de trong ~mods neu pak goc ten <Project>-).
    top = max((pak_order(p.game, x), x.name) for x in game_paks(p.game))
    mine = pak_order(p.game, rel)
    print(f"  uu tien pak mod {mine} vs pak goc cao nhat {top[0]} ({top[1]}): {'dung' if mine > top[0] else 'SAI'}")
    ok &= mine > top[0]
    # E-unreal-003: game IoStore (co .utoc) bo qua pak thieu .utoc/.ucas cung ten.
    if list(p.game.glob("*/Content/Paks/*.utoc")):
        has = all(mod.with_suffix(x).exists() for x in (".utoc", ".ucas"))
        print(f"  game IoStore: pak mod co .utoc/.ucas di kem: {'dung' if has else 'SAI (game se bo qua pak)'}")
        ok &= has
    r, gf = PakReader(mod), UnrealLocres._files(p.game, p.cfg)
    chars, cjk = set(), 0
    for f in sorted(x for x in r.files if x.endswith(".locres")):
        new, old = dict(Locres(r.read(f)).items()), dict(Locres(gf.read(f)).items())
        left = sum(1 for v in new.values() if any(0x3040 <= ord(c) <= 0x30FF or 0x4E00 <= ord(c) <= 0x9FFF for c in v))
        cjk += left
        ok &= set(new) == set(old)
        print(f"  {f.split('/')[-2]:<8} khoa {len(new)} (du: {set(new) == set(old)}) doi {sum(old[k] != new[k] for k in old)} con CJK {left}")
        for v in new.values():
            chars |= set(v)
    from fontTools.ttLib import TTFont
    for f in {hashlib.sha1(r.read(x)).hexdigest(): x for x in r.files if x.endswith(".ufont")}.values():
        cm = TTFont(io.BytesIO(r.read(f)[4:]), lazy=True).getBestCmap()
        miss = sorted(c for c in chars - set("\r\n\t") if ord(c) not in cm)
        print(f"  font {f.split('/')[-1]} (va cac ban trung): thieu {len(miss)} {''.join(miss[:30])}")
    print("DAT_OFFLINE" if ok and not cjk else "KHONG DAT_OFFLINE", "(chua phai choi thu trong game)")
    return 0 if ok and not cjk else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
