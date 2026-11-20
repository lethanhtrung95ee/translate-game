#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VGK - bo cong cu loi Viet hoa game, dung chung cho moi engine.

Chi dung thu vien chuan Python 3.8+. Chay trong thu muc lam viec cua game (WORK)
hoac chi dinh bang -w WORK. Xem lenh: python3 vgk.py -h

Du lieu trong WORK:
  game.json      cau hinh game
  src.jsonl      van ban goc do adapter trich (moi dong 1 JSON:
                 id, src, en?, speaker?, scene?, file?, kind?, maxlen?, note?)
  plan.json      phan loai + chia lo (tu tao lai khi src.jsonl doi)
  tr.jsonl       ban dich, chi ghi them; moi dong mang ma bam cua cau goc (phat hien goc doi)
  glossary.tsv   thuat ngu: src, vi, type, note, forbid, lo_tu (bi mat: chi duoc hien tu moc nay)
  xungho.tsv     xung ho theo moc: speaker, listener, tu_canh, xung, goi, note   (speaker = ten goc nhu trong src.jsonl)
  scenes.tsv     chi dao canh: scene, summary, priority
  giong.tsv      ho so nhan vat theo moc: speaker, tu_canh, gioi, vai_ve, tam_ly, giong, mau   ("_ke" = loi dan)
  sotay.md       so tay giong (van phong, muc 18+, cau mau hay, dieu tranh)
  phieu.tsv      phieu bao cua nguoi dich cho phien chinh
  neo.tsv        cau neo da duyet: speaker, vi, nguon (P5/F3/mau) -> in trong khoi NEO
  minor_ids.txt  id giu nguyen ban goc (noi dung vi thanh nien), chi dung id do
  glossary_skip.txt, coverage_skip.txt   ung vien ten / tep da quyet dinh bo qua (kem ly do)
  HANDOFF.md, notes.md, log.md, state.json, reports/, backup/, tools/, patch/, bible_snap/
Moc (tu_canh, lo_tu) = ma canh hoac id cau: dong co moc chi ap tu cho do tro di; next chi in dieu nguoi doc da biet.
Bible chung (quy-tac-dich.md, nguon-<lang>.md, the-loai-<tl>.md) tim o <thu muc vgk>/hoso/ hoac ../references/.
Khau vi chung o <thu muc vgk>/khauvi/ (KHAU_VI.md, mau.tsv, cam_mau.tsv, hieu_chuan.tsv).
Khong bao gio xoa tep (thu muc may co the chan quyen xoa).
"""

VERSION = "2.5.0"
PLAN_VERSION = 2

import argparse
import collections
import csv
import datetime
import fnmatch
import hashlib
import io
import json
import math
import os
import random
import re
import shutil
import time
import sys
import unicodedata

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORK = "."

F_GAME = "game.json"
F_SRC = "src.jsonl"
F_PLAN = "plan.json"
F_TR = "tr.jsonl"
F_GLOSS = "glossary.tsv"
F_PAIR = "xungho.tsv"
F_SCENE = "scenes.tsv"
F_VOICE = "giong.tsv"
F_MINOR = "minor_ids.txt"
F_NOTES = "notes.md"
F_HANDOFF = "HANDOFF.md"
F_LOG = "log.md"
F_STATE = "state.json"
F_NEO = "neo.tsv"
F_GSKIP = "glossary_skip.txt"
F_CSKIP = "coverage_skip.txt"
F_EXPMETA = "export_meta.json"
F_PHIEU = "phieu.tsv"
F_SOTAY = "sotay.md"
SNAP_DIR = "bible_snap"
DIRS = ["tools", "reports", "backup", "patch"]

GLOSS_COLS = ["src", "vi", "type", "note", "forbid", "lo_tu"]
PAIR_COLS = ["speaker", "listener", "tu_canh", "xung", "goi", "note"]
SCENE_COLS = ["scene", "summary", "priority", "loai"]
VOICE_COLS = ["speaker", "tu_canh", "gioi", "vai_ve", "tam_ly", "giong", "mau"]
PHIEU_COLS = ["n", "time", "lo", "id", "noi_dung", "trang_thai", "tra_loi"]
NEO_COLS = ["speaker", "vi", "nguon"]
CAM_COLS = ["regex", "goi_y", "pham_vi"]
HC_COLS = ["pair_id", "ngu_canh", "a", "b", "chon", "can", "nguon"]
KINDS = ("dialogue", "ui", "data", "system")
SCENE_LOAI = ("chien_dau", "hai", "18", "tinh_cam", "tuyen_moi", "khac")
THE_LOAI = ("vn", "rpg", "hanh_dong", "khac")
BOI_CANH = ("co_trang", "fantasy", "hien_dai", "khac")
EN_MODES = ("all", "on_demand", "none")
LANG_TYPOS = {"jp": "ja", "jpn": "ja", "cn": "zh", "chs": "zh", "cht": "zh", "kr": "ko", "kor": "ko", "eng": "en"}
# Nguong ty le do dai Viet/goc (ky tu, da bo ma) truoc khi game du 500 cau de tu tinh bach phan vi 95.
LEN_RATIO_DEFAULT = {"ja": 4.5, "zh": 5.5, "ko": 3.0, "en": 1.8}
LEN_RATIO_MEAN = {"ja": 2.6, "zh": 3.2, "ko": 1.9, "en": 1.25}
NEO_MAX = 1000

DEFAULT_CFG = {
    "vgk_version": VERSION,
    "name": "",
    "slug": "",
    "engine": "",
    "kind": "thuong",
    "source_lang": "ja",
    "the_loai": "",
    "boi_canh": "",
    "en_mode": "",
    "linebreaks": "free",
    "batch_dialogue": 80,
    "batch_short": 350,
    "code_patterns": [],
    "skip_patterns": [],
    "allow_chars": "",
    "max_len": {},
    "fit_auto": [],
    "name_types": ["nhan_vat", "dia_danh", "to_chuc", "ten"],
    "term_check_types": ["vat_pham", "ky_nang", "trang_thai"],
    "minor_fallback": "en",
    "require_scene_summary": None,
    "require_emotion": None,
    "hoso_dir": "",
    "cps_max": None,
    "ngan_sach_token": None,
    "gop_ok": False,
    "qa_dinh_ky": False,
    "doc_chuong_dau": 1500,
    "doc_chuong_sau": 5000,
    "phieu_toi_da": 15,
}

# Ma dieu khien / the / bien. Mau rieng cua game (game.json: code_patterns) duoc xet truoc.
DEFAULT_CODE_PATTERNS = [
    r"\\[A-Za-z]+\[[^\]\n]*\]",                          # RPG Maker/WOLF: \C[3] \N[1] \I[64]
    r"\\[A-Za-z]+<",                                     # mo hop ten \n<Ten> (YEP): ten ben trong van dich
    r"\\[A-Za-z]+",                                      # \G \E ...
    r"\\[{}|.!<>^$]",                                    # RPG Maker: \{ \} \| \. \! \> \< \^ \$
    r"</?[A-Za-z][A-Za-z0-9_-]*(?:[=\s][^<>\n]*)?>",     # the: <color=#fff> </b> <br> <sprite=3>
    r"</>",                                              # Unreal rich text: dong the
    r"\{[A-Za-z0-9_.:#=/+\-\[\]]*\}",                    # {0} {name} {b} {/b} {color=#f00}
    r"%(?:\d+\$)?[-+#0]*\d*(?:\.\d+)?[sdifuxXoceEgG]",   # printf: %s %d %1$s %.2f
    r"%\d+",                                             # RPG Maker: %1 %2
    r"%%",
]
NAMEBOX_OPEN = re.compile(r"\\[A-Za-z]+<")
NAMEBOX_FULL = re.compile(r"\\[A-Za-z]+<[^>\n]*>")
CJK_RE = re.compile(
    "[\u3000-\u303f\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
    "\uff01-\uff60\uff61-\uff9f\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]"
)
KATA_ONLY_RE = re.compile("^[\u30a0-\u30ff]+$")
LETTER_RE = re.compile(r"[^\W\d_]")
ALIAS_RE = re.compile(r"^~(\d+)\.(\d+)$")
PUNCT_MAP = {
    "！": "!", "？": "?", "、": ",", "。": ".", "，": ",", "：": ":", "；": ";",
    "（": "(", "）": ")", "「": "“", "」": "”", "『": "“", "』": "”", "～": "~",
    "〜": "~", "・": "·", "　": " ", "－": "-", "―": "—", "【": "[", "】": "]",
    "〈": "<", "〉": ">", "《": "«", "》": "»", "＆": "&", "＋": "+", "＝": "=",
    "％": "%", "＃": "#", "＊": "*", "／": "/", "．": ".",
}
SELF_RE = re.compile(r"(?<!\w)(tôi|ta|tao|tớ|tui)(?!\w)", re.I)
SELF_EXCL_RE = re.compile(r"(?<!\w)(?:người|chúng|anh|chị|cô|cậu|hắn|ông|bà|lão|mụ|gã)\s+ta(?!\w)", re.I)
# mày/tao: loai tu ghep khong phai xung ho
MAYTAO_EXCL_RE = re.compile(
    r"(?<!\w)(?:lông|chân|cau|nhíu|chau|nhướn|nhướng|rướn|đôi|cặp|hàng|ăn|mặt)\s+mày(?!\w)"
    r"|(?<!\w)mày\s+(?:mò|râu|đay)(?!\w)|(?<!\w)nở\s+mày(?!\w)"
    r"|(?<!\w)tao\s+(?:nhã|ngộ|khang|đàn|loạn)(?!\w)|(?<!\w)(?:phong|tiêu)\s+tao(?!\w)", re.I)
MAYTAO_RE = re.compile(r"(?<!\w)(mày|tao)(?!\w)", re.I)
CAUCO_EXCL_RE = re.compile(
    r"(?<!\w)cô\s+(?:ấy|ta|gái|bé|nàng|đơn|độc|lập|đọng|nhi|hồn|đặc|quạnh|liêu|giáo|dâu|út)(?!\w)"
    r"|(?<!\w)cậu\s+(?:ấy|ta|bé|chàng|nhóc|út|mợ|ruột)(?!\w)", re.I)
CAUCO_RE = re.compile(r"(?<!\w)(cậu|cô)(?!\w)", re.I)
TOI_RE = re.compile(r"(?<!\w)tôi(?!\w)", re.I)
# Xung chi cua mot gioi: doi chieu cot xung cua bang xung ho voi gioi trong ho so nhan vat (dung moc).
XUNG_NAM = {"anh", "huynh", "đệ", "ông", "chú", "bố", "cha", "cậu", "chàng", "lão phu", "công tử", "bổn công tử",
            "bản công tử", "tiểu sinh", "bần tăng", "lão nạp", "nô tài"}
XUNG_NU = {"chị", "tỷ", "tỉ", "muội", "bà", "cô", "dì", "mẹ", "má", "thiếp", "tiện thiếp", "nàng", "cô nương",
           "bổn cô nương", "bản cô nương", "nô gia", "nô tỳ", "bần ni", "lão thân", "ai gia"}
# Trong cau thoai: chi cac cum gan nhu chi dung de tu xung (it nham voi ngoi khac).
TU_XUNG_NAM_RE = re.compile(r"(?<!\w)(lão phu|bổn công tử|bản công tử|tiểu sinh|bần tăng|lão nạp)(?!\w)(?!\s+nhân)", re.I)
TU_XUNG_NU_RE = re.compile(r"(?<!\w)(?<!ngủ )(?<!mê )(?<!tiểu )(?<!thê )(?<!ái )(?<!nạp )"
                           r"(tiện thiếp|thiếp|bổn cô nương|bản cô nương|nô gia|bần ni|lão thân|ai gia)(?!\w)"
                           r"(?!\s+(?:đi|mời|vàng))", re.I)
EN_STOP = {"the", "and", "of", "is", "you", "it", "that", "for", "with", "this", "are", "was", "my", "your", "we",
           "what", "not", "have", "just", "but", "if", "or", "at", "from", "be", "will", "yeah", "okay", "hey",
           "please", "sorry", "thank", "thanks", "don't", "i'm", "it's", "let's", "can't", "won't", "they", "he",
           "she", "his", "her", "there", "here", "would", "could", "should"}
JP_DASH = "\u2e3a\u2e3b\u2015"   # ⸺ ⸻ ― (gach kieu Nhat)
ELL_RUN_RE = re.compile("\u2026{2,}")
END_PUNCT = set(".!?…:;—–-~)]}»*♪♥♡☆★")
TRAIL_CLOSE = "\"”’'」』】）) \t"
CONT_SRC = set("、，,")
# Duoi cau hoi cua ban goc: chi dung khi EN la cau hoi ma ban goc khong co dau hoi (EN hay tu ban dia hoa)
Q_TAIL = {"ja": ("か", "かな", "かい", "かしら", "の", "のか", "でしょ", "でしょう", "だろ", "だろう", "っけ", "じゃない",
                 "じゃん", "じゃ", "ない", "よね"),
          "zh": ("吗", "呢", "吧", "么", "嘛"), "ko": ("까", "니", "냐", "나요", "죠", "지", "가요")}
Q_STRIP = " \t\n…‥。、！!〜~ー」』）)】・.,\"”’'"
ASCII_RUN_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*(?:[ \t]+[A-Za-z][A-Za-z'’-]*){2,}")
ICU_HEAD_RE = re.compile(r"\{\s*([A-Za-z_][\w.]*)\s*,\s*(plural|select|selectordinal)\s*,", re.I)
UE_MOD_RE = re.compile(r"\|(plural|gender|ordinal|hpp)\(", re.I)
GOP_BODY = "=gộp"


# ---------------------------------------------------------------- tien ich

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def stamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def die(msg, code=1):
    print("LỖI: " + msg)
    sys.exit(code)


def p(name):
    return os.path.join(WORK, name)


def uniq(seq):
    out, seen = [], set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def fmt_n(n):
    return f"{n:,}".replace(",", ".")


def fmt_pct(a, b):
    if not b:
        return "0%"
    return f"{100.0 * a / b:.1f}".replace(".", ",") + "%"


def fmt_cnt(c):
    return [k if v == 1 else f"{k}×{v}" for k, v in c.items()]


def one_line(t):
    return (t or "").replace("\r", "").replace("\n", " ⏎ ")


def split_list(s, sep=";"):
    return [x.strip() for x in (s or "").split(sep) if x.strip()]


def normalize_punct(t):
    return "".join(PUNCT_MAP.get(ch, ch) for ch in t)


def norm_auto(t):
    """Muc tu dong (khong co chu) cua nguon CJK: doi dau, gach keo dai thanh '…', '……' thanh '…'."""
    t = normalize_punct(t).replace("\u2e3a", "—").replace("\u2e3b", "—")
    t = re.sub("—{2,}", "…", t)
    return re.sub("\u2026{2,}", "\u2026", t)


def src_hash(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


def slugify(name):
    t = name.replace("đ", "d").replace("Đ", "D")
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return t or "game"


def atomic_write(path, text, newline="\n"):
    """Ghi qua tep tam roi thay the (khong can quyen xoa)."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline=newline) as f:
        f.write(text)
    try:
        os.replace(tmp, path)
    except OSError:
        with open(path, "w", encoding="utf-8", newline=newline) as f:
            f.write(text)
        try:
            open(tmp, "w").close()
        except OSError:
            pass


def append_text(path, text):
    need_nl = False
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "rb") as f:
            f.seek(-1, 2)
            need_nl = f.read(1) != b"\n"
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(("\n" if need_nl else "") + text)


def file_sha(path, full=False):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    d = h.hexdigest()
    return d if full else d[:16]


def read_jsonl(path):
    items, bad = [], 0
    if not os.path.exists(path):
        return items, bad
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                bad += 1
    return items, bad


def clean_cell(v):
    return str(v if v is not None else "").replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()


def read_tsv(path, cols):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().split("\n")
    if not lines or not lines[0].strip():
        return rows
    header = [h.strip() for h in lines[0].rstrip("\r").split("\t")]
    idx = {h: i for i, h in enumerate(header)}
    for ln, line in enumerate(lines[1:], start=2):
        line = line.rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        row = {c: (parts[idx[c]].strip() if c in idx and idx[c] < len(parts) else "") for c in cols}
        row["_line"] = ln
        rows.append(row)
    return rows


def write_tsv(path, cols, rows):
    out = ["\t".join(cols)]
    for r in rows:
        out.append("\t".join(clean_cell(r.get(c, "")) for c in cols))
    atomic_write(path, "\n".join(out) + "\n")


def word_re(term, ci=None):
    if ci is None:
        ci = term == term.lower()
    return re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.I if ci else 0)


def word_in(term, text, ci=None):
    return bool(term) and word_re(term, ci).search(text) is not None


def term_pattern(s):
    if KATA_ONLY_RE.match(s):
        return "(?<![\u30a0-\u30ff])" + re.escape(s) + "(?![\u30a0-\u30ff])"
    if CJK_RE.search(s):
        return re.escape(s)
    return r"(?<!\w)" + re.escape(s) + r"(?!\w)"


def build_term_re(rows):
    """Mot regex cho moi thuat ngu, dai truoc ngan: tai moi vi tri chi thuat ngu dai nhat khop."""
    rows = [r for r in rows if r.get("src")]
    if not rows:
        return None, {}
    parts, mp = [], {}
    for r in sorted(rows, key=lambda r: -len(r["src"])):
        k = r["src"].lower()
        if k in mp:
            continue
        mp[k] = r
        parts.append(term_pattern(r["src"]))
    return re.compile("|".join(parts), re.I), mp


def term_hits(rx, mp, text):
    """Counter: khoa thuat ngu -> so lan khop (theo thuat ngu dai nhat)."""
    c = collections.Counter()
    if rx is None or not text:
        return c
    for m in rx.finditer(text):
        k = m.group(0).lower()
        if k in mp:
            c[k] += 1
    return c


def find_terms(rx, mp, text):
    return [mp[k] for k in term_hits(rx, mp, text)]


STDIN_CACHE = None


def read_input(path):
    global STDIN_CACHE
    if path == "-":
        if STDIN_CACHE is None:
            STDIN_CACHE = sys.stdin.buffer.read()
        data = STDIN_CACHE
    else:
        with open(path, "rb") as f:
            data = f.read()
    return data.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


# ---------------------------------------------------------------- nap du lieu

def load_cfg():
    path = p(F_GAME)
    if not os.path.exists(path):
        die("Chưa có game.json — chạy: vgk.py init")
    try:
        with open(path, encoding="utf-8-sig") as f:
            user = json.load(f)
    except Exception as ex:
        die(f"game.json hỏng: {ex}")
    cfg = dict(DEFAULT_CFG)
    cfg.update(user)
    if cfg["linebreaks"] not in ("free", "keep"):
        die("game.json: linebreaks phải là 'free' hoặc 'keep'")
    lang = str(cfg.get("source_lang") or "").lower()
    if lang in LANG_TYPOS:
        die(f"game.json: source_lang '{lang}' → dùng '{LANG_TYPOS[lang]}'")
    cfg["source_lang"] = lang or "ja"
    if cfg["kind"] not in ("thuong", "18"):
        die("game.json: kind phải là 'thuong' hoặc '18'")
    for key, allowed in (("the_loai", THE_LOAI), ("boi_canh", BOI_CANH)):
        if cfg.get(key) and cfg[key] not in allowed:
            die(f"game.json: {key} '{cfg[key]}' không hợp lệ (dùng: {', '.join(allowed)})")
    if not cfg.get("en_mode"):
        cfg["en_mode"] = "none" if cfg["source_lang"] == "en" else "on_demand"
    elif cfg["en_mode"] not in EN_MODES:
        die(f"game.json: en_mode phải là {' | '.join(EN_MODES)}")
    if cfg.get("require_scene_summary") is None:
        # WORK cu (chua co the_loai) giu hanh vi 1.x: bat nhac tom tat canh.
        cfg["require_scene_summary"] = (not cfg.get("the_loai")) or cfg["the_loai"] in ("vn", "rpg")
    if cfg.get("require_emotion") is None:
        cfg["require_emotion"] = cfg.get("the_loai") == "vn"
    return cfg


def vgk_dir():
    return os.path.dirname(os.path.abspath(__file__))


def load_root_cfg():
    """config.json canh vgk.py (ROOT/_chung): bang_tien_do, chuan_tham_chieu, ngan_sach_token, root_win…"""
    path = os.path.join(vgk_dir(), "config.json")
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def khauvi_dirs():
    """Khau vi chung: <vgk>/khauvi (ROOT/_chung/khauvi), roi hat giong trong goi skill."""
    out = []
    for d in (os.path.join(vgk_dir(), "khauvi"), os.path.join(vgk_dir(), "..", "references", "khauvi-seed")):
        d = os.path.normpath(d)
        if os.path.isdir(d) and d not in out:
            out.append(d)
    return out


def build_code_re(cfg):
    pats = list(cfg.get("code_patterns") or []) + DEFAULT_CODE_PATTERNS
    for x in pats:
        try:
            re.compile(x)
        except re.error as ex:
            die(f"code_patterns '{x}' sai: {ex}")
    return re.compile("|".join("(?:%s)" % x for x in pats))


def load_src():
    path = p(F_SRC)
    if not os.path.exists(path):
        die("Chưa có src.jsonl — adapter phải trích văn bản ra tệp này trước.")
    items, bad = read_jsonl(path)
    if bad:
        die(f"src.jsonl có {bad} dòng JSON hỏng.")
    src, problems = collections.OrderedDict(), []
    for n, e in enumerate(items, 1):
        if not isinstance(e, dict) or "id" not in e or "src" not in e:
            problems.append(f"dòng {n}: thiếu id hoặc src")
            continue
        eid = str(e["id"])
        if not eid or re.search(r"\s", eid) or "·" in eid or eid.startswith("~"):
            problems.append(f"dòng {n}: id '{eid}' rỗng, chứa khoảng trắng/·, hoặc bắt đầu bằng ~")
            continue
        if eid in src:
            problems.append(f"dòng {n}: id trùng '{eid}'")
            continue
        e["id"] = eid
        e["src"] = "" if e["src"] is None else str(e["src"])
        for fld in ("en", "speaker", "scene", "file", "note", "page"):
            if e.get(fld) is None or e.get(fld) == "":
                e.pop(fld, None)
            elif not isinstance(e[fld], str):
                e[fld] = str(e[fld])
        if "voice" in e:
            if e["voice"] in (None, "", False, 0):
                e.pop("voice")
            else:
                e["voice"] = str(e["voice"])
        for fld in ("maxlen", "maxlines", "dur_ms"):
            if fld in e:
                try:
                    e[fld] = int(e[fld]) or None
                except (TypeError, ValueError):
                    e[fld] = None
                if not e[fld]:
                    e.pop(fld)
        e["kind"] = str(e.get("kind") or "dialogue")
        if e["kind"] not in KINDS:
            problems.append(f"dòng {n}: kind '{e['kind']}' không hợp lệ (dùng: {', '.join(KINDS)})")
            continue
        src[eid] = e
    if problems:
        more = f"\n  … và {len(problems) - 20} lỗi khác" if len(problems) > 20 else ""
        die("src.jsonl không hợp lệ:\n  " + "\n  ".join(problems[:20]) + more)
    return src


def load_tr():
    """Tra ve (tr, trh, so dong hong, trx). trx[id] = {"l": nguoi nghe, "g": 1 neu =gop}."""
    items, bad = read_jsonl(p(F_TR))
    tr, trh, trx = {}, {}, {}
    for it in items:
        if not isinstance(it, dict) or "id" not in it:
            bad += 1
            continue
        eid = str(it["id"])
        if it.get("vi") is None:
            tr.pop(eid, None)
            trh.pop(eid, None)
            trx.pop(eid, None)
        else:
            tr[eid] = str(it["vi"])
            trh[eid] = it.get("h")
            x = {}
            if it.get("l"):
                x["l"] = str(it["l"])
            if it.get("g"):
                x["g"] = 1
            if x:
                trx[eid] = x
            else:
                trx.pop(eid, None)
    return tr, trh, bad, trx


def load_minors():
    s = set()
    path = p(F_MINOR)
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                if line.lstrip().startswith("#"):
                    continue
                t = re.split(r"\s+#", line.strip(), maxsplit=1)[0].strip()
                if t:
                    s.add(t)
    return s


def load_state():
    path = p(F_STATE)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(st):
    atomic_write(p(F_STATE), json.dumps(st, ensure_ascii=False, indent=1) + "\n")


def fit_matches(pats, e):
    """game.json fit_auto: mau (kind, 'kind:ui', 'file:Menu*', '*') cho muc engine tu ngat/tu co (P2)."""
    f = (e.get("file") or "").replace("\\", "/")
    base = f.split("/")[-1]
    for k in pats or []:
        if k == "*" or k == e.get("kind") or k == "kind:" + str(e.get("kind")):
            return True
        if k.startswith("file:") and (fnmatch.fnmatch(f, k[5:]) or fnmatch.fnmatch(base, k[5:])):
            return True
    return False


def maxlen_for(cfg, e):
    ml = cfg.get("max_len") or {}
    f = e.get("file") or ""
    base = f.replace("\\", "/").split("/")[-1]
    for k, v in ml.items():
        if k.startswith("file:") and (fnmatch.fnmatch(f, k[5:]) or fnmatch.fnmatch(base, k[5:])):
            return int(v)
    for k, v in ml.items():
        if k == e.get("kind") or k == "kind:" + str(e.get("kind")):
            return int(v)
    return None


def build_plan(cfg, src, tr, trh):
    code_re = build_code_re(cfg)
    skips = []
    for x in cfg.get("skip_patterns") or []:
        try:
            skips.append(re.compile(x))
        except re.error as ex:
            die(f"skip_patterns '{x}' sai: {ex}")
    auto, groups, key2c = [], collections.OrderedDict(), {}
    for eid, e in src.items():
        t = e["src"]
        if any(r.search(t) for r in skips) or not LETTER_RE.search(code_re.sub("", t)):
            auto.append(eid)
            continue
        # Thoai: chi gom cau trung trong cung canh va cung nguoi noi (xung ho phu thuoc nguoi nghe).
        if e["kind"] == "dialogue":
            key = ("d", t, e.get("speaker") or "", e.get("scene") or "")
        else:
            key = ("s", e["kind"], t)
        if key in key2c:
            groups[key2c[key]].append(eid)
        else:
            key2c[key] = eid
            groups[eid] = []
    final = collections.OrderedDict()
    for c, dups in groups.items():
        mem = [c] + dups
        best = next((m for m in mem if m in tr and trh.get(m) in (None, src_hash(src[m]["src"]))), c)
        if best != c:
            mem.remove(best)
            mem.insert(0, best)
        final[mem[0]] = mem[1:]
    order = list(final.keys())
    td, ts = int(cfg["batch_dialogue"]), int(cfg["batch_short"])
    batches = []

    def chunk(ids, cls, target, key, low):
        cur = []
        for i, eid in enumerate(ids):
            cur.append(eid)
            e = src[eid]
            nxt = src[ids[i + 1]] if i + 1 < len(ids) else None
            bnd = nxt is None or not e.get(key) or nxt.get(key) != e.get(key)
            if (len(cur) >= int(target * low) and bnd) or len(cur) >= int(target * (1.5 if cls == "dialogue" else 1)):
                batches.append({"n": len(batches) + 1, "cls": cls, "ids": cur})
                cur = []
        if cur:
            batches.append({"n": len(batches) + 1, "cls": cls, "ids": cur})

    # Muc ngan (UI, du lieu, ten) dich truoc, thoai dich sau theo thu tu cot truyen.
    chunk([i for i in order if src[i]["kind"] != "dialogue"], "short", ts, "file", 0.6)
    chunk([i for i in order if src[i]["kind"] == "dialogue"], "dialogue", td, "scene", 1.0)
    plan = {"version": PLAN_VERSION, "vgk": VERSION, "created": now() + ":" + stamp(), "src_sha": file_sha(p(F_SRC)),
            "batch": [td, ts], "auto": auto, "groups": final, "batches": batches}
    nd = sum(1 for c in order if src[c]["kind"] == "dialogue")
    st = {"total": len(src), "auto": len(auto), "dup": sum(len(v) for v in final.values()), "need": len(order),
          "dlg": nd, "batches": len(batches), "bd": sum(1 for b in batches if b["cls"] == "dialogue")}
    return plan, st


def plan_summary(st):
    return (f"{fmt_n(st['total'])} mục · tự động {fmt_n(st['auto'])} · trùng {fmt_n(st['dup'])} · "
            f"cần dịch {fmt_n(st['need'])} · {st['batches']} lô")


class Ctx:
    def __init__(self, need_plan=True, quiet=False):
        self.cfg = load_cfg()
        self.src = load_src()
        self.code_re = build_code_re(self.cfg)
        self.cjk = self.cfg["source_lang"] in ("ja", "zh", "ko")
        self.allow = set(self.cfg.get("allow_chars") or "")
        self.tr, self.trh, self.tr_bad, self.trx = load_tr()
        self.minors = load_minors()
        self.state = load_state()
        self.root_cfg = load_root_cfg()
        self.src_order = list(self.src)
        self.src_index = {eid: k for k, eid in enumerate(self.src_order)}
        self._scene_spk = None
        self._scene_pos = None
        self._ratio_thr = None
        self._cam = None
        self._gl_words = None
        self.reload_tables()
        self.stale = {i for i, h in self.trh.items() if h and i in self.src and h != src_hash(self.src[i]["src"])}
        self.plan = None
        if need_plan:
            path = p(F_PLAN)
            plan = None
            if os.path.exists(path):
                try:
                    with open(path, encoding="utf-8") as f:
                        plan = json.load(f)
                except Exception:
                    plan = None
            want = [int(self.cfg["batch_dialogue"]), int(self.cfg["batch_short"])]
            # Plan cua ban 1.x khong ghi "batch": giu nguyen de khong doi so lo (tien do, ghi chu cu dung so lo do).
            if (plan is None or plan.get("version") != PLAN_VERSION or plan.get("src_sha") != file_sha(p(F_SRC))
                    or ("batch" in plan and plan["batch"] != want)):
                plan, st = build_plan(self.cfg, self.src, self.tr, self.trh)
                atomic_write(path, json.dumps(plan, ensure_ascii=False) + "\n")
                if not quiet:
                    print("(src.jsonl mới hoặc đã đổi → đã chia lại lô: " + plan_summary(st) + ")")
            self.plan = plan
            self._derive()

    def reload_tables(self):
        self.gloss = read_tsv(p(F_GLOSS), GLOSS_COLS)
        self.pairs = read_tsv(p(F_PAIR), PAIR_COLS)
        self.scenes = {r["scene"]: r for r in read_tsv(p(F_SCENE), SCENE_COLS) if r["scene"]}
        self.voices = read_tsv(p(F_VOICE), VOICE_COLS)
        self._all_terms = None
        self._secret = None

    # --- moc truyen: dong co tu_canh/lo_tu chi ap tu cho do tro di
    def pos(self, eid):
        return self.src_index.get(eid, -1)

    def scene_pos(self):
        if self._scene_pos is None:
            d = {}
            for k, eid in enumerate(self.src_order):
                sc = self.src[eid].get("scene")
                if sc and sc not in d:
                    d[sc] = k
            self._scene_pos = d
        return self._scene_pos

    def mark_pos(self, mark):
        """Vi tri cua moc (ma canh hoac id cau). Rong: tu dau (-1). Khong ro: None (dong khong bao gio ap)."""
        mark = (mark or "").strip()
        if not mark:
            return -1
        sp = self.scene_pos()
        if mark in sp:
            return sp[mark]
        return self.src_index.get(mark)

    def phase_pick(self, rows, eid):
        """Cac dong cung chu the: lay dong co moc gan nhat ma <= vi tri cau eid."""
        pe = self.pos(eid)
        best, bp = [], None
        for r in rows:
            mp = self.mark_pos(r.get("tu_canh"))
            if mp is None or mp > pe:
                continue
            if bp is None or mp > bp:
                best, bp = [r], mp
            elif mp == bp:
                best.append(r)
        return best

    def voice_rows(self, spk):
        return [v for v in self.voices if v["speaker"] == spk]

    def voice_at(self, spk, pe):
        """Ho so nhan vat dung tai vi tri pe: gop cac dong co moc <= pe, dong sau ghi de o co noi dung."""
        valid = []
        for r in self.voice_rows(spk):
            mp = self.mark_pos(r.get("tu_canh"))
            if mp is not None and mp <= pe:
                valid.append((mp, r))
        if not valid:
            return None
        out = {}
        for _, r in sorted(valid, key=lambda x: x[0]):
            for k, v in r.items():
                if k != "_line" and (v or k not in out):
                    out[k] = v
        return out

    def voice_for(self, spk, eid=None):
        return self.voice_at(spk, self.pos(eid) if eid is not None else -1)

    def secret_terms(self):
        if self._secret is None:
            self._secret = [r for r in self.gloss if (r.get("lo_tu") or "").strip() and r["src"] and r["vi"]]
        return self._secret

    def _derive(self):
        pl = self.plan
        self.auto = set(pl.get("auto", []))
        self.canon_of, self.members = {}, {}
        for c, dups in pl.get("groups", {}).items():
            mem = [c] + list(dups)
            self.members[c] = mem
            for m in mem:
                self.canon_of[m] = c
        self.minor_all = self.minors & set(self.src)
        self.rep_of = {c: next((m for m in mem if m not in self.minor_all), None) for c, mem in self.members.items()}
        self.batches = pl.get("batches", [])
        self.batch_of = {}
        for b in self.batches:
            for c in b["ids"]:
                for m in self.members.get(c, [c]):
                    self.batch_of[m] = b["n"]
        self.sig = f"{pl.get('created')}|{pl.get('src_sha')}"
        self._laps = None

    # --- tra cuu
    def _lookup(self, eid, fresh):
        def ok(i):
            return i in self.tr and not (fresh and i in self.stale)
        if ok(eid):
            return self.tr[eid]
        c = self.canon_of.get(eid)
        if c is None:
            return None
        for m in self.members.get(c, ()):
            if ok(m):
                return self.tr[m]
        return None

    def eff(self, eid):
        """Ban dich dung cho id (uu tien ban con hop voi cau goc hien tai)."""
        v = self._lookup(eid, True)
        return v if v is not None else self._lookup(eid, False)

    def done(self, eid):
        return self._lookup(eid, True) is not None

    def needs(self):
        return [r for r in self.rep_of.values() if r]

    def batch_reps(self, b):
        return [self.rep_of[c] for c in b["ids"] if self.rep_of.get(c)]

    def batch_pending(self, b):
        return [r for r in self.batch_reps(b) if not self.done(r)]

    def group_size(self, eid):
        c = self.canon_of.get(eid)
        return len(self.members.get(c, [eid])) if c else 1

    def laps(self):
        """Cau thoai cung nguoi noi, cung chu o canh khac (2.3): {dai dien: [cac dai dien cung bo, theo thu tu truyen]}.
        Cau trung trong cung canh va cung nguoi noi da gop nhom tu plan (dich 1 lan)."""
        if getattr(self, "_laps", None) is None:
            by = collections.OrderedDict()
            for b in getattr(self, "batches", None) or []:
                if b["cls"] != "dialogue":
                    continue
                for c in b["ids"]:
                    r = self.rep_of.get(c)
                    if r:
                        e = self.src[r]
                        by.setdefault((e["src"], e.get("speaker") or ""), []).append(r)
            self._laps = {r: mem for mem in by.values() if len(mem) > 1 for r in mem}
        return self._laps

    def lap_hint(self, eid):
        """Id cau lap o canh khac da dich (som nhat theo thu tu truyen), hoac None."""
        for r in self.laps().get(eid, ()):
            if r != eid and self.done(r):
                return r
        return None

    def all_terms(self):
        if self._all_terms is None:
            self._all_terms = build_term_re([r for r in self.gloss if r["src"] and r["vi"]])
        return self._all_terms

    def check_terms(self, text):
        """Thuat ngu co forbid, la ten, hoac thuoc term_check_types (>=2 ky tu CJK / >=2 tu);
        khop theo thuat ngu dai nhat; bo thuat ngu CJK 1 ky tu (qua mo ho)."""
        nt = set(self.cfg.get("name_types") or [])
        xt = set(self.cfg.get("term_check_types") or [])
        rx, mp = self.all_terms()
        out = []
        for r in find_terms(rx, mp, text):
            long_enough = (len(r["src"]) >= 2 if CJK_RE.search(r["src"]) else len(r["src"].split()) >= 2)
            if not (r["forbid"] or r["type"] in nt or (r["type"] in xt and long_enough)):
                continue
            if len(r["src"]) < 2 and CJK_RE.search(r["src"]):
                continue
            out.append(r)
        return out

    # --- xung ho theo cap
    def scene_speakers(self):
        if self._scene_spk is None:
            d = collections.defaultdict(set)
            for e in self.src.values():
                if e["kind"] == "dialogue" and e.get("speaker") and e.get("scene"):
                    d[e["scene"]].add(e["speaker"])
            self._scene_spk = d
        return self._scene_spk

    def listener(self, eid, given=None):
        """Nguoi nghe: ghi ro (@@ ~N.k >ten) > da luu trong tr.jsonl > canh dung 2 nguoi noi."""
        if given:
            return given
        x = self.trx.get(eid) or {}
        if x.get("l"):
            return x["l"]
        e = self.src.get(eid) or {}
        s, sc = e.get("speaker"), e.get("scene")
        if s and sc:
            others = self.scene_speakers().get(sc, set()) - {s}
            if len(others) == 1:
                return next(iter(others))
        return None

    def pair_rows(self, spk, lis, eid=None):
        """Dong xung ho dung cho (nguoi noi, nguoi nghe): dung cap > dong '*' > (chi khi chua ro nguoi nghe) moi dong.
        Nguoi nghe 'A,B' (noi voi nhieu nguoi): gop dong cua tung nguoi. Co eid: moi cap chi lay dong dung moc."""
        if lis and "," in lis:
            out = []
            for one in (x.strip() for x in lis.split(",") if x.strip()):
                out += [r for r in self.pair_rows(spk, one, eid) if r not in out]
            return out

        def ph(rows):
            if eid is None:
                return rows
            out = []
            for k in uniq(r["listener"] for r in rows):
                out += self.phase_pick([r for r in rows if r["listener"] == k], eid)
            return out
        if lis:
            exact = ph([r for r in self.pairs if r["speaker"] == spk and r["listener"] == lis])
            if exact:
                return exact
        star = ph([r for r in self.pairs if r["speaker"] == spk and r["listener"] in ("*", "")])
        if star or lis:
            return star
        return ph([r for r in self.pairs if r["speaker"] == spk])

    # --- do dai bat thuong
    def min_ratio_len(self):
        return 30 if self.cfg["source_lang"] == "en" else 8

    def ratio_threshold(self):
        if self._ratio_thr is None:
            vals = []
            ml = self.min_ratio_len()
            for eid, vi in self.tr.items():
                e = self.src.get(eid)
                if not e:
                    continue
                s = strip_codes(self, e["src"]).strip()
                if len(s) < ml:
                    continue
                v = strip_codes(self, vi).strip()
                if v:
                    vals.append(len(v) / len(s))
            if len(vals) >= 500:
                vals.sort()
                self._ratio_thr = vals[int(0.95 * (len(vals) - 1))]
            else:
                self._ratio_thr = float(LEN_RATIO_DEFAULT.get(self.cfg["source_lang"], 4.0))
        return self._ratio_thr

    def gloss_words(self):
        if self._gl_words is None:
            w = set()
            for r in self.gloss:
                for x in re.findall(r"[A-Za-z][A-Za-z'’-]*", r.get("vi") or ""):
                    w.add(x.lower())
            self._gl_words = w
        return self._gl_words

    # --- mau dich sat (cam_mau.tsv), loc theo pham_vi
    def scope_ok(self, pv):
        pv = (pv or "chung").strip()
        if pv in ("", "chung"):
            return True
        k, _, v = pv.partition(":")
        c = self.cfg
        return ((k == "nguon" and v == c["source_lang"]) or (k == "the_loai" and v == c.get("the_loai"))
                or (k == "boi_canh" and v == c.get("boi_canh")) or (k == "game" and v == c.get("slug")))

    def cam_rules(self):
        if self._cam is None:
            rows, seen = [], set()
            # Ban chung tren may (ROOT/_chung/khauvi) neu co, khong thi hat giong trong goi; cong them ban rieng cua WORK.
            chung = [os.path.join(d, "cam_mau.tsv") for d in khauvi_dirs()]
            chung = [f for f in chung if os.path.exists(f)][:1]
            for f in chung + [p("cam_mau.tsv")]:
                for r in read_tsv(f, CAM_COLS):
                    if not r["regex"] or r["regex"] in seen or not self.scope_ok(r["pham_vi"]):
                        continue
                    try:
                        rows.append((re.compile(r["regex"], re.I), r["goi_y"]))
                        seen.add(r["regex"])
                    except re.error:
                        pass
            self._cam = rows
        return self._cam


