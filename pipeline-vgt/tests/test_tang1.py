"""Kiem thu: ban tham khao (tieng Anh chinh thuc), luat QA G-018/G-020, kiem font (tang 1)."""
import json
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_pipeline import make_game, tmpdir  # noqa: E402
from vgt import bible as biblemod  # noqa: E402
from vgt import fontcheck  # noqa: E402
from vgt.backend import MockBackend  # noqa: E402
from vgt.pipeline import Project  # noqa: E402
from vgt.qa import check  # noqa: E402
from vgt.store import Entry  # noqa: E402


def tiny_font(path: Path, chars: str) -> Path:
    """Font TrueType toi thieu chi co cac ky tu `chars` (de kiem cmap)."""
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    chars = "".join(dict.fromkeys(chars))
    names = [".notdef"] + [f"g{ord(c)}" for c in chars]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap({ord(c): f"g{ord(c)}" for c in chars})
    pen = TTGlyphPen(None)
    pen.moveTo((0, 0)); pen.lineTo((0, 500)); pen.lineTo((400, 0)); pen.closePath()
    g = pen.glyph()
    fb.setupGlyf({n: g for n in names})
    fb.setupHorizontalMetrics({n: (500, 0) for n in names})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": "Tiny", "styleName": "Regular"})
    fb.setupOS2()
    fb.setupPost()
    fb.save(str(path))
    return path


class Cfg:
    cfg = {"qa": {"max_line_chars": 48, "max_lines_per_box": 4, "ui_max_chars": 24, "ui_max_ratio": 2.2,
                  "ui_too_long": "error"}}


def qa(src, out, kind="dialogue"):
    e = Entry(id="x", file="f", locator={}, grp="g", seq=0, kind=kind, source=src)
    return check(e, src, out, out, biblemod.BibleIndex({}), Cfg.cfg, "zh")


class TestQARules(unittest.TestCase):
    def test_mixed_self_pronoun_warns(self):
        self.assertTrue(any("G-018" in x for x in qa("我來了。", "Tôi tới rồi, ta mệt quá.")))
        self.assertFalse(any("G-018" in x for x in qa("我們走吧。", "Chúng ta đi thôi, tôi mệt rồi.")))
        self.assertFalse(any("G-018" in x for x in qa("我來了。", "Ta tới rồi.")))

    def test_stutter_lost_warns(self):
        self.assertTrue(any("G-020" in x for x in qa("討、討厭！", "Ghét quá!")))
        self.assertFalse(any("G-020" in x for x in qa("討、討厭！", "G-ghét quá!")))
        self.assertFalse(any("G-020" in x for x in qa("討厭！", "Ghét quá!")))
        self.assertTrue(any("G-020" in x for x in qa("I-I hate it!", "Ghét quá!")))


