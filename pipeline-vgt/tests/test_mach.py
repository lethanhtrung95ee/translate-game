"""Boi canh kich tung canh (02/11): goc loi 'dich dung nghia nhung khong truyen cam xuc'."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_resume_lessons import Base  # noqa: E402
from vgt import bible as biblemod  # noqa: E402
from vgt import mach  # noqa: E402
from vgt.backend import MockBackend  # noqa: E402
from vgt.prompts import MACH_DICH, MACH_REVIEW, SYSTEM_REVIEW, SYSTEM_TRANSLATE  # noqa: E402


class SpyBackend(MockBackend):
    def call(self, system, prompt, schema, model, effort=None, timeout=None):
        self.calls.append((system, prompt))
        return super().call(system, prompt, schema, model, effort, timeout)


class TestMach(Base):
    def grp(self):
        return next(e.grp for e in self.p.store.entries() if e.kind == "dialogue")

    def test_khong_co_mach_thi_khong_doi_gi(self):
        """Chua chay `vgt mach`: prompt + boi canh y nguyen nhu cu (khong lam lech cac lan do truoc)."""
        self.p.run("mock")
        self.assertEqual(biblemod.load_scene_ctx(self.p.path), biblemod.load_scenes(self.p.path))
        self.assertNotIn(MACH_DICH, self.p.system_prompt(SYSTEM_TRANSLATE))

    def test_mach_vao_payload_dich_va_luat(self):
        p = self.p
        p.run("mock")
        (p.path / "research.md").write_text("x", "utf-8")
        p.run("mock")  # bible
        g = self.grp()
        be = SpyBackend()
        out = mach.build(p, be, [g])
        self.assertEqual(out["viet"], 1)
        sysm, q = next((s, q) for s, q in be.calls if isinstance(q, str))
        pl = json.loads(q.split("\n", 1)[1])
        self.assertTrue(pl["canh"][0]["lines"])
        self.assertIn("HỒ SƠ TÁC PHẨM", sysm)  # ho so toan truyen trong system (cache), khong chi premise
        ctx = biblemod.load_scene_ctx(p.path)
        self.assertEqual(ctx[g]["mach"]["mach_toi_day"], "mock mach")
        self.assertNotIn("mach", biblemod.load_scenes(p.path).get(g) or {})  # scenes.yaml khong bi ghi de
        self.assertTrue(p.system_prompt(SYSTEM_TRANSLATE).startswith(MACH_DICH))  # chi dao dat len dau
        self.assertIn(MACH_REVIEW, p.system_prompt(SYSTEM_REVIEW))
        self.assertNotIn(MACH_DICH, p.system_prompt(SYSTEM_REVIEW))
        # chay lai: bo qua canh da co
        self.assertEqual(mach.build(p, SpyBackend(), [g])["viet"], 0)
        # dich that (backend gia): payload lo dich co scene.mach, system co luat
        self.reviewed()
        spy = SpyBackend()
        p.backend = lambda kind: spy
        p.translate("mock", force=True, grps=[g])
        tr = [(s, json.loads(q.split("\n", 1)[1])) for s, q in spy.calls if isinstance(q, str) and q.startswith("#JSON")]
        hit = [pl for s, pl in tr if "mach" in json.dumps(pl.get("scene") or pl.get("scenes") or {}, ensure_ascii=False)]
        self.assertTrue(hit)
        self.assertTrue(all(MACH_DICH in s for s, _ in tr))


class TestLuong0211(Base):
    def test_review_mac_dinh_chi_bat_nghia(self):
        from vgt.prompts import SYSTEM_REVIEW_NGHIA, review_system
        self.assertIs(review_system(self.p.cfg), SYSTEM_REVIEW_NGHIA)
        self.assertEqual(self.p.cfg["review"]["ap_sua_nhe"], [])

    def test_chi_dao_xung_ho_thang_goi_y_cap(self):
        """Canh co chi dao xung ho -> lo dich khong con 'xh' theo cap ca game (hai nguon danh nhau)."""
        import yaml
        p = self.p
        p.run("mock")
        (p.path / "research.md").write_text("x", "utf-8")
        p.run("mock")
        g = next(e.grp for e in p.store.entries() if e.kind == "dialogue")
        (p.path / "mach_canh.yaml").write_text(yaml.safe_dump({g: {"mach_toi_day": "x", "xung_ho": [
            {"noi": "a", "nghe": "b", "xung": "anh", "goi": "em", "tu_cau": ""}]}}, allow_unicode=True), "utf-8")
        self.reviewed()
        spy = SpyBackend()
        p.backend = lambda kind: spy
        p._address_hints = lambda batch, bidx: {e.id: "xưng tôi, gọi bạn" for e in batch}
        p.translate("mock", force=True, grps=[g])
        tr = [json.loads(q.split("\n", 1)[1]) for s, q in spy.calls if isinstance(q, str) and q.startswith("#JSON")]
        self.assertTrue(tr)
        self.assertFalse(any("xh" in x for pl in tr for x in pl.get("lines", [])))


class TestReportFiles(unittest.TestCase):
    def test_bo_file_khong_phai_ket_qua(self):
        """Loi 02/11: compare lay nham doc_thu_sach.json (list) lam lan chay truoc -> AttributeError."""
        from vgt import evalset
        names = [p.name for p in evalset.report_files()]
        self.assertTrue(all(n[:8].isdigit() for n in names))
        self.assertTrue(evalset.compare({"case": [], "nhan": "x", "chi_phi": 0, "_file": ""}).startswith("Bo de"))


if __name__ == "__main__":
    unittest.main()


class TestGom(unittest.TestCase):
    def test_gom_canh_nho(self):
        from types import SimpleNamespace
        from vgt import mach
        n = {"a": 5, "b": 30, "c": 10, "d": 10, "e": 50, "f": 3, "z": 0}
        orig = mach._es
        mach._es = lambda p, g: [0] * n[g]
        try:
            self.assertEqual(mach.groups(None, list("abcdefz"), gop_dong=15, canh_nho=20),
                             [["a"], ["b"], ["c"], ["d"], ["e"], ["f"]])
            self.assertEqual(mach.groups(None, list("acdf"), gop_dong=60, canh_nho=20), [["a", "c", "d", "f"]])
        finally:
            mach._es = orig


class TestDichLai(Base):
    def test_dich_lai_xoa_tm(self):
        p = self.p
        p.run("mock")
        (p.path / "research.md").write_text("x", "utf-8")
        p.run("mock")
        self.reviewed()
        p.translate("mock", force=True)
        done = [e for e in p.store.entries() if e.kind in ("dialogue", "choice") and e.status != "new"]
        self.assertTrue(done)
        r = p.dich_lai()
        self.assertEqual(r["dong"], len([e for e in done if e.status in ("done", "tm", "qa_fail")]))
        self.assertFalse([e for e in p.store.entries() if e.kind == "dialogue" and e.status in ("done", "tm")])
        self.assertEqual(p._apply_tm(), 0)  # bo nho dich khong dien lai ban cu


class TestTheLoai(unittest.TestCase):
    def test_xung_ho_co_trang_hop_vo_hiep(self):
        """Quet Legend of Mortal 02/11: 'tai ha/bon toa' dung trong vo hiep, chi bao o the loai khac."""
        from types import SimpleNamespace
        from vgt import scan
        e = SimpleNamespace(kind="dialogue", source="在下姓葉", target="Tại hạ họ Diệp.")
        self.assertTrue(scan.line_hints(e, "zh", "dark fantasy phương Tây"))
        self.assertFalse(scan.line_hints(e, "zh", "RPG võ hiệp thế giới mở"))
        e2 = SimpleNamespace(kind="dialogue", source="宿願", target="Túc nguyện của ta.")
        self.assertTrue(scan.line_hints(e2, "zh", "võ hiệp"))  # tu hiem van bao moi the loai
