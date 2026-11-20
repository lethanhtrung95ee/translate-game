"""Thu luong vgt tren MOT CHUONG cua game da co ban dich cu (02/11, vd Legend of Mortal).

Dau vao: file cap {zh: {key: cau goc}, vi: {key: ban cu}}. Lay cac key khop --chuong lam du an nho
(projects/_thu/<ten>), lam bible RIENG cho chuong do (Opus doc tuan tu), chi dao cho canh --canh,
dich canh do bang luong hien tai (dich gia Sonnet) + kiem nghia, roi xuat du lieu doc mu ban cu / ban moi.
Khong dong vao game. Chay tren Windows (can `claude -p`); --backend mock de thu.
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vgt import bible as biblemod  # noqa: E402
from vgt import mach  # noqa: E402
from vgt.pipeline import Project  # noqa: E402
from vgt.store import Entry  # noqa: E402


def canh_cua(key: str, rx: str) -> str:
    m = re.search(rx, key)
    return m.group(1) if m and m.groups() else (m.group(0) if m else key)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", required=True)
    ap.add_argument("--chuong", required=True, help="regex chon key cua chuong, vd 'Story/[A-Z]_S08'")
    ap.add_argument("--canh", required=True, help="regex chon canh dich thu trong chuong, vd '_S0801_01_'")
    ap.add_argument("--nhom", default=r"Story/[A-Z]_S(\d{4}_\d{2})", help="regex (1 nhom) tach id canh tu key")
    ap.add_argument("--ten", required=True)
    ap.add_argument("--backend", default="claude", choices=["claude", "mock"])
    ap.add_argument("--cau-hinh", help="yaml ghi de cau hinh (vd prompt_version: 5)")
    ap.add_argument("--lai-bible", action="store_true", help="lam lai bible cua chuong")
    a = ap.parse_args()
    cap = json.loads(Path(a.cap).read_text(encoding="utf-8"))
    zh, vi = cap["zh"], cap["vi"]
    keys = sorted(k for k in zh if re.search(a.chuong, k))
    if not keys:
        raise SystemExit("Khong co key nao khop --chuong")
    pdir = ROOT / "projects" / "_thu" / a.ten
    pdir.mkdir(parents=True, exist_ok=True)
    p = Project(pdir)
    if a.cau_hinh:
        import yaml
        from vgt.config import _merge
        p.cfg = _merge(p.cfg, yaml.safe_load(Path(a.cau_hinh).read_text(encoding="utf-8")) or {})
    p.store.set_meta("source_lang", "zh")
    es = [Entry(id=k, file="story", locator={"key": k}, grp=canh_cua(k, a.nhom), seq=i, kind="dialogue",
                source=zh[k].replace("\\n", "\n")) for i, k in enumerate(keys)]
    p.store.upsert_entries(es)
    (pdir / "research.md").write_text("(thu 1 chuong, khong tim boi canh ngoai)", encoding="utf-8")
    if a.lai_bible or not biblemod.load(pdir).get("work"):
        print(f"Bible rieng cho chuong: {len(keys)} cau, {sum(len(zh[k]) for k in keys)} ky tu...")
        p.draft_bible(a.backend)
    b = biblemod.load(pdir)
    b["reviewed"] = True
    biblemod.save(pdir, b)
    grp = sorted({e.grp for e in es if re.search(a.canh, e.id)})
    if not grp:
        raise SystemExit("Khong co canh nao khop --canh")
    print("Chi dao canh:", mach.build(p, p.backend(a.backend), grp, force=True))
    p.translate(a.backend, grps=grp, force=True)
    p.review(a.backend, grps=grp)
    rows = [e for e in p.store.entries() if e.grp in grp]
    rows.sort(key=lambda e: e.seq)
    rnd = random.Random()
    out, khoa = [], {}
    for g in grp:
        flip = rnd.random() < 0.5
        dong = []
        for e in rows:
            if e.grp != g:
                continue
            cu, moi = vi.get(e.id, ""), e.target or ""
            x, y = (moi, cu) if flip else (cu, moi)
            dong.append({"X": x, "Y": y})
        out.append({"id": g, "tom_tat": "", "khong_khi": "", "dong": dong})
        khoa[g] = {"X": "moi" if flip else "cu", "Y": "cu" if flip else "moi"}
    od = ROOT / "eval" / "ket_qua"
    od.mkdir(parents=True, exist_ok=True)
    (od / f"doc_{a.ten}_data.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    (od / f"doc_{a.ten}_data.khoa.json").write_text(json.dumps(khoa, ensure_ascii=False), encoding="utf-8")
    cost = sum(u.get("cost", 0) or 0 for u in p.store.usage_summary())
    print(f"Xong: {len(rows)} dong, chi phi ~${cost:.2f} quy doi -> eval/ket_qua/doc_{a.ten}_data.json")


if __name__ == "__main__":
    main()
