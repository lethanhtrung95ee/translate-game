"""G-023: cua bible ve xung ho (dung cho moi game)."""
import unittest
from types import SimpleNamespace as E

from vgt import biblecheck


def lines(pairs):
    out = []
    for i, sp in enumerate(pairs):
        out.append(E(kind="dialogue", grp="g1", seq=i, speaker=sp, face=None, source=f"{sp} noi {i}"))
    return out


BIBLE = {"characters": [{"id": "boss", "names": ["獄霸"], "name_vi": "Trùm", "self": "ông đây"},
                        {"id": "lili", "names": ["莉莉娜"], "name_vi": "Lilina", "self": "tôi"}],
         "relations": [{"from": "boss", "to": "lili", "self": "ông đây", "call": "em gái / mày"}]}


class BibleCheckTest(unittest.TestCase):
    def test_ambiguous(self):
        self.assertTrue(biblecheck.ambiguous("em gái / mày"))
        self.assertTrue(biblecheck.ambiguous("anh / ông"))
        self.assertFalse(biblecheck.ambiguous("mày; khi dụ dỗ: em gái"))
        self.assertFalse(biblecheck.ambiguous("con / \\N[1]"))
        self.assertFalse(biblecheck.ambiguous("chủ nhân; trịnh trọng: nữ vương (của em)/nữ vương đại nhân"))

    def test_missing_reverse_and_ambiguous(self):
        es = lines(["獄霸", "莉莉娜", "獄霸", "莉莉娜", "獄霸", "莉莉娜"])
        iss = biblecheck.check(BIBLE, es, min_exchanges=3)
        kinds = {(i["loai"], i["from"], i.get("to")) for i in iss}
        self.assertIn(("thieu_quan_he", "lili", "boss"), kinds)   # Lilina goi Trum the nao: chua co
        self.assertIn(("mo_ho", "boss", "lili"), kinds)          # 'em gai / may'
        self.assertNotIn(("thieu_quan_he", "boss", "lili"), kinds)

    def test_address_hints(self):
        """G-023: xung/goi theo tung dong; quan he theo cap thang ho so chung."""
        from vgt.bible import BibleIndex
        b = BibleIndex({"characters": [{"id": "lili", "names": ["莉莉娜"], "name_vi": "Lilina",
                                        "self": "tôi (với người ngoài); mình (độc thoại)"},
                                       {"id": "nell", "names": ["妮兒"], "name_vi": "Nell", "self": "mình"}],
                        "relations": [{"from": "lili", "to": "nell", "self": "mình", "call": "cậu"}]})
        es = lines(["莉莉娜", "妮兒", "莉莉娜"])
        for i, e in enumerate(es):
            e.id = f"e{i}"
        h = b.address_hints(es)
        self.assertIn("xưng 'mình'", h["e0"])        # quan he cap thang 'tôi' cua ho so
        self.assertIn("gọi 'cậu'", h["e0"])
        self.assertIn("xưng 'mình'", h["e1"])        # Nell: khong co quan he -> self chung
        self.assertEqual(BibleIndex._first("tôi (với người ngoài); mình"), "tôi")

    def test_thuat_ngu_apply(self):
        """G-024: thay doi thuat ngu ap bang vgt term (0 token)."""
        import tempfile
        from pathlib import Path
        from vgt import thuatngu
        class FakeProj:
            def __init__(s):
                s.path = Path(tempfile.mkdtemp()); s.calls = []
        self.assertEqual(thuatngu._split({"src": "淫魔 / 淫魔王", "vi": "dâm ma / Dâm Ma Vương"}),
                         [("淫魔", "dâm ma"), ("淫魔王", "Dâm Ma Vương")])
        self.assertEqual(thuatngu._split({"src": "a / b", "vi": "x"}), [("a", "x")])

    def test_thuat_ngu_lech_goc(self):
        """Loi 02/11: lo duyet doc lap chon cach dich goc khac nhau (淫魔 Succubus / quy dam)."""
        from vgt import thuatngu
        ch = [{"src": "淫魔", "moi": "Succubus"}, {"src": "淫魔王", "moi": "Vua Succubus"},
              {"src": "淫魔將", "moi": "Tướng quỷ dâm"}]
        lech = thuatngu._lech_goc(ch)
        self.assertEqual(len(lech), 1)
        self.assertIn("淫魔將", lech[0])
        self.assertEqual(thuatngu._lech_goc(ch[:2]), [])

    def test_few_exchanges_ignored(self):
        self.assertFalse([i for i in biblecheck.check(BIBLE, lines(["獄霸", "莉莉娜"]), min_exchanges=3)
                          if i["loai"] == "thieu_quan_he"])


if __name__ == "__main__":
    unittest.main()
