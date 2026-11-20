"""LinguaGacha lam "tay chan": doc/ghi file game (WOLF RPG truoc, cac engine LinguaGacha ho tro sau).

vgt chi dung bo doc/ghi cua LinguaGacha, KHONG dung model/bo dich cua no. Cau noi la
`vgt-bridge.mjs` (tools/lg_bridge, dung tu ma nguon LinguaGacha dung phien ban da tai):
  extract  <ban sao nho cua game> -> du an .lg (SQLite, bang items: src/dst/status/extra_field)
  generate <du an .lg>            -> thu muc ban dich (file game da ghi ban dich)

Khong bao gio dua thu muc game goc cho LinguaGacha: no sua thu muc game tai cho (giai nen .wolf,
xoa ban ma hoa). vgt chep vao `<du an>/lg/shadow` dung cac file chua chu (vai chuc MB), khong chep ca game.

WOLF: ban dich la Data/BasicData/*, Data/MapData/* dang giai nen -> patch phai cat cac file
.wolf tuong ung vao _backup khi cai (`hides`), neu khong game doc ban goc trong .wolf.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path

from ..config import REPO_ROOT
from ..store import Entry

VERSION = "0.132.1"
TEXT_STATUSES = {"NONE", "DUPLICATED"}  # LANGUAGE_SKIPPED/RULE_SKIPPED: chu noi bo, nhan, ma
WOLF_ARCHIVES = ("BasicData", "MapData")  # chua chu; anh/am thanh khong can
_CODE = re.compile(r"\\[a-zA-Z]+(\[[^\]]*\])?|\\.|<[A-Z_]+>")
_CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]")
_ASSET = re.compile(r"\.(png|jpe?g|bmp|ogg|wav|mp3|mid|txt|ttf|otf|webp)$", re.I)


def _lgcfg(cfg: dict) -> dict:
    c = dict(cfg.get("linguagacha") or {})
    tools = Path(c.get("tools_dir") or (REPO_ROOT.parent / "tools" / "LinguaGacha" / c.get("version", VERSION)))
    c["tools_dir"] = tools
    c.setdefault("node", "node")
    c.setdefault("source_language", "ALL")
    return c


def _workdir(cfg: dict) -> Path:
    p = cfg.get("_project_dir")
    if not p:
        raise SystemExit("linguagacha: thieu _project_dir (Pipeline phai truyen).")
    return Path(p) / "lg"


def _bridge(cfg: dict, *args: str) -> dict:
    c = _lgcfg(cfg)
    t = c["tools_dir"]
    bridge, builtin = t / "vgt-bridge.mjs", t / "app" / "resources" / "builtin"
    if not bridge.is_file() or not builtin.is_dir():
        raise SystemExit(f"linguagacha: thieu {bridge} hoac {builtin}. Xem tools/lg_bridge/README.md.")
    data = t / "bridge_data"
    data.mkdir(parents=True, exist_ok=True)
    if not (data / "version.txt").exists():
        (data / "version.txt").write_text(c.get("version", VERSION), "utf-8")
    try:
        v = subprocess.run([c["node"], "--version"], capture_output=True, text=True).stdout.strip().lstrip("v")
    except OSError:
        raise SystemExit("linguagacha: khong thay Node.js (can >= 22.5, https://nodejs.org).")
    if tuple(int(x) for x in v.split(".")[:2]) < (22, 5):
        raise SystemExit(f"linguagacha: Node.js {v} qua cu (can >= 22.5 vi dung node:sqlite).")
    cmd = [c["node"], "--no-warnings", str(bridge), *args,
           "--app-root", str(data), "--builtin", str(builtin)]
    logs = data / "log"
    sizes = {f: f.stat().st_size for f in logs.glob("*.jsonl")} if logs.is_dir() else {}
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    line = (r.stdout.strip().splitlines() or [""])[-1]
    if r.returncode != 0 or not line.startswith("{"):
        raise SystemExit(f"linguagacha bridge loi ({r.returncode}): {(r.stderr or r.stdout)[-1500:]}")
    # LinguaGacha bo qua IM LANG file khong doc duoc (chi ghi canh bao vao log) -> vgt chan lai (E-wolfrpg-002).
    bad = []
    for f in (logs.glob("*.jsonl") if logs.is_dir() else []):
        if f.name.endswith(".idx.jsonl"):
            continue
        with f.open(encoding="utf-8", errors="replace") as fh:
            fh.seek(sizes.get(f, 0))
            for ln in fh:
                try:
                    j = json.loads(ln)
                except ValueError:
                    continue
                if j.get("level") in ("warning", "error") and j.get("source") != "app":
                    bad.append(str(j.get("content", ""))[:200])
    if bad and not c.get("allow_warnings"):
        raise SystemExit(f"linguagacha: {len(bad)} canh bao khi {args[0]} (vd: {bad[:3]}). File game khong doc "
                         "duoc se bi bo sot. Xem docs/lessons/engines/wolfrpg.md E-wolfrpg-002; "
                         "chap nhan thi dat linguagacha.allow_warnings: true.")
    return json.loads(line)


def is_wolf(game: Path) -> bool:
    d = game / "Data"
    return any((d / f"{a}.wolf").is_file() or (d / a).is_dir() for a in WOLF_ARCHIVES) or (game / "Data.wolf").is_file()


def wolf_sources(game: Path) -> tuple[list[str], list[str]]:
    """(file can chep vao ban sao nho, file .wolf can cat di khi cai patch). Duong dan tuong doi."""
    copy, hide = [], []
    if (game / "Data.wolf").is_file():
        raise SystemExit("linguagacha: game dong goi 1 file Data.wolf (ca anh/am thanh) - chua ho tro, "
                         "can tach rieng file chu truoc.")
    for a in WOLF_ARCHIVES:
        arc = game / "Data" / f"{a}.wolf"
        if arc.is_file():
            copy.append(f"Data/{a}.wolf")
            hide.append(f"Data/{a}.wolf")
        folder = game / "Data" / a
        if folder.is_dir():
            copy += [p.relative_to(game).as_posix() for p in folder.rglob("*") if p.is_file()]
    return copy, hide


def _is_text(src: str, loc: dict) -> bool:
    plain = _CODE.sub("", src).strip()
    if not re.search(r"[^\W\d_]", plain):  # chi con ma/so
        return False
    if _ASSET.search(plain) or ("/" in plain and " " not in plain):
        return False
    if loc.get("code") == 122:  # bien chuoi: thoai that cua game nay, nhung cung chua ten BGM/nhan noi bo
        return " " in plain or bool(re.search(r"[.!?…─」』！？。]$", plain)) or bool(re.search(r"[^\x00-\x7f]", plain))
    return True


def _kind(src: str, loc: dict) -> str:
    code, k = loc.get("code"), loc.get("kind")
    if code == 102:
        return "choice"
    if code in (101, 122):
        return "dialogue"
    return "ui"


def _grp(file: str, loc: dict) -> tuple[str, int]:
    k = loc.get("kind")
    if k == "common_command":
        return f"CE{loc['event']}", loc["command"] * 10 + loc.get("string", 0)
    if k == "map_command":
        return f"{Path(file).stem}:ev{loc['event']}p{loc.get('page', 0)}", loc["command"] * 10 + loc.get("string", 0)
    if k == "database_string":
        return f"{Path(file).stem}:t{loc.get('type')}", loc.get("record", 0) * 100 + loc.get("string", 0)
    return Path(file).stem, 0


def item_id(file: str, loc: dict) -> str:
    return file + "|" + json.dumps(loc, sort_keys=True, separators=(",", ":"))


def read_items(lg: Path):
    con = sqlite3.connect(lg)
    try:
        for iid, data in con.execute("select id, data from items order by id"):
            yield iid, json.loads(data)
    finally:
        con.close()


class LinguaGacha:
    name = "linguagacha"
    patchable = True

    @staticmethod
    def detect(game: Path) -> bool:
        return Path(game).is_dir() and is_wolf(Path(game))

    @classmethod
    def build_project(cls, game: Path, cfg: dict) -> Path:
        """Ban sao nho -> du an .lg moi (LinguaGacha sua ban sao, khong dung toi game)."""
        work = _workdir(cfg)
        shadow, lg = work / "shadow" / "game", work / "project.lg"
        if shadow.parent.exists():
            shutil.rmtree(shadow.parent)
        for f in (lg, lg.with_suffix(".lg-wal"), lg.with_suffix(".lg-shm")):
            f.unlink(missing_ok=True)
        copy, hide = wolf_sources(game)
        for rel in copy:
            dst = shadow / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(game / rel, dst)
        lang = _lgcfg(cfg)["source_language"]
        r = _bridge(cfg, "extract", "--game", str(shadow), "--project", str(lg),
                    "--src-lang", lang, "--tgt-lang", "VI")
        shutil.rmtree(shadow.parent, ignore_errors=True)  # .lg da chua toan bo du lieu can thiet
        (work / "info.json").write_text(json.dumps({"version": _lgcfg(cfg).get("version", VERSION),
                                                    "copied": copy, "hide": hide, "bridge": r},
                                                   ensure_ascii=False, indent=1), "utf-8")
        return lg

    @classmethod
    def extract(cls, game: Path, cfg: dict | None = None) -> list[Entry]:
        cfg = cfg or {}
        lg = cls.build_project(Path(game), cfg)
        # Ban phat hanh tieng Anh/Latin: chu Nhat/Trung con sot la nhan noi bo, menu debug -> bo.
        drop_cjk = _lgcfg(cfg)["source_language"] not in ("ALL", "JA", "ZH", "ZH-HANT", "KO")
        out = []
        for _, it in read_items(lg):
            w = (it.get("extra_field") or {}).get("wolfrpg")
            if not w or w.get("usage") != "text" or it.get("status") not in TEXT_STATUSES:
                continue
            src, loc, f = it["src"], w["location"], w["internal_file_path"]
            if not _is_text(src, loc) or (drop_cjk and _CJK.search(src)):
                continue
            grp, seq = _grp(f, loc)
            out.append(Entry(id=item_id(f, loc), file=f, locator={"lg": loc}, grp=grp, seq=seq,
                             kind=_kind(src, loc), source=src, speaker=it.get("name_src") or None))
        return out

    @classmethod
    def hides(cls, game: Path, cfg: dict) -> list[str]:
        return wolf_sources(Path(game))[1]

    @classmethod
    def probe(cls, game: Path, cfg: dict) -> str | None:
        """File luon co trong game (ca truoc va sau khi cai) de script nhan ra thu muc game."""
        for n in ("Game.exe", "GamePro.exe", "Game.ini"):
            if (Path(game) / n).is_file():
                return n
        return None

    @classmethod
    def apply(cls, game: Path, out_dir: Path, entries: list[Entry], cfg: dict) -> list[Path]:
        work = _workdir(cfg)
        base = work / "project.lg"
        if not base.is_file():
            base = cls.build_project(Path(game), cfg)
        tmp = work / "apply"
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir(parents=True)
        lg = tmp / "project.lg"
        shutil.copy2(base, lg)
        want = {e.id: e.target for e in entries if e.target and e.status in ("done", "manual", "tm")}
        con = sqlite3.connect(lg)
        n = 0
        try:
            rows = list(con.execute("select id, data from items"))
            for iid, data in rows:
                it = json.loads(data)
                w = (it.get("extra_field") or {}).get("wolfrpg")
                if not w:
                    continue
                key = item_id(w["internal_file_path"], w["location"])
                if key in want:
                    it["dst"], it["status"] = want[key], "PROCESSED"
                    n += 1
                elif it.get("status") == "PROCESSED":  # khong de sot ban dich cu
                    it["dst"], it["status"] = "", "NONE"
                else:
                    continue
                con.execute("update items set data=? where id=?", (json.dumps(it, ensure_ascii=False), iid))
            con.commit()
        finally:
            con.close()
        missing = len(want) - n
        if missing:
            raise SystemExit(f"linguagacha: {missing} dong khong con trong du an LinguaGacha (game doi phien ban?). "
                             "Chay lai vgt extract.")
        gen = tmp / "out"
        _bridge(cfg, "generate", "--project", str(lg), "--out", str(gen))
        roots = [p for p in gen.iterdir() if p.is_dir() and p.name != "bilingual"]
        if len(roots) != 1:
            raise SystemExit(f"linguagacha: thu muc ban dich la: {[p.name for p in roots]}")
        written = []
        for p in sorted(roots[0].rglob("*")):
            if p.is_file():
                rel = p.relative_to(roots[0])
                dst = Path(out_dir) / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst)
                written.append(dst)
        shutil.rmtree(tmp, ignore_errors=True)
        return written