def codes(ctx, text):
    return [m.group(0) for m in ctx.code_re.finditer(text)]


def strip_codes(ctx, text):
    return ctx.code_re.sub("", text)


def validate(ctx, eid, vi, force=False):
    """Tra ve (loi, canh bao), moi phan tu la (nhom, chi tiet). force: bo qua kiem chu goc va thuat ngu cam."""
    e = ctx.src[eid]
    s = e["src"]
    errs, warns = [], []
    if not vi.strip() and s.strip():
        errs.append(("rỗng", "bản dịch rỗng"))
    sc = collections.Counter(codes(ctx, s))
    vc = collections.Counter(codes(ctx, vi))
    if sc != vc:
        bits = []
        miss, extra = sc - vc, vc - sc
        if miss:
            bits.append("thiếu " + ", ".join(fmt_cnt(miss)))
        if extra:
            bits.append("thừa " + ", ".join(fmt_cnt(extra)))
        errs.append(("mã/thẻ lệch", "; ".join(bits)))
    if NAMEBOX_OPEN.search(vi) and len(NAMEBOX_OPEN.findall(vi)) != len(NAMEBOX_FULL.findall(vi)):
        errs.append(("mã/thẻ lệch", "hộp tên \\x<…> thiếu dấu >"))
    if ctx.cfg["linebreaks"] == "keep" and s.count("\n") != vi.count("\n"):
        errs.append(("số dòng lệch", f"{vi.count(chr(10)) + 1} dòng, gốc {s.count(chr(10)) + 1}"))
    if ctx.cjk and not force:
        left = [ch for ch in CJK_RE.findall(strip_codes(ctx, vi)) if ch not in ctx.allow]
        if left:
            errs.append(("còn chữ/dấu gốc", "".join(sorted(set(left)))[:12]))
    if not force:
        jd = sorted({ch for ch in vi if ch in JP_DASH and ch not in ctx.allow})
        if jd:
            errs.append(("dấu Nhật", f"còn {''.join(jd)}: bỏ đi; lời bị ngắt thì dùng một dấu '—'"))
    nt = set(ctx.cfg.get("name_types") or [])
    rx, mp = ctx.all_terms()
    found_all = find_terms(rx, mp, s)
    for r in ctx.check_terms(s):
        if not force and r["forbid"]:
            # Che nghia cua cac thuat ngu khac cung co trong cau (vd 'Cảng Vera' khi cam 'Vera').
            mv = vi
            for o in found_all:
                if o is not r and o["vi"] and o["vi"] != r["vi"]:
                    mv = word_re(o["vi"], ci=True).sub(" ", mv)
            for fv in split_list(r["forbid"]):
                if word_in(fv, mv) and not word_in(fv, r["vi"]):
                    errs.append(("thuật ngữ cấm", f"'{fv}' → dùng '{r['vi']}' ({r['src']})"))
        if not word_in(r["vi"], vi, ci=True):
            if r["type"] in nt:
                warns.append(("thiếu tên", f"'{r['vi']}' ({r['src']})"))
            elif r["type"] in set(ctx.cfg.get("term_check_types") or []):
                warns.append(("thiếu thuật ngữ", f"'{r['vi']}' ({r['src']})"))
    if not force:
        pe = ctx.pos(eid)
        for r in ctx.secret_terms():
            mp = ctx.mark_pos(r["lo_tu"])
            if (mp is not None and pe < mp and word_in(r["vi"], vi, ci=True)
                    and not re.search(term_pattern(r["src"]), s, re.I)):
                errs.append(("lộ tình tiết", f"'{r['vi']}' chỉ được xuất hiện từ {r['lo_tu']}; câu gốc chưa có '{r['src']}'"))
    if not ctx.cjk:
        ss = s.strip()
        if len(ss) >= 12 and LETTER_RE.search(ss) and ss in vi:
            warns.append(("giống câu gốc", "bản dịch chứa nguyên câu gốc"))
    errs += plural_errors(s, vi)
    sn = nums_of(ctx, s)
    if sn:
        vn = nums_of(ctx, vi)
        low = vi.lower()
        miss = [x for x in sorted((sn - vn).elements()) if not (x in NUM_WORDS and word_in(NUM_WORDS[x], low))]
        if miss:
            warns.append(("số liệu lệch", "số trong gốc không có trong bản dịch: " + ", ".join(uniq(miss)[:6])))
    ml = e.get("maxlen") or maxlen_for(ctx.cfg, e)
    mxl = e.get("maxlines")
    if ml and mxl:
        # Adapter tu ngat dong: chi kiem so dong sau khi ngat theo tu.
        n = wrap_count(strip_codes(ctx, vi), int(ml))
        if n > int(mxl):
            warns.append(("quá số dòng", f"{n}>{mxl} dòng ở {ml} ký tự/dòng"))
    elif ml:
        longest = max(len(x) for x in strip_codes(ctx, vi).split("\n"))
        if longest > int(ml):
            warns.append(("quá dài", f"{longest}>{ml} ký tự"))
    dur, cps = e.get("dur_ms"), ctx.cfg.get("cps_max")
    if dur and cps:
        rate = len(strip_codes(ctx, vi).replace("\n", "")) / (dur / 1000.0)
        if rate > float(cps):
            warns.append(("phụ đề quá nhanh", f"{rate:.0f} ký tự/giây > {cps}"))
    return errs, warns


NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")
NUM_WORDS = {"0": "không", "1": "một", "2": "hai", "3": "ba", "4": "bốn", "5": "năm", "6": "sáu", "7": "bảy",
             "8": "tám", "9": "chín", "10": "mười"}


def nums_of(ctx, text):
    """Cac so (bo dau ngan cach . ,) trong van ban da bo ma, sau NFKC (so toan goc -> so thuong)."""
    t = unicodedata.normalize("NFKC", strip_codes(ctx, text))
    # So di kem don vi chu Han (300万, 2億, 5千…) doi chu so khi sang tieng Viet ("ba triệu"): khong dem.
    return collections.Counter(re.sub(r"[.,]", "", m.group(0)) for m in NUM_RE.finditer(t)
                               if not re.match(r"\s*[万萬億亿千百兆만억천조]", t[m.end():]))


def wrap_count(text, width):
    """So dong sau khi ngat theo tu o be rong `width` ky tu (moi doan xuong dong la it nhat 1 dong)."""
    n = 0
    for para in text.split("\n"):
        cur, lines = 0, 1
        for w in para.split(" "):
            if not w:
                continue
            if cur == 0:
                cur = len(w)
            elif cur + 1 + len(w) > width:
                lines += 1
                cur = len(w)
            else:
                cur += 1 + len(w)
        n += lines
    return n


def icu_frames(t):
    """Khung ICU {bien, plural|select|selectordinal, khoa {..} …}: danh sach (bien, loai, ((khoa, co_#), …)).
    None neu sai cu phap (thieu ngoac)."""
    out, i, n = [], 0, len(t)
    while True:
        m = ICU_HEAD_RE.search(t, i)
        if not m:
            return out
        k, keys = m.end(), []
        while True:
            while k < n and t[k].isspace():
                k += 1
            if k >= n:
                return None
            if t[k] == "}":
                k += 1
                break
            om = re.match(r"offset:\s*\d+", t[k:])
            if om:
                k += om.end()
                continue
            km = re.match(r"(=?[\w-]+)\s*\{", t[k:])
            if not km:
                return None
            key = km.group(1)
            k += km.end()
            d, start = 1, k
            while k < n and d:
                if t[k] == "{":
                    d += 1
                elif t[k] == "}":
                    d -= 1
                k += 1
            if d:
                return None
            keys.append((key, "#" in t[start:k - 1]))
        out.append((m.group(1), m.group(2).lower(), tuple(keys)))
        i = k


def ue_frames(t):
    """Khung Unreal |plural(one=..,other=..) |gender(..) |ordinal(..) |hpp(..): danh sach (loai, khoa)."""
    out = []
    for m in UE_MOD_RE.finditer(t):
        k, n, args, cur, q = m.end(), len(t), [], "", False
        while k < n:
            c = t[k]
            if q:
                q = c != '"'
                cur += c
            elif c == '"':
                q = True
                cur += c
            elif c == ",":
                args.append(cur)
                cur = ""
            elif c == ")":
                args.append(cur)
                break
            else:
                cur += c
            k += 1
        else:
            return None
        kind = m.group(1).lower()
        if kind in ("hpp", "gender"):
            # Doi so theo vi tri (gender: nam, nu, trung tinh): chi so so luong, chu ben trong duoc dich.
            out.append((kind, (str(len([a for a in args if a.strip()])),)))
        else:
            out.append((kind, tuple(sorted(a.split("=", 1)[0].strip() for a in args if a.strip()))))
    return out


def plural_errors(s, vi):
    errs = []
    if ICU_HEAD_RE.search(s):
        sf, vf = icu_frames(s), icu_frames(vi)
        if sf is not None:
            sig = lambda fr: sorted((a, b, tuple(sorted(k for k, _ in c))) for a, b, c in fr)
            if vf is None or sig(sf) != sig(vf):
                errs.append(("khung số nhiều lệch", "khung ICU {biến, plural/select, khóa {…}} phải giữ đủ biến và khóa như gốc"))
            else:
                need = {(a, k) for a, _, c in sf for k, h in c if h}
                have = {(a, k) for a, _, c in vf for k, h in c if h}
                if need - have:
                    errs.append(("khung số nhiều lệch", "mất '#' trong nhánh " + ", ".join(sorted(k for _, k in need - have))))
    if UE_MOD_RE.search(s):
        sf, vf = ue_frames(s), ue_frames(vi)
        if sf is not None and (vf is None or sorted(sf) != sorted(vf)):
            errs.append(("khung số nhiều lệch", "giữ đủ khóa của |plural(…)/|ordinal(…) và đủ số đối số của |gender(…)/|hpp(…) như gốc"))
    return errs


def validate_gop(ctx, eid):
    """'=gop': cau nay da duoc don vao cau lien truoc cung trang (khong long tieng, khong ma)."""
    if not ctx.cfg.get("gop_ok"):
        return [("gộp không hợp lệ", "game này chưa bật =gộp (game.json gop_ok: true) — chỉ bật khi đã thử trong game "
                                     "thấy câu rỗng bị bỏ qua, không hiện ô thoại trống hay câu gốc")]
    k = ctx.src_index.get(eid, 0)
    if k == 0:
        return [("gộp không hợp lệ", "không có câu liền trước")]
    prev, e = ctx.src[ctx.src_order[k - 1]], ctx.src[eid]
    bad = []
    if (prev.get("scene") or "") != (e.get("scene") or ""):
        bad.append("khác cảnh với câu trước")
    if not e.get("page") or prev.get("page") != e.get("page"):
        bad.append("khác trang hoặc adapter không ghi trường page")
    if e.get("voice") or prev.get("voice"):
        bad.append("có lồng tiếng")
    if codes(ctx, e["src"]):
        bad.append("câu có mã/thẻ")
    if ctx.plan is not None and ctx.group_size(eid) > 1:
        bad.append("câu này dùng chung bản dịch với câu trùng khác")
    return [("gộp không hợp lệ", "; ".join(bad))] if bad else []


def pair_words(field):
    return {w for x in re.split(r"[/,;]", field or "") for w in x.strip().lower().split() if w}


def gioi_of(v):
    """'nam' | 'nu' | None tu cot gioi cua ho so ('nam (vỏ)' van la nam cho toi moc lo)."""
    g = unicodedata.normalize("NFC", ((v or {}).get("gioi") or "").strip().lower())
    if g.startswith("nữ") or g.startswith("nu"):
        return "nu"
    if g.startswith("nam"):
        return "nam"
    return None


def xung_gioi_sai(xung, g):
    """Cac cach xung trong cot xung trai voi gioi g."""
    bad = XUNG_NU if g == "nam" else XUNG_NAM if g == "nu" else set()
    opts = {unicodedata.normalize("NFC", x.strip().lower()) for x in re.split(r"[/,;]", xung or "") if x.strip()}
    return sorted(o for o in opts if o in bad)


def pair_lint(ctx, eid, vi, lis=None):
    """Kiem xung ho; nguoi nghe 'A,B' (noi voi nhieu nguoi) thi kiem tung nguoi, loi o ai cung bao."""
    if lis is None:
        lis = ctx.listener(eid, None)
    names = [x.strip() for x in (lis or "").split(",") if x.strip()]
    if len(names) <= 1:
        return pair_lint1(ctx, eid, vi, names[0] if names else lis)
    errs, warns = [], []
    for one in names:
        a, b = pair_lint1(ctx, eid, vi, one)
        errs += [x for x in a if x not in errs]
        warns += [x for x in b if x not in warns]
    return errs, warns


def pair_lint1(ctx, eid, vi, lis=None):
    """Kiem xung ho theo cap (nguoi noi, nguoi nghe). Tra ve (loi, canh bao)."""
    e = ctx.src[eid]
    errs, warns = [], []
    spk = e.get("speaker")
    if e["kind"] != "dialogue" or not spk or not vi:
        return errs, warns
    lis = ctx.listener(eid, lis)
    rows = ctx.pair_rows(spk, lis, eid)
    # Chua ro nguoi nghe ma bang cua nguoi noi chia theo tung nguoi nghe: chi dung khi dung voi moi nguoi nghe.
    amb = not lis and len({r["listener"] for r in rows}) >= 2 and not any(r["listener"] in ("*", "") for r in rows)
    xs = [pair_words(r["xung"]) for r in rows]
    gs = [pair_words(r["goi"]) for r in rows]
    xw = set().union(*xs) if xs else set()
    gw = set().union(*gs) if gs else set()
    ax = {x.strip().lower() for r in rows for x in re.split(r"[/,;]", r["xung"]) if x.strip()}
    who = spk + (f" → {lis}" if lis else "")
    hint = "→ thêm ' >tên gốc người nghe' sau mã câu"

    def allows(w, x, g):
        return (w == "tao" and "tao" in x) or (w == "mày" and "mày" in g)
    found = {m.group(1).lower() for m in MAYTAO_RE.finditer(MAYTAO_EXCL_RE.sub(" ", vi))}
    badmt = sorted(w for w in found if not any(allows(w, x, g) for x, g in zip(xs, gs)))
    if badmt:
        errs.append(("xưng hô cấm", f"'{'/'.join(badmt)}' mà bảng xưng hô của {who} không cho phép"
                     + ("" if rows else f" (chưa có dòng xưng hô {spk} → {lis or '*'})")))
    elif amb:
        part = sorted(w for w in found if not all(allows(w, x, g) for x, g in zip(xs, gs)))
        if part:
            okl = [r["listener"] for r, x, g in zip(rows, xs, gs) if all(allows(w, x, g) for w in part)]
            errs.append(("xưng hô cấm", f"'{'/'.join(part)}': chưa rõ người nghe, bảng của {spk} chỉ cho với "
                         f"{', '.join(okl)} {hint}"))
    ngoi = [any("ngươi" in x for x in re.split(r"[/,;]", r["goi"].lower())) and not ({"cậu", "cô"} & g)
            for r, g in zip(rows, gs)]
    if rows and (all(ngoi) if amb else (any(ngoi) and not ({"cậu", "cô"} & gw))):
        if CAUCO_RE.search(CAUCO_EXCL_RE.sub(" ", vi)):
            warns.append(("gọi lệch bảng", f"'cậu/cô' trong khi bảng ghi gọi 'ngươi' ({who})"))
    srows = rows if rows or not lis else ctx.pair_rows(spk, None, eid)
    if srows and not rows:
        # Chua co cap (nguoi noi, nguoi nghe): doi chieu tu xung voi moi dong cua nguoi noi, nhac them cap.
        xw = set().union(*[pair_words(r["xung"]) for r in srows])
        ax = {x.strip().lower() for r in srows for x in re.split(r"[/,;]", r["xung"]) if x.strip()}
        who = f"{spk} (chưa có cặp {spk} → {lis}; thêm @@pair)"
    if srows:
        selfw = {m.group(1).lower() for m in SELF_RE.finditer(SELF_EXCL_RE.sub(" ", vi))} - {"tao"}
        off = sorted(w for w in selfw if w not in xw)
        if off:
            warns.append(("tự xưng khác bảng xưng hô", f"{'/'.join(off)} (bảng {who}: {'/'.join(sorted(ax)) or '?'})"))
        elif amb:
            part = sorted(w for w in selfw if not all(w in x for x in xs))
            if part:
                warns.append(("tự xưng khác bảng xưng hô", f"{'/'.join(part)}: chưa rõ người nghe, chỉ đúng với một số "
                              f"người nghe của {spk} {hint}"))
    v = ctx.voice_for(spk, eid)
    g = gioi_of(v)
    if g:
        rx = TU_XUNG_NU_RE if g == "nam" else TU_XUNG_NAM_RE
        hits = sorted({m.group(1).lower() for m in rx.finditer(vi)})
        if hits:
            warns.append(("giới tính lệch hồ sơ", f"'{'/'.join(hits)}' là cách tự xưng của {'nữ' if g == 'nam' else 'nam'};"
                          f" hồ sơ {spk} lúc này: {v.get('gioi')}"))
    return errs, warns


def style_warns(ctx, eid, vi):
    """Canh bao phong cach: do dai bat thuong, chu Anh sot, mau dich sat (cam_mau.tsv)."""
    warns = []
    e = ctx.src[eid]
    s = strip_codes(ctx, e["src"]).strip()
    v = strip_codes(ctx, vi).strip()
    if v and len(s) >= ctx.min_ratio_len():
        thr = ctx.ratio_threshold()
        if len(v) / len(s) > thr:
            warns.append(("dài bất thường", f"tỷ lệ {len(v) / len(s):.1f} > {thr:.1f} (kiểm có thêm ý không)"))
    if ctx.cfg["source_lang"] != "en":
        gl = ctx.gloss_words()
        for m in ASCII_RUN_RE.finditer(v):
            words = [w.lower() for w in m.group(0).split()]
            if sum(1 for w in words if w in EN_STOP) >= 2 and not all(w in gl for w in words):
                warns.append(("chữ Anh sót", m.group(0)[:40]))
                break
    else:
        words = re.findall(r"[^\W\d_]+", v)
        if len(words) >= 4 and not any(ch in VI_SET for ch in v.lower()):
            sw = {w.lower() for w in re.findall(r"[^\W\d_]+", s)}
            if sum(1 for w in words if w.lower() in sw) >= 0.5 * len(words):
                warns.append(("có thể chưa dịch", "câu không có dấu tiếng Việt, phần lớn từ trùng câu gốc"))
    for rx, hint in ctx.cam_rules():
        m = rx.search(vi)
        if m:
            warns.append(("dịch sát", f"'{m.group(0)[:30]}'" + (f" → {hint}" if hint else "")))
    return warns + dau_warns(ctx, e, v)


def norm_dau(vi):
    """Chuan hoa dau an toan truoc khi ghi: '……' -> '…'."""
    return ELL_RUN_RE.sub("\u2026", vi)


def dau_warns(ctx, e, v):
    """Canh bao dau cau va cau nen cho thoai/loi ke (v: ban dich da bo ma)."""
    out = []
    if e["kind"] != "dialogue" or not v:
        return out
    body = v.lstrip(" \"“'‘(「『")
    if body[:1] in "—–":
        out.append(("mở câu bằng gạch", "bỏ gạch đầu câu (dấu kiểu Nhật)"))
    words = re.findall(r"[^\W_]+", v)
    tail = v.rstrip(TRAIL_CLOSE)
    sraw = strip_codes(ctx, e["src"]).strip()
    s = sraw.rstrip(TRAIL_CLOSE)
    # Goc khong co dau ket (nut, lua chon, nhan) va cau ngan thi bo qua
    src_end = bool(sraw) and sraw[-1] in "。．.！!？?…‥」』”\"）)～~"
    if (len(words) >= 3 and tail and tail[-1] not in END_PUNCT and not (s and s[-1] in CONT_SRC)
            and (src_end or len(words) > 6)):
        out.append(("thiếu dấu kết", "câu chưa có dấu kết (. ! ? …)"))
    en = (e.get("en") or (e["src"] if ctx.cfg["source_lang"] == "en" else "")).strip()
    sr = strip_codes(ctx, e["src"])
    is_q = "？" in sr or "?" in sr
    if not is_q and en.rstrip(TRAIL_CLOSE).endswith("?"):
        tail = sr.rstrip(Q_STRIP)
        is_q = any(tail.endswith(x) for x in Q_TAIL.get(ctx.cfg["source_lang"], ()))
    if is_q and "?" not in v:
        out.append(("thiếu dấu hỏi", "gốc là câu hỏi mà bản Việt không có '?'"))
    if en:
        en = re.sub(r"\[[^\]\n]*\]|<[^>\n]*>|\{[^}\n]*\}", " ", en)   # bo the dinh dang trong EN truoc khi dem
        ew = len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", en))
        if ew >= 10 and len(words) < 0.7 * ew:
            out.append(("câu nén", f"{len(words)} từ Việt / {ew} từ EN: kiểm thiếu ý, thiếu chủ ngữ"))
    return out


def fit_newlines(src, vi):
    """Giu dung xuong dong dau/cuoi cua cau goc."""
    lead = src[:len(src) - len(src.lstrip("\n"))]
    trail = src[len(src.rstrip("\n")):]
    return lead + vi.strip("\n") + trail


# ---------------------------------------------------------------- ghi ban dich

DIR_RE = re.compile(r"([A-Za-z]+)(?:[ \t]+(.*))?$")
DIRECTIVES = {"scene": "scene", "canh": "scene", "term": "term", "thuatngu": "term",
              "pair": "pair", "xungho": "pair", "voice": "voice", "giong": "voice", "bao": "bao", "phieu": "bao"}


class Payload:
    def __init__(self):
        self.entries = collections.OrderedDict()
        self.scenes = collections.OrderedDict()
        self.terms, self.pairs, self.voices, self.baos = [], [], [], []
        self.dups, self.problems = [], []
        self.listeners, self.gop = {}, set()


def parse_payload(text):
    pl = Payload()
    cur = None

    def close():
        if cur is None:
            return
        body = list(cur["lines"])
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()
        if cur["t"] == "e":
            if cur["id"] in pl.entries:
                pl.dups.append(cur["id"])
            txt = re.sub(r"[ \t]*⏎[ \t]*", "\n", "\n".join(body))  # ky hieu xuong dong in boi one_line -> xuong dong that
            txt = re.sub("─+", "—", re.sub(r"…\.+", "…", txt))  # dau ve khung va '….' chep tu goc
            pl.entries[cur["id"]] = txt
            if txt.strip() == GOP_BODY:
                pl.gop.add(cur["id"])
            else:
                pl.gop.discard(cur["id"])
            if cur.get("lis"):
                pl.listeners[cur["id"]] = cur["lis"]
        else:
            pl.scenes[cur["id"]] = (" ".join(x.strip() for x in body if x.strip()), cur["prio"], cur.get("loai"))

    for line in text.split("\n"):
        if line.startswith("@@"):
            body = line[2:]
            m = DIR_RE.match(body)
            d = DIRECTIVES.get(m.group(1).lower()) if m else None
            rest = (m.group(2) or "").strip() if m else ""
            if d is None:
                close()
                tok = body.strip().split()
                eid = tok[0].split("·")[0].strip() if tok else ""
                if not eid:
                    pl.problems.append("dòng '@@' thiếu id")
                    cur = None
                    continue
                lm = re.search(r"(?:^|\s)>\s*(\S.*?)\s*$", body)
                cur = {"t": "e", "id": eid, "lines": [], "lis": lm.group(1) if lm else None}
            elif d == "scene":
                close()
                prio, loai = None, None
                lm = re.search(r"(?:^|\s)loai=(\S+)", rest)
                if lm:
                    loai = lm.group(1)
                    rest = (rest[:lm.start()] + " " + rest[lm.end():]).strip()
                if rest.endswith("!"):
                    prio, rest = "y", rest[:-1].strip()
                elif rest.endswith(" -") or rest == "-":
                    prio, rest = "", rest[:-1].strip()
                if not rest:
                    pl.problems.append("@@scene thiếu mã cảnh")
                    cur = None
                    continue
                cur = {"t": "s", "id": rest, "prio": prio, "loai": loai, "lines": []}
            else:
                close()
                cur = None
                if d == "bao":
                    if rest:
                        pl.baos.append(rest)
                    else:
                        pl.problems.append("@@bao trống")
                    continue
                if d == "term" and "|" not in rest and "=" in rest:
                    rest = rest.replace("=", "|", 1)   # nhan ca dang "goc = viet"
                fields = [x.strip() for x in rest.split("|")]
                {"term": pl.terms, "pair": pl.pairs, "voice": pl.voices}[d].append(fields)
            continue
        if cur is None:
            if line.strip() and not line.startswith("#>"):
                pl.problems.append(f"dòng nằm ngoài mục: {line[:40]}")
            continue
        if line.startswith("#>"):
            continue
        cur["lines"].append(line)
    close()
    return pl


def upsert(path, cols, keys, new_rows):
    rows = read_tsv(path, cols)
    index = {tuple(r[k] for k in keys): r for r in rows}
    added = updated = 0
    for nr in new_rows:
        k = tuple(nr.get(x, "") for x in keys)
        if k in index:
            r = index[k]
            changed = False
            for c in cols:
                if c in nr and nr[c] is not None and (nr[c] or c in nr.get("_clear", ())) and nr[c] != r.get(c):
                    r[c] = nr[c]
                    changed = True
            updated += changed
        else:
            r = {c: (nr.get(c) or "") for c in cols}
            rows.append(r)
            index[k] = r
            added += 1
    if added or updated:
        write_tsv(path, cols, rows)
    return added, updated


def add_terms(ctx, term_rows):
    """Them thuat ngu moi; khong doi nghia thuat ngu da co (doi nghia: term change)."""
    msgs, ok_rows = [], []
    existing = {r["src"]: r for r in ctx.gloss if r["src"]}
    seen = {}
    for t in term_rows:
        t = {c: clean_cell(t.get(c, "")) for c in GLOSS_COLS}
        if not t["src"] or not t["vi"]:
            msgs.append(f"thuật ngữ thiếu src/vi: {t['src'] or t['vi']}")
            continue
        if t["src"] in seen:
            if seen[t["src"]] != t["vi"]:
                msgs.append(f"'{t['src']}' lặp trong cùng lần nhập với nghĩa khác ('{seen[t['src']]}' / '{t['vi']}') — giữ nghĩa đầu")
            continue
        seen[t["src"]] = t["vi"]
        old = existing.get(t["src"])
        if old and old["vi"] and old["vi"] != t["vi"]:
            msgs.append(f"'{t['src']}' đã là '{old['vi']}' — muốn đổi sang '{t['vi']}' thì dùng: vgk.py term change")
            continue
        if old and t["forbid"]:
            t["forbid"] = ";".join(uniq(split_list(old["forbid"]) + split_list(t["forbid"])))
        ok_rows.append(t)
    a, u = upsert(p(F_GLOSS), GLOSS_COLS, ["src"], ok_rows)
    return a, u, msgs


def phieu_rows():
    return read_tsv(p(F_PHIEU), PHIEU_COLS)


def phieu_open(rows=None):
    return [r for r in (rows if rows is not None else phieu_rows()) if r["trang_thai"] != "đóng"]


def phieu_add(ctx, texts):
    """@@bao [~N.k|id] noi dung -> phieu.tsv (trang thai mo) cho phien chinh."""
    rows = phieu_rows()
    n = max([int(r["n"]) for r in rows if r["n"].isdigit()] + [0])
    t = now()
    bo = getattr(ctx, "batch_of", None) or {}
    for txt in texts:
        tok, _, rest = txt.strip().partition(" ")
        tok = tok.strip().rstrip("|:").strip()
        eid = resolve_one(ctx, tok) if ALIAS_RE.match(tok) else (tok if tok in ctx.src else None)
        body = rest.strip().lstrip("|:").strip() if eid else txt.strip()
        n += 1
        rows.append({"n": str(n), "time": t, "lo": str(bo.get(eid, "")) if eid else "", "id": eid or "",
                     "noi_dung": body, "trang_thai": "mở", "tra_loi": ""})
    write_tsv(p(F_PHIEU), PHIEU_COLS, rows)
    return len(texts)


def apply_directives(ctx, pl):
    out, warn = [], []
    if pl.scenes:
        rows = []
        have = {k for k, r in ctx.scenes.items() if (r.get("summary") or "").strip()}
        for k, (summ, prio, loai) in pl.scenes.items():
            if not summ and prio is None and not loai:
                warn.append(f"@@scene {k} không có nội dung")
                continue
            if k in have:
                warn.append(f"@@scene {k}: cảnh đã có tóm tắt, không đổi (sửa bằng 'vgk.py scene set' ở phiên chính)")
                continue
            r = {"scene": k, "summary": summ}
            if prio is not None:
                r["priority"] = prio
                r["_clear"] = ("priority",)
            if loai:
                if loai not in SCENE_LOAI:
                    warn.append(f"@@scene {k}: loai '{loai}' lạ (dùng: {', '.join(SCENE_LOAI)})")
                r["loai"] = loai
            rows.append(r)
        a, u = upsert(p(F_SCENE), SCENE_COLS, ["scene"], rows)
        out.append(f"tóm tắt cảnh +{a}/sửa {u}")
    if pl.terms:
        rows = []
        for f in pl.terms:
            f = f + [""] * (5 - len(f))
            rows.append({"src": f[0], "vi": f[1], "type": f[2], "note": f[3], "forbid": f[4]})
        a, u, msgs = add_terms(ctx, rows)
        warn += msgs
        out.append(f"thuật ngữ +{a}/sửa {u}")
    if pl.pairs:
        rows = []
        for f in pl.pairs:
            f = f + [""] * (5 - len(f))
            if not (f[0] and f[2] and f[3]):
                warn.append(f"@@pair thiếu cột: {' | '.join(f)}")
                continue
            key = (f[0], f[1] or "*")
            if key in {(r["speaker"], r["listener"]) for r in ctx.pairs}:
                warn.append(f"@@pair {key[0]} → {key[1]}: đã có dòng xưng hô, không đổi (sửa bằng 'vgk.py pair set' ở phiên chính)")
                continue
            if MAYTAO_RE.search(f[2] + " " + f[3]):
                warn.append(f"@@pair {key[0]} → {key[1]}: tao/mày chỉ phiên chính đặt được bằng 'vgk.py pair set'")
                continue
            g = gioi_of(ctx.voice_for(f[0]))
            sai = xung_gioi_sai(f[2], g)
            if sai:
                warn.append(f"@@pair {key[0]} → {key[1]}: xưng '{'/'.join(sai)}' trái giới tính trong hồ sơ ({g}), không ghi")
                continue
            rows.append({"speaker": f[0], "listener": f[1] or "*", "tu_canh": "", "xung": f[2], "goi": f[3], "note": f[4]})
        a, u = upsert(p(F_PAIR), PAIR_COLS, ["speaker", "listener", "tu_canh"], rows)
        out.append(f"xưng hô +{a}/sửa {u}")
    if pl.voices:
        rows = []
        for f in pl.voices:
            f = f + [""] * (3 - len(f))
            if not (f[0] and f[1]):
                warn.append(f"@@voice thiếu cột: {' | '.join(f)}")
                continue
            if f[0] in {r["speaker"] for r in ctx.voices}:
                warn.append(f"@@voice {f[0]}: đã có giọng, không đổi (sửa bằng 'vgk.py voice' ở phiên chính)")
                continue
            rows.append({"speaker": f[0], "tu_canh": "", "giong": f[1], "mau": f[2]})
        a, u = upsert(p(F_VOICE), VOICE_COLS, ["speaker", "tu_canh"], rows)
        out.append(f"giọng +{a}/sửa {u}")
    if pl.baos:
        k = phieu_add(ctx, pl.baos)
        out.append(f"phiếu báo +{k} (phiên chính đọc khi đọc chương)")
    known = {e.get("speaker") for e in ctx.src.values() if e.get("speaker")}
    for f in pl.pairs + pl.voices:
        if f and f[0] and f[0] != "*" and known and f[0] not in known:
            warn.append(f"người nói '{f[0]}' không có trong src.jsonl — dùng tên gốc như trong next (vd: {next(iter(known))})")
    ctx.reload_tables()
    return out, warn


def resolve_aliases(ctx, entries):
    """'~N.k' (in boi next) -> id that. Chi hop le khi lo chua bi chia lai."""
    out, bad = collections.OrderedDict(), []
    al = ctx.state.get("alias", {})
    for k, v in entries.items():
        m = ALIAS_RE.match(k)
        if not m:
            out[k] = v
            continue
        rec = al.get(m.group(1))
        idx = int(m.group(2))
        if not rec or rec.get("sig") != ctx.sig or not (1 <= idx <= len(rec.get("ids", []))):
            bad.append((k, f"không hiểu mã tắt {k} (lô đã chia lại hoặc chưa in) — chạy lại: vgk.py next --batch {m.group(1)}"))
            continue
        out[rec["ids"][idx - 1]] = v
    return out, bad


def bible_loop_lines(ctx):
    """Dong trang thai vong phan hoi: phieu mo, cau can sua, doc chuong."""
    st, out = ctx.state, []
    nph = len(phieu_open())
    if nph:
        out.append(f"- Phiếu báo đang mở: {nph} (vgk.py phieu)")
    sua = st.get("sua") or {}
    if sua:
        out.append(f"- Câu cần sửa: {len(sua)} (vgk.py sua next)")
    ch = st.get("chuong") or {}
    if ch.get("runs"):
        out.append(f"- Đọc chương: {ch['runs']} lần, gần nhất {ch.get('time', '?')} (tới câu thoại thứ {ch.get('upto', 0)})")
    return out


def update_handoff(ctx):
    path = p(F_HANDOFF)
    if not os.path.exists(path):
        return
    pr = progress(ctx)
    st = ctx.state
    nx = pr["next"]
    lines = [
        "<!-- vgk:trang-thai -->",
        f"- Cập nhật: {now()} (vgk {VERSION})",
        f"- Tiến độ: {fmt_n(pr['done'])}/{fmt_n(pr['needs'])} câu cần dịch ({fmt_pct(pr['done'], pr['needs'])})"
        f" · tự động {fmt_n(pr['auto'])} · trùng {fmt_n(pr['dup'])} · giữ nguyên (vị thành niên) {fmt_n(pr['minor'])}"
        + (f" · gốc đã đổi cần dịch lại {fmt_n(pr['stale'])}" if pr["stale"] else ""),
        f"- Lô: {pr['bdone']}/{pr['batches']} xong"
        + (f" · kế tiếp: lô {nx[0]['n']} (còn {nx[1]} câu)" if nx else " · đã dịch hết, chạy check"),
    ]
    if st.get("last_write"):
        lines.append(f"- Lần ghi cuối: {st['last_write']} · lô {st.get('last_batch', '?')} · id {st.get('last_id', '?')}")
    pol = st.get("polish") or {}
    if pol.get("done"):
        nd = sum(1 for b in ctx.batches if b["cls"] == "dialogue")
        lines.append(f"- Chuốt lại: {len(pol['done'])}/{nd} lô thoại")
    lines += bible_loop_lines(ctx)
    q = (st.get("qa") or {}).get("last")
    if q:
        lines.append(f"- Cổng QA gần nhất: {q}")
    ds = st.get("dongbo") or {}
    if ds.get("last"):
        lines.append(f"- Lần ghi về máy gần nhất: {ds['last']}")
    lines.append("- Làm tiếp: `vgk.py status` rồi `vgk.py next` (chạy trong WORK)")
    lines.append("<!-- /vgk:trang-thai -->")
    block = "\n".join(lines)
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    m = re.search(r"<!-- vgk:trang-thai -->.*?<!-- /vgk:trang-thai -->", text, re.S)
    text = text[:m.start()] + block + text[m.end():] if m else text.rstrip("\n") + "\n\n" + block + "\n"
    atomic_write(path, text)


NOFLAG_CATS = {"quá dài", "quá số dòng", "phụ đề quá nhanh"}


def emotion_missing(ctx, e):
    """Canh thoai can 'Cam xuc:' (require_emotion) ma tom tat chua co."""
    if not (ctx.cfg["require_emotion"] and e["kind"] == "dialogue" and e.get("scene")):
        return False
    r = ctx.scenes.get(e["scene"])
    return not r or "cảm xúc:" not in (r["summary"] or "").lower()


