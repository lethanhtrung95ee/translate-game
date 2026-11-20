"""Kiem thu: python -m unittest discover -s tests"""
import gc
import json
import os
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vgt import bible as biblemod  # noqa: E402
from vgt.backend import ClaudeCodeBackend, LimitReached  # noqa: E402
from vgt.config import load_config  # noqa: E402
from vgt.pipeline import Project  # noqa: E402
from vgt.protect import mask, unmask  # noqa: E402
from vgt.textfit import fit_message  # noqa: E402


def cmd(code, *params, indent=0):
    return {"code": code, "indent": indent, "parameters": list(params)}


def make_game(root: Path) -> Path:
    data = root / "game" / "data"
    data.mkdir(parents=True)
    long_line = "とても長い台詞です。" * 3
    ev_list = [
        cmd(101, "Actor1", 0, 0, 2, "アリス"),          # MZ: speakerName
        cmd(401, "こんにちは、\\C[2]ボブ\\C[0]さん。"),
        cmd(401, "ポーションを持ってる？"),
        cmd(101, "Actor2", 1, 0, 2, ""),              # MV kieu: ten o dong dau
        cmd(401, "【ボブ】"),
        cmd(401, long_line),
        cmd(401, long_line),
        cmd(401, long_line),
        cmd(102, ["はい", "いいえ"], 1, 0, 2, 0),
        cmd(402, 0, "はい"),
        cmd(101, "", 0, 0, 2, ""),
        cmd(401, "ポーションを持ってる？"),              # trung lap -> TM/dedupe
        cmd(0),
    ]
    (data / "Map001.json").write_text(json.dumps({"events": [None, {"id": 1, "name": "EV001",
                                      "pages": [{"list": ev_list}]}]}, ensure_ascii=False), "utf-8")
    (data / "CommonEvents.json").write_text("[null]", "utf-8")
    (data / "Actors.json").write_text(json.dumps([None, {"name": "アリス", "nickname": "",
                                      "profile": "元気な少女。"}], ensure_ascii=False), "utf-8")
    (data / "Items.json").write_text(json.dumps([None, {"name": "ポーション",
                                     "description": "HPを\\V[1]回復する。"}], ensure_ascii=False), "utf-8")
    (data / "System.json").write_text(json.dumps({"gameTitle": "テスト", "elements": ["", "炎"],
                                      "terms": {"basic": ["レベル"], "commands": ["戦う"],
                                                "params": [], "messages": {"victory": "%1の勝利！"}}},
                                                 ensure_ascii=False), "utf-8")
    return root / "game"


