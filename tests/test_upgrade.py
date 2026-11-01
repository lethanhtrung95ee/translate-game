"""Kiem thu nang cap theo docs/DAC_TA_HE_THONG.md: ho so tac pham doc toan bo kich ban,
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


class Recorder(MockBackend):
    """Backend gia ghi lai payload; dich gia tra them ghi chu chien luoc 'n'."""

    def __init__(self):
        super().__init__()
        self.payloads = []

    def call(self, system, prompt, schema, model, effort=None, timeout=None):
        self.payloads.append((model, json.loads(prompt.split("\n", 1)[1])))
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
        self.assertTrue(all(pl["work"]["premise"] == "mock premise" for pl in dlg))
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
