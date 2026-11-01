"""Kiem tra file bai hoc: du truong bat buoc, truong may doc hop le, gioi han so bai.
Chay: python tools/check_lessons.py [thu muc goc repo]
In them goi y nang pham vi (bai muc game da gap o >= 2 game) - khong tinh la loi."""
import re
import sys
from pathlib import Path

FIELDS = ["Phạm vi", "Loại", "Chỉ áp dụng khi", "Không áp dụng khi", "Dấu hiệu kiểm tra",
          "Bằng chứng", "Xử lý", "Mức chặn", "Chặn bởi", "Trạng thái"]
LEVELS = ("1-test", "2-qa", "3-config", "4-hướng dẫn")
KINDS = ("ky-thuat", "chat-luong-dich")
MAX_ACTIVE = 40


def _detectors(root: Path):
    sys.path.insert(0, str(root))
    try:
        from vgt.lessons import DETECTORS
        return set(DETECTORS)
    except Exception:  # repo thu (test) khong co vgt
        return None


def check_file(path: Path, detectors=None):
    errs, hints, active = [], [], 0
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"^### ", text, flags=re.M)[1:]
    for b in blocks:
        title = b.splitlines()[0].strip()
        if title.startswith("<"):  # mau
            continue
        got = {m.group(1): m.group(2).strip() for m in re.finditer(r"^- ([^:]+):\s*(.*)$", b, flags=re.M)}
        for f in FIELDS:
            if not got.get(f):
                errs.append(f"{path}: {title}: thieu '{f}'")
        lvl = got.get("Mức chặn", "")
        if lvl and not lvl.startswith(LEVELS):
            errs.append(f"{path}: {title}: 'Mức chặn' phai la mot trong {LEVELS}")
        kind = got.get("Loại", "")
        if kind and kind not in KINDS:
            errs.append(f"{path}: {title}: 'Loại' phai la mot trong {KINDS}")
        if kind == "chat-luong-dich" and not got.get("Luật dịch"):
            errs.append(f"{path}: {title}: bai chat-luong-dich phai co 'Luật dịch' (1 cau dua vao prompt)")
        det = got.get("Dò", "")
        if det and detectors is not None and det not in detectors:
            errs.append(f"{path}: {title}: 'Dò: {det}' khong co trong vgt/lessons.py DETECTORS")
        tags = got.get("Thẻ", "")
        if tags and not all("=" in p for p in tags.split(";") if p.strip()):
            errs.append(f"{path}: {title}: 'Thẻ' phai dang khoa=gia_tri; khoa=gia_tri")
        seen = [x.strip() for x in got.get("Gặp ở", "").split(",") if x.strip()]
        if len(set(seen)) >= 2 and got.get("Phạm vi", "").startswith("game"):
            hints.append(f"{title}: gap o {len(set(seen))} game -> xet nang len engine/global")
        st = got.get("Trạng thái", "")
        if st.startswith(("mở", "đã chặn")):
            active += 1
    if path.parent.name in ("lessons", "engines") and active > MAX_ACTIVE:
        errs.append(f"{path}: {active} bai dang hieu luc > {MAX_ACTIVE}, can gop/rut gon")
    return errs, hints


def run(root: Path, with_hints: bool = False):
    files = list((root / "docs" / "lessons").rglob("*.md")) + list((root / "projects").glob("*/LESSONS.md"))
    files = [f for f in files if f.name not in ("README.md", "TEMPLATE_GAME_LESSONS.md")]
    dets = _detectors(root)
    errs, hints = [], []
    for f in files:
        e, h = check_file(f, dets)
        errs += e
        hints += h
    return (files, errs, hints) if with_hints else (files, errs)


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    files, errs, hints = run(root, with_hints=True)
    for e in errs:
        print(e)
    for h in hints:
        print("goi y:", h)
    print(f"{len(files)} file, {len(errs)} loi")
    sys.exit(1 if errs else 0)
