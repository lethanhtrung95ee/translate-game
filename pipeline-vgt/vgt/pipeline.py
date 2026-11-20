"""Cac buoc chinh: init -> extract -> bible -> translate -> review -> apply."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import time
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from . import bible as biblemod
from . import dossier
from . import lessons as lessonsmod
from .batching import pack
from . import patch as patchmod
from . import review as reviewmod
from .adapters import ADAPTERS, detect
from .backend import BackendError, ClaudeCodeBackend, MockBackend
from .config import load_config
from .lang import NAMES, detect_corpus, detect_one
from .prompts import (BIBLE_SCHEMA, SYSTEM_BIBLE, SYSTEM_TRANSLATE, SYSTEM_TRANSLATE_V3, SYSTEM_TRANSLATE_V4, SYSTEM_TRANSLATE_V5, TRANSLATE_SCHEMA,
                      lang_line, POLISH_SCHEMA, SYSTEM_POLISH)
from .protect import mask, unmask
from .prompts import SYSTEM_REVIEW, SYSTEM_REVIEW_NGHIA, mach_block, phuong_ngu_block, van_phong_block
from .qa import blocking, check
from .scan import line_hints, space_codes
from .store import Entry, Store, tm_key
from .textfit import norm_punct

REPO = Path(__file__).resolve().parents[1]


def add_fixed(base: str, fixed: dict) -> str:
    """System prompt + ho so co dinh (style, premise) cua game. Dung chung cho pipeline va vgt eval."""
    if not fixed:
        return base
    return base + ("\n\nHỒ SƠ CỐ ĐỊNH CỦA TÁC PHẨM (style, work.premise — áp dụng cho mọi lô):\n"
                   + json.dumps(fixed, ensure_ascii=False, separators=(",", ":")))


def add_rules(base: str, rules: list[str]) -> str:
    if not rules:
        return base
    return base + "\n\nBÀI HỌC TỪ CÁC GAME TRƯỚC (bắt buộc):\n" + "\n".join(f"- {r}" for r in rules)


def add_adult(base: str, src_lang: str | None) -> str:
    """Game nguoi lon: them THANG TU NGU 18+ chung (G-022) vao system prompt (cache duoc)."""
    from .adult import prompt_block
    return base + "\n\n" + prompt_block(src_lang)


def translate_system(cfg: dict) -> str:
    v = cfg.get("prompt_version")
    if v == 5:
        return SYSTEM_TRANSLATE_V5
    return SYSTEM_TRANSLATE_V4 if v == 4 else SYSTEM_TRANSLATE_V3 if v == 3 else SYSTEM_TRANSLATE


class Project:
    def __init__(self, path: Path, log=print):
        self.path = Path(path)
        self.log = log
        self.cfg = load_config(self.path)
        self.cfg["_project_dir"] = str(self.path)  # adapter can noi lam viec rieng (vd linguagacha)
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
        self._extract_reference(entries, lang)
        kinds = Counter(e.kind for e in entries)
        self.log(f"Trich xuat {len(entries)} dong ({dict(kinds)}); moi {added}, doi {changed}. "
                 f"Ngon ngu nguon: {lang} {stats}")

    def reference_dir(self, src_lang: str | None = None) -> str | None:
        """Ban tham khao cung vi tri dong (vd tieng Anh chinh thuc) de dich gia/kiem dinh vien hieu dung
        cau goc mo ho. Dich van tu ban goc. config reference.data_dir; reference.enabled: false de tat.
        Tu nhan: RPG Maker co www/dataEN canh www/data va nguon khong phai tieng Anh."""
        r = self.cfg.get("reference") or {}
        if r.get("enabled") is False:
            return None
        if r.get("data_dir"):
            return r["data_dir"]
        if self.adapter and self.adapter.name == "unreal_locres":
            src_c = (self.cfg.get("unreal") or {}).get("source_culture") or "en"
            ref_c = r.get("culture") or ("en" if src_c != "en" else None)
            return f"culture:{ref_c}" if ref_c and ref_c != src_c else None
        if self.adapter and self.adapter.name == "rpgmaker_mvmz" and (src_lang or "") != "en":
            for d in ("www/dataEN", "dataEN", "www/data_en", "data_en"):
                if (Path(self.game) / d / "System.json").exists():
                    return d
        return None

    def _extract_reference(self, entries, src_lang) -> None:
        d = self.reference_dir(src_lang)
        if not d or self.adapter.name not in ("rpgmaker_mvmz", "unreal_locres"):
            return
        if d.startswith("culture:"):  # Unreal: ban tham khao = culture khac trong cung locres
            cfg = {**self.cfg, "unreal": {**self.cfg.get("unreal", {}), "source_culture": d[8:]}}
        else:
            cfg = {**self.cfg, "rpgmaker": {**self.cfg.get("rpgmaker", {}), "data_dir": d, "js_tables": []}}
        src = {e.id: e.source for e in entries}
        refs = {e.id: e.source for e in self.adapter.extract(self.game, cfg)
                if e.id in src and e.source.strip() and e.source != src[e.id]}
        self.store.set_refs(refs)
        self.log(f"Ban tham khao {d}: {len(refs)}/{len(src)} dong khop vi tri (chi de hieu nghia).")

    # ------------------------------------------------------------------ backend
    def backend(self, kind: str):
        if kind == "mock":
            return MockBackend()
        return ClaudeCodeBackend(self.cfg, self.path / ".claude_work", self._backend_log)

    # ------------------------------------------------------------------ chay tiep an toan
    def _backend_log(self, msg: str) -> None:
        self.log(msg)
        if "[han muc]" in msg:
            self.progress(cho_han_muc=msg[:300])
        elif "[mang]" in msg:
            self.progress(loi_mang=msg[:300])

    def progress(self, **kw) -> None:
        """projects/<game>/TIEN_DO.json: buoc hien tai, so dong xong, lan cho han muc/loi gan nhat.
        Ghi lien tuc de nguoi dung/phien sau biet dang o dau ma khong can doc log."""
        f = self.path / "TIEN_DO.json"
        try:
            d = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        except (OSError, ValueError):
            d = {}
        d.update(kw)
        d["cap_nhat"] = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError:
            pass

    def bible_version(self) -> str:
        """Dau van tay cua ho so (bible + scenes, bo co reviewed). Doi -> dong dich theo ho so cu
        duoc kiem dinh vien cham lai."""
        b = dict(biblemod.load(self.path))
        b.pop("reviewed", None)
        sc = biblemod.load_scenes(self.path)
        if not b and not sc:
            return ""
        raw = json.dumps([b, sc], sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]

    def system_prompt(self, base: str, bidx=None) -> str:
        """Prompt he thong + luat dich tu bai hoc + ho so co dinh (style, premise) cua game.
        Co dinh trong 1 lan chay -> duoc cache."""
        kind = "review" if base.startswith((SYSTEM_REVIEW[:60], SYSTEM_REVIEW_NGHIA[:60])) else "dich"
        if biblemod.load_mach(self.path):  # chi dao canh (vgt mach): voi dich gia dat LEN DAU (nguon hieu chinh)
            base = (mach_block(kind) + "\n\n" + base) if kind == "dich" else (base + "\n\n" + mach_block(kind))
        base = add_fixed(base, bidx.fixed_context() if bidx is not None else {})
        if kind == "dich" and self.cfg.get("prompt_version") == 5:
            return base  # gon: khong chong van phong / thang 18+ / bai hoc len dich gia (02/11)
        pn = phuong_ngu_block(self.cfg)
        if pn:
            base = base + "\n\n" + pn
        vp = "" if base.startswith(SYSTEM_REVIEW_NGHIA[:60]) else van_phong_block(self.is_adult())  # kiem nghia: khong cham van phong
        if vp:
            base = base + "\n\n" + vp
        if self.is_adult():
            base = add_adult(base, self.store.get_meta("source_lang", None))
        if getattr(self, "_rules", None) is None:
            try:
                self._rules = lessonsmod.quality_rules(self)
            except Exception as e:  # bai hoc loi khong duoc lam dung dich
                self.log(f"[bai hoc] bo qua: {e}")
                self._rules = []
        return add_rules(base, self._rules)

    def old_bible_lines(self) -> int:
        return self.store.db.execute(
            "SELECT COUNT(*) FROM entries WHERE bible_ver IS NOT NULL AND bible_ver != ?",
            (self.bible_version(),)).fetchone()[0]

    def model_of(self, role: str) -> tuple[str, str | None]:
        """Vai tro (bible, dialogue, ui...) -> (model, muc effort)."""
        return self.cfg["models"][role], (self.cfg.get("effort") or {}).get(role)

    def _call(self, be, system, payload, schema, role, purpose, n):
        prompt = "#JSON\n" + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        model, effort = self.model_of(role)
        long = role in ("bible_read", "bible")
        try:
            r = be.call(system, prompt, schema, model, effort,
                        timeout=self.cfg["claude"].get("timeout_long_sec") if long else None)
        except Exception as e:
            self.store.log_run(model, purpose, n, {}, 0, False, str(e)[:200])
            raise
        self.store.log_run(model, purpose, n, r["usage"], r["cost"], True)
        return r["data"]

    # ------------------------------------------------------------------ bible
    def draft_bible(self, backend: str = "claude", sample_chars: int = 60000,
                    full: bool = True) -> Path:
        """full: doc TOAN BO kich ban (vgt/dossier.py) -> bible.yaml + scenes.yaml.
        full=False: cach cu, chi doc sample_chars ky tu dau (nhanh, re, kem chinh xac)."""
        if full:
            old = self.path / "bible.yaml"
            if old.exists() and biblemod.load(self.path).get("reviewed"):
                shutil.copyfile(old, self.path / "bible.prev.yaml")  # ban da duyet truoc do
            self.log(f"Soan ho so tac pham: {self.model_of('bible_read')} doc toan bo kich ban, "
                     f"{self.model_of('bible')} gop...")
            bible, scenes = dossier.build(self, self.backend(backend))
            biblemod.save_scenes(self.path, scenes)
            p = biblemod.save(self.path, bible)
            n = len(bible.get("can_xac_nhan") or [])
            self.log(f"Da ghi {p} ({len(bible.get('characters') or [])} nhan vat, {len(scenes)} canh "
                     f"co tom tat, {n} muc CAN XAC NHAN). Hay ra soat roi dat reviewed: true.")
            return p
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
        """Che do scene: loi thoai/lua chon chia lo theo tung canh (1 lo = 1 grp, canh dai thi cat),
        de dich lien mach kem tom tat canh. Con lai (ui, ten, mo ta, dich lai) chia nhu cu."""
        b = self.cfg["batch"]
        groups: dict[str, list[Entry]] = defaultdict(list)
        scened: dict[str, dict[str, list[Entry]]] = defaultdict(lambda: defaultdict(list))
        for e in pending:
            role = self.route(e, bidx)
            if b.get("mode", "flat") == "scene" and e.kind in ("dialogue", "choice"):
                scened[role][e.grp].append(e)  # ke ca dich lai (repair): van kem tom tat canh
            else:
                groups[role].append(e)
        # Canh nho lien tiep gom chung 1 lo (khong ton 1 lan goi/canh); canh lon cat nho.
        for role, by_grp in scened.items():
            for batch in pack(list(by_grp.values()), b["max_entries"], b["max_source_chars"]):
                yield role, batch
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
                  only_kind: str | None = None, grps: list[str] | None = None) -> None:
        bib = biblemod.load(self.path)
        if not force and not bib.get("reviewed"):
            raise SystemExit("bible.yaml chua duoc duyet (reviewed: true). Chay `vgt bible` roi duyet, "
                             "hoac dung --force de thu nghiem.")
        bidx = biblemod.BibleIndex(bib)
        src_lang = self.store.get_meta("source_lang", "ja")
        self._bver = self.bible_version()
        n_old = self.old_bible_lines()
        if n_old:
            self.log(f"Canh bao: {n_old} dong da dich theo ho so cu (bible/scenes da doi). "
                     f"`vgt review` se cham lai cac dong nay theo ho so moi.")
        n_tm = self._apply_tm()
        if n_tm:
            self.log(f"Translation memory: dung lai {n_tm} dong, khong ton han muc.")
        n_ok = self._recheck_qa_fail(bidx, src_lang, grps)
        if n_ok:
            self.log(f"QA lai: {n_ok} dong qa_fail nay da dat (luat QA da doi), khong can dich lai.")
        where = "status IN ('new','qa_fail') AND attempts < ?"
        params: tuple = (self.cfg["max_attempts"],)
        if only_kind:
            where += " AND kind=?"
            params += (only_kind,)
        if grps:
            where += f" AND grp IN ({','.join('?' * len(grps))})"
            params += tuple(grps)
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
            self._run_batches(be, work, dupes, bidx, src_lang, biblemod.load_scene_ctx(self.path))
            ids = [e.id for e in work]
            work = [e for e in (self.store.entries("id=?", (i,))[0] for i in ids)
                    if e.status == "qa_fail" and e.attempts < self.cfg["max_attempts"]]
        n_keep = self._keep_original_refused()
        if n_keep:
            self.log(f"{n_keep} dong model khong dich: giu ban tieng Anh chinh thuc / ban goc ([giữ gốc]).")

    def _keep_original(self, e: Entry, why: str) -> None:
        """Dong Claude khong dich: giu ban tieng Anh chinh thuc cua game neu co (nguoi dung doc duoc),
        khong thi giu nguyen ban goc. Khong goi lai, khong chuyen sang cong cu khac (G-022)."""
        e.target = e.ref or e.source
        e.status, e.attempts = "manual", self.cfg["max_attempts"]
        e.qa = [f"W: [giữ gốc] {why}; dùng {'bản tiếng Anh chính thức' if e.ref else 'nguyên văn gốc'} (G-022)"]
        self.store.save_result(e)

    def kept_original(self) -> list:
        return [e for e in self.store.entries("status='manual'") if any("[giữ gốc]" in x for x in e.qa)]

    def _keep_original_refused(self) -> int:
        n = 0
        for e in self.store.entries("status='qa_fail'"):
            if any("[từ chối]" in x for x in e.qa) and e.attempts >= self.cfg["max_attempts"]:
                self._keep_original(e, "model trả lời thay vì dịch")
                n += 1
        return n

    def _recheck_qa_fail(self, bidx, src_lang, grps=None) -> int:
        """Dong qa_fail chi vi loi QA tu dong (khong phai kiem dinh vien): chay lai QA hien tai.

        Luat QA sai (vd glossary gop, cursed_armor_v2 31/10) lam dong bi ket o qa_fail sau
        max_attempts; sua luat xong thi dong dung phai tu thoat ra ma khong ton them lan goi.
        """
        where, params = "status='qa_fail' AND target IS NOT NULL AND target!=''", ()
        if grps:
            where += f" AND grp IN ({','.join('?' * len(grps))})"
            params = tuple(grps)
        n = 0
        for e in self.store.entries(where, params):
            if any("[kiểm định]" in x for x in e.qa):
                continue
            m, c_src = mask(e.source)
            _, c_out = mask(e.target)
            notes = [x for x in e.qa if x.startswith("N:")]
            e.qa = check(e, m, m if sorted(c_src) == sorted(c_out) else "", e.target, bidx,
                         self.cfg, src_lang) + notes
            if not blocking(e.qa):
                e.status = "done"
                self.store.save_result(e)
                n += 1
        return n

    def _run_batches(self, be, work, dupes, bidx, src_lang, scenes=None):
        done = 0
        for model, batch in self._batches(work, bidx):
            self._do_batch(be, model, batch, dupes, bidx, src_lang, scenes)
            done += len(batch)
            self.log(f"  [{model}->{self.model_of(model)[0]}] {done}/{len(work)}  {self.store.counts()}")
            self.progress(buoc="translate", lo=f"{done}/{len(work)}", trang_thai=self.store.counts())

    def _do_batch(self, be, model, batch, dupes, bidx, src_lang, scenes=None):
        """Dich 1 lo. Model khong tra ket qua (vd tu choi ca lo vi 1 dong): chia doi tim dung dong,
        dong con lai van dich binh thuong; dong tu choi ghi '[từ chối]', khong bi bo qua am tham (G-022)."""
        if True:
            masked = {}
            lines = []
            multi = len({e.grp for e in batch}) > 1
            xh = self._address_hints(batch, bidx)
            # Canh co chi dao (xung ho cua dung khoanh khac) -> bo goi y xung ho theo cap ca game (hai nguon danh nhau)
            cd = {g for g in {e.grp for e in batch} if (((scenes or {}).get(g) or {}).get("mach") or {}).get("xung_ho")}
            for i, e in enumerate(batch):
                m, codes = mask(e.source)
                masked[e.id] = (m, codes)
                row = {"id": str(i), "k": e.kind, "s": m}
                if multi and e.kind in ("dialogue", "choice"):
                    row["g"] = e.grp
                if e.ref:
                    row["en"] = e.ref
                sp = bidx.speaker_label(e) if e.kind == "dialogue" else None
                if sp:
                    row["sp"] = sp
                if xh.get(e.id) and e.grp not in cd:
                    row["xh"] = xh[e.id]
                if e.qa and e.status == "qa_fail":
                    row["fix"] = "; ".join(x[3:] for x in e.qa if x.startswith("E:"))
                    row["prev"] = e.target
                lines.append(row)
            # Game nguon tieng Anh van co the con dong tieng Nhat chua dich (vd FF Resonance).
            other = {detect_one(e.source) for e in batch} - {src_lang, None, "en"}
            lang = lang_line(src_lang) + (f" Có dòng gốc {', '.join(NAMES[x] for x in sorted(other))}: "
                                          f"dịch thẳng sang tiếng Việt." if other else "")
            sc = {g: (scenes or {})[g] for g in dict.fromkeys(e.grp for e in batch)
                  if g in (scenes or {})}
            payload = {"lang": lang, **bidx.context_for(batch),
                       **({"scenes": sc} if multi else {"scene": sc.get(batch[0].grp)}),
                       "before": self._context(batch), "lines": lines}
            payload = {k: v for k, v in payload.items() if v not in ([], {}, None, "")}
            try:
                data = self._call(be, self.system_prompt(translate_system(self.cfg), bidx), payload, TRANSLATE_SCHEMA,
                                  model, "translate", len(batch))
            except BackendError as err:
                if len(batch) > 1:
                    mid = len(batch) // 2
                    self.log(f"  Lo {len(batch)} dong loi ({str(err)[:80]}) -> chia doi de tim dong gay loi")
                    self._do_batch(be, model, batch[:mid], dupes, bidx, src_lang, scenes)
                    self._do_batch(be, model, batch[mid:], dupes, bidx, src_lang, scenes)
                    return
                e = batch[0]
                self._keep_original(e, f"model không trả bản dịch: {str(err)[:100]}")
                self.log(f"  Dong {e.id}: model khong dich -> giu ban tieng Anh chinh thuc / ban goc")
                return
            role, model = model, self.model_of(model)[0]
            got = {str(x.get("id")): x.get("v", "") for x in data.get("t", [])}
            outmask = {}
            notes = {str(x.get("id")): (x.get("n") or "").strip() for x in data.get("t", [])}
            for i, e in enumerate(batch):
                m, codes = masked[e.id]
                out = norm_punct(got.get(str(i), ""))
                final = space_codes(unmask(out, codes))
                e.attempts += 1
                e.model = model
                e.bible_ver = getattr(self, "_bver", None)
                e.target = final or e.target
                e.qa = check(e, m, out, final, bidx, self.cfg, src_lang) + line_hints(e, src_lang, bidx.genre())
                if notes.get(str(i)):  # ghi chu chien luoc cua dich gia -> kiem dinh vien doc
                    e.qa.append("N: " + notes[str(i)])
                e.status = "qa_fail" if blocking(e.qa) else "done"
                outmask[e.id] = out
                self.store.save_result(e)
                self._sync_dupes(e, dupes)
            pol = self.cfg.get("polish") or {}
            if pol.get("enabled") and role in (pol.get("roles") or []):
                self._polish(be, batch, masked, outmask, bidx, sc, src_lang, dupes)

    def _address_hints(self, batch, bidx) -> dict:
        """Xung/goi bat buoc theo tung dong (G-023), tinh tren CA canh (khong chi lo)."""
        out = {}
        for g in dict.fromkeys(e.grp for e in batch):
            out.update(bidx.address_hints(self.store.entries("grp=?", (g,))))
        return out

    def _sync_dupes(self, e, dupes) -> None:
        for d in dupes.get(tm_key(e), []):
            d.target, d.status, d.model, d.qa, d.attempts, d.bible_ver = (
                e.target, e.status, "dup", e.qa, e.attempts, e.bible_ver)
            self.store.save_result(d)

    def _polish(self, be, batch, masked, outmask, bidx, sc, src_lang, dupes) -> None:
        """Bien tap vien doc tron ban tieng Viet (khong nhin cau goc), chi sua cau nghe nhu may dich.
        Ban sua phai qua lai QA cua dong do; hong QA thi giu ban dich cu."""
        rows, idx = [], {}
        for i, e in enumerate(batch):
            if e.status != "done" or e.id not in outmask:
                continue
            row = {"id": str(i), "v": outmask[e.id]}
            sp = bidx.speaker_label(e) if e.kind == "dialogue" else None
            if sp:
                row["sp"] = sp
            rows.append(row)
            idx[str(i)] = e
        if not rows:
            return
        ctx = bidx.context_for(batch)
        payload = {"scenes": sc, "characters": ctx.get("characters"), "relations": ctx.get("relations"),
                   "glossary": ctx.get("glossary"), "lines": rows}
        payload = {k: v for k, v in payload.items() if v}
        try:
            data = self._call(be, self.system_prompt(SYSTEM_POLISH, bidx), payload, POLISH_SCHEMA,
                              "polish", "polish", len(rows))
        except BackendError as err:
            self.log(f"  [bien tap] bo qua lo: {str(err)[:80]}")
            return
        n = 0
        for x in data.get("t") or []:
            e = idx.get(str(x.get("id")))
            v = (x.get("v") or "").strip()
            if not e or not v or v == outmask[e.id]:
                continue
            m, codes = masked[e.id]
            out = norm_punct(v)
            final = space_codes(unmask(out, codes))
            qa = check(e, m, out, final, bidx, self.cfg, src_lang)
            if blocking(qa):
                continue
            e.target = final
            e.qa = qa + line_hints(e, src_lang, bidx.genre()) + [q for q in e.qa if q.startswith("N:")]
            e.model = f"{e.model}+bt"
            self.store.save_result(e)
            self._sync_dupes(e, dupes)
            n += 1
        self.log(f"  [bien tap] sua {n}/{len(rows)} dong")

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

    def review(self, backend: str = "claude", limit: int | None = None,
               grps: list[str] | None = None) -> dict:
        """Kiem dinh vien cham tung canh (vgt/review.py)."""
        if not biblemod.load(self.path).get("reviewed"):
            raise SystemExit("bible.yaml chua duoc duyet (reviewed: true).")
        return reviewmod.run(self, self.backend(backend), limit, grps)

    def status(self) -> str:
        c = self.store.counts()
        lines = [f"Trang thai: {c}"]
        rv = reviewmod.summary(self.store, self.bible_version())
        if rv:
            lines.append(f"Kiem dinh: {rv}")
        n_old = self.old_bible_lines()
        if n_old:
            lines.append(f"Dich theo ho so cu (can cham lai): {n_old} dong")
        qa_all = [x for e in self.store.entries("qa IS NOT NULL AND qa != '[]'") for x in e.qa]
        n_ref = sum(1 for x in qa_all if "[từ chối]" in x or "[giữ gốc]" in x)
        n_soft = sum(1 for x in qa_all if "[làm nhẹ?]" in x)
        if n_ref or n_soft:
            lines.append(f"Trung thanh noi dung: model tu choi {n_ref} dong, nghi lam nhe {n_soft} dong "
                         f"(xem review-export)")
        if (self.path / "TIEN_DO.json").exists():
            lines.append(f"Tien do: {(self.path / 'TIEN_DO.json').read_text(encoding='utf-8')}")
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
        script = dossier.script_entries(self.store)
        n_read = len(dossier.make_chunks(script, self.cfg["dossier"]["chunk_chars"]))
        m, eff = self.model_of("bible_read")
        out.append(f"  {'bible_read':<11} {m}/{eff or '-':<6} {n_read} lan goi (doc "
                   f"{sum(len(e.source) for e in script)} ky tu kich ban) + 1 lan gop (bible)")
        for role, (calls, n, chars) in per.items():
            m, eff = self.model_of(role)
            out.append(f"  {role:<11} {m}/{eff or '-':<6} {calls} lan goi, {n} dong, {chars} ky tu nguon")
        n_rev = reviewmod.calls_needed(self.store, self.cfg["review"])
        m, eff = self.model_of("review")
        out.append(f"  {'review':<11} {m}/{eff or '-':<6} ~{n_rev} lan goi (1 vong, chua tinh cham lai)")
        return "\n".join(out)

    # ------------------------------------------------------------------ nhieu game
    # Trang thai du an (meta "trang_thai"): danh sach "lam tiep" chi hien dang_lam / cho_nguoi_dung.
    STATES = {"dang_lam": "đang làm", "cho_nguoi_dung": "chờ bạn", "xong": "đã xong",
              "tam_dung": "tạm dừng", "luu_tru": "lưu trữ"}
    ACTIVE = ("dang_lam", "cho_nguoi_dung")

    def mark(self, state: str, ten: str | None = None) -> None:
        if state not in self.STATES:
            raise SystemExit(f"Trang thai phai la mot trong: {', '.join(self.STATES)}")
        self.store.set_meta("trang_thai", state)
        if ten:
            self.store.set_meta("ten_hien_thi", ten)
        self.log(f"{self.path.name}: {self.STATES[state]}" + (f" ({ten})" if ten else ""))

    @staticmethod
    def list_projects(root: Path, all_: bool = False) -> list[dict]:
        """Du an trong projects/. Mac dinh chi du an con viec (dang lam / cho ban); all_=True: tat ca."""
        out = []
        for d in sorted(Path(root).iterdir()):
            if not (d / "project.db").exists():
                continue
            st = Store(d / "project.db")
            state = st.get_meta("trang_thai", "dang_lam")
            ten = st.get_meta("ten_hien_thi") or d.name
            st.db.close()
            if not all_ and state not in Project.ACTIVE:
                continue
            prog = {}
            try:
                prog = json.loads((d / "TIEN_DO.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                pass
            nxt = ""
            ck = d / "CHECKPOINT.md"
            if ck.exists():
                txt = ck.read_text(encoding="utf-8")
                if "## Việc tiếp theo" in txt:
                    nxt = txt.split("## Việc tiếp theo", 1)[1].strip().splitlines()[0][:90]
            out.append({"ten": d.name, "ten_hien_thi": ten, "trang_thai": state,
                        "buoc": prog.get("buoc", "-"), "cap_nhat": prog.get("cap_nhat", "-"),
                        "dang_chay": bool(prog.get("dang_chay")), "viec_tiep": nxt})
        return out

    # ------------------------------------------------------------------ so sanh ban cu/moi
    @classmethod
    def fork(cls, src_dir: Path, dst_dir: Path, log=print) -> "Project":
        """Tao du an thu tu du an cu: cung game, cung dong, NHUNG chua dich, khong TM, khong bible,
        patch rieng (khong de len ban Viet hoa that). Dung de dich lai vai canh va so sanh."""
        src = cls(src_dir, log)
        dst_dir = Path(dst_dir)
        if (dst_dir / "project.db").exists():
            raise SystemExit(f"{dst_dir} da co du an.")
        dst_dir.mkdir(parents=True, exist_ok=True)
        cfg = {}
        cp = Path(src_dir) / "config.yaml"
        if cp.exists():
            cfg = yaml.safe_load(cp.read_text(encoding="utf-8")) or {}
        cfg.pop("patch", None)
        (dst_dir / "config.yaml").write_text(
            f"# Du an thu, tach tu {Path(src_dir).name} (vgt fork). Patch o <du an>/patch.\n"
            + (yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False) if cfg else ""), encoding="utf-8")
        for f in ("research.md",):
            if (Path(src_dir) / f).exists():
                shutil.copyfile(Path(src_dir) / f, dst_dir / f)
        dst = cls(dst_dir, log)
        for k in ("game_dir", "adapter", "source_lang"):
            dst.store.set_meta(k, src.store.get_meta(k))
        es = src.store.entries()
        dst.store.upsert_entries([Entry(id=e.id, file=e.file, locator=e.locator, grp=e.grp,
                                        seq=e.seq, kind=e.kind, source=e.source, speaker=e.speaker,
                                        face=e.face, tags=e.tags) for e in es])
        src.store.db.close()
        log(f"Da tao du an thu {dst_dir} ({len(es)} dong, chua dich).")
        return cls(dst_dir, log)

    @staticmethod
    def compare(old_dir: Path, new_dir: Path, out: Path | None = None,
                grps: list[str] | None = None) -> Path:
        """Bang so sanh ban cu / ban moi theo tung canh (HTML) de nguoi dung doc."""
        import html
        old, new = Store(Path(old_dir) / "project.db"), Store(Path(new_dir) / "project.db")
        olds = {e.id: e for e in old.entries()}
        scenes = biblemod.load_scenes(Path(new_dir))
        rows = [e for e in new.entries("target IS NOT NULL") if not grps or e.grp in grps]
        out = Path(out or Path(new_dir) / "so_sanh.html")
        h = ["<!doctype html><meta charset='utf-8'><title>So sánh bản dịch</title><style>"
             "body{font:15px/1.5 system-ui,sans-serif;margin:16px;max-width:1200px}"
             "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:6px;"
             "vertical-align:top}th{background:#eee}.n{color:#777;font-size:13px}"
             "h2{margin-top:28px}</style><h1>So sánh bản dịch cũ / mới</h1>"]
        last = None
        for e in rows:
            if e.grp != last:
                if last is not None:
                    h.append("</table>")
                sc = scenes.get(e.grp) or {}
                h.append(f"<h2>{html.escape(e.grp)}</h2><p class='n'>"
                         f"{html.escape(' · '.join(str(sc[k]) for k in ('summary', 'mood', 'effect') if sc.get(k)))}"
                         "</p><table><tr><th>Người nói</th><th>Gốc</th><th>Bản cũ</th><th>Bản mới</th></tr>")
                last = e.grp
            o = olds.get(e.id)
            notes = "; ".join(x[3:] for x in e.qa if x.startswith("N:") or "[kiểm định]" in x)
            h.append("<tr>" + "".join(f"<td>{html.escape(x or '')}</td>" for x in (
                e.speaker, e.source, o.target if o else "", e.target))
                + "</tr>" + (f"<tr><td></td><td colspan=3 class='n'>{html.escape(notes)}</td></tr>"
                             if notes else ""))
        if last is not None:
            h.append("</table>")
        out.write_text("\n".join(h), encoding="utf-8")
        old.db.close()
        new.db.close()
        return out

    # ------------------------------------------------------------------ may trang thai
    def is_adult(self) -> bool:
        """Game nguoi lon (>= content.adult_min_lines dong co tu nguoi lon): ap chuan 18+ chung."""
        if not (self.cfg.get("content") or {}).get("chuan_18", True):
            return False
        if getattr(self, "_adult", None) is None:
            n = sum(self.adult_scenes().values())
            self._adult = n >= int((self.cfg.get("content") or {}).get("adult_min_lines", 20))
        return self._adult

    def adult_scenes(self) -> dict:
        """{canh: so dong co tu nguoi lon/tuc} (G-022, 1_QUYET_DINH muc 4)."""
        from .adult import table
        from .content import EXPLICIT_SRC
        from .protect import visible
        q = (self.cfg.get("qa") or {})
        t = table()
        skip = set(t.get("qa_bo_qua") or [])
        extra = [w for k in t["khai_niem"] for lv in (k.get("goc") or {}).values() for ws in lv.values()
                 for w in ws if w not in skip]
        terms = list({x.lower() for x in EXPLICIT_SRC + extra + list(q.get("explicit_src") or [])})
        out = defaultdict(int)
        for e in self.store.entries():
            if e.kind in ("dialogue", "choice") and any(t in visible(e.source).lower() for t in terms):
                out[e.grp] += 1
        return dict(out)

    def set_trial(self, grps: list[str], force: bool = False) -> None:
        known = {r[0] for r in self.store.db.execute("SELECT DISTINCT grp FROM entries")}
        bad = [g for g in grps if g not in known]
        if bad:
            raise SystemExit(f"Khong co canh: {bad}")
        # Game 18+: ban thu BAT BUOC co 1 canh nguoi lon (1_QUYET_DINH muc 4, G-022).
        adult = self.adult_scenes()
        need = int((self.cfg.get("content") or {}).get("adult_min_lines", 20))
        if not force and sum(adult.values()) >= need and not any(adult.get(g) for g in grps):
            top = sorted(adult, key=lambda g: -adult[g])[:5]
            raise SystemExit("Game co noi dung nguoi lon: ban thu phai co it nhat 1 canh nguoi lon "
                             f"(1_QUYET_DINH muc 4). Goi y: {', '.join(f'{g} ({adult[g]} dong)' for g in top)}. "
                             "Chac chan khong can: --force.")
        self.store.set_meta("trial_grps", list(grps))
        self.store.set_meta("trial_ok", False)
        self.log(f"Canh thu: {grps}")

    def approve_trial(self) -> None:
        self.store.set_meta("trial_ok", True)
        self.log("Nguoi dung da dong y ban thu -> `vgt run` se dich toan bo.")

    def _sent_back(self, grps=None) -> int:
        es = self.store.entries("status='qa_fail'")
        return sum(1 for e in es if (not grps or e.grp in grps)
                   and any("[kiểm định]" in x for x in e.qa))

    def _translate_review_loop(self, backend: str, grps=None) -> None:
        """Dich -> kiem dinh -> dich lai dong bi tra ve, toi da review.max_rounds + 1 vong (co chan tren)."""
        self.chi_dao(backend, grps)
        for rnd in range(self.cfg["review"]["max_rounds"] + 1):
            self.progress(buoc="translate" if not grps else "thu_translate", vong=rnd + 1)
            self.translate(backend, grps=grps)
            self.progress(buoc="review" if not grps else "thu_review", vong=rnd + 1)
            self.review(backend, grps=grps)
            if not self._sent_back(grps):
                break

    def dich_lai(self, kinds=("dialogue", "choice")) -> dict:
        """Dua cac dong da dich (done/tm/qa_fail) ve 'new' de dich lai theo luong moi (02/11). Xoa ca muc
        bo nho dich (tm) cua cac dong do, khong thi _apply_tm dien lai ban cu. Dong 'manual' (giu goc, nguoi
        dung sua) giu nguyen. Sao luu truoc."""
        from .store import tm_key
        from .term import backup
        bk = backup(self, "dich_lai")
        q = "kind IN (%s) AND status IN ('done','tm','qa_fail')" % ",".join("?" * len(kinds))
        es = self.store.entries(q, tuple(kinds))
        keys = {tm_key(e) for e in es}
        for e in es:
            e.status, e.attempts, e.qa = "new", 0, []
            self.store.save_result(e)
        self.store.db.executemany("DELETE FROM tm WHERE key=?", [(k,) for k in keys])
        self.store.db.commit()
        self.store.set_meta("luong_dich", self.cfg.get("luong_dich", 2))
        return {"dong": len(es), "xoa_tm": len(keys), "sao_luu": str(bk)}

    def chi_dao(self, backend: str, grps=None) -> dict:
        """Chi dao tung canh (vgt/mach.py) truoc khi dich: bien kich truong viet cho moi canh co thoai chua co.
        Chay tiep duoc (ghi sau moi canh). Tat: chi_dao.bat: false."""
        if not (self.cfg.get("chi_dao") or {}).get("bat", True):
            return {}
        from . import mach
        if grps is None:
            grps = [g for (g,) in self.store.db.execute(
                "SELECT DISTINCT grp FROM entries WHERE kind='dialogue' ORDER BY rowid")]
        have = biblemod.load_mach(self.path)
        todo = [g for g in grps if g not in have]
        if not todo:
            return {}
        self.progress(buoc="chi_dao", con=len(todo))
        self.log(f"Chi dao canh: {len(todo)} canh chua co")
        return mach.build(self, self.backend(backend), todo, log=self.log)

    def _trial_suggestions(self, n: int = 6) -> str:
        scenes = biblemod.load_scenes(self.path)
        key = set(biblemod.load(self.path).get("key_scenes") or [])
        size = dict(self.store.db.execute(
            "SELECT grp, COUNT(*) FROM entries WHERE kind IN ('dialogue','choice') GROUP BY grp"))
        cand = sorted((g for g in scenes if size.get(g, 0) >= 10),
                      key=lambda g: (g not in key, -size.get(g, 0)))[:n]
        out = "; ".join(f"{g} ({size.get(g)} dong, {(scenes[g].get('effect') or '')[:30]}: "
                         f"{(scenes[g].get('summary') or '')[:60]})" for g in cand)
        adult = self.adult_scenes()
        if sum(adult.values()) >= int((self.cfg.get("content") or {}).get("adult_min_lines", 20)):
            g = max(adult, key=adult.get)
            out += f" | BAT BUOC 1 canh nguoi lon, vd {g} ({adult[g]} dong co tu nguoi lon)"
        return out

    BUSY_MIN = 40  # TIEN_DO khong cap nhat qua so phut nay -> coi la phien truoc da chet

    def busy(self) -> str | None:
        """Phien khac dang chay `vgt run` tren CUNG du an (nhieu game chay song song la binh thuong,
        nhung 2 phien cung 1 game se ghi de nhau)."""
        f = self.path / "TIEN_DO.json"
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if not d.get("dang_chay"):
            return None
        try:
            age = time.time() - time.mktime(time.strptime(d["cap_nhat"], "%Y-%m-%d %H:%M:%S"))
        except (KeyError, ValueError):
            return None
        return None if age > self.BUSY_MIN * 60 else (
            f"du an dang chay o phien khac (cap nhat {int(age // 60)} phut truoc, buoc {d.get('buoc')})")

    def run(self, backend: str = "claude", force: bool = False) -> str:
        """Chay tiep tu dung cho dang do, tu dung o cac cua can nguoi/phien dieu phoi.
        Tra ve ma buoc dung. Chay lai bao nhieu lan cung an toan (moi buoc deu chay tiep duoc)."""
        why = None if force else self.busy()
        if why:
            raise SystemExit(f"Khong chay: {why}. Chac chan phien kia da tat thi dung --force.")

        def stop(code: str, msg: str) -> str:
            self.progress(buoc=code, can_lam=msg, dang_chay=False)
            self.log(f"[DUNG] {code}: {msg}")
            return code
        self.progress(dang_chay=True)
        try:
            if not self.store.db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]:
                self.progress(buoc="extract")
                self.extract()
            rf = self.path / self.cfg["dossier"].get("research_file", "research.md")
            if not rf.exists():
                return stop("CAN_RESEARCH", f"Phien dieu phoi tim boi canh tren web, ghi {rf} "
                                            "(khong tim duoc thi ghi 'khong co nguon').")
            if not biblemod.load(self.path).get("work"):
                self.progress(buoc="bible")
                self.draft_bible(backend)
            if not biblemod.load(self.path).get("reviewed"):
                return stop("CAN_DUYET_BIBLE", "Ra soat bible.yaml (docs/3_QUY_TRINH.md phu luc A, can_xac_nhan), "
                                               "dat reviewed: true roi `vgt run` lai.")
            bc = self.cfg.get("bible_check") or {}
            if bc.get("block", True) and not self.store.get_meta("xung_ho_ok"):
                from . import biblecheck, xungho
                iss = xungho.issues(self)
                if not self.store.get_meta("xung_ho_duyet"):
                    return stop("CAN_SUA_XUNG_HO", "Chua co bien tap truong doc lap chot xung ho: chay "
                                "`vgt xung-ho <du an> --duyet` (Opus, ~1-4 lan goi), roi `vgt run` lai. "
                                "Cau hoi khong spoil (neu co) o cau_hoi_xung_ho.md, khong chan. (G-023)")
                # 02/11: co chi dao canh thi bien kich truong chot xung ho cua TUNG canh (moi cap co thoai) tu toan bo
                # truyen -> cap thieu trong bang chung khong con la cho dich gia phai doan; khong chan nua.
                if iss and (self.cfg.get("chi_dao") or {}).get("bat", True):
                    self.log(f"Xung ho: {biblecheck.summary(iss)} -> de chi dao canh chot theo tung canh (khong chan).")
                elif iss:
                    return stop("CAN_SUA_XUNG_HO",
                                f"Bible thieu/mo ho xung ho ({biblecheck.summary(iss)}). Chay `vgt xung-ho <du an> "
                                "--de-xuat` (Opus chot tung cap, ton han muc), ra soat cac dong co note "
                                "'de xuat tu dong', roi `vgt run` lai. Chap nhan phan con lai: `vgt xung-ho <du an> "
                                "--chap-nhan`. (G-023)")
            if bc.get("block", True) and not self.store.get_meta("thuat_ngu_duyet"):
                return stop("CAN_DUYET_THUAT_NGU", "Chua co bien tap truong doc lap ra bang thuat ngu (tranh ghep "
                            "Han-Viet tung chu, tu Han-Viet hiem): `vgt thuat-ngu <du an>` (Opus, vai lan goi). (G-024)")
            # Cua chung (02/11): dong dich theo luong cu -> hoi dich lai theo luong hien tai (luong_dich trong config)
            ver = self.cfg.get("luong_dich", 2)
            if self.store.get_meta("luong_dich") != ver and not self.store.get_meta("giu_luong_cu"):
                n = self.store.db.execute("SELECT COUNT(*) FROM entries WHERE kind IN ('dialogue','choice') "
                                          "AND status IN ('done','tm','qa_fail')").fetchone()[0]
                if not n:
                    self.store.set_meta("luong_dich", ver)  # chua dich dong nao: dich thang bang luong moi
                else:
                    return stop("CAN_DICH_LAI_LUONG_MOI",
                                f"{n} dong thoai/lua chon da dich theo luong cu (truoc chi dao canh + dich gia Sonnet). "
                                "Hoi nguoi dung: dich lai het `vgt dich-lai <du an>` (co sao luu; ton han muc khi run), "
                                "hoac giu ban cu `vgt dich-lai <du an> --giu`. Roi `vgt run`.")
            trial = self.store.get_meta("trial_grps") or []
            if not trial:
                return stop("CAN_CHON_CANH_THU", "Chon 2-3 canh (hai, cam xuc, UI): `vgt trial <du an> "
                                                 f"--grp ...`. Goi y: {self._trial_suggestions()}")
            if not self.store.get_meta("trial_ok"):
                self._translate_review_loop(backend, trial)
                return stop("CAN_NGUOI_DUNG_DOC_THU", "Apply + kiem chung ban thu, gui nguoi dung doc "
                                                      "(vgt compare); dong y thi `vgt approve-trial`.")
            if (self.cfg.get("chi_dao") or {}).get("bat", True) and not self.store.get_meta("chi_dao_dong_y"):
                from . import mach
                have = biblemod.load_mach(self.path)
                todo = [g for (g,) in self.store.db.execute("SELECT DISTINCT grp FROM entries WHERE kind='dialogue'")
                        if g not in have]
                if todo:
                    cd = self.cfg.get("chi_dao") or {}
                    k = len(mach.groups(self, todo, cd.get("gop_dong", 60), cd.get("canh_nho", 20)))
                    gia = cd.get("usd_moi_lan_goi", 0.25)
                    return stop("CAN_DONG_Y_CHI_DAO",
                                f"Con {len(todo)} canh chua co chi dao: {k} lan goi Opus (~${k * gia:.0f} quy doi, "
                                "uoc tinh). Hoi nguoi dung; dong y: "
                                "`vgt chi-dao <du an> --dong-y` roi `vgt run`. Khong lam: dat chi_dao.bat: false.")
            self._translate_review_loop(backend)
            kept = self.kept_original()
            lim = max(int(self.cfg.get("content", {}).get("max_keep_lines", 5)),
                      int(self.cfg.get("content", {}).get("max_keep_ratio", 0.005) * len(self.store.entries())))
            if len(kept) > lim:
                return stop("CAN_KIEM_TRA_GIU_GOC",
                            f"{len(kept)} dong bi giu goc (> {lim}): bat thuong, co the model chan nham. "
                            f"Khong tu y giu goc them; xem `vgt review-export`, sua prompt/content_policy roi dich lai.")
            c = self.store.counts()
            left = c.get("new", 0) + c.get("qa_fail", 0)
            if left or self._sent_back():
                return stop("CON_LOI", f"Con {left} dong chua dat ({c}); xem `vgt review-export`.")
            self.store.set_meta("trang_thai", "cho_nguoi_dung")
            return stop("XONG_DICH", "Chay apply + kiem chung (docs/3_QUY_TRINH.md buoc 6-7).")
        except SystemExit:
            self.progress(dang_chay=False)
            raise
        except BaseException as e:
            self.progress(loi_gan_nhat=f"{type(e).__name__}: {str(e)[:300]}", dang_chay=False)
            raise

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
        hide = self.adapter.hides(self.game, self.cfg) if hasattr(self.adapter, "hides") else None
        patchmod.build(self.game, staging, files, probe, hide)
        patchmod.replace_dir(staging, patch_dir)
        self.log(f"Da tao patch {len(files)} file o {patch_dir} (game goc khong bi sua). "
                 f"Cai: CAI_VIETHOA.bat, go: GO_VIETHOA.bat.")
        return patch_dir