class TestCore(unittest.TestCase):
    def test_mask_roundtrip(self):
        s = "こんにちは\\C[2]ボブ\\C[0]、%1と<color=red>{0}</color>\\!"
        m, codes = mask(s)
        self.assertNotIn("\\C", m)
        self.assertEqual(unmask(m, codes), s)

    def test_fit_keeps_name_line_and_wraps(self):
        lines = fit_message("【Bob】\n" + "xin chào " * 20, 30, True)
        self.assertEqual(lines[0], "【Bob】")
        self.assertTrue(all(len(x) <= 30 for x in lines))
        # Ten tieng Viet dai (25 ky tu) van phai giu la dong ten rieng.
        name = "\\C[3]Quản lý nhiệm vụ cao cấp\\C[0]:"
        self.assertEqual(fit_message(name + "\nxin chào", 44, True)[0], name)

    def test_fit_no_space_around_codes_and_keeps_hard_breaks(self):
        # Cursed Armor: wrap cu chen khoang trang sau ma (\C[4] G) va gop mat xuong dong co chu y.
        t = "Chúc mừng bạn đã hoàn thành nhiệm vụ!\nNhận được: 100 \\C[4]G\\C[0] 50\\C[4]EXP\\C[0]"
        self.assertEqual(fit_message(t, 44, False),
                         ["Chúc mừng bạn đã hoàn thành nhiệm vụ!",
                          "Nhận được: 100 \\C[4]G\\C[0] 50\\C[4]EXP\\C[0]"])
        lines = fit_message("Do dâm năng tăng lên, \\C[5]Gông xiềng nguyền rủa\\C[0] xuất hiện trên"
                            "\nngười \\C[6]\\N[1]\\C[0]……", 44, False)
        self.assertIn("\\C[5]Gông", " ".join(lines))
        self.assertTrue(" ".join(lines).endswith("\\C[6]\\N[1]\\C[0]……"))
        # Dong tieu de ket bang ma mau phai giu xuong dong.
        lines = fit_message("Ám thị - \\C[5]Lộ thân ngoài trời\\C[0]\nDùng ma pháp hệ Ánh sáng", 44, False)
        self.assertEqual(lines[0], "Ám thị - \\C[5]Lộ thân ngoài trời\\C[0]")
        # Dong dai bi ngat giua cau van duoc gop.
        lines = fit_message("Do dâm năng tăng lên, gông xiềng nguyền rủa xuất hiện\ntrên người cô", 44, False)
        self.assertEqual(lines, ["Do dâm năng tăng lên, gông xiềng nguyền rủa",
                                 "xuất hiện trên người cô"])

    def test_ui_too_long_warn(self):
        # zh -> vi dai ~4 lan; RPG Maker co chu theo maxWidth nen co the chi canh bao.
        from vgt import qa
        from vgt.store import Entry
        cfg = load_config()
        e = Entry(id="x", file="f", locator={}, grp="g", seq=0, kind="name", source="時崎狂三的頭飾")
        bidx = biblemod.BibleIndex({})
        out = "Trang sức đầu của Tokisaki Kurumi"
        self.assertTrue(qa.blocking(qa.check(e, e.source, out, out, bidx, cfg, "zh")))
        cfg["qa"]["ui_too_long"] = "warn"
        self.assertFalse(qa.blocking(qa.check(e, e.source, out, out, bidx, cfg, "zh")))

    def test_stray_backslash_before_cjk(self):
        # Cursed Armor: `\C[5]\精液寶瓶` -> dich thanh `\Bảo` = ma \B nuot chu.
        from vgt import qa
        from vgt.protect import mask
        from vgt.store import Entry
        m, codes = mask("獲得\\C[5]\\精液寶瓶\\C[0]！")
        self.assertEqual(m, "獲得⟦0⟧精液寶瓶⟦1⟧！")
        cfg = load_config()
        e = Entry(id="x", file="f", locator={}, grp="g", seq=0, kind="dialogue",
                  source="獲得\\C[5]\\精液寶瓶\\C[0]！")
        bad = "Nhận \\C[5]\\Bảo bình\\C[0]!"
        self.assertTrue(qa.blocking(qa.check(e, m, "Nhận ⟦0⟧\\Bảo bình⟦1⟧!", bad,
                                             biblemod.BibleIndex({}), cfg, "zh")))

    def test_bare_code_before_latin_letter(self):
        from vgt.protect import mask, unmask
        m, codes = mask("\\S原來是\\C[6]夫人\\C[0]啊 50%")
        self.assertEqual(unmask("⟦0⟧Thì ra là ⟦1⟧phu nhân⟦2⟧ à 50%", codes),
                         "\\S Thì ra là \\C[6]phu nhân\\C[0] à 50%")

    def test_norm_punct_fullwidth(self):
        # Cursed Armor: 167 dau '：' '？' sot lai du prompt da dan doi.
        from vgt.textfit import norm_punct
        self.assertEqual(norm_punct("\\C[6]\\N[1]\\C[0]：\n？？？～（a）！，"), "\\C[6]\\N[1]\\C[0]:\n???~(a)!,")

    def test_long_name_line_fits_box_width(self):
        # Cursed Armor: ten 36 ky tu > NAME_MAX nhung vua khung 44 -> khong bat dich lai.
        from vgt import qa
        from vgt.store import Entry
        cfg = load_config()
        cfg["qa"]["max_line_chars"] = 44
        e = Entry(id="x", file="f", locator={"name_line": True}, grp="g", seq=0, kind="dialogue",
                  source="\\C[3]偽裝成平民的雇傭兵A\\C[0]：\n給我走快點！")
        bidx = biblemod.BibleIndex({})
        out = "\\C[3]Lính đánh thuê A giả dạng dân thường\\C[0]:\nĐi nhanh lên!"
        self.assertFalse(qa.blocking(qa.check(e, e.source, out, out, bidx, cfg, "zh")))
        out = "\\C[3]Lính đánh thuê A giả dạng dân thường\\C[0]: Đi nhanh lên!"
        self.assertTrue(qa.blocking(qa.check(e, e.source, out, out, bidx, cfg, "zh")))

    def test_glossary_split_and_longest(self):
        # Bible do Opus soan ghi gop "A / B" va "(\N[59])"; tu ngan nam trong tu dai thi bo.
        g = [{"src": "詛咒鎧甲 / 詛咒的鎧甲", "vi": "Bộ giáp nguyền rủa"},
             {"src": "賤奴 (\\N[59])", "vi": "tiện nô"},
             {"src": "浴場", "vi": "nhà tắm công cộng"},
             {"src": "老板 / 浴場老板", "vi": "ông chủ / ông chủ nhà tắm"}]
        hits = {s: vis for _, s, vis in biblemod.glossary_hits(g, "詛咒的鎧甲和浴場老板，賤奴")}
        self.assertEqual(hits, {"詛咒的鎧甲": ["Bộ giáp nguyền rủa"], "賤奴": ["tiện nô"],
                                "浴場老板": ["ông chủ nhà tắm"]})

    def test_colored_name_line_speaker(self):
        # Cursed Armor: dong ten `\C[6]\N[1]\C[0]：` (co ma mau) phai nhan ra nguoi noi.
        from vgt.adapters.rpgmaker_mvmz import RpgMakerMVMZ
        cmds = [cmd(101, "Face1", 0, 0, 2), cmd(401, "\\C[6]\\N[1]\\C[0]："), cmd(401, "門被鎖死了"),
                cmd(101, "", 0, 0, 2), cmd(401, "\\C[2]傭兵\\C[0]："), cmd(401, "站住！"),
                cmd(101, "", 0, 0, 2), cmd(401, "是否需要跳過重復H？"), cmd(401, "……")]
        out = []
        RpgMakerMVMZ._scan_list(cmds, ["list"], "data/Map001.json", "g", out, {1: "莉莉娜"})
        self.assertEqual([e.speaker for e in out], ["莉莉娜", "傭兵", None])
        self.assertEqual([e.locator["name_line"] for e in out], [True, True, False])