def commit(ctx, entries, label, force=(), dry=False, quiet_ok=False, pre_bad=(), listeners=None, gop=()):
    """Kiem tra va ghi ban dich. Ghi muc hop le, tra lai muc loi."""
    force = set(force)
    listeners = listeners or {}
    gop = set(gop)
    ok, bad, warns = collections.OrderedDict(), list(pre_bad), []
    scene_missing = collections.Counter()
    lap_auto = collections.OrderedDict()
    for eid, vi in entries.items():
        if eid not in ctx.src:
            bad.append((eid, "id không có trong src"))
            continue
        if eid in ctx.minor_all:
            bad.append((eid, "thuộc minor_ids — giữ nguyên, không dịch"))
            continue
        e = ctx.src[eid]
        if emotion_missing(ctx, e):
            bad.append((eid, f"cảnh {e['scene']} chưa có tóm tắt kèm 'Cảm xúc:' → thêm khối '@@scene {e['scene']}'"))
            continue
        if eid in gop:
            errs = validate_gop(ctx, eid)
            if errs:
                bad.append((eid, "; ".join(f"{c}: {m}" for c, m in errs)))
                continue
            ok[eid] = ""
            continue
        vi = norm_dau(fit_newlines(e["src"], unicodedata.normalize("NFC", vi)))
        errs, ws = validate(ctx, eid, vi, force=eid in force)
        pe, pw = pair_lint(ctx, eid, vi, listeners.get(eid))
        if eid not in force:
            errs += pe
        if errs:
            bad.append((eid, "; ".join(f"{c}: {m}" for c, m in errs)))
            continue
        if (ctx.cfg["require_scene_summary"] and e["kind"] == "dialogue" and e.get("scene")
                and e["scene"] not in ctx.scenes):
            scene_missing[e["scene"]] += 1
        sw = style_warns(ctx, eid, vi)
        sat = [m for c, m in sw if c == "dịch sát"]
        if sat and eid not in force:
            bad.append((eid, "dịch sát (viết lại câu; cố ý giữ thì --force): " + "; ".join(sat)))
            continue
        ok[eid] = vi
        for c, m in ws + pw + sw:
            warns.append((eid, f"{c}: {m}"))
    touched = sorted(uniq(ctx.batch_of[i] for i in ok if i in ctx.batch_of))
    if ok and not dry:
        t = now()

        def rec(i, v):
            r = {"id": i, "vi": v, "h": src_hash(ctx.src[i]["src"]), "t": t}
            lis = listeners.get(i) or (ctx.trx.get(i) or {}).get("l")   # ghi lai cau (sua, chuot) giu nguoi nghe cu
            if lis:
                r["l"] = lis
            if i in gop:
                r["g"] = 1
            return json.dumps(r, ensure_ascii=False) + "\n"
        append_text(p(F_TR), "".join(rec(i, v) for i, v in ok.items()))
        ctx.tr.update(ok)
        for i in ok:
            ctx.trh[i] = src_hash(ctx.src[i]["src"])
            ctx.stale.discard(i)
            x = dict(ctx.trx.get(i) or {})
            x.pop("g", None)
            if listeners.get(i):
                x["l"] = listeners[i]
            if i in gop:
                x["g"] = 1
            if x:
                ctx.trx[i] = x
            else:
                ctx.trx.pop(i, None)
        if ctx.laps():
            for i, v in ok.items():
                if i in gop or not v:
                    continue
                k = ctx.rep_of.get(ctx.canon_of.get(i, i), i)
                for r in ctx.laps().get(k, ()):
                    if (r != k and r not in ok and r not in lap_auto and r not in ctx.minor_all and not ctx.done(r)
                            and lap_tu_chep(ctx, r, v)):
                        lap_auto[r] = (v, i)
        if lap_auto:
            append_text(p(F_TR), "".join(json.dumps({"id": r, "vi": v, "h": src_hash(ctx.src[r]["src"]), "t": t, "lap": i},
                                                    ensure_ascii=False) + "\n" for r, (v, i) in lap_auto.items()))
            for r, (v, i) in lap_auto.items():
                ctx.tr[r] = v
                ctx.trh[r] = src_hash(ctx.src[r]["src"])
                ctx.stale.discard(r)
        st = ctx.state
        st["last_write"] = t
        st["last_id"] = list(ok)[-1]
        if touched:
            st["last_batch"] = touched[-1]
        if force & set(ok):
            st["force"] = sorted(set(st.get("force", [])) | (force & set(ok)))
        fl = st.setdefault("flags", {})
        for i in ok:
            fl.pop(i, None)
        sua = st.get("sua") or {}
        for i in ok:
            sua.pop(i, None)
        for eid, m in warns:
            cat = m.partition(": ")[0]
            if cat not in NOFLAG_CATS:
                fl[eid] = cat
        st["writes"] = st.get("writes", 0) + 1
        save_state(st)
        append_text(p(F_LOG), f"- {t} {label}: ghi {len(ok)}" + (f" (+{len(lap_auto)} câu lặp tự chép)" if lap_auto else "")
                    + f", lỗi {len(bad)}, cảnh báo {len(warns)}"
                    + (f"; lô {', '.join(map(str, touched[:20]))}" if touched else "") + "\n")
        update_handoff(ctx)
    head = "THỬ (không ghi)" if dry else "Ghi"
    done_b, open_b = [], []
    for n in touched:
        pend = len(ctx.batch_pending(ctx.batches[n - 1]))
        (open_b if pend else done_b).append((n, pend))
    if len(touched) <= 6:
        bstat = [f"lô {n} xong" for n, _ in done_b] + [f"lô {n} còn {k}" for n, k in open_b]
    else:
        bstat = [f"{len(done_b)} lô xong"] + ([f"{len(open_b)} lô còn dở (vd lô {open_b[0][0]})"] if open_b else [])
    print(f"{head}: {len(ok)}/{len(entries) + len(pre_bad)} mục · lỗi {len(bad)} · cảnh báo {len(warns)}"
          + (" · " + ", ".join(bstat) if bstat else ""))
    if lap_auto:
        print(f"Câu lặp ở cảnh khác: tự chép {len(lap_auto)} câu (không có xưng hô): "
              + ", ".join(list(lap_auto)[:8]) + (" …" if len(lap_auto) > 8 else ""))
    if bad:
        print("LỖI (chưa ghi — sửa và chỉ gửi lại các mục này):")
        for eid, m in bad[:40]:
            print(f"  {eid}: {m}")
        if len(bad) > 40:
            print(f"  … và {len(bad) - 40} mục khác")
    if warns:
        groups = collections.OrderedDict()
        for eid, m in warns:
            cat, _, detail = m.partition(": ")
            groups.setdefault(cat, []).append(f"{eid} {detail}")
        if len(warns) <= 30:
            print("CẢNH BÁO (đã ghi; đọc hết, sửa câu nào thật là lỗi):")
            for cat, items in groups.items():
                print(f"  {cat}: {len(items)} — " + "; ".join(items))
        else:
            rep = os.path.join("reports", f"write-{stamp()}.txt")
            os.makedirs(p("reports"), exist_ok=True)
            atomic_write(p(rep), "\n".join(f"{cat}\t{it}" for cat, items in groups.items() for it in items) + "\n")
            print(f"CẢNH BÁO (đã ghi; {len(warns)} cái, đủ chi tiết ở {rep} — đọc hết tệp đó):")
            for cat, items in groups.items():
                print(f"  {cat}: {len(items)} — " + "; ".join(items[:4]) + (" …" if len(items) > 4 else ""))
    if scene_missing:
        names = [f"{s} ({n} câu)" for s, n in scene_missing.items()]
        print("CẢNH CHƯA CÓ TÓM TẮT: " + ", ".join(names[:8]) + (f" … ({len(names)} cảnh)" if len(names) > 8 else "")
              + " → thêm khối '@@scene <mã>' ở lần ghi tới")
    if not dry and ok and not quiet_ok:
        pr = progress(ctx)
        nx = pr["next"]
        print(f"Tiến độ: {fmt_n(pr['done'])}/{fmt_n(pr['needs'])} ({fmt_pct(pr['done'], pr['needs'])})"
              + (f" · kế tiếp: lô {nx[0]['n']}" if nx else " · đã dịch hết → vgk.py check"))
    return ok, bad, warns


def progress(ctx):
    needs = ctx.needs()
    done = sum(1 for r in needs if ctx.done(r))
    stale = sum(1 for r in needs if not ctx.done(r) and ctx.eff(r) is not None)
    dup = sum(len(v) for v in ctx.plan.get("groups", {}).values())
    bdone, nxt = 0, None
    for b in ctx.batches:
        pend = ctx.batch_pending(b)
        if not pend:
            bdone += 1
        elif nxt is None:
            nxt = (b, len(pend))
    return {"total": len(ctx.src), "auto": len(ctx.auto), "dup": dup, "minor": len(ctx.minor_all),
            "needs": len(needs), "done": done, "stale": stale, "batches": len(ctx.batches), "bdone": bdone, "next": nxt}


# ---------------------------------------------------------------- mau tep

HANDOFF_TMPL = """# HANDOFF — {NAME}

> Phiên mới: đọc tệp này, chạy `vgk.py status`, rồi đọc `references/quy-tac-dich.md` (bible chung), `sotay.md` và mục Quy tắc riêng của game dưới đây. Không dựa vào trí nhớ hội thoại.

## Đường dẫn
- Game (Windows):
- Game (shell máy, nếu có):
- WORK trên máy:
- Chế độ: có shell máy / không shell (WORK chép lên cloud, ghi về máy sau mỗi dải lô và khi xong)

## Việc tồn đọng
-

## Khôi phục môi trường (lệnh)
- Trích lại:
- Build patch:
- Kiểm adapter (khứ hồi):
- Kiểm đủ (quét sót trước khi dịch, quét bản đã vá):

## Kết quả khảo sát
- Engine / phiên bản:
- Văn bản nằm ở:
- Cơ chế chọn ngôn ngữ:
- Font / glyph tiếng Việt:
- Code đặt cỡ chữ hoặc khung theo độ dài:
- Ảnh có chữ:
- Tệp không đọc được / chữ nằm trong mã (cần bản vá đánh dấu?):
- Bản EN (chính thức do người dịch / cộng đồng / máy) → en_mode:
- Rủi ro khả thi:

## Chính sách tên (chốt trước lô đầu)
| Loại | Cách xử lý | Ví dụ |
|---|---|---|

## Quy tắc riêng của game
-

## Lỗi đã gặp & điều phải tránh
-

## Trạng thái (vgk tự cập nhật — không sửa tay)
<!-- vgk:trang-thai -->
<!-- /vgk:trang-thai -->
"""

NOTES_TMPL = """# Ghi chú dịch — {NAME}

Mọi dữ kiện về game ghi kèm căn cứ: id câu thoại hoặc đường link. Chưa có căn cứ thì ghi "(chưa xác minh)".

## Game, tác giả, cộng đồng
-

## Chủ đề, không khí, giọng văn tác giả
-

## Nhân vật (sự thật cả truyện, kèm căn cứ — chỉ Opus đọc; người dịch thấy hồ sơ theo mốc trong giong.tsv)
-

## Bí mật và mốc lộ (điều gì → lộ ở cảnh/id nào; tên thật ghi lo_tu trong glossary)
-

## Quyết định dịch
- Kính ngữ (-san, senpai…):
- Xưng hô đặc biệt:
- Thể loại / văn phong:

## NEO (tối đa 4 dòng luật riêng của game, vgk in kèm mỗi lô; mỗi dòng bắt đầu bằng "- ")
-

## Chơi chữ và câu khó (id → cách xử lý)
-

## Bản EN lệch bản gốc (id → theo gốc vì…)
-

## Điểm chưa xác minh / quyết định tạm
-
"""

SOTAY_TMPL = """# Sổ tay giọng — {NAME}

<!-- Bible riêng: văn phong của game này. Opus giữ, tối đa 60 dòng; người dịch đọc khi bắt đầu phiên,
     vgk báo khi tệp đổi. Câu mẫu lấy từ chính bản dịch, sau mỗi lần đọc chương thay câu kém bằng câu hay hơn.
     Không ghi điều người đọc chưa biết (bí mật, mốc lộ). Không chép lại bible chung. -->

## Văn phong
- Lời kể:
- Mức Hán Việt:
- Nhịp câu, độ dài:

## Mức 18+ (chỉ game 18+)
- Độ nóng: đúng như bản gốc, lời gợi cảm tự nhiên, không nói tránh, không thay bằng từ y khoa.
- Cách gọi bộ phận, hành động:

## Câu mẫu hay (từ bản dịch, ghi id)
-

## Tránh
-
"""

LESSONS_TMPL = """# Kinh nghiệm chung — mọi game

Mỗi phiên đọc tệp này khi bắt đầu. Khi xong một game, thêm tối đa 5 dòng: lỗi lặp lại, mẹo engine, quy tắc dịch rút ra.
Ghi ở mức "loại lỗi", có ngày và tên game. Gộp, rút gọn khi tệp dài quá 150 dòng.
Nguồn ban đầu (2026-11): rà soát 4 game đã dịch — một game Unreal (locres/pak), Legend of Mortal (Unity),
một game 18+ RPG Maker (plugins.js), AI: The Somnium Files – nirvanA Initiative (Unity, msgpack).

## Lỗi lặp lại và cách tránh
- Glossary thiếu lúc đầu → thuật ngữ trôi giữa các lô, phải sửa ngược bằng sed nhiều lần, ~27% lệnh chỉ để tra lại thuật ngữ. Tránh: trích toàn bộ tên từ dữ liệu game vào glossary trước lô thoại đầu; đổi thuật ngữ bằng `vgk.py term change`.
- Chính sách tên (giữ EN hay dịch) chốt giữa chừng → làm lại. Tránh: chốt cho từng loại ngay ở bible.
- Nhân vật phụ rơi về mặc định "ta – ngươi" nghe lạnh (vd bà cụ với cháu). Tránh: bảng kiểu người trong lap-bible.md.
- Phần UI/tóm tắt dịch không đối chiếu glossary → cùng một tên hai cách (So/Sejima). Tránh: glossary có cột forbid; `vgk.py check` trước khi giao.
- Công cụ in cắt dòng → phải in lại; gõ lại câu gốc làm khóa → tốn token đầu ra. Tránh: `vgk.py next` in đủ, ghi theo mã tắt ~lô.số.
- Sai số mã điều khiển (\\N[n]), ⏎, thẻ <color> lặp nhiều lần. Tránh: `vgk.py write` tự kiểm từng mục, chỉ gửi lại mục lỗi.
- Chép tệp về máy dính bản cũ do cache theo đường dẫn; hai phiên ghi đè tệp của nhau. Tránh: mỗi lần chép một tên mới có giờ + so `vgk.py hash`; báo cáo đặt tên theo phiên.
- Mất kết nối / nén ngữ cảnh giữa lô → dựng lại trạng thái tốn lượt. Tránh: checkpoint tự động trong HANDOFF (vgk).
- Test giao diện nhiều vòng không trúng nguyên nhân (code tự đặt cỡ chữ theo độ dài tên). Tránh: đọc code tìm chỗ đặt cỡ chữ/khung trước, sửa tĩnh, test 1 lượt.
- Báo "xong" khi chưa xong; báo câu giữ nguyên mà không nói lý do → người dùng phải hỏi lại. Tránh: quy tắc báo cáo trong SKILL.md.

## Engine
- Unity (Legend of Mortal): font TMP cần glyph tiếng Việt; Best Fit; có code tự đặt cỡ chữ theo độ dài chuỗi.
- Unity (Somnium nirvanA): dữ liệu msgpack/lz4 + ZeroFormatter; tên người nói nằm trong tệp .code; khớp ⏎ theo bản EN thì hết lỗi xuống dòng.
- Unreal: .locres v3 + .pak v11; tên người nói lấy từ DataTable; phải thêm glyph tiếng Việt vào các font SE.
- RPG Maker 18+: ngoài data/*.json còn chữ trong plugins.js, chuỗi JS và ảnh (tem Completed/Failed); quét hết ở bước khảo sát.

## Quy tắc dịch rút ra
- Chơi chữ: làm lại cơ chế đùa bằng tiếng Việt (vd "Enda Chán-ma", "ba mươi sáu kế, chuồn là thượng sách") thay vì dịch nghĩa.
- EN lệch JA về ý → theo JA (vd câu "con đường luôn nối dài từ quá khứ" bị EN bỏ mất).
- Thoại tình cảm làm kỹ ngay lần đầu (một game phải sửa lại 241 dòng).
- Cảnh H: các dòng rên liên tiếp dễ lặp một công thức → bám khác biệt từng câu gốc.
"""

BAT_INSTALL = r"""@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
set "GAME=%~1"
if not defined GAME if exist "game_path.txt" set /p GAME=<"game_path.txt"
if not defined GAME goto :nogame
if not exist "%GAME%\" goto :nogame
if not exist "manifest_sha.txt" goto :noman
where certutil >nul 2>&1 || goto :nocert
set "BK=%GAME%\_viethoa_backup"
set "LOG=%~dp0cai_viethoa_log.txt"
>"%LOG%" echo CAI_VIETHOA
set /a NUPD=0, NMISS=0, NBADBK=0, NNEW=0, NSAME=0, NOK=0, NPREV=0
rem Luot 1: kiem het truoc, chua chep gi
for /f "usebackq tokens=1,2,3 delims=|" %%A in ("manifest_sha.txt") do (
  call :check "%%A" "%%B" "%%C"
  if defined UPD >>"%LOG%" echo(khac ban goc luc dong goi: %%A
  if defined MISS >>"%LOG%" echo(khong thay tep goc: %%A
  if defined BADBK >>"%LOG%" echo(ban sao luu khong khop ban goc cua ban Viet hoa nay: %%A
)
if not "%NMISS%"=="0" goto :missing
if not "%NUPD%"=="0" goto :updated
if not "%NBADBK%"=="0" goto :badbk
if not exist "%BK%\" mkdir "%BK%"
set "ERR="
rem Luot 2: sao luu ban goc roi chep; loi o tep nao thi dung ngay o tep do
for /f "usebackq tokens=1,2,3 delims=|" %%A in ("manifest_sha.txt") do (
  call :install "%%A" "%%B" "%%C"
  if defined ERRNOW >>"%LOG%" echo(LOI khi chep: %%A
)
if defined ERR goto :fail
echo.
echo Da cai ban Viet hoa: %NOK% tep thay ban goc, %NPREV% tep thay ban Viet hoa cu, %NNEW% tep moi, %NSAME% tep da dung san.
echo Go bo: chay GO_VIETHOA.bat
pause
exit /b 0

:check
set "REL=%~1"
set "GOC=%~2"
set "PSH=%~3"
set "UPD="
set "MISS="
set "BADBK="
if not defined REL exit /b 0
set "REL=%REL:/=\%"
if not exist "%GAME%\%REL%" goto :check_absent
call :sha "%GAME%\%REL%"
if /i "%H%"=="%PSH%" goto :check_same
if not "%GOC%"=="-" if /i "%H%"=="%GOC%" goto :check_ok
set "PREV="
if exist "%BK%\_installed\%REL%.sha" set /p PREV=<"%BK%\_installed\%REL%.sha"
if defined PREV if /i "%H%"=="%PREV%" goto :check_prev
set "UPD=1"
set /a NUPD+=1
exit /b 0
:check_absent
if not "%GOC%"=="-" goto :check_miss
set /a NNEW+=1
exit /b 0
:check_miss
set "MISS=1"
set /a NMISS+=1
exit /b 0
:check_same
set /a NSAME+=1
exit /b 0
:check_ok
set /a NOK+=1
exit /b 0
:check_prev
set /a NPREV+=1
if "%GOC%"=="-" exit /b 0
call :sha "%BK%\%REL%"
if /i "%H%"=="%GOC%" exit /b 0
set "BADBK=1"
set /a NBADBK+=1
exit /b 0

:install
set "ERRNOW="
if defined ERR exit /b 0
set "REL=%~1"
set "GOC=%~2"
set "PSH=%~3"
if not defined REL exit /b 0
set "REL=%REL:/=\%"
if not exist "%GAME%\%REL%" goto :inst_copy
call :sha "%GAME%\%REL%"
if /i "%H%"=="%PSH%" goto :inst_mark
if "%GOC%"=="-" goto :inst_copy
if /i not "%H%"=="%GOC%" goto :inst_copy
rem Tep dang la ban goc: sao luu. Ban sao luu cu khac noi dung thi giu lai o _cu\<sha>, khong de.
if not exist "%BK%\%REL%" goto :inst_bk
call :sha "%BK%\%REL%"
if /i "%H%"=="%GOC%" goto :inst_copy
set "OLD=%BK%\_cu\%H:~0,16%\%REL%"
if not exist "%OLD%" call :copyto "%BK%\%REL%" "%OLD%"
if defined ERR goto :inst_err
:inst_bk
call :copyto "%GAME%\%REL%" "%BK%\%REL%"
if defined ERR goto :inst_err
call :sha "%BK%\%REL%"
if /i not "%H%"=="%GOC%" goto :inst_err
:inst_copy
call :copyto "files\%REL%" "%GAME%\%REL%"
if defined ERR goto :inst_err
call :sha "%GAME%\%REL%"
if /i not "%H%"=="%PSH%" goto :inst_err
:inst_mark
set "MK=%BK%\_installed\%REL%.sha"
for %%D in ("%MK%") do if not exist "%%~dpD" mkdir "%%~dpD"
>"%MK%" echo %PSH%
exit /b 0
:inst_err
set "ERR=1"
set "ERRNOW=1"
exit /b 0

:copyto
if not exist "%~dp2" mkdir "%~dp2"
copy /y "%~1" "%~2" >nul || set "ERR=1"
exit /b 0

:sha
set "H="
for /f "skip=1 delims=" %%H in ('certutil -hashfile "%~1" SHA256 2^>nul') do if not defined H set "H=%%H"
if defined H set "H=%H: =%"
exit /b 0

:missing
echo Khong thay %NMISS% tep goc cua game trong thu muc da chon (xem cai_viethoa_log.txt).
echo Co the da chon nham thu muc: keo tha dung thu muc game (thu muc co file chay game). Chua chep tep nao.
pause
exit /b 2

:updated
echo Game da cap nhat so voi luc dong goi ban Viet hoa: %NUPD% tep khac ban goc (xem cai_viethoa_log.txt).
echo Can build lai patch cho ban game moi. Chua chep tep nao.
pause
exit /b 2

:badbk
echo Ban Viet hoa nay lam cho phien ban game khac voi ban dang cai: %NBADBK% tep (xem cai_viethoa_log.txt). Chua chep tep nao.
echo Go ban Viet hoa dang cai bang GO_VIETHOA.bat cua ban do, roi cai lai.
pause
exit /b 2

:nogame
echo Khong biet thu muc game. Keo tha thu muc game vao file CAI_VIETHOA.bat, hoac ghi duong dan vao game_path.txt.
pause
exit /b 1

:noman
echo Thieu manifest_sha.txt canh file bat.
pause
exit /b 1

:nocert
echo Khong tim thay lenh certutil cua Windows.
pause
exit /b 1

:fail
echo Co loi khi chep tep (xem cai_viethoa_log.txt). Da dung o tep loi; cac tep da thay van co ban sao luu.
echo Kiem tra quyen ghi trong thu muc game roi chay lai CAI_VIETHOA.bat, hoac chay GO_VIETHOA.bat de go phan da cai.
pause
exit /b 1
"""

BAT_UNINSTALL = r"""@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
set "GAME=%~1"
if not defined GAME if exist "game_path.txt" set /p GAME=<"game_path.txt"
if not defined GAME goto :nogame
if not exist "%GAME%\" goto :nogame
if not exist "manifest_sha.txt" goto :noman
where certutil >nul 2>&1 || goto :nocert
set "BK=%GAME%\_viethoa_backup"
set "LOG=%~dp0go_viethoa_log.txt"
>"%LOG%" echo GO_VIETHOA
set /a NCHG=0, NMISS=0, NNOBK=0, NRES=0, NDEL=0, NDONE=0
rem Luot 1: kiem het truoc, chua doi gi
for /f "usebackq tokens=1,2,3 delims=|" %%A in ("manifest_sha.txt") do (
  call :check "%%A" "%%B" "%%C"
  if defined CHG >>"%LOG%" echo(da bi thay doi sau khi cai: %%A
  if defined MISS >>"%LOG%" echo(khong thay tep: %%A
  if defined NOBK >>"%LOG%" echo(khong co ban sao luu khop ban goc: %%A
)
if not "%NMISS%"=="0" goto :missing
if not "%NCHG%"=="0" goto :changed
if not "%NNOBK%"=="0" goto :nobk
set /a NTODO=NRES+NDEL
if "%NTODO%"=="0" goto :nothing
set "ERR="
rem Luot 2: khoi phuc ban goc, xoa tep moi; loi o tep nao thi dung ngay o tep do
for /f "usebackq tokens=1,2,3 delims=|" %%A in ("manifest_sha.txt") do (
  call :restore "%%A" "%%B" "%%C"
  if defined ERRNOW >>"%LOG%" echo(LOI khi khoi phuc: %%A
)
if defined ERR goto :fail
echo.
echo Da go ban Viet hoa: khoi phuc %NRES% tep goc, xoa %NDEL% tep moi.
pause
exit /b 0

:check
set "REL=%~1"
set "GOC=%~2"
set "PSH=%~3"
set "CHG="
set "MISS="
set "NOBK="
if not defined REL exit /b 0
set "REL=%REL:/=\%"
if not exist "%GAME%\%REL%" goto :check_absent
call :sha "%GAME%\%REL%"
if not "%GOC%"=="-" if /i "%H%"=="%GOC%" goto :check_done
if /i "%H%"=="%PSH%" goto :check_ours
set "PREV="
if exist "%BK%\_installed\%REL%.sha" set /p PREV=<"%BK%\_installed\%REL%.sha"
if defined PREV if /i "%H%"=="%PREV%" goto :check_ours
set "CHG=1"
set /a NCHG+=1
exit /b 0
:check_absent
if "%GOC%"=="-" goto :check_done
set "MISS=1"
set /a NMISS+=1
exit /b 0
:check_done
set /a NDONE+=1
exit /b 0
:check_ours
if "%GOC%"=="-" goto :check_del
if not exist "%BK%\%REL%" goto :check_nobk
call :sha "%BK%\%REL%"
if /i not "%H%"=="%GOC%" goto :check_nobk
set /a NRES+=1
exit /b 0
:check_del
set /a NDEL+=1
exit /b 0
:check_nobk
set "NOBK=1"
set /a NNOBK+=1
exit /b 0

:restore
set "ERRNOW="
if defined ERR exit /b 0
set "REL=%~1"
set "GOC=%~2"
if not defined REL exit /b 0
set "REL=%REL:/=\%"
if not exist "%GAME%\%REL%" exit /b 0
call :sha "%GAME%\%REL%"
if not "%GOC%"=="-" if /i "%H%"=="%GOC%" exit /b 0
if "%GOC%"=="-" goto :restore_new
copy /y "%BK%\%REL%" "%GAME%\%REL%" >nul || goto :restore_err
call :sha "%GAME%\%REL%"
if /i not "%H%"=="%GOC%" goto :restore_err
goto :restore_mark
:restore_new
del /q "%GAME%\%REL%" >nul 2>&1
if exist "%GAME%\%REL%" goto :restore_err
:restore_mark
if exist "%BK%\_installed\%REL%.sha" del /q "%BK%\_installed\%REL%.sha" >nul 2>&1
exit /b 0
:restore_err
set "ERR=1"
set "ERRNOW=1"
exit /b 0

:delnew
set "DELNOW="
set "REL=%~1"
set "GOC=%~2"
set "PSH=%~3"
if not defined REL exit /b 0
if not "%GOC%"=="-" exit /b 0
set "REL=%REL:/=\%"
if not exist "%GAME%\%REL%" exit /b 0
call :sha "%GAME%\%REL%"
set "OURS="
if /i "%H%"=="%PSH%" set "OURS=1"
set "PREV="
if exist "%BK%\_installed\%REL%.sha" set /p PREV=<"%BK%\_installed\%REL%.sha"
if defined PREV if /i "%H%"=="%PREV%" set "OURS=1"
if not defined OURS exit /b 0
del /q "%GAME%\%REL%" >nul 2>&1
if exist "%GAME%\%REL%" exit /b 0
set "DELNOW=1"
set /a NDEL+=1
if exist "%BK%\_installed\%REL%.sha" del /q "%BK%\_installed\%REL%.sha" >nul 2>&1
exit /b 0

:sha
set "H="
for /f "skip=1 delims=" %%H in ('certutil -hashfile "%~1" SHA256 2^>nul') do if not defined H set "H=%%H"
if defined H set "H=%H: =%"
exit /b 0

:changed
rem Game da doi tep sau khi cai: khong chep ban goc cu de len (co the lech phien ban); chi xoa tep moi van dung la cua ban Viet hoa.
set /a NDEL=0
for /f "usebackq tokens=1,2,3 delims=|" %%A in ("manifest_sha.txt") do (
  call :delnew "%%A" "%%B" "%%C"
  if defined DELNOW >>"%LOG%" echo(da xoa tep moi cua ban Viet hoa: %%A
)
echo Game da cap nhat hoac tep bi doi sau khi cai ban Viet hoa: %NCHG% tep (xem go_viethoa_log.txt).
echo Khong chep lai ban goc cu (co the lech phien ban game). Da xoa %NDEL% tep moi cua ban Viet hoa.
echo De ve ban goc hoan toan, dung chuc nang kiem tra tep cua Steam hoac launcher.
pause
exit /b 2

:missing
echo Khong thay %NMISS% tep cua game trong thu muc da chon (xem go_viethoa_log.txt). Chua doi gi.
echo Co the da chon nham thu muc: keo tha dung thu muc game vao GO_VIETHOA.bat.
pause
exit /b 2

:nobk
echo Thieu ban sao luu khop ban goc: %NNOBK% tep (xem go_viethoa_log.txt). Chua doi gi.
echo Dung chuc nang kiem tra tep cua Steam hoac launcher de ve ban goc.
pause
exit /b 2

:nothing
echo Ban Viet hoa nay da duoc go truoc do: moi tep dang la ban goc. Khong co gi de lam.
pause
exit /b 0

:nogame
echo Khong biet thu muc game. Keo tha thu muc game vao file GO_VIETHOA.bat, hoac ghi duong dan vao game_path.txt.
pause
exit /b 1

:noman
echo Thieu manifest_sha.txt canh file bat.
pause
exit /b 1

:nocert
echo Khong tim thay lenh certutil cua Windows.
pause
exit /b 1

:fail
echo Co loi khi khoi phuc (xem go_viethoa_log.txt). Da dung o tep loi; ban sao luu van con trong _viethoa_backup.
echo Kiem tra quyen ghi trong thu muc game roi chay lai GO_VIETHOA.bat.
pause
exit /b 1
"""

# ---------------------------------------------------------------- lenh

def cmd_init(a):
    os.makedirs(WORK, exist_ok=True)
    for d in DIRS:
        os.makedirs(p(d), exist_ok=True)
    made, kept = [], []

    def mk(name, content, path=None):
        path = path or p(name)
        if os.path.exists(path):
            kept.append(name)
            return
        atomic_write(path, content)
        made.append(name)

    cfg = dict(DEFAULT_CFG)
    for k, v in (("name", a.name), ("slug", a.slug), ("engine", a.engine), ("kind", a.kind), ("source_lang", a.lang),
                 ("the_loai", a.the_loai), ("boi_canh", a.boi_canh), ("en_mode", a.en_mode)):
        if v:
            cfg[k] = v
    if not cfg["slug"] and cfg["name"]:
        cfg["slug"] = slugify(cfg["name"])
    if cfg["kind"] not in ("thuong", "18"):
        die("--kind phải là 'thuong' hoặc '18'")
    if str(cfg["source_lang"]).lower() in LANG_TYPOS:
        die(f"--lang '{cfg['source_lang']}' → dùng '{LANG_TYPOS[str(cfg['source_lang']).lower()]}'")
    for key, allowed in (("the_loai", THE_LOAI), ("boi_canh", BOI_CANH), ("en_mode", EN_MODES)):
        if cfg[key] and cfg[key] not in allowed:
            die(f"--{key.replace('_', '-')} phải là {' | '.join(allowed)}")
    name = cfg["name"] or "?"
    mk(F_GAME, json.dumps({k: v for k, v in cfg.items() if v is not None}, ensure_ascii=False, indent=2) + "\n")
    mk(F_GLOSS, "\t".join(GLOSS_COLS) + "\n")
    mk(F_PAIR, "\t".join(PAIR_COLS) + "\n")
    mk(F_SCENE, "\t".join(SCENE_COLS) + "\n")
    mk(F_VOICE, "\t".join(VOICE_COLS) + "\n")
    mk(F_MINOR, "# Mỗi dòng một id giữ nguyên bản gốc (nội dung tình dục liên quan vị thành niên). Ghi chú: '<id>  # lý do'.\n")
    mk(F_NOTES, NOTES_TMPL.replace("{NAME}", name))
    mk(F_SOTAY, SOTAY_TMPL.replace("{NAME}", name))
    mk(F_HANDOFF, HANDOFF_TMPL.replace("{NAME}", name))
    mk(F_LOG, "# Nhật ký vgk\n")
    lessons = os.path.join(os.path.dirname(os.path.abspath(__file__)), "KINH_NGHIEM.md")
    if not a.no_lessons:
        mk("KINH_NGHIEM.md (chung)", LESSONS_TMPL, path=lessons)
    print("Đã tạo: " + (", ".join(made) if made else "không có gì mới"))
    if kept:
        print("Giữ nguyên (đã có): " + ", ".join(kept))


def cmd_plan(a):
    cfg = load_cfg()
    src = load_src()
    tr, trh, _, _ = load_tr()
    plan, st = build_plan(cfg, src, tr, trh)
    atomic_write(p(F_PLAN), json.dumps(plan, ensure_ascii=False) + "\n")
    print(f"Mục: {fmt_n(st['total'])} · tự động {fmt_n(st['auto'])} · trùng (dịch 1 lần) {fmt_n(st['dup'])} · "
          f"cần dịch {fmt_n(st['need'])} (thoại {fmt_n(st['dlg'])}, ngắn {fmt_n(st['need'] - st['dlg'])})")
    print(f"Lô: {st['batches']} (thoại {st['bd']}, ngắn {st['batches'] - st['bd']})")
    orphan = [i for i in tr if i not in src]
    if orphan:
        print(f"CẢNH BÁO: {len(orphan)} bản dịch có id không còn trong src (vd {', '.join(orphan[:5])})")
    ctx = Ctx(quiet=True)
    if ctx.stale:
        print(f"CẢNH BÁO: {len(ctx.stale)} câu đã dịch nhưng câu gốc đã đổi — sẽ được đưa lại vào lô để dịch lại")
    if os.path.exists(p(F_HANDOFF)):
        update_handoff(ctx)


def fix_dau_text(t):
    """Doi dau kieu Nhat trong ban dich cu: gach dau cau bo; chuoi gach o cuoi dong -> '—'; chuoi gach giua cau -> '…'."""
    out = []
    for ln in t.split("\n"):
        ln = re.sub(r'^(\s*["“「『(]?)\s*[⸺⸻―—]+\s*', r"\1", ln)
        ln = re.sub(r'[⸺⸻―—]{2,}(\s*["”」』)]*\s*)$', r"—\1", ln)
        ln = re.sub(r"[⸺⸻―—]{2,}", "…", ln)
        ln = ln.replace("\u2e3a", "—").replace("\u2e3b", "—").replace("\u2015", "—")
        out.append(ELL_RUN_RE.sub("\u2026", ln))
    return "\n".join(out)


def cmd_fixdau(a):
    """Doi dau kieu Nhat (⸺, ―, '……') trong cac ban dich da co; mac dinh chi xem truoc."""
    ctx = Ctx()
    ent = collections.OrderedDict()
    for eid in ctx.src_order:
        vi = ctx.eff(eid)
        if vi and (re.search("[⸺⸻―]|……|^[\\s\"“「『(]*—", vi, re.M)):
            nv = fix_dau_text(vi)
            if nv != vi:
                ent[eid] = nv
    print(f"{len(ent)} câu cần đổi dấu.")
    for eid in list(ent)[:5]:
        print(f"  {eid}: {one_line(ctx.eff(eid))[:60]} → {one_line(ent[eid])[:60]}")
    if not a.apply:
        print("Xem trước. Thêm --apply để ghi (qua bước kiểm như write).")
        return
    if ent:
        _, bad, _ = commit(ctx, ent, "fix-dau")
        sys.exit(2 if bad else 0)


def cmd_lo(a):
    """Danh sach lo de chia dai cho agent dich: loai, so cau, con lai, uu tien, canh."""
    ctx = Ctx()
    pri = {sc for sc, r in ctx.scenes.items() if r["priority"]}
    print("lô\tloại\tcâu\tcòn\tưu tiên\tcảnh")
    for b in ctx.batches:
        if (a.tu and b["n"] < a.tu) or (a.den and b["n"] > a.den):
            continue
        pend = ctx.batch_pending(b)
        if a.con and not pend:
            continue
        scs = uniq(ctx.src[i].get("scene") for i in b["ids"] if i in ctx.src and ctx.src[i].get("scene"))
        up = "có" if any(sc in pri for sc in scs) else ""
        more = f" …(+{len(scs) - 4})" if len(scs) > 4 else ""
        print(f"{b['n']}\t{'thoại' if b['cls'] == 'dialogue' else 'ngắn'}\t{len(b['ids'])}\t{len(pend)}\t{up}\t"
              + ", ".join(scs[:4]) + more)


def cmd_status(a):
    ctx = Ctx()
    c = ctx.cfg
    pr = progress(ctx)
    kind = "18+" if c["kind"] == "18" else "thường"
    print(f"{c['name'] or '?'} · {c['engine'] or '?'} · {kind} · nguồn {c['source_lang']} · vgk {VERSION}")
    print(f"Kiểu: thể loại {c.get('the_loai') or '?'} · bối cảnh {c.get('boi_canh') or '?'} · EN {c['en_mode']}"
          f" · tóm tắt cảnh {'bật' if c['require_scene_summary'] else 'tắt'}"
          f"{' (kèm Cảm xúc:)' if c['require_emotion'] else ''}")
    nlap = lap_count(ctx)
    print(f"Mục: {fmt_n(pr['total'])} · tự động {fmt_n(pr['auto'])} · trùng {fmt_n(pr['dup'])} · "
          f"giữ nguyên (vị thành niên) {fmt_n(pr['minor'])}"
          + (f" · lặp ở cảnh khác {fmt_n(nlap)} (gợi ý '=' hoặc tự chép)" if nlap else ""))
    print(f"Cần dịch: {fmt_n(pr['needs'])} · đã dịch {fmt_n(pr['done'])} ({fmt_pct(pr['done'], pr['needs'])}) · "
          f"còn {fmt_n(pr['needs'] - pr['done'])}" + (f" (trong đó gốc đã đổi cần dịch lại {fmt_n(pr['stale'])})" if pr["stale"] else ""))
    nx = pr["next"]
    print(f"Lô: {pr['bdone']}/{pr['batches']} xong"
          + (f" · kế tiếp: lô {nx[0]['n']} ({'thoại' if nx[0]['cls'] == 'dialogue' else 'ngắn'}, còn {nx[1]} câu)"
             if nx else " · đã dịch hết → chạy check"))
    miss = set()
    for eid, e in ctx.src.items():
        if e["kind"] == "dialogue" and e.get("scene") and e["scene"] not in ctx.scenes and ctx.eff(eid) is not None:
            miss.add(e["scene"])
    extra = [f"glossary {len(ctx.gloss)}", f"xưng hô {len(ctx.pairs)}", f"giọng {len(ctx.voices)}",
             f"cảnh có tóm tắt {len(ctx.scenes)}"]
    if miss:
        extra.append(f"cảnh đã dịch thiếu tóm tắt {len(miss)}")
    if ctx.tr_bad:
        extra.append(f"tr.jsonl dòng hỏng {ctx.tr_bad}")
    print("Hồ sơ: " + " · ".join(extra))
    st = ctx.state
    if st.get("last_write"):
        print(f"Lần ghi cuối: {st['last_write']} · lô {st.get('last_batch', '?')} · id {st.get('last_id', '?')}")
    pol = st.get("polish") or {}
    if pol.get("done"):
        nd = sum(1 for b in ctx.batches if b["cls"] == "dialogue")
        print(f"Chuốt lại: {len(pol['done'])}/{nd} lô thoại")
    for ln in bible_loop_lines(ctx):
        print(ln[2:])
    q = st.get("qa") or {}
    if q.get("last"):
        print(f"Cổng QA gần nhất: {q['last']}")
    due = qa_due(ctx)
    if due:
        print("CỔNG ĐẾN HẠN: " + "; ".join(due))
    if (st.get("dongbo") or {}).get("last"):
        print(f"Lần ghi về máy gần nhất: {st['dongbo']['last']}")
    if a.handoff:
        update_handoff(ctx)
        print("Đã cập nhật khối trạng thái trong HANDOFF.md")


def ref_dirs(ctx):
    return [ctx.cfg.get("hoso_dir") or "", os.path.join(vgk_dir(), "hoso"),
            os.path.join(vgk_dir(), "..", "references", "hoso"), os.path.join(vgk_dir(), "..", "references")]


def find_ref(ctx, name):
    for d in ref_dirs(ctx):
        f = os.path.normpath(os.path.join(d, name + ".md")) if d else ""
        if f and os.path.isfile(f):
            return f
    return None


