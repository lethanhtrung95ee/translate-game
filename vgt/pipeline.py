"""Cac buoc chinh: init -> extract -> bible -> translate -> review -> apply."""
from __future__ import annotations

import csv
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from . import bible as biblemod
from . import patch as patchmod
from .adapters import ADAPTERS, detect
from .backend import ClaudeCodeBackend, MockBackend
from .config import load_config
from .lang import NAMES, detect_corpus, detect_one
from .prompts import (BIBLE_SCHEMA, SYSTEM_BIBLE, SYSTEM_TRANSLATE, TRANSLATE_SCHEMA,
                      lang_line)
from .protect import mask, unmask
from .qa import blocking, check
from .store import Entry, Store, tm_key
from .textfit import norm_punct

REPO = Path(__file__).resolve().parents[1]


class Project:
    def __init__(self, path: Path, log=print):
        self.path = Path(path)
        self.log = log
        self.cfg = load_config(self.path)
        self.store = Store(self.path / "project.db")
        self.game = Path(self.store.get_meta("game_dir", "")) if self.store.get_meta("game_dir") else None
        self.adapter = ADAPTERS.get(self.store.get_meta("adapter", ""))

    @property
    def patch_dir(self) -> Path:
        """Noi giao ban Viet hoa (CAI/GO_VIETHOA.bat). patch.dir tuong doi tinh tu thu muc repo vgt,
        vd "../Cursed Armor" -> Translation/Cursed Armor. Trong = <du an>/patch."""
        d = ((self.cfg.get("patch") or {}).get("dir") or "").strip()
        if not d:
            return self.path / "patch"
        d = Path(d)
        return d if d.is_absolute() else (REPO / d).resolve()

    # ------------------------------------------------------------------ init/extract
    @classmethod
    def init(cls, game_dir: Path, project_dir: Path, adapter: str | None = None, log=print,
             name: str | None = None):
        game_dir = Path(game_dir).resolve()
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
        ad = ADAPTERS[adapter] if adapter else detect(game_dir)
        if not ad:
            raise SystemExit("Khong nhan ra dinh dang game. Dung --adapter table voi file xuat tu "
                             "Translator++ (CSV/XLSX).")
        p = cls(project_dir, log)
        p.store.set_meta("game_dir", str(game_dir))
        p.store.set_meta("adapter", ad.name)
        cfgp = project_dir / "config.yaml"
        if not cfgp.exists():
            text = "# Ghi de cau hinh cho rieng game nay (xem config.default.yaml)\n"
            if name:  # ban Viet hoa giao o Translation/<ten game>/ (chi CAI/GO_VIETHOA.bat)
                text += f'patch:\n  dir: "../{name}"\n'
            cfgp.write_text(text, encoding="utf-8")
        log(f"Da tao du an: adapter={ad.name}, game={game_dir}")
        return cls(project_dir, log)

    def extract(self) -> None:
        if getattr(self.adapter, "patchable", False):
            patchmod.guard_clean(self.game, self.patch_dir)
        entries = self.adapter.extract(self.game, self.cfg)
        added, changed = self.store.upsert_entries(entries)
        lang, stats = detect_corpus([e.source for e in entries if e.kind == "dialogue"]
                                    or [e.source for e in entries])
        lang = self.cfg.get("source_lang") or lang  # ghi de khi tu nhan sai (game lan 2 ngon ngu)
        self.store.set_meta("source_lang", lang)
        kinds = Counter(e.kind for e in entries)
        self.log(f"Trich xuat {len(entries)} dong ({dict(kinds)}); moi {added}, doi {changed}. "
                 f"Ngon ngu nguon: {lang} {stats}")

    # ------------------------------------------------------------------ backend
    def backend(self, kind: str):
        if kind == "mock":
            return MockBackend()
        return ClaudeCodeBackend(self.cfg, self.path / ".claude_work", self.log)

    def model_of(self, role: str) -> tuple[str, str | None]:
        """Vai tro (bible, dialogue, ui...) -> (model, muc effort)."""
        return self.cfg["models"][role], (self.cfg.get("effort") or {}).get(role)

    def _call(self, be, system, payload, schema, role, purpose, n):
        prompt = "#JSON\n" + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        model, effort = self.model_of(role)
        try:
            r = be.call(system, prompt, schema, model, effort)
        except Exception as e:
            self.store.log_run(model, purpose, n, {}, 0, False, str(e)[:200])
            raise
        self.store.log_run(model, purpose, n, r["usage"], r["cost"], True)
        return r["data"]

    # ------------------------------------------------------------------ bible
    def draft_bible(self, backend: str = "claude", sample_chars: int = 60000) -> Path:
        dlg = self.store.entries("kind='dialogue'")
        spk = Counter()
        samples = defaultdict(list)
        for e in dlg:
            key = e.speaker or (f"face:{e.face}" if e.face else None)
            if key:
                spk[key] += 1
                if len(samples[key]) < 6:
                    samples[key].append(e.source[:200])
        names = [e.source for e in self.store.entries("kind='name'")][:200]
        script, size = [], 0
        for e in dlg:  # mau kich ban theo thu tu, co gan nguoi noi
            line = f"[{e.speaker or e.face or '?'}] {e.source}"
            size += len(line)
            if size > sample_chars:
                break
            script.append(line)
        payload = {
            "lang": lang_line(self.store.get_meta("source_lang", "ja")),
            "speakers": [{"name": k, "count": c, "samples": samples[k]} for k, c in spk.most_common(60)],
            "names_in_db": names,
            "script_sample": script,
        }
        self.log(f"Soan bible bang {self.model_of('bible')} ({len(script)} dong mau)...")
        data = self._call(self.backend(backend), SYSTEM_BIBLE, payload, BIBLE_SCHEMA, "bible",
                          "bible", len(script))
        old = biblemod.load(self.path)
        data = {"reviewed": False, "source_lang": self.store.get_meta("source_lang"), **data,
                "key_scenes": old.get("key_scenes", [])}
        p = biblemod.save(self.path, data)
        self.log(f"Da ghi {p}. Hay duyet, sua roi dat reviewed: true.")
        return p

    # ------------------------------------------------------------------ translate
    def route(self, e: Entry, bidx) -> str:
        """Tra ve vai tro; model + effort cua vai tro nam trong config (models / effort)."""
        if e.attempts >= 2:
            return "repair"
        if e.kind == "dialogue" and ("deep" in e.tags or bidx.is_key_scene(e.grp)):
            return "key_scene"
        return {"choice": "dialogue", "ui": "ui", "name": "ui",
                "description": "description"}.get(e.kind, "dialogue")

    def _apply_tm(self) -> int:
        n = 0
        for e in self.store.entries("status='new'"):
            hit = self.store.tm_lookup(e)
            if hit:
                e.target, e.status, e.model = hit, "tm", "tm"
                self.store.save_result(e)
                n += 1
        return n

    def _batches(self, pending: list[Entry], bidx):
        b = self.cfg["batch"]
        groups: dict[str, list[Entry]] = defaultdict(list)
        for e in pending:
            groups[self.route(e, bidx)].append(e)
        for model, items in groups.items():
            cur, size = [], 0
            for e in items:
                if cur and (len(cur) >= b["max_entries"] or size + len(e.source) > b["max_source_chars"]):
                    yield model, cur
                    cur, size = [], 0
                cur.append(e)
                size += len(e.source)
            if cur:
                yield model, cur

    def _context(self, batch: list[Entry]) -> list[dict]:
        """Vai dong da dich ngay truoc lo nay trong cung canh, de giu mach va xung ho."""
        first = batch[0]
        k = self.cfg["batch"]["context_lines"]
        if not k or first.kind != "dialogue":
            return []
        prev = self.store.entries("grp=? AND seq<? AND target IS NOT NULL", (first.grp, first.seq))
        return [{"sp": p.speaker, "s": p.source, "v": p.target} for p in prev[-k:]]

    def translate(self, backend: str = "claude", limit: int | None = None, force: bool = False,
                  only_kind: str | None = None) -> None:
        bib = biblemod.load(self.path)
        if not force and not bib.get("reviewed"):
            raise SystemExit("bible.yaml chua duoc duyet (reviewed: true). Chay `vgt bible` roi duyet, "
                             "hoac dung --force de thu nghiem.")
        bidx = biblemod.BibleIndex(bib)
        src_lang = self.store.get_meta("source_lang", "ja")
        n_tm = self._apply_tm()
        if n_tm:
            self.log(f"Translation memory: dung lai {n_tm} dong, khong ton han muc.")
        where = "status IN ('new','qa_fail') AND attempts < ?"
        params: tuple = (self.cfg["max_attempts"],)
        if only_kind:
            where += " AND kind=?"
            params += (only_kind,)
        pending = self.store.entries(where, params)
        # Trung lap: cung khoa TM chi dich 1 lan, roi chep sang cac ban sao.
        uniq, dupes = {}, defaultdict(list)
        for e in pending:
            k = tm_key(e)
            (dupes[k].append(e) if k in uniq else uniq.__setitem__(k, e))
        work = list(uniq.values())
        if limit:
            work = work[:limit]
        self.log(f"Can dich {len(work)} dong (bo {len(pending) - len(uniq)} dong trung lap).")
        be = self.backend(backend)
        for rnd in range(self.cfg["max_attempts"]):
            if not work:
                break
            if rnd:
                self.log(f"Vong {rnd + 1}: dich lai {len(work)} dong loi QA (leo thang model).")
            self._run_batches(be, work, dupes, bidx, src_lang)
            ids = [e.id for e in work]
            work = [e for e in (self.store.entries("id=?", (i,))[0] for i in ids)
                    if e.status == "qa_fail" and e.attempts < self.cfg["max_attempts"]]

    def _run_batches(self, be, work, dupes, bidx, src_lang):
        done = 0
        for model, batch in self._batches(work, bidx):
            masked = {}
            lines = []
            for i, e in enumerate(batch):
                m, codes = mask(e.source)
                masked[e.id] = (m, codes)
                row = {"id": str(i), "k": e.kind, "s": m}
                sp = bidx.speaker_label(e) if e.kind == "dialogue" else None
                if sp:
                    row["sp"] = sp
                if e.qa and e.status == "qa_fail":
                    row["fix"] = "; ".join(x[3:] for x in e.qa if x.startswith("E:"))
                    row["prev"] = e.target
                lines.append(row)
            # Game nguon tieng Anh van co the con dong tieng Nhat chua dich (vd FF Resonance).
            other = {detect_one(e.source) for e in batch} - {src_lang, None, "en"}
            lang = lang_line(src_lang) + (f" Có dòng gốc {', '.join(NAMES[x] for x in sorted(other))}: "
                                          f"dịch thẳng sang tiếng Việt." if other else "")
            payload = {"lang": lang, **bidx.context_for(batch),
                       "before": self._context(batch), "lines": lines}
            payload = {k: v for k, v in payload.items() if v not in ([], {}, None, "")}
            data = self._call(be, SYSTEM_TRANSLATE, payload, TRANSLATE_SCHEMA, model,
                              "translate", len(batch))
            role, model = model, self.model_of(model)[0]
            got = {str(x.get("id")): x.get("v", "") for x in data.get("t", [])}
            for i, e in enumerate(batch):
                m, codes = masked[e.id]
                out = norm_punct(got.get(str(i), ""))
                final = unmask(out, codes)
                e.attempts += 1
                e.model = model
                e.target = final or e.target
                e.qa = check(e, m, out, final, bidx, self.cfg, src_lang)
                e.status = "qa_fail" if blocking(e.qa) else "done"
                self.store.save_result(e)
                for d in dupes.get(tm_key(e), []):
                    d.target, d.status, d.model, d.qa, d.attempts = (e.target, e.status, "dup",
                                                                     e.qa, e.attempts)
                    self.store.save_result(d)
            done += len(batch)
            self.log(f"  [{role}->{model}] {done}/{len(work)}  {self.store.counts()}")

    # ------------------------------------------------------------------ review/report
    def export_review(self, out: Path | None = None) -> Path:
        out = out or self.path / "review.csv"
        bidx = biblemod.BibleIndex(biblemod.load(self.path))
        rows = [e for e in self.store.entries()
                if e.status == "qa_fail" or e.qa or bidx.is_key_scene(e.grp) or "deep" in e.tags]
        with out.open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "kind", "speaker", "source", "target", "qa", "fixed"])
            for e in rows:
                w.writerow([e.id, e.kind, e.speaker or "", e.source, e.target or "",
                            " | ".join(e.qa), ""])
        self.log(f"Danh sach can duyet: {out} ({len(rows)} dong). Sua cot 'fixed' roi chay "
                 f"`vgt review-import`.")
        return out

    def import_review(self, path: Path | None = None) -> int:
        path = path or self.path / "review.csv"
        n = 0
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("fixed", "").strip():
                    e = self.store.entries("id=?", (r["id"],))
                    if e:
                        e = e[0]
                        e.target, e.status, e.qa = r["fixed"], "manual", []
                        self.store.save_result(e)
                        n += 1
        self.log(f"Da nhan {n} ban sua tay (luu vao translation memory).")
        return n

    def status(self) -> str:
        c = self.store.counts()
        lines = [f"Trang thai: {c}"]
        for u in self.store.usage_summary():
            lines.append(f"  {u['model']:<7} {u['purpose']:<9} goi={u['calls']} dong={u['n']} "
                         f"in={u['inp']} out={u['outp']} cache_read={u['cr']} loi={u['fails']} "
                         f"(uoc tinh ${u['cost'] or 0:.2f} neu tinh theo API)")
        return "\n".join(lines)

    def estimate(self) -> str:
        bidx = biblemod.BibleIndex(biblemod.load(self.path))
        pending = self.store.entries("status IN ('new','qa_fail')")
        seen, work = set(), []
        for e in pending:
            k = tm_key(e)
            if k not in seen and not self.store.tm_lookup(e):
                seen.add(k)
                work.append(e)
        per = defaultdict(lambda: [0, 0, 0])
        for model, batch in self._batches(work, bidx):
            per[model][0] += 1
            per[model][1] += len(batch)
            per[model][2] += sum(len(e.source) for e in batch)
        out = [f"Uoc tinh (chua tinh dich lai do QA): {len(work)} dong duy nhat / {len(pending)} dong"]
        for role, (calls, n, chars) in per.items():
            m, eff = self.model_of(role)
            out.append(f"  {role:<11} {m}/{eff or '-':<6} {calls} lan goi, {n} dong, {chars} ky tu nguon")
        return "\n".join(out)

    # ------------------------------------------------------------------ apply
    def apply(self, out_dir: Path | None = None) -> Path:
        """Game engine vgt ghi truc tiep: tao patch (chi file da dich + CAI/GO_VIETHOA), khong chep ca game.
        Adapter bang (Translator++): ghi CSV/XLSX ra output/ de nhap lai."""
        if not getattr(self.adapter, "patchable", False):
            out_dir = Path(out_dir or self.path / "output")
            files = self.adapter.apply(self.game, out_dir, self.store.entries(), self.cfg)
            self.log(f"Da ghi {len(files)} file vao {out_dir}.")
            return out_dir
        patch_dir = Path(out_dir) if out_dir else self.patch_dir
        patchmod.guard_clean(self.game, patch_dir)
        staging = patch_dir.with_name(patch_dir.name + ".tmp")
        if staging.exists():
            shutil.rmtree(staging)
        files = self.adapter.apply(self.game, patchmod.files_dir(staging), self.store.entries(), self.cfg)
        probe = self.adapter.probe(self.game, self.cfg) if hasattr(self.adapter, "probe") else None
        patchmod.build(self.game, staging, files, probe)
        patchmod.replace_dir(staging, patch_dir)
        self.log(f"Da tao patch {len(files)} file o {patch_dir} (game goc khong bi sua). "
                 f"Cai: CAI_VIETHOA.bat, go: GO_VIETHOA.bat.")
        return patch_dir