def tmpdir(case: unittest.TestCase) -> Path:
    """Thu muc tam tu xoa sau test (dong sqlite truoc, Windows khong xoa file dang mo)."""
    d = Path(tempfile.mkdtemp())
    case.addCleanup(shutil.rmtree, d, True)
    case.addCleanup(gc.collect)
    return d


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir(self)
        self.game = make_game(self.tmp)
        self.logs = []
        self.p = Project.init(self.game, self.tmp / "proj", log=self.logs.append)
        self.p.log = self.logs.append
        self.addCleanup(lambda: self.p.store.db.close())

    def test_end_to_end_mock(self):
        p = self.p
        p.extract()
        self.assertEqual(p.store.get_meta("source_lang"), "ja")
        es = {e.id: e for e in p.store.entries()}
        a = es["Map001.json:ev1p0@0"]
        self.assertEqual(a.speaker, "アリス")
        self.assertEqual(es["Map001.json:ev1p0@3"].speaker, "【ボブ】")

        p.draft_bible("mock")
        b = biblemod.load(p.path)
        self.assertFalse(b["reviewed"])
        with self.assertRaises(SystemExit):
            p.translate("mock")
        b["reviewed"] = True
        b["glossary"] = [{"src": "ポーション", "vi": "VI: ポーション"}]
        biblemod.save(p.path, b)

        p.translate("mock")
        c = p.store.counts()
        self.assertNotIn("new", c)
        # Mock khong dich that -> con chu Nhat -> QA bat loi, het luot thu.
        self.assertIn("qa_fail", c)
        tr = [u for u in p.store.usage_summary() if u["purpose"] == "translate"]
        self.assertTrue(tr)

        # Gia lap ban sua tay roi apply.
        for e in p.store.entries():
            e.target = "Xin chào " * 12 if e.kind == "dialogue" else "Mục"
            e.status, e.qa = "manual", []
            p.store.save_result(e)
        out = p.apply()
        doc = json.loads((out / "_viethoa" / "files" / "data" / "Map001.json").read_text("utf-8"))
        lst = doc["events"][1]["pages"][0]["list"]
        codes = [c["code"] for c in lst]
        self.assertEqual(codes.count(102), 1)
        self.assertGreaterEqual(codes.count(101), 3)
        self.assertTrue(all(len(c["parameters"][0]) <= 48 for c in lst if c["code"] == 401))
        # Game goc khong bi sua.
        orig = json.loads((self.game / "data" / "Map001.json").read_text("utf-8"))
        self.assertEqual(orig["events"][1]["pages"][0]["list"][1]["parameters"][0],
                         "こんにちは、\\C[2]ボブ\\C[0]さん。")

    def test_apply_font_override(self):
        p = self.p
        p.extract()
        font = self.tmp / "vn.ttf"
        font.write_bytes(b"fake")
        p.cfg["rpgmaker"]["font_file"] = str(font)
        out = p.apply()
        self.assertEqual((out / "_viethoa" / "files" / "fonts" / "vn.ttf").read_bytes(), b"fake")
        self.assertIn('url("vn.ttf")', (out / "_viethoa" / "files" / "fonts" / "gamefont.css").read_text("utf-8"))
        # Cursed Armor: arial.ttf trung metric sans-serif -> MV "Failed to load GameFont".
        arial = self.tmp / "arial.ttf"
        arial.write_bytes(b"fake")
        p.cfg["rpgmaker"]["font_file"] = str(arial)
        with self.assertRaises(SystemExit):
            p.apply()

    def test_js_table_roundtrip(self):
        # Cursed Armor: chu UI cung trong plugin (var wolfzqText = {...}); bang EN phia sau khong dong.
        js = self.game / "js" / "plugins" / "T.js"
        js.parent.mkdir(parents=True)
        js.write_text("var t = {\n\t'version': '2.60', 'a': '重登陸','p19': '（被\\\\W[4]破處）',\n};\n"
                      "var tEN = {'a': 'Relogin'};\n", "utf-8")
        p = self.p
        p.cfg["rpgmaker"]["js_tables"] = [{"file": "js/plugins/T.js", "start": "var t = {"}]
        p.extract()
        es = {e.id: e for e in p.store.entries() if e.file.endswith(".js")}
        self.assertEqual(sorted(es), ["js/plugins/T.js:a", "js/plugins/T.js:p19"])
        self.assertEqual(es["js/plugins/T.js:p19"].source, "（被\\W[4]破處）")
        for e, v in ((es["js/plugins/T.js:a"], "Đăng nhập lại"),
                     (es["js/plugins/T.js:p19"], "(bị \\W[4] phá trinh, 'x')")):
            e.target, e.status = v, "manual"
            p.store.save_result(e)
        out = p.apply()
        txt = (out / "_viethoa" / "files" / "js" / "plugins" / "T.js").read_text("utf-8")
        self.assertIn("'a': 'Đăng nhập lại'", txt)
        self.assertIn("'p19': '(bị \\\\W[4] phá trinh, \\'x\\')'", txt)
        self.assertIn("'version': '2.60'", txt)
        self.assertIn("var tEN = {'a': 'Relogin'}", txt)

    def test_js_replace_count(self):
        # Cursed Armor: ep game luon nap data tieng Viet du save chon ngon ngu EN (P-004).
        js = self.game / "js" / "plugins" / "Z.js"
        js.parent.mkdir(parents=True)
        js.write_text('a="data"+L("language");b=eval("t"+L("language"))', "utf-8")
        p = self.p
        p.extract()
        rule = {"file": "js/plugins/Z.js", "find": 'L("language")', "replace": '""', "count": 2}
        p.cfg["rpgmaker"]["js_replace"] = [rule]
        out = p.apply()
        self.assertEqual((out / "_viethoa" / "files" / "js" / "plugins" / "Z.js").read_text("utf-8"),
                         'a="data"+"";b=eval("t"+"")')
        rule["count"] = 3
        with self.assertRaises(SystemExit):
            p.apply()

    def test_patch_only_changed_files_no_game_copy(self):
        # Khong chep ca game (game 100 GB): patch chi co file da dich + CAI/GO_VIETHOA.
        p = self.p
        p.extract()
        (self.game / "big.bin").write_bytes(b"x" * 1000)
        for e in p.store.entries():
            if e.file.endswith("Items.json"):
                e.target, e.status = "Thuốc", "manual"
                p.store.save_result(e)
        out = p.apply()
        self.assertEqual(out, p.path / "patch")
        # patch.dir tuong doi -> tinh tu repo (Translation/<ten game>); init --name ghi san.
        p2 = Project.init(self.game, self.tmp / "proj2", name="Ten Game", log=self.logs.append)
        self.assertEqual(p2.patch_dir, Path(__file__).resolve().parents[1].parent / "Ten Game")
        # Nguoi dung chi thay CAI/GO_VIETHOA.bat; con lai trong _viethoa (an).
        names = sorted(x.name for x in out.iterdir())
        self.assertEqual(names, ["CAI_VIETHOA.bat", "GO_VIETHOA.bat", "_viethoa"])
        fd = out / "_viethoa" / "files"
        files = [x.relative_to(fd).as_posix() for x in fd.rglob("*") if x.is_file()]
        self.assertEqual(files, ["data/Items.json"])
        mf = json.loads((out / "_viethoa" / "vgt_patch.json").read_text("utf-8"))
        self.assertEqual(mf["files"][0]["path"], "data/Items.json")
        self.assertIsNotNone(mf["files"][0]["orig"])
        self.assertNotEqual(mf["files"][0]["orig"], mf["files"][0]["new"])
        self.assertIn(b"\r\n", (out / "CAI_VIETHOA.bat").read_bytes())

    @unittest.skipUnless(sys.platform == "win32", "can PowerShell tren Windows")
    def test_patch_install_uninstall_roundtrip(self):
        import shutil
        import subprocess
        from vgt.patch import sha256
        p = self.p
        font = self.tmp / "vn.ttf"
        font.write_bytes(b"fake")
        p.cfg["rpgmaker"]["font_file"] = str(font)  # file moi (khong co trong game) -> go phai xoa
        p.extract()
        for e in p.store.entries():
            e.target, e.status = "Mục", "manual"
            p.store.save_result(e)
        out = p.apply()
        # Duong dan co [ ] va dau cach nhu thu muc game that.
        game = self.tmp / "[Hentai] x" / "My Game"
        shutil.copytree(self.game, game)
        before = {f.relative_to(game).as_posix(): sha256(f) for f in game.rglob("*") if f.is_file()}

        def run(mode):
            r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                str(out / "_viethoa" / "vgt_patch.ps1"), "-Mode", mode, "-Game", str(game), "-NoPrompt"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        run("install")
        self.assertEqual(sha256(game / "data" / "Items.json"), sha256(out / "_viethoa" / "files" / "data" / "Items.json"))
        self.assertTrue((game / "fonts" / "vn.ttf").exists())
        self.assertTrue((out / "_viethoa" / "_backup").exists())
        # Build lai tu game da cai = lay ban dich lam goc (G-004) -> chan.
        p.game = game
        with self.assertRaises(SystemExit):
            p.apply()
        run("uninstall")
        after = {f.relative_to(game).as_posix(): sha256(f) for f in game.rglob("*") if f.is_file()}
        self.assertEqual(after, before)
        self.assertFalse((out / "_viethoa" / "_backup").exists())

    def test_tm_reuse_no_calls(self):
        p = self.p
        p.extract()
        for e in p.store.entries():
            e.target, e.status = "x", "manual"
            p.store.save_result(e)
        p.store.db.execute("UPDATE entries SET status='new', target=NULL")
        p.store.db.commit()
        b = {"reviewed": True}
        biblemod.save(p.path, b)
        p.translate("mock")
        self.assertEqual(p.store.counts(), {"tm": len(p.store.entries())})
        self.assertFalse(p.store.usage_summary())


