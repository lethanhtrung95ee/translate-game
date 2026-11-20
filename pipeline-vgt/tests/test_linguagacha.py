"""Adapter LinguaGacha (tay chan) + patch co `hide` (cat file goc vao _backup khi cai).

- Phan don vi: gia lap du an .lg (SQLite) va bridge -> khong can node/LinguaGacha.
- Phan that (tu bo qua neu thieu): VGT_LG_GAME=<thu muc game WOLF> + tools/LinguaGacha/<ver>/vgt-bridge.mjs
  -> trich xuat that, ghi 1 dong, tao ban dich, trich xuat lai ban dich thay dung dong do doi.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vgt.adapters import linguagacha as lgmod  # noqa: E402
from vgt.adapters.linguagacha import LinguaGacha, item_id  # noqa: E402
from vgt.patch import build, sha256  # noqa: E402
from vgt.pipeline import Project  # noqa: E402


def tmpdir(tc):
    d = Path(tempfile.mkdtemp(prefix="vgt_lg_"))
    tc.addCleanup(shutil.rmtree, d, True)
    return d


def wolf_item(src, file, loc, status="NONE", usage="text"):
    return {"src": src, "dst": "", "name_src": None, "name_dst": None,
            "extra_field": {"wolfrpg": {"internal_file_path": file, "usage": usage, "location": loc}},
            "tag": "", "file_path": "G.wolfrpg", "status": status, "skip_internal_filter": False, "row": 0}


ITEMS = [
    wolf_item("Hello there, Lecia.", "Data/BasicData/CommonEvent.dat",
              {"kind": "common_command", "event": 5, "command": 3, "code": 122, "string": 0}),
    wolf_item("Hello there, Lecia.", "Data/BasicData/CommonEvent.dat",
              {"kind": "common_command", "event": 9, "command": 1, "code": 122, "string": 0}, "DUPLICATED"),
    wolf_item("BGS", "Data/BasicData/CommonEvent.dat",                       # ten bien noi bo
              {"kind": "common_command", "event": 5, "command": 4, "code": 122, "string": 0}),
    wolf_item("\\f[24]\\E\\cself[5]", "Data/BasicData/CommonEvent.dat",       # chi ma dieu khien
              {"kind": "common_command", "event": 5, "command": 5, "code": 150, "string": 0}),
    wolf_item("Yes", "Data/MapData/Map001.mps",
              {"kind": "map_command", "event": 1, "page": 0, "command": 2, "code": 102, "string": 0}),
    wolf_item("Straw Hat", "Data/BasicData/DataBase.dat",
              {"kind": "database_string", "type": 23, "record": 4, "string": 0}),
    wolf_item("MapChip/a.png", "Data/BasicData/TileSetData.dat",
              {"kind": "tileset_string", "record": 0, "string": 1}, "RULE_SKIPPED", "metadata"),
    wolf_item("┗罰則_目", "Data/BasicData/DataBase.dat",
              {"kind": "database_string", "type": 2, "record": 1, "string": 0}, "LANGUAGE_SKIPPED"),
]


def make_lg(path: Path, items=ITEMS):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE items (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL)")
    for it in items:
        con.execute("INSERT INTO items (data) VALUES (?)", (json.dumps(it, ensure_ascii=False),))
    con.commit()
    con.close()


def make_wolf_game(root: Path) -> Path:
    g = root / "[Hentai] x" / "Wolf Game"
    (g / "Data").mkdir(parents=True)
    (g / "Data" / "BasicData.wolf").write_bytes(b"DX\x08\x00basic")
    (g / "Data" / "MapData.wolf").write_bytes(b"DX\x08\x00map")
    (g / "Data" / "Picture.wolf").write_bytes(b"DX\x08\x00pic")
    (g / "GamePro.exe").write_bytes(b"MZ")
    return g


class TestLinguaGachaAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir(self)
        self.game = make_wolf_game(self.tmp)
        self.proj = self.tmp / "proj"
        self.calls = []

        def fake_build(game, cfg):
            lg = Path(cfg["_project_dir"]) / "lg" / "project.lg"
            lg.parent.mkdir(parents=True, exist_ok=True)
            if not lg.exists():
                make_lg(lg)
            return lg

        def fake_bridge(cfg, *args):
            self.calls.append(args)
            if args[0] == "generate":
                proj, out = Path(args[args.index("--project") + 1]), Path(args[args.index("--out") + 1])
                con = sqlite3.connect(proj)
                done = [json.loads(d) for (d,) in con.execute("select data from items")]
                con.close()
                f = out / "game" / "Data" / "BasicData" / "CommonEvent.dat"
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(json.dumps([d["dst"] for d in done if d["status"] == "PROCESSED"], ensure_ascii=False), "utf-8")
                (out / "game" / "Data" / "MapData").mkdir(parents=True)
                (out / "game" / "Data" / "MapData" / "Map001.mps").write_bytes(b"m")
                (out / "bilingual").mkdir()
            return {"ok": True}

        orig_build, orig_bridge = LinguaGacha.build_project, lgmod._bridge
        LinguaGacha.build_project = classmethod(lambda cls, g, c: fake_build(g, c))
        lgmod._bridge = fake_bridge
        self.addCleanup(lambda: setattr(LinguaGacha, "build_project", orig_build))
        self.addCleanup(lambda: setattr(lgmod, "_bridge", orig_bridge))

    def test_detect_and_hides(self):
        self.assertTrue(LinguaGacha.detect(self.game))
        self.assertEqual(LinguaGacha.hides(self.game, {}), ["Data/BasicData.wolf", "Data/MapData.wolf"])
        self.assertEqual(LinguaGacha.probe(self.game, {}), "GamePro.exe")
        copy, _ = lgmod.wolf_sources(self.game)
        self.assertNotIn("Data/Picture.wolf", copy)  # chi chep file chua chu, khong chep ca game

    def test_extract_filters_and_groups(self):
        p = Project.init(self.game, self.proj, adapter="linguagacha", log=lambda *a: None)
        self.addCleanup(lambda: p.store.db.close())
        p.extract()
        es = {e.source: e for e in p.store.entries()}
        self.assertEqual(sorted(e.source for e in p.store.entries()),
                         ["Hello there, Lecia.", "Hello there, Lecia.", "Straw Hat", "Yes"])
        self.assertNotIn("BGS", es)
        self.assertEqual(es["Yes"].kind, "choice")
        self.assertEqual(es["Yes"].grp, "Map001:ev1p0")
        self.assertEqual(es["Straw Hat"].kind, "ui")
        dlg = [e for e in p.store.entries() if e.source.startswith("Hello")]
        self.assertEqual({e.grp for e in dlg}, {"CE5", "CE9"})
        self.assertTrue(all(e.kind == "dialogue" for e in dlg))

    def test_apply_writes_each_item_and_builds_hide_patch(self):
        p = Project.init(self.game, self.proj, adapter="linguagacha", log=lambda *a: None)
        self.addCleanup(lambda: p.store.db.close())
        p.extract()
        for e in p.store.entries():
            if e.grp == "CE5":
                e.target, e.status = "Chào, Lecia.", "done"
                p.store.save_result(e)
        out = p.apply(self.tmp / "patch")
        files = sorted(f.relative_to(out / "_viethoa" / "files").as_posix()
                       for f in (out / "_viethoa" / "files").rglob("*") if f.is_file())
        self.assertEqual(files, ["Data/BasicData/CommonEvent.dat", "Data/MapData/Map001.mps"])
        written = json.loads((out / "_viethoa" / "files" / "Data/BasicData/CommonEvent.dat").read_text("utf-8"))
        self.assertEqual(written, ["Chào, Lecia."])  # dong trung o CE9 chua dich -> khong bi ghi
        mf = json.loads((out / "_viethoa" / "vgt_patch.json").read_text("utf-8"))
        self.assertEqual([h["path"] for h in mf["hide"]], ["Data/BasicData.wolf", "Data/MapData.wolf"])
        self.assertEqual(mf["probe"], "GamePro.exe")
        base = self.proj / "lg" / "project.lg"
        con = sqlite3.connect(base)
        self.assertFalse([d for (d,) in con.execute("select data from items") if '"PROCESSED"' in d])
        con.close()  # ban goc .lg khong bi sua; ghi tren ban sao

    def test_apply_refuses_stale_ids(self):
        p = Project.init(self.game, self.proj, adapter="linguagacha", log=lambda *a: None)
        self.addCleanup(lambda: p.store.db.close())
        p.extract()
        e = p.store.entries()[0]
        e.target, e.status = "x", "done"
        p.store.save_result(e)
        lg = self.proj / "lg" / "project.lg"
        lg.unlink()
        make_lg(lg, ITEMS[2:])  # game doi phien ban: dong cu bien mat
        with self.assertRaises(SystemExit):
            p.apply(self.tmp / "patch")

    def test_extract_drops_cjk_labels_for_english_release(self):
        cfg = {"_project_dir": str(self.proj), "linguagacha": {"source_language": "EN"}}
        lg = Path(cfg["_project_dir"]) / "lg" / "project.lg"
        lg.parent.mkdir(parents=True)
        make_lg(lg, ITEMS[:1] + [wolf_item("音量[%]:\\cself[90]", "Data/BasicData/CommonEvent.dat",
                                           {"kind": "common_command", "event": 508, "command": 1, "code": 122, "string": 0})])
        self.assertEqual([e.source for e in LinguaGacha.extract(self.game, cfg)], ["Hello there, Lecia."])
        cfg["linguagacha"]["source_language"] = "JA"
        self.assertEqual(len(LinguaGacha.extract(self.game, cfg)), 2)

    def test_item_id_stable(self):
        a = item_id("f", {"b": 1, "a": 2})
        self.assertEqual(a, item_id("f", {"a": 2, "b": 1}))


def _pwsh():
    return shutil.which("pwsh") or (shutil.which("powershell") if sys.platform == "win32" else None) \
        or (str(Path.home() / "pwsh" / "pwsh") if (Path.home() / "pwsh" / "pwsh").exists() else None)


@unittest.skipUnless(_pwsh(), "can PowerShell (pwsh)")
class TestPatchHideRoundtrip(unittest.TestCase):
    def test_install_uninstall_with_hide(self):
        tmp = tmpdir(self)
        game = make_wolf_game(tmp)
        before = {f.relative_to(game).as_posix(): sha256(f) for f in game.rglob("*") if f.is_file()}
        staging = tmp / "Patch Name"
        fd = staging / "_viethoa" / "files" / "Data" / "BasicData"
        fd.mkdir(parents=True)
        (fd / "CommonEvent.dat").write_bytes(b"translated")
        build(game, staging, [fd / "CommonEvent.dat"], "GamePro.exe", ["Data/BasicData.wolf"])

        def run(mode, ok=True):
            r = subprocess.run([_pwsh(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                str(staging / "_viethoa" / "vgt_patch.ps1"), "-Mode", mode, "-Game", str(game),
                                "-NoPrompt"], capture_output=True, text=True)
            self.assertEqual(r.returncode == 0, ok, r.stdout + r.stderr)

        run("install")
        self.assertFalse((game / "Data" / "BasicData.wolf").exists())
        self.assertEqual((game / "Data" / "BasicData" / "CommonEvent.dat").read_bytes(), b"translated")
        self.assertTrue((staging / "_viethoa" / "_backup" / "Data" / "BasicData.wolf").exists())
        run("uninstall")
        after = {f.relative_to(game).as_posix(): sha256(f) for f in game.rglob("*") if f.is_file()}
        self.assertEqual(after, before)
        self.assertFalse((game / "Data" / "BasicData").exists())  # thu muc rong do patch tao da xoa
        self.assertFalse((staging / "_viethoa" / "_backup").exists())
        # File .wolf khac phien ban -> khong cai
        (game / "Data" / "BasicData.wolf").write_bytes(b"other version")
        run("install", ok=False)
        self.assertTrue((game / "Data" / "BasicData.wolf").exists())


GAME = os.environ.get("VGT_LG_GAME")


@unittest.skipUnless(GAME and (lgmod._lgcfg({})["tools_dir"] / "vgt-bridge.mjs").exists() and shutil.which("node"),
                     "can VGT_LG_GAME + vgt-bridge.mjs + node")
class TestLinguaGachaReal(unittest.TestCase):
    def test_real_roundtrip(self):
        tmp = tmpdir(self)
        cfg = {"_project_dir": str(tmp / "proj"), "linguagacha": {"source_language": "EN"}}
        game = Path(GAME)
        before = {f.name: f.stat().st_mtime for f in (game / "Data").glob("*.wolf")}
        es = LinguaGacha.extract(game, cfg)
        self.assertGreater(len(es), 100)
        e = next(x for x in es if x.kind == "dialogue")
        e.target, e.status = "Thử: ăn ơ ư đ ạ ấ ỡ", "done"
        out = tmp / "out"
        files = LinguaGacha.apply(game, out, [e], cfg)
        self.assertTrue(any(f.name == "CommonEvent.dat" or f.suffix == ".mps" for f in files))
        self.assertEqual(before, {f.name: f.stat().st_mtime for f in (game / "Data").glob("*.wolf")})  # game khong bi sua
        # Trich xuat lai tu ban dich: dung dong do doi, so dong giu nguyen.
        shadow = tmp / "rt" / "g"
        shutil.copytree(out, shadow)
        lg = tmp / "rt.lg"
        lgmod._bridge(cfg, "extract", "--game", str(shadow), "--project", str(lg), "--src-lang", "EN", "--tgt-lang", "VI")
        got = {item_id(it["extra_field"]["wolfrpg"]["internal_file_path"], it["extra_field"]["wolfrpg"]["location"]): it["src"]
               for _, it in lgmod.read_items(lg) if "wolfrpg" in (it.get("extra_field") or {})}
        self.assertEqual(got[e.id], e.target)


if __name__ == "__main__":
    unittest.main()
