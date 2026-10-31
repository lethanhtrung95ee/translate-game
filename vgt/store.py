"""Luu tru du an bang SQLite: cac dong can dich, translation memory, nhat ky su dung.

Moi buoc deu ghi ngay vao DB, nen bi ngat giua chung (het han muc, tat may) thi chay lai
se tiep tuc dung cho cu, khong dich lai dong da xong.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id TEXT PRIMARY KEY,          -- duy nhat, on dinh giua cac lan extract
    file TEXT NOT NULL,           -- file nguon (tuong doi)
    locator TEXT NOT NULL,        -- JSON: vi tri de ghi lai
    grp TEXT NOT NULL,            -- nhom ngu canh (vd 1 su kien/canh)
    seq INTEGER NOT NULL,         -- thu tu trong nhom
    kind TEXT NOT NULL,           -- dialogue | choice | name | ui | description
    speaker TEXT,                 -- ten nguoi noi (neu biet)
    face TEXT,                    -- file mat nhan vat (RPG Maker) de doan nguoi noi
    source TEXT NOT NULL,
    target TEXT,
    status TEXT NOT NULL DEFAULT 'new',  -- new | done | qa_fail | tm | manual
    model TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    qa TEXT,                      -- JSON list loi QA
    tags TEXT                     -- JSON list, vd ["deep"]
);
CREATE INDEX IF NOT EXISTS ix_entries_status ON entries(status);
CREATE INDEX IF NOT EXISTS ix_entries_grp ON entries(grp, seq);
CREATE TABLE IF NOT EXISTS tm (
    key TEXT PRIMARY KEY,         -- hash(kind + speaker + source)
    source TEXT NOT NULL,
    target TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    ts REAL, model TEXT, purpose TEXT, entries INTEGER,
    input_tokens INTEGER, output_tokens INTEGER, cache_read INTEGER, cache_write INTEGER,
    cost_est REAL, ok INTEGER, note TEXT
);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
"""


@dataclass
class Entry:
    id: str
    file: str
    locator: dict
    grp: str
    seq: int
    kind: str
    source: str
    speaker: str | None = None
    face: str | None = None
    target: str | None = None
    status: str = "new"
    model: str | None = None
    attempts: int = 0
    qa: list = field(default_factory=list)
    tags: list = field(default_factory=list)


def tm_key(e: Entry) -> str:
    # Hoi thoai phu thuoc nguoi noi (xung ho), nen kem speaker vao khoa.
    spk = (e.speaker or "") if e.kind == "dialogue" else ""
    return hashlib.sha1(f"{e.kind}\x1f{spk}\x1f{e.source}".encode("utf-8")).hexdigest()


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    # ---- meta ----
    def set_meta(self, k: str, v) -> None:
        self.db.execute("REPLACE INTO meta VALUES (?,?)", (k, json.dumps(v, ensure_ascii=False)))
        self.db.commit()

    def get_meta(self, k: str, default=None):
        r = self.db.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
        return json.loads(r[0]) if r else default

    # ---- entries ----
    def upsert_entries(self, entries: list[Entry]) -> tuple[int, int]:
        """Them dong moi; dong da co ma nguon doi thi reset ve 'new'. Tra (moi, doi)."""
        added = changed = 0
        for e in entries:
            row = self.db.execute("SELECT source FROM entries WHERE id=?", (e.id,)).fetchone()
            if row is None:
                added += 1
                self.db.execute(
                    "INSERT INTO entries (id,file,locator,grp,seq,kind,speaker,face,source,tags)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (e.id, e.file, json.dumps(e.locator), e.grp, e.seq, e.kind, e.speaker,
                     e.face, e.source, json.dumps(e.tags)))
            elif row["source"] != e.source:
                changed += 1
                self.db.execute(
                    "UPDATE entries SET source=?,locator=?,speaker=?,face=?,target=NULL,"
                    "status='new',attempts=0,qa=NULL WHERE id=?",
                    (e.source, json.dumps(e.locator), e.speaker, e.face, e.id))
            else:
                # Cap nhat ca speaker/face: adapter nhan dien nguoi noi tot hon thi ap dung luon.
                self.db.execute("UPDATE entries SET locator=?,grp=?,seq=?,speaker=?,face=? WHERE id=?",
                                (json.dumps(e.locator), e.grp, e.seq, e.speaker, e.face, e.id))
        self.db.commit()
        return added, changed

    @staticmethod
    def _row(r) -> Entry:
        return Entry(id=r["id"], file=r["file"], locator=json.loads(r["locator"]), grp=r["grp"],
                     seq=r["seq"], kind=r["kind"], source=r["source"], speaker=r["speaker"],
                     face=r["face"], target=r["target"], status=r["status"], model=r["model"],
                     attempts=r["attempts"], qa=json.loads(r["qa"] or "[]"),
                     tags=json.loads(r["tags"] or "[]"))

    def entries(self, where: str = "1=1", params: tuple = ()) -> list[Entry]:
        q = f"SELECT * FROM entries WHERE {where} ORDER BY grp, seq"
        return [self._row(r) for r in self.db.execute(q, params)]

    def save_result(self, e: Entry) -> None:
        self.db.execute(
            "UPDATE entries SET target=?,status=?,model=?,attempts=?,qa=? WHERE id=?",
            (e.target, e.status, e.model, e.attempts, json.dumps(e.qa, ensure_ascii=False), e.id))
        if e.status in ("done", "manual") and e.target:
            self.db.execute("REPLACE INTO tm VALUES (?,?,?)", (tm_key(e), e.source, e.target))
        self.db.commit()

    def tm_lookup(self, e: Entry) -> str | None:
        r = self.db.execute("SELECT target FROM tm WHERE key=?", (tm_key(e),)).fetchone()
        return r[0] if r else None

    def counts(self) -> dict:
        return {r[0]: r[1] for r in
                self.db.execute("SELECT status, COUNT(*) FROM entries GROUP BY status")}

    # ---- usage ----
    def log_run(self, model, purpose, n, usage: dict, cost, ok, note="") -> None:
        self.db.execute(
            "INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (time.time(), model, purpose, n, usage.get("input_tokens", 0),
             usage.get("output_tokens", 0), usage.get("cache_read_input_tokens", 0),
             usage.get("cache_creation_input_tokens", 0), cost or 0.0, int(ok), note))
        self.db.commit()

    def usage_summary(self) -> list[dict]:
        q = ("SELECT model, purpose, COUNT(*) calls, SUM(entries) n, SUM(input_tokens) inp,"
             " SUM(output_tokens) outp, SUM(cache_read) cr, SUM(cost_est) cost, SUM(1-ok) fails"
             " FROM runs GROUP BY model, purpose")
        return [dict(r) for r in self.db.execute(q)]
