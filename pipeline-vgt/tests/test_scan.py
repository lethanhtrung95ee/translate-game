"""Do loi chung (0 token): dau cach ma ten, giong may theo ngon ngu nguon, xung ho ca canh."""
import unittest
from types import SimpleNamespace as E

from vgt import scan
from vgt.bible import BibleIndex

B = BibleIndex({"characters": [{"id": "boss", "names": ["獄霸"]}, {"id": "lili", "names": ["莉莉娜"]}]})


def ln(i, sp, src, vi, kind="dialogue"):
    return E(id=f"e{i}", kind=kind, grp="g", seq=i, speaker=sp, face=None, source=src, target=vi, qa=[])


class ScanTest(unittest.TestCase):
    def test_space_codes(self):
        self.assertEqual(scan.space_codes(r"\C[6]Chó cái\N[1]\C[0]"), r"\C[6]Chó cái \N[1]\C[0]")
        self.assertEqual(scan.space_codes(r"Thánh nữ\C[6]\N[1]\C[0]!"), r"Thánh nữ \C[6]\N[1]\C[0]!")
        self.assertEqual(scan.space_codes(r"\C[6]\N[1]\C[0]: Ông!"), r"\C[6]\N[1]\C[0]: Ông!")
        self.assertEqual(scan.space_codes(r"\N[53]canh gác"), r"\N[53] canh gác")

    def test_line_hints_zh(self):
        e = ln(1, "歐文", "帝國頒發了\\C[6]1,000,000\\G\\C[0]給你做為額外獎金！",
               "Đế quốc ban cho em \\C[6]1,000,000\\G\\C[0] làm tiền thưởng thêm!")
        self.assertTrue(scan.line_hints(e, "zh"))
        self.assertFalse(scan.line_hints(e, "ja"))
        good = ln(2, "歐文", e.source, "Đế quốc thưởng thêm cho em \\C[6]1,000,000\\G\\C[0]!")
        self.assertFalse(scan.line_hints(good, "zh"))
        e3 = ln(3, "歐文", "行了，就這些事，你可以出去了", "Được rồi, chỉ có thế thôi, em ra ngoài được rồi.")
        self.assertTrue(scan.line_hints(e3, "zh"))

    def test_lam_nhe_cap(self):
        from vgt.content import lam_nhe_cap
        self.assertTrue(lam_nhe_cap("你的洞里也讓我很舒服～", "bên trong em cũng làm anh sướng lắm~", "zh"))
        self.assertEqual(lam_nhe_cap("你的洞里也讓我很舒服～", "lỗ của em cũng làm anh sướng lắm~", "zh"), [])

    def test_thang_18(self):
        """G-022: giu dung muc tu (chuan chung moi game)."""
        from vgt.adult import check_levels, prompt_block
        self.assertIn("nói tránh", check_levels("一直摩擦著陰莖", "cứ cọ vào cái ấy", "zh")[0])
        self.assertIn("không có từ", check_levels("那么粗大的肉棒", "thứ to thế kia", "zh")[0])
        self.assertIn("hạ mức", check_levels("我要肏死你", "Ta sẽ chiếm đoạt ngươi", "zh")[0])
        self.assertIn("nâng mức", check_levels("陰莖好硬", "Cặc cứng quá", "zh")[0])
        self.assertEqual(check_levels("快把精液射進我的小穴里", "bắn hết tinh dịch vào khe thịt của em", "zh"), [])
        self.assertEqual(check_levels("我要肏死你這個騷屄", "Tao sẽ địt chết con lồn dâm này", "zh"), [])
        self.assertEqual(check_levels("Your cock is so hard", "Cặc anh cứng quá", "en"), [])
        self.assertEqual(check_levels("我舔了一下冰淇淋", "Tôi liếm cây kem", "zh"), [])  # tu da nghia: bo qua
        self.assertIn("雞巴", prompt_block("zh"))
        self.assertNotIn("ちんぽ", prompt_block("zh"))

    def test_more_hints(self):
        self.assertEqual(scan.space_codes("cứng quá đi……  cảm giác lạ"), "cứng quá đi…… cảm giác lạ")
        self.assertEqual(scan.space_codes("  thụt lề"), "  thụt lề")
        h = scan.line_hints(ln(1, "x", "讓～讓我～射～射～～", "Cho… cho tôi… bắn… bắn……"), "zh")
        self.assertTrue(any("kéo dài" in x for x in h))
        self.assertTrue(scan.line_hints(ln(2, "x", "我只是可以介紹一份工作而已", "mình chỉ có thể giới thiệu cho cậu một công việc thôi"), "zh"))
        self.assertTrue(scan.line_hints(ln(3, "x", "射了啊～～", "bắn rồi a~~"), "zh"))
        self.assertTrue(scan.line_hints(ln(4, "x", "讓我重整雄風", "để anh lấy lại hùng phong"), "zh"))
        self.assertFalse(scan.line_hints(ln(5, "x", "射了啊～～", "bắn rồi~~"), "zh"))

    def test_scene_pair_mismatch(self):
        es = [ln(1, "獄霸", "我聽說…", "Trùm: Ông đây nghe nói em định vượt ngục"),
              ln(2, "莉莉娜", "你！你別胡說！", "Lilina: Anh! Đừng có nói bậy!"),
              ln(3, "獄霸", "我哪敢胡說呢～", "Trùm: Ông đây nào dám nói bậy~")]
        h = scan.scene_hints(es, B)
        self.assertIn("e2", h)
        self.assertNotIn("e1", h)

    def test_self_against_bible(self):
        b = BibleIndex({"characters": [{"id": "lili", "names": ["莉莉娜"], "self": "tôi"},
                                       {"id": "nell", "names": ["妮兒"], "self": "mình"}],
                        "relations": [{"from": "lili", "to": "nell", "self": "mình", "call": "cậu"}]})
        es = [ln(1, "莉莉娜", "a", "Lilina: Chào cậu, cần tôi giúp không?"),
              ln(2, "妮兒", "b", "Nell: Cậu là……"),
              ln(3, "莉莉娜", "c", "Lilina: Mình tên Lilina")]
        h = scan.scene_hints(es, b)
        self.assertIn("e1", h)
        self.assertNotIn("e3", h)

    def test_no_false_positive_crowd(self):
        """Eval 01/11: canh nhieu nguoi / noi voi ca nhom: khong bao xung nhieu kieu."""
        es = [ln(1, "莉莉娜", "a", "Lilina: Ta không sợ"), ln(2, "獄霸", "b", "Trùm: Hử?"),
              ln(3, "囚犯", "c", "Tù: Đại ca!"), ln(4, "莉莉娜", "d", "Lilina: Tôi xin lỗi")]
        self.assertEqual(scan.scene_hints(es, B), {})
        es2 = [ln(1, "莉莉娜", "a", "Lilina: Ta đi đây"), ln(2, "獄霸", "b", "Trùm: Ừ"),
               ln(3, "莉莉娜", "c", "Lilina: Mọi người đừng lo, tôi ổn")]
        self.assertEqual(scan.scene_hints(es2, B), {})

    def test_scene_self_variety(self):
        es = [ln(1, "莉莉娜", "a", "Lilina: Tôi đi đây"), ln(2, "莉莉娜", "b", "Lilina: Tôi mệt"),
              ln(3, "莉莉娜", "c", "Lilina: Ta không sợ")]
        h = scan.scene_hints(es, B)
        self.assertEqual(list(h), ["e3"])


if __name__ == "__main__":
    unittest.main()