def hoso_paths(ctx):
    """Tep ho so dang bat: loi quy-tac-dich, nguon-<lang>, the-loai-<the_loai>."""
    dirs = ref_dirs(ctx)
    names = ["quy-tac-dich", "nguon-" + ctx.cfg["source_lang"]]
    if ctx.cfg.get("the_loai"):
        names.append("the-loai-" + ctx.cfg["the_loai"].replace("_", "-"))
    out = []
    for nm in names:
        for d in dirs:
            f = os.path.normpath(os.path.join(d, nm + ".md")) if d else ""
            if f and os.path.isfile(f):
                out.append(f)
                break
    return out


def neo_section(path):
    """Cac dong '- …' trong muc '## NEO' cua mot tep markdown."""
    lines, on = [], False
    try:
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                s = line.rstrip("\n")
                if s.startswith("## "):
                    on = s[3:].strip().upper().startswith("NEO")
                    continue
                if on and s.lstrip().startswith("- "):
                    lines.append(s.strip()[2:].strip())
    except OSError:
        pass
    return lines


def build_neo(ctx, speakers):
    """Khoi NEO <= NEO_MAX ky tu: luat cot loi cua ho so dang bat + NEO cua game + loi dan mau + cau neo.
    Tra ve (dong, tep luat da doi tu lan next truoc)."""
    files = hoso_paths(ctx)
    notes = p(F_NOTES)
    # Thu tu uu tien khi phai cat cho vua NEO_MAX: luat rieng cua game, cau neo, loi dan mau, roi moi den luat ho so
    # (ho so da doc day du luc mo phien, nen cat phan cuoi it hai nhat).
    game_rules = neo_section(notes) if os.path.exists(notes) else []
    out = [f"  - {x}" for x in game_rules]
    anc = [r for r in read_tsv(p(F_NEO), NEO_COLS) if r["vi"] and r["speaker"] in speakers]
    anc.sort(key=lambda r: 0 if r["nguon"] in ("P5", "F3") else 1)
    pick = []
    for r in anc:
        if len(pick) < 3 and r["speaker"] not in {x["speaker"] for x in pick}:
            pick.append(r)
    for r in anc:
        if len(pick) < 3 and r not in pick:
            pick.append(r)
    out += [f"  - Neo {r['speaker']}: {one_line(r['vi'])}" for r in pick]
    ke = next((v for v in ctx.voices if v["speaker"] == "_ke" and v["mau"]), None)
    if ke:
        out.append(f"  - Lời dẫn mẫu: {one_line(ke['mau'])}")
    rules = list(game_rules)
    for f in files:
        for x in neo_section(f):
            if x not in rules:
                rules.append(x)
                out.append(f"  - {x}")
    res = []
    if out:
        head = "NEO (đọc trước khi dịch lô này):"
        note = "  - (NEO bị cắt cho vừa giới hạn, xem đủ trong tệp hồ sơ)"
        res, total, cut = [head], len(head) + 1, False
        for ln in out:
            if total + len(ln) + 1 > NEO_MAX - len(note) - 1:
                cut = True
                break
            res.append(ln)
            total += len(ln) + 1
        if cut:
            res.append(note)
    cur = {}
    # Nguoi dich doc bible chung (ho so) va so tay giong; de xuat trong KHAU_VI.md khong ap luc dang dich.
    for f in files + [p(F_SOTAY)]:
        if os.path.exists(f):
            cur[os.path.normpath(f)] = file_sha(f)
    if os.path.exists(notes):
        cur[notes] = hashlib.sha256("\n".join(neo_section(notes)).encode("utf-8")).hexdigest()[:16]
    old = ctx.state.get("neo_files")
    changed = [f for f in cur if old is not None and old.get(f) != cur[f]]
    ctx.state["neo_files"] = cur
    return res, changed


def batches_done(ctx):
    dd = ds = 0
    for b in ctx.batches:
        if not ctx.batch_pending(b):
            if b["cls"] == "dialogue":
                dd += 1
            else:
                ds += 1
    return dd, ds


def qa_due(ctx):
    """Cong QA den han theo tien do (dem bang cong cu, khong de model tu nho)."""
    if ctx.plan is None:
        return []
    q = ctx.state.get("qa") or {}
    t2, t3 = q.get("T2") or {}, q.get("T3") or {}
    dd, ds = batches_done(ctx)
    due = []
    dlg_runs = t2.get("dlg_runs", t2.get("runs", 0) if t2.get("done_dlg") else 0)
    need = t2.get("interval", 10) if dlg_runs else 3
    why = []
    dinh_ky = bool(ctx.cfg.get("qa_dinh_ky"))
    if not dinh_ky:
        need = float("inf")
    if dd - t2.get("done_dlg", 0) >= need:
        why.append(f"{dd - t2.get('done_dlg', 0)} lô thoại mới")
    if dinh_ky and ds - t2.get("done_short", 0) >= 3:
        why.append(f"{ds - t2.get('done_short', 0)} lô ngắn mới")
    if why:
        due.append(f"T2 ({', '.join(why)}) → vgk.py qa sample --gate T2")
    need3 = t2.get("interval", 10) if t3.get("runs") else 3
    if dinh_ky and dd >= 3 and dd - t3.get("done_dlg", 0) >= need3:
        due.append(f"T3 ({dd - t3.get('done_dlg', 0)} lô thoại mới) → vgk.py qa sample --gate T3")
    ch = ctx.state.get("chuong") or {}
    new = dlg_done(ctx) - int(ch.get("upto", 0))
    step = int(ctx.cfg.get("doc_chuong_dau" if ch.get("runs", 0) < 3 else "doc_chuong_sau") or 0)
    nph = len(phieu_open())
    lim = int(ctx.cfg.get("phieu_toi_da") or 0)
    if step > 0 and new >= step:
        due.append(f"C đọc chương ({fmt_n(new)} câu thoại mới) → vgk.py doc-chuong (phiên chính)")
    elif lim and nph >= lim:
        due.append(f"C đọc chương sớm ({nph} phiếu báo đang mở) → vgk.py doc-chuong (phiên chính)")
    pr = progress(ctx)
    if pr["needs"] and pr["done"] == pr["needs"] and not (q.get("F2") or {}).get("ok"):
        due.append("F2 (đã dịch hết) → vgk.py qa sample --gate F2")
    return due


def dlg_done(ctx):
    """So cau thoai (dai dien) da dich."""
    return sum(1 for b in ctx.batches if b["cls"] == "dialogue" for r in ctx.batch_reps(b) if ctx.done(r))


def en_selection(ctx, en_arg, b, show):
    mode = ctx.cfg["en_mode"]
    if mode == "none":
        if en_arg:
            print("(en_mode = none: không in EN)")
        return False, set()
    en_all = en_arg == "all" or (en_arg is None and mode == "all")
    en_ids = set()
    if en_arg and en_arg != "all":
        for x in split_list(en_arg, ","):
            m = ALIAS_RE.match(x)
            if m and int(m.group(1)) == b["n"] and 1 <= int(m.group(2)) <= len(show):
                en_ids.add(show[int(m.group(2)) - 1])
            else:
                en_ids.add(x)
    return en_all, en_ids


ADDR_WORDS = {unicodedata.normalize("NFC", w) for w in (
    "tôi tao mày ta ngươi mình cậu tớ anh em chị ông bà cô chú bác cháu con bố mẹ cha má ba ngài nàng chàng "
    "hắn nó y ả gã lão thị họ bạn huynh đệ tỷ tỉ muội thầy thiếp trẫm ạ dạ vâng thưa ừ nhé nha").split()}
LAP_CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af\uf900-\ufaff]")
LAP_WORD_RE = re.compile(r"[^\W\d_]+")


def lap_tu_chep(ctx, eid, vi):
    """Cau lap o canh khac duoc tu chep khi cau goc du dai (>=6 chu Han/kana/Hangul, hoac >=4 tu) va ban dich khong co
    xung ho, kinh ngu hay tu chi nguoi (nhung thu doi theo nguoi nghe). Con lai: next in ban da dich, nguoi dich ghi '='."""
    s = ctx.src[eid]["src"]
    n = len(LAP_CJK_RE.findall(s))
    if n < 6 and (n or len(LAP_WORD_RE.findall(s)) < 4):
        return False
    if getattr(ctx, "_addr_extra", None) is None:
        ex = set()
        for r in ctx.pairs:
            for col in ("xung", "goi"):
                ex.update(w.lower() for w in LAP_WORD_RE.findall(r.get(col) or ""))
        ctx._addr_extra = ex
    words = {w.lower() for w in LAP_WORD_RE.findall(vi)}
    return not (words & (ADDR_WORDS | ctx._addr_extra))


def lap_count(ctx):
    sets = {id(m): m for m in ctx.laps().values()}
    return sum(len(m) - 1 for m in sets.values())


def phien_get(ctx, tag):
    """Phien cua mot agent dich (2.3): nho phan da in de lo sau khong in lai. Giu 8 phien gan nhat."""
    ph = ctx.state.setdefault("phien", {})
    s = ph.get(tag)
    if s is None:
        for k in sorted(ph, key=lambda k: ph[k].get("t", ""))[:-7]:
            ph.pop(k, None)
        s = ph[tag] = {"t": now(), "seen": {}, "last": None}
    return s


def voice_line(v):
    bits = [x for x in (v.get("gioi"), v.get("vai_ve"), v.get("tam_ly")) if x]
    if v.get("giong"):
        bits.append("giọng: " + v["giong"])
    if v.get("mau"):
        bits.append("mẫu: " + v["mau"])
    return f"{v['speaker']}: " + " · ".join(bits)


def pair_line(r):
    return (f"{r['speaker']} → {r['listener'] or '*'}: xưng {r['xung']}, gọi {r['goi']}"
            + (f" ({r['note']})" if r["note"] else ""))


def emit_batch(ctx, b, show, en_all, en_ids, vi_lines=False, phien=None):
    """In mot lo kem ngu canh; luu ma tat ~lo.so cho lan write ke tiep."""
    al = ctx.state.setdefault("alias", {})
    al.pop(str(b["n"]), None)
    al[str(b["n"])] = {"sig": ctx.sig, "ids": show}
    for k in list(al)[:-8]:
        al.pop(k, None)
    ents = [ctx.src[i] for i in show]
    dlg = b["cls"] == "dialogue"
    ses = phien_get(ctx, phien) if phien else None
    seen = ses["seen"] if ses is not None else None
    om = collections.OrderedDict()   # nhom -> so muc khong in lai vi da in o lo truoc trong phien

    def fresh(key, text, group):
        if seen is None:
            return True
        h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
        if seen.get(key) == h:
            om[group] = om.get(group, 0) + 1
            return False
        seen[key] = h
        return True
    reps = ctx.batch_reps(b)
    left = sum(1 for x in ctx.batches if ctx.batch_pending(x))
    print(f"LÔ {b['n']}/{len(ctx.batches)} · {'thoại' if dlg else 'ngắn'} · in {len(show)}/{len(reps)} câu · "
          f"còn {left} lô chưa xong")
    spk = uniq(e.get("speaker") for e in ents if e.get("speaker"))
    neo, changed = build_neo(ctx, set(spk))
    if changed:
        print("LUẬT ĐÃ ĐỔI: đọc lại " + ", ".join(os.path.basename(f) for f in changed))
    if neo and fresh("neo", "\n".join(neo), "NEO"):
        for ln in neo:
            print(ln)
    due = qa_due(ctx)
    if due:
        print("CỔNG ĐẾN HẠN (làm trước khi dịch tiếp): " + "; ".join(due))
    save_state(ctx.state)
    if dlg:
        for s in uniq(e.get("scene") for e in ents if e.get("scene"))[:15]:
            r = ctx.scenes.get(s)
            if r:
                if not fresh("canh:" + s, f"{r['summary']}|{r['priority']}|{r.get('loai')}", "chỉ đạo cảnh"):
                    continue
                tags = [x for x in ("ưu tiên" if r["priority"] else "", r.get("loai") or "") if x]
                print(f"CẢNH {s}{' (' + ', '.join(tags) + ')' if tags else ''}: {r['summary']}")
                if ctx.cfg["require_emotion"] and "cảm xúc:" not in (r["summary"] or "").lower():
                    print(f"CẢNH {s}: THIẾU 'Cảm xúc:' → ghi lại '@@scene {s}' kèm 'Cảm xúc: ai cảm thấy gì, muốn gì, vì sao'")
            elif ctx.cfg["require_scene_summary"]:
                print(f"CẢNH {s}: CHƯA CÓ TÓM TẮT → thêm khối '@@scene {s}' (2–3 câu: ai, ở đâu, chuyện gì, không khí"
                      + ("; kèm 'Cảm xúc:'" if ctx.cfg["require_emotion"] else "") + ")")
    spset = set(spk)
    # Chi in dieu nguoi doc da biet: dong dung moc tai cau dau lo, cong dong co moc nam trong lo (ghi "tu <moc>").
    first = ents[0]["id"] if ents else None
    lo_pos = ctx.pos(first) if first else -1
    hi_pos = ctx.pos(ents[-1]["id"]) if ents else -1

    def in_batch(mark):
        mp = ctx.mark_pos(mark)
        return bool((mark or "").strip()) and mp is not None and lo_pos < mp <= hi_pos
    vspk = list(spk) + (["_ke"] if dlg and any(not e.get("speaker") for e in ents) else [])
    vl, vlater = [], []
    for s in vspk:
        v = ctx.voice_at(s, lo_pos)
        if v:
            vl.append(v)
        vlater += [r for r in ctx.voice_rows(s) if in_batch(r.get("tu_canh"))]
    vl = [v for v in vl[:15] if fresh("ho:" + v["speaker"], voice_line(v), "hồ sơ")]
    vlater = [r for r in vlater[:10] if fresh(f"ho:{r['speaker']}@{r['tu_canh']}", voice_line(r), "hồ sơ")]
    if vl or vlater:
        print("HỒ SƠ NHÂN VẬT (đúng tới chỗ đang dịch):")
        for v in vl:
            print("  " + voice_line(v))
        for r in vlater:
            print(f"  từ {r['tu_canh']}: " + voice_line(r))
    cand = [r for r in ctx.pairs if r["speaker"] in spset or r["speaker"] == "*"]
    prs = []
    for k in uniq((r["speaker"], r["listener"]) for r in cand):
        grp = [r for r in cand if (r["speaker"], r["listener"]) == k]
        prs += ctx.phase_pick(grp, first) if first else grp
    prs = sorted(prs, key=lambda r: 0 if r["listener"] in spset else 1)
    plater = [r for r in cand if in_batch(r.get("tu_canh"))]
    prs = [r for r in prs[:24] if fresh(f"xh:{r['speaker']}|{r['listener']}", pair_line(r), "xưng hô")]
    plater = [r for r in plater[:10] if fresh(f"xh:{r['speaker']}|{r['listener']}@{r['tu_canh']}", pair_line(r), "xưng hô")]
    if prs or plater:
        print("XƯNG HÔ:")
        for r in prs:
            print("  " + pair_line(r))
        for r in plater:
            print(f"  từ {r['tu_canh']}: " + pair_line(r))
    if dlg:
        nopair = [s for s in spk if not any(r["speaker"] == s for r in ctx.pairs)]
        if nopair and fresh("nopair", ",".join(nopair), "nhắc xưng hô"):
            print("CHƯA CÓ XƯNG HÔ: " + ", ".join(nopair[:20])
                  + " → thêm '@@pair <tên gốc người nói> | <tên gốc người nghe hoặc *> | xưng | gọi | ghi chú'"
                  " (chỉ thêm được dòng chưa có, không được tao/mày; ghi vào báo cáo cho phiên chính)")
    rx, mp = ctx.all_terms()
    found = []
    for e in ents:
        for r in find_terms(rx, mp, e["src"] + "\n" + (e.get("speaker") or "")):
            if r not in found:
                found.append(r)
    tl = []
    for r in found[:60]:
        sec = (r.get("lo_tu") or "").strip()
        smp = ctx.mark_pos(sec) if sec else -1
        note = "" if sec and (smp is None or lo_pos < smp) else r["note"]   # ghi chu cua bi mat: chi in tu moc lo
        extra = (f" [{r['type']}]" if r["type"] else "") + (f" ({note})" if note else "")
        ln = f"  {r['src']} = {r['vi']}{extra}"
        if fresh("tn:" + r["src"], ln, "thuật ngữ"):
            tl.append(ln)
    if tl:
        print("THUẬT NGỮ:")
        for ln in tl:
            print(ln)
    if len(found) > 60:
        print(f"  … và {len(found) - 60} mục khác (vgk.py term find <chữ>)")
    if dlg and b["n"] > 1:
        pb = ctx.batches[b["n"] - 2]
        if pb["cls"] == "dialogue":
            prev = [i for i in ctx.batch_reps(pb) if ctx.eff(i) is not None][-5:]
            # Chi in cau truoc khi cung canh (hoac cung tep neu khong co canh) voi cau dau lo: canh khac de lam lech ngu canh.
            f0 = ents[0] if ents else {}
            key = "scene" if f0.get("scene") else "file"
            prev = [i for i in prev if f0.get(key) and ctx.src[i].get(key) == f0.get(key)]
            if prev and ses is not None and ses.get("last") == b["n"] - 1:
                print(f"TRƯỚC ĐÓ: cuối lô {b['n'] - 1} vừa dịch trong phiên này.")
            elif prev:
                print("TRƯỚC ĐÓ:")
                for i in prev:
                    e = ctx.src[i]
                    print(f"  {e.get('speaker') or '-'}: {one_line(ctx.eff(i))}")
    if om:
        print(f"#> Đã in ở lô trước trong phiên {phien}, vẫn áp dụng: " + ", ".join(f"{g} {n}" for g, n in om.items()))
    print("#> ---")
    last_file = last_scene = None
    for k, e in enumerate(ents, 1):
        if not dlg and e.get("file") != last_file:
            last_file = e.get("file")
            print(f"#> tệp: {last_file}")
        if dlg and e.get("scene") and e.get("scene") != last_scene:
            last_scene = e.get("scene")
            print(f"#> cảnh: {last_scene}")
        meta = []
        if e.get("speaker"):
            meta.append(e["speaker"])
            lis = ctx.listener(e["id"]) if dlg else None
            if lis:
                meta.append(f"→ {lis}")
        if e.get("note"):
            meta.append(f"({e['note']})")
        ml = e.get("maxlen") or maxlen_for(ctx.cfg, e)
        if ml:
            meta.append(f"≤{ml}" + (f"×{e['maxlines']} dòng" if e.get("maxlines") else ""))
        if e.get("page"):
            meta.append(f"trang {e['page']}" + (" · lồng tiếng" if e.get("voice") else ""))
        elif e.get("voice"):
            meta.append("lồng tiếng")
        if not dlg and e["kind"] != "data":
            meta.append(e["kind"])
        gs = ctx.group_size(e["id"])
        if gs > 1:
            meta.append(f"×{gs}")
        print(f"@@ ~{b['n']}.{k}" + (" · " + " · ".join(meta) if meta else ""))
        for line in e["src"].split("\n"):
            print("#> " + line)
        if (en_all or e["id"] in en_ids) and e.get("en"):
            print("#> EN: " + one_line(e["en"]))
        if not ctx.done(e["id"]):
            h = ctx.lap_hint(e["id"])
            if h:
                print("#> đã dịch ở cảnh khác: " + one_line(ctx.eff(h)) + " (đúng ý ở đây thì ghi '=')")
        if ctx.eff(e["id"]) is not None and not ctx.done(e["id"]):
            print("#> bản cũ (gốc đã đổi): " + one_line(ctx.eff(e["id"])))
        elif vi_lines and ctx.eff(e["id"]) is not None:
            print("#> VI: " + (GOP_BODY if (ctx.trx.get(e["id"]) or {}).get("g") else one_line(ctx.eff(e["id"]))))
    print("#> ---")
    cmdw = f"vgk.py write - --phien {phien} --tiep" if phien else "vgk.py write -"
    if fresh("ghi", cmdw, "hướng dẫn ghi"):
        print(f"#> Ghi: {cmdw} <<'VGK' … VGK — mỗi mục: dòng '@@ ~{b['n']}.<số>' (thêm ' >tên gốc người nghe' khi cảnh "
              "≥3 người) rồi bản dịch; không chép lại dòng '#>'; thêm @@term/@@pair/@@voice/@@scene khi còn thiếu; "
              "bible sai, thiếu hoặc truyện đổi quan hệ: '@@bao ~lô.số nội dung' cho phiên chính")
    else:
        print(f"#> Ghi như lô trước: {cmdw} <<'VGK' … VGK")
    if ses is not None:
        ses["last"], ses["t"] = b["n"], now()
        save_state(ctx.state)


def cmd_next(a):
    ctx = Ctx()
    if a.en and a.en != "all" and not a.batch and not a.all and not a.limit:
        # Xin EN vai cau cua lo vua in: chi in cac cau do, khong in lai ca lo (giu nguyen ma tat).
        if ctx.cfg["en_mode"] == "none":
            print("(en_mode = none: không in EN)")
            return
        for k in split_list(a.en, ","):
            i = resolve_one(ctx, k) if ALIAS_RE.match(k) else (k if k in ctx.src else None)
            if not i:
                print(f"{k}: mã không còn dùng được (chạy lại vgk.py next)")
                continue
            e = ctx.src[i]
            print(f"@@ {k}" + (f" · {e['speaker']}" if e.get("speaker") else ""))
            print("#> EN: " + (one_line(e["en"]) if e.get("en") else "(không có bản EN)"))
        return
    if a.batch:
        b = next((x for x in ctx.batches if x["n"] == a.batch), None)
        if b is None:
            die(f"không có lô {a.batch}")
    else:
        b = next((x for x in ctx.batches if ctx.batch_pending(x)), None)
        if b is None:
            sua = ctx.state.get("sua") or {}
            if sua:
                print(f"Đã dịch hết các lô. Còn {len(sua)} câu cần sửa → vgk.py sua next")
                return
            print("Đã dịch hết các lô. Bước tiếp: vgk.py check, rồi vgk.py qa sample --gate F2")
            return
    reps = ctx.batch_reps(b)
    show = reps if a.all else [r for r in reps if not ctx.done(r)]
    if a.limit:
        show = show[:a.limit]
    en_all, en_ids = en_selection(ctx, a.en, b, show)
    emit_batch(ctx, b, show, en_all, en_ids, phien=a.phien)


def tiep_after_write(ctx, tag, bad):
    """write --tiep (2.3): ghi sach thi in luon lo ke trong dai, bot mot luot goi lenh moi lo."""
    if bad:
        print("CHƯA IN LÔ KẾ: sửa các mục lỗi ở trên rồi ghi lại chỉ các mục đó (vẫn kèm --tiep).")
        return
    ses = phien_get(ctx, tag) if tag else None
    cur = (ses or {}).get("cur") or ctx.state.get("last_batch") or 0
    den = (ses or {}).get("den")
    cb = ctx.batches[cur - 1] if 0 < cur <= len(ctx.batches) else None
    if cb is not None and ctx.batch_pending(cb):
        b, head = cb, f"======== LÔ {cur} CÒN {len(ctx.batch_pending(cb))} CÂU CHƯA GHI ========"
    else:
        b = next((x for x in ctx.batches if x["n"] > cur and (not den or x["n"] <= den) and ctx.batch_pending(x)), None)
        head = "======== LÔ KẾ TIẾP ========"
    if b is None:
        print("HẾT DẢI" + (f" (tới lô {den})" if den else "") + ": báo cáo theo mẫu rồi dừng.")
        save_state(ctx.state)
        return
    due = qa_due(ctx)
    if due:
        print("CỔNG ĐẾN HẠN: " + "; ".join(due) + " → dừng ở đây, báo cáo cho phiên chính.")
        save_state(ctx.state)
        return
    if ses is not None:
        ses["cur"] = b["n"]
    show = ctx.batch_pending(b)
    en_all, en_ids = en_selection(ctx, None, b, show)
    print(head)
    emit_batch(ctx, b, show, en_all, en_ids, phien=tag)


def cmd_khoidong(a):
    """Mo dau cho agent dich (2.3): mot lan goi in du bible chung, ho so nguon va the loai, nguoi-lon (game 18+),
    so tay giong, N cau da dich gan nhat va lo dau cua dai (thay 4-5 lan goi lenh rieng, moi lan doc lai ca ngu canh)."""
    ctx = Ctx()
    tag = a.phien or (f"{a.batch}-{a.den}" if a.den else str(a.batch))
    b = next((x for x in ctx.batches if x["n"] >= a.batch and (not a.den or x["n"] <= a.den) and ctx.batch_pending(x)), None)
    ctx.state.setdefault("phien", {}).pop(tag, None)
    ses = phien_get(ctx, tag)
    ses["den"] = a.den
    print(f"KHỞI ĐỘNG phiên {tag} · dải lô {a.batch}" + (f"–{a.den}" if a.den else " trở đi")
          + f". Ghi mỗi lô: vgk.py write - --phien {tag} --tiep (ghi sạch thì tự in lô kế; mục lỗi thì sửa rồi ghi lại).")
    names = ["quy-tac-dich", "nguon-" + ctx.cfg["source_lang"]]
    if ctx.cfg.get("the_loai"):
        names.append("the-loai-" + ctx.cfg["the_loai"].replace("_", "-"))
    if ctx.cfg["kind"] == "18":
        names.append("nguoi-lon")
    for nm in names:
        f = find_ref(ctx, nm)
        if not f:
            print(f"===== {nm}.md: KHÔNG THẤY cạnh vgk.py, đọc tệp này trong gói skill (thư mục references) =====")
            continue
        print(f"===== {nm}.md =====")
        with open(f, encoding="utf-8-sig") as fh:
            print(fh.read().rstrip())
    if os.path.exists(p(F_SOTAY)):
        print("===== sotay.md (sổ tay giọng của game) =====")
        with open(p(F_SOTAY), encoding="utf-8-sig") as fh:
            print(fh.read().rstrip())
    build_neo(ctx, set())   # ghi nhan tep luat vua in du: lo dau khong bao 'LUAT DA DOI'
    print("=====")
    doclai_print(ctx, a.n, upto=b["n"] if b else None)
    if b is None:
        save_state(ctx.state)
        print("Dải này đã dịch xong: báo cáo rồi dừng.")
        return
    ses["cur"] = b["n"]
    show = ctx.batch_pending(b)
    en_all, en_ids = en_selection(ctx, None, b, show)
    print("======== LÔ ĐẦU ========")
    emit_batch(ctx, b, show, en_all, en_ids, phien=tag)


def resolve_one(ctx, k):
    m = ALIAS_RE.match(k)
    if not m:
        return k
    rec = ctx.state.get("alias", {}).get(m.group(1))
    idx = int(m.group(2))
    if not rec or rec.get("sig") != ctx.sig or not (1 <= idx <= len(rec.get("ids", []))):
        return None
    return rec["ids"][idx - 1]


def cmd_write(a):
    ctx = Ctx()
    pl = parse_payload(read_input(a.file))
    for pr in pl.problems[:10]:
        print("CẢNH BÁO: " + pr)
    if pl.dups:
        print("CẢNH BÁO: id lặp trong lần ghi (lấy bản sau): " + ", ".join(uniq(pl.dups)[:10]))
    has_dir = bool(pl.scenes or pl.terms or pl.pairs or pl.voices or pl.baos)
    if not a.dry:
        out, warn = apply_directives(ctx, pl)
        if out:
            print("Hồ sơ: " + " · ".join(out))
        for w in warn:
            print("CẢNH BÁO: " + w)
    elif has_dir:
        print("THỬ: không ghi @@scene/@@pair/@@voice/@@term (bỏ --dry để ghi)")
    if not pl.entries:
        if not has_dir:
            die("không có mục nào để ghi (mỗi mục bắt đầu bằng dòng '@@ id' hoặc '@@ ~lô.số').")
        return
    entries, alias_bad = resolve_aliases(ctx, pl.entries)
    for i, vi in list(entries.items()):
        if vi.strip() == "=":   # cau lap o canh khac: dung lai ban da dich (next in dong 'da dich o canh khac')
            h = ctx.lap_hint(ctx.rep_of.get(ctx.canon_of.get(i, i), i)) if i in ctx.src else None
            if h:
                entries[i] = ctx.eff(h)
            else:
                entries.pop(i)
                alias_bad.append((i, "'=' chỉ dùng khi next in dòng 'đã dịch ở cảnh khác' cho câu này"))
    force, fbad = resolve_aliases(ctx, collections.OrderedDict((x, "") for x in split_list(a.force or "", ",")))
    listeners = {}
    for k, v in pl.listeners.items():
        i = resolve_one(ctx, k)
        if i:
            listeners[i] = v
    known = {e.get("speaker") for e in ctx.src.values() if e.get("speaker")}
    for v in set(listeners.values()):
        for one in (x.strip() for x in v.split(",")):
            if one and one != "*" and known and one not in known:
                print(f"CẢNH BÁO: người nghe '{one}' không có trong src.jsonl — dùng tên gốc như trong next"
                      " ('*' = mọi người hoặc người chơi; nhiều người: 'A,B')")
    gop = {i for i in (resolve_one(ctx, k) for k in pl.gop) if i}
    _, bad, _ = commit(ctx, entries, "write", force=list(force), dry=a.dry, pre_bad=alias_bad + fbad,
                       listeners=listeners, gop=gop)
    if a.tiep and not a.dry:
        tiep_after_write(ctx, a.phien, bad)
    sys.exit(2 if bad else 0)


def cmd_check(a):
    ctx = Ctx()
    E, W = collections.OrderedDict(), collections.OrderedDict()

    def add(D, cat, key, msg=""):
        D.setdefault(cat, []).append((key, msg))

    seen = {}
    for r in ctx.gloss:
        if not r["src"] or not r["vi"]:
            add(W, "glossary thiếu cột", f"dòng {r['_line']}", r["src"] or r["vi"])
            continue
        if r["src"] in seen and seen[r["src"]] != r["vi"]:
            add(E, "glossary trùng nghĩa", f"dòng {r['_line']}", f"{r['src']}: '{seen[r['src']]}' / '{r['vi']}'")
        seen.setdefault(r["src"], r["vi"])
    for r in ctx.pairs:
        if not (r["speaker"] and r["xung"] and r["goi"]):
            add(W, "xưng hô thiếu cột", f"dòng {r['_line']}", r["speaker"])
        mp = ctx.mark_pos(r.get("tu_canh"))
        if mp is None:
            add(W, "mốc lạ (không phải mã cảnh hay id câu)", f"xungho.tsv dòng {r['_line']}", r["tu_canh"])
            continue
        sai = xung_gioi_sai(r["xung"], gioi_of(ctx.voice_at(r["speaker"], mp)))
        if sai:
            add(E, "xưng hô trái giới tính", f"xungho.tsv dòng {r['_line']}",
                f"{r['speaker']} → {r['listener']}: xưng {'/'.join(sai)}, hồ sơ lúc đó: {ctx.voice_at(r['speaker'], mp).get('gioi')}")
    for r in ctx.voices:
        if ctx.mark_pos(r.get("tu_canh")) is None:
            add(W, "mốc lạ (không phải mã cảnh hay id câu)", f"giong.tsv dòng {r['_line']}", r["tu_canh"])
    for r in ctx.secret_terms():
        if ctx.mark_pos(r["lo_tu"]) is None:
            add(W, "mốc lạ (không phải mã cảnh hay id câu)", f"glossary.tsv dòng {r['_line']}", r["lo_tu"])
    for r in ctx.needs():
        if not ctx.done(r):
            add(E, "gốc đã đổi, cần dịch lại" if ctx.eff(r) is not None else "chưa dịch", r)
    force = set(ctx.state.get("force", []))
    scene_missing = collections.Counter()
    emo_missing = collections.Counter()
    fit_auto = ctx.cfg.get("fit_auto") or []
    for eid, e in ctx.src.items():
        if eid in ctx.minor_all:
            continue
        if e["kind"] in ("ui", "data") and eid in ctx.canon_of and not (
                e.get("maxlen") or e.get("maxlines") or maxlen_for(ctx.cfg, e) or fit_matches(fit_auto, e)):
            add(W, "khung chưa rõ (P2)", eid, "chưa có maxlen/maxlines hoặc fit_auto")
        vi = ctx.eff(eid)
        if vi is None:
            continue
        if (ctx.trx.get(eid) or {}).get("g"):
            for c, m in validate_gop(ctx, eid):
                add(E, c, eid, m)
            continue
        errs, ws = validate(ctx, eid, vi, force=eid in force)
        pe, pw = pair_lint(ctx, eid, vi)
        if eid not in force:
            errs += pe
        for c, m in errs:
            add(E, c, eid, m)
        for c, m in ws + pw + style_warns(ctx, eid, vi):
            add(W, c, eid, m)
        if (ctx.cfg["require_scene_summary"] and e["kind"] == "dialogue" and e.get("scene")
                and e["scene"] not in ctx.scenes):
            scene_missing[e["scene"]] += 1
        elif emotion_missing(ctx, e):
            emo_missing[e["scene"]] += 1
    for s, n in scene_missing.items():
        (add(E, "cảnh thiếu tóm tắt kèm Cảm xúc:", s, f"{n} câu") if ctx.cfg["require_emotion"]
         else add(W, "cảnh đã dịch thiếu tóm tắt", s, f"{n} câu"))
    for s, n in emo_missing.items():
        add(E, "cảnh thiếu tóm tắt kèm Cảm xúc:", s, f"{n} câu")
    has_pair = {r["speaker"] for r in ctx.pairs}
    by_spk = collections.defaultdict(list)
    for eid, e in ctx.src.items():
        if e["kind"] != "dialogue" or not e.get("speaker") or eid in ctx.minor_all or e["speaker"] in has_pair:
            continue
        vi = ctx.eff(eid)
        if not vi:
            continue
        t = SELF_EXCL_RE.sub(" ", vi)
        for w in set(m.group(1).lower() for m in SELF_RE.finditer(t)):
            by_spk[e["speaker"]].append((w, eid))
    for spk, lst in by_spk.items():
        cnt = collections.Counter(w for w, _ in lst)
        mc = cnt.most_common()
        if len(mc) >= 2 and mc[1][1] >= 3 and mc[1][1] >= 0.15 * sum(cnt.values()):
            add(W, "tự xưng lẫn lộn (chưa có bảng)", spk, ", ".join(f"{w} {n}" for w, n in mc[:4]))
    for c, mem in ctx.members.items():
        if len(mem) < 2 or ctx.src[c]["kind"] == "dialogue":
            continue
        vals = uniq(ctx.tr[m] for m in mem if m in ctx.tr)
        if len(vals) > 1:
            add(W, "cùng câu gốc, dịch khác nhau", c, " | ".join(vals[:3]))
    for i in [i for i in ctx.tr if i not in ctx.src]:
        add(W, "bản dịch có id không còn trong src", i)
    if ctx.tr_bad:
        add(W, "tr.jsonl dòng hỏng", f"{ctx.tr_bad} dòng")
    rep = os.path.join("reports", f"check-{stamp()}.txt")
    os.makedirs(p("reports"), exist_ok=True)
    lines = [f"# check {now()} · vgk {VERSION}", ""]
    for title, D in (("LỖI CHẶN", E), ("CẢNH BÁO", W)):
        lines.append(f"## {title}")
        for cat, items in D.items():
            lines.append(f"### {cat}: {len(items)}")
            for key, msg in items[:5000]:
                if key in ctx.src:
                    s = one_line(ctx.src[key]["src"])[:120]
                    v = one_line(ctx.eff(key) or "")[:160]
                    lines.append(f"{key}\t{msg}\t{s}\t{v}")
                else:
                    lines.append(f"{key}\t{msg}")
        lines.append("")
    atomic_write(p(rep), "\n".join(lines) + "\n")
    ne = sum(len(v) for v in E.values())
    print(f"LỖI CHẶN: {ne}")
    for cat, items in E.items():
        ex = items[0][1]
        print(f"  - {cat}: {len(items)} (vd: {', '.join(k for k, _ in items[:5])}" + (f" — {ex}" if ex else "") + ")")
    print(f"CẢNH BÁO: {sum(len(v) for v in W.values())}")
    for cat, items in W.items():
        print(f"  - {cat}: {len(items)} (vd: {', '.join(k for k, _ in items[:4])})")
    print(f"Chi tiết: {rep}")
    sys.exit(1 if ne else 0)


def cmd_review(a):
    ctx = Ctx()
    cand = [r for r in ctx.needs() if ctx.done(r) and (a.all_kinds or ctx.src[r]["kind"] == "dialogue")]
    if not cand:
        die("chưa có câu nào đã dịch để rà.")
    seed = a.seed if a.seed is not None else random.randrange(1 << 30)
    rnd = random.Random(seed)
    print(f"(seed {seed})")
    by_file = collections.defaultdict(list)
    for eid in cand:
        by_file[ctx.src[eid].get("file") or "-"].append(eid)
    pick = []
    for f, lst in by_file.items():
        k = max(1, round(a.n * len(lst) / len(cand)))
        pick += rnd.sample(lst, min(k, len(lst)))
    if len(pick) > a.n:
        pick = rnd.sample(pick, a.n)
    pick = set(pick)
    if a.uu_tien:
        pri = {s for s, r in ctx.scenes.items() if r["priority"]}
        lst = [eid for eid in cand if ctx.src[eid].get("scene") in pri]
        pick |= set(rnd.sample(lst, min(a.cap, len(lst))))
    order = [eid for eid in ctx.src if eid in pick]
    out = []
    for eid in order:
        e = ctx.src[eid]
        out.append(f"@@ {eid}" + (f" · {e['speaker']}" if e.get("speaker") else ""))
        for line in e["src"].split("\n"):
            out.append("#> " + line)
        out.append(ctx.eff(eid))
    rep = os.path.join("reports", f"review-{stamp()}.txt")
    os.makedirs(p("reports"), exist_ok=True)
    atomic_write(p(rep), "\n".join(out) + "\n")
    print(f"RÀ {len(order)} câu (mẫu ngẫu nhiên theo tệp{', + cảnh ưu tiên' if a.uu_tien else ''}). "
          f"Chỉ gửi lại mục cần sửa qua vgk.py write (dùng id đầy đủ như dưới). Lưu: {rep}")
    print("#> ---")
    print("\n".join(out))


def cmd_show(a):
    ctx = Ctx(need_plan=os.path.exists(p(F_PLAN)), quiet=True)
    get = (lambda i: ctx.eff(i)) if ctx.plan else (lambda i: ctx.tr.get(i))
    ids = list(ctx.src)
    if a.around:
        if a.around not in ctx.src:
            die(f"không có id {a.around}")
        k = ids.index(a.around)
        sel = ids[max(0, k - a.n):k + a.n + 1]
    else:
        sel = []
        started = a.start is None
        g = a.grep.lower() if a.grep else None
        for eid in ids:
            if not started:
                started = eid == a.start
                if not started:
                    continue
            e = ctx.src[eid]
            if a.file and not (fnmatch.fnmatch(e.get("file") or "", a.file)
                               or fnmatch.fnmatch((e.get("file") or "").split("/")[-1], a.file)):
                continue
            if a.speaker and (e.get("speaker") or "") != a.speaker:
                continue
            if a.scene and (e.get("scene") or "") != a.scene:
                continue
            if g:
                hay = (e["src"] + "\n" + (e.get("en") or "") + "\n" + (get(eid) or "")).lower()
                if g not in hay:
                    continue
            sel.append(eid)
            if len(sel) >= a.n:
                break
    for eid in sel:
        e = ctx.src[eid]
        print(f"{eid} · {e.get('speaker') or '-'}: {one_line(e['src'])}")
        if a.en and e.get("en"):
            print(f"   EN: {one_line(e['en'])}")
        if a.vi:
            vi = get(eid)
            if vi is not None:
                print(f"   = {one_line(vi)}")
    if not sel:
        print("(không có câu nào khớp)")