class TestReferenceAndFont(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir(self)
        self.game = make_game(self.tmp)
        en = self.game / "dataEN"
        shutil.copytree(self.game / "data", en)
        doc = json.loads((en / "Map001.json").read_text("utf-8"))
        doc["events"][1]["pages"][0]["list"][2]["parameters"][0] = "Do you have a potion?"
        (en / "Map001.json").write_text(json.dumps(doc, ensure_ascii=False), "utf-8")
        self.logs = []
        self.p = Project.init(self.game, self.tmp / "proj", log=self.logs.append)
        self.p.log = self.logs.append
        self.addCleanup(lambda: self.p.store.db.close())

    def test_reference_extracted_and_sent(self):
        p = self.p
        p.extract()
        e = p.store.entries("id=?", ("Map001.json:ev1p0@0",))[0]
        self.assertIn("Do you have a potion?", e.ref)
        self.assertTrue(any("Ban tham khao dataEN" in x for x in self.logs))
        p.draft_bible("mock")
        b = biblemod.load(p.path)
        b["reviewed"] = True
        biblemod.save(p.path, b)
        seen = []

        class Rec(MockBackend):
            def call(s, system, prompt, schema, model, effort=None, timeout=None):
                seen.append(json.loads(prompt.split("\n", 1)[1]))
                return MockBackend.call(s, system, prompt, schema, model, effort, timeout)
        p.backend = lambda kind: Rec()
        p.translate("mock")
        rows = [r for pl in seen for r in pl.get("lines", [])]
        self.assertTrue(any("potion" in (r.get("en") or "") for r in rows))

    def test_reference_off(self):
        (self.p.path / "config.yaml").write_text("reference:\n  enabled: false\n", "utf-8")
        p = Project(self.p.path, self.logs.append)
        self.addCleanup(lambda: p.store.db.close())
        p.extract()
        self.assertTrue(all(e.ref is None for e in p.store.entries()))

    def test_font_missing_vietnamese_glyphs(self):
        p = self.p
        p.extract()
        for e in p.store.entries():
            e.target, e.status = "Xin chào bạn", "done"
            p.store.save_result(e)
        ascii_font = tiny_font(self.tmp / "ascii.ttf", "Xin chao b")
        ok, msg = fontcheck.report(p, ascii_font)
        self.assertFalse(ok)
        self.assertIn("U+00E0", msg)  # à
        full = tiny_font(self.tmp / "full.ttf", "Xin chào bạn")
        ok, msg = fontcheck.report(p, full)
        self.assertTrue(ok, msg)
        # Khong co font -> bao ro, khong bao dat
        ok, msg = fontcheck.report(p, self.tmp / "khong_co.ttf")
        self.assertFalse(ok)


class TestContentFidelity(unittest.TestCase):
    def test_refusal_and_softening_flagged(self):
        self.assertTrue(any("[từ chối]" in x for x in qa("他抱住了她。", "I can't help with that.")))
        self.assertTrue(any("[làm nhẹ?]" in x for x in qa("他的肉棒插入了小穴。", "Anh ấy ôm cô ấy.")))
        self.assertFalse(any("[làm nhẹ?]" in x for x in qa("他的肉棒插入了小穴。", "Dương vật hắn đâm vào lồn cô.")))
        self.assertFalse(any("[làm nhẹ?]" in x for x in qa("他抱住了她。", "Anh ấy ôm cô ấy.")))


class TestRefusedLineIsolated(unittest.TestCase):
    def test_content_fidelity(self):
        from vgt.backend import BackendError
        tmp = tmpdir(self)
        game = make_game(tmp)
        p = Project.init(game, tmp / "proj", log=lambda *a: None)
        p.log = lambda *a: None
        self.addCleanup(lambda: p.store.db.close())
        p.extract()
        p.draft_bible("mock")
        b = biblemod.load(p.path)
        b["reviewed"] = True
        biblemod.save(p.path, b)

        class Refuse(MockBackend):  # tu choi ca lo neu co dong chua "ポーション"
            def call(s, system, prompt, schema, model, effort=None, timeout=None):
                pl = json.loads(prompt.split("\n", 1)[1])
                if any("ポーション" in r["s"] for r in pl.get("lines", [])):
                    raise BackendError("Khong co structured_output: refused")
                return MockBackend.call(s, system, prompt, schema, model, effort, timeout)
        p.backend = lambda kind: Refuse()
        p.translate("mock")
        es = p.store.entries()
        refused = [e for e in es if any("[giữ gốc]" in x for x in e.qa)]
        self.assertTrue(refused and all("ポーション" in e.source for e in refused))
        # Khong dich duoc -> giu nguyen ban goc (khong co ban tieng Anh), khong goi lai
        self.assertTrue(all(e.target == (e.ref or e.source) and e.status == "manual" for e in refused))
        others = [e for e in es if "ポーション" not in e.source]
        self.assertTrue(all(e.attempts > 0 for e in others))  # dong khac van duoc dich
        self.assertIn("tu choi", p.status())
        # Qua nhieu dong giu goc -> run dung lai, khong tu y giu goc them
        p.cfg["content"] = {"max_keep_lines": 0, "max_keep_ratio": 0}
        (p.path / "research.md").write_text("x", "utf-8")
        p.store.set_meta("trial_grps", ["Map001.json:ev1p0"])
        p.store.set_meta("trial_ok", True)
        p.store.set_meta("xung_ho_duyet", "test")
        p.store.set_meta("xung_ho_ok", True)
        p.store.set_meta("thuat_ngu_duyet", "test")
        self.assertEqual(p.run("mock"), "CAN_DICH_LAI_LUONG_MOI")  # 02/11: da co dong dich theo luong cu
        p.store.set_meta("giu_luong_cu", "test")
        self.assertEqual(p.run("mock"), "CAN_DONG_Y_CHI_DAO")  # 02/11: hoi truoc khi lam chi dao ca game
        p.store.set_meta("chi_dao_dong_y", "test")
        self.assertEqual(p.run("mock"), "CAN_KIEM_TRA_GIU_GOC")


if __name__ == "__main__":
    unittest.main()
