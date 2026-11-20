"""Kiem thu adapter Unreal (pak v11 + locres) bang game gia, khong can Oodle."""
import gc
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vgt.patch import sha256  # noqa: E402
from vgt.pipeline import Project  # noqa: E402
from vgt.protect import mask, unmask  # noqa: E402
from vgt.unreal.locres import Locres  # noqa: E402
from vgt.unreal.pak import PakReader, pak_order, path_hash, write_pak  # noqa: E402
from vgt.adapters.unreal_locres import UnrealLocres  # noqa: E402

LOC = "FG/Content/Localization/Game/{}/Game.locres"
FONT = "FG/Content/UI/Font/SE-Alps.ufont"
NOTO = "FG/Content/UI/Font/Noto.ufont"


def make_locres(rows: dict) -> bytes:
    """rows: {(ns, key): text} -> locres v3 (hash gia, giu nguyen khi ghi lai)."""
    loc = Locres.__new__(Locres)
    loc.ver = 3
    by_ns: dict = {}
    for i, ((ns, k), t) in enumerate(rows.items()):
        by_ns.setdefault(ns, []).append([1000 + i, k, 7000 + i, t])
    loc.ns = [(len(ns), ns, keys) for ns, keys in by_ns.items()]
    return loc.dump()


EN = {("ST_C01_101", "101_001"): "Hello,\r\nfriend. <text style=\"italic\">Run</>!",
      ("ST_C01_101", "101_002"): "Thanks.",
      ("ST_EquipmentName", "Equip1"): "Silver Plate",
      ("ST_EquipmentName", "Equip1_sg"): "silver plate",
      ("ST_EquipmentName", "Equip1_det_sg"): "a silver plate",
      ("ST_UI_Word", "Next"): "Next",
      ("ST_UI_Word", "Empty"): ""}
JA = {k: f"日本語{i}" if v else "" for i, (k, v) in enumerate(EN.items())}


def make_game(root: Path) -> Path:
    game = root / "Game X [v1]"
    paks = game / "FG" / "Content" / "Paks"
    write_pak(paks / "FG-Windows.pak", {LOC.format("en"): make_locres(EN), LOC.format("ja"): make_locres(JA),
                                        FONT: b"alps", NOTO: b"noto", "FG/Content/x.bin": b"x" * 100})
    (game / "FG.exe").write_bytes(b"MZ")
    return game


