"""Kiem thu: chay tiep an toan (phien ban ho so, may trang thai, tien do) va bai hoc theo game."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_pipeline import make_game, tmpdir  # noqa: E402
from vgt import bible as biblemod  # noqa: E402
from vgt import lessons as lessonsmod  # noqa: E402
from vgt import review as reviewmod  # noqa: E402
from vgt.backend import MockBackend  # noqa: E402
from vgt.pipeline import Project  # noqa: E402
from vgt.prompts import SYSTEM_TRANSLATE  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir(self)
        self.game = make_game(self.tmp)
        self.logs = []
        self.p = Project.init(self.game, self.tmp / "proj", log=self.logs.append)
        self.p.log = self.logs.append
        self.addCleanup(lambda: self.p.store.db.close())

    def reviewed(self):
        b = biblemod.load(self.p.path)
        b["reviewed"] = True
        biblemod.save(self.p.path, b)

    def finish_all(self, text="Xin chào"):
        for e in self.p.store.entries():
            e.target, e.status, e.qa = text, "done", []
            self.p.store.save_result(e)


class TestResume(Base):
    def test_run_stops_at_each_gate_then_finishes(self):
        p = self.p
        self.assertEqual(p.run("mock"), "CAN_RESEARCH")
        self.assertTrue(p.store.entries())  # da extract
        (p.path / "research.md").write_text("khong co nguon", "utf-8")
        self.assertEqual(p.run("mock"), "CAN_DUYET_BIBLE")
        self.assertTrue(biblemod.load(p.path).get("work"))
        self.reviewed()
        self.assertEqual(p.run("mock"), "CAN_SUA_XUNG_HO")  # G-023: chua co bien tap truong doc lap
        from vgt import xungho
        from vgt.backend import MockBackend
        xungho.review(p, MockBackend())
        self.assertEqual(p.run("mock"), "CAN_DUYET_THUAT_NGU")  # G-024
        from vgt import thuatngu
        thuatngu.review(p, MockBackend())
        self.assertEqual(p.run("mock"), "CAN_CHON_CANH_THU")
        p.set_trial(["Map001.json:ev1p0"])
        code = p.run("mock")
        self.assertEqual(code, "CAN_NGUOI_DUNG_DOC_THU")
        others = [e for e in p.store.entries() if e.grp != "Map001.json:ev1p0"]
        self.assertTrue(all(e.status == "new" for e in others))  # chua dich toan bo khi chua duyet
        prog = json.loads((p.path / "TIEN_DO.json").read_text("utf-8"))
        self.assertEqual(prog["buoc"], "CAN_NGUOI_DUNG_DOC_THU")
        p.approve_trial()
        code = p.run("mock")  # mock khong dich that -> con dong loi
        self.assertIn(code, ("CON_LOI", "XONG_DICH"))
        self.assertNotIn("new", p.store.counts())
        # Chay lai lan nua: an toan, khong goi lai bible
        n_bible = sum(u["calls"] for u in p.store.usage_summary() if u["purpose"] == "bible")
        p.run("mock")
        self.assertEqual(n_bible, sum(u["calls"] for u in p.store.usage_summary() if u["purpose"] == "bible"))

    def test_set_trial_rejects_unknown_scene(self):
        self.p.extract()
        with self.assertRaises(SystemExit):
            self.p.set_trial(["khong_co"])

    def test_bible_change_marks_lines_for_rereview(self):
        p = self.p
        p.extract()
        p.draft_bible("mock")
        self.reviewed()
        p.translate("mock")
        v1 = p.bible_version()
        self.assertTrue(v1)
        self.assertTrue(all(e.bible_ver == v1 for e in p.store.entries() if e.attempts))
        self.finish_all()
        for e in p.store.entries():
            e.bible_ver = v1
            p.store.save_result(e)
        p.review("mock")
        self.assertEqual(p.old_bible_lines(), 0)
        sm = reviewmod.summary(p.store, p.bible_version())
        self.assertEqual(sm["dong_da_cham"], sm["tong_dong"])
        # Sua ho so (vd doi xung ho) -> phien ban doi -> dong cu can cham lai
        b = biblemod.load(p.path)
        b["style"]["tone"] = "nghiem tuc hon"
        biblemod.save(p.path, b)
        self.assertNotEqual(p.bible_version(), v1)
        self.assertEqual(p.old_bible_lines(), len(p.store.entries()))
        self.assertEqual(reviewmod.summary(p.store, p.bible_version())["dong_da_cham"], 0)
        st = p.review("mock")
        self.assertGreater(st.get("goi", 0), 0)
        # chi doi co reviewed khong lam doi phien ban
        b["reviewed"] = False
        biblemod.save(p.path, b)
        v2 = p.bible_version()
        b["reviewed"] = True
        biblemod.save(p.path, b)
        self.assertEqual(v2, p.bible_version())

    def test_limit_wait_written_to_progress(self):
        self.p._backend_log("[han muc] het han muc -> cho 30 phut")
        prog = json.loads((self.p.path / "TIEN_DO.json").read_text("utf-8"))
        self.assertIn("han muc", prog["cho_han_muc"])

    def test_old_db_gets_bible_ver_column(self):
        import sqlite3
        db = self.tmp / "old.db"
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE entries (id TEXT PRIMARY KEY, file TEXT NOT NULL, locator TEXT NOT NULL,"
                    " grp TEXT NOT NULL, seq INTEGER NOT NULL, kind TEXT NOT NULL, speaker TEXT, face TEXT,"
                    " source TEXT NOT NULL, target TEXT, status TEXT NOT NULL DEFAULT 'new', model TEXT,"
                    " attempts INTEGER NOT NULL DEFAULT 0, qa TEXT, tags TEXT)")
        con.execute("INSERT INTO entries (id,file,locator,grp,seq,kind,source) VALUES ('a','f','{}','g',0,'ui','x')")
        con.commit()
        con.close()
        from vgt.store import Store
        s = Store(db)
        self.assertIsNone(s.entries()[0].bible_ver)
        s.db.close()


class TestLessons(Base):
    def test_only_matching_lessons_and_rules_reach_prompt(self):
        p = self.p
        p.extract()  # nguon ja, RPG Maker MV, co nguoi noi
        m = lessonsmod.match(p)
        codes = {l["_code"] for l in m["ap_dung"] + m["chan_bang_code"]}
        self.assertIn("G-003", codes)       # nguon CJK
        self.assertIn("G-018", codes)       # co nguoi noi
        self.assertNotIn("E-unreal-001", codes)  # engine khac: khong doc
        self.assertNotIn("E-rpgmaker_mvmz-003", codes)  # bo do: khong co '\' lac
        self.assertFalse(m["loi_bo_do"])
        sysp = p.system_prompt(SYSTEM_TRANSLATE)
        self.assertIn("BÀI HỌC TỪ CÁC GAME TRƯỚC", sysp)
        self.assertIn("MỘT đại từ tự xưng", sysp)
        # Bai hoc den kiem dinh vien
        p.draft_bible("mock")
        self.reviewed()
        self.finish_all()
        seen = []

        class Rec(MockBackend):
            def call(s, system, prompt, schema, model, effort=None, timeout=None):
                seen.append(system)
                return MockBackend.call(s, system, prompt, schema, model, effort, timeout)
        p.backend = lambda kind: Rec()
        p.review("mock")
        self.assertTrue(seen and all("MỘT đại từ tự xưng" in x for x in seen))

    def test_detector_matches_real_data(self):
        p = self.p
        p.extract()
        self.assertFalse(lessonsmod.DETECTORS["mv_backslash_lac"](p, lessonsmod.facts(p)))
        p.store.db.execute("UPDATE entries SET source='\\\\安維爾' WHERE kind='ui'")
        p.store.db.commit()
        self.assertTrue(lessonsmod.DETECTORS["mv_backslash_lac"](p, lessonsmod.facts(p)))

    def test_report_runs(self):
        self.p.extract()
        txt = lessonsmod.report(self.p)
        self.assertIn("Khong khop game nay", txt)


class TestCodeMerge(Base):
    def test_lists_merged_by_code_only_conflicts_to_opus(self):
        from vgt import dossier
        parts = [{"glossary": [{"src": "勇者", "vi": "Dũng giả"}, {"src": "魔王", "vi": "Ma Vương"}],
                  "handbook": [{"src": "爆裂魔法", "meaning": "x", "vi": "Bộc Liệt Ma Pháp"}]},
                 {"glossary": [{"src": "勇者", "vi": "dũng giả"}, {"src": "魔王", "vi": "Quỷ Vương"}],
                  "handbook": [{"src": "爆裂魔法", "meaning": "x", "vi": "Phép Nổ"}]}]
        agreed, conflicts, hb = dossier.merge_lists(parts)
        self.assertEqual([g["src"] for g in agreed], ["勇者"])
        self.assertEqual(conflicts[0]["src"], "魔王")
        self.assertEqual(conflicts[0]["options"], ["Ma Vương", "Quỷ Vương"])
        self.assertEqual(len(hb), 1)
        self.assertEqual(hb[0]["alt"], ["Phép Nổ"])

    def test_merge_payload_and_unresolved_conflict(self):
        from vgt import dossier
        p = self.p
        p.extract()
        sent = []

        class Rec(MockBackend):
            def call(s, system, prompt, schema, model, effort=None, timeout=None):
                pl = json.loads(prompt.split("\n", 1)[1])
                r = MockBackend.call(s, system, prompt, schema, model, effort, timeout)
                if "scenes" in schema["properties"]:
                    r["data"]["glossary"] = [{"src": "魔王", "vi": "Ma Vương" if "1/" in pl["part"] else "Quỷ Vương"}]
                else:
                    sent.append(pl)
                return r
        p.cfg["dossier"]["chunk_chars"] = 60
        p.backend = lambda kind: Rec()
        p.draft_bible("mock")
        self.assertTrue(sent and all("glossary" not in n for pl in sent for n in pl["notes"]))
        self.assertEqual(sent[-1]["glossary_conflicts"][0]["src"], "魔王")
        b = biblemod.load(p.path)
        g = [x for x in b["glossary"] if x["src"] == "魔王"][0]
        self.assertEqual(g["vi"], "Ma Vương")  # Opus khong quyet -> lay phuong an dau
        self.assertTrue(any("魔王" in x for x in b["can_xac_nhan"]))


class TestManyGames(Base):
    def test_busy_blocks_second_run_same_project(self):
        p = self.p
        p.progress(dang_chay=True, buoc="translate")
        with self.assertRaises(SystemExit):
            p.run("mock")
        # TIEN_DO cu (phien truoc da chet) -> chay duoc
        d = json.loads((p.path / "TIEN_DO.json").read_text("utf-8"))
        d["cap_nhat"] = "2020-01-01 00:00:00"
        (p.path / "TIEN_DO.json").write_text(json.dumps(d), "utf-8")
        self.assertIsNone(p.busy())
        self.assertEqual(p.run("mock"), "CAN_RESEARCH")
        self.assertFalse(json.loads((p.path / "TIEN_DO.json").read_text("utf-8"))["dang_chay"])

    def test_list_projects_with_next_step(self):
        p = self.p
        (p.path / "CHECKPOINT.md").write_text("# X\n\n## Việc tiếp theo\nDich toan bo.\n", "utf-8")
        p.progress(buoc="translate")
        ps = Project.list_projects(p.path.parent)
        x = [q for q in ps if q["ten"] == p.path.name][0]
        self.assertEqual(x["buoc"], "translate")
        self.assertEqual(x["viec_tiep"], "Dich toan bo.")
        # Da xong / luu tru: khong hien trong danh sach lam tiep, van thay khi --all
        p.mark("xong", "Game Thu (ban 1)")
        self.assertFalse([q for q in Project.list_projects(p.path.parent) if q["ten"] == p.path.name])
        x = [q for q in Project.list_projects(p.path.parent, True) if q["ten"] == p.path.name][0]
        self.assertEqual((x["trang_thai"], x["ten_hien_thi"]), ("xong", "Game Thu (ban 1)"))
        with self.assertRaises(SystemExit):
            p.mark("linh_tinh")


if __name__ == "__main__":
    unittest.main()
