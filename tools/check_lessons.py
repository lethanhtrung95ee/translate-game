"""Kiem tra file bai hoc: du truong bat buoc, gioi han so bai.
Chay: python tools/check_lessons.py [thu muc goc repo]"""
import re, sys
from pathlib import Path

FIELDS = ["Phạm vi", "Chỉ áp dụng khi", "Không áp dụng khi", "Dấu hiệu kiểm tra",
          "Bằng chứng", "Xử lý", "Mức chặn", "Chặn bởi", "Trạng thái"]
LEVELS = ("1-test", "2-qa", "3-config", "4-hướng dẫn")
MAX_ACTIVE = 40


def check_file(path: Path):
    errs, active = [], 0
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
        st = got.get("Trạng thái", "")
        if st.startswith(("mở", "đã chặn")):
            active += 1
    if path.parent.name in ("lessons", "engines") and active > MAX_ACTIVE:
        errs.append(f"{path}: {active} bai dang hieu luc > {MAX_ACTIVE}, can gop/rut gon")
    return errs


def run(root: Path):
    files = list((root / "docs" / "lessons").rglob("*.md")) + list((root / "projects").glob("*/LESSONS.md"))
    files = [f for f in files if f.name not in ("README.md", "TEMPLATE_GAME_LESSONS.md")]
    errs = []
    for f in files:
        errs += check_file(f)
    return files, errs


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    files, errs = run(root)
    for e in errs:
        print(e)
    print(f"{len(files)} file, {len(errs)} loi")
    sys.exit(1 if errs else 0)