class TestUnreal(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._td.name)
        self.game = make_game(self.tmp)

    def tearDown(self):
        gc.collect()  # dong ket noi sqlite con mo truoc khi xoa thu muc tam (Windows)
        self._td.cleanup()

    def test_mask_unreal_rich_text(self):
        s = '<text style="italic">Hi {Effect1Param1}</> <IA tag="Unit_Ride"/> [Black Magic]'
        m, codes = mask(s)
        self.assertEqual(codes, ['<text style="italic">', "{Effect1Param1}", "</>", '<IA tag="Unit_Ride"/>'])
        self.assertIn("[Black Magic]", m)  # chu hien thi, phai dich
        self.assertEqual(unmask(m, codes), s)

    def test_qa_catches_japanese_left_in_english_game(self):
        from vgt.qa import check
        from vgt.bible import BibleIndex
        from vgt.config import load_config
        from vgt.store import Entry
        e = Entry(id="a", file="f", locator={}, grp="g", seq=1, kind="dialogue", source="異質な台座がある……。")
        errs = check(e, e.source, "Có bệ thờ 台座……", "Có bệ thờ 台座……", BibleIndex({}), load_config(), "en")
        self.assertTrue(any("sót chữ gốc" in x for x in errs))

    def test_locres_roundtrip_unicode(self):
        rows = {**EN, ("ST_X", "k"): "Tiếng Việt ’ữ’"}
        data = make_locres(rows)
        loc = Locres(data)
        self.assertEqual(dict(loc.items()), rows)
        self.assertEqual(loc.dump(), data)

    def test_pak_write_read_and_index(self):
        files = {"A/b.txt": b"hello", "A/C/d.bin": b"\0" * 10, "e.txt": b"root", "F/same.ufont": b"hello"}
        p = write_pak(self.tmp / "t.pak", files, seed=0x1234)
        r = PakReader(p)
        self.assertEqual({k: r.read(k) for k in r.files}, files)
        # Path hash index phai co ca pruned directory index day du (game shipping duyet thu muc bang no).
        raw = p.read_bytes()
        self.assertEqual(raw.count(b"hello"), 1)  # noi dung trung chi luu 1 lan
        _, _, ioff, isz = struct.unpack("<IIqq", raw[-221 + 17:-221 + 41])
        idx = raw[ioff:ioff + isz]
        mlen, = struct.unpack_from("<i", idx)
        phi_off, phi_len = struct.unpack_from("<qq", idx, 4 + mlen + 4 + 8 + 4)
        cnt, = struct.unpack_from("<I", raw, phi_off)
        hashes = {struct.unpack_from("<Q", raw, phi_off + 4 + i * 12)[0] for i in range(cnt)}
        self.assertEqual(hashes, {path_hash(k, 0x1234) for k in files})
        self.assertGreater(phi_len, 4 + cnt * 12 + 4)
        r.close()

    def test_mod_pak_outranks_every_game_pak(self):
        # FINAL FANTASY RESONANCE: pak trong ~mods (3100) thua FFRS-Windows.pak (4000) -> van tieng Anh.
        g = Path("G")
        self.assertEqual(pak_order(g, "FG/Content/Paks/FG-Windows.pak"), 4000)
        self.assertEqual(pak_order(g, "FG/Content/Paks/FG-Windows_0_P.pak"), 4100)
        self.assertEqual(pak_order(g, "FG/Content/Paks/~mods/zVietHoa_P.pak"), 3100)
        self.assertEqual(pak_order(g, "FG/Content/Paks/pakchunk0-WindowsNoEditor.pak"), 3000)
        (self.game / "FG/Content/Paks/FG-Windows_0_P.pak").write_bytes(b"")
        mod = UnrealLocres.mod_pak(self.game, {})
        top = max(pak_order(self.game, p) for p in (self.game / "FG/Content/Paks").rglob("*.pak"))
        self.assertGreater(pak_order(self.game, mod), top)
        self.assertGreater(pak_order(g, mod), pak_order(g, "FG/Content/Paks/FG-Windows_98_P.pak"))

    def test_iostore_game_gets_empty_utoc_ucas(self):
        # FINAL FANTASY RESONANCE (UE5 IoStore): pak mod thieu .utoc bi bo qua -> game van tieng Anh.
        from vgt.unreal.iostore import HEADER, MAGIC, empty_container, read_header
        paks = self.game / "FG/Content/Paks"
        game_toc = struct.pack("<16sB", MAGIC, 8) + bytes(HEADER - 17)
        (paks / "FG-Windows.utoc").write_bytes(bytes(game_toc))
        (paks / "FG-Windows.ucas").write_bytes(b"")
        p = Project.init(self.game, self.tmp / "proj", log=lambda *a: None)
        p.extract()
        e = next(x for x in p.store.entries() if x.id == "ST_UI_Word/Next")
        e.target, e.status = "Tiếp", "manual"
        p.store.save_result(e)
        out = p.apply()
        fd = out / "_viethoa" / "files"
        files = sorted(x.relative_to(fd).as_posix() for x in fd.rglob("*") if x.is_file())
        self.assertEqual(files, ["FG/Content/Paks/FG-zVietHoa_999_P.pak", "FG/Content/Paks/FG-zVietHoa_999_P.ucas",
                                 "FG/Content/Paks/FG-zVietHoa_999_P.utoc"])
        h = read_header((fd / files[2]).read_bytes())
        self.assertEqual((h["version"], h["entries"], h["header_size"], h["partitions"]), (8, 0, HEADER, 1))
        self.assertNotEqual(h["container_id"], read_header(bytes(game_toc))["container_id"])
        self.assertEqual(len((fd / files[2]).read_bytes()), HEADER)

    def test_source_ja_with_english_reference_and_fallback(self):
        """Dich tu ban goc tieng Nhat; tieng Anh lam tham khao; dong chua dich hien tieng Anh."""
        p = Project.init(self.game, self.tmp / "projja", log=lambda *a: None)
        p.cfg["unreal"]["source_culture"] = "ja"
        p.cfg["unreal"]["variant_suffixes"] = ["_det_sg", "_sg"]
        p.cfg["source_lang"] = "ja"
        p.extract()
        e = p.store.entries("id=?", ("ST_C01_101/101_002",))[0]
        self.assertTrue(e.source.startswith("日本語"))
        self.assertEqual(e.ref, "Thanks.")
        t = p.store.entries("id=?", ("ST_UI_Word/Next",))[0]
        t.target, t.status = "Tiếp", "manual"
        p.store.save_result(t)
        out = p.apply()
        r = PakReader(out / "_viethoa" / "files" / "FG/Content/Paks/FG-zVietHoa_999_P.pak")
        ja = dict(Locres(r.read(LOC.format("ja"))).items())
        self.assertEqual(ja[("ST_C01_101", "101_002")], "Thanks.")  # chua dich -> tieng Anh, khong tieng Nhat
        p.store.db.close()

    def test_end_to_end_patch_adds_only_mod_pak(self):
        p = Project.init(self.game, self.tmp / "proj", log=lambda *a: None)
        self.assertEqual(p.adapter.name, "unreal_locres")
        p.cfg["unreal"]["variant_suffixes"] = ["_det_sg", "_sg"]
        p.cfg["unreal"]["fonts"] = {FONT: NOTO}
        p.extract()
        ents = {e.id: e for e in p.store.entries()}
        # Bien the _sg/_det_sg va chuoi rong khong gui model; \r\n doi thanh \n.
        self.assertEqual(sorted(ents), ["ST_C01_101/101_001", "ST_C01_101/101_002",
                                        "ST_EquipmentName/Equip1", "ST_UI_Word/Next"])
        self.assertEqual(ents["ST_C01_101/101_001"].source, 'Hello,\nfriend. <text style="italic">Run</>!')
        self.assertEqual(ents["ST_EquipmentName/Equip1"].kind, "name")
        self.assertEqual(ents["ST_C01_101/101_001"].kind, "dialogue")
        for i, t in (("ST_C01_101/101_001", 'Chào,\nbạn. <text style="italic">Chạy</>!'),
                     ("ST_EquipmentName/Equip1", "Giáp bạc")):
            e = ents[i]
            e.target, e.status = t, "manual"
            p.store.save_result(e)
        out = p.apply()
        fd = out / "_viethoa" / "files"
        files = [x.relative_to(fd).as_posix() for x in fd.rglob("*") if x.is_file()]
        self.assertEqual(files, ["FG/Content/Paks/FG-zVietHoa_999_P.pak"])
        mf = json.loads((out / "_viethoa" / "vgt_patch.json").read_text("utf-8"))
        self.assertEqual(mf["probe"], "FG/Content/Paks/FG-Windows.pak")
        self.assertIsNone(mf["files"][0]["orig"])
        r = PakReader(fd / files[0])
        self.assertEqual(r.read(FONT), b"noto")
        en, ja = (dict(Locres(r.read(LOC.format(c))).items()) for c in ("en", "ja"))
        for d in (en, ja):  # moi lua chon ngon ngu deu ra tieng Viet
            self.assertEqual(d[("ST_C01_101", "101_001")], 'Chào,\r\nbạn. <text style="italic">Chạy</>!')
            self.assertEqual(d[("ST_EquipmentName", "Equip1_det_sg")], "Giáp bạc")
            self.assertEqual(d[("ST_C01_101", "101_002")], "Thanks.")  # chua dich -> tieng Anh, khong CJK
            self.assertEqual(d[("ST_UI_Word", "Empty")], "")
        # source hash giu nguyen (hash cua chuoi native), neu doi game bo qua ban dich.
        ja_loc = Locres(r.read(LOC.format("ja")))
        orig = Locres(make_locres(JA))
        self.assertEqual([[k[0], k[1], k[2]] for _, _, ks in ja_loc.ns for k in ks],
                         [[k[0], k[1], k[2]] for _, _, ks in orig.ns for k in ks])
        r.close()
        if sys.platform != "win32":
            return
        before = {f.relative_to(self.game).as_posix(): sha256(f) for f in self.game.rglob("*") if f.is_file()}

        def run(mode):
            res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                  str(out / "_viethoa" / "vgt_patch.ps1"), "-Mode", mode, "-Game",
                                  str(self.game), "-NoPrompt"], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

        run("install")
        self.assertEqual(sha256(self.game / files[0]), sha256(fd / files[0]))
        with self.assertRaises(SystemExit):  # dang cai -> khong extract/apply tu file da patch
            p.extract()
        run("uninstall")
        after = {f.relative_to(self.game).as_posix(): sha256(f) for f in self.game.rglob("*") if f.is_file()}
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