class TestClaudeBackend(unittest.TestCase):
    def _fake(self, tmp: Path, payload: dict, code=0) -> str:
        f = tmp / "fakeclaude"
        f.write_text(f"#!/bin/sh\ncat >/dev/null\necho '{json.dumps(payload)}'\nexit {code}\n")
        f.chmod(f.stat().st_mode | stat.S_IEXEC)
        return str(f)

    def test_workdir_absolute(self):
        # Windows: workdir tuong doi + cwd=workdir -> "System prompt file not found" (duong dan nhan doi).
        tmp = tmpdir(self)
        old = os.getcwd()
        os.chdir(tmp)
        try:
            be = ClaudeCodeBackend(load_config(), Path("proj") / ".claude_work")
            self.assertTrue(be.workdir.is_absolute())
        finally:
            os.chdir(old)

    @unittest.skipIf(os.name == "nt", "fake exe dung sh")
    def test_parse_and_limit(self):
        tmp = tmpdir(self)
        cfg = load_config()
        cfg["claude"]["executable"] = self._fake(tmp, {"is_error": False, "structured_output":
                                                       {"t": [{"id": "0", "v": "ok"}]},
                                                       "usage": {"input_tokens": 5}})
        be = ClaudeCodeBackend(cfg, tmp / "w")
        r = be.call("sys", "#JSON\n{}", {"type": "object"}, "sonnet")
        self.assertEqual(r["data"]["t"][0]["v"], "ok")
        cmdline = be._cmd("sonnet", {}, tmp / "s.txt")
        for flag in ("--system-prompt-file", "--tools", "--strict-mcp-config", "--json-schema"):
            self.assertIn(flag, cmdline)
        self.assertNotIn("--bare", cmdline)

        cfg["claude"]["executable"] = self._fake(tmp, {"is_error": True,
                                                       "result": "Claude usage limit reached. Resets 3pm"}, 1)
        cfg["claude"]["wait_on_limit"] = False
        with self.assertRaises(LimitReached):
            ClaudeCodeBackend(cfg, tmp / "w").call("sys", "x", {"type": "object"}, "sonnet")

    def test_network_error_retried(self):
        """Loi mang tam thoi (ENOTFOUND, gap khi chay bible that 31/10) phai thu lai, khong chet."""
        import subprocess as sp
        from unittest import mock
        from vgt.backend import BackendError
        tmp = tmpdir(self)
        cfg = load_config()
        cfg["claude"]["network_wait_sec"] = 0
        cfg["claude"]["network_retries"] = 2
        bad = sp.CompletedProcess([], 1, json.dumps({"is_error": True, "result":
                                  "API Error: Can't reach the API server (ENOTFOUND)"}), "")
        good = sp.CompletedProcess([], 0, json.dumps({"is_error": False,
                                   "structured_output": {"t": []}}), "")
        be = ClaudeCodeBackend(cfg, tmp / "w", log=lambda *a: None)
        with mock.patch("vgt.backend.subprocess.run", side_effect=[bad, good]) as m:
            self.assertEqual(be.call("sys", "x", {"type": "object"}, "sonnet")["data"], {"t": []})
            self.assertEqual(m.call_count, 2)
        with mock.patch("vgt.backend.subprocess.run", side_effect=[bad, bad, bad]):
            with self.assertRaises(BackendError):
                be.call("sys", "x", {"type": "object"}, "sonnet")


if __name__ == "__main__":
    unittest.main()