def cmd_speakers(a):
    ctx = Ctx(need_plan=False)
    cnt = collections.Counter(e.get("speaker") for e in ctx.src.values() if e["kind"] == "dialogue" and e.get("speaker"))
    haspair = {r["speaker"] for r in ctx.pairs}
    hasvoice = {r["speaker"] for r in ctx.voices}
    print(f"{len(cnt)} người nói · [x] có xưng hô · [g] có giọng · tên dùng trong @@pair/@@voice đúng như cột này")
    for s, n in cnt.most_common(a.n):
        print(f"  {s}: {fmt_n(n)} câu {'[x]' if s in haspair else '[ ]'}{'[g]' if s in hasvoice else '[ ]'}")


def cmd_fill(a):
    ctx = Ctx()
    exact = {r["src"].strip(): r["vi"] for r in ctx.gloss if r["src"] and r["vi"]}
    cand = collections.OrderedDict()
    for r in ctx.needs():
        if ctx.done(r):
            continue
        e = ctx.src[r]
        if e["kind"] == "dialogue" and not a.all_kinds:
            continue
        k = e["src"].strip()
        if k in exact:
            cand[r] = e["src"].replace(k, exact[k], 1)
    print(f"Khớp nguyên văn với glossary: {len(cand)} mục")
    for c, v in list(cand.items())[:5]:
        print(f"  {c}: {one_line(ctx.src[c]['src'])} → {one_line(v)}")
    if not a.apply:
        print("Chưa ghi. Thêm --apply để ghi.")
        return
    if cand:
        commit(ctx, cand, "fill")


def cmd_bulk(a):
    ctx = Ctx()
    try:
        rx = re.compile(a.match)
    except re.error as ex:
        die(f"--match sai: {ex}")
    exact = {r["src"].strip(): r["vi"] for r in ctx.gloss if r["src"] and r["vi"]}
    tpl = a.to.replace("\\n", "\n")
    cand, miss = collections.OrderedDict(), collections.Counter()
    pool = ctx.needs()
    for c in pool:
        if not a.redo and ctx.done(c):
            continue
        e = ctx.src[c]
        if a.kind and e["kind"] != a.kind:
            continue
        if a.file and not (fnmatch.fnmatch(e.get("file") or "", a.file)
                           or fnmatch.fnmatch((e.get("file") or "").split("/")[-1], a.file)):
            continue
        m = rx.fullmatch(e["src"])
        if not m:
            continue
        lost = []

        def rep(mm, m=m, lost=lost):
            g = int(mm.group(1))
            val = (m.group(g) if g <= (m.re.groups or 0) else "") or ""
            if mm.group(2):
                vv = exact.get(val.strip())
                if vv is None:
                    lost.append(val.strip())
                    return ""
                return vv
            return val
        vi = re.sub(r"\$\{(\d+)(\|g)?\}", rep, tpl)
        if lost:
            for x in lost:
                miss[x] += 1
            continue
        cand[c] = vi
    print(f"Khớp mẫu: {len(cand) + sum(miss.values())} · tạo được {len(cand)} · thiếu thuật ngữ {sum(miss.values())}")
    for c, v in list(cand.items())[:5]:
        print(f"  {c}: {one_line(ctx.src[c]['src'])} → {one_line(v)}")
    if miss:
        print("Thiếu trong glossary: " + ", ".join(f"{k}×{n}" for k, n in miss.most_common(10)))
    if not a.apply:
        print("Chưa ghi. Thêm --apply để ghi.")
        return
    if cand:
        commit(ctx, cand, "bulk")


def cmd_term(a):
    if a.tcmd == "add":
        ctx = Ctx(need_plan=False)
        if a.lo_tu and ctx.mark_pos(a.lo_tu) is None:
            die(f"mốc '{a.lo_tu}' không phải mã cảnh hay id câu trong src.jsonl")
        a_, u, msgs = add_terms(ctx, [{"src": a.src, "vi": a.vi, "type": a.type or "", "note": a.note or "",
                                       "forbid": a.forbid or "", "lo_tu": a.lo_tu or ""}])
        for m in msgs:
            print("CẢNH BÁO: " + m)
        print(f"Thuật ngữ: +{a_} · sửa {u}")
    elif a.tcmd == "find":
        ctx = Ctx(need_plan=False)
        q = a.text.lower()
        rows = [r for r in ctx.gloss if q in r["src"].lower() or q in r["vi"].lower() or q in r["note"].lower()]
        for r in rows[:a.n]:
            extra = (f" [{r['type']}]" if r["type"] else "") + (f" ({r['note']})" if r["note"] else "") \
                + (f" {{cấm: {r['forbid']}}}" if r["forbid"] else "")
            print(f"{r['src']} = {r['vi']}{extra}")
        print(f"({len(rows)} mục)" if rows else "(không có)")
    elif a.tcmd == "stats":
        ctx = Ctx(need_plan=False)
        cnt = collections.Counter(r["type"] or "-" for r in ctx.gloss)
        print(f"{len(ctx.gloss)} mục: " + ", ".join(f"{k} {v}" for k, v in cnt.most_common()))
    elif a.tcmd == "import":
        ctx = Ctx(need_plan=False)
        rows = read_tsv(a.file, GLOSS_COLS)
        if not rows:
            die("tệp rỗng hoặc thiếu dòng tiêu đề (src, vi, type, note, forbid).")
        a_, u, msgs = add_terms(ctx, rows)
        for m in msgs[:30]:
            print("XUNG ĐỘT: " + m)
        if len(msgs) > 30:
            print(f"… và {len(msgs) - 30} xung đột khác")
        print(f"Nhập: +{a_} · sửa {u} · xung đột {len(msgs)}")
    elif a.tcmd == "change":
        term_change(a)
    elif a.tcmd == "candidates":
        cmd_term_candidates(a)
    elif a.tcmd == "skip":
        cmd_term_skip(a)


def term_change(a):
    """Doi nghia mot thuat ngu an toan:
    - chi xet cau ma goc khop dung thuat ngu nay (thuat ngu dai nhat thang),
    - che nghia cua thuat ngu khac truoc khi thay,
    - chi tu thay khi so lan xuat hien khop va nghia cu du dac trung (nhieu tieng hoac viet hoa);
      con lai lap danh sach de sua tay,
    - kiem moi cau truoc khi ghi bat cu gi; khong cam chuoi long nhau voi nghia moi."""
    ctx = Ctx()
    rows = read_tsv(p(F_GLOSS), GLOSS_COLS)
    row = next((r for r in rows if r["src"] == a.src), None)
    if row is None:
        die(f"không có thuật ngữ '{a.src}' trong glossary")
    old, new = row["vi"], a.vi.strip()
    if not old:
        die(f"'{a.src}' chưa có nghĩa — dùng: vgk.py term add")
    if not new or old == new:
        die("nghĩa mới rỗng hoặc trùng nghĩa cũ")
    key = a.src.lower()
    distinctive = (" " in old.strip()) or old[:1].isupper()
    rx, mp = ctx.all_terms()
    others = sorted({r["vi"] for r in ctx.gloss if r["vi"] and r["src"] != a.src and r["vi"] != old
                     and word_in(old, r["vi"], ci=True)}, key=len, reverse=True)
    old_re = word_re(old, ci=True)
    changes, manual, elsewhere = collections.OrderedDict(), [], []
    def sub(m):
        g = m.group(0)
        return new[:1].upper() + new[1:] if g[:1].isupper() and not new[:1].isupper() else new

    for eid, vi in ctx.tr.items():
        if eid not in ctx.src:
            continue
        n_src = term_hits(rx, mp, ctx.src[eid]["src"]).get(key, 0)
        masked, holds = vi, collections.defaultdict(list)
        for k, ov in enumerate(others):
            if word_in(ov, masked, ci=True):
                masked = word_re(ov, ci=True).sub(
                    lambda m, k=k: holds[k].append(m.group(0)) or f"\x00{k}\x00", masked)
        n_vi = len(old_re.findall(masked))
        if not n_src:
            if n_vi:
                elsewhere.append(eid)
            continue
        if n_vi == 0:
            continue
        if distinctive and n_vi == n_src:
            nv = old_re.sub(sub, masked)
            its = {k: iter(v) for k, v in holds.items()}
            nv = re.sub("\x00(\\d+)\x00", lambda m: next(its[int(m.group(1))]), nv)
            changes[eid] = nv
        else:
            manual.append(eid)
    safe_forbid = distinctive and old.lower() not in new.lower() and new.lower() not in old.lower()
    print(f"'{a.src}': '{old}' → '{new}' · tự sửa {len(changes)} câu · cần sửa tay {len(manual)} câu"
          + (f" · {len(elsewhere)} câu có '{old}' nhưng gốc không chứa '{a.src}' (không đụng)" if elsewhere else "")
          + ("" if safe_forbid else f" · không đưa '{old}' vào danh sách cấm (từ chung/chồng lấn)"))
    for eid, v in list(changes.items())[:3]:
        print(f"  {eid}: {one_line(ctx.tr[eid])[:70]} → {one_line(v)[:70]}")
    if manual:
        print("  sửa tay (số lần xuất hiện không khớp hoặc nghĩa cũ là từ chung): " + ", ".join(manual[:12])
              + (" …" if len(manual) > 12 else ""))
    rep = os.path.join("reports", f"term-change-{stamp()}.txt")
    os.makedirs(p("reports"), exist_ok=True)
    lines = [f"# term change {a.src}: '{old}' → '{new}' ({now()})", "## tự sửa"]
    lines += [f"{i}\t{one_line(ctx.tr[i])}\t→\t{one_line(v)}" for i, v in changes.items()]
    lines += ["## sửa tay", *[f"{i}\t{one_line(ctx.tr[i])}" for i in manual]]
    lines += ["## có nghĩa cũ nhưng gốc không chứa thuật ngữ", *[f"{i}\t{one_line(ctx.tr[i])}" for i in elsewhere]]
    atomic_write(p(rep), "\n".join(lines) + "\n")
    print(f"Chi tiết: {rep}")
    if not a.apply:
        print("Chưa ghi gì. Thêm --apply để ghi (tự sao lưu trước).")
        return
    new_rows = [dict(r) for r in rows]
    for r in new_rows:
        if r["src"] == a.src:
            r["vi"] = new
            if safe_forbid:
                r["forbid"] = ";".join(uniq(split_list(r["forbid"]) + [old]))
    ctx.gloss = [dict(r) for r in new_rows]
    ctx._all_terms = None
    bad = []
    for eid, v in changes.items():
        errs, _ = validate(ctx, eid, fit_newlines(ctx.src[eid]["src"], v), force=eid in set(ctx.state.get("force", [])))
        if errs:
            bad.append((eid, "; ".join(f"{c}: {m}" for c, m in errs)))
    if bad:
        print("DỪNG — một số câu sau khi đổi không qua kiểm tra, chưa ghi gì:")
        for eid, m in bad[:20]:
            print(f"  {eid}: {m}")
        sys.exit(2)
    bdir = p(os.path.join("backup", f"term-{stamp()}"))
    os.makedirs(bdir, exist_ok=True)
    for f in (F_TR, F_GLOSS):
        if os.path.exists(p(f)):
            shutil.copyfile(p(f), os.path.join(bdir, f))
    write_tsv(p(F_GLOSS), GLOSS_COLS, new_rows)
    ctx.reload_tables()
    if changes:
        commit(ctx, changes, f"term change {a.src}", quiet_ok=True)
    print(f"Đã đổi glossary. Sao lưu: backup/{os.path.basename(bdir)}"
          + (f" · còn {len(manual)} câu cần sửa tay (xem {rep})" if manual else ""))


def cmd_pair(a):
    ctx = Ctx(need_plan=False)
    if a.pcmd == "set":
        known = {e.get("speaker") for e in ctx.src.values() if e.get("speaker")}
        if known and a.speaker != "*" and a.speaker not in known:
            print(f"CẢNH BÁO: '{a.speaker}' không có trong src.jsonl — dùng tên gốc như trong next/speakers")
        tc = (a.tu_canh or "").strip()
        mp = ctx.mark_pos(tc)
        if mp is None:
            die(f"mốc '{tc}' không phải mã cảnh hay id câu trong src.jsonl")
        sai = xung_gioi_sai(a.xung, gioi_of(ctx.voice_at(a.speaker, mp)))
        if sai and not a.force:
            die(f"xưng '{'/'.join(sai)}' trái giới tính trong hồ sơ {a.speaker} ({ctx.voice_at(a.speaker, mp).get('gioi')})"
                " — sửa hồ sơ (vgk.py voice … --gioi) hoặc cố ý thì thêm --force")
        ad, up = upsert(p(F_PAIR), PAIR_COLS, ["speaker", "listener", "tu_canh"],
                        [{"speaker": a.speaker, "listener": a.listener or "*", "tu_canh": tc, "xung": a.xung,
                          "goi": a.goi, "note": a.note or ""}])
        print(f"Xưng hô: +{ad} · sửa {up}" + (f" (áp từ {tc})" if tc else ""))
    else:
        q = a.name.lower()
        rows = [r for r in ctx.pairs if q in r["speaker"].lower() or q in r["listener"].lower()]
        for r in rows:
            print((f"từ {r['tu_canh']}: " if r.get("tu_canh") else "") + pair_line(r))
        print(f"({len(rows)} mục)" if rows else "(không có)")


def cmd_scene(a):
    if a.scmd == "set":
        r = {"scene": a.scene, "summary": a.summary}
        if a.uu_tien or a.bo_uu_tien:
            r["priority"] = "y" if a.uu_tien else ""
            r["_clear"] = ("priority",)
        ad, up = upsert(p(F_SCENE), SCENE_COLS, ["scene"], [r])
        print(f"Tóm tắt cảnh: +{ad} · sửa {up}")
    else:
        ctx = Ctx()
        miss = collections.Counter()
        for eid, e in ctx.src.items():
            if e["kind"] == "dialogue" and e.get("scene") and e["scene"] not in ctx.scenes:
                if a.all or ctx.eff(eid) is not None:
                    miss[e["scene"]] += 1
        for s, n in list(miss.items())[:a.n]:
            print(f"{s}: {n} câu")
        print(f"({len(miss)} cảnh thiếu tóm tắt)")


def cmd_voice(a):
    """Ho so nhan vat (giong.tsv). Moc --tu-canh: dong chi ap tu do; o de trong thi ke thua dong truoc."""
    ctx = Ctx(need_plan=False)
    tc = (a.tu_canh or "").strip()
    mp = ctx.mark_pos(tc)
    if mp is None:
        die(f"mốc '{tc}' không phải mã cảnh hay id câu trong src.jsonl")
    if not tc and not (a.giong or "").strip() and not any(not (r.get("tu_canh") or "").strip()
                                                       for r in ctx.voice_rows(a.speaker)):
        die("dòng gốc (không có --tu-canh) cần mô tả giọng")
    row = {"speaker": a.speaker, "tu_canh": tc, "gioi": a.gioi or "", "vai_ve": a.vai_ve or "", "tam_ly": a.tam_ly or "",
           "giong": a.giong or "", "mau": a.mau or ""}
    ad, up = upsert(p(F_VOICE), VOICE_COLS, ["speaker", "tu_canh"], [row])
    print(f"Hồ sơ: +{ad} · sửa {up}" + (f" (áp từ {tc})" if tc else ""))
    ctx.reload_tables()
    for r in ctx.pairs:
        if r["speaker"] != a.speaker:
            continue
        pm = ctx.mark_pos(r.get("tu_canh"))
        if pm is None:
            continue
        sai = xung_gioi_sai(r["xung"], gioi_of(ctx.voice_at(a.speaker, pm)))
        if sai:
            print(f"CẢNH BÁO: xưng hô {pair_line(r)} trái giới tính hồ sơ ({'/'.join(sai)}) → sửa bằng vgk.py pair set")


def cmd_minor(a):
    ids = list(getattr(a, "ids", None) or [])
    ctx = Ctx(quiet=True) if any(ALIAS_RE.match(i) for i in ids) else Ctx(need_plan=False)
    if a.mcmd == "add":
        res = []
        for i in ids:
            r = resolve_one(ctx, i) if ALIAS_RE.match(i) else i
            if r is None:
                die(f"mã tắt {i} không còn dùng được (lô đã chia lại hoặc quá cũ) — chạy lại vgk.py next")
            res.append(r)
        bad = [i for i in res if i not in ctx.src]
        if bad:
            die("id không có trong src: " + ", ".join(bad[:10]))
        new = uniq(i for i in res if i not in ctx.minors)
        if new:
            note = f"  # {clean_cell(a.note)}" if a.note else ""
            append_text(p(F_MINOR), "".join(f"{i}{note}\n" for i in new))
        print(f"Giữ nguyên thêm {len(new)} id (tổng {len(ctx.minors) + len(new)}). "
              "Chỉ đúng các id này; câu trùng chữ ở cảnh khác vẫn dịch bình thường.")
    else:
        print(f"{len(ctx.minors)} id giữ nguyên: " + ", ".join(sorted(ctx.minors)[:30]) + (" …" if len(ctx.minors) > 30 else ""))


def cmd_export(a):
    ctx = Ctx()
    out, st, missing, gop_ids = collections.OrderedDict(), collections.Counter(), [], []
    mark = None
    if getattr(a, "danh_dau", None):
        mark = ("※" if ctx.cjk else "^") if a.danh_dau == "auto" else a.danh_dau
    for eid, e in ctx.src.items():
        if a.identity:
            out[eid] = e["src"]
            continue
        if mark is not None:
            out[eid] = mark + e["src"] if e["src"].strip() else e["src"]
            continue
        if (ctx.trx.get(eid) or {}).get("g") and ctx.done(eid):
            out[eid] = ""
            gop_ids.append(eid)
            st["gộp vào câu trước"] += 1
            continue
        if eid in ctx.minor_all:
            use_en = ctx.cfg["minor_fallback"] == "en" and e.get("en")
            out[eid] = e["en"] if use_en else e["src"]
            st["giữ nguyên vị thành niên (hiện " + ("tiếng Anh)" if use_en else "bản gốc)")] += 1
            continue
        vi = ctx.eff(eid)
        if vi is not None:
            out[eid] = vi
            st["đã dịch" if ctx.done(eid) else "gốc đã đổi (đang dùng bản dịch cũ)"] += 1
        elif eid in ctx.auto:
            out[eid] = norm_auto(e["src"]) if ctx.cjk else e["src"]
            st["tự động"] += 1
        else:
            out[eid] = e["src"]
            missing.append(eid)
    path = a.out or p("export.json")
    if a.format == "tsv":
        def esc(v):
            return v.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t")
        atomic_write(path, "".join(f"{k}\t{esc(v)}\n" for k, v in out.items()))
    else:
        atomic_write(path, json.dumps(out, ensure_ascii=False, indent=0) + "\n")
    if a.identity:
        print(f"Xuất nguyên bản (kiểm adapter khứ hồi): {fmt_n(len(out))} mục → {path}")
        return
    if mark is not None:
        print(f"Xuất bản đánh dấu ('{mark}' + câu gốc): {fmt_n(len(out))} mục → {path}. Ghi vào game bằng adapter như bản thật, "
              f"chơi thử vài phút (mở menu, túi đồ, trận đấu, lưu game): chữ nào hiện lên mà không có dấu '{mark}' là chưa "
              "được trích hoặc chưa ghi được vào game.")
        return
    atomic_write(os.path.join(os.path.dirname(path) or ".", F_EXPMETA),
                 json.dumps({"gop": gop_ids}, ensure_ascii=False) + "\n")
    parts = [f"{k} {fmt_n(v)}" for k, v in st.items()]
    if missing:
        parts.append(f"CHƯA DỊCH {fmt_n(len(missing))} (đang để bản gốc)")
    print(f"Xuất {fmt_n(len(out))} mục → {path}: " + ", ".join(parts))
    if missing and not a.allow_missing:
        print("Còn câu chưa dịch: " + ", ".join(missing[:10]) + " … (bản thử giữa chừng: thêm --allow-missing)")
        sys.exit(1)


def read_first(path):
    """Dong dau cua tep (bo khoang trang); "" neu khong co."""
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            return (f.readline() or "").strip()
    except OSError:
        return ""


def known_patch_shas():
    """sha day du cua moi tep da dong goi trong WORK/patch/*/manifest_sha.txt -> ten thu muc patch."""
    out = {}
    root = p("patch")
    if os.path.isdir(root):
        for d in sorted(os.listdir(root)):
            f = os.path.join(root, d, "manifest_sha.txt")
            if not os.path.isfile(f):
                continue
            with open(f, encoding="utf-8-sig") as fh:
                for ln in fh:
                    parts = ln.strip().split("|")
                    # bo tep patch giong het ban goc (khong doi gi): trung sha khong phai dau hieu da cai
                    if len(parts) == 3 and len(parts[2]) == 64 and parts[1].lower() != parts[2].lower():
                        out[parts[2].lower()] = f"patch/{d}"
    return out


def cmd_goc(a):
    """Ban chep 'goc' cua game da cai ban Viet hoa: chep phan can doc, thay tep da bi patch bang ban sao luu."""
    game, out = os.path.abspath(a.game), os.path.abspath(a.out)
    bk = os.path.join(game, "_viethoa_backup")
    if not os.path.isdir(bk):
        print("Game chưa cài bản Việt hóa (không có _viethoa_backup): adapter và patchkit dùng thẳng thư mục game.")
        return
    if os.path.isdir(out) and os.listdir(out):
        die(f"{out} đã có dữ liệu — chọn một thư mục mới")
    if (out + os.sep).startswith(game + os.sep):
        die("--out phải nằm ngoài thư mục game")
    for s in a.sub or ["."]:
        src = os.path.join(game, s)
        dst = os.path.normpath(os.path.join(out, s))
        if os.path.isdir(src):
            shutil.copytree(src, dst, copy_function=shutil.copyfile, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("_viethoa_backup"))
        elif os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
        else:
            die(f"không thấy '{s}' trong thư mục game")
    inst = os.path.join(bk, "_installed")
    rest = rm = newer = 0
    for dp, _, fn in os.walk(inst):
        for f in fn:
            if not f.endswith(".sha"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), inst)[:-4]
            dst = os.path.join(out, rel)
            if not os.path.isfile(dst):
                continue
            if file_sha(dst, full=True) != read_first(os.path.join(dp, f)).lower():
                newer += 1  # game da doi tep nay sau khi cai: day la ban goc moi
                continue
            b = os.path.join(bk, rel)
            if os.path.isfile(b):
                shutil.copyfile(b, dst)
                rest += 1
            else:
                os.remove(dst)  # tep moi do patch them vao (chi xoa trong ban chep nay)
                rm += 1
    known = known_patch_shas()
    left = [os.path.relpath(os.path.join(dp, f), out) for dp, _, fn in os.walk(out) for f in fn
            if known and file_sha(os.path.join(dp, f), full=True) in known]
    print(f"Bản gốc → {out}: khôi phục {rest} tệp từ sao lưu, bỏ {rm} tệp do patch thêm"
          + (f", {newer} tệp game đã đổi sau khi cài (giữ bản hiện tại)" if newer else ""))
    if left:
        die("vẫn còn tệp trùng bản Việt hóa đã đóng gói: " + ", ".join(left[:5]) + " — không dùng thư mục này làm gốc")


def cmd_patchkit(a):
    d = a.dir
    files_dir = os.path.join(d, "files")
    if not os.path.isdir(files_dir):
        die(f"không thấy {files_dir} (adapter apply phải ghi tệp vào <patch>/files/<đường dẫn trong game>)")
    man = os.path.join(d, "manifest.txt")
    if os.path.exists(man):
        with open(man, encoding="utf-8-sig") as f:
            rels = [x.strip().replace("\\", "/") for x in f if x.strip()]
    else:
        rels = []
        for root, _, fs in os.walk(files_dir):
            for fn in fs:
                rels.append(os.path.relpath(os.path.join(root, fn), files_dir).replace("\\", "/"))
        rels.sort()
        atomic_write(man, "\n".join(rels) + "\n", newline="\r\n")
    miss = [r for r in rels if not os.path.isfile(os.path.join(files_dir, *r.split("/")))]
    if miss:
        die("manifest có tệp không nằm trong files/: " + ", ".join(miss[:5]))
    if not a.game or not os.path.isdir(a.game):
        die("cần --game <thư mục game gốc> (hoặc bản chép các tệp gốc) để ghi goc_sha — bộ cài dùng nó "
            "để phát hiện game đã cập nhật")
    bad = [r for r in rels if "|" in r]
    if bad:
        die("đường dẫn chứa '|': " + ", ".join(bad[:3]))
    psha = {r: file_sha(os.path.join(files_dir, *r.split("/")), full=True) for r in rels}
    known = known_patch_shas()
    bk = os.path.join(a.game, "_viethoa_backup")
    new_files, lines, from_bk, bad = [], [], 0, []
    for r in rels:
        gp = os.path.join(a.game, *r.split("/"))
        goc = "-"
        if os.path.isfile(gp):
            s = file_sha(gp, full=True)
            inst = read_first(os.path.join(bk, "_installed", *r.split("/")) + ".sha").lower()
            if s not in known and s != inst:
                goc = s
            else:
                # Tep trong --game la ban Viet hoa da cai: sha goc phai lay tu ban sao luu, khong thi bo cai se
                # coi ban Viet cu la "ban goc" va sao luu de len ban goc that.
                bp = os.path.join(bk, *r.split("/"))
                if os.path.isfile(bp):
                    goc = file_sha(bp, full=True)
                    from_bk += 1
                    if goc in known:
                        bad.append(f"{r}: bản sao lưu cũng trùng một bản Việt hóa")
                elif inst:
                    from_bk += 1  # tep moi do patch truoc them vao: van la tep moi
                else:
                    bad.append(f"{r}: tệp trong --game là bản Việt hóa ({known.get(s, 'đã cài')}) mà không có bản sao lưu gốc")
        if goc == "-":
            new_files.append(r)
        lines.append(f"{r}|{goc}|{psha[r]}")
    if bad:
        die("--game không phải bản gốc: " + "; ".join(bad[:5]) + ". Dùng thư mục tệp gốc (vgk.py goc tạo từ game đã cài).")
    atomic_write(os.path.join(d, "manifest_sha.txt"), "\n".join(lines) + "\n", newline="\r\n")
    atomic_write(os.path.join(d, "them_moi.txt"), "".join(r + "\n" for r in new_files), newline="\r\n")
    atomic_write(os.path.join(d, "CAI_VIETHOA.bat"), BAT_INSTALL, newline="\r\n")
    atomic_write(os.path.join(d, "GO_VIETHOA.bat"), BAT_UNINSTALL, newline="\r\n")
    if a.game_win:
        atomic_write(os.path.join(d, "game_path.txt"), a.game_win.strip().strip('"').rstrip("\\/") + "\n", newline="\r\n")
    if from_bk:
        print(f"Game đang cài bản Việt hóa: lấy sha gốc của {from_bk} tệp từ _viethoa_backup.")
    print(f"Bộ cài: {len(rels)} tệp · thay {len(rels) - len(new_files)} · thêm mới {len(new_files)} · manifest_sha.txt"
          + (" · game_path.txt" if a.game_win else " · không có game_path.txt (người dùng kéo thả thư mục game vào .bat)")
          + f" → {d}")


