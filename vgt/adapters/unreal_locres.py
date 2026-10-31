"""Unreal Engine 4.26+/5 (pak v11, khong ma hoa): doc Game.locres trong pak, ghi pak mod.

Trich xuat: <Project>/Content/Localization/<target>/<source_culture>/<target>.locres (moi chuoi
mot dong; namespace = nhom canh). Ghi: mot pak mod MOI (Paks/<Project>-zVietHoa_999_P.pak) chua locres
tieng Viet cho moi culture game co + font thay the; khong ghi de file nao cua game.
"""
from __future__ import annotations

import re
import struct
from pathlib import Path

from ..store import Entry
from ..unreal.locres import Locres
from ..unreal.iostore import write_empty_container
from ..unreal.pak import GameFiles, Oodle, game_paks, write_pak

# namespace -> loai dong (khop dau tien). Ghi de bang unreal.kinds trong config.
KINDS = [
    (r"Choice", "choice"),
    (r"Name|NAME|Title$", "name"),
    (r"Description|Summary|Trait|Progress|Guide|Tips|Help", "description"),
    (r"(^|_)(UI|Option|Dialog|Common|Menu|System)(_|$)", "ui"),
]


def _ucfg(cfg: dict) -> dict:
    return (cfg or {}).get("unreal") or {}


def _project(game: Path) -> str:
    """Ten thu muc project UE (thu muc co Content/Paks), vd FFRS."""
    for p in sorted(Path(game).glob("*/Content/Paks")):
        if p.parent.parent.name != "Engine":
            return p.parent.parent.name
    raise SystemExit(f"Khong thay <Project>/Content/Paks trong {game}")


def _oodle(game: Path, cfg: dict) -> Oodle | None:
    dll = _ucfg(cfg).get("oodle_dll") or next(iter(sorted(Path(game).rglob("oo2core_*win64.dll"))), None)
    return Oodle(Path(dll)) if dll else None


def _kind(ns: str, text: str, cfg: dict) -> str:
    for rx, kind in [*((_ucfg(cfg).get("kinds") or {}).items()), *KINDS]:
        if re.search(rx, ns):
            return kind
    return "dialogue"


def _base_key(key: str, cfg: dict) -> str | None:
    for sfx in _ucfg(cfg).get("variant_suffixes") or []:
        if key.endswith(sfx):
            return key[: -len(sfx)]
    return None


class UnrealLocres:
    name = "unreal_locres"
    patchable = True  # apply -> patch them 1 pak mod (CAI/GO_VIETHOA), khong chep ca game

    @staticmethod
    def detect(game: Path) -> bool:
        return bool(game_paks(Path(game)))

    @staticmethod
    def mod_pak(game: Path, cfg: dict) -> str:
        # Paks/<Project>-zVietHoa_999_P.pak: uu tien 4000+100*1000, cao hon moi pak goc
        # (~mods chi 3000+, thua pak goc '<Project>-Windows.pak' = 4000 -> game van hien tieng Anh).
        proj = _project(game)
        return _ucfg(cfg).get("mod_pak") or f"{proj}/Content/Paks/{proj}-zVietHoa_999_P.pak"

    @classmethod
    def probe(cls, game: Path, cfg: dict) -> str:
        """File chac chan co trong game, de CAI/GO_VIETHOA nhan ra thu muc game."""
        return game_paks(Path(game))[0].relative_to(game).as_posix()

    @classmethod
    def _files(cls, game: Path, cfg: dict) -> GameFiles:
        return GameFiles(Path(game), _oodle(game, cfg), Path(game) / cls.mod_pak(game, cfg))

    @staticmethod
    def _loc_path(game: Path, cfg: dict, culture: str) -> str:
        t = _ucfg(cfg).get("target") or "Game"
        return f"{_project(game)}/Content/Localization/{t}/{culture}/{t}.locres"

    @classmethod
    def extract(cls, game: Path, cfg: dict | None = None) -> list[Entry]:
        cfg = cfg or {}
        gf = cls._files(game, cfg)
        try:
            loc = Locres(gf.read(cls._loc_path(game, cfg, _ucfg(cfg).get("source_culture") or "en")))
        finally:
            gf.close()
        keys = {k for k, _ in loc.items()}
        out, seq = [], {}
        for (ns, key), text in loc.items():
            base = _base_key(key, cfg)
            if not text.strip() or (base and (ns, base) in keys):
                continue  # bien the so it/nhieu (_sg/_pl...) dung chung ban dich cua khoa goc
            seq[ns] = seq.get(ns, 0) + 1
            src = text.replace("\r\n", "\n")
            out.append(Entry(id=f"{ns}/{key}", file=ns, locator={"ns": ns, "key": key, "crlf": "\r\n" in text},
                             grp=ns, seq=seq[ns], kind=_kind(ns, src, cfg), source=src))
        return out

    @classmethod
    def apply(cls, game: Path, out_dir: Path, entries: list[Entry], cfg: dict) -> list[Path]:
        u = _ucfg(cfg)
        vi = {}
        for e in entries:
            if e.target and e.status in ("done", "manual", "tm"):
                t = e.target.replace("\r\n", "\n")
                vi[(e.locator["ns"], e.locator["key"])] = t.replace("\n", "\r\n") if e.locator.get("crlf") else t
        if not vi and not u.get("fonts"):
            return []
        gf = cls._files(game, cfg)
        try:
            proj, t = _project(game), u.get("target") or "Game"
            prefix = f"{proj}/Content/Localization/{t}/"
            cultures = u.get("cultures") or sorted({p[len(prefix):].split("/")[0] for p in gf.where
                                                   if p.startswith(prefix) and p.endswith(".locres")})
            src = dict(Locres(gf.read(cls._loc_path(game, cfg, u.get("source_culture") or "en"))).items())

            def pick(k, text):
                base = _base_key(k[1], cfg)
                if k in vi:
                    return vi[k]
                if base and (k[0], base) in vi:
                    return vi[(k[0], base)]
                # Chua dich: dung ban nguon (tieng Anh) cho moi culture, khong de chu CJK (font da thay).
                return src.get(k, text) if text.strip() else None

            files: dict[str, bytes] = {}
            for c in cultures:
                rel = cls._loc_path(game, cfg, c)
                loc = Locres(gf.read(rel))
                loc.set_all(pick)
                files[rel] = loc.dump()
            for dst, repl in (u.get("fonts") or {}).items():
                if dst not in gf.where:
                    raise SystemExit(f"unreal.fonts: khong co {dst} trong pak cua game")
                if repl in gf.where:
                    files[dst] = gf.read(repl)
                else:  # .ttf/.otf ngoai: dong khung nhu .ufont (int32 do dai + du lieu + 4 byte 0)
                    data = Path(repl).read_bytes()
                    files[dst] = struct.pack("<I", len(data)) + data + b"\0" * 4
        finally:
            gf.close()
        pak = write_pak(Path(out_dir) / cls.mod_pak(game, cfg), files)
        # Game UE5 IoStore (co .utoc canh pak goc): pak thieu .utoc bi bo qua ("utoc not found").
        like = sorted(Path(game).glob(f"{_project(game)}/Content/Paks/*.utoc"))
        like = [x for x in like if x.name != "global.utoc"] or like
        return [pak] + (write_empty_container(pak, like[0]) if like else [])
