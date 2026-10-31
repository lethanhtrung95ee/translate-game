"""Unreal .pak (phien ban 11, UE4.26+/UE5): doc (Oodle/khong nen) va ghi pak mod khong nen.

Chi doc pak khong ma hoa. Pak mod chi chua file khong phai package (.locres, .ufont...) nen
khong can .utoc/.ucas. Dinh dang theo FPakFile (footer 221 byte, index ma hoa bitfield,
path hash index FNV64 + full directory index, moi phan co SHA1).
"""
from __future__ import annotations

import ctypes
import hashlib
import io
import struct
from pathlib import Path

MAGIC = 0x5A6F12E1
VERSION = 11
FOOTER = 221
MOUNT = "../../../"


def _rstr(b: io.BytesIO) -> str:
    n, = struct.unpack("<i", b.read(4))
    if n == 0:
        return ""
    if n < 0:
        return b.read(-n * 2).decode("utf-16-le")[:-1]
    return b.read(n)[:-1].decode("latin-1")


def _wstr(s: str) -> bytes:
    if s.isascii():
        return struct.pack("<i", len(s) + 1) + s.encode("ascii") + b"\0"
    raw = s.encode("utf-16-le") + b"\0\0"
    return struct.pack("<i", -(len(raw) // 2)) + raw


class Oodle:
    """oo2core_*_win64.dll (Oodle) qua ctypes; game UE5 nen pak bang Oodle."""

    def __init__(self, dll: Path):
        self.lib = ctypes.WinDLL(str(dll))
        f = self.lib.OodleLZ_Decompress
        f.restype = ctypes.c_int64
        f.argtypes = ([ctypes.c_char_p, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int64]
                      + [ctypes.c_int] * 3 + [ctypes.c_void_p, ctypes.c_int64]
                      + [ctypes.c_void_p] * 3 + [ctypes.c_int64, ctypes.c_int])

    def decompress(self, src: bytes, size: int) -> bytes:
        dst = ctypes.create_string_buffer(size)
        r = self.lib.OodleLZ_Decompress(src, len(src), dst, size, 1, 0, 0, None, 0, None, None, None, 0, 3)
        if r != size:
            raise ValueError(f"Oodle giai nen loi ({r} != {size})")
        return dst.raw


class PakReader:
    def __init__(self, path: Path, oodle: Oodle | None = None):
        self.path, self.oodle = Path(path), oodle
        self.f = open(path, "rb")
        self.f.seek(-FOOTER, 2)
        ft = self.f.read(FOOTER)
        enc_index = ft[16]
        magic, ver, ioff, isz = struct.unpack("<IIqq", ft[17:41])
        if magic != MAGIC or ver < 10:
            raise ValueError(f"{path.name}: khong phai pak v10+ (magic={magic:x}, ver={ver})")
        if enc_index:
            raise ValueError(f"{path.name}: index pak bi ma hoa (can AES key), khong ho tro")
        self.comp = [ft[61 + i * 32:93 + i * 32].rstrip(b"\0").decode() for i in range(5)]
        self.f.seek(ioff)
        b = io.BytesIO(self.f.read(isz))
        self.mount = _rstr(b)
        b.read(4 + 8)  # so entry, path hash seed
        if struct.unpack("<I", b.read(4))[0]:
            b.read(8 + 8 + 20)
        if not struct.unpack("<I", b.read(4))[0]:
            raise ValueError(f"{path.name}: pak khong co full directory index")
        fdo, fds = struct.unpack("<qq", b.read(16))
        b.read(20)
        self.enc = b.read(struct.unpack("<i", b.read(4))[0])
        self.f.seek(fdo)
        d = io.BytesIO(self.f.read(fds))
        prefix = self.mount.replace(MOUNT, "", 1) if self.mount.startswith(MOUNT) else self.mount
        self.files: dict[str, int] = {}
        for _ in range(struct.unpack("<i", d.read(4))[0]):
            dn = _rstr(d).lstrip("/")
            for _ in range(struct.unpack("<i", d.read(4))[0]):
                fn = _rstr(d)
                off, = struct.unpack("<i", d.read(4))
                self.files[(prefix + dn + fn).replace("//", "/")] = off

    def close(self):
        self.f.close()

    def _entry(self, eo: int):
        enc = self.enc
        v, = struct.unpack_from("<I", enc, eo)
        p = eo + 4
        if (v & 0x3F) == 0x3F:
            cbs, = struct.unpack_from("<I", enc, p)
            p += 4
        else:
            cbs = (v & 0x3F) << 11
        nb, comp, encr = (v >> 6) & 0xFFFF, (v >> 23) & 0x3F, (v >> 22) & 1
        vals = []
        for bit in (31, 30, 29)[:3 if comp else 2]:
            if (v >> bit) & 1:
                vals.append(struct.unpack_from("<I", enc, p)[0]); p += 4
            else:
                vals.append(struct.unpack_from("<Q", enc, p)[0]); p += 8
        off, usize = vals[0], vals[1]
        csize = vals[2] if comp else usize
        sizes = []
        if comp and nb > 1:
            sizes = list(struct.unpack_from(f"<{nb}I", enc, p))
        elif comp and nb == 1:
            sizes = [csize]
        return off, usize, csize, comp, encr, cbs or usize, sizes

    def read(self, rel: str) -> bytes:
        off, usize, csize, comp, encr, cbs, sizes = self._entry(self.files[rel])
        if encr:
            raise ValueError(f"{rel}: file bi ma hoa")
        if not comp:
            self.f.seek(off + 53)
            return self.f.read(usize)
        if self.comp[comp - 1] != "Oodle":
            raise ValueError(f"{rel}: chua ho tro nen {self.comp[comp - 1]}")
        if not self.oodle:
            raise ValueError("Pak nen Oodle: dat unreal.oodle_dll trong config.yaml (oo2core_*_win64.dll)")
        cur = off + 8 * 3 + 4 + 20 + 4 + 16 * len(sizes) + 1 + 4
        out = bytearray()
        for i, n in enumerate(sizes):
            self.f.seek(cur)
            out += self.oodle.decompress(self.f.read(n), min(cbs, usize - i * cbs))
            cur += n
        return bytes(out)


def path_hash(rel: str, seed: int) -> int:
    """FPakFile::HashPath: FNV64 tren UTF-16 chu thuong, offset basis + seed."""
    h = (0xCBF29CE484222325 + seed) & 0xFFFFFFFFFFFFFFFF
    for byte in rel.lower().encode("utf-16-le"):
        h = ((h ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def write_pak(dst: Path, files: dict[str, bytes], mount: str = MOUNT, seed: int = 0) -> Path:
    """Ghi pak v11 khong nen. files: duong dan tuong doi mount (vd FFRS/Content/...) -> noi dung."""
    out = bytearray()
    enc = bytearray()
    loc: dict[str, int] = {}
    stored: dict[bytes, int] = {}  # file trung noi dung (vd 1 font thay cho 20 font) dung chung du lieu
    for rel in sorted(files):
        data = files[rel]
        sha = hashlib.sha1(data).digest()
        off = stored.get(sha)
        if off is None:
            off = stored[sha] = len(out)
            out += struct.pack("<QQQI", 0, len(data), len(data), 0) + sha + b"\0" + struct.pack("<I", 0)
            out += data
        loc[rel] = len(enc)
        flags = ((off < 1 << 32) << 31) | ((len(data) < 1 << 32) << 30) | ((len(data) < 1 << 32) << 29)
        enc += struct.pack("<I", flags)
        enc += struct.pack("<I" if off < 1 << 32 else "<Q", off)
        enc += struct.pack("<I" if len(data) < 1 << 32 else "<Q", len(data))
    # Full directory index: thu muc (co ca thu muc cha) -> {ten file: vi tri entry}.
    dirs: dict[str, dict[str, int]] = {"/": {}}
    for rel, o in loc.items():
        parts = rel.split("/")
        for i in range(1, len(parts)):
            dirs.setdefault("/".join(parts[:i]) + "/", {})
        dirs["/".join(parts[:-1]) + "/" if len(parts) > 1 else "/"][parts[-1]] = o
    fdi = struct.pack("<i", len(dirs))
    for d in sorted(dirs):
        fdi += _wstr(d) + struct.pack("<i", len(dirs[d]))
        for fn in sorted(dirs[d]):
            fdi += _wstr(fn) + struct.pack("<i", dirs[d][fn])
    # Path hash index: TMap<uint64,int32> + pruned directory index. Game shipping chi dung ban
    # pruned de duyet thu muc (tim *.locres theo culture) -> pruned = day du, khong de rong.
    phi = struct.pack("<I", len(loc)) + b"".join(
        struct.pack("<Qi", path_hash(r, seed), o) for r, o in sorted(loc.items())) + fdi
    phi_off = len(out)
    fdi_off = phi_off + len(phi)
    idx_off = fdi_off + len(fdi)
    idx = _wstr(mount) + struct.pack("<iQ", len(files), seed)
    idx += struct.pack("<I", 1) + struct.pack("<qq", phi_off, len(phi)) + hashlib.sha1(phi).digest()
    idx += struct.pack("<I", 1) + struct.pack("<qq", fdi_off, len(fdi)) + hashlib.sha1(fdi).digest()
    idx += struct.pack("<i", len(enc)) + bytes(enc) + struct.pack("<i", 0)
    footer = (b"\0" * 16 + b"\0" + struct.pack("<IIqq", MAGIC, VERSION, idx_off, len(idx))
              + hashlib.sha1(idx).digest() + b"\0" * 160)
    assert len(footer) == FOOTER
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(bytes(out) + phi + fdi + idx + footer)
    return dst


def pak_order(game: Path, pak: Path | str) -> int:
    """Thu tu uu tien UE gan cho pak (FPakPlatformFile::GetPakOrderFromPakFilePath + _P).
    Cao hon = file trong pak do de len. Pak trong Paks/ ten bat dau '<Project>-' duoc 4000,
    pak khac trong <Project>/Content (ca ~mods) chi 3000 -> mod trong ~mods KHONG de duoc pak goc
    ten '<Project>-Windows.pak'. Hau to _N_P cong 100*(N+1), _P tron cong 100."""
    rel = (Path(game) / pak).relative_to(Path(game)).as_posix() if not Path(pak).is_absolute()         else Path(pak).relative_to(Path(game)).as_posix()
    proj = rel.split("/")[0]
    if rel.startswith(f"{proj}/Content/Paks/{proj}-") and proj != "Engine":
        order = 4000
    elif rel.startswith(f"{proj}/Content/") and proj != "Engine":
        order = 3000
    elif rel.startswith("Engine/Content/"):
        order = 2000
    else:
        order = 0
    stem = Path(rel).stem
    if stem.endswith("_P"):
        head, _, ver = stem[:-2].rpartition("_")
        order += 100 * (int(ver) + 1 if head and ver.isdigit() else 1)
    return order


def game_paks(game: Path, exclude: Path | None = None) -> list[Path]:
    """Pak cua game theo thu tu uu tien tang dan (pak sau de pak truoc). Bo qua pak mod cua vgt."""
    paks = [p for p in Path(game).glob("*/Content/Paks/**/*.pak")
            if "zviethoa" not in p.name.lower()
            and not (exclude and p.resolve() == Path(exclude).resolve())]
    return sorted(paks, key=lambda p: (pak_order(game, p), p.as_posix().lower()))


class GameFiles:
    """Doc file trong cac pak cua game (ban co uu tien cao nhat)."""

    def __init__(self, game: Path, oodle: Oodle | None, exclude: Path | None = None):
        self.where: dict[str, PakReader] = {}
        self.readers = []
        for p in game_paks(game, exclude):
            r = PakReader(p, oodle)
            self.readers.append(r)
            for rel in r.files:
                self.where[rel] = r

    def read(self, rel: str) -> bytes:
        return self.where[rel].read(rel)

    def close(self):
        for r in self.readers:
            r.close()