def cmd_backup(a):
    # 2 o sao luu ghi de luan phien (o1, o2): khong de thu muc sao luu moi moc tren may nguoi dung moi lan
    st = load_state()
    k = int(st.get("backup_n") or 0)
    name = f"o{k % 2 + 1}"
    st["backup_n"] = k + 1
    save_state(st)
    d = p(os.path.join("backup", name))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "GHI_CHU.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"{now()} {a.note or ''}\n")
    n = 0
    for f in (F_GAME, F_SRC, F_PLAN, F_TR, F_GLOSS, F_PAIR, F_SCENE, F_VOICE, F_MINOR, F_NOTES, F_HANDOFF, F_LOG, F_STATE,
              F_NEO, F_GSKIP, F_CSKIP, "cam_mau.tsv"):
        if os.path.exists(p(f)):
            shutil.copyfile(p(f), os.path.join(d, f))
            n += 1
    if os.path.isdir(p("tools")):
        shutil.copytree(p("tools"), os.path.join(d, "tools"), copy_function=shutil.copyfile, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        n += 1
    if a.compact and os.path.exists(p(F_TR)):
        tr, trh, _, trx = load_tr()
        src = load_src()
        order = [i for i in src if i in tr] + [i for i in tr if i not in src]
        t = now()

        def rec(i):
            r = {"id": i, "vi": tr[i], "h": trh.get(i), "t": t}
            r.update(trx.get(i) or {})
            return json.dumps(r, ensure_ascii=False) + "\n"
        atomic_write(p(F_TR), "".join(rec(i) for i in order))
        print(f"Đã gọn tr.jsonl: {fmt_n(len(order))} bản dịch")
    print(f"Đã sao lưu {n} mục vào backup/{name}")


def cmd_hash(a):
    for f in a.files:
        if not os.path.exists(f):
            print(f"(không có)  {f}")
            continue
        print(f"{file_sha(f)}  {fmt_n(os.path.getsize(f))} B  {f}")


VI_CHARS = sorted(set("ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯư"
                       + "".join(chr(c) for c in range(0x1EA0, 0x1EFA))))
VI_SET = {c.lower() for c in VI_CHARS}


def sfnt_tables(data):
    import struct
    import zlib
    sig = data[:4]
    tables = {}
    if sig == b"wOFF":
        num = struct.unpack(">H", data[12:14])[0]
        for k in range(num):
            tag, off, comp, orig, _ = struct.unpack(">4sIIII", data[44 + k * 20:64 + k * 20])
            raw = data[off:off + comp]
            tables[tag.decode("latin-1")] = zlib.decompress(raw) if comp < orig else raw
        return tables
    if sig == b"wOF2":
        raise ValueError("WOFF2 (nén Brotli) chưa hỗ trợ — kiểm bản TTF/OTF của font này")
    base = struct.unpack(">I", data[12:16])[0] if sig == b"ttcf" else 0
    num = struct.unpack(">H", data[base + 4:base + 6])[0]
    for k in range(num):
        tag, _, off, ln = struct.unpack(">4sIII", data[base + 12 + k * 16:base + 28 + k * 16])
        tables[tag.decode("latin-1")] = data[off:off + ln]
    return tables


def cmap_codepoints(cmap):
    import struct
    n = struct.unpack(">H", cmap[2:4])[0]
    cps = set()
    for k in range(n):
        _, _, off = struct.unpack(">HHI", cmap[4 + k * 8:12 + k * 8])
        fmt = struct.unpack(">H", cmap[off:off + 2])[0]
        if fmt == 4:
            segx2 = struct.unpack(">H", cmap[off + 6:off + 8])[0]
            seg = segx2 // 2
            ends = struct.unpack(">%dH" % seg, cmap[off + 14:off + 14 + segx2])
            starts = struct.unpack(">%dH" % seg, cmap[off + 16 + segx2:off + 16 + 2 * segx2])
            deltas = struct.unpack(">%dh" % seg, cmap[off + 16 + 2 * segx2:off + 16 + 3 * segx2])
            ro = off + 16 + 3 * segx2
            ros = struct.unpack(">%dH" % seg, cmap[ro:ro + segx2])
            for i in range(seg):
                for c in range(starts[i], ends[i] + 1):
                    if c == 0xFFFF:
                        continue
                    if ros[i] == 0:
                        g = (c + deltas[i]) & 0xFFFF
                    else:
                        gp = ro + i * 2 + ros[i] + 2 * (c - starts[i])
                        g = struct.unpack(">H", cmap[gp:gp + 2])[0] if gp + 2 <= len(cmap) else 0
                        g = (g + deltas[i]) & 0xFFFF if g else 0
                    if g:
                        cps.add(c)
        elif fmt == 12:
            ng = struct.unpack(">I", cmap[off + 12:off + 16])[0]
            for gk in range(ng):
                s, e, g = struct.unpack(">III", cmap[off + 16 + gk * 12:off + 28 + gk * 12])
                for c in range(s, e + 1):
                    if g + (c - s):
                        cps.add(c)
    return cps


def used_chars(path):
    """Moi ky tu hien thi dung trong ban xuat (export.json dang {id: van ban} hoac tsv id<TAB>van ban)."""
    with open(path, encoding="utf-8-sig") as f:
        raw = f.read()
    try:
        vals = list(json.loads(raw).values())
    except Exception:
        vals = [ln.split("\t", 1)[1].replace("\\n", "\n") for ln in raw.split("\n") if "\t" in ln]
    return {ch for v in vals for ch in str(v) if not ch.isspace() and unicodedata.category(ch)[0] != "C"}


def cmd_font(a):
    used = used_chars(a.text) if a.text else None
    bad_any = False
    for f in a.files:
        try:
            with open(f, "rb") as fh:
                data = fh.read()
            t = sfnt_tables(data)
            if "cmap" not in t:
                print(f"{f}: không có bảng cmap")
                continue
            cps = cmap_codepoints(t["cmap"])
            miss = [ch for ch in VI_CHARS if ord(ch) not in cps]
            if miss:
                print(f"{f}: THIẾU {len(miss)}/{len(VI_CHARS)} ký tự tiếng Việt: " + " ".join(miss[:30]) + (" …" if len(miss) > 30 else ""))
            else:
                print(f"{f}: đủ {len(VI_CHARS)}/{len(VI_CHARS)} ký tự tiếng Việt")
            if used is not None:
                m2 = sorted(ch for ch in used if ord(ch) not in cps)
                bad_any = bad_any or bool(m2)
                print(f"  ký tự đang dùng trong bản dịch: {len(used)} · thiếu trong font {len(m2)}"
                      + (": " + " ".join(m2[:40]) + (" …" if len(m2) > 40 else "") if m2 else ""))
        except Exception as ex:
            print(f"{f}: không đọc được ({ex})")
    if used is not None and bad_any:
        sys.exit(1)


# ---------------------------------------------------------------- cong QA

QA_GATES = ("P3", "P5", "T2", "T3", "F2", "F3")
QA_MUC = {"nang": "nang", "nặng": "nang", "nhe": "nhe", "nhẹ": "nhe", "ok": "ok"}


def qa_parse(rows, expected, check):
    """Moi muc trong expected phai co dung 1 dong hop le; thieu, lap, ma la, sai dinh dang -> dung, khong ghi gi."""
    exp = set(expected)
    got, bad = {}, []
    for r in rows:
        k = r[0]
        if k.startswith("|"):
            bad.append("dòng dạng bảng Markdown, cần TSV (cột cách nhau bằng tab)")
            continue
        if k not in exp:
            bad.append(f"mã lạ '{k[:40]}'")
            continue
        if k in got:
            bad.append(f"'{k}' có 2 dòng")
            continue
        why = check(r)
        if why:
            bad.append(f"'{k}': {why}")
            continue
        got[k] = r
    miss = [k for k in expected if k not in got]
    if bad or miss:
        msg = []
        if miss:
            msg.append(f"thiếu {len(miss)}/{len(expected)} mục (vd {', '.join(miss[:5])})")
        if bad:
            msg.append(f"{len(bad)} dòng sai: " + "; ".join(uniq(bad)[:5]))
        die("kết quả giám khảo chưa dùng được — " + " · ".join(msg)
            + ". Chưa ghi gì; nhờ giám khảo trả lại đủ và đúng định dạng rồi chấm lại.", code=2)
    return got


def notes_fact_lines():
    """Dong du kien trong notes.md (bo muc NEO, quyet dinh, chua xac minh va dong mau trong) cho cong P3."""
    out, head = [], ""
    if not os.path.exists(p(F_NOTES)):
        return out
    with open(p(F_NOTES), encoding="utf-8-sig") as f:
        for n, line in enumerate(f, 1):
            t = line.strip()
            if t.startswith("#"):
                head = t.lower()
                continue
            if head.startswith(("## neo", "## quyết định", "## điểm chưa xác minh")):
                continue
            if t.startswith(("- ", "* ")):
                body = t[2:].strip()
                if len(body) >= 8 and not body.endswith(":"):
                    out.append((n, body))
    return out


def qa_cfg(ctx):
    q = ctx.state.setdefault("qa", {})
    t2 = q.setdefault("T2", {})
    for k, v in (("runs", 0), ("streak", 0), ("interval", 10), ("n", 50), ("need_pass", 0),
                 ("done_dlg", 0), ("done_short", 0), ("seen", []), ("fails", 0)):
        t2.setdefault(k, v)
    # State 2.0.0 cu khong co dlg_runs: coi cac lan da chay sau lo thoai la lan co thoai.
    t2.setdefault("dlg_runs", t2["runs"] if t2.get("done_dlg") else 0)
    t3 = q.setdefault("T3", {})
    for k, v in (("runs", 0), ("done_dlg", 0), ("fails", 0)):
        t3.setdefault(k, v)
    q.setdefault("can", {})
    return q


def is_gop(ctx, eid):
    return bool((ctx.trx.get(eid) or {}).get("g"))


def done_reps(ctx, kinds=None):
    out = []
    for c in ctx.members:
        r = ctx.rep_of.get(c)
        if not r or not ctx.done(r) or is_gop(ctx, r):
            continue
        if kinds and ctx.src[r]["kind"] not in kinds:
            continue
        out.append(r)
    return out


def qa_window(ctx, q):
    """Cac lo da xong ma cong T2 chua lay mau (khong co thi lay moi lo da xong)."""
    seen = set(q["T2"].get("seen") or [])
    bs = [b for b in ctx.batches if not ctx.batch_pending(b) and b["n"] not in seen]
    if not bs:
        bs = [b for b in ctx.batches if not ctx.batch_pending(b)]
    ids = [r for b in bs for r in ctx.batch_reps(b) if ctx.done(r) and not is_gop(ctx, r)]
    return bs, ids


def near_lines(ctx, eid, k=2):
    i = ctx.src_index[eid]
    e = ctx.src[eid]
    key = "scene" if e["kind"] == "dialogue" else "file"
    out = []
    for j in list(range(max(0, i - k), i)) + list(range(i + 1, min(len(ctx.src_order), i + k + 1))):
        o = ctx.src[ctx.src_order[j]]
        if o.get(key) == e.get(key):
            out.append((j - i, o))
    return out


def vi_name(ctx, name):
    if not name:
        return ""
    for r in ctx.gloss:
        if r["src"] == name and r["vi"]:
            return r["vi"]
    return name


def judge_block(ctx, eid, tag):
    """Mot muc cho giam khao doi chieu (T2/F2): goc, EN, ban dich, ngu canh, xung ho, giong."""
    e = ctx.src[eid]
    lis = ctx.listener(eid) if e["kind"] == "dialogue" else None
    out = [f"== {eid} · {e.get('speaker') or '-'}" + (f" → {lis}" if lis else "") + f" · {e['kind']} · [{tag}]"]
    sc = ctx.scenes.get(e.get("scene") or "")
    if sc and sc["summary"]:
        out.append("cảnh: " + one_line(sc["summary"])[:300])
    if e.get("speaker"):
        rows = ctx.pair_rows(e["speaker"], lis, eid)
        if rows:
            out.append("xưng hô: " + "; ".join(f"{r['speaker']}→{r['listener'] or '*'} xưng {r['xung']}, gọi {r['goi']}"
                                                + (f" ({r['note']})" if r["note"] else "") for r in rows[:2]))
        v = ctx.voice_for(e["speaker"], eid)
        if v:
            out.append("hồ sơ: " + voice_line(v))
    near = near_lines(ctx, eid)
    for d, o in near:
        if d < 0:
            out.append(f"{d:+d} {o.get('speaker') or '-'}: {one_line(o['src'])} ⇒ {one_line(ctx.eff(o['id']) or '')}")
    out.append("GỐC: " + one_line(e["src"]))
    if e.get("en"):
        out.append("EN: " + one_line(e["en"]))
    out.append("VI: " + one_line(ctx.eff(eid) or ""))
    for d, o in near:
        if d > 0:
            out.append(f"{d:+d} {o.get('speaker') or '-'}: {one_line(o['src'])} ⇒ {one_line(ctx.eff(o['id']) or '')}")
    ml = e.get("maxlen") or maxlen_for(ctx.cfg, e)
    if ml:
        out.append(f"giới hạn: ≤{ml} ký tự" + (f" × {e['maxlines']} dòng" if e.get("maxlines") else ""))
    return out


def sheet_lines(ctx, ids):
    """Bang doc cho nguoi dung: chi tieng Viet + boi canh ngan; khong co chu nguon."""
    out, last, names = [], None, {}

    def nm(s):
        if not s:
            return ""
        v = vi_name(ctx, s)
        if CJK_RE.search(v):
            names.setdefault(s, f"Nhân vật {chr(65 + len(names) % 26)}")
            v = names[s]
        return v
    for n, eid in enumerate(ids, 1):
        e = ctx.src[eid]
        key = e.get("scene") or e.get("file") or ""
        if key != last:
            r = ctx.scenes.get(e.get("scene") or "")
            summ = one_line(r["summary"]) if r and r["summary"] else ""
            summ = re.split(r"(?<=[.!?])\s", summ)[0][:160] if summ else ""
            if not summ and e["kind"] != "dialogue":
                summ = "giao diện, mô tả trong game"
            out += ["", "Bối cảnh: " + (CJK_RE.sub("", summ).strip() or "(chưa có tóm tắt)")]
            last = key
        spk = nm(e.get("speaker"))
        lis = nm(ctx.listener(eid)) if e["kind"] == "dialogue" and e.get("speaker") else ""
        who = f"{spk} nói với {lis}" if spk and lis else spk
        vi = CJK_RE.sub("□", one_line(ctx.eff(eid) or "(chưa dịch)"))
        out.append(f"{n}. " + (f"{who}: " if who else "") + vi)
    return out


def pick_quota(rnd, pools, total, taken=None):
    """Lay mau theo tang: pools = [(danh sach, so luong)], thieu thi bu tu pool cuoi."""
    taken = list(taken or [])
    have = set(taken)
    for lst, k in pools:
        cand = [i for i in lst if i not in have]
        got = rnd.sample(cand, min(k, len(cand)))
        taken += got
        have |= set(got)
    if len(taken) < total:
        rest = [i for lst, _ in pools for i in lst if i not in have]
        rest = uniq(rest)
        taken += rnd.sample(rest, min(total - len(taken), len(rest)))
    return taken[:total]


def qa_files(g):
    os.makedirs(p("reports"), exist_ok=True)
    tag = f"qa-{g}-{stamp()}"
    return os.path.join("reports", tag + ".txt"), os.path.join("reports", tag + ".ids.json")


def qa_sample(ctx, q, a):
    g = a.gate
    seed = a.seed if a.seed is not None else random.randrange(1 << 30)
    rnd = random.Random(seed)
    meta = {"gate": g, "seed": seed, "time": now()}
    txt, idf = qa_files(g)
    loai = {s: (r.get("loai") or "") for s, r in ctx.scenes.items()}
    pri = {s for s, r in ctx.scenes.items() if r["priority"]}
    if g == "T2":
        bs, win = qa_window(ctx, q)
        if not win:
            die("chưa có lô nào dịch xong để lấy mẫu.")
        n = a.n or q["T2"]["n"]
        rand = rnd.sample(win, min(n, len(win)))
        fl = ctx.state.get("flags") or {}
        ws, rs = set(win), set(rand)
        flagged = [i for i in fl if i in ws and i not in rs]
        flagged += [i for i in fl if i not in ws and i not in rs and i in ctx.src and ctx.done(i) and i not in flagged]
        flagged = flagged[:20]
        meta.update(random=rand, flagged=flagged, batches=[b["n"] for b in bs],
                    dlg=sum(1 for i in rand if ctx.src[i]["kind"] == "dialogue"))
        lines = [f"# T2 · seed {seed} · {len(rand)} câu ngẫu nhiên (tính cổng) + {len(flagged)} câu bị cờ (chỉ để sửa)"
                 f" · lô {bs[0]['n']}–{bs[-1]['n']}",
                 "# Giám khảo: làm theo references/giam-khao.md mục T2/F2. Trả TSV, mỗi dòng: "
                 "id<TAB>muc (nang|nhe|ok)<TAB>loai<TAB>ly_do<TAB>de_xuat"]
        for i in rand:
            lines += [""] + judge_block(ctx, i, "ngẫu nhiên")
        for i in flagged:
            lines += [""] + judge_block(ctx, i, "cờ: " + fl.get(i, ""))
    elif g == "F2":
        dl, sh = done_reps(ctx, ("dialogue",)), done_reps(ctx, ("ui", "data", "system"))
        if not dl and not sh:
            die("chưa có câu nào dịch xong.")
        n = a.n or 200
        d_pri = [i for i in dl if ctx.src[i].get("scene") in pri]
        d_oth = [i for i in dl if ctx.src[i].get("scene") not in pri]
        pick = pick_quota(rnd, [(d_pri, round(0.4 * n)), (d_oth, round(0.4 * n)), (sh, n - 2 * round(0.4 * n))], n)
        # Cau bi canh bao ma nguoi dich giu nguyen: giam khao xem them (chi de sua, khong tinh cong)
        fl = ctx.state.get("flags") or {}
        ps = set(pick)
        flagged = [i for i in fl if i not in ps and i in ctx.src and ctx.done(i)][:20]
        meta.update(random=pick, flagged=flagged)
        lines = [f"# F2 · seed {seed} · {len(pick)} câu phân tầng (cảnh ưu tiên, cảnh thường, ui/data)"
                 f" + {len(flagged)} câu bị cờ (chỉ để sửa)",
                 "# Giám khảo: làm theo references/giam-khao.md mục T2/F2. Trả TSV, mỗi dòng: "
                 "id<TAB>muc (nang|nhe|ok)<TAB>loai<TAB>ly_do<TAB>de_xuat"]
        for i in pick:
            lines += [""] + judge_block(ctx, i, "ngẫu nhiên")
        for i in flagged:
            lines += [""] + judge_block(ctx, i, "cờ: " + fl.get(i, ""))
    elif g == "T3":
        _, win = qa_window(ctx, q)
        dl = [i for i in win if ctx.src[i]["kind"] == "dialogue"]
        if not dl:
            dl = done_reps(ctx, ("dialogue",))
        if not dl:
            die("chưa có thoại nào dịch xong.")
        n = a.n or 40
        start = rnd.randrange(0, len(dl) - n + 1) if len(dl) > n else 0
        block = dl[start:start + n]
        cnt = collections.Counter(e.get("speaker") for e in ctx.src.values() if e["kind"] == "dialogue" and e.get("speaker"))
        cands = uniq(ctx.src[i].get("speaker") for i in block if ctx.src[i].get("speaker"))
        letters = {s: chr(65 + k) for k, s in enumerate(cands[:26])}
        items, body = [], []
        for k, i in enumerate(block, 1):
            e = ctx.src[i]
            vi = one_line(ctx.eff(i) or "")
            el = bool(e.get("speaker")) and cnt[e["speaker"]] >= 50 and len(vi.split()) >= 8
            items.append({"k": k, "id": i, "speaker": e.get("speaker") or "", "letter": letters.get(e.get("speaker"), ""),
                          "eligible": el})
            body.append(f"{k}. " + ("[lời dẫn] " if not e.get("speaker") else "") + CJK_RE.sub("□", vi))
        meta.update(items=items, random=[it["id"] for it in items], candidates={v: k for k, v in letters.items()})
        cl = []
        for s, l in letters.items():
            v = ctx.voice_for(s)
            cl.append(f"{l} = {CJK_RE.sub('□', vi_name(ctx, s))}" + (f" — {v['giong']}" if v and v.get("giong") else ""))
        lines = [f"# T3 · seed {seed} · {len(block)} câu liền mạch, đã che tên người nói",
                 "# Giám khảo: làm theo references/giam-khao.md mục T3. Trả TSV, mỗi dòng: "
                 "k<TAB>doan (chữ cái, bỏ trống với lời dẫn)<TAB>can (0|1)<TAB>ly_do", "Ứng viên:"] + cl + [""] + body
    elif g == "P3":
        facts = notes_fact_lines()
        if not facts:
            die("notes.md chưa có dòng dữ kiện nào (mục Game, Chủ đề, Nhân vật…).")
        n = a.n or 10
        pick = sorted(rnd.sample(facts, min(n, len(facts))))
        items = []
        lines = [f"# P3 · seed {seed} · {len(pick)} dòng ngẫu nhiên của notes.md",
                 "# Giám khảo: làm theo references/giam-khao.md mục P3. Trả TSV, mỗi dòng: k<TAB>khop (1|0)<TAB>ly_do"]
        for k, (ln, body) in enumerate(pick, 1):
            ids = uniq(x.strip(".,:;") for x in re.findall(r"[^\s,;()\[\]{}“”\"']+", body))
            ids = [x for x in ids if x in ctx.src]
            urls = re.findall(r"https?://[^\s)\]]+", body)
            lines += ["", f"== {k} · notes.md dòng {ln}", "DÒNG: " + body]
            for i in ids[:4]:
                e = ctx.src[i]
                lines.append(f"  {i} · {e.get('speaker') or '-'}: {one_line(e['src'])}"
                             + (f" · EN: {one_line(e['en'])}" if e.get("en") else ""))
            for u in urls[:2]:
                lines.append(f"  link: {u}")
            if not ids and not urls:
                lines.append("  (dòng này không có id câu hay link làm căn cứ)")
            items.append({"k": k, "line": ln, "ids": ids})
        meta.update(items=items, random=[str(it["k"]) for it in items])
    else:  # P5, F3: bang doc cho nguoi dung
        n = a.n or (30 if g == "P5" else 40)
        if g == "P5":
            dl = [r for r in ctx.needs() if ctx.src[r]["kind"] == "dialogue" and not is_gop(ctx, r)][:2000]
            sh = [r for r in ctx.needs() if ctx.src[r]["kind"] in ("ui", "data") and not is_gop(ctx, r)]
            narr = [i for i in dl if not ctx.src[i].get("speaker")]
            ta_spk = {r["speaker"] for r in ctx.pairs if "ta" in [x.strip() for x in re.split(r"[/,;]", r["xung"])]}
            cnt = collections.Counter(ctx.src[i]["speaker"] for i in dl if ctx.src[i].get("speaker"))
            pools = [(narr, 6)] + [([i for i in dl if ctx.src[i].get("speaker") == s], 4) for s, _ in cnt.most_common(3)]
            pools += [([i for i in dl if loai.get(ctx.src[i].get("scene") or "") == "hai"], 3),
                      ([i for i in dl if loai.get(ctx.src[i].get("scene") or "") == "tinh_cam"
                        or ctx.src[i].get("scene") in pri], 3),
                      ([i for i in dl if ctx.src[i].get("speaker") in ta_spk], 2),
                      (sh, 4), (dl, n)]
            pick = pick_quota(rnd, pools, n)
        else:
            dl = done_reps(ctx, ("dialogue",))
            hard = [i for i in dl if ctx.src[i].get("scene") in pri
                    or loai.get(ctx.src[i].get("scene") or "") in ("hai", "tinh_cam", "18", "chien_dau")]
            pick = pick_quota(rnd, [(hard, n // 2), (dl + done_reps(ctx, ("ui", "data")), n - n // 2)], n)
        pick.sort(key=lambda i: ctx.src_index[i])
        meta.update(random=pick, flagged=[])
        todo = [i for i in pick if not ctx.done(i)]
        if todo:
            lines = [f"# {g} · seed {seed} · {len(pick)} câu tiêu biểu. Dịch trước {len(todo)} câu chưa dịch dưới đây "
                     f"(vgk.py write, dùng id đầy đủ), rồi chạy: vgk.py qa sheet {idf}"]
            for i in todo:
                e = ctx.src[i]
                lis = ctx.listener(i) if e.get("speaker") else None
                lines.append(f"@@ {i}" + (f" · {e['speaker']}" if e.get("speaker") else "") + (f" · → {lis}" if lis else ""))
                lines += ["#> " + x for x in e["src"].split("\n")]
                if e.get("en") and ctx.cfg["en_mode"] != "none":
                    lines.append("#> EN: " + one_line(e["en"]))
        else:
            lines = [f"# {g} · {len(pick)} câu · chỉ tiếng Việt. Người dùng trả lời: số câu thấy cấn + vài chữ lý do;",
                     f"# ghi kết quả: vgk.py qa record {idf} --can \"3,7\" [--xungho \"5\"]"] + sheet_lines(ctx, pick)
    atomic_write(p(idf), json.dumps(meta, ensure_ascii=False, indent=1) + "\n")
    atomic_write(p(txt), "\n".join(lines) + "\n")
    print(f"{g}: seed {seed} · {len(meta.get('random') or [])} câu" + (f" + {len(meta.get('flagged') or [])} cờ" if meta.get("flagged") else "")
          + f" → {txt} (danh sách: {idf})")
    if g in ("T2", "F2", "T3", "P3"):
        print("Giao tệp trên cho một agent giám khảo độc lập kèm references/giam-khao.md; lưu kết quả TSV rồi chạy: "
              f"vgk.py qa score <tệp kết quả> --ids {idf}")
    else:
        print("\n".join(lines))


def read_cells(path):
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            cells = [c.strip() for c in line.split("\t")]
            if cells[0].lower() in ("id", "k", "pair_id"):
                continue
            rows.append(cells)
    return rows


def p4_status():
    for d in khauvi_dirs():
        f = os.path.join(d, "p4.json")
        if os.path.exists(f):
            try:
                with open(f, encoding="utf-8") as fh:
                    return json.load(fh)
            except Exception:
                return {}
    return {}


def qa_log(ctx, q, g, seed, n, errs, ok, note=""):
    line = f"{g} {'ĐẠT' if ok else 'TRƯỢT'} ({now()})"
    q["last"] = line
    path = p(os.path.join("reports", "qa.tsv"))
    if not os.path.exists(path):
        append_text(path, "thoi_gian\tcong\tseed\tco_mau\tloi\tket_qua\tghi_chu\n")
    append_text(path, f"{now()}\t{g}\t{seed}\t{n}\t{errs}\t{'dat' if ok else 'truot'}\t{clean_cell(note)}\n")


def qa_score(ctx, q, a):
    with open(a.ids, encoding="utf-8") as f:
        meta = json.load(f)
    g = meta["gate"]
    if g not in ("T2", "F2", "T3", "P3"):
        die(f"qa score không dùng cho {g}; với P5/F3 dùng: vgk.py qa record")
    rows = read_cells(a.file)
    p4 = p4_status()
    p4note = "" if p4.get("ok") or g == "P3" else " · P4 chưa đạt: kết quả chỉ để lọc lỗi, không phải bằng chứng chất lượng"
    prev = meta.get("scored")
    if prev and q.get("last_ids") not in (None, os.path.basename(a.ids)):
        die("mẫu này đã chấm và sau đó đã chấm mẫu khác; chỉ chấm lại được mẫu gần nhất — lấy mẫu mới")
    if prev:
        # Cham lai cung mau (vd sau khi bac loi): thay ket qua lan truoc, khong tinh them mot lan.
        for key in ("T2", "T3"):
            if prev.get(key) is not None:
                q[key] = prev[key]
        q.pop("f3_bat_buoc", None)
        if prev.get("f3_bat_buoc"):
            q["f3_bat_buoc"] = prev["f3_bat_buoc"]
    before = json.loads(json.dumps({"T2": q.get("T2"), "T3": q.get("T3"), "f3_bat_buoc": q.get("f3_bat_buoc")}))
    t2, t3 = q["T2"], q["T3"]
    if g in ("T2", "F2"):
        exp = list(meta.get("random") or []) + list(meta.get("flagged") or [])
        got = qa_parse(rows, exp, lambda r: None if len(r) >= 2 and r[1].strip().lower() in QA_MUC
                       else "cột 2 phải là nang | nhe | ok")
        rand = list(meta.get("random") or [])
        heavy = [got[i] for i in rand if QA_MUC[got[i][1].strip().lower()] == "nang"]
        rebut = [r for r in heavy if len(r) >= 6 and r[5]]
        cnt = len(heavy) - len(rebut)
        n = len(rand)
        allowed = 2 if g == "F2" else max(1, n // 50)
        light = sum(1 for i in rand if QA_MUC[got[i][1].strip().lower()] == "nhe")
        allowed_l = max(1, n // 20)          # câu chưa tự nhiên, dịch sát: tối đa 5% mẫu
        ok = cnt <= allowed and light <= allowed_l
        note = (f"{cnt} lỗi nặng/{n} câu ngẫu nhiên (ngưỡng ≤{allowed}) · "
                f"{light} câu chưa tự nhiên (ngưỡng ≤{allowed_l})")
        if heavy and len(rebut) > 0.3 * len(heavy):
            note += f" · bác {len(rebut)}/{len(heavy)} lỗi (>30%): giám khảo lệch → chạy lại P4"
        if g == "T2":
            dd, ds = batches_done(ctx)
            dl = meta.get("dlg")
            if dl is None:
                dl = sum(1 for i in rand if i in ctx.src and ctx.src[i]["kind"] == "dialogue")
            t2.update(runs=t2["runs"] + 1, done_short=ds,
                      seen=sorted(set(t2.get("seen") or []) | set(meta.get("batches") or [])))
            if dl:
                t2.update(done_dlg=dd, dlg_runs=t2.get("dlg_runs", 0) + 1)
            if ok:
                t2["fails"] = 0
                if dl >= 10:
                    t2["streak"] += 1
                if t2["need_pass"]:
                    t2["need_pass"] -= 1
                    if not t2["need_pass"]:
                        t2["n"] = 50
                if t2["streak"] >= 3:
                    t2["interval"] = 20
            else:
                t2.update(streak=0, interval=10, n=100, need_pass=2, fails=t2.get("fails", 0) + 1)
                if t2["fails"] >= 2:
                    q["f3_bat_buoc"] = "T2 trượt 2 lần liền"
        else:
            q["F2"] = {"ok": ok, "time": now()}
            if not ok:
                q["f3_bat_buoc"] = "F2 trượt"
        fl = ctx.state.get("flags") or {}
        for i in exp:
            fl.pop(i, None)
    elif g == "T3":
        items = {str(it["k"]): it for it in meta.get("items") or []}
        got = qa_parse(rows, list(items), lambda r: None if len(r) >= 3 and r[2].strip() in ("0", "1")
                       else "cột 3 (can) phải là 0 hoặc 1")
        el = [k for k, it in items.items() if it["eligible"]]
        right = sum(1 for k in el if got[k][1].strip().upper() == items[k]["letter"])
        can = sum(1 for k in items if got[k][2].strip() == "1")
        acc = right / len(el) if el else 1.0
        ok = acc >= 0.8 and can <= 3
        cnt = can
        n = len(items)
        note = f"đoán đúng người nói {right}/{len(el)} câu đủ điều kiện ({acc:.0%}) · {can} câu cấn" + (
            " · ít câu đủ điều kiện, nên lấy đoạn khác" if len(el) < 5 else "")
        dd, _ = batches_done(ctx)
        t3.update(runs=t3["runs"] + 1, done_dlg=dd)
        if ok:
            t3["fails"] = 0
        else:
            t3["fails"] = t3.get("fails", 0) + 1
            if t3["fails"] >= 2:
                q["f3_bat_buoc"] = "T3 trượt 2 lần liền"
    else:  # P3: giam khao doi chieu dong notes.md voi can cu
        items = {str(it["k"]): it for it in meta.get("items") or []}
        got = qa_parse(rows, list(items), lambda r: None if len(r) >= 2 and r[1].strip() in ("0", "1")
                       else "cột 2 (khop) phải là 1 hoặc 0")
        n = len(items)
        good = sum(1 for k in items if got[k][1].strip() == "1")
        cnt = n - good
        ok = n > 0 and good >= math.ceil(0.9 * n)
        note = f"{good}/{n} dòng notes khớp căn cứ (cần ≥{math.ceil(0.9 * n)})"
        q["P3"] = {"ok": ok, "time": now()}
    meta["scored"] = dict(before, time=now(), ok=ok, note=note)
    atomic_write(a.ids, json.dumps(meta, ensure_ascii=False, indent=1) + "\n")
    q["last_ids"] = os.path.basename(a.ids)
    qa_log(ctx, q, g, meta.get("seed"), n, cnt, ok, ("chấm lại · " if prev else "") + note + p4note)
    save_state(ctx.state)
    update_handoff(ctx)
    print(f"{g}: {'ĐẠT' if ok else 'TRƯỢT'} — {note}{p4note}" + (" (chấm lại: thay kết quả lần trước)" if prev else ""))
    if q.get("f3_bat_buoc") and not before.get("f3_bat_buoc"):
        print(f"Ghi nhận: {q['f3_bat_buoc']} (F3 là tùy chọn từ 2.1; không cần báo người dùng).")
    if not ok:
        print("Trượt: sửa cả loại lỗi trong phạm vi lấy mẫu (vgk.py show --grep); lỗi máy bắt được thì thêm vào cam_mau.tsv "
              "hoặc TODO.md; rồi lấy mẫu lại." + (" T2 kế tiếp lấy 100 câu cho tới khi đạt 2 lần liền." if g == "T2" else ""))


def qa_record(ctx, q, a):
    with open(a.ids, encoding="utf-8") as f:
        meta = json.load(f)
    g = meta["gate"]
    if g not in ("P5", "F3"):
        die("qa record chỉ dùng cho P5/F3 (bảng đọc của người dùng)")
    ids = meta.get("random") or []

    def nums(s):
        out = []
        for x in split_list(s or "", ","):
            if x.isdigit() and 1 <= int(x) <= len(ids):
                out.append(ids[int(x) - 1])
        return out
    can, xh = nums(a.can), nums(a.xungho)
    allc = uniq(can + xh)
    ok = len(allc) <= 2 and not xh
    for i in allc:
        q["can"][i] = {"vi": ctx.eff(i) or "", "gate": g,
                       "ngu_canh": one_line((ctx.scenes.get(ctx.src[i].get("scene") or "") or {}).get("summary", ""))[:200]}
    note = f"{len(allc)} câu cấn ({len(xh)} sai xưng hô) / {len(ids)}" + (f" · {a.note}" if a.note else "")
    if ok and g == "P5":
        rows, per = [], collections.Counter()
        for i in ids:
            e = ctx.src[i]
            if i in allc or not e.get("speaker") or per[e["speaker"]] >= 2:
                continue
            per[e["speaker"]] += 1
            rows.append({"speaker": e["speaker"], "vi": one_line(ctx.eff(i) or ""), "nguon": "P5"})
        ex = read_tsv(p(F_NEO), NEO_COLS)
        write_tsv(p(F_NEO), NEO_COLS, ex + rows)
        note += f" · thêm {len(rows)} câu neo"
    qa_log(ctx, q, g, meta.get("seed"), len(ids), len(allc), ok, note)
    save_state(ctx.state)
    update_handoff(ctx)
    print(f"{g}: {'ĐẠT' if ok else 'TRƯỢT'} — {note}")
    if allc:
        print("Câu cấn (sửa cả loại lỗi rồi chạy vgk.py qa collect để đưa vào bộ hiệu chuẩn P4): " + ", ".join(allc))
    if not ok and g == "P5":
        print("Trượt P5: sửa luật, gửi lại người dùng tối đa 10 câu đã sửa (một lần), rồi mới dịch tiếp.")


def khauvi_write_dir():
    d = os.path.join(vgk_dir(), "khauvi")
    os.makedirs(d, exist_ok=True)
    return d


def qa_collect(ctx, q, a):
    rows, keep = [], {}
    for i, rec in (q.get("can") or {}).items():
        cur = ctx.eff(i) or ""
        if i not in ctx.src or not cur or cur == rec.get("vi"):
            keep[i] = rec
            continue
        new_a = random.random() < 0.5
        a_txt, b_txt = (cur, rec["vi"]) if new_a else (rec["vi"], cur)
        rows.append({"pair_id": f"{ctx.cfg.get('slug') or 'game'}:{i}", "ngu_canh": rec.get("ngu_canh", ""),
                     "a": one_line(a_txt), "b": one_line(b_txt), "chon": "A" if new_a else "B",
                     "can": "B" if new_a else "A", "nguon": rec.get("gate", "")})
    q["can"] = keep
    if rows:
        path = os.path.join(khauvi_write_dir(), "hieu_chuan.tsv")
        write_tsv(path, HC_COLS, read_tsv(path, HC_COLS) + rows)
        print(f"Thêm {len(rows)} cặp (bản cấn / bản đã sửa) vào {path}")
    else:
        print("Chưa có câu cấn nào đã được sửa.")
    save_state(ctx.state)


def qa_calibrate(ctx, a):
    pairs = [r for r in read_tsv(a.pairs, HC_COLS) if r["pair_id"]]
    if not a.judge:
        txt, _ = qa_files("P4")
        lines = [f"# P4 · {len(pairs)} cặp · giám khảo làm theo references/giam-khao.md mục P4.",
                 "# Trả TSV, mỗi dòng: pair_id<TAB>chon (A|B)<TAB>can (A|B|AB|trống)"]
        for r in pairs:
            lines += ["", f"== {r['pair_id']}", "ngữ cảnh: " + r["ngu_canh"], "A: " + r["a"], "B: " + r["b"]]
        atomic_write(p(txt), "\n".join(lines) + "\n")
        print(f"P4: {len(pairs)} cặp → {txt}. Giao cho agent giám khảo (không kèm đáp án), rồi chạy: "
              f"vgk.py qa calibrate --pairs {a.pairs} --judge <tệp kết quả>")
        return
    jud = {r[0]: r for r in read_cells(a.judge)}
    n = agree = 0
    user_can, hit = set(), set()
    for r in pairs:
        if r["chon"] not in ("A", "B"):
            continue
        n += 1
        j = jud.get(r["pair_id"])
        if j and len(j) >= 2 and j[1].strip().upper() == r["chon"]:
            agree += 1
        for side in r["can"].upper():
            if side in "AB":
                user_can.add((r["pair_id"], side))
                if j and len(j) >= 3 and side in j[2].upper():
                    hit.add((r["pair_id"], side))
    ag = agree / n if n else 0.0
    rc = len(hit) / len(user_can) if user_can else 0.0
    ok = n >= 40 and ag >= 0.85 and len(user_can) >= 5 and rc >= 0.7
    st = {"ok": ok, "n": n, "agree": round(ag, 3), "can": len(user_can), "recall": round(rc, 3), "time": now()}
    atomic_write(os.path.join(khauvi_write_dir(), "p4.json"), json.dumps(st, ensure_ascii=False) + "\n")
    why = [] if ok else [x for x, bad in (("cần ≥40 cặp", n < 40), ("chọn trùng <85%", ag < 0.85),
                                           ("cần ≥5 câu cấn", len(user_can) < 5), ("bắt câu cấn <70%", rc < 0.7)) if bad]
    print(f"P4: {'ĐẠT' if ok else 'CHƯA ĐẠT'} — {n} cặp · chọn trùng {ag:.0%} · bắt {len(hit)}/{len(user_can)} câu cấn ({rc:.0%})"
          + (" · " + "; ".join(why) if why else ""))


def cmd_qa(a):
    if a.qcmd == "calibrate":
        qa_calibrate(None, a)
        return
    ctx = Ctx()
    q = qa_cfg(ctx)
    if a.qcmd == "due":
        due = qa_due(ctx)
        print("CỔNG ĐẾN HẠN: " + "; ".join(due) if due else "Chưa có cổng nào đến hạn.")
    elif a.qcmd == "sample":
        qa_sample(ctx, q, a)
        save_state(ctx.state)
    elif a.qcmd == "sheet":
        with open(a.ids, encoding="utf-8") as f:
            meta = json.load(f)
        todo = [i for i in meta.get("random") or [] if not ctx.done(i)]
        if todo:
            die(f"còn {len(todo)} câu chưa dịch trong mẫu (vd {todo[0]})")
        lines = [f"# {meta['gate']} · {len(meta['random'])} câu · chỉ tiếng Việt",
                 f"# ghi kết quả: vgk.py qa record {a.ids} --can \"3,7\" [--xungho \"5\"]"] + sheet_lines(ctx, meta["random"])
        txt, _ = qa_files(meta["gate"] + "-sheet")
        atomic_write(p(txt), "\n".join(lines) + "\n")
        print("\n".join(lines))
    elif a.qcmd == "score":
        qa_score(ctx, q, a)
    elif a.qcmd == "record":
        qa_record(ctx, q, a)
    elif a.qcmd == "collect":
        qa_collect(ctx, q, a)
    elif a.qcmd == "status":
        p4 = p4_status()
        t2 = q["T2"]
        print("P4: " + ("ĐẠT" if p4.get("ok") else "chưa đạt") + (f" ({p4.get('n')} cặp, trùng {p4.get('agree')}, "
                                                                 f"bắt cấn {p4.get('recall')}, {p4.get('time')})" if p4 else ""))
        if ctx.cfg.get("qa_dinh_ky") or t2["runs"]:
            print(f"T2: {t2['runs']} lần ({t2['dlg_runs']} lần có thoại) · đạt liền {t2['streak']} · mỗi {t2['interval']} lô thoại"
                  f" hoặc 3 lô ngắn · cỡ mẫu {t2['n']} · T3: {q['T3']['runs']} lần")
        else:
            print("T2/T3: tắt (qa_dinh_ky = false) · chỉ kiểm cuối F2")
        for gname in ("P3", "F2"):
            if q.get(gname):
                print(f"{gname}: {'ĐẠT' if q[gname].get('ok') else 'TRƯỢT'} ({q[gname].get('time')})")
        print("F3: tùy chọn (người dùng đọc khi chơi)" + (f" · ghi nhận: {q['f3_bat_buoc']}" if q.get("f3_bat_buoc") else ""))
        print(f"Câu bị cờ chờ T2: {len(ctx.state.get('flags') or {})} · câu cấn chờ thu vào hiệu chuẩn: {len(q['can'])}")
        due = qa_due(ctx)
        print("CỔNG ĐẾN HẠN: " + "; ".join(due) if due else "Chưa có cổng nào đến hạn.")
        path = p(os.path.join("reports", "qa.tsv"))
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                tail = f.read().strip().split("\n")[1:][-5:]
            for ln in tail:
                print("  " + ln.replace("\t", " · "))


# ---------------------------------------------------------------- do phu trich, ung vien thuat ngu, uoc tinh

TEXT_EXT = {".json", ".txt", ".csv", ".tsv", ".xml", ".yaml", ".yml", ".ini", ".rpy", ".ks", ".tjs", ".po", ".pot",
            ".lua", ".js", ".gd", ".tscn", ".tres", ".md", ".html", ".htm", ".srt", ".vtt", ".ass", ".ssa", ".scn",
            ".msg", ".dat", ".cfg", ".nut", ".asset", ".bytes", ".locres_json"}
SRC_CHAR_RE = {"ja": re.compile("[぀-ヿ一-鿿]"), "zh": re.compile("[一-鿿]"),
               "ko": re.compile("[가-힯]")}
EN_STR_RE = re.compile(r"[\"'“]([A-Za-z][^\"'“”\n]{12,200}?)[\"'”]")


def decode_any(data, lang):
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:].decode("utf-8", "replace")
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", "replace")
    for enc in ("utf-8", "cp932" if lang == "ja" else "gb18030" if lang == "zh" else "cp949" if lang == "ko" else "utf-8"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def read_skip(path):
    out = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                t = line.strip()
                if not t or t.startswith("#"):
                    continue
                k, _, why = t.partition("#")
                out[k.strip().replace("\\", "/")] = why.strip()
    return out


SRC_RUN_RE = {"ja": re.compile("[\u3040-\u30ff\u3005\u3006\u4e00-\u9fff]{2,}"), "zh": re.compile("[\u4e00-\u9fff]{2,}"),
              "ko": re.compile("[\uac00-\ud7af]{2,}")}
F_CIGNORE = "coverage_ignore.txt"


def json_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from json_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from json_strings(v)


def text_units(texts, lang):
    """Don vi so khop: chuoi chu nguon lien nhau (ja/zh/ko) hoac dong co tu 3 tu tro len (en)."""
    out = []
    for t in texts:
        if lang == "en":
            for ln in t.split("\n"):
                ln = " ".join(ln.split())
                if len(ln.split()) >= 3 and re.search("[a-z]", ln):
                    out.append(ln)
        else:
            out += SRC_RUN_RE.get(lang, SRC_RUN_RE["ja"]).findall(t)
    return out


MEDIA_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tga", ".dds", ".psd", ".ktx", ".pvr", ".ico",
             ".ogg", ".mp3", ".wav", ".m4a", ".flac", ".opus", ".wma", ".aac", ".mid", ".midi",
             ".mp4", ".webm", ".avi", ".mov", ".wmv", ".mkv", ".ogv", ".usm", ".bik", ".bk2",
             ".ttf", ".otf", ".ttc", ".woff", ".woff2", ".fnt"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tga", ".dds", ".psd"}
PACKED_EXT = {".xp3", ".pak", ".rpa", ".rpyc", ".pck", ".bundle", ".unity3d", ".arc", ".rgss3a", ".rgss2a", ".rgssad",
              ".wolf", ".npk", ".cpk", ".afs", ".pac", ".zip", ".7z", ".rar", ".gz", ".lz4", ".cab", ".obb", ".apk"}
IMG_TEXT_HINT = re.compile(r"title|menu|button|btn|logo|tutorial|help|text|word|hud|ui[_-]|chapter|ending|caption|"
                           r"label|tip|message|msg|name", re.I)
UTF8_RUN_RE = {
    "ja": re.compile(rb"(?:[\xe4-\xe9][\x80-\xbf]{2}|\xe3[\x81-\x83][\x80-\xbf]){3,}"),
    "zh": re.compile(rb"(?:[\xe4-\xe9][\x80-\xbf]{2}){3,}"),
    "ko": re.compile(rb"(?:[\xea-\xed][\x80-\xbf]{2}){3,}"),
}
COV_BIG = 4 << 30


def byte_entropy(b):
    if not b:
        return 0.0
    n = len(b)
    return -sum(c / n * math.log2(c / n) for c in collections.Counter(b).values())


SJIS_RUN_RE = re.compile(rb"(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]){4,}")
U16_RUN_RE = re.compile(rb"(?:[\x20-\x7e]\x00|[\x00-\xff][\x30\x4e-\x9f\xac-\xd7]|[\x01-\x9f]\xff){3,}\x00\x00")
KANA_CH_RE = re.compile("[\u3041-\u30fa]")


def scan_binary(full, lang):
    """Chuoi chu nguon trong tep nhi phan, doc tung khuc; kem do hon loan cua 1 MB dau.
    UTF-8 lien nhau >= 3 ky tu; khong thay thi thu Shift-JIS (ja, can >= 2 chu kana) va chuoi UTF-16
    co tien to do dai am kieu FString cua Unreal (.locres, .uasset)."""
    rx = UTF8_RUN_RE.get(lang)
    src_re = SRC_RUN_RE.get(lang)
    hits, alt, ent, first, tail = [], [], 0.0, True, b""
    with open(full, "rb") as fh:
        while True:
            chunk = fh.read(32 << 20)
            if not chunk:
                break
            if first:
                ent, first = byte_entropy(chunk[:1 << 20]), False
            buf = tail + chunk
            if rx is not None:
                for m in rx.finditer(buf):
                    if m.start() >= len(tail):   # chuoi bat dau trong khuc truoc da lay o lan truoc
                        hits.append(m.group(0).decode("utf-8", "ignore"))
            if not hits and src_re is not None and ent < 7.5:
                if lang == "ja" and ent < 7.0:
                    for m in SJIS_RUN_RE.finditer(buf):
                        if m.start() < len(tail):
                            continue
                        t = m.group(0).decode("cp932", "ignore")
                        if len(KANA_CH_RE.findall(t)) >= 2 and src_re.search(t):
                            alt.append(t)
                for m in U16_RUN_RE.finditer(buf):
                    if m.start() < len(tail):
                        continue
                    # FString: int32 am = -(so ky tu + 1), roi chuoi UTF-16, roi 00 00; chuoi co the lech 1 byte so voi m
                    for s0 in range(max(m.start(), 4), m.start() + 8):
                        n = int.from_bytes(buf[s0 - 4:s0], "little", signed=True)
                        if -4096 <= n <= -2:
                            e0 = s0 + 2 * (-n - 1)
                            if buf[e0:e0 + 2] == b"\x00\x00":
                                t = buf[s0:e0].decode("utf-16-le", "ignore")
                                if src_re.search(t):
                                    alt.append(t)
                                    break
            tail = buf[-256:]
    return (hits or alt), ent


def cmd_coverage(a):
    """P1 (truoc khi dich): moi chuoi chu nguon trong moi tep phai co trong src.jsonl, hoac bo co ly do.
    --sau-va (truoc khi giao): quet thu muc game DA VA, con chu nguon la sot (tru chuoi giu nguyen co chu dich)."""
    after = bool(getattr(a, "sau_va", False))
    ctx = Ctx(quiet=True) if after else Ctx(need_plan=False, quiet=True)
    lang = ctx.cfg["source_lang"]
    have = collections.Counter((e.get("file") or "").replace("\\", "/").lower() for e in ctx.src.values() if e.get("file"))
    if after:
        keep = [ctx.src[i]["src"] for i in ctx.minor_all
                if not (ctx.cfg["minor_fallback"] == "en" and ctx.src[i].get("en"))]
        keep += [ctx.src[i]["src"] for i in ctx.auto if i in ctx.src]
        known = set(text_units(keep, lang))
    else:
        known = set(text_units([e["src"] for e in ctx.src.values()], lang))
    if os.path.exists(p(F_CIGNORE)):
        with open(p(F_CIGNORE), encoding="utf-8-sig") as f:
            known |= set(text_units([ln.rstrip("\r\n").replace("\\n", "\n") for ln in f if not ln.startswith("#")], lang))
    skips = read_skip(p(F_CSKIP))
    root = os.path.abspath(a.dir)
    work = os.path.abspath(WORK)
    skipdirs = (".git", "__pycache__", "_viethoa_backup", "_viethoa_work")
    assets = set()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in skipdirs]
        assets |= {os.path.splitext(f)[0] for f in fn}
    need = a.min if a.min is not None else (3 if lang == "en" else 1)
    rows, unread, imgs, nbin = [], [], [], 0

    def skip_of(low):
        return next((k for k in skips if (fnmatch.fnmatch(low, k.lower()) if any(c in k for c in "*?[")
                                          else low.endswith(k.lower()))), None)
    for dp, dn, fn in os.walk(root):
        if (os.path.abspath(dp) + os.sep).startswith(work + os.sep):
            dn[:] = []
            continue
        dn[:] = [d for d in dn if d not in skipdirs]
        for f in fn:
            full = os.path.join(dp, f)
            ext = os.path.splitext(f)[1].lower()
            rel = os.path.relpath(full, root).replace("\\", "/")
            low = rel.lower()
            if ext in MEDIA_EXT:
                if ext in IMG_EXT and IMG_TEXT_HINT.search(f):
                    imgs.append(rel)
                continue
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            if not size:
                continue
            sk = skip_of(low)
            if size > COV_BIG:
                unread.append((rel, size, "quá lớn, chưa quét", sk))
                continue
            texts, binary = None, False
            try:
                with open(full, "rb") as fh:
                    head = fh.read(4096)
                is_text = (b"\x00" not in head or head[:2] in (b"\xff\xfe", b"\xfe\xff")) and ext not in PACKED_EXT
                if is_text and size <= (64 << 20):
                    with open(full, "rb") as fh:
                        data = fh.read()
                    t = decode_any(data, lang)
                    if ext == ".json":
                        try:
                            texts = list(json_strings(json.loads(t)))
                        except Exception:
                            texts = None
                    if texts is None and lang == "en" and ext in (".csv", ".tsv"):
                        try:
                            texts = [c for row in csv.reader(io.StringIO(t), delimiter="\t" if ext == ".tsv" else ",")
                                     for c in row]
                        except csv.Error:
                            texts = None
                    if texts is None and lang == "en" and ext in (".txt", ".srt", ".vtt", ".ass", ".ssa"):
                        texts = t.split("\n")
                    if texts is None:
                        if lang == "en" and ext not in TEXT_EXT and not a.all_files:
                            continue
                        texts = [m.group(1) for m in EN_STR_RE.finditer(t)] if lang == "en" else [t]
                elif lang == "en":
                    # Nguon EN: khong do duoc chuoi trong tep nhi phan; chi bao tep goi/nen.
                    with open(full, "rb") as fh:
                        ent = byte_entropy(fh.read(1 << 20))
                    if ext in PACKED_EXT or (ent > 7.5 and size >= (64 << 10)):
                        unread.append((rel, size, f"tệp gói {ext}" if ext in PACKED_EXT else "dữ liệu nén/mã hóa", sk))
                    continue
                else:
                    hits, ent = scan_binary(full, lang)
                    nbin += 1
                    if not hits:
                        if ext in PACKED_EXT or (ent > 7.5 and size >= (64 << 10)):
                            unread.append((rel, size, f"tệp gói {ext}" if ext in PACKED_EXT else "dữ liệu nén/mã hóa", sk))
                        continue
                    texts, binary = hits, True
            except OSError:
                continue
            texts = [x for x in texts if x.strip() not in assets]  # ten tep anh/am thanh, khong phai chu hien thi
            units = text_units(texts, lang)
            if not units:
                continue
            miss_u = [u for u in units if u not in known]
            msize = len(miss_u) if lang == "en" else sum(len(u) for u in miss_u)
            total = len(units) if lang == "en" else sum(len(u) for u in units)
            cov = any(h and (h.endswith(low) or low.endswith(h)) for h in have)
            if msize < need:
                state = "ok"
            elif after:
                state = "CÒN"
            else:
                state = "THIẾU" if cov else ("NHỊ" if binary else "CHƯA")
            rows.append((rel, total, msize, state, sk, uniq(miss_u)[:5]))
    miss = [r for r in rows if r[3] != "ok" and not r[4]]
    ur = [u for u in unread if not u[3]]
    unit = "chuỗi" if lang == "en" else "ký tự nguồn"
    rep = os.path.join("reports", f"{'sau-va' if after else 'coverage'}-{stamp()}.txt")
    os.makedirs(p("reports"), exist_ok=True)
    labels = {"CHƯA": "CHƯA TRÍCH", "THIẾU": "TRÍCH THIẾU", "NHỊ": "NHỊ PHÂN CÓ CHỮ", "CÒN": "CÒN CHỮ GỐC"}

    def lab(r):
        if r[3] == "ok":
            return "sạch" if after else "đã trích"
        if r[4]:
            return "bỏ: " + (skips[r[4]] or "(có trong coverage_skip.txt)")
        return labels[r[3]]
    out = [f"{lab(r)}\t{r[2]}/{r[1]}\t{r[0]}" + (("\tvd: " + " | ".join(x[:40] for x in r[5])) if r[5] and r[3] != "ok" else "")
           for r in sorted(rows, key=lambda x: -x[2])]
    out += [f"{'bỏ: ' + (skips[u[3]] or '(có lý do)') if u[3] else 'KHÔNG ĐỌC ĐƯỢC'}\t{fmt_n(u[1])} byte\t{u[0]}\t{u[2]}"
            for u in unread]
    out += [f"ảnh có thể có chữ\t-\t{x}" for x in imgs]
    atomic_write(p(rep), "\n".join(out) + "\n")
    cnt = collections.Counter(r[3] for r in miss)
    if after:
        print(f"Quét bản đã vá: {len(rows)} tệp có chữ nguồn · sạch {sum(1 for r in rows if r[3] == 'ok')} · "
              f"bỏ có lý do {sum(1 for r in rows if r[3] != 'ok' and r[4])} · CÒN CHỮ GỐC {len(miss)} tệp"
              f" ({fmt_n(sum(r[2] for r in miss))} {unit}) · KHÔNG ĐỌC ĐƯỢC {len(ur)} → {rep}")
    else:
        print(f"Độ phủ (P1): {len(rows)} tệp có chữ nguồn · đủ {sum(1 for r in rows if r[3] == 'ok')} · "
              f"bỏ có lý do {sum(1 for r in rows if r[3] != 'ok' and r[4])} · CHƯA TRÍCH {cnt['CHƯA']} · "
              f"TRÍCH THIẾU {cnt['THIẾU']} · NHỊ PHÂN CÓ CHỮ {cnt['NHỊ']} · KHÔNG ĐỌC ĐƯỢC {len(ur)} → {rep}")
    for r in sorted(miss, key=lambda x: -x[2])[:30]:
        print(f"  {lab(r)}: {r[0]}: {fmt_n(r[2])}/{fmt_n(r[1])} {unit} " + ("còn trong bản đã vá" if after else "chưa có trong src")
              + (f" · vd: {r[5][0][:40]}" if r[5] else ""))
    for u in ur[:20]:
        print(f"  KHÔNG ĐỌC ĐƯỢC: {u[0]} ({u[2]}, {fmt_n(u[1])} byte)")
    if imgs:
        print(f"Ảnh có thể có chữ: {len(imgs)} tệp (máy không đọc chữ trong ảnh; kiểm bằng bản vá đánh dấu: vgk.py export --danh-dau)")
    if miss or ur:
        if after:
            print("Còn chữ gốc: câu chưa dịch, chưa ghi được vào game, hoặc chưa trích → trích thêm, dịch nốt, build lại rồi quét lại. "
                  "Chuỗi cố ý giữ (không hiện cho người chơi) ghi coverage_ignore.txt; cả tệp: coverage_skip.txt kèm lý do.")
        else:
            print("Trích thêm bằng adapter; chuỗi không hiện cho người chơi thì adapter ghi vào coverage_ignore.txt; "
                  "cả tệp không hiện thì ghi coverage_skip.txt: '<đường dẫn hoặc mẫu *>  # lý do'. Tệp không đọc được: "
                  "bung bằng adapter rồi quét thư mục đã bung, hoặc ghi lý do vào coverage_skip.txt.")
    key = "coverage_sau_va" if after else "coverage"
    ctx.state[key] = {"time": now(), "missing": len(miss), "unread": len(ur), "files": len(rows), "binary": nbin}
    save_state(ctx.state)
    sys.exit(1 if (miss or ur) else 0)


KO_PARTICLES = ("은", "는", "이", "가", "을", "를", "의", "에", "도", "로", "와", "과", "께", "님")
# Tu thong dung khong bao gio la thuat ngu: loai khoi ung vien (zh/ko dem n-gram nen de ngap).
ZH_STOP = set("""我们 你们 他们 她们 它们 咱们 自己 大家 什么 怎么 怎样 为什么 这个 那个 这些 那些 这里 那里 这样 那样 这么
那么 哪里 哪个 一个 一下 一起 一点 一些 一直 一定 一样 一般 一切 已经 现在 刚才 马上 立刻 然后 之后 以后 以前 之前 时候 今天 明天
昨天 晚上 早上 可以 可能 应该 必须 需要 想要 希望 知道 觉得 认为 看到 看看 听到 听说 告诉 喜欢 讨厌 如果 因为 所以 但是 可是 不过
虽然 而且 或者 还是 就是 只是 不是 没有 不要 不会 不能 不用 不行 不错 没事 没关系 对不起 谢谢 真的 当然 其实 确实 果然 居然 竟然
难道 到底 究竟 终于 突然 好像 似乎 也许 大概 非常 特别 十分 有点 有些 还有 还要 东西 事情 地方 问题 意思 样子 办法 关系 感觉 声音
出来 起来 过来 回来 下去 上去 进去 出去 进来 回去 过去 下来 上来 开始 结束 继续 准备 决定 发现 出现 帮忙 帮助 等等 怎么办 怎么样
什么样 为了 关于 对于 根据 通过 之间 之中 里面 外面 上面 下面 前面 后面 旁边 中间 一边 别人 女人 男人 孩子 朋友 先生 小姐 大人
老师 同学 哥哥 姐姐 弟弟 妹妹 父亲 母亲 爸爸 妈妈 这次 那次 一次 每次 有人 没人 这种 那种 各种 所有 全部 每个 任何 其他 其它
别的 这边 那边 好的 是的 好了 算了 走吧 来吧 快点 小心 注意 放心 真是 不好 好吧 是吗 对吗 一会 一样 可惜 原来 本来 后来 起码 至少
只有 只要 不管 无论 而已 罢了 不如 比较 更加 最后 最近 以为 打算 记得 忘记 相信 明白 清楚 了解 理解 同意 答应 拒绝 离开 回家
时间 世界 人生 生活 工作 身体 心里 眼睛 地上 天下 一天 两个 几个 多少 很多 不少 一半 自然 如此 这时 此时 那时 当时 刚刚 正在""".split())
ZH_EDGE = set("的了是吗呢吧啊呀哦嗯着过把被给让和与也都就还很太么们在我你他她它这那不没说要会能去来个")
KO_STOP = set("""그리고 그래서 하지만 그런데 그러나 그럼 그냥 정말 진짜 아주 너무 조금 많이 지금 오늘 내일 어제 여기 거기 저기
이것 그것 저것 이거 그거 저거 우리 너희 저희 당신 자기 사람 무엇 누구 어디 언제 어떻게 그래 그래요 아니 아니요 감사합니다
미안해 괜찮아 알았어 있어 없어 했어 해요 합니다 입니다 거야 같아 같은 다시 이제 벌써 아직 먼저 나중 정도 생각 시간 이야기
얘기 때문 그렇게 이렇게 저렇게 좋아 싫어 빨리 천천히 혹시 역시 물론 모두 전부 하나 다른 어떤 무슨 이런 그런 저런 정말로""".split())


def term_candidates(ctx, top, minc):
    lang = ctx.cfg["source_lang"]
    have = {r["src"] for r in ctx.gloss if r["src"]}
    skip = set(read_skip(p(F_GSKIP)))
    cnt, ex = collections.Counter(), {}
    for eid, e in ctx.src.items():
        t = e["src"]
        ws = set()
        if lang == "ja":
            for m in re.finditer("[ァ-ヺー・]{2,}", t):
                w = m.group(0).strip("・").lstrip("ー")
                if len(w) >= 2:
                    ws.add(w)
        elif lang == "zh":
            for run in re.findall("[一-鿿]{2,}", t):
                for L in (2, 3, 4):
                    for i in range(0, len(run) - L + 1):
                        w = run[i:i + L]
                        if w not in ZH_STOP and w[0] not in ZH_EDGE and w[-1] not in ZH_EDGE:
                            ws.add(w)
        elif lang == "ko":
            for w in re.findall("[가-힯]{2,}", t):
                if len(w) > 2 and w.endswith(KO_PARTICLES):
                    w = w[:-1]
                if len(w) >= 2 and w not in KO_STOP:
                    ws.add(w)
        else:
            for m in re.finditer(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", t):
                w = m.group(1)
                if w not in ("I", "The", "A", "An", "But", "And", "Oh", "Yes", "No", "What", "Why", "How"):
                    ws.add(w)
        for w in ws:  # dem so cau co tu, khong dem lap trong mot cau
            cnt[w] += 1
            ex.setdefault(w, eid)
    if lang == "zh":
        # bo n-gram nam tron trong n-gram dai hon co tan suat gan bang
        mx = {}
        for x, n in list(cnt.items()):
            if len(x) >= 3:
                for y in (x[:-1], x[1:]):
                    if mx.get(y, -1) < n:
                        mx[y] = n
        for w in sorted([w for w in cnt if len(w) < 4], key=len):
            if w in mx and mx[w] >= 0.8 * cnt[w]:
                cnt[w] = 0
    spk = collections.Counter(e.get("speaker") for e in ctx.src.values() if e.get("speaker"))
    speakers = [s for s, _ in spk.most_common() if s not in have and s not in skip and s != "_ke"
                and not re.search(r"#\d+$", s)]
    for eid, e in ctx.src.items():
        if e.get("speaker") in speakers:
            ex.setdefault(e["speaker"], eid)
    for s in speakers:
        cnt[s] = max(cnt[s], spk[s])
    cands = [w for w, n in cnt.most_common() if n >= minc and w not in have and w not in skip and w not in speakers][:top]
    names = []; nset = set(); cset = set(cands)
    for eid, e in ctx.src.items():
        s = e["src"].strip()
        if e["kind"] in ("data", "ui") and 1 < len(s) <= 16 and ("name" in eid.lower() or (e.get("note") or "").startswith("tên")):
            if s not in have and s not in skip and s not in cset and s not in nset and s not in speakers:
                names.append(s); nset.add(s)
                ex.setdefault(s, eid)
    return speakers + cands, names, cnt, ex


def cmd_term_candidates(a):
    ctx = Ctx(need_plan=False)
    cands, names, cnt, ex = term_candidates(ctx, a.top, a.min)
    allc = cands + names
    print(f"Ứng viên tên/thuật ngữ chưa quyết (P3): {len(allc)} (người nói + lặp ≥{a.min} lần: {len(cands)}, "
          f"trường tên dữ liệu: {len(names)})")
    for w in allc[:80]:
        print(f"  {w}\t{cnt.get(w) or 1}\t{ex.get(w, '')}")
    if len(allc) > 80:
        print(f"  … và {len(allc) - 80} mục khác")
    if allc:
        print("Mỗi mục: dịch rồi nạp (vgk.py term import / @@term), hoặc bỏ qua: vgk.py term skip <gốc…> --note 'lý do'.")
    sys.exit(1 if allc else 0)


def cmd_term_skip(a):
    note = f"  # {clean_cell(a.note)}" if a.note else ""
    have = read_skip(p(F_GSKIP))
    new = [x for x in a.items if x not in have]
    if not os.path.exists(p(F_GSKIP)):
        append_text(p(F_GSKIP), "# Ứng viên tên/thuật ngữ đã quyết là không cần glossary. Mỗi dòng: '<gốc>  # lý do'.\n")
    if new:
        append_text(p(F_GSKIP), "".join(f"{x}{note}\n" for x in new))
    print(f"Bỏ qua thêm {len(new)} mục (tổng {len(have) + len(new)})")


def cmd_estimate(a):
    ctx = Ctx()
    lang = ctx.cfg["source_lang"]
    pend = [r for r in ctx.needs() if not ctx.done(r)]
    cps = {"ja": 1.0, "zh": 0.9, "ko": 1.1, "en": 4.0}.get(lang, 2.0)
    sc = sum(len(ctx.src[r]["src"]) for r in pend)
    ec = sum(len(ctx.src[r].get("en") or "") for r in pend) if ctx.cfg["en_mode"] == "all" else 0
    t_in = sc / cps + ec / 4.0
    t_out = sc * LEN_RATIO_MEAN.get(lang, 2.5) / 2.6
    nb = len({ctx.batch_of.get(r) for r in pend})
    nbd = len({ctx.batch_of.get(r) for r in pend if ctx.src[r]["kind"] == "dialogue"})
    per_batch = int(a.per_batch)
    qa = (nbd // 10 + 1) * 40000 if load_cfg().get("qa_dinh_ky") else 0
    qa += 250000   # kiem cuoi F2 (mot lan)
    total = t_in + t_out + nb * per_batch + qa
    print(f"Ước tính thô cho {fmt_n(len(pend))} câu còn lại, {nb} lô: chữ đầu vào ~{fmt_n(int(t_in))} token · "
          f"đầu ra ~{fmt_n(int(t_out))} token · ngữ cảnh phiên ~{fmt_n(nb * per_batch)} ({per_batch}/lô, phần lớn được cache) · "
          f"cổng QA ~{fmt_n(qa)} → tổng ~{fmt_n(int(total))} token")
    budget = ctx.cfg.get("ngan_sach_token") or ctx.root_cfg.get("ngan_sach_token")
    if budget:
        if total > float(budget):
            print(f"VƯỢT NGÂN SÁCH {fmt_n(int(budget))} token: dừng, báo người dùng 1 dòng, chờ duyệt.")
            sys.exit(3)
        print(f"Trong ngân sách {fmt_n(int(budget))} token.")
    else:
        print("Chưa đặt ngân sách (ngan_sach_token): chỉ báo số ước tính cho người dùng, không dừng.")


# ---------------------------------------------------------------- chuot lai hang loat (thay chuot.py)

def polish_lints(ctx, eid, vi):
    """Lint khi chuot: loi kiem tra + goi y van phong (toi lap, cau cut, thieu danh xung)."""
    out = []
    errs, ws = validate(ctx, eid, vi, force=eid in set(ctx.state.get("force", [])))
    pe, pw = pair_lint(ctx, eid, vi)
    for c, m in errs + pe:
        out.append(("LỖI " + c, m))
    for c, m in ws + pw + style_warns(ctx, eid, vi):
        out.append((c, m))
    e = ctx.src[eid]
    if len(TOI_RE.findall(vi)) >= 3:
        out.append(("tôi lặp", f"{len(TOI_RE.findall(vi))} lần 'tôi' trong một câu"))
    if e["kind"] == "dialogue" and not e.get("speaker"):
        for sent in re.split(r"(?<=[.!?…])\s+", vi.strip()):
            w = re.findall(r"[^\W\d_]+", sent)
            if 0 < len(w) <= 2 and not sent.strip().startswith(("“", "\"", "(")):
                out.append(("câu cụt", f"'{sent.strip()[:30]}' — viết thành câu trọn (có chủ ngữ)"))
                break
    if e["kind"] == "dialogue" and e.get("speaker") and len(vi.split()) >= 10:
        rows = ctx.pair_rows(e["speaker"], ctx.listener(eid), eid)
        terms = {w for r in rows for x in re.split(r"[/,;]", r["xung"] + "/" + r["goi"]) for w in [x.strip().lower()] if w}
        low = vi.lower()
        names = {r["vi"].lower() for r in ctx.gloss if r["type"] in ("nhan_vat", "ten") and r["vi"]}
        if terms and not any(word_in(t, low) for t in terms) and not any(n in low for n in names):
            out.append(("thiếu danh xưng?", "câu thoại dài không có xưng/gọi theo bảng cũng không có tên"))
    if emotion_missing(ctx, e):
        out.append(("LỖI thiếu Cảm xúc:", f"cảnh {e.get('scene')}"))
    return out


def cmd_polish(a):
    ctx = Ctx()
    pol = ctx.state.setdefault("polish", {})
    pol.setdefault("done", [])
    dlg = [b for b in ctx.batches if b["cls"] == "dialogue"]
    if a.pcmd == "status":
        nx = next((b["n"] for b in dlg if b["n"] not in pol["done"]), None)
        print(f"Chuốt lại: {len(pol['done'])}/{len(dlg)} lô thoại" + (f" · kế tiếp: lô {nx}" if nx else " · xong hết"))
        return
    if a.pcmd == "next":
        b = next((b for b in dlg if b["n"] not in pol["done"] and b["n"] >= (a.batch or 0)), None)
        if b is None:
            print("Đã chuốt hết các lô thoại.")
            return
        show = ctx.batch_reps(b)
        en_all, en_ids = en_selection(ctx, a.en, b, show)
        print(f"CHUỐT LẠI lô {b['n']}: dòng '#> VI:' là bản hiện tại; chỉ write những câu cần đổi và câu chưa dịch.")
        emit_batch(ctx, b, show, en_all, en_ids, vi_lines=True)
        return
    if a.pcmd == "done":
        nums = parse_nums(a.n)
        have = {x["n"] for x in dlg}
        bad = [n for n in nums if n not in have]
        if bad:
            die("không phải lô thoại: " + ", ".join(map(str, bad[:10])))
        for n in nums:
            if n not in pol["done"]:
                pol["done"].append(n)
        save_state(ctx.state)
        update_handoff(ctx)
        print(f"Đã đánh dấu chuốt xong {len(nums)} lô ({a.n}) · {len(pol['done'])}/{len(dlg)} lô thoại")
        return
    b = next((x for x in ctx.batches if x["n"] == a.n), None)
    if b is None:
        die(f"không có lô {a.n}")
    reps = ctx.batch_reps(b)
    if a.pcmd == "lint":
        n = 0
        for i in reps:
            vi = ctx.eff(i)
            if vi is None:
                print(f"{i}: chưa dịch")
                n += 1
                continue
            if is_gop(ctx, i):
                continue
            for c, m in polish_lints(ctx, i, vi):
                print(f"{i}: {c}: {m}")
                n += 1
        print(f"Lint lô {b['n']}: {n} mục")
    elif a.pcmd == "doc":
        last = None
        for i in reps:
            e = ctx.src[i]
            if e.get("scene") != last:
                last = e.get("scene")
                r = ctx.scenes.get(last or "")
                print(f"\n[{last}] " + (one_line(r["summary"]) if r else ""))
            vi = ctx.eff(i)
            if vi is None or is_gop(ctx, i):
                continue
            spk = vi_name(ctx, e.get("speaker"))
            print((f"{spk}: " if spk else "") + one_line(vi))


# ---------------------------------------------------------------- vong phan hoi: phieu bao, doc lai, doc chuong, cau anh huong

DOC_CATS = ("câu nén", "thiếu dấu kết", "thiếu dấu hỏi", "tự xưng khác bảng xưng hô", "gọi lệch bảng",
            "giới tính lệch hồ sơ", "dịch sát", "dài bất thường", "chữ Anh sót")


def cmd_phieu(a):
    ctx = Ctx(need_plan=False, quiet=True)
    rows = phieu_rows()
    if getattr(a, "phcmd", None) == "dong":
        want = None if a.n == "all" else set(split_list(a.n, ","))
        k = 0
        for r in rows:
            if r["trang_thai"] != "đóng" and (want is None or r["n"] in want):
                r["trang_thai"] = "đóng"
                if a.tra_loi:
                    r["tra_loi"] = a.tra_loi
                k += 1
        if k:
            write_tsv(p(F_PHIEU), PHIEU_COLS, rows)
        print(f"Đã đóng {k} phiếu · còn mở {len(phieu_open(rows))}")
        return
    show = rows if a.all else phieu_open(rows)
    for r in show:
        e = ctx.src.get(r["id"]) or {}
        where = " · ".join(x for x in (f"lô {r['lo']}" if r["lo"] else "", r["id"], e.get("speaker") or "") if x)
        print(f"#{r['n']} [{r['trang_thai']}] " + (where + ": " if where else "") + r["noi_dung"]
              + (f" → {r['tra_loi']}" if r["tra_loi"] else ""))
    print(f"({len(show)} phiếu{'' if a.all else ' đang mở'})")


def dlg_done_ids(ctx):
    return [r for b in ctx.batches if b["cls"] == "dialogue" for r in ctx.batch_reps(b)
            if ctx.done(r) and not is_gop(ctx, r)]


def cmd_doclai(a):
    """N cau thoai da dich gan nhat truoc cho dang dich: nguoi dich moi doc de bat giong ban dich dang dung."""
    doclai_print(Ctx(quiet=True), a.n)


def doclai_print(ctx, n, upto=None):
    dlg = [b for b in ctx.batches if b["cls"] == "dialogue"]
    nxt = next((b for b in dlg if ctx.batch_pending(b)), None)
    stop = upto if upto is not None else (nxt["n"] if nxt is not None else None)
    ids = []
    for b in dlg:
        ids += [i for i in ctx.batch_reps(b) if ctx.done(i) and not is_gop(ctx, i)]
        if stop is not None and b["n"] >= stop:
            break
    ids = ids[-n:] if n > 0 else []
    if not ids:
        print("(chưa có câu thoại nào đã dịch)")
        return
    print(f"ĐỌC LẠI {len(ids)} câu đã dịch gần nhất (đọc như truyện để bắt giọng đang dùng; không sửa ở đây):")
    last = None
    for i in ids:
        e = ctx.src[i]
        if e.get("scene") != last:
            last = e.get("scene")
            print(f"[{last or '-'}]")
        spk = vi_name(ctx, e.get("speaker"))
        print((f"{spk}: " if spk else "") + one_line(ctx.eff(i)))


def stretch_stats(ctx, ids):
    """So tu trung binh moi cau thoai va so canh bao /100 cau theo nhom."""
    words, cats = 0, collections.Counter()
    for i in ids:
        vi = ctx.eff(i) or ""
        words += len(re.findall(r"[^\W\d_]+", strip_codes(ctx, vi)))
        _, ws = validate(ctx, i, vi, force=True)
        _, pw = pair_lint(ctx, i, vi)
        for c in {c for c, _m in ws + pw + style_warns(ctx, i, vi)}:
            cats[c] += 1
    n = len(ids) or 1
    return words / n, {c: 100.0 * cats[c] / n for c in DOC_CATS}


def bible_snapshot():
    snap = p(SNAP_DIR)
    os.makedirs(snap, exist_ok=True)
    for f in (F_PAIR, F_VOICE, F_GLOSS, F_SCENE, F_SOTAY):
        if os.path.exists(p(f)):
            shutil.copyfile(p(f), os.path.join(snap, f))


def cmd_doc_chuong(a):
    """Vong doc chuong cua phien chinh (Opus): bai doc tieng Viet, so do, phieu mo; 'xong' de ghi lai."""
    ctx = Ctx(quiet=True)
    st = ctx.state
    ch = st.setdefault("chuong", {})
    done_ids = dlg_done_ids(ctx)
    upto = min(int(ch.get("upto", 0)), len(done_ids))
    if getattr(a, "dccmd", None) == "xong":
        ch["runs"] = int(ch.get("runs", 0)) + 1
        ch["upto"] = len(done_ids)
        ch["time"] = now()
        if a.ghi_chu:
            ch.setdefault("ghi_chu", []).append(f"{now()} {clean_cell(a.ghi_chu)}")
        bible_snapshot()
        save_state(st)
        append_text(p(F_LOG), f"- {now()} đọc chương lần {ch['runs']}: tới câu thoại thứ {ch['upto']}"
                    + (f" · {clean_cell(a.ghi_chu)}" if a.ghi_chu else "") + "\n")
        update_handoff(ctx)
        print(f"Đã ghi đọc chương lần {ch['runs']} (tới câu thoại thứ {fmt_n(ch['upto'])}); "
              f"ảnh chụp bible ở {SNAP_DIR}/ để lần sau vgk.py anh-huong so.")
        return
    if not os.path.isdir(p(SNAP_DIR)):
        bible_snapshot()   # anh chup truoc khi sua: anh-huong so voi ban nay
    new, old = done_ids[upto:], done_ids[:upto]
    k = int(ch.get("runs", 0)) + 1
    ph = phieu_open()
    print(f"ĐỌC CHƯƠNG lần {k}: {fmt_n(len(new))} câu thoại mới (câu {fmt_n(upto + 1)}–{fmt_n(len(done_ids))})"
          f" · phiếu mở {len(ph)} · câu cần sửa {len(st.get('sua') or {})}")
    print("Cách đọc: đọc BÀI ĐỌC như người đọc truyện, chỉ bản Việt; chỗ nào vấp mới mở gốc "
          "(vgk.py show --around <id> --vi --en).")
    print("Sau khi đọc: (1) sotay.md: thay câu mẫu kém bằng câu hay nhất của bài đọc (ghi id), thêm điều tránh, tối đa 60 dòng;"
          " (2) bible riêng: vgk.py voice / pair set (đổi theo truyện thì --tu-canh <mốc>), term change; chỉ đạo cảnh chương sau;"
          " (3) phiếu: trả lời rồi vgk.py phieu dong <n> --tra-loi '…'; (4) câu cũ bị ảnh hưởng: vgk.py anh-huong --sua;"
          " (5) xong: vgk.py doc-chuong xong --ghi-chu '…'.")
    if new:
        w1, c1 = stretch_stats(ctx, new)
        w0, c0 = stretch_stats(ctx, old[-3000:]) if old else (None, None)
        print("SỐ ĐO (chương này" + (" | trước đó" if old else "") + "):")
        print(f"  từ/câu thoại: {w1:.1f}" + (f" | {w0:.1f}" if old else ""))
        for c in DOC_CATS:
            if c1[c] or (c0 and c0[c]):
                up = c0 is not None and c1[c] > c0[c] * 1.5 + 0.5
                print(f"  {c} /100 câu: {c1[c]:.1f}" + (f" | {c0[c]:.1f}" if c0 is not None else "") + ("  ← tăng" if up else ""))
    if ph:
        print("PHIẾU MỞ:")
        for r in ph[:40]:
            print(f"  #{r['n']}" + (f" · {r['id']}" if r["id"] else "") + f": {r['noi_dung']}")
    if not new:
        print("(chưa có câu thoại mới từ lần đọc trước)")
        return
    if len(new) <= a.n:
        pick = list(new)
    else:
        rnd = random.Random(a.seed if a.seed is not None else len(done_ids))
        chosen = [i for i in new if (ctx.scenes.get(ctx.src[i].get("scene") or "") or {}).get("priority")][:a.n // 2]
        have = set(chosen)
        tries = 0
        while len(have) < a.n and tries < 200:
            s0 = rnd.randrange(max(1, len(new) - 15))
            have.update(new[s0:s0 + 15])
            tries += 1
        pick = sorted(have, key=ctx.pos)[:a.n]
    print(f"BÀI ĐỌC ({len(pick)}/{len(new)} câu):")
    last = None
    for i in pick:
        e = ctx.src[i]
        if e.get("scene") != last:
            last = e.get("scene")
            sc = ctx.scenes.get(last or "")
            print(f"[{last or '-'}] " + (one_line(sc["summary"])[:220] if sc and sc["summary"] else ""))
        spk = vi_name(ctx, e.get("speaker"))
        print((f"{spk}: " if spk else "") + one_line(ctx.eff(i)) + f"  ·{i}")
    fl = st.get("flags") or {}
    flagged = [i for i in new if i in fl][:30]
    if flagged:
        print(f"CÂU CÓ CỜ ({len(flagged)}, đối chiếu gốc):")
        for i in flagged:
            e = ctx.src[i]
            print(f"  {i} · {fl[i]} · GỐC: {one_line(e['src'])[:120]}" + (f" · EN: {one_line(e['en'])[:120]}" if e.get("en") else "")
                  + f" · VI: {one_line(ctx.eff(i))[:160]}")


def cmd_anhhuong(a):
    """Cau da dich ma bible (xung ho, ho so, thuat ngu, bi mat) doi tu anh chup lan doc chuong truoc."""
    ctx = Ctx(quiet=True)
    snap = a.tu or p(SNAP_DIR)
    if not os.path.isdir(snap):
        die(f"chưa có ảnh chụp bible ({SNAP_DIR}/): chạy vgk.py doc-chuong (tự chụp lần đầu) hoặc doc-chuong xong")
    old_p = read_tsv(os.path.join(snap, F_PAIR), PAIR_COLS)
    old_v = read_tsv(os.path.join(snap, F_VOICE), VOICE_COLS)
    old_g = read_tsv(os.path.join(snap, F_GLOSS), GLOSS_COLS)
    new_p, new_v = ctx.pairs, ctx.voices
    hit = collections.OrderedDict()
    fields = ("gioi", "vai_ve", "tam_ly", "giong")

    def pk(rows):
        return sorted((r["listener"], r["xung"], r["goi"]) for r in rows)

    def by_spk(rows, cols):
        d = collections.defaultdict(set)
        for r in rows:
            d[r["speaker"]].add(tuple(r.get(c, "") for c in cols))
        return d
    op, np_ = by_spk(old_p, PAIR_COLS), by_spk(new_p, PAIR_COLS)
    ov_, nv_ = by_spk(old_v, VOICE_COLS), by_spk(new_v, VOICE_COLS)
    # Chi xet nguoi noi co dong xung ho/ho so doi (dong '*' doi thi xet moi nguoi noi)
    touched = {k for k in set(op) | set(np_) if op.get(k) != np_.get(k)} | {k for k in set(ov_) | set(nv_) if ov_.get(k) != nv_.get(k)}
    every = "*" in touched
    try:
        for eid in ctx.src_order:
            e = ctx.src[eid]
            if e["kind"] != "dialogue" or not e.get("speaker") or ctx.eff(eid) is None or is_gop(ctx, eid):
                continue
            if not every and e["speaker"] not in touched:
                continue
            spk, lis = e["speaker"], ctx.listener(eid)
            ctx.pairs = old_p
            o = pk(ctx.pair_rows(spk, lis, eid))
            ctx.pairs = new_p
            if o != pk(ctx.pair_rows(spk, lis, eid)):
                hit[eid] = "xưng hô đổi"
                continue
            ctx.voices = old_v
            ov = ctx.voice_for(spk, eid) or {}
            ctx.voices = new_v
            nv = ctx.voice_for(spk, eid) or {}
            if any((ov.get(f) or "") != (nv.get(f) or "") for f in fields):
                hit[eid] = "hồ sơ đổi"
    finally:
        ctx.pairs, ctx.voices = new_p, new_v
    oldmap = {r["src"]: r["vi"] for r in old_g if r["src"]}
    changed = [(r, oldmap[r["src"]]) for r in ctx.gloss if r["src"] in oldmap and r["vi"] and oldmap[r["src"]]
               and oldmap[r["src"]] != r["vi"]]
    for eid, vi in ctx.tr.items():
        if eid not in ctx.src or eid in hit:
            continue
        s = ctx.src[eid]["src"]
        for r, ov in changed:
            if re.search(term_pattern(r["src"]), s, re.I) and word_in(ov, vi, ci=True) and not word_in(r["vi"], vi, ci=True):
                hit[eid] = f"thuật ngữ đổi: {ov} → {r['vi']}"
                break
        else:
            if any(c == "lộ tình tiết" for c, _m in validate(ctx, eid, vi)[0]):
                hit[eid] = "lộ tình tiết"
    cnt = collections.Counter(v.partition(":")[0] for v in hit.values())
    rep = os.path.join("reports", f"anh-huong-{stamp()}.txt")
    os.makedirs(p("reports"), exist_ok=True)
    atomic_write(p(rep), "".join(f"{i}\t{why}\t{ctx.src[i].get('speaker') or '-'}\t{one_line(ctx.eff(i) or '')[:160]}\n"
                                 for i, why in hit.items()))
    print(f"Câu đã dịch bị ảnh hưởng: {len(hit)}" + (" · " + ", ".join(f"{k} {v}" for k, v in cnt.items()) if hit else "")
          + f" → {rep}")
    if not hit:
        return
    if a.sua:
        if len(hit) > a.toi_da and not a.force:
            print(f"Quá {a.toi_da} câu: thay đổi lớn (thường là hồ sơ của nhân vật chính) → chuốt lại theo lô "
                  "(vgk.py polish next --batch N) thay vì sửa từng câu, hoặc thêm --force.")
            return
        sua = ctx.state.setdefault("sua", {})
        for i, why in hit.items():
            sua[i] = why
        save_state(ctx.state)
        update_handoff(ctx)
        print(f"Đã thêm {len(hit)} câu vào danh sách cần sửa (tổng {len(sua)}) → giao người dịch: vgk.py sua next")
    else:
        print("Thêm vào danh sách cần sửa: vgk.py anh-huong --sua")


def cmd_sua(a):
    """Danh sach cau can sua theo bible moi: them | next | bo | status. Ghi lai cau bang write la tu roi khoi danh sach."""
    ctx = Ctx(quiet=True)
    st = ctx.state
    sua = st.setdefault("sua", {})
    if a.scmd == "them":
        add = collections.OrderedDict()
        if a.tep:
            with open(a.tep, encoding="utf-8-sig") as f:
                for ln in f:
                    parts = ln.rstrip("\n").split("\t")
                    if parts and parts[0].strip():
                        add[parts[0].strip()] = parts[1].strip() if len(parts) > 1 and parts[1].strip() else ""
        for i in a.ids or []:
            add[i] = ""
        bad = [i for i in add if i not in ctx.src]
        if bad:
            die("id không có trong src: " + ", ".join(bad[:10]))
        for i, why in add.items():
            sua[i] = a.ly_do or why or "sửa theo bible mới"
        save_state(st)
        update_handoff(ctx)
        print(f"Cần sửa: +{len(add)} · tổng {len(sua)}")
        return
    if a.scmd == "bo":
        ids = list(sua) if a.ids == ["all"] else a.ids
        k = sum(1 for i in ids if sua.pop(i, None) is not None)
        save_state(st)
        update_handoff(ctx)
        print(f"Bỏ khỏi danh sách: {k} · còn {len(sua)}")
        return
    if a.scmd == "status":
        cnt = collections.Counter(v.partition(":")[0] for v in sua.values())
        print(f"Cần sửa: {len(sua)}" + (" · " + ", ".join(f"{k} {v}" for k, v in cnt.most_common()) if sua else ""))
        return
    ids = sorted((i for i in sua if i in ctx.src), key=ctx.pos)[:a.n]
    if not ids:
        print("Không còn câu nào cần sửa.")
        return
    _, changed = build_neo(ctx, {ctx.src[i].get("speaker") for i in ids if ctx.src[i].get("speaker")})
    save_state(st)
    if changed:
        print("LUẬT ĐÃ ĐỔI: đọc lại " + ", ".join(os.path.basename(f) for f in changed))
    print(f"SỬA LẠI {len(ids)}/{len(sua)} câu theo bible hiện tại. Dòng '#> VI:' là bản đang có; ghi bản sửa bằng '@@ <id>'. "
          "Câu đọc lại thấy vẫn đúng thì ghi lại y nguyên (để đánh dấu đã xem).")
    groups = collections.OrderedDict()
    for i in ids:
        groups.setdefault(ctx.src[i].get("scene") or "", []).append(i)
    show_en = ctx.cfg["en_mode"] != "none"
    for sc, grp in groups.items():
        r = ctx.scenes.get(sc)
        if sc:
            print(f"CẢNH {sc}: " + (r["summary"] if r and r["summary"] else "(chưa có chỉ đạo)"))
        first = grp[0]
        spk = uniq(ctx.src[i].get("speaker") for i in grp if ctx.src[i].get("speaker"))
        vl = [v for v in (ctx.voice_for(s, first) for s in spk) if v]
        if vl:
            print("HỒ SƠ NHÂN VẬT:")
            for v in vl:
                print("  " + voice_line(v))
        prs = []
        for s in spk:
            for i in grp:
                if ctx.src[i].get("speaker") == s:
                    prs += [x for x in ctx.pair_rows(s, ctx.listener(i), i) if x not in prs]
        if prs:
            print("XƯNG HÔ:")
            for x in prs[:16]:
                print("  " + pair_line(x))
        for i in grp:
            e = ctx.src[i]
            lis = ctx.listener(i)
            meta = [x for x in (e.get("speaker") or "", f"→ {lis}" if lis else "", f"lý do: {sua[i]}") if x]
            print(f"@@ {i}" + (" >" + lis if lis else ""))
            print("#> " + " · ".join(meta))
            for line in e["src"].split("\n"):
                print("#> " + line)
            if show_en and e.get("en"):
                print("#> EN: " + one_line(e["en"]))
            print("#> VI: " + one_line(ctx.eff(i) or ""))
    print("#> ---")
    print("#> Ghi: vgk.py write - <<'VGK' … VGK — mỗi mục dòng '@@ <id>' (giữ ' >người nghe' nếu có) rồi bản dịch; "
          "không chép dòng '#>'.")


# ---------------------------------------------------------------- dong bo WORK cloud <-> may (phien khong shell)

SYNC_CHUNG_DIRS = ("khauvi", "adapters", "hoso")
SYNC_CHUNG_FILES = ("KINH_NGHIEM.md", "TODO.md", "config.json")
BRIDGE_MAX = 400 << 20


def sync_files():
    """[(khoa tinh tu ROOT, duong dan)] moi tep can giu tren may: ca WORK (gom backup/, patch/) va phan chung trong _chung."""
    out = []
    wname = os.path.basename(os.path.abspath(WORK))
    for dp, dn, fn in os.walk(WORK):
        dn[:] = [d for d in dn if d != "__pycache__"]
        rel = os.path.relpath(dp, WORK)
        if rel == "reports" or rel.startswith("reports" + os.sep):
            continue   # bao cao, log: de o cloud, khong chep ve may
        for f in fn:
            if f.endswith((".tmp", ".pyc")) or f == ".vgk.lock" or (rel == "." and f == "export.json"):
                continue
            r = f if rel == "." else os.path.join(rel, f)
            out.append((wname + "/" + r.replace(os.sep, "/"), os.path.join(WORK, r)))
    ch = vgk_dir()
    if os.path.basename(ch) == "_chung" or os.path.isfile(os.path.join(ch, "config.json")):
        for f in SYNC_CHUNG_FILES:
            if os.path.isfile(os.path.join(ch, f)):
                out.append(("_chung/" + f, os.path.join(ch, f)))
        for d in SYNC_CHUNG_DIRS:
            for dp, dn, fn in os.walk(os.path.join(ch, d)):
                dn[:] = [x for x in dn if x != "__pycache__"]
                for f in fn:
                    if not f.endswith((".tmp", ".pyc")):
                        fp = os.path.join(dp, f)
                        out.append(("_chung/" + os.path.relpath(fp, ch).replace(os.sep, "/"), fp))
    return sorted(out)


def cmd_dongbo(a):
    st = load_state()
    ds = st.setdefault("dongbo", {})
    old = ds.get("files") or {}
    skey = os.path.basename(os.path.abspath(WORK)) + "/" + F_STATE
    files = [(k, f) for k, f in sync_files() if k != skey]
    if a.mark:
        ds["last"] = now()
        save_state(st)
        if os.path.exists(p(F_HANDOFF)) and os.path.exists(p(F_SRC)) and os.path.exists(p(F_GAME)):
            update_handoff(Ctx(quiet=True))
        st = load_state()
        st.setdefault("dongbo", {}).update(last=ds["last"], files={k: file_sha(f) for k, f in sync_files() if k != skey})
        save_state(st)
        print(f"Đã ghi nhận lần đồng bộ ({len(st['dongbo']['files'])} tệp) lúc {ds['last']}")
        return
    changed = [(k, f) for k, f in files if old.get(k) != file_sha(f)]
    if not changed:
        print("Không có tệp nào đổi từ lần đồng bộ trước.")
        return
    changed.append((skey, p(F_STATE)))
    size = sum(os.path.getsize(f) for _, f in changed)
    big = [k for k, f in changed if os.path.getsize(f) > BRIDGE_MAX]
    print(f"Cần ghi về máy {len(changed)} tệp, {size / (1 << 20):.1f} MB (đổi từ lần đồng bộ trước"
          f"{' ' + ds['last'] if ds.get('last') else ''}); đường dẫn tính từ ROOT:")
    for k, _ in changed:
        print("  " + k)
    if big:
        print("QUÁ 400 MB, cầu nối không chép được: " + ", ".join(big[:5]) + " — báo người dùng chép tay hoặc chia nhỏ.")
    print("Ghi xong (so vgk.py hash) thì chạy: vgk.py dongbo --mark")


# ---------------------------------------------------------------- di tru bo cuc cu

MAU_COLS = ["thua", "thang", "ly_do", "pham_vi", "nguon"]


def parse_nums(spec):
    """'9-22,25' -> [9..22, 25]"""
    out = []
    for part in split_list(str(spec), ","):
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if m:
            out += list(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.append(int(part))
        else:
            die(f"không hiểu '{part}' (dạng 9-22,25)")
    return uniq(out)


def merge_rows(src, dst, cols, keyf, defaults=None, do=False):
    """Them vao dst cac dong cua src chua co (theo khoa). Tra ve so dong them."""
    if not os.path.exists(src):
        return 0
    cur = read_tsv(dst, cols)
    have = {keyf(r) for r in cur}
    add = []
    for r in read_tsv(src, cols):
        r = {c: r.get(c, "") for c in cols}
        for k, v in (defaults or {}).items():
            r[k] = r[k] or v
        key = keyf(r)
        if key and key not in have:
            add.append(r)
            have.add(key)
    if do and add:
        write_tsv(dst, cols, [{c: r.get(c, "") for c in cols} for r in cur] + add)
    return len(add)


def merge_md(src, dst, title, do=False):
    """Noi tep .md cu vao cuoi tep dang co, mot lan (danh dau bang sha). Tra ve True neu can/da noi."""
    if not os.path.exists(src):
        return False
    with open(src, encoding="utf-8-sig") as f:
        body = f.read().strip()
    mark = f"<!-- tu-ban-cu:{hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]} -->"
    cur = ""
    if os.path.exists(dst):
        with open(dst, encoding="utf-8-sig") as f:
            cur = f.read()
    if not body or mark in cur or cur.strip() == body:
        return False
    if do:
        append_text(dst, f"\n\n## {title} ({now()})\n{mark}\n{body}\n")
    return True


def merge_khauvi(lkv, kv, pv, do=False):
    """Gop khau vi ban cu vao khauvi dang co. do=False: tra ve so muc se them; do=True: lam va tra ve tep da doi."""
    st = collections.OrderedDict()
    changed = []
    st["KHAU_VI.md"] = int(merge_md(os.path.join(lkv, "KHAU_VI.md"), os.path.join(kv, "KHAU_VI.md"),
                                    "Khẩu vị từ bản cũ", do=do))
    for f, cols, keyf, dft in (
            ("mau.tsv", MAU_COLS, lambda r: (r["thua"], r["thang"]) if r["thua"] or r["thang"] else None, {"pham_vi": pv}),
            ("cam_mau.tsv", CAM_COLS, lambda r: r["regex"] or None, {"pham_vi": pv}),
            ("hieu_chuan.tsv", HC_COLS, lambda r: r["pair_id"] or None, None)):
        st[f] = merge_rows(os.path.join(lkv, f), os.path.join(kv, f), cols, keyf, dft, do=do)
    other = [f for f in sorted(os.listdir(lkv)) if os.path.isfile(os.path.join(lkv, f))
             and f not in st and not os.path.exists(os.path.join(kv, f))]
    st["tệp khác"] = len(other)
    if do:
        for f in other:
            shutil.copyfile(os.path.join(lkv, f), os.path.join(kv, f))
        changed = [os.path.join(kv, f) for f in list(st)[:4] if st[f]] + [os.path.join(kv, f) for f in other]
        return changed
    return st


def cmd_migrate(a):
    """Di tru tu bo cuc 1.x: khau vi ve ROOT/_chung, them pham_vi, TODO, config, viec ton dong, gom adapter."""
    root = os.path.abspath(a.root)
    chung = os.path.join(root, "_chung")
    seed = os.path.normpath(os.path.join(vgk_dir(), "..", "references", "khauvi-seed"))
    ops = []
    kv = os.path.join(chung, "khauvi")
    leg = os.path.abspath(a.legacy_chung) if a.legacy_chung else None
    works = [os.path.abspath(w) for w in (a.work or [])]
    slug0 = ""
    for w in works:
        try:
            with open(os.path.join(w, F_GAME), encoding="utf-8-sig") as fh:
                slug0 = slug0 or json.load(fh).get("slug", "")
        except Exception:
            pass
    pv = a.pham_vi or (f"game:{slug0}" if slug0 else "chung")
    lkv = os.path.join(leg, "khauvi") if leg else None
    if lkv and os.path.isdir(lkv) and not os.path.isdir(kv):
        ops.append(("copytree", lkv, kv, "khẩu vị cũ lên ROOT/_chung"))
    elif lkv and os.path.isdir(lkv):
        # ROOT da co khauvi (vd hat giong da chep o Buoc 0): gop phan cu vao, khong bo.
        st = merge_khauvi(lkv, kv, pv, do=False)
        if any(st.values()):
            ops.append(("merge_khauvi", lkv, kv, "gộp khẩu vị cũ vào khauvi đang có: "
                        + ", ".join(f"{k} +{v}" for k, v in st.items() if v)))
    elif not os.path.isdir(kv) and os.path.isdir(seed):
        ops.append(("copytree", seed, kv, "khẩu vị hạt giống từ gói skill"))
    for f in ("KINH_NGHIEM.md", "chuot.py"):
        lf, cf = (os.path.join(leg, f) if leg else ""), os.path.join(chung, f)
        if not leg or not os.path.exists(lf):
            continue
        if not os.path.exists(cf):
            ops.append(("copy", lf, cf, f"{f} cũ"))
        elif f.endswith(".md") and merge_md(lf, cf, "Từ bản cũ", do=False):
            ops.append(("merge_md", lf, cf, f"nối {f} cũ vào cuối {f} đang có"))
    ops.append(("pham_vi", os.path.join(kv, "mau.tsv"), pv, f"thêm cột pham_vi (mặc định {pv}) vào mau.tsv"))
    if not os.path.exists(os.path.join(chung, "TODO.md")):
        ops.append(("write", os.path.join(chung, "TODO.md"), "# Việc chung tồn đọng (mọi game)\n\n-\n", "tạo TODO.md"))
    cfgp = os.path.join(chung, "config.json")
    if not os.path.exists(cfgp):
        cur_cfg = {"root_win": a.root_win or "", "bang_tien_do": a.bang_tien_do or "", "chuan_tham_chieu": {},
                   "ngan_sach_token": None}
        ops.append(("write", cfgp, json.dumps(cur_cfg, ensure_ascii=False, indent=2) + "\n", "tạo config.json"))
    else:
        try:
            with open(cfgp, encoding="utf-8-sig") as fh:
                cur_cfg = json.load(fh)
        except Exception:
            cur_cfg = {}
        upd = {k: v for k, v in (("root_win", a.root_win), ("bang_tien_do", a.bang_tien_do)) if v and cur_cfg.get(k) != v}
        if upd:
            ops.append(("gamejson", cfgp, upd, "config.json cập nhật " + ", ".join(upd)))
            cur_cfg.update(upd)
    warn = []
    if not cur_cfg.get("root_win"):
        warn.append("config.json: root_win trống → chạy lại với --root-win \"<đường dẫn ROOT trên Windows>\"")
    if not cur_cfg.get("bang_tien_do"):
        warn.append("config.json: bang_tien_do trống → tìm link bảng tiến độ trong danh sách artifact của người dùng "
                    "(bản 1.x ghi link trong SKILL.md), rồi chạy lại với --bang-tien-do \"<link>\"; không thấy thì hỏi 1 câu")
    if a.polish_done and works:
        nums = parse_nums(a.polish_done)
        ops.append(("polish_done", works[0], nums, f"đánh dấu đã chuốt {len(nums)} lô ({a.polish_done}) trong state.json"))
    if a.ton_dong and works:
        with open(a.ton_dong, encoding="utf-8-sig") as fh:
            td = fh.read().strip()
        hf = os.path.join(works[0], F_HANDOFF)
        mark = "<!-- ton-dong-tu-skill -->"
        cur = open(hf, encoding="utf-8-sig").read() if os.path.exists(hf) else ""
        if mark not in cur:
            ops.append(("append", hf, f"\n\n## Việc tồn đọng (chuyển từ skill, {now()})\n{mark}\n{td}\n", "việc tồn đọng vào HANDOFF"))
    for w in works:
        try:
            with open(os.path.join(w, F_GAME), encoding="utf-8-sig") as fh:
                g = json.load(fh)
        except Exception:
            g = {}
        tools = os.path.join(w, "tools")
        if os.path.isdir(tools):
            fs = [f for f in os.listdir(tools) if f.endswith((".py", ".ps1", ".bat", ".js", ".cs", ".md")) and not f.startswith(".")]
            if fs:
                dst = os.path.join(chung, "adapters", slugify(g.get("engine") or "khac"), g.get("slug") or os.path.basename(w))
                if not os.path.isdir(dst):
                    ops.append(("adapters", tools, dst, f"gom {len(fs)} tệp adapter của {g.get('slug') or w}"))
        if a.the_loai or a.boi_canh or a.en_mode:
            upd = {k: v for k, v in (("the_loai", a.the_loai), ("boi_canh", a.boi_canh), ("en_mode", a.en_mode)) if v
                   and not g.get(k)}
            if upd:
                ops.append(("gamejson", os.path.join(w, F_GAME), upd, f"game.json thêm {upd}"))
    print(f"DI TRÚ → {chung}")
    for op in ops:
        print(f"  - {op[-1]}")
    for w in warn:
        print("  ! " + w)
    if not a.apply:
        print("Chưa ghi gì (xem trước). Thêm --apply để làm; tệp có sẵn được sao lưu trước khi đổi, không xóa gì.")
        return
    bdir = os.path.join(chung, "backup", f"migrate-{stamp()}")
    changed = []

    def backup(path):
        if os.path.exists(path):
            rel = os.path.relpath(path, root).replace("..", "_up")
            dst = os.path.join(bdir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(path, dst)
    for kind, x, y, _ in ops:
        if kind == "copytree":
            shutil.copytree(x, y, copy_function=shutil.copyfile)
            changed += [os.path.join(dp, f) for dp, _, fn in os.walk(y) for f in fn]
        elif kind == "copy":
            os.makedirs(os.path.dirname(y), exist_ok=True)
            shutil.copyfile(x, y)
            changed.append(y)
        elif kind == "write":
            os.makedirs(os.path.dirname(x), exist_ok=True)
            atomic_write(x, y)
            changed.append(x)
        elif kind == "append":
            backup(x)
            append_text(x, y)
            changed.append(x)
        elif kind == "pham_vi":
            if os.path.exists(x):
                with open(x, encoding="utf-8-sig") as fh:
                    lines = fh.read().split("\n")
                if lines and lines[0].strip() and "pham_vi" not in lines[0].split("\t"):
                    backup(x)
                    out = [lines[0].rstrip("\r") + "\tpham_vi"] + [ln.rstrip("\r") + ("\t" + y if ln.strip() and not ln.startswith("#") else "")
                                                                   for ln in lines[1:]]
                    atomic_write(x, "\n".join(out).rstrip("\n") + "\n")
                    changed.append(x)
        elif kind == "adapters":
            shutil.copytree(x, y, copy_function=shutil.copyfile, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.json"))
            readme = os.path.join(y, "README.md")
            if not os.path.exists(readme):
                atomic_write(readme, f"# Adapter gom từ {x}\n\n- Ngày gom: {now()}\n- Đã thử với: (ghi tên game + phiên bản)\n"
                                     "- Định dạng đọc/ghi: (ghi ngắn)\n")
            changed += [os.path.join(dp, f) for dp, _, fn in os.walk(y) for f in fn]
        elif kind == "gamejson":
            backup(x)
            with open(x, encoding="utf-8-sig") as fh:
                g = json.load(fh)
            g.update(y)
            atomic_write(x, json.dumps(g, ensure_ascii=False, indent=2) + "\n")
            changed.append(x)
        elif kind == "merge_khauvi":
            for f in os.listdir(y):
                if os.path.isfile(os.path.join(y, f)):
                    backup(os.path.join(y, f))
            changed += merge_khauvi(x, y, pv, do=True)
        elif kind == "merge_md":
            backup(y)
            merge_md(x, y, "Từ bản cũ", do=True)
            changed.append(y)
        elif kind == "polish_done":
            sp_ = os.path.join(x, F_STATE)
            backup(sp_)
            try:
                with open(sp_, encoding="utf-8") as fh:
                    st = json.load(fh)
            except Exception:
                st = {}
            done = st.setdefault("polish", {}).setdefault("done", [])
            done += [n for n in y if n not in done]
            atomic_write(sp_, json.dumps(st, ensure_ascii=False, indent=1) + "\n")
            changed.append(sp_)
    os.makedirs(bdir, exist_ok=True)
    rep = os.path.join(bdir, "migrate.txt")
    atomic_write(rep, "\n".join(os.path.relpath(c, root).replace(os.sep, "/") for c in changed) + "\n")
    print(f"Đã di trú: {len(changed)} tệp tạo/đổi (danh sách để ghi về máy: {rep}); sao lưu ở {bdir}")


def cmd_version(a):
    print(VERSION)


def build_parser():
    ap = argparse.ArgumentParser(prog="vgk.py", description="Bộ công cụ lõi Việt hóa game (VGK " + VERSION + ")")
    ap.add_argument("-w", "--work", default=os.environ.get("VGK_WORK", "."), help="thư mục làm việc của game (mặc định: thư mục hiện tại)")
    sp = ap.add_subparsers(dest="cmd", required=True)

    x = sp.add_parser("init", help="tạo cấu trúc WORK và các tệp mẫu (không ghi đè)")
    x.add_argument("--name"); x.add_argument("--slug"); x.add_argument("--engine")
    x.add_argument("--kind", help="thuong | 18"); x.add_argument("--lang", help="ngôn ngữ gốc: ja | zh | ko | en …")
    x.add_argument("--the-loai", dest="the_loai", help="vn | rpg | hanh_dong | khac (chọn hồ sơ thể loại)")
    x.add_argument("--boi-canh", dest="boi_canh", help="co_trang | fantasy | hien_dai | khac")
    x.add_argument("--en-mode", dest="en_mode", help="all | on_demand | none (mặc định: none nếu nguồn en, không thì on_demand)")
    x.add_argument("--no-lessons", dest="no_lessons", action="store_true", help="không tạo KINH_NGHIEM.md cạnh vgk.py")
    x.set_defaults(fn=cmd_init)

    x = sp.add_parser("plan", help="phân loại (tự động, trùng) và chia lô từ src.jsonl (lệnh khác tự chạy lại khi src đổi)")
    x.set_defaults(fn=cmd_plan)

    x = sp.add_parser("status", help="tiến độ gọn")
    x.add_argument("--handoff", action="store_true", help="cập nhật khối trạng thái trong HANDOFF.md")
    x.set_defaults(fn=cmd_status)

    x = sp.add_parser("fix-dau", help="đổi dấu kiểu Nhật (⸺, ―, '……') trong bản dịch đã có (WORK cũ); xem trước, --apply để ghi")
    x.add_argument("--apply", action="store_true")
    x.set_defaults(fn=cmd_fixdau)

    x = sp.add_parser("lo", help="danh sách lô (loại, số câu, còn lại, ưu tiên, cảnh) để chia dải cho agent dịch")
    x.add_argument("--tu", type=int, help="từ lô N")
    x.add_argument("--den", type=int, help="đến lô M")
    x.add_argument("--con", action="store_true", help="chỉ lô còn câu chưa dịch")
    x.set_defaults(fn=cmd_lo)

    x = sp.add_parser("next", help="in lô kế tiếp kèm ngữ cảnh; mỗi câu có mã tắt ~lô.số để ghi")
    x.add_argument("--batch", type=int, help="in lô số N")
    x.add_argument("--en", help="in bản EN: 'all' hoặc danh sách mã tắt/id cách nhau dấu phẩy")
    x.add_argument("--all", action="store_true", help="in cả câu đã dịch trong lô")
    x.add_argument("--limit", type=int, help="chỉ in N câu đầu")
    x.add_argument("--phien", help="mã phiên của agent (từ khoi-dong): không in lại NEO, hồ sơ, xưng hô, thuật ngữ đã in ở lô trước")
    x.set_defaults(fn=cmd_next)

    x = sp.add_parser("write", help="ghi bản dịch (tệp hoặc '-' = stdin), tự kiểm từng mục")
    x.add_argument("file")
    x.add_argument("--force", help="mã tắt/id bỏ qua kiểm chữ gốc sót và thuật ngữ cấm (cách nhau dấu phẩy), chỉ khi cố ý")
    x.add_argument("--dry", action="store_true", help="chỉ kiểm, không ghi")
    x.add_argument("--phien", help="mã phiên của agent (từ khoi-dong)")
    x.add_argument("--tiep", action="store_true", help="ghi sạch thì in luôn lô kế trong dải; có lỗi thì không in, sửa rồi ghi lại")
    x.set_defaults(fn=cmd_write)

    x = sp.add_parser("check", help="kiểm toàn bộ: chưa dịch, gốc đổi, mã/thẻ, chữ gốc, thuật ngữ, xưng hô, độ dài")
    x.set_defaults(fn=cmd_check)

    x = sp.add_parser("review", help="mẫu ngẫu nhiên câu đã dịch (kèm gốc) để rà nghĩa")
    x.add_argument("--n", type=int, default=120); x.add_argument("--seed", type=int, help="mặc định: ngẫu nhiên mỗi lần (in ra)")
    x.add_argument("--uu-tien", dest="uu_tien", action="store_true", help="thêm câu trong cảnh ưu tiên")
    x.add_argument("--cap", type=int, default=150, help="tối đa câu cảnh ưu tiên")
    x.add_argument("--all-kinds", dest="all_kinds", action="store_true", help="lấy cả UI/dữ liệu")
    x.set_defaults(fn=cmd_review)

    x = sp.add_parser("show", help="xem câu gốc gọn (tìm, lọc, quanh một id)")
    x.add_argument("--around"); x.add_argument("--start", help="bắt đầu từ id")
    x.add_argument("--file"); x.add_argument("--speaker"); x.add_argument("--scene"); x.add_argument("--grep")
    x.add_argument("--n", type=int, default=40); x.add_argument("--en", action="store_true"); x.add_argument("--vi", action="store_true")
    x.set_defaults(fn=cmd_show)

    x = sp.add_parser("speakers", help="người nói theo số câu (tên gốc dùng cho @@pair/@@voice)")
    x.add_argument("--n", type=int, default=50)
    x.set_defaults(fn=cmd_speakers)

    x = sp.add_parser("fill", help="điền mục ngắn trùng nguyên văn thuật ngữ trong glossary")
    x.add_argument("--apply", action="store_true"); x.add_argument("--all-kinds", dest="all_kinds", action="store_true")
    x.set_defaults(fn=cmd_fill)

    x = sp.add_parser("bulk", help="dịch hàng loạt theo mẫu regex: ${1} = nhóm 1, ${1|g} = nhóm 1 tra glossary")
    x.add_argument("--match", required=True); x.add_argument("--to", required=True)
    x.add_argument("--kind"); x.add_argument("--file"); x.add_argument("--redo", action="store_true")
    x.add_argument("--apply", action="store_true")
    x.set_defaults(fn=cmd_bulk)

    x = sp.add_parser("term", help="thuật ngữ: add | find | change | import | stats")
    ts = x.add_subparsers(dest="tcmd", required=True)
    y = ts.add_parser("add", help="thêm thuật ngữ mới; không đổi nghĩa mục đã có (đổi nghĩa: term change)"); y.add_argument("src"); y.add_argument("vi"); y.add_argument("--type")
    y.add_argument("--note"); y.add_argument("--forbid", help="biến thể cấm, cách nhau dấu ;")
    y.add_argument("--lo-tu", dest="lo_tu", help="bí mật: bản dịch chỉ được có từ này từ mốc (mã cảnh hoặc id câu)")
    y = ts.add_parser("find"); y.add_argument("text"); y.add_argument("--n", type=int, default=30)
    y = ts.add_parser("change", help="đổi nghĩa thuật ngữ: chỉ xét câu có gốc chứa thuật ngữ này (khớp dài nhất); câu dùng "
                      "nghĩa cũ thì tự sửa, câu không chắc thì liệt kê để sửa tay; không --apply thì chỉ xem trước")
    y.add_argument("src"); y.add_argument("vi"); y.add_argument("--apply", action="store_true")
    y = ts.add_parser("import", help="nhập tệp TSV cùng cột glossary.tsv (src, vi, type, note, forbid, lo_tu): chỉ thêm "
                      "mục mới, không đổi nghĩa mục đã có"); y.add_argument("file")
    ts.add_parser("stats")
    y = ts.add_parser("candidates", help="ứng viên tên/thuật ngữ: chuỗi lặp từ --min lần trong câu gốc, chưa có trong "
                      "glossary và chưa skip, xếp theo số lần; quyết từng mục bằng term add hoặc term skip tới khi về 0")
    y.add_argument("--top", type=int, default=300); y.add_argument("--min", type=int, default=5)
    y = ts.add_parser("skip", help="ghi ứng viên đã quyết là không cần glossary (glossary_skip.txt): candidates không hiện lại")
    y.add_argument("items", nargs="+"); y.add_argument("--note")
    x.set_defaults(fn=cmd_term)

    x = sp.add_parser("qa", help="cổng kiểm chất lượng: due | status | sample | sheet | score | record | collect | calibrate")
    qs = x.add_subparsers(dest="qcmd", required=True)
    qs.add_parser("due", help="cổng nào đến hạn theo tiến độ")
    qs.add_parser("status", help="tình trạng các cổng")
    y = qs.add_parser("sample", help="lấy mẫu cho một cổng")
    y.add_argument("--gate", required=True, choices=QA_GATES); y.add_argument("--seed", type=int); y.add_argument("--n", type=int)
    y = qs.add_parser("sheet", help="bảng đọc chỉ tiếng Việt cho P5/F3 sau khi đã dịch đủ"); y.add_argument("ids")
    y = qs.add_parser("score", help="chấm kết quả giám khảo (T2/T3/F2)"); y.add_argument("file"); y.add_argument("--ids", required=True)
    y = qs.add_parser("record", help="ghi kết quả người dùng đọc (P5/F3)"); y.add_argument("ids")
    y.add_argument("--can", default=""); y.add_argument("--xungho", default=""); y.add_argument("--note")
    qs.add_parser("collect", help="đưa câu cấn đã sửa vào bộ hiệu chuẩn P4")
    y = qs.add_parser("calibrate", help="P4: tạo bài cho giám khảo (--pairs) hoặc chấm (--pairs --judge)")
    y.add_argument("--pairs", required=True); y.add_argument("--judge")
    x.set_defaults(fn=cmd_qa)

    x = sp.add_parser("coverage", help="cổng P1: mọi chuỗi chữ nguồn trong mọi tệp (cả nhị phân) phải có trong src.jsonl; "
                                       "--sau-va: quét game đã vá, còn chữ gốc là sót")
    x.add_argument("dir"); x.add_argument("--min", type=int, default=None,
                                          help="ngưỡng sót mỗi tệp (mặc định 1 ký tự nguồn; nguồn EN: 3 chuỗi)")
    x.add_argument("--sau-va", dest="sau_va", action="store_true", help="thư mục là game ĐÃ VÁ: báo mọi chữ nguồn còn lại")
    x.add_argument("--all-files", dest="all_files", action="store_true", help="nguồn EN: xét cả tệp văn bản không có đuôi quen")
    x.set_defaults(fn=cmd_coverage)

    x = sp.add_parser("estimate", help="ước tính token phần còn lại, so với ngân sách")
    x.add_argument("--per-batch", dest="per_batch", type=int, default=30000, help="token ngữ cảnh phiên mỗi lô (ước)")
    x.set_defaults(fn=cmd_estimate)

    x = sp.add_parser("polish", help="chuốt lại hàng loạt: next | status | lint N | doc N | done N")
    ps = x.add_subparsers(dest="pcmd", required=True)
    y = ps.add_parser("next"); y.add_argument("--en"); y.add_argument("--batch", type=int, help="bắt đầu từ lô thoại N")
    ps.add_parser("status")
    for nm in ("lint", "doc"):
        y = ps.add_parser(nm); y.add_argument("n", type=int)
    y = ps.add_parser("done"); y.add_argument("n", help="lô N, hoặc dải như 9-22,25")
    x.set_defaults(fn=cmd_polish)

    x = sp.add_parser("dongbo", help="phiên không shell: liệt kê tệp WORK (cả patch/, backup/) và _chung cần ghi về máy; --mark sau khi ghi xong")
    x.add_argument("--mark", action="store_true")
    x.set_defaults(fn=cmd_dongbo)

    x = sp.add_parser("migrate", help="di trú bố cục 1.x lên ROOT/_chung (mặc định chỉ xem trước)")
    x.add_argument("--root", required=True, help="thư mục ROOT (thư mục chứa _chung và các WORK; khi không có shell là bản chép trên cloud)")
    x.add_argument("--legacy-chung", dest="legacy_chung", help="_chung cũ (vd cạnh WORK của game cũ)")
    x.add_argument("--work", action="append", help="WORK của game cũ (lặp được)")
    x.add_argument("--ton-dong", dest="ton_dong", help="tệp việc tồn đọng để chèn vào HANDOFF của --work đầu")
    x.add_argument("--pham-vi", dest="pham_vi", help="pham_vi mặc định cho mau.tsv cũ (mặc định game:<slug>)")
    x.add_argument("--root-win", dest="root_win"); x.add_argument("--bang-tien-do", dest="bang_tien_do")
    x.add_argument("--the-loai", dest="the_loai"); x.add_argument("--boi-canh", dest="boi_canh"); x.add_argument("--en-mode", dest="en_mode")
    x.add_argument("--polish-done", dest="polish_done", help="lô thoại đã chuốt bằng công cụ cũ (vd 9-22), ghi vào state của --work đầu")
    x.add_argument("--apply", action="store_true")
    x.set_defaults(fn=cmd_migrate)

    x = sp.add_parser("pair", help="xưng hô: set | find (tên gốc như trong src). Người nghe của một câu: '>tên' khi write, "
                      "rồi người nghe đã lưu, rồi người còn lại khi cảnh chỉ có 2 người nói; không rõ thì dùng dòng người nghe '*'")
    ps = x.add_subparsers(dest="pcmd", required=True)
    y = ps.add_parser("set"); y.add_argument("speaker"); y.add_argument("listener"); y.add_argument("xung"); y.add_argument("goi")
    y.add_argument("--note"); y.add_argument("--tu-canh", dest="tu_canh", help="mốc: mã cảnh hoặc id câu; dòng chỉ áp từ đó")
    y.add_argument("--force", action="store_true", help="vẫn ghi khi xưng trái giới tính trong hồ sơ (cố ý)")
    y = ps.add_parser("find"); y.add_argument("name")
    x.set_defaults(fn=cmd_pair)

    x = sp.add_parser("scene", help="tóm tắt cảnh: set | missing")
    ss = x.add_subparsers(dest="scmd", required=True)
    y = ss.add_parser("set"); y.add_argument("scene"); y.add_argument("summary")
    y.add_argument("--uu-tien", dest="uu_tien", action="store_true")
    y.add_argument("--bo-uu-tien", dest="bo_uu_tien", action="store_true")
    y = ss.add_parser("missing"); y.add_argument("--all", action="store_true"); y.add_argument("--n", type=int, default=30)
    x.set_defaults(fn=cmd_scene)

    x = sp.add_parser("voice", help="hồ sơ nhân vật: voice <tên gốc> [mô tả giọng] [--gioi --vai-ve --tam-ly --mau --tu-canh]")
    x.add_argument("speaker"); x.add_argument("giong", nargs="?", default="")
    x.add_argument("--mau"); x.add_argument("--gioi", help="nam | nữ | 'nam (vỏ)'…: giới tính người đọc thấy lúc đó")
    x.add_argument("--vai-ve", dest="vai_ve"); x.add_argument("--tam-ly", dest="tam_ly", help="tính cách, tâm lý (một dòng)")
    x.add_argument("--tu-canh", dest="tu_canh", help="mốc: mã cảnh hoặc id câu; ô trống kế thừa dòng trước")
    x.set_defaults(fn=cmd_voice)

    x = sp.add_parser("minor", help="id giữ nguyên bản gốc: add | list (chỉ đúng id đó)")
    ms = x.add_subparsers(dest="mcmd", required=True)
    y = ms.add_parser("add"); y.add_argument("ids", nargs="+"); y.add_argument("--note")
    ms.add_parser("list")
    x.set_defaults(fn=cmd_minor)

    x = sp.add_parser("export", help="xuất id → văn bản cho adapter ghi vào game")
    x.add_argument("--out"); x.add_argument("--format", choices=["json", "tsv"], default="json")
    x.add_argument("--identity", action="store_true", help="xuất nguyên bản gốc để kiểm adapter khứ hồi")
    x.add_argument("--allow-missing", dest="allow_missing", action="store_true", help="vẫn xuất khi còn câu chưa dịch (bản thử)")
    x.add_argument("--danh-dau", dest="danh_dau", nargs="?", const="auto", default=None,
                   help="bản vá đánh dấu: mọi mục = dấu + câu gốc (mặc định ※; nguồn EN: ^); chữ hiện lên không có dấu là sót")
    x.set_defaults(fn=cmd_export)

    x = sp.add_parser("patchkit", help="tạo CAI_VIETHOA.bat / GO_VIETHOA.bat cho thư mục patch (files/ + manifest.txt)")
    x.add_argument("dir")
    x.add_argument("--game", help="thư mục tệp gốc của game (game chưa cài bản Việt hóa, hoặc bản do 'vgk.py goc' tạo)")
    x.add_argument("--game-win", dest="game_win", help="đường dẫn game trên Windows, ghi vào game_path.txt")
    x.set_defaults(fn=cmd_patchkit)

    x = sp.add_parser("goc", help="game đã cài bản Việt hóa: tạo bản chép tệp gốc (từ _viethoa_backup) cho adapter và patchkit")
    x.add_argument("--game", required=True); x.add_argument("--out", required=True, help="thư mục mới, ngoài thư mục game")
    x.add_argument("--sub", action="append", help="chỉ chép phần này của game (lặp được), vd www hoặc data; mặc định cả game")
    x.set_defaults(fn=cmd_goc)

    x = sp.add_parser("backup", help="sao lưu hồ sơ, bản dịch, công cụ vào backup/<giờ>")
    x.add_argument("--note"); x.add_argument("--compact", action="store_true", help="gọn tr.jsonl sau khi sao lưu")
    x.set_defaults(fn=cmd_backup)

    x = sp.add_parser("hash", help="sha256 (16 ký tự) và kích thước, để so bản sau khi chép")
    x.add_argument("files", nargs="+")
    x.set_defaults(fn=cmd_hash)

    x = sp.add_parser("font", help="kiểm font (ttf/otf/ttc/woff) có đủ ký tự tiếng Việt không")
    x.add_argument("files", nargs="+")
    x.add_argument("--text", help="export.json: kiểm thêm mọi ký tự thực dùng trong bản dịch")
    x.set_defaults(fn=cmd_font)

    x = sp.add_parser("phieu", help="phiếu báo của người dịch: liệt kê (--all cả phiếu đã đóng) | dong <n,n|all> --tra-loi")
    x.add_argument("--all", action="store_true")
    ps = x.add_subparsers(dest="phcmd")
    y = ps.add_parser("dong"); y.add_argument("n"); y.add_argument("--tra-loi", dest="tra_loi")
    x.set_defaults(fn=cmd_phieu)

    x = sp.add_parser("doc-lai", help="in N câu thoại đã dịch gần nhất trước chỗ đang dịch (người dịch mới đọc để bắt giọng)")
    x.add_argument("--n", type=int, default=30)
    x.set_defaults(fn=cmd_doclai)

    x = sp.add_parser("khoi-dong", help="mở đầu cho agent dịch: in một lần bible chung, hồ sơ nguồn và thể loại, "
                      "người lớn (game 18+), sổ tay giọng, N câu đã dịch gần nhất và lô đầu của dải")
    x.add_argument("--batch", type=int, required=True, help="lô đầu của dải")
    x.add_argument("--den", type=int, help="lô cuối của dải: write --tiep dừng sau lô này")
    x.add_argument("--phien", help="mã phiên (mặc định '<lô đầu>-<lô cuối>')")
    x.add_argument("--n", type=int, default=30, help="số câu đã dịch gần nhất in kèm")
    x.set_defaults(fn=cmd_khoidong)

    x = sp.add_parser("doc-chuong", help="vòng đọc chương (phiên chính): bài đọc tiếng Việt, số đo, phiếu mở | xong --ghi-chu")
    x.add_argument("--n", type=int, default=150, help="số câu tối đa của bài đọc"); x.add_argument("--seed", type=int)
    ds = x.add_subparsers(dest="dccmd")
    y = ds.add_parser("xong"); y.add_argument("--ghi-chu", dest="ghi_chu")
    x.set_defaults(fn=cmd_doc_chuong)

    x = sp.add_parser("anh-huong", help="câu đã dịch bị ảnh hưởng vì bible đổi từ lần đọc chương trước; --sua: thêm vào danh sách sửa")
    x.add_argument("--tu", help="thư mục ảnh chụp để so (mặc định bible_snap/)")
    x.add_argument("--sua", action="store_true"); x.add_argument("--toi-da", dest="toi_da", type=int, default=500)
    x.add_argument("--force", action="store_true")
    x.set_defaults(fn=cmd_anhhuong)

    x = sp.add_parser("sua", help="câu cần sửa theo bible mới: them | next | bo | status")
    ss = x.add_subparsers(dest="scmd", required=True)
    y = ss.add_parser("them"); y.add_argument("ids", nargs="*"); y.add_argument("--tep", help="tệp TSV id<TAB>lý do (vd reports/anh-huong-*.txt)")
    y.add_argument("--ly-do", dest="ly_do")
    y = ss.add_parser("next"); y.add_argument("--n", type=int, default=40)
    y = ss.add_parser("bo"); y.add_argument("ids", nargs="+", help="id, hoặc all")
    ss.add_parser("status")
    x.set_defaults(fn=cmd_sua)

    x = sp.add_parser("version")
    x.set_defaults(fn=cmd_version)
    return ap


def work_lock():
    """Khoa WORK trong luc mot lenh chay: nhieu agent cung WORK khong ghi chong len nhau.
    Tep .vgk.lock duoc giu lai (vgk khong xoa tep); khoa tu nha khi tien trinh ket thuc."""
    path = os.path.join(WORK, ".vgk.lock")
    try:
        f = open(path, "a+")
    except OSError:
        return None
    try:
        import fcntl

        def take():
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except ImportError:
        try:
            import msvcrt
        except ImportError:
            return f

        def take():
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
    waited = 0.0
    while True:
        try:
            take()
            return f
        except OSError:
            if waited == 0:
                print("Đang chờ khóa WORK: một lệnh vgk khác đang chạy trong WORK này…", file=sys.stderr)
            if waited >= 90:
                die("WORK bị khóa quá 90 giây (một lệnh vgk khác chưa xong). Chạy lại sau.")
            time.sleep(0.5)
            waited += 0.5


def main(argv=None):
    global WORK
    a = build_parser().parse_args(argv)
    WORK = a.work
    lock = None
    global STDIN_CACHE
    if getattr(a, "file", None) == "-" and STDIN_CACHE is None:
        STDIN_CACHE = sys.stdin.buffer.read()   # doc het stdin truoc khi khoa WORK: khong giu khoa trong luc cho du lieu
    if (isinstance(WORK, str) and getattr(a, "fn", None) not in (cmd_version, cmd_hash, cmd_font)
            and os.path.exists(os.path.join(WORK, "game.json"))):
        lock = work_lock()
    try:
        a.fn(a)
    except BrokenPipeError:
        try:
            sys.stdout = open(os.devnull, "w")
        except OSError:
            pass


if __name__ == "__main__":
    main()
