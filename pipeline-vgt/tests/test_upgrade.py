"""Kiem thu nang cap theo docs/2_DAC_TA.md: ho so tac pham doc toan bo kich ban,
dich theo canh, kiem dinh vien, du an thu + so sanh. Chay bang backend gia (khong ton han muc)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_pipeline import make_game, tmpdir  # noqa: E402
from vgt import bible as biblemod  # noqa: E402
from vgt import dossier  # noqa: E402
from vgt.backend import MockBackend  # noqa: E402
from vgt.pipeline import Project  # noqa: E402


class VietRecorder(MockBackend):
    """Dich gia gia tra ban 'tieng Viet' sach (giu token) de dong qua QA; bien tap them ' (bt)'."""

    def __init__(self):
        super().__init__()
        self.payloads = []

    def call(self, system, prompt, schema, model, effort=None, timeout=None):
        import re
        pl = json.loads(prompt.split("\n", 1)[1])
        self.payloads.append((model, pl))
        if "issues" in schema.get("properties", {}) or "lines" not in pl:
            return super().call(system, prompt, schema, model, effort, timeout)
        out = []
        for x in pl["lines"]:
            if "s" in x:
                toks = re.findall(r"⟦\d+⟧", x["s"])
                out.append({"id": x["id"], "v": "Xin chào " + " ".join(toks)})
            else:
                out.append({"id": x["id"], "v": x["v"] + " (bt)"})
        return {"data": {"t": out}, "usage": {}, "cost": 0.0}


class Recorder(MockBackend):
    """Backend gia ghi lai payload; dich gia tra them ghi chu chien luoc 'n'."""

    def __init__(self):
        super().__init__()
        self.payloads = []
        self.systems = []

    def call(self, system, prompt, schema, model, effort=None, timeout=None):
        self.payloads.append((model, json.loads(prompt.split("\n", 1)[1])))
        self.systems.append(system)
        r = super().call(system, prompt, schema, model, effort, timeout)
        if "t" in r["data"]:
            for x in r["data"]["t"]:
                x["n"] = "choi chu: giu tac dung"
        return r


class E:
    def __init__(self, g, n=1):
        self.grp, self.source = g, "x" * n


class TestPack(unittest.TestCase):
    def test_pack_small_scenes_together_split_big_keep_order(self):
        from vgt.batching import pack
        groups = [[E("a"), E("a")], [E("b")], [E("c")] * 5, [E("d")]]
        out = list(pack(groups, 4, 1000))
        flat = [e.grp for b in out for e in b]
        self.assertEqual(flat, ["a", "a", "b"] + ["c"] * 5 + ["d"])  # khong mat, dung thu tu
        self.assertEqual([e.grp for e in out[0]], ["a", "a", "b"])  # canh nho gom chung
        self.assertTrue(all(len(b) <= 4 for b in out))
        # Gioi han ky tu
        out = list(pack([[E("a", 600)], [E("b", 600)]], 40, 1000))
        self.assertEqual(len(out), 2)


class TestUpgrade(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir(self)
        self.game = make_game(self.tmp)
        self.logs = []
        self.p = Project.init(self.game, self.tmp / "proj", log=self.logs.append)
        self.p.log = self.logs.append
        self.addCleanup(lambda: self.p.store.db.close())
        self.p.extract()
        self.p.cfg["dossier"]["scene_min_lines"] = 1

    def _reviewed(self):
        b = biblemod.load(self.p.path)
        b["reviewed"] = True
        biblemod.save(self.p.path, b)

    def _reads(self):
        return sum(u["calls"] for u in self.p.store.usage_summary() if u["purpose"] == "bible_read")

    def test_full_read_all_parts_scenes_and_resume(self):
        p = self.p
        p.cfg["dossier"]["chunk_chars"] = 60  # ep chia nhieu phan
        n = len(dossier.make_chunks(dossier.script_entries(p.store), 60))
        self.assertGreater(n, 1)
        # Moi dong kich ban nam trong dung 1 phan, khong mat dong nao.
        ids = [e.id for ch in dossier.make_chunks(dossier.script_entries(p.store), 60) for e in ch]
        self.assertEqual(sorted(ids), sorted(e.id for e in dossier.script_entries(p.store)))
        p.draft_bible("mock")
        self.assertEqual(len(list((p.path / "bible_parts").glob("part_*.json"))), n)
        self.assertEqual(self._reads(), n)
        b = biblemod.load(p.path)
        self.assertFalse(b["reviewed"])
        self.assertEqual(b["work"]["premise"], "mock premise")
        scenes = biblemod.load_scenes(p.path)
        self.assertIn("Map001.json:ev1p0", scenes)
        # Chay lai: phan da doc khong goi lai (bi ngat giua chung van tiep tuc duoc).
        p.draft_bible("mock")
        self.assertEqual(self._reads(), n)
        # Ban da duyet duoc giu lai khi soan lai.
        self._reviewed()
        p.draft_bible("mock")
        self.assertTrue((p.path / "bible.prev.yaml").exists())

    def test_research_file_reaches_reader(self):
        p = self.p
        (p.path / "research.md").write_text("Dua tren Tay Du Ky: dung ten Han-Viet.", "utf-8")
        rec = Recorder()
        p.backend = lambda kind: rec
        p.draft_bible("mock")
        reads = [pl for m, pl in rec.payloads if "script" in pl]
        self.assertTrue(reads and all("Tay Du Ky" in pl["research"] for pl in reads))

    def test_polish_pass(self):
        """Bien tap doc tron: chi gui ban Viet (khong cau goc), ban sua qua QA moi duoc ghi."""
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        p.cfg["polish"] = {"enabled": True, "roles": ["dialogue", "key_scene"]}
        rec = VietRecorder()
        p.backend = lambda kind: rec
        p.translate("mock")
        pol = [pl for m, pl in rec.payloads if pl.get("lines") and "v" in pl["lines"][0]]
        self.assertTrue(pol, "phai co luot bien tap")
        self.assertTrue(all("s" not in x for pl in pol for x in pl["lines"]), "bien tap khong nhin cau goc")
        dlg = [e for e in p.store.entries() if e.kind == "dialogue" and e.status == "done"]
        self.assertTrue(dlg and all(e.target.endswith("(bt)") and e.model.endswith("+bt") for e in dlg))
        ui = [e for e in p.store.entries() if e.kind == "ui" and e.target]
        self.assertTrue(all(not e.target.endswith("(bt)") for e in ui), "ui khong qua bien tap")
        self.assertIn("polish", {r[0] for r in p.store.db.execute("SELECT purpose FROM runs")})

    def test_review_strict_machine(self):
        from vgt import review
        from vgt.prompts import REVIEW_STRICT_MACHINE
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        p.backend = lambda kind: VietRecorder()
        p.translate("mock")
        rec = Recorder()
        p.backend = lambda kind: rec
        p.cfg["review"]["giong_may"] = "major"
        p.cfg["review"]["che_do"] = "day_du"  # cach cu; mac dinh 02/11 la 'nghia'
        review.run(p, rec)
        self.assertTrue(rec.systems and all(REVIEW_STRICT_MACHINE in s for s in rec.systems))

    def test_term_rename_keeps_review(self):
        """Doi 1 thuat ngu: thay o ban dich + bible, khong bat cham lai ca game, chay lai khong doi 2 lan."""
        from vgt import review, term
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        b = biblemod.load(p.path)
        b["glossary"] = [{"src": "ボブ", "vi": "Bốp"}]
        biblemod.save(p.path, b)
        for e in p.store.entries():
            e.target, e.status = ("Chào Bốp" if "ボブ" in e.source else "Xin chào"), "done"
            p.store.save_result(e)
        p.store.db.commit()
        es = [e for e in p.store.entries() if "ボブ" in e.source]
        self.assertTrue(es)
        review.run(p, MockBackend())
        before = review.pending_groups(p.store, None, p.bible_version())
        r = term.rename(p, "ボブ", "Bốp", "Bốp Bự")
        self.assertEqual(r["dong_doi"], len(es))
        self.assertTrue(all(e.target == "Chào Bốp Bự" for e in p.store.entries() if e.id in {x.id for x in es}))
        self.assertEqual(biblemod.load(p.path)["glossary"][0]["vi"], "Bốp Bự")
        after = review.pending_groups(p.store, None, p.bible_version())
        self.assertEqual(len(after[0]), len(before[0]), "khong duoc bat cham lai vi doi thuat ngu")
        self.assertEqual(term.rename(p, "ボブ", "Bốp", "Bốp Bự", dry=True)["dong_doi"], 0)

    def test_prompt_version_3(self):
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        p.cfg["prompt_version"] = 3
        rec = Recorder()
        p.backend = lambda kind: rec
        p.translate("mock")
        self.assertTrue(rec.systems and all("GẬP câu gốc" in s for s in rec.systems))

    def test_xung_ho_gate_and_propose(self):
        """G-023: cap noi qua lai thieu xung ho -> vgt run dung CAN_SUA_XUNG_HO; de xuat (mock) lap day."""
        from vgt import xungho
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        p.cfg["bible_check"] = {"block": True, "min_exchanges": 1, "min_lines": 99}
        b = biblemod.load(p.path)
        b["relations"] = []
        biblemod.save(p.path, b)
        iss = xungho.issues(p)
        if not iss:
            self.skipTest("game mau khong co 2 nguoi noi qua lai")
        (p.path / "research.md").write_text("khong co nguon", encoding="utf-8")
        self.assertEqual(p.run("mock"), "CAN_SUA_XUNG_HO")
        r = xungho.propose(p, MockBackend(), iss)
        p.store.set_meta("xung_ho_duyet", "test")
        self.assertGreater(r["them"], 0)
        self.assertEqual(r["con_lai"], 0)
        self.assertNotEqual(p.run("mock"), "CAN_SUA_XUNG_HO")

    def test_eval_case_roundtrip(self):
        """Bo de chung: chup 1 canh thanh case, chay lai bang backend gia, phep kiem hoat dong."""
        from vgt import evalset
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        grp = next(e.grp for e in p.store.entries() if e.kind == "dialogue")
        old = evalset.EVAL
        evalset.EVAL = self.tmp / "eval"
        try:
            evalset.add_case(p, grp, "t1", "giong_may", "thu", [{"line": 0, "cam": ["Cái này"], "phai": ["Xin chào"]}])
            rep = evalset.run(VietRecorder(), {}, None, "t", log=lambda *a: None)
            self.assertEqual(len(rep["case"]), 1)
            self.assertTrue(rep["case"][0]["dat"], rep["case"][0]["kiem"])
            rep2 = evalset.run(MockBackend(), {}, None, "t2", log=lambda *a: None)
            self.assertFalse(rep2["case"][0]["dat"])  # mock tra 'VI: <goc>' -> thieu 'Xin chao'
            self.assertIn("so voi", evalset.compare(rep2))
        finally:
            evalset.EVAL = old

    def test_trial_requires_adult_scene(self):
        """Game 18+: ban thu bat buoc co 1 canh nguoi lon (1_QUYET_DINH muc 4)."""
        p = self.p
        grps = sorted({e.grp for e in p.store.entries()})
        p.adult_scenes = lambda: {grps[-1]: 30}
        with self.assertRaises(SystemExit):
            p.set_trial([grps[0]])
        p.set_trial([grps[0], grps[-1]])
        p.set_trial([grps[0]], force=True)
        p.adult_scenes = lambda: {}
        p.set_trial([grps[0]])

    def test_adult_block_in_system(self):
        """Game nguoi lon: thang tu ngu 18+ chung vao system prompt dich gia + kiem dinh vien (G-022)."""
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        p._adult = True
        rec = Recorder()
        p.backend = lambda kind: rec
        p.translate("mock")
        self.assertTrue(rec.systems and all("THANG TỪ NGỮ 18+" in s and "NỘI DUNG NGƯỜI LỚN" in s for s in rec.systems))
        p._adult = False
        rec2 = Recorder()
        p.backend = lambda kind: rec2
        p.translate("mock", force=True)
        self.assertTrue(all("THANG TỪ NGỮ 18+" not in s for s in rec2.systems))

    def test_review_applies_minor_fix(self):
        """Loi nhe tu_nhien: ap cau sua cua kiem dinh vien (giu ma, qua QA); loi dung_y: khong ap."""
        from vgt import fixapply, review
        self.assertIsNone(fixapply.candidate("\\C[2]Chào\\C[0] bạn", "Chào bạn"))  # mat ma
        self.assertEqual(fixapply.candidate("Chào  bạn nhé", "Chào bạn nha"), "Chào bạn nha")
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        p.backend = lambda kind: VietRecorder()
        p.translate("mock")

        class Rv(MockBackend):
            def call(self, system, prompt, schema, model, effort=None, timeout=None):
                pl = json.loads(prompt.split("\n", 1)[1])
                iss = []
                for x in pl.get("lines", []):
                    if x["id"] == "0":
                        iss.append({"id": "0", "severity": "minor", "criterion": "tu_nhien", "problem": "gượng",
                                    "fix": x["v"].replace("Xin chào", "Chào nhé")})
                    if x["id"] == "1":
                        iss.append({"id": "1", "severity": "minor", "criterion": "dung_y", "problem": "x",
                                    "fix": x["v"].replace("Xin chào", "Khác ý")})
                return {"data": {"scores": {}, "issues": iss}, "usage": {}, "cost": 0.0}
        p.cfg["review"]["ap_sua_nhe"] = ["tu_nhien", "giong", "hon"]
        out = review.run(p, Rv())
        self.assertGreater(out.get("ap_sua_nhe", 0), 0)
        ts = [e.target for e in p.store.entries() if e.target]
        self.assertTrue(any("Chào nhé" in t for t in ts))
        self.assertFalse(any("Khác ý" in t for t in ts))

    def test_xh_in_payload(self):
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        b = biblemod.load(p.path)
        ids = [c["id"] for c in b["characters"]]
        if len(ids) < 2:
            self.skipTest("can 2 nhan vat")
        b["relations"] = [{"from": a, "to": c, "self": "tớ", "call": "cậu"} for a in ids for c in ids if a != c]
        biblemod.save(p.path, b)
        rec = Recorder()
        p.backend = lambda kind: rec
        p.translate("mock")
        rows = [x for m, pl in rec.payloads for x in pl.get("lines", []) if x.get("k") == "dialogue"]
        self.assertTrue(any("xưng 'tớ'" in (x.get("xh") or "") for x in rows))

    def test_scene_batches_and_scene_context(self):
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        rec = Recorder()
        p.backend = lambda kind: rec
        p.translate("mock")
        tr = [pl for m, pl in rec.payloads if "lines" in pl]
        dlg = [pl for pl in tr if pl.get("scene")]
        self.assertTrue(dlg, "lo loi thoai phai kem tom tat canh")
        # style + premise nam trong system prompt (cache), khong lap lai trong tung lo
        self.assertTrue(all("work" not in pl and "style" not in pl for pl in tr))
        self.assertTrue(all('"premise":"mock premise"' in s for s in rec.systems))
        # Lo loi thoai khong chua ui/ten/mo ta (chi dialogue/choice cua canh).
        for model, batch in p._batches(p.store.entries(),
                                       biblemod.BibleIndex(biblemod.load(p.path))):
            kinds = {e.kind for e in batch}
            self.assertTrue(kinds <= {"dialogue", "choice"} or not kinds & {"dialogue", "choice"})
        # Ghi chu chien luoc cua dich gia duoc luu cho kiem dinh vien.
        self.assertTrue(any(x.startswith("N:") for e in p.store.entries() for x in e.qa))

    def test_translate_only_selected_scene(self):
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        p.translate("mock", grps=["Map001.json:ev1p0"])
        other = [e for e in p.store.entries() if e.grp != "Map001.json:ev1p0"]
        self.assertTrue(other and all(e.status == "new" for e in other))

    def _finish(self, bad_id=None):
        for e in self.p.store.entries():
            e.target = "BAD dịch sai" if e.id == bad_id else "Xin chào"
            e.status, e.qa, e.attempts = "done", [], 1
            self.p.store.save_result(e)

    def test_review_major_sends_back_then_pass(self):
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        bad = "Map001.json:ev1p0@3"
        self._finish(bad)
        st = p.review("mock")
        self.assertEqual(st.get("truot"), 1)
        e = p.store.entries("id=?", (bad,))[0]
        self.assertEqual(e.status, "qa_fail")
        self.assertTrue(any(x.startswith("E: [kiểm định]") for x in e.qa))
        self.assertEqual(e.attempts, 2)  # dich lai bang vai tro repair
        self.assertEqual(p.route(e, biblemod.BibleIndex(biblemod.load(p.path))), "repair")
        # Dong khac khong bi dong vao.
        ok = p.store.entries("id=?", ("Map001.json:ev1p0@0",))[0]
        self.assertEqual(ok.status, "done")
        # Dich gia nhan dung loi kiem dinh vien neu (fix) + ban cu (prev) + tom tat canh.
        rec = Recorder()
        p.backend = lambda kind: rec
        p.translate("mock")
        row = [r for m, pl in rec.payloads for r in pl.get("lines", []) if "fix" in r]
        self.assertTrue(row and "sai nghia" in row[0]["fix"] and row[0]["prev"].startswith("BAD"))
        self.assertTrue(any(pl.get("scene") for m, pl in rec.payloads if "lines" in pl))
        e = p.store.entries("id=?", (bad,))[0]
        # Sua xong -> cham lai dat; cham lan nua khong ton goi (hash khong doi).
        e.target, e.status = "Xin chào bạn", "done"
        p.store.save_result(e)
        st = p.review("mock")
        self.assertEqual(st.get("truot", 0), 0)
        self.assertEqual(st.get("goi"), 1)
        st = p.review("mock")
        self.assertEqual(st.get("goi", 0), 0)
        from vgt import review as reviewmod
        sm = reviewmod.summary(p.store, p.bible_version())
        self.assertEqual(sm["dong_da_cham"], sm["tong_dong"])
        self.assertEqual(sm["tra_ve_dich_lai"], 0)

    def test_review_gives_up_after_max_rounds(self):
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        bad = "Map001.json:ev1p0@3"
        p.cfg["review"]["max_rounds"] = 1
        self._finish(bad)
        p.review("mock")
        e = p.store.entries("id=?", (bad,))[0]
        e.target, e.status = "BAD van sai", "done"
        p.store.save_result(e)
        st = p.review("mock")
        self.assertEqual(st.get("can_nguoi"), 1)
        e = p.store.entries("id=?", (bad,))[0]
        self.assertTrue(any("cần người duyệt" in x for x in e.qa))

    def test_review_skips_unfinished_scene(self):
        p = self.p
        p.draft_bible("mock")
        self._reviewed()
        st = p.review("mock")
        self.assertEqual(st.get("goi", 0), 0)

    def test_fork_and_compare(self):
        p = self.p
        self._finish()
        (p.path / "research.md").write_text("boi canh", "utf-8")
        (p.path / "config.yaml").write_text('patch:\n  dir: "../That"\nqa:\n  max_line_chars: 40\n', "utf-8")
        q = Project.fork(p.path, self.tmp / "thu", log=self.logs.append)
        self.addCleanup(lambda: q.store.db.close())
        self.assertEqual(set(q.store.counts()), {"new"})
        self.assertEqual(len(q.store.entries()), len(p.store.entries()))
        self.assertIsNone(q.store.tm_lookup(q.store.entries()[0]))
        self.assertNotEqual(q.patch_dir.name, "That")  # khong de len ban Viet hoa that
        self.assertEqual(q.cfg["qa"]["max_line_chars"], 40)
        self.assertTrue((q.path / "research.md").exists())
        for e in q.store.entries("grp=?", ("Map001.json:ev1p0",)):
            e.target, e.status = "Bản mới", "done"
            q.store.save_result(e)
        out = Project.compare(p.path, q.path, grps=["Map001.json:ev1p0"])
        html = out.read_text("utf-8")
        self.assertIn("Bản mới", html)
        self.assertIn("Xin chào", html)
        self.assertIn("こんにちは", html)

    def test_estimate_lists_new_steps(self):
        txt = self.p.estimate()
        self.assertIn("bible_read", txt)
        self.assertIn("review", txt)


if __name__ == "__main__":
    unittest.main()


class TestRealRunFixes(unittest.TestCase):
    """Loi gap khi chay that cursed_armor_v2 (31/10/2026)."""

    def test_compound_glossary_not_used_for_qa(self):
        g = [{"src": "初級/中級/高級/特殊任務管理員", "vi": "Quản lý nhiệm vụ sơ cấp/trung cấp/cao cấp/đặc biệt"},
             {"src": "初級/中級冒險者 / 資深冒險者憑證 / 公會經驗值",
              "vi": "mạo hiểm giả sơ cấp/trung cấp / chứng chỉ Mạo hiểm giả Kỳ cựu / điểm kinh nghiệm hội"},
             {"src": "銅/鐵/鋼/合金 + 頭盔/盔甲/盾/護手/靴", "vi": "Mũ giáp / Giáp / Khiên / Hộ thủ / Ủng"},
             {"src": "煉之修女", "vi": "Nữ tu Luyện"}]
        self.assertEqual(biblemod.glossary_hits(g, "初級任務管理員：這個鐵則", strict=True), [])
        hit = biblemod.glossary_hits(g, "她已經成為煉之修女了", strict=True)
        self.assertEqual([(s, v) for _, s, v in hit], [("煉之修女", ["Nữ tu Luyện"])])
        self.assertTrue(biblemod.glossary_hits(g, "初級任務管理員"))  # van gui lam ngu canh

    def test_punct_rule_in_review_and_bible_prompts(self):
        from vgt import prompts
        for p in (prompts.SYSTEM_REVIEW, prompts.SYSTEM_BIBLE):
            self.assertIn("～ → ~", p)



class TestRecheckStuck(unittest.TestCase):
    def test_stuck_qa_fail_rechecked_without_calls(self):
        """Dong ket qa_fail vi luat QA sai (attempts = max) phai tu thoat khi QA hien tai dat."""
        tmp = tmpdir(self)
        p = Project.init(make_game(tmp), tmp / "proj", log=lambda *a: None)
        p.log = lambda *a: None
        self.addCleanup(lambda: p.store.db.close())
        p.extract()
        p.draft_bible("mock")
        b = biblemod.load(p.path)
        b["reviewed"] = True
        biblemod.save(p.path, b)
        ds = p.store.entries("kind='dialogue'")
        plain = [x for x in ds if x.source == "ポーションを持ってる？"] + [x for x in ds if "【" in x.source]
        mx = p.cfg["max_attempts"]
        for x, err in zip(plain, ["E: thuật ngữ '初級' phải dịch là 'mạo hiểm giả sơ cấp'",
                                  "E: [kiểm định] giong: sai giọng"]):
            x.target, x.status, x.attempts, x.qa = "Bạn có thuốc không?", "qa_fail", mx, [err]
            p.store.save_result(x)
        p.translate("mock", grps=[plain[0].grp, plain[1].grp])
        self.assertEqual(p.store.entries("id=?", (plain[0].id,))[0].status, "done")
        self.assertEqual(p.store.entries("id=?", (plain[1].id,))[0].status, "qa_fail")
        self.assertEqual(p.store.entries("id=?", (plain[0].id,))[0].target, "Bạn có thuốc không?")  # khong dich lai
