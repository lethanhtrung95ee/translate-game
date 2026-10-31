"""Bang CSV/XLSX: dung cho file xuat tu Translator++ (moi engine khac: Unity, Unreal, Ren'Py...).

Translator++ lo trich xuat + bao ve the + ghi lai vao game; vgt chi doc/ghi cot ban dich.
Ten cot cau hinh trong config.yaml (muc `table`) vi dinh dang xuat thuc te can kiem chung
voi file that cua ban.
"""
from __future__ import annotations

import csv
from pathlib import Path

from ..store import Entry

DEFAULT_COLS = {
    "source": ["Original Text", "Original", "source", "Source"],
    "target": ["Translation", "Better Translation", "Initial", "target", "Target"],
    "context": ["Context", "context", "Address"],
    "speaker": ["Speaker", "speaker", "Name"],
}


def _pick(header: list[str], names: list[str]) -> int | None:
    for n in names:
        if n in header:
            return header.index(n)
    return None


def _read(path: Path) -> list[list[str]]:
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as fh:
            return [list(r) for r in csv.reader(fh)]
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True).active
    return [["" if v is None else str(v) for v in row] for row in ws.iter_rows(values_only=True)]


def _write(path: Path, rows: list[list[str]]) -> None:
    if path.suffix.lower() == ".csv":
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            csv.writer(fh).writerows(rows)
        return
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    wb.save(path)


class TableAdapter:
    name = "table"

    @staticmethod
    def detect(game: Path) -> bool:
        return game.is_dir() and (any(game.glob("*.csv")) or any(game.glob("*.xlsx")))

    @staticmethod
    def _cols(header, cfg):
        conf = {**DEFAULT_COLS, **{k: [v] for k, v in (cfg.get("table") or {}).items()}}
        return {k: _pick(header, v) for k, v in conf.items()}

    @classmethod
    def extract(cls, game: Path, cfg: dict | None = None) -> list[Entry]:
        out = []
        for f in sorted([*game.glob("*.csv"), *game.glob("*.xlsx")]):
            rows = _read(f)
            if not rows:
                continue
            c = cls._cols(rows[0], cfg or {})
            if c["source"] is None:
                continue
            for r, row in enumerate(rows[1:], start=1):
                src = row[c["source"]] if c["source"] < len(row) else ""
                if not src.strip():
                    continue
                ctx = row[c["context"]] if c["context"] is not None and c["context"] < len(row) else ""
                spk = row[c["speaker"]] if c["speaker"] is not None and c["speaker"] < len(row) else None
                # Nhom theo tien to ngu canh (vd "Map001/ev3") de giu mach hoi thoai.
                grp = f"{f.name}:{ctx.rsplit('/', 1)[0] if ctx else r // 50}"
                kind = "ui" if len(src) <= 12 and "\n" not in src and not spk else "dialogue"
                out.append(Entry(id=f"{f.name}#{r}", file=f.name, locator={"row": r},
                                 grp=grp, seq=r, kind=kind, source=src, speaker=spk or None))
        return out

    @classmethod
    def apply(cls, game: Path, out_dir: Path, entries: list[Entry], cfg: dict) -> list[Path]:
        by_file: dict[str, list[Entry]] = {}
        for e in entries:
            if e.target and e.status in ("done", "manual", "tm"):
                by_file.setdefault(e.file, []).append(e)
        written = []
        for fname, items in by_file.items():
            rows = _read(game / fname)
            c = cls._cols(rows[0], cfg)
            tcol = c["target"]
            if tcol is None:
                rows[0].append("Translation")
                tcol = len(rows[0]) - 1
            for e in items:
                row = rows[e.locator["row"]]
                row.extend([""] * (tcol + 1 - len(row)))
                row[tcol] = e.target
            out_dir.mkdir(parents=True, exist_ok=True)
            dst = out_dir / fname
            _write(dst, rows)
            written.append(dst)
        return written

