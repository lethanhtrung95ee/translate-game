#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tu kiem bo cong cu VGK (vgk.py, rpgmv_adapter.py, adapters/kv) tren game gia lap trong thu muc tam.
Chay: python3 selftest.py  -> "SELFTEST: N/N đạt", exit 0 khi moi kiem tra deu dat.
Chi ghi vao thu muc tam cua he thong; khong tao tep nao canh cac script."""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ok = fail = 0


def run(args, cwd, stdin=None):
    r = subprocess.run([sys.executable] + args, cwd=cwd, input=stdin, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


def check(name, cond, out=""):
    global ok, fail
    if cond:
        ok += 1
    else:
        fail += 1
        print(f"HỎNG: {name}\n{str(out)[-1800:]}\n")


def jl(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def setcfg(w, **kw):
    path = os.path.join(w, "game.json")
    cfg = json.load(open(path, encoding="utf-8"))
    cfg.update(kw)
    json.dump(cfg, open(path, "w", encoding="utf-8"), ensure_ascii=False)


def test_core(tmp, v):
    w = os.path.join(tmp, "Viet hoa game", "thu")
    os.makedirs(w)
    rc, out = run([v, "init", "--name", "Thử", "--kind", "18", "--lang", "jp"], w)
    check("init từ chối --lang jp", rc != 0 and "dùng 'ja'" in out, out)
    rc, out = run([v, "init", "--name", "Thử", "--kind", "18", "--lang", "ja"], w)
    check("init", rc == 0 and os.path.exists(os.path.join(w, "HANDOFF.md"))
          and os.path.exists(os.path.join(os.path.dirname(v), "KINH_NGHIEM.md")), out)
    setcfg(w, batch_dialogue=4, skip_patterns=[r"^\[TEMP\]"], max_len={"ui": 12, "file:Menu*": 6})
    rows = [
        {"id": "u1", "src": "はじめから", "kind": "ui"},
        {"id": "u2", "src": "はじめから", "kind": "ui"},
        {"id": "u3", "src": "所持金：%d G", "kind": "ui"},
        {"id": "u4", "src": "[TEMP]未使用", "kind": "ui"},
        {"id": "u5", "src": "……", "kind": "ui"},
        {"id": "m1", "src": "設定", "kind": "ui", "file": "data/Menu.json"},
        {"id": "i1", "src": "ポーション", "kind": "data", "file": "Items"},
        {"id": "k1", "src": "カイルの固有スキル", "kind": "data", "file": "Skills"},
        {"id": "k2", "src": "ゼノの固有スキル", "kind": "data", "file": "Skills"},
        {"id": "d1", "src": "\\C[3]ミラ\\C[0]、何してるんだ？", "en": "Mira, what?", "speaker": "カイル", "scene": "s1"},
        {"id": "d2", "src": "遅いよ！", "speaker": "ミラ", "scene": "s1"},
        {"id": "d3", "src": "遅いよ！", "speaker": "ミラ", "scene": "s1"},
        {"id": "d3b", "src": "遅いよ！", "speaker": "ミラ", "scene": "s9"},
        {"id": "d4", "src": "世島だ。", "speaker": "世島", "scene": "s2"},
        {"id": "d5", "src": "（秘密）", "en": "(secret)", "speaker": "ミラ", "scene": "s2"},
        {"id": "d6", "src": "魔導具の話だ。", "speaker": "世島", "scene": "s2"},
        {"id": "d7", "src": "（秘密）", "en": "(secret)", "speaker": "ミラ", "scene": "s2"},
        {"id": "d8", "src": "プレイヤーだ。", "speaker": 7, "scene": 3},
        {"id": "d9", "src": "剣で探す。", "speaker": "カイル", "scene": "s2"},
        {"id": "d10", "src": "ヴェラとヴェラ港へ。", "speaker": "カイル", "scene": "s2"},
        {"id": "d11", "src": "テスト\n", "speaker": "カイル", "scene": "s2"},
    ]
    open(os.path.join(w, "src.jsonl"), "w", encoding="utf-8").write(jl(rows))
    open(os.path.join(w, "t.tsv"), "w", encoding="utf-8").write(
        "src\tvi\ttype\tnote\tforbid\nカイル\tKael\tnhan_vat\t\t\nミラ\tMira\tnhan_vat\t\t\n世島\tSejima\tnhan_vat\t\tSo\n"
        "ポーション\tThuốc hồi phục\tvat_pham\t\t\n魔導具\tpháp cụ\tkhai_niem\t\t\n魔導\tma đạo\tkhai_niem\t\tpháp\n"
        "レイ\tRei\tnhan_vat\t\t\n剣\tkiếm\tvat_pham\t\t\nヴェラ\tVera\tdia_danh\t\t\nヴェラ港\tCảng Vera\tdia_danh\t\t\n"
        "カイル\tKhải\tnhan_vat\tlặp\t\n")
    rc, out = run([v, "term", "import", "t.tsv"], w)
    check("term import + lặp trong tệp", "+10" in out and "lặp trong cùng lần nhập" in out, out)
    rc, out = run([v, "plan"], w)
    check("plan: tự động, trùng theo cảnh, kiểu dữ liệu lạ được đổi thành chuỗi",
          rc == 0 and "tự động 2" in out and "trùng (dịch 1 lần) 3" in out and "cần dịch 16 (thoại 10, ngắn 6)" in out, out)
    rc, out = run([v, "fill", "--apply"], w)
    check("fill", "Ghi: 1/1" in out, out)
    rc, out = run([v, "bulk", "--match", "(.+)の固有スキル", "--to", "Kỹ năng riêng của ${1|g}", "--apply"], w)
    check("bulk ${1|g} + thiếu thuật ngữ", "tạo được 1" in out and "ゼノ×1" in out, out)
    pay = "@@term ゼノ | Zeno | nhan_vat\n@@u1\nChơi mới\n@@ u3\nTiền: G\n@@ k2\nKỹ năng của ゼノ\n@@ zz\nx\n@@ m1\nCài đặt hệ thống\n"
    rc, out = run([v, "write", "-"], w, pay)
    check("write: lỗi từng mục, id không cách, max_len theo tên tệp", rc == 2 and "u3: mã/thẻ lệch" in out
          and "k2: còn chữ/dấu gốc" in out and "zz: id không có" in out and "Ghi: 2/5" in out and "quá dài" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ u3\nTiền: %d G\n@@ k2\nKỹ năng riêng của Zeno\n")
    check("write sửa", rc == 0 and "Ghi: 2/2" in out and "lô 1 xong" in out, out)
    rc, out = run([v, "next"], w)
    check("next: mã tắt, dòng gốc #>, ×N, không lặp câu trùng", "@@ ~2.1 · カイル" in out and "#> \\C[3]ミラ" in out
          and "×2" in out and "CHƯA CÓ TÓM TẮT" in out and out.count("#> 遅いよ") == 2 and "#> Ghi:" in out, out)
    pay = ("@@scene s1 !\nKael gặp Mira.\n@@pair Kael | Mira | tớ | cậu\n@@pair カイル | ミラ | tớ | cậu\n"
           "@@pair ミラ | カイル | tớ | cậu\n@@voice ミラ | lanh lợi | Trễ quá nha!\n"
           "@@ ~2.1\nMira, gì vậy?\n#> dòng chép từ next bị bỏ qua\n@@ ~2.2\nTôi đợi lâu rồi!\n")
    rc, out = run([v, "write", "-"], w, pay)
    check("ghi bằng mã tắt + cảnh báo tên dịch trong @@pair", rc == 2 and "thiếu \\C[3], \\C[0]" in out
          and "'Kael' không có trong src.jsonl" in out and "xưng hô +3" in out and "Ghi: 1/2" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ ~2.1\n\\C[3]Mira\\C[0], gì vậy?\n")
    check("mã tắt sửa", rc == 0, out)
    tr = [json.loads(x) for x in open(os.path.join(w, "tr.jsonl"), encoding="utf-8")]
    check("#> không lọt vào bản dịch", all("#>" not in t["vi"] for t in tr), tr)
    rc, out = run([v, "minor", "add", "d5", "--note", "thử"], w)
    check("minor add theo id", "thêm 1" in out and "Chỉ đúng các id này" in out, out)
    ids = {}
    outs = ""
    for bn in ("2", "3"):
        rc, out = run([v, "next", "--batch", bn], w)
        outs += out
        L = out.split("\n")
        for n, ln in enumerate(L):
            if ln.startswith("@@ ~"):
                ids[ln.split()[1]] = L[n + 1][3:]
    check("minor không lan sang câu trùng (d7 vẫn cần dịch)", "#> （秘密）" in outs and "@@ ~2.1" not in outs.split("LÔ 3")[0]
          or "#> （秘密）" in outs, outs)
    pay = "@@scene s2\nGặp Sejima.\n@@pair 世島 | カイル | ta | cậu\n"
    for k, s in ids.items():
        vi = {"遅いよ！": "Trễ quá à!", "世島だ。": "Ta là So.", "（秘密）": "(bí mật)", "魔導具の話だ。": "Chuyện pháp cụ.", "プレイヤーだ。": "Người chơi đây.",
              "剣で探す。": "Dùng kiếm để tìm kiếm.", "ヴェラとヴェラ港へ。": "Tới Vera và Cảng Vera.", "テスト": "Thử"}.get(s, "?")
        pay += f"@@ {k}\n{vi}\n"
    rc, out = run([v, "write", "-"], w, pay)
    check("thuật ngữ cấm + so dài nhất (魔導 không bắt 魔導具) + katakana biên",
          "thuật ngữ cấm: 'So'" in out and "pháp' → dùng 'ma đạo'" not in out and "'Rei'" not in out and "?" not in pay, out + pay)
    k4 = [k for k, s in ids.items() if s == "世島だ。"][0]
    rc, out = run([v, "write", "-", "--force", k4], w, f"@@ {k4}\nTa là So.\n")
    check("--force bỏ qua thuật ngữ cấm", rc == 0, out)
    run([v, "write", "-"], w, f"@@ {k4}\nTa là Sejima.\n")
    run([v, "write", "-"], w, "@@scene s9\nCảnh khác.\n@@scene 3\nCảnh số.\n")
    tr = {}
    for x in open(os.path.join(w, "tr.jsonl"), encoding="utf-8"):
        t = json.loads(x)
        tr[t["id"]] = t["vi"]
    check("giữ xuống dòng cuối của gốc", tr.get("d11") == "Thử\n", tr.get("d11"))
    rc, out = run([v, "status"], w)
    check("status 100%", "(100,0%)" in out and "giữ nguyên (vị thành niên) 1" in out, out)
    rc, out = run([v, "check"], w)
    check("check: 0 lỗi chặn + tự xưng lệch bảng", rc == 0 and "LỖI CHẶN: 0" in out and "tự xưng khác bảng xưng hô" in out, out)
    rc, out = run([v, "term", "change", "剣", "gươm", "--apply"], w)
    tr2 = {}
    for x in open(os.path.join(w, "tr.jsonl"), encoding="utf-8"):
        t = json.loads(x)
        tr2[t["id"]] = t["vi"]
    gl = open(os.path.join(w, "glossary.tsv"), encoding="utf-8").read()
    check("term change từ đơn: không tự sửa, không cấm, liệt kê sửa tay",
          "tự sửa 0" in out and "sửa tay 1" in out and tr2["d9"] == "Dùng kiếm để tìm kiếm." and "剣\tgươm\tvat_pham\t\t\t\n" in gl, out)
    rc, out = run([v, "term", "change", "ヴェラ", "Vila", "--apply"], w)
    tr3 = {}
    for x in open(os.path.join(w, "tr.jsonl"), encoding="utf-8"):
        t = json.loads(x)
        tr3[t["id"]] = t["vi"]
    gl = open(os.path.join(w, "glossary.tsv"), encoding="utf-8").read()
    check("term change tên riêng: che 'Cảng Vera', chỉ đổi đúng chỗ, cấm nghĩa cũ",
          tr3["d10"] == "Tới Vila và Cảng Vera." and "ヴェラ\tVila\tdia_danh\t\tVera" in gl, out + tr3["d10"])
    rc, out = run([v, "export"], w)
    exp = json.load(open(os.path.join(w, "export.json"), encoding="utf-8"))
    check("export: minor theo id, câu trùng, tự động", rc == 0 and exp["u2"] == "Chơi mới" and exp["d3"] == "Tôi đợi lâu rồi!"
          and exp["d5"] == "(secret)" and exp["d7"] == "(bí mật)" and exp["u5"] == "…" and exp["d3b"] == "Trễ quá à!", out)
    rc, out = run([v, "export", "--identity", "--out", "id.json"], w)
    ide = json.load(open(os.path.join(w, "id.json"), encoding="utf-8"))
    check("export identity", ide["d1"] == rows[9]["src"], out)
    rc, out = run([v, "review", "--n", "3", "--uu-tien"], w)
    check("review", "#> " in out and rc == 0, out)
    rc, out = run([v, "show", "--around", "d2", "--n", "1", "--vi"], w)
    check("show", "d2 · ミラ" in out and "= Tôi đợi lâu rồi!" in out, out)
    hand = open(os.path.join(w, "HANDOFF.md"), encoding="utf-8").read()
    check("HANDOFF tự cập nhật", "vgk:trang-thai" in hand and "100,0%" in hand, hand)
    # gốc đổi + plan lại giữ bản dịch + mã tắt cũ bị từ chối
    rc0, out0 = run([v, "next", "--batch", "2", "--all"], w)
    rows2 = [dict(r) for r in rows]
    rows2[9]["src"] = "\\C[3]ミラ\\C[0]、何をしているんだ？"
    rows2.insert(0, {"id": "u0", "src": "はじめから", "kind": "ui"})
    open(os.path.join(w, "src.jsonl"), "w", encoding="utf-8").write(jl(rows2))
    rc, out = run([v, "status"], w)
    check("gốc đổi → đưa lại vào lô; plan lại giữ bản dịch nhóm trùng",
          "gốc đã đổi cần dịch lại 1" in out and "đã chia lại lô" in out, out)
    rc, out = run([v, "export", "--allow-missing"], w)
    exp = json.load(open(os.path.join(w, "export.json"), encoding="utf-8"))
    check("plan lại: câu trùng mới dùng bản dịch sẵn có", exp["u0"] == "Chơi mới", out)
    rc, out = run([v, "write", "-"], w, "@@ ~2.1\nx\n")
    check("mã tắt cũ sau khi chia lại lô bị từ chối", rc == 2 and "không hiểu mã tắt" in out, out)
    rc, out = run([v, "check"], w)
    check("check báo gốc đã đổi", rc == 1 and "gốc đã đổi, cần dịch lại" in out, out)
    # bộ cài
    pd = os.path.join(w, "patch", "p0")
    os.makedirs(os.path.join(pd, "files", "data"))
    open(os.path.join(pd, "files", "data", "A.json"), "w").write("{}")
    open(os.path.join(pd, "files", "data", "New.json"), "w").write("{}")
    g = os.path.join(tmp, "G")
    os.makedirs(os.path.join(g, "data"))
    open(os.path.join(g, "data", "A.json"), "w").write("{}")
    rc, out = run([v, "patchkit", pd, "--game", g, "--game-win", "C:\\Games\\G!"], w)
    bat = open(os.path.join(pd, "CAI_VIETHOA.bat"), "rb").read()
    new = open(os.path.join(pd, "them_moi.txt"), encoding="utf-8").read()
    check("patchkit: bat CRLF, them_moi, game_path", rc == 0 and b"\r\n" in bat and b"EnableDelayedExpansion" not in bat
          and new.strip() == "data/New.json" and os.path.exists(os.path.join(pd, "game_path.txt")), out)
    # src không hợp lệ
    open(os.path.join(w, "src.jsonl"), "a", encoding="utf-8").write(jl([{"id": "x1", "src": "a", "kind": "dialog"}]))
    rc, out = run([v, "status"], w)
    check("src: kind sai bị chặn", rc != 0 and "kind 'dialog'" in out, out)


def mz_game(g, mv=False):
    d = os.path.join(g, "www", "data") if mv else os.path.join(g, "data")
    os.makedirs(d)
    js = os.path.join(g, "www", "js") if mv else os.path.join(g, "js")
    os.makedirs(js)
    open(os.path.join(js, "rpg_core.js" if mv else "rmmz_core.js"), "w").close()

    def w(n, o):
        open(os.path.join(d, n), "w", encoding="utf-8").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))
    w("System.json", {"gameTitle": "勇者の旅", "currencyUnit": "G", "elements": ["", "炎"], "skillTypes": [""], "weaponTypes": [""],
                      "armorTypes": [""], "equipTypes": [""], "terms": {"basic": ["レベル"], "commands": ["戦う", None],
                      "params": [], "messages": {"actionFailure": "%1には効かなかった！"}}, "advanced": {"screenWidth": 816, "fontSize": 26}})
    w("Actors.json", [None, {"id": 1, "name": "カイル", "nickname": "", "profile": ""}])
    if mv:
        lst = [{"code": 101, "indent": 0, "parameters": ["Actor1", 0, 0, 2]},
               {"code": 401, "indent": 0, "parameters": ["【カイル】"]},
               {"code": 401, "indent": 0, "parameters": ["\\C[3]ミラ\\C[0]、ここで何してるんだ？"]},
               {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2]},
               {"code": 401, "indent": 0, "parameters": ["\\n<ミラ>うん！"]},
               {"code": 0, "indent": 0, "parameters": []}]
    else:
        lst = [{"code": 101, "indent": 0, "parameters": ["Actor1", 0, 0, 2, "カイル"]},
               {"code": 401, "indent": 0, "parameters": ["\\C[3]ミラ\\C[0]、ここで何してるんだ？"]},
               {"code": 401, "indent": 0, "parameters": ["もう時間だぞ。"]},
               {"code": 102, "indent": 0, "parameters": [["行く", "やめる"], 1, 0, 2, 0]},
               {"code": 0, "indent": 0, "parameters": []}]
    w("Map001.json", {"displayName": "村", "events": [None, {"id": 1, "pages": [{"list": lst}]}]})
    w("MapInfos.json", [None, {"id": 1, "order": 1}])
    w("CommonEvents.json", [None, {"id": 1, "list": [{"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]},
                                                     {"code": 401, "indent": 0, "parameters": ["昔々……"]},
                                                     {"code": 0, "indent": 0, "parameters": []}]}])


VI = {"勇者の旅": "Hành trình", "G": "G", "炎": "Lửa", "レベル": "Cấp", "戦う": "Chiến đấu",
      "%1には効かなかった！": "Không tác dụng với %1!", "カイル": "Kael", "村": "Làng",
      "\\C[3]ミラ\\C[0]、ここで何してるんだ？\nもう時間だぞ。":
          "\\C[3]Mira\\C[0], cậu làm gì ở đây thế? Tới giờ đi rồi đó, nhanh lên kẻo trễ chuyến đò sáng!",
      "\\C[3]ミラ\\C[0]、ここで何してるんだ？": "\\C[3]Mira\\C[0], cậu làm gì ở đây?",
      "\\n<ミラ>うん！": "\\n<Mira>Ừ!", "行く": "Đi", "やめる": "Thôi", "昔々……": "Ngày xửa ngày xưa…"}


def test_mz(tmp, v, adp):
    g = os.path.join(tmp, "MZ")
    mz_game(g)
    w = os.path.join(tmp, "W")
    os.makedirs(w)
    rc, out = run([adp, "roundtrip", "--game", g, "--work", w], w)
    check("rpgmv roundtrip", rc == 0 and "KHỚP 100%" in out, out)
    rc, out = run([adp, "scan", "--game", g], w)
    check("rpgmv scan", "RPG Maker MZ" in out, out)
    run([v, "init", "--name", "MZ", "--lang", "ja"], w)
    rc, out = run([adp, "extract", "--game", g, "--work", w], w)
    check("rpgmv extract", rc == 0 and "trích" in out, out)
    src = [json.loads(x) for x in open(os.path.join(w, "src.jsonl"), encoding="utf-8")]
    pay = "@@scene Map001\nThử.\n@@scene CE1\nMở đầu.\n" + "".join(f"@@ {e['id']}\n{VI[e['src']]}\n" for e in src)
    rc, out = run([v, "write", "-"], w, pay)
    check("rpgmv write", rc == 0, out)
    run([v, "export"], w)
    rc, out = run([adp, "apply", "--game", g, "--work", w, "--name", "p1"], w)
    check("rpgmv apply", rc == 0 and "patchkit" in out, out)
    m = json.load(open(os.path.join(w, "patch", "p1", "files", "data", "Map001.json"), encoding="utf-8"))
    L = m["events"][1]["pages"][0]["list"]
    lines = [c["parameters"][0] for c in L if c["code"] == 401]
    vis = [len(re.sub(r"\\[A-Za-z]+\[\d+\]", "", x)) for x in lines]
    check("rpgmv ngắt dòng + tên + lựa chọn", L[0]["parameters"][4] == "Kael" and len(lines) >= 2
          and all(n <= 42 for n in vis) and L[len(lines) + 1]["parameters"][0] == ["Đi", "Thôi"]
          and m["displayName"] == "Làng", json.dumps(L, ensure_ascii=False))
    check("rpgmv không sửa game gốc", json.load(open(os.path.join(g, "data", "Map001.json"), encoding="utf-8"))
          ["events"][1]["pages"][0]["list"][0]["parameters"][4] == "カイル")
    rc, out = run([v, "patchkit", os.path.join(w, "patch", "p1"), "--game", g], w)
    check("patchkit trên patch thật", rc == 0 and "thêm mới 0" in out, out)


def test_mv(tmp, v, adp):
    g = os.path.join(tmp, "MV")
    mz_game(g, mv=True)
    w = os.path.join(tmp, "WMV")
    os.makedirs(w)
    run([v, "init", "--name", "MV", "--lang", "ja"], w)
    rc, out = run([adp, "scan", "--game", g], w)
    check("rpgmv MV scan", "RPG Maker MV" in out, out)
    rc, out = run([adp, "extract", "--game", g, "--work", w, "--name-regex", "^【(.+?)】$"], w)
    src = [json.loads(x) for x in open(os.path.join(w, "src.jsonl"), encoding="utf-8")]
    names = [e for e in src if e["id"].endswith("nl")]
    body = [e for e in src if e["id"] == "Map001.json:e1.p0.0"]
    check("MV tên dòng đầu: tách thành mục tên, thân thoại không còn 【】", rc == 0 and names and names[0]["src"] == "カイル"
          and body and body[0]["src"].startswith("\\C[3]") and body[0].get("speaker") == "カイル", src)
    rc, out = run([adp, "roundtrip", "--game", g, "--work", w], w)
    check("MV roundtrip dùng regex đã lưu", rc == 0 and "KHỚP 100%" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ Map001.json:e1.p0.3\n\\n<Mira Ừ!\n")
    check("hộp tên \\n<…> thiếu '>' bị chặn", rc == 2 and "thiếu dấu >" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ Map001.json:e1.p0.3\n\\n<ミラ>Ừ!\n")
    check("hộp tên giữ tên Nhật bị chặn", rc == 2 and "còn chữ/dấu gốc" in out, out)
    pay = "@@scene Map001\nThử.\n@@scene CE1\nMở đầu.\n" + "".join(f"@@ {e['id']}\n{VI[e['src']]}\n" for e in src)
    rc, out = run([v, "write", "-"], w, pay)
    check("MV write", rc == 0, out)
    run([v, "export"], w)
    rc, out = run([adp, "apply", "--game", g, "--work", w, "--name", "p1"], w)
    m = json.load(open(os.path.join(w, "patch", "p1", "files", "www", "data", "Map001.json"), encoding="utf-8"))
    L = [c["parameters"][0] for c in m["events"][1]["pages"][0]["list"] if c["code"] == 401]
    check("MV ghi lại: giữ khung 【】 với tên đã dịch, hộp tên dịch", L[0] == "【Kael】" and L[1].startswith("\\C[3]Mira")
          and L[-1] == "\\n<Mira>Ừ!", L)


# ---------------------------------------------------------------- 2.0.0

CJK = re.compile("[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\u3000-\u303f\uff01-\uff60]")


def trmap(w):
    tr, extra = {}, {}
    for x in open(os.path.join(w, "tr.jsonl"), encoding="utf-8"):
        if x.strip():
            t = json.loads(x)
            tr[t["id"]] = t["vi"]
            extra[t["id"]] = t
    return tr, extra


def writefile(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def judge_tsv(path, ids_json, heavy=(), rebut=None):
    """Tep ket qua giam khao T2/F2 du dong cho moi muc (mac dinh ok)."""
    m = json.load(open(ids_json, encoding="utf-8"))
    rebut = rebut or {}
    rows = [f"{i}\t{'nang' if i in heavy else 'ok'}\t\tthử\t\t{rebut.get(i, '')}\n"
            for i in list(m.get("random") or []) + list(m.get("flagged") or [])]
    writefile(path, "id\tmuc\tloai\tly_do\tde_xuat\tbac\n" + "".join(rows))


def judge_t3(path, ids_json, can=()):
    m = json.load(open(ids_json, encoding="utf-8"))
    writefile(path, "k\tdoan\tcan\tly_do\n" + "".join(f"{it['k']}\t{it['letter']}\t{1 if it['k'] in can else 0}\t\n"
                                                    for it in m["items"]))


def latest(w, gate):
    return sorted(glob.glob(os.path.join(w, "reports", f"qa-{gate}-*.ids.json")))[-1]


def neo_block(out):
    lines, on = [], False
    for ln in out.split("\n"):
        if ln.startswith("NEO ("):
            on = True
        elif on and not ln.startswith("  - "):
            break
        if on:
            lines.append(ln)
    return lines


def test_v2(tmp, v, chung):
    w = os.path.join(tmp, "Viet hoa game", "v2")
    os.makedirs(w)
    rc, out = run([v, "init", "--name", "V2", "--kind", "18", "--lang", "ja", "--the-loai", "vn", "--boi-canh", "hien_dai"], w)
    cfg = json.load(open(os.path.join(w, "game.json"), encoding="utf-8"))
    check("init 2.0: the_loai, boi_canh, lô thoại 80, không ghi khóa rỗng", rc == 0 and cfg.get("the_loai") == "vn"
          and cfg.get("batch_dialogue") == 80 and "require_emotion" not in cfg, out)
    os.makedirs(os.path.join(tmp, "x"))
    rc, out = run([v, "init", "--name", "X", "--the-loai", "visual"], os.path.join(tmp, "x"))
    check("init từ chối the_loai sai", rc != 0, out)
    setcfg(w, batch_dialogue=4, batch_short=4, qa_dinh_ky=True)
    rows = [
        {"id": "ui1", "src": "{n, plural, one {# 個のアイテム} other {# 個のアイテム}}", "kind": "ui", "maxlen": 40},
        {"id": "ui2", "src": "{N}|plural(one=匹,other=匹)", "kind": "ui", "maxlen": 40},
        {"id": "it1", "src": "炎の剣。敵一体に火属性の大ダメージを与える。", "kind": "data", "file": "Items", "maxlen": 12, "maxlines": 2},
        {"id": "it2", "src": "回復薬", "kind": "data", "file": "Items", "maxlen": 12},
        {"id": "a1", "src": "おい、何してるんだ？", "speaker": "アキラ", "scene": "s1", "en": "Hey, what are you doing?"},
        {"id": "b1", "src": "別に。", "speaker": "ベニ", "scene": "s1"},
        {"id": "a2", "src": "これは長い文章のテストです。", "speaker": "アキラ", "scene": "s1"},
        {"id": "b2", "src": "テメエ、ふざけるな！", "speaker": "ベニ", "scene": "s1"},
        {"id": "n1", "src": "夜が来た。", "scene": "s2", "page": "1"},
        {"id": "n2", "src": "静かだった。", "scene": "s2", "page": "1"},
        {"id": "n3", "src": "風が吹いた。", "scene": "s2", "page": "1", "voice": "v1.ogg"},
        {"id": "c1", "src": "貴様は何者だ。", "speaker": "カゲ", "scene": "s2"},
        {"id": "c2", "src": "彼女はもう行った。", "speaker": "カゲ", "scene": "s2"},
        {"id": "a3", "src": "俺はアキラだ。", "speaker": "アキラ", "scene": "s2"},
        {"id": "b3", "src": "私も。", "speaker": "ベニ", "scene": "s2"},
    ]
    open(os.path.join(w, "src.jsonl"), "w", encoding="utf-8").write(jl(rows))
    rc, out = run([v, "plan"], w)
    check("plan 2.0", rc == 0 and "Lô:" in out, out)
    # ho so + khau vi cho NEO va lint dich sat
    hoso = os.path.join(chung, "hoso")
    writefile(os.path.join(chung, "khauvi", "cam_mau.tsv"), "regex\tgoi_y\tpham_vi\nnói đúng ra thì\tbỏ cụm này\tchung\n"
              "xin hãy chiếu cố\tmong được giúp đỡ\tnguon:zh\n")
    notes = re.sub(r"(## NEO[^\n]*\n)", r"\1- Tên nhân vật giữ âm Nhật.\n",
                   open(os.path.join(w, "notes.md"), encoding="utf-8").read(), count=1)
    writefile(os.path.join(w, "notes.md"), notes)
    # 1) Cam xuc bat buoc voi the_loai vn
    rc, out = run([v, "write", "-"], w, "@@ a1\nNày, cậu đang làm gì đấy?\n")
    check("vn: thiếu 'Cảm xúc:' → lỗi chặn", rc == 2 and "Cảm xúc:" in out and "Ghi: 0/1" in out, out)
    pay = ("@@scene s1 ! loai=hai\nAkira bắt gặp Beni. Cảm xúc: Akira tò mò, Beni bực.\n"
           "@@scene s2 loai=chien_dau\nĐêm, ba người chạm trán. Cảm xúc: căng thẳng.\n"
           "@@pair アキラ | ベニ | tớ | cậu | bạn cùng lớp\n@@pair ベニ | アキラ | tớ | cậu | bạn cùng lớp\n"
           "@@pair カゲ | * | ta | ngươi | kẻ địch thanh lịch\n"
           "@@ a1\nNói đúng ra thì cậu đang làm gì đấy?\n"
           "@@ b1\nChẳng có gì, you know what is the point.\n"
           "@@ a2\nĐây là một câu rất dài được viết ra chỉ để kiểm tra xem vgk có cảnh báo tỷ lệ độ dài bất thường hay không.\n"
           "@@ b2\nTao bảo mày đừng có giỡn!\n")
    rc, out = run([v, "write", "-"], w, pay)
    sc = open(os.path.join(w, "scenes.tsv"), encoding="utf-8").read()
    check("write: mày–tao ngoài bảng bị chặn; cảnh báo dịch sát, chữ Anh sót, dài bất thường; @@scene loai",
          rc == 2 and "b2: xưng hô cấm" in out and "dịch sát" in out and "chữ Anh sót" in out and "dài bất thường" in out
          and "\thai" in sc and "chien_dau" in sc, out)
    st = json.load(open(os.path.join(w, "state.json"), encoding="utf-8"))
    check("2.4: câu dính mẫu dịch sát bị trả lại; câu cảnh báo khác vào nhóm cờ T2",
          "a1: dịch sát" in out and "a1" not in st.get("flags", {}) and "b1" in st.get("flags", {}), st.get("flags"))
    rc0, out0 = run([v, "write", "-"], w, "@@pair ベニ | アキラ | tớ/tao | cậu/mày | nổi điên (テメエ)\n@@ b2\nTao bảo mày đừng có giỡn!\n")
    check("2.1: agent dịch không tự đặt hay đổi xưng hô có tao/mày qua @@pair", rc0 == 2 and "xưng hô cấm" in out0, out0)
    run([v, "pair", "set", "ベニ", "アキラ", "tớ/tao", "cậu/mày", "--note", "nổi điên (テメエ)"], w)
    rc, out = run([v, "write", "-"], w, "@@ b2\nTao bảo mày đừng có giỡn!\n")
    check("mày–tao được phép khi bảng cho phép (phiên chính đặt bằng pair set)", rc == 0 and "Ghi: 1/1" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ b1\nKhông có gì. Lông mày cậu nhíu lại kìa.\n")
    check("'lông mày' không bị coi là xưng hô", rc == 0, out)
    rc, out = run([v, "write", "-"], w, "@@ c2\nCậu tới muộn rồi đấy.\n")
    check("cậu/cô khi bảng gọi ngươi → cảnh báo", rc == 0 and "gọi lệch bảng" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ c2\nCô ấy đi rồi.\n@@ c1\nNgươi là ai?\n@@ a3 >カゲ\nTôi là Akira.\n")
    check("'cô ấy' không bị cờ; người nghe ghi rõ; tôi ngoài bảng → cảnh báo",
          rc == 0 and "gọi lệch bảng" not in out and "tự xưng khác bảng xưng hô" in out, out)
    rc, out = run([v, "write", "-"], w, "@@pair アキラ | カゲ | tôi | anh | người lạ\n@@ a3 >カゲ\nTôi là Akira.\n")
    _, ex = trmap(w)
    check("cặp đúng người nghe hết cảnh báo; tr.jsonl lưu người nghe", rc == 0 and "tự xưng khác" not in out
          and ex["a3"].get("l") == "カゲ", out)
    rc, out = run([v, "write", "-"], w, "@@ n2\n=gộp\n")
    check("=gộp khi game chưa bật gop_ok → chặn", rc == 2 and "chưa bật =gộp" in out, out)
    setcfg(w, gop_ok=True)
    rc, out = run([v, "write", "-"], w, "@@ n1\nĐêm buông xuống, tĩnh lặng.\n@@ n2\n=gộp\n@@ n3\n=gộp\n@@ b3\nTớ cũng vậy.\n")
    check("=gộp: cùng trang, không lồng tiếng → được; có lồng tiếng → chặn", rc == 2 and "n3: gộp không hợp lệ" in out
          and "Ghi: 3/4" in out, out)
    run([v, "write", "-"], w, "@@ n3\nGió thổi qua.\n")
    pay = ("@@ ui1\n{n, plural, other {# món}}\n@@ ui2\n{N}|plural(one=con)\n"
           "@@ it1\nKiếm lửa. Gây sát thương lửa rất lớn lên một kẻ địch duy nhất trên chiến trường.\n@@ it2\nThuốc hồi phục\n")
    rc, out = run([v, "write", "-"], w, pay)
    check("khung ICU/Unreal thiếu khóa → chặn; maxlines → cảnh báo quá số dòng", rc == 2 and "ui1: khung số nhiều lệch" in out
          and "ui2: khung số nhiều lệch" in out and "quá số dòng" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ ui1\n{n, plural, one {món đồ} other {# món đồ}}\n")
    check("khung ICU mất '#' → chặn", rc == 2 and "mất '#'" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ ui1\n{n, plural, one {# món đồ} other {# món đồ}}\n@@ ui2\n{N}|plural(one=con,other=con)\n")
    check("khung ICU/Unreal đúng → ghi", rc == 0 and "Ghi: 2/2" in out, out)
    run([v, "write", "-"], w, "@@ a1\nNày, cậu đang làm gì đấy?\n@@ a2\nĐây là bài kiểm tra.\n@@ b1\nKhông có gì.\n")
    # NEO
    hsrc = os.path.join(HERE, "hoso") if os.path.isdir(os.path.join(HERE, "hoso")) else os.path.join(HERE, "..", "references", "hoso")
    qtd = os.path.join(HERE, "hoso", "quy-tac-dich.md")
    if not os.path.exists(qtd):
        qtd = os.path.join(HERE, "..", "references", "quy-tac-dich.md")
    if not (os.path.isdir(hsrc) and os.path.exists(qtd)):
        print("(bỏ qua kiểm NEO: không thấy thư mục hồ sơ cạnh selftest.py)")
        writefile(os.path.join(hoso, "quy-tac-dich.md"), "# lõi\n\n## NEO\n- Dịch sát ý, viết như văn Việt.\n")
        writefile(os.path.join(hoso, "nguon-ja.md"), "# ja\n\n## NEO\n- Kính ngữ.\n")
    else:
        shutil.copytree(hsrc, hoso)
        shutil.copy(qtd, os.path.join(hoso, "quy-tac-dich.md"))
    rc, out = run([v, "next", "--batch", "3", "--all"], w)
    nb = neo_block(out)
    total = sum(len(x) + 1 for x in nb)
    check("NEO in đầu lô, ≤1.000 ký tự, có luật lõi + NEO game", nb and total <= 1000 and any("Tên nhân vật giữ âm Nhật" in x for x in nb)
          and any("sát ý tác giả" in x for x in nb), "\n".join(nb) + f"\n{total} ký tự")
    check("en_mode on_demand: không in EN khi không xin", "#> EN:" not in out and "→ ベニ" in out, out)
    rc, out = run([v, "next", "--batch", "3", "--all", "--en", "all"], w)
    check("--en all in EN", "#> EN: Hey, what are you doing?" in out, out)
    with open(os.path.join(hoso, "nguon-ja.md"), "a", encoding="utf-8") as f:
        f.write("\n")
    rc, out = run([v, "next", "--batch", "3", "--all"], w)
    check("tệp luật đổi → LUẬT ĐÃ ĐỔI", "LUẬT ĐÃ ĐỔI: đọc lại nguon-ja.md" in out, out)
    rc, out = run([v, "status"], w)
    check("status 2.0: kiểu game + cổng đến hạn", "Kiểu: thể loại vn" in out and "CỔNG ĐẾN HẠN" in out, out)
    rc, out = run([v, "check"], w)
    check("check 2.0: 0 lỗi chặn", rc == 0 and "LỖI CHẶN: 0" in out, out)
    # QA
    rc, out = run([v, "qa", "sample", "--gate", "T2", "--seed", "5"], w)
    ids1 = sorted(glob.glob(os.path.join(w, "reports", "qa-T2-*.ids.json")))
    m1 = json.load(open(ids1[-1], encoding="utf-8"))
    txt = open(ids1[-1].replace(".ids.json", ".txt"), encoding="utf-8").read()
    check("qa sample T2: tệp mẫu có GỐC/VI/xưng hô", rc == 0 and "GỐC:" in txt and "VI:" in txt and "xưng hô:" in txt
          and m1["seed"] == 5 and m1["random"], out)
    time.sleep(1.1)
    run([v, "qa", "sample", "--gate", "T2", "--seed", "5"], w)
    ids2 = sorted(glob.glob(os.path.join(w, "reports", "qa-T2-*.ids.json")))
    check("qa sample cùng seed → cùng mẫu", len(ids2) == 2 and json.load(open(ids2[-1], encoding="utf-8"))["random"] == m1["random"], ids2)
    jt = os.path.join(w, "reports", "giamkhao-1.tsv")
    writefile(jt, "")
    rc, out = run([v, "qa", "score", jt, "--ids", ids1[-1]], w)
    st = json.load(open(os.path.join(w, "state.json"), encoding="utf-8"))
    check("qa score: tệp giám khảo rỗng → từ chối, không ghi gì", rc == 2 and "thiếu" in out
          and st["qa"]["T2"]["runs"] == 0, out)
    writefile(jt, "| id | muc |\n|---|---|\n" + "".join(f"| {i} | ok |\n" for i in m1["random"]))
    rc, out = run([v, "qa", "score", jt, "--ids", ids1[-1]], w)
    check("qa score: bảng Markdown → từ chối", rc == 2 and "Markdown" in out, out)
    judge_tsv(jt, ids1[-1])
    with open(jt, "a", encoding="utf-8") as f:
        f.write("zz9\tok\t\t\t\n")
    rc, out = run([v, "qa", "score", jt, "--ids", ids1[-1]], w)
    check("qa score: id lạ → từ chối", rc == 2 and "mã lạ" in out, out)
    judge_tsv(jt, ids1[-1], heavy=m1["random"][:2])
    rc, out = run([v, "qa", "score", jt, "--ids", ids1[-1]], w)
    st = json.load(open(os.path.join(w, "state.json"), encoding="utf-8"))
    check("qa score: 2 lỗi nặng/≤50 → TRƯỢT, lần sau lấy 100 câu", "TRƯỢT" in out and "P4 chưa đạt" in out
          and st["qa"]["T2"]["n"] == 100 and st["qa"]["T2"]["need_pass"] == 2 and st["qa"]["T2"]["runs"] == 1, out)
    judge_tsv(jt, ids1[-1], heavy=m1["random"][:2], rebut={m1["random"][0]: "câu gốc nói đúng như vậy",
                                                           m1["random"][1]: "đúng ngữ cảnh"})
    rc, out = run([v, "qa", "score", jt, "--ids", ids1[-1]], w)
    st = json.load(open(os.path.join(w, "state.json"), encoding="utf-8"))
    log = open(os.path.join(w, "reports", "qa.tsv"), encoding="utf-8").read()
    check("chấm lại cùng mẫu sau khi bác: thay kết quả cũ, không tính thêm lần; bác >30% → giám khảo lệch",
          "ĐẠT" in out and "chấm lại" in out and "giám khảo lệch" in out and st["qa"]["T2"]["runs"] == 1
          and st["qa"]["T2"]["n"] == 50 and "chấm lại" in log, out)
    judge_tsv(jt, ids2[-1])
    rc, out = run([v, "qa", "score", jt, "--ids", ids2[-1]], w)
    judge_tsv(jt, ids1[-1])
    rc2, out2 = run([v, "qa", "score", jt, "--ids", ids1[-1]], w)
    check("chấm mẫu mới rồi chấm lại mẫu cũ → từ chối", "ĐẠT" in out and rc2 != 0 and "mẫu gần nhất" in out2, out + out2)
    rc, out = run([v, "qa", "sample", "--gate", "T3", "--seed", "2"], w)
    i3 = sorted(glob.glob(os.path.join(w, "reports", "qa-T3-*.ids.json")))[-1]
    t3 = open(i3.replace(".ids.json", ".txt"), encoding="utf-8").read()
    body = t3.split("Ứng viên:")[1]
    check("qa sample T3: che tên, không có chữ gốc trong thân", "Ứng viên:" in t3 and "アキラ" not in body.split("\n", 1)[1]
          and not CJK.search("\n".join(x for x in body.split("\n") if re.match(r"^\d+\. ", x))), t3)
    writefile(jt, "1\tA\t0\t\n")
    rc, out = run([v, "qa", "score", jt, "--ids", i3], w)
    check("qa score T3: thiếu câu → từ chối", rc == 2 and "thiếu" in out, out)
    judge_t3(jt, i3)
    rc, out = run([v, "qa", "score", jt, "--ids", i3], w)
    check("qa score T3", "ĐẠT" in out and "đoán đúng người nói" in out, out)
    rc, out = run([v, "qa", "sample", "--gate", "F2", "--seed", "3"], w)
    iF = sorted(glob.glob(os.path.join(w, "reports", "qa-F2-*.ids.json")))[-1]
    judge_tsv(jt, iF)
    rc, out = run([v, "qa", "score", jt, "--ids", iF], w)
    rc2, due = run([v, "qa", "due"], w)
    check("F2 đạt → không còn đến hạn", "ĐẠT" in out and "F2 (" not in due, out + due)
    rc, out = run([v, "qa", "sample", "--gate", "P5", "--seed", "4"], w)
    i5 = sorted(glob.glob(os.path.join(w, "reports", "qa-P5-*.ids.json")))[-1]
    sheet = open(i5.replace(".ids.json", ".txt"), encoding="utf-8").read()
    check("P5: bảng đọc chỉ tiếng Việt (không chữ Nhật, có bối cảnh)", "Bối cảnh:" in sheet and not CJK.search(sheet), sheet)
    rc, out = run([v, "qa", "record", i5, "--can", "1"], w)
    neo = open(os.path.join(w, "neo.tsv"), encoding="utf-8").read() if os.path.exists(os.path.join(w, "neo.tsv")) else ""
    check("qa record P5: 1 câu cấn → ĐẠT, thêm câu neo", "ĐẠT" in out and "P5" in neo, out + neo)
    rc, out = run([v, "qa", "record", i5, "--xungho", "2"], w)
    check("qa record: sai xưng hô → TRƯỢT", "TRƯỢT" in out, out)
    m5 = json.load(open(i5, encoding="utf-8"))
    first = m5["random"][0]
    st = json.load(open(os.path.join(w, "state.json"), encoding="utf-8"))
    tr, _ = trmap(w)
    run([v, "write", "-", "--force", first], w, f"@@ {first}\n{tr[first].rstrip('.!?') + ' đấy.' if tr[first] else 'x'}\n")
    rc, out = run([v, "qa", "collect"], w)
    hc = os.path.join(chung, "khauvi", "hieu_chuan.tsv")
    check("qa collect: câu cấn đã sửa → cặp hiệu chuẩn", os.path.exists(hc) and "Thêm" in out, out)
    pairs = "pair_id\tngu_canh\ta\tb\tchon\tcan\tnguon\n" + "".join(
        f"p{k}\tbối cảnh\tbản A {k}\tbản B {k}\t{'A' if k % 2 else 'B'}\t{'B' if k < 5 else ''}\tthử\n" for k in range(40))
    writefile(os.path.join(w, "reports", "pairs.tsv"), pairs)
    judge = "".join(f"p{k}\t{('A' if k % 2 else 'B') if k < 36 else ('B' if k % 2 else 'A')}\t{'B' if k < 4 else ''}\n" for k in range(40))
    writefile(os.path.join(w, "reports", "pj.tsv"), judge)
    rc, out = run([v, "qa", "calibrate", "--pairs", "reports/pairs.tsv"], w)
    check("qa calibrate: tạo bài cho giám khảo không kèm đáp án", "P4: 40 cặp" in out, out)
    rc, out = run([v, "qa", "calibrate", "--pairs", "reports/pairs.tsv", "--judge", "reports/pj.tsv"], w)
    p4 = json.load(open(os.path.join(chung, "khauvi", "p4.json"), encoding="utf-8"))
    check("qa calibrate: 90% trùng, bắt 4/5 câu cấn → P4 ĐẠT", "P4: ĐẠT" in out and p4["ok"], out)
    judge_tsv(jt, iF)
    rc, out = run([v, "qa", "score", jt, "--ids", iF], w)
    check("P4 đạt → kết quả không còn ghi chỉ là bộ lọc", rc == 0 and "P4 chưa đạt" not in out, out)
    rc, out = run([v, "qa", "status"], w)
    check("qa status", "P4: ĐẠT" in out and "T2:" in out, out)
    # cong P3 / P6
    rc, out = run([v, "term", "candidates", "--min", "1"], w)
    check("term candidates: ứng viên katakana", rc == 1 and "アイテム" in out, out)
    run([v, "term", "skip", "アイテム", "--note", "thử"], w)
    rc, out = run([v, "term", "candidates", "--min", "1"], w)
    check("term skip: ứng viên đã quyết không còn", "アイテム" not in out.split("\n", 1)[1], out)
    rc, out = run([v, "estimate"], w)
    check("estimate", rc == 0 and "Ước tính thô" in out, out)
    setcfg(w, ngan_sach_token=10)
    rc, out = run([v, "estimate"], w)
    check("estimate vượt ngân sách → exit 3", rc == 3 and "VƯỢT NGÂN SÁCH" in out, out)
    setcfg(w, ngan_sach_token=None)
    # polish
    rc, out = run([v, "polish", "next"], w)
    check("polish next: in bản hiện tại", "CHUỐT LẠI lô 3" in out and "#> VI:" in out, out)
    rc, out = run([v, "polish", "lint", "3"], w)
    check("polish lint", "Lint lô 3" in out, out)
    rc, out = run([v, "polish", "doc", "3"], w)
    check("polish doc: chỉ bản Việt", "cậu đang làm gì" in out, out)
    run([v, "polish", "done", "3"], w)
    rc, out = run([v, "polish", "status"], w)
    check("polish done/status", "Chuốt lại: 1/" in out, out)
    # dong bo
    rc, out = run([v, "dongbo"], w)
    check("dongbo liệt kê tệp cần ghi về máy", "tr.jsonl" in out, out)
    run([v, "dongbo", "--mark"], w)
    rc, out = run([v, "dongbo"], w)
    check("dongbo --mark → không còn tệp đổi", "Không có tệp nào đổi" in out, out)
    # export / backup
    rc, out = run([v, "export"], w)
    exp = json.load(open(os.path.join(w, "export.json"), encoding="utf-8"))
    meta = json.load(open(os.path.join(w, "export_meta.json"), encoding="utf-8"))
    check("export: =gộp ra chuỗi rỗng + export_meta.json", rc == 0 and exp["n2"] == "" and meta["gop"] == ["n2"], out)
    run([v, "backup", "--compact"], w)
    _, ex = trmap(w)
    check("backup --compact giữ người nghe và =gộp", ex["a3"].get("l") == "カゲ" and ex["n2"].get("g") == 1, ex.get("a3"))
    rc, out = run([v, "review", "--n", "3"], w)
    check("review: seed ngẫu nhiên được in", "(seed " in out, out)


def test_v2b(tmp, v, chung):
    """Nhip cong T2/T3, F3 bat buoc, P3, bang doc F3, ma tat cho minor/EN, so lieu, xung ho khi chua ro nguoi nghe."""
    w = os.path.join(tmp, "Viet hoa game", "v2b")
    os.makedirs(w)
    run([v, "init", "--name", "V2B", "--lang", "ja", "--the-loai", "rpg", "--boi-canh", "fantasy"], w)
    setcfg(w, batch_dialogue=2, batch_short=2, cps_max=17, qa_dinh_ky=True)
    rows = [{"id": f"u{k}", "src": f"メニュー{k}", "kind": "ui"} for k in range(6)]
    rows += [{"id": "s1", "src": "攻撃力が150%上昇し、敵を2ターン気絶させる。", "kind": "data", "file": "Skills", "maxlen": 40,
              "maxlines": 2},
             {"id": "g1", "src": "{G}|gender(彼,彼女)が来た。", "kind": "ui", "maxlen": 40}]
    spk = ["士郎", "凛", "ランサー"]
    for k in range(12):
        rows.append({"id": f"d{k}", "src": f"台詞その{k}だ。", "speaker": spk[k % 3], "scene": "c1", "en": f"Line {k}."})
    rows.append({"id": "sub1", "src": "急げ！", "speaker": "士郎", "scene": "c1", "dur_ms": 2000})
    writefile(os.path.join(w, "src.jsonl"), jl(rows))
    run([v, "plan"], w)
    rc, out = run([v, "term", "candidates", "--min", "1"], w)
    check("term candidates: người nói chữ Hán (士郎, 凛) là ứng viên", rc == 1 and "士郎" in out and "凛" in out, out)
    # lo ngan truoc: T2 den han, T3 chua
    run([v, "write", "-"], w, "".join(f"@@ u{k}\nMục {k}\n" for k in range(6)))
    rc, out = run([v, "qa", "due"], w)
    check("3 lô ngắn xong, chưa có thoại: T2 đến hạn, T3 chưa", "T2 (" in out and "lô ngắn" in out and "T3" not in out, out)
    rc, out = run([v, "write", "-"], w, "@@ s1\nTăng 115% công, làm choáng địch 3 lượt.\n")
    check("số liệu lệch → cảnh báo", "số liệu lệch" in out and "150" in out and "2" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ s1\nTăng 150% công, làm choáng địch 2 lượt.\n")
    check("số liệu khớp, trong khung → không cảnh báo (số liệu, quá số dòng)", rc == 0 and "số liệu lệch" not in out
          and "quá số dòng" not in out, out)
    rc, out = run([v, "write", "-"], w, "@@ g1\n{G}|gender(họ) đã tới.\n")
    check("Unreal |gender thiếu đối số → chặn", rc == 2 and "khung số nhiều lệch" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ g1\n{G}|gender(anh ấy,cô ấy) đã tới.\n")
    check("Unreal |gender dịch đối số theo vị trí → ghi", rc == 0, out)
    # xung ho khi canh co 3 nguoi noi
    run([v, "pair", "set", "ランサー", "士郎", "tao", "mày", "--note", "khinh thường"], w)
    pay = ("@@scene c1\nBa người gặp nhau trong sân.\n"
           "@@pair ランサー | 凛 | ta | cô em | trêu chọc\n@@pair 士郎 | * | tôi | anh | \n@@pair 凛 | * | tôi | anh | \n"
           "@@ d2\nLùi lại đi, mày.\n")
    rc, out = run([v, "write", "-"], w, pay)
    check("cảnh 3 người, không ghi >người nghe, 'mày' chỉ đúng với một người nghe → chặn", rc == 2
          and "chưa rõ người nghe" in out and "士郎" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ d2 >凛\nLùi lại đi, mày.\n")
    check("ghi >凛 mà bảng ランサー→凛 không có 'mày' → chặn", rc == 2 and "xưng hô cấm" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ d2 >士郎\nLùi lại đi, mày.\n")
    check("ghi >士郎 → được", rc == 0, out)
    rc, out = run([v, "write", "-"], w, "@@ sub1\nNhanh lên!\n")
    check("phụ đề trong ngưỡng cps → không cảnh báo", rc == 0 and "phụ đề quá nhanh" not in out, out)
    rc, out = run([v, "next"], w)
    al = re.findall(r"@@ (~\d+\.\d+)", out)
    rc2, out2 = run([v, "next", "--en", al[1]], w)
    check("next --en ~N.k: chỉ in EN của câu xin, không in lại cả lô", "#> EN: Line" in out2 and "LÔ " not in out2
          and out2.count("@@ ~") == 1, out2)
    rc, out = run([v, "minor", "add", al[0], "--note", "thử mã tắt"], w)
    check("minor add nhận mã tắt ~N.k", rc == 0 and "thêm 1" in out, out)
    vi = {f"d{k}": f"Câu thoại số {k} đây." for k in range(12)}
    vi["d2"] = None
    run([v, "write", "-"], w, "".join(f"@@ {i}\n{t}\n" for i, t in vi.items() if t))
    rc, out = run([v, "qa", "due"], w)
    check("≥3 lô thoại xong: T3 đến hạn", "T3 (" in out, out)
    # hai lan T2 truot lien → F3 bat buoc
    for seed in (11, 12):
        run([v, "qa", "sample", "--gate", "T2", "--seed", str(seed)], w)
        ids = latest(w, "T2")
        m = json.load(open(ids, encoding="utf-8"))
        judge_tsv(os.path.join(w, "reports", "gk.tsv"), ids, heavy=m["random"][:3])
        rc, out = run([v, "qa", "score", os.path.join(w, "reports", "gk.tsv"), "--ids", ids], w)
    rc2, st = run([v, "qa", "status"], w)
    check("T2 trượt 2 lần liền → ghi nhận (F3 tùy chọn từ 2.1)", "Ghi nhận: T2 trượt 2 lần liền" in out
          and "F3: tùy chọn" in st and "ghi nhận: T2 trượt 2 lần liền" in st, out + st)
    # P3: dong notes do lenh chon, giam khao cham
    notes = open(os.path.join(w, "notes.md"), encoding="utf-8").read()
    hd = "## Nhân vật (sự thật cả truyện, kèm căn cứ — chỉ Opus đọc; người dịch thấy hồ sơ theo mốc trong giong.tsv)\n"
    assert hd + "-" in notes
    notes = notes.replace(hd + "-", hd + "- 士郎 nói câu mở đầu (d0).\n"
                          "- 凛 trả lời ngay sau đó (d1).\n- ランサー khinh thường 士郎 (d2).")
    writefile(os.path.join(w, "notes.md"), notes)
    rc, out = run([v, "qa", "sample", "--gate", "P3", "--seed", "1"], w)
    i3 = latest(w, "P3")
    txt = open(i3.replace(".ids.json", ".txt"), encoding="utf-8").read()
    check("P3: lệnh chọn dòng notes, kèm câu gốc của id căn cứ", rc == 0 and "DÒNG:" in txt and "台詞その0だ。" in txt, txt)
    writefile(os.path.join(w, "reports", "p3.tsv"), "1\t1\t\n")
    rc, out = run([v, "qa", "score", os.path.join(w, "reports", "p3.tsv"), "--ids", i3], w)
    check("P3: thiếu dòng → từ chối", rc == 2, out)
    m = json.load(open(i3, encoding="utf-8"))
    writefile(os.path.join(w, "reports", "p3.tsv"), "".join(f"{it['k']}\t1\t\n" for it in m["items"]))
    rc, out = run([v, "qa", "score", os.path.join(w, "reports", "p3.tsv"), "--ids", i3], w)
    check("P3: đủ dòng khớp → ĐẠT", rc == 0 and "P3: ĐẠT" in out, out)
    # F3: bang doc chi tieng Viet, sai xung ho → truot
    run([v, "write", "-"], w, "@@ d2 >士郎\nLùi lại đi, mày.\n")
    rc, out = run([v, "qa", "sample", "--gate", "F3", "--seed", "1", "--n", "4"], w)
    iF3 = latest(w, "F3")
    rc, out = run([v, "qa", "sheet", iF3], w)
    check("qa sheet F3: chỉ tiếng Việt, có bối cảnh", rc == 0 and "Bối cảnh:" in out and not CJK.search(out.split("\n", 2)[2]), out)
    rc, out = run([v, "qa", "record", iF3, "--can", "1", "--xungho", "2"], w)
    check("F3: 2 câu cấn trong đó 1 sai xưng hô → TRƯỢT", "TRƯỢT" in out and "1 sai xưng hô" in out, out)
    # polish: dai lo, bat dau tu lo N
    plan = json.load(open(os.path.join(w, "plan.json"), encoding="utf-8"))
    dl = [b["n"] for b in plan["batches"] if b["cls"] == "dialogue"]
    rc, out = run([v, "polish", "done", f"{dl[0]}-{dl[1]}"], w)
    rc2, out2 = run([v, "polish", "next", "--batch", str(dl[2])], w)
    check("polish done dải lô + polish next --batch", "chuốt xong 2 lô" in out and f"CHUỐT LẠI lô {dl[2]}" in out2, out + out2)
    # dongbo: ca _chung va patch/
    writefile(os.path.join(w, "patch", "px", "files", "a.json"), "{}")
    rc, out = run([v, "dongbo"], w)
    check("dongbo liệt kê cả _chung (khẩu vị, adapter) và patch/", "v2b/tr.jsonl" in out and "_chung/khauvi/" in out
          and "_chung/adapters/kv/kv_adapter.py" in out and "v2b/patch/px/files/a.json" in out, out)


def test_compat(tmp, v):
    """WORK tao boi vgk 1.1.0 (khong co khoa moi, plan cu, tr.jsonl cu) chay duoc, khong mat ban dich."""
    w = os.path.join(tmp, "Viet hoa game", "cu")
    os.makedirs(w)
    writefile(os.path.join(w, "game.json"), json.dumps({"vgk_version": "1.1.0", "name": "Cũ", "slug": "cu", "kind": "thuong",
                                                         "source_lang": "ja", "batch_dialogue": 150, "batch_short": 350}))
    rows = [{"id": f"d{k}", "src": f"テスト{k}です。", "speaker": "ミラ", "scene": "s1"} for k in range(6)]
    writefile(os.path.join(w, "src.jsonl"), jl(rows))
    import hashlib
    trl = "".join(json.dumps({"id": f"d{k}", "vi": f"Thử {k}.", "h": hashlib.sha1(f"テスト{k}です。".encode()).hexdigest()[:10],
                              "t": "2026-11-01 10:00"}, ensure_ascii=False) + "\n" for k in range(4))
    writefile(os.path.join(w, "tr.jsonl"), trl)
    writefile(os.path.join(w, "scenes.tsv"), "scene\tsummary\tpriority\ns1\tCảnh cũ.\t\n")
    writefile(os.path.join(w, "plan.json"), json.dumps({"version": 2, "src_sha": "x", "auto": [], "groups": {}, "batches": []}))
    rc, out = run([v, "status"], w)
    check("WORK 1.1.0: status chạy, chia lại lô, giữ 4 bản dịch", rc == 0 and "đã chia lại lô" in out and "đã dịch 4" in out, out)
    rc, out = run([v, "export", "--allow-missing"], w)
    exp = json.load(open(os.path.join(w, "export.json"), encoding="utf-8"))
    check("WORK 1.1.0: export giữ bản dịch cũ", exp["d0"] == "Thử 0." and exp["d3"] == "Thử 3.", out)
    rc, out = run([v, "write", "-"], w, "@@ d4\nThử 4.\n")
    check("WORK 1.1.0: write được, không đòi Cảm xúc khi chưa có the_loai", rc == 0, out)
    plan = json.load(open(os.path.join(w, "plan.json"), encoding="utf-8"))
    plan.pop("batch", None)
    writefile(os.path.join(w, "plan.json"), json.dumps(plan))
    setcfg(w, batch_dialogue=2)
    rc, out = run([v, "status"], w)
    check("plan 1.x không ghi 'batch' → giữ nguyên số lô (không chia lại)", rc == 0 and "chia lại lô" not in out, out)


def test_patchkit2(tmp, v):
    import hashlib
    w = os.path.join(tmp, "Viet hoa game", "v2")
    pd = os.path.join(w, "patch", "pk")
    writefile(os.path.join(pd, "files", "data", "A.json"), '{"a":"Việt"}')
    writefile(os.path.join(pd, "files", "data", "New.json"), "{}")
    g = os.path.join(tmp, "GK")
    writefile(os.path.join(g, "data", "A.json"), '{"a":"日本"}')
    rc, out = run([v, "patchkit", pd], w)
    check("patchkit thiếu --game → từ chối", rc != 0 and "--game" in out, out)
    rc, out = run([v, "patchkit", pd, "--game", g, "--game-win", "C:\\Games\\GK"], w)
    import hashlib
    ms = open(os.path.join(pd, "manifest_sha.txt"), "rb").read().decode("utf-8")
    goc = hashlib.sha256(open(os.path.join(g, "data", "A.json"), "rb").read()).hexdigest()
    psh = hashlib.sha256(open(os.path.join(pd, "files", "data", "A.json"), "rb").read()).hexdigest()
    bat = open(os.path.join(pd, "CAI_VIETHOA.bat"), "rb").read()
    go = open(os.path.join(pd, "GO_VIETHOA.bat"), "rb").read()
    check("patchkit: manifest_sha (gốc|patch, tệp mới '-'), bat dùng certutil, CRLF, không delayed expansion",
          rc == 0 and f"data/A.json|{goc}|{psh}" in ms and "data/New.json|-|" in ms and "\r\n" in ms
          and b"certutil" in bat and b"manifest_sha.txt" in bat and b"EnableDelayedExpansion" not in bat
          and b"Game da cap nhat" in bat and b"_installed" in bat and b"certutil" in go and b"\r\n" in go, out + ms)
    bad = []
    for name, s in (("CAI", bat.decode("utf-8")), ("GO", go.decode("utf-8"))):
        labels = set(re.findall(r"(?m)^:([A-Za-z_]+)\s*$", s))
        refs = set(re.findall(r"(?:goto|call)\s+:([A-Za-z_]+)", s, re.I))
        bad += [f"{name}: thiếu nhãn {x}" for x in sorted(refs - labels)]
        bad += [f"{name}: dòng in đường dẫn qua %REL%" for ln in s.split("\n") if "echo" in ln and "%REL%" in ln]
    check("bộ .bat: mọi goto/call có nhãn; log không in đường dẫn qua %REL%", not bad, bad)
    # game dang cai ban Viet hoa: sha goc phai lay tu _viethoa_backup, khong lay ban Viet lam goc
    gi = os.path.join(tmp, "GI")
    writefile(os.path.join(gi, "data", "A.json"), '{"a":"Việt"}')
    writefile(os.path.join(gi, "data", "New.json"), "{}")
    writefile(os.path.join(gi, "_viethoa_backup", "data", "A.json"), '{"a":"日本"}')
    writefile(os.path.join(gi, "_viethoa_backup", "_installed", "data", "A.json.sha"), psh + "\n")
    writefile(os.path.join(gi, "_viethoa_backup", "_installed", "data", "New.json.sha"),
              hashlib.sha256(b"{}").hexdigest() + "\n")
    pd2 = os.path.join(w, "patch", "pk2")
    writefile(os.path.join(pd2, "files", "data", "A.json"), '{"a":"Việt 2"}')
    writefile(os.path.join(pd2, "files", "data", "New.json"), "{}")
    rc, out = run([v, "patchkit", pd2, "--game", gi], w)
    ms2 = open(os.path.join(pd2, "manifest_sha.txt"), encoding="utf-8").read()
    check("patchkit trên game đã cài: sha gốc lấy từ _viethoa_backup, tệp patch thêm vẫn là tệp mới",
          rc == 0 and f"data/A.json|{goc}|" in ms2 and "data/New.json|-|" in ms2 and "2 tệp từ _viethoa_backup" in out, out + ms2)
    gj = os.path.join(tmp, "GJ")
    writefile(os.path.join(gj, "data", "A.json"), '{"a":"Việt"}')
    rc, out = run([v, "patchkit", pd2, "--game", gj], w)
    check("patchkit: tệp game trùng bản Việt đã đóng gói mà không có sao lưu → từ chối", rc != 0 and "không phải bản gốc" in out, out)
    gd = os.path.join(tmp, "GI_goc")
    rc, out = run([v, "goc", "--game", gi, "--out", gd], w)
    ag = open(os.path.join(gd, "data", "A.json"), encoding="utf-8").read() if os.path.exists(os.path.join(gd, "data", "A.json")) else ""
    check("vgk goc: lấy lại tệp gốc từ sao lưu, bỏ tệp do patch thêm, không chép _viethoa_backup",
          rc == 0 and ag == '{"a":"日本"}' and not os.path.exists(os.path.join(gd, "data", "New.json"))
          and not os.path.exists(os.path.join(gd, "_viethoa_backup")), out)
    gm = os.path.join(tmp, "GM_cai")
    mz_game(gm)
    writefile(os.path.join(gm, "_viethoa_backup", "_installed", "data", "Map001.json.sha"), "x\n")
    rc, out = run([os.path.join(os.path.dirname(v), "rpgmv_adapter.py"), "extract", "--game", gm, "--work", w], w)
    check("adapter từ chối đọc thư mục game đang cài bản Việt hóa", rc != 0 and "đang cài bản Việt hóa" in out, out)


def test_migrate(tmp, v):
    root = os.path.join(tmp, "ROOTM")
    leg = os.path.join(tmp, "GameF", "_viethoa_work", "_chung")
    work = os.path.join(tmp, "GameF", "_viethoa_work", "fsn-thu")
    writefile(os.path.join(leg, "khauvi", "KHAU_VI.md"), "# cũ\n")
    writefile(os.path.join(leg, "khauvi", "mau.tsv"), "thua\tthang\nA\tB\n")
    writefile(os.path.join(leg, "chuot.py"), "print('cu')\n")
    writefile(os.path.join(leg, "KINH_NGHIEM.md"), "# kn\n")
    writefile(os.path.join(work, "game.json"), json.dumps({"name": "F", "slug": "fsn-thu", "engine": "Khac"}))
    writefile(os.path.join(work, "HANDOFF.md"), "# HANDOFF\n")
    writefile(os.path.join(work, "tools", "fsn_adapter.py"), "# adapter\n")
    td = os.path.join(tmp, "ton-dong.md")
    writefile(td, "- việc 1\n- việc 2\n")
    os.makedirs(root)
    args = [v, "migrate", "--root", root, "--legacy-chung", leg, "--work", work, "--ton-dong", td, "--the-loai", "vn",
            "--boi-canh", "fantasy", "--en-mode", "all"]
    rc, out = run(args, tmp)
    check("migrate mặc định chỉ xem trước", rc == 0 and "Chưa ghi gì" in out and not os.path.exists(os.path.join(root, "_chung")), out)
    rc, out = run(args + ["--apply"], tmp)
    ch = os.path.join(root, "_chung")
    mau = open(os.path.join(ch, "khauvi", "mau.tsv"), encoding="utf-8").read()
    hand = open(os.path.join(work, "HANDOFF.md"), encoding="utf-8").read()
    g = json.load(open(os.path.join(work, "game.json"), encoding="utf-8"))
    check("migrate --apply: khẩu vị lên ROOT, pham_vi, TODO, config, chuot.py, việc tồn đọng, gom adapter, game.json",
          rc == 0 and "pham_vi" in mau.split("\n")[0] and "game:fsn-thu" in mau and os.path.exists(os.path.join(ch, "TODO.md"))
          and os.path.exists(os.path.join(ch, "config.json")) and os.path.exists(os.path.join(ch, "chuot.py"))
          and "- việc 1" in hand and os.path.exists(os.path.join(ch, "adapters", "khac", "fsn-thu", "fsn_adapter.py"))
          and g.get("the_loai") == "vn" and g.get("en_mode") == "all"
          and glob.glob(os.path.join(ch, "backup", "migrate-*", "migrate.txt")), out)
    rc, out = run(args + ["--apply"], tmp)
    hand = open(os.path.join(work, "HANDOFF.md"), encoding="utf-8").read()
    check("migrate chạy lại không chèn trùng việc tồn đọng", hand.count("ton-dong-tu-skill") == 1, out)
    root2 = os.path.join(tmp, "ROOTM2")
    writefile(os.path.join(root2, "_chung", "khauvi", "KHAU_VI.md"), "# hạt giống\n")
    writefile(os.path.join(root2, "_chung", "khauvi", "mau.tsv"), "thua\tthang\tly_do\tpham_vi\tnguon\nX\tY\tz\tchung\tseed\n")
    writefile(os.path.join(root2, "_chung", "KINH_NGHIEM.md"), "# kn mới\n")
    args2 = [v, "migrate", "--root", root2, "--legacy-chung", leg, "--work", work, "--polish-done", "9-11"]
    rc, out = run(args2, tmp)
    check("migrate xem trước: báo gộp khẩu vị cũ, cảnh báo config thiếu root_win/bang_tien_do",
          "gộp khẩu vị cũ" in out and "root_win trống" in out and "bang_tien_do trống" in out, out)
    rc, out = run(args2 + ["--apply"], tmp)
    k2 = os.path.join(root2, "_chung")
    kvm = open(os.path.join(k2, "khauvi", "KHAU_VI.md"), encoding="utf-8").read()
    mau2 = open(os.path.join(k2, "khauvi", "mau.tsv"), encoding="utf-8").read()
    kn2 = open(os.path.join(k2, "KINH_NGHIEM.md"), encoding="utf-8").read()
    st = json.load(open(os.path.join(work, "state.json"), encoding="utf-8"))
    check("migrate gộp: KHAU_VI cũ nối vào, mau.tsv thêm cặp cũ kèm pham_vi, KINH_NGHIEM cũ nối, đánh dấu lô đã chuốt",
          rc == 0 and "# cũ" in kvm and "# hạt giống" in kvm and "A\tB\t\tgame:fsn-thu" in mau2 and "X\tY" in mau2
          and "# kn" in kn2.replace("# kn mới", "") and st["polish"]["done"] == [9, 10, 11], out)
    rc, out = run(args2 + ["--apply"], tmp)
    kvm2 = open(os.path.join(k2, "khauvi", "KHAU_VI.md"), encoding="utf-8").read()
    check("migrate gộp chạy lại không nối trùng", kvm2.count("# cũ") == 1, out)


def kv_game_a(g):
    writefile(os.path.join(g, "script", "ch1.json"), json.dumps([
        {"id": "l1", "speaker": "ユキ", "text": "おはよう、ハル。", "page": "1"},
        {"id": "l2", "text": "朝の光が差し込む。", "page": "2"},
        {"id": "l3", "text": "暖かい。", "page": "2"},
        {"id": "l4", "speaker": "ハル", "text": "……おはよう。", "voice": "h01.ogg", "page": "3"},
        {"id": "l5", "speaker": "ユキ", "text": "（秘密）", "page": "4"}], ensure_ascii=False, indent=2))


def full_pipeline(name, tmp, v, kv, w, g, init_args, extract_args, pay, gate, fix=None):
    os.makedirs(w, exist_ok=True)
    run([v, "init", "--name", name] + init_args, w)
    setcfg(w, batch_dialogue=4, batch_short=4)
    rc, out = run([kv, "extract", "--game", g, "--work", w] + extract_args, w)
    rc2, out2 = run([kv, "roundtrip", "--game", g, "--work", w], w)
    check(f"{name}: kv extract + khứ hồi KHỚP 100%", rc == 0 and rc2 == 0 and "KHỚP 100%" in out2, out + out2)
    run([v, "plan"], w)
    if fix:
        fix(w)
    rc, out = run([v, "write", "-"], w, pay)
    check(f"{name}: write", rc == 0, out)
    rc, out = run([v, "check"], w)
    check(f"{name}: check 0 lỗi chặn", rc == 0 and "LỖI CHẶN: 0" in out, out)
    rc, out = run([v, "qa", "sample", "--gate", gate, "--seed", "1"], w)
    ids = sorted(glob.glob(os.path.join(w, "reports", f"qa-{gate}-*.ids.json")))[-1]
    (judge_t3 if gate == "T3" else judge_tsv)(os.path.join(w, "reports", "gk.tsv"), ids)
    rc, out = run([v, "qa", "score", os.path.join(w, "reports", "gk.tsv"), "--ids", ids], w)
    check(f"{name}: cổng {gate}", rc == 0 and "ĐẠT" in out, out)
    rc, out = run([v, "export"], w)
    check(f"{name}: export đủ", rc == 0, out)
    rc, out = run([kv, "apply", "--game", g, "--work", w, "--name", "p1"], w)
    pd = os.path.join(w, "patch", "p1")
    rc2, out2 = run([v, "patchkit", pd, "--game", g], w)
    check(f"{name}: apply + patchkit", rc == 0 and rc2 == 0 and os.path.exists(os.path.join(pd, "manifest_sha.txt")), out + out2)
    return pd


def test_games4(tmp, v, adp, kv):
    # (a) visual novel Nhat 18+: trang, long tieng, =gop, cau minor
    g, w = os.path.join(tmp, "GA"), os.path.join(tmp, "Viet hoa game", "ga")
    kv_game_a(g)

    def fix_a(w):
        setcfg(w, gop_ok=True)
        run([v, "minor", "add", "script/ch1.json:l5", "--note", "thử"], w)
    pay = ("@@scene ch1 ! loai=tinh_cam\nBuổi sáng, Yuki gọi Haru dậy. Cảm xúc: Yuki vui, Haru còn ngái ngủ.\n"
           "@@pair ユキ | ハル | mình | Haru | bạn thơ ấu\n@@pair ハル | ユキ | mình | Yuki | bạn thơ ấu\n"
           "@@ script/ch1.json:l1\nChào buổi sáng, Haru.\n@@ script/ch1.json:l2\nÁnh nắng sớm len vào phòng, ấm áp lạ thường.\n"
           "@@ script/ch1.json:l3\n=gộp\n@@ script/ch1.json:l4\n…Chào buổi sáng.\n")
    pd = full_pipeline("Game (a) VN Nhật 18+", tmp, v, kv, w, g, ["--kind", "18", "--lang", "ja", "--the-loai", "vn", "--boi-canh", "hien_dai"],
                       ["--files", "script/*.json", "--map", "speaker=speaker,page=page,voice=voice"], pay, "T2", fix_a)
    out_a = json.load(open(os.path.join(pd, "files", "script", "ch1.json"), encoding="utf-8"))
    check("Game (a): =gộp ghi rỗng, câu minor giữ nguyên gốc", out_a[2]["text"] == "" and out_a[4]["text"] == "（秘密）"
          and out_a[1]["text"].startswith("Ánh nắng"), out_a)
    # (b) kiem hiep goc Trung, bang CSV
    g, w = os.path.join(tmp, "GB"), os.path.join(tmp, "Viet hoa game", "gb")
    writefile(os.path.join(g, "loc", "strings.csv"), "key,spk,zh,en,type\nskill_1,,九阴真经,Nine Yin Manual,data\n"
              "skill_2,,攻击力提升150%，眩晕2回合。,,data\nskill_3,,恢复全体队友30点生命。,,data\n"
              "skill_4,,《九阴真经》第一重：内力+20。,,data\n"
              "dlg_1,李,在下见过阁下。,I greet you.,dialogue\ndlg_2,李,师姐，等我一下。,\"Senior sister, wait for me.\",dialogue\n")

    def fix_b(w):
        rc, out = run([v, "write", "-"], w, "@@ loc/strings.csv:skill_1\n《Cửu Âm Chân Kinh》\n")
        check("Game (b): 《》 còn trong bản dịch → chặn", rc == 2 and "còn chữ/dấu gốc" in out, out)
        rc, out = run([v, "write", "-", "--dry"], w, "@@ loc/strings.csv:skill_2\nTăng 115% sức công, gây choáng 3 lượt.\n"
                                                    "@@ loc/strings.csv:skill_3\nHồi 300 điểm sinh lực cho một đồng đội.\n")
        check("Game (b): sai số liệu trong lô kỹ năng → cảnh báo số liệu lệch", "số liệu lệch" in out
              and "skill_2" in out and "150" in out and "skill_3" in out, out)
        rc, out = run([v, "next"], w)
        check("Game (b): lô kỹ năng là lô ngắn (dữ liệu)", "ngắn" in out and "skill_2" not in out.split("#> ---")[0], out)
    pay = ("@@pair 李 | * | tại hạ/đệ | các hạ/sư tỷ | giang hồ\n@@ loc/strings.csv:skill_1\n“Cửu Âm Chân Kinh”\n"
           "@@ loc/strings.csv:skill_2\nTăng 150% sức công, gây choáng 2 lượt.\n"
           "@@ loc/strings.csv:skill_3\nHồi 30 điểm sinh lực cho toàn đội.\n"
           "@@ loc/strings.csv:skill_4\n“Cửu Âm Chân Kinh” tầng một: nội lực +20.\n"
           "@@ loc/strings.csv:dlg_1\nTại hạ xin ra mắt các hạ.\n@@ loc/strings.csv:dlg_2\nSư tỷ, đợi đệ với.\n")
    pd = full_pipeline("Game (b) kiếm hiệp Trung", tmp, v, kv, w, g, ["--lang", "zh", "--the-loai", "rpg", "--boi-canh", "co_trang"],
                       ["--files", "loc/*.csv", "--key-col", "key", "--text-col", "zh", "--en-col", "en",
                        "--map", "speaker=spk,kind=type"], pay, "F2", fix_b)
    csvt = open(os.path.join(pd, "files", "loc", "strings.csv"), encoding="utf-8").read()
    check("Game (b): CSV ghi bản dịch vào cột nguồn", "Sư tỷ, đợi đệ với." in csvt and "“Cửu Âm Chân Kinh”" in csvt, csvt)
    # (c) RPG Maker MV khong ten nguoi noi, mo ta dai
    g = os.path.join(tmp, "GC")
    mz_game(g, mv=True)
    d = os.path.join(g, "www", "data")
    mp = json.load(open(os.path.join(d, "Map001.json"), encoding="utf-8"))
    mp["events"][1]["name"] = "宝箱イベントその一"
    mp["events"][1]["pages"][0]["list"] = [
        {"code": 101, "indent": 0, "parameters": ["Actor1", 2, 0, 2]},
        {"code": 401, "indent": 0, "parameters": ["今日はいい天気だね。"]},
        {"code": 108, "indent": 0, "parameters": ["ここは開発用のメモです。プレイヤーには見えない。"]},
        {"code": 356, "indent": 0, "parameters": ["Popup 宝箱を見つけた！中には何もなかったけれど、気分は悪くない。"]},
        {"code": 0, "indent": 0, "parameters": []}]
    json.dump(mp, open(os.path.join(d, "Map001.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump([None, {"id": 1, "name": "ポーション", "description": "体力を少し回復する。戦闘中でも使える便利な薬だ。"}],
              open(os.path.join(d, "Items.json"), "w", encoding="utf-8"), ensure_ascii=False)
    writefile(os.path.join(g, "www", "js", "plugins.js"), 'var $plugins = [{"name":"Msg","parameters":{"text":"これはプラグインの中にある日本語の長い文章です。表示される。"}}];\n')
    w = os.path.join(tmp, "Viet hoa game", "gc")
    os.makedirs(w)
    run([v, "init", "--name", "GC", "--lang", "ja", "--the-loai", "rpg"], w)
    rc, out = run([adp, "extract", "--game", g, "--work", w], w)
    src = [json.loads(x) for x in open(os.path.join(w, "src.jsonl"), encoding="utf-8")]
    sp = [e for e in src if e["id"] == "Map001.json:e1.p0.0"]
    desc = [e for e in src if e["id"] == "Items.json:1.description"]
    check("Game (c) MV: người nói theo ảnh mặt; mô tả có maxlen×maxlines", sp and sp[0].get("speaker") == "Actor1#2"
          and desc and desc[0].get("maxlines") == 2 and desc[0].get("maxlen", 0) >= 20, src)
    rc, out = run([v, "coverage", g], w)
    check("Game (c): coverage báo plugins.js chưa trích, Map001 trích thiếu (lệnh 356), bỏ tên sự kiện và ghi chú 108",
          rc == 1 and "plugins.js" in out and "TRÍCH THIẾU: www/data/Map001.json" in out and "宝箱イベント" not in out
          and "開発用" not in out, out)
    writefile(os.path.join(w, "coverage_skip.txt"), "www/js/plugins.js  # thử: bỏ có lý do\n"
              "www/data/Map*.json  # thử: lệnh 356 Popup chỉ dùng khi gỡ lỗi\n")
    rc, out = run([v, "coverage", g], w)
    check("Game (c): coverage_skip (cả mẫu *) → đạt P1", rc == 0 and "CHƯA TRÍCH 0" in out and "TRÍCH THIẾU 0" in out, out)
    vi = {"今日はいい天気だね。": "Hôm nay trời đẹp ghê.",
          "体力を少し回復する。戦闘中でも使える便利な薬だ。": "Hồi một ít thể lực. Loại thuốc tiện lợi, dùng được cả trong trận đấu, ai cũng nên mang theo vài lọ."}
    pay = "@@scene Map001\nBuổi sáng ở làng.\n@@scene CE1\nMở đầu.\n@@pair Actor1#2 | * | tớ | cậu | bạn\n" + "".join(
        f"@@ {e['id']}\n{vi.get(e['src']) or VI.get(e['src']) or 'Thử'}\n" for e in src)
    rc, out = run([v, "write", "-"], w, pay)
    check("Game (c): write", rc == 0, out)
    rc, out = run([v, "check"], w)
    check("Game (c): check 0 lỗi chặn", "LỖI CHẶN: 0" in out, out)
    rc, out = run([v, "qa", "sample", "--gate", "F2", "--seed", "1"], w)
    ids = sorted(glob.glob(os.path.join(w, "reports", "qa-F2-*.ids.json")))[-1]
    judge_tsv(os.path.join(w, "reports", "gk.tsv"), ids)
    rc, out = run([v, "qa", "score", os.path.join(w, "reports", "gk.tsv"), "--ids", ids], w)
    check("Game (c): cổng F2", rc == 0 and "ĐẠT" in out, out)
    run([v, "export"], w)
    rc, out = run([adp, "apply", "--game", g, "--work", w, "--name", "p1"], w)
    it = json.load(open(os.path.join(w, "patch", "p1", "files", "www", "data", "Items.json"), encoding="utf-8"))
    lines = it[1]["description"].split("\n")
    rc2, out2 = run([v, "patchkit", os.path.join(w, "patch", "p1"), "--game", g], w)
    check("Game (c): apply ngắt dòng mô tả theo bề rộng; patchkit", rc == 0 and len(lines) == 2
          and all(len(x) <= desc[0]["maxlen"] for x in lines) and rc2 == 0, lines)
    # (d) AAA goc Anh: plural ICU/Unreal, phu de dur_ms, tieng ho
    g, w = os.path.join(tmp, "GD"), os.path.join(tmp, "Viet hoa game", "gd")
    writefile(os.path.join(g, "ui", "menu.json"), json.dumps({"count": "{n, plural, one {# item} other {# items}}",
                                                              "cats": "{N}|plural(one=cat,other=cats)", "start": "Start Game",
                                                              "join": "{G}|gender(He,She) joined the party."}))
    writefile(os.path.join(g, "subs", "ch1.json"), json.dumps([
        {"id": "s1", "speaker": "Cole", "text": "Reloading!", "dur": "800"},
        {"id": "s2", "speaker": "Cole", "text": "We have to move before they find us, there is no time left.", "dur": "1500"}]))

    def fix_d(w):
        setcfg(w, cps_max=17)
        rc, out = run([v, "write", "-"], w, "@@ ui/menu.json:count\n{n, plural, other {# món}}\n"
                                            "@@ subs/ch1.json:s2\nWe have to move before they find us, there is no time left.\n")
        check("Game (d): plural thiếu khóa → chặn; câu chưa dịch → cảnh báo", rc == 2 and "khung số nhiều lệch" in out
              and "có thể chưa dịch" in out, out)
        rc, out = run([v, "next"], w)
        check("Game (d): nguồn EN → en_mode none, không in EN", "#> EN:" not in out, out)
    pay = ("@@ ui/menu.json:count\n{n, plural, one {# món đồ} other {# món đồ}}\n@@ ui/menu.json:cats\n{N}|plural(one=con mèo,other=con mèo)\n"
           "@@ ui/menu.json:start\nBắt đầu\n@@ ui/menu.json:join\n{G}|gender(Anh ấy,Cô ấy) đã vào đội.\n@@ subs/ch1.json:s1\nNạp đạn!\n"
           "@@ subs/ch1.json:s2\nPhải di chuyển ngay trước khi bọn chúng tìm ra chúng ta, không còn thời gian nữa đâu.\n")
    full_pipeline("Game (d) AAA gốc Anh", tmp, v, kv, w, g, ["--lang", "en", "--the-loai", "hanh_dong", "--boi-canh", "hien_dai"],
                  ["--files", "ui/*.json;subs/*.json", "--map", "speaker=speaker,dur_ms=dur"], pay, "T3", fix_d)
    rc, out = run([v, "write", "-"], w, "@@ subs/ch1.json:s2\nPhải di chuyển ngay trước khi bọn chúng tìm ra chúng ta, "
                                        "không còn thời gian nữa đâu, nhanh lên nào mọi người ơi.\n")
    check("Game (d): phụ đề quá nhanh → cảnh báo", "phụ đề quá nhanh" in out, out)


def test_docs():
    """Quet tai lieu goi skill: khong ten game, khong duong dan cung, khong cau phan dinh uu tien; lenh va tep duoc nhac deu co."""
    pkg = os.path.normpath(os.path.join(HERE, ".."))
    if not os.path.exists(os.path.join(pkg, "SKILL.md")):
        print("(bỏ qua kiểm tài liệu: không chạy trong gói skill)")
        return
    docs = [os.path.join(pkg, "SKILL.md")] + sorted(glob.glob(os.path.join(pkg, "references", "*.md"))) \
        + sorted(glob.glob(os.path.join(pkg, "references", "hoso", "*.md"))) + [os.path.join(pkg, "references", "khauvi-seed", "KHAU_VI.md")]
    text = {d: open(d, encoding="utf-8").read() for d in docs}
    names = re.compile(r"Fate|Shirou|Saber|Archer|Lancer|Gilgamesh|Kirei|Caster|\bRin\b|Mitsuzuri|Legend of Mortal|LegendOfMortal"
                       r"|Triệu Hoạt|Đường Môn|Somnium|Cursed Armor|Bảo Khí", re.I)
    bad = [(os.path.basename(d), m.group(0)) for d, t in text.items() for m in names.finditer(t)]
    check("tài liệu: 0 tên riêng của game nào", not bad, bad)
    paths = re.compile(r"[A-Za-z]:\\[A-Za-z]|\$HOME/mnt|https?://|claude\.ai/")
    bad = [(os.path.basename(d), m.group(0)) for d, t in text.items() for m in paths.finditer(t)]
    check("tài liệu: 0 đường dẫn tuyệt đối hay URL", not bad, bad)
    prio = re.compile(r"ưu tiên hơn|theo các mục ở trên|trái với lõi|đè lên luật|ghi đè luật|thắng luật|luật nào thắng|thu hẹp luật", re.I)
    bad = [(os.path.basename(d), m.group(0)) for d, t in text.items() for m in prio.finditer(t)]
    check("tài liệu: 0 câu phân định ưu tiên giữa các tệp luật", not bad, bad)
    rc, out = run([os.path.join(HERE, "vgk.py"), "-h"], HERE)
    cmds = set(re.findall(r"\{([a-z,-]+)\}", out)[0].split(","))
    mig = {d: open(d, encoding="utf-8").read() for d in glob.glob(os.path.join(pkg, "scripts", "migrate", "*.md"))}
    used = {m for t in list(text.values()) + list(mig.values()) for m in re.findall(r"vgk\.py ([a-z][a-z-]*)", t)}
    check("tài liệu: mọi lệnh vgk.py được nhắc đều có", used <= cmds, sorted(used - cmds))
    known = {"game.json", "src.jsonl", "plan.json", "tr.jsonl", "glossary.tsv", "xungho.tsv", "giong.tsv", "scenes.tsv", "neo.tsv",
             "minor_ids.txt", "glossary_skip.txt", "coverage_skip.txt", "coverage_ignore.txt", "notes.md", "HANDOFF.md", "log.md", "state.json",
             "export.json", "export_meta.json", "manifest.txt", "manifest_sha.txt", "them_moi.txt", "game_path.txt",
             "CAI_VIETHOA.bat", "GO_VIETHOA.bat", "DON_DEP.bat", "KINH_NGHIEM.md", "TODO.md", "config.json", "hieu_chuan.tsv", "p4.json",
             "rpgmv_settings.json", "kv_settings.json", "qa.tsv", "han_viet.tsv", "chuot.py", "plugins.js", "System.json",
             "Map001.json", "gamefont.css", "Assembly-CSharp.dll", "GameAssembly.dll", "global-metadata.dat", "Scene.pck",
             "Gameexe.dat", "SiglusEngine.exe", "BGI.exe", "root.pfs", "patch.xp3", "package.nw", "Game.rgss3a",
             "rmmz_core.js", "rpg_core.js", "UnityPlayer.dll", ".ids.json", "sotay.md", "phieu.tsv"}
    files = {os.path.basename(f) for f in glob.glob(os.path.join(pkg, "**", "*"), recursive=True)}
    missing = []
    for d, t in text.items():
        for m in re.findall(r"`([^`\s]*?([\w.-]+\.(?:md|tsv|json|jsonl|txt|py|bat)))`", t):
            full, base = m
            if "<" in full or "*" in full or base in known or base in files:
                continue
            missing.append((os.path.basename(d), full))
        for m in re.findall(r"`((?:references|scripts)/[\w./-]+)`", t):
            if "*" not in m and not os.path.exists(os.path.join(pkg, m)):
                missing.append((os.path.basename(d), m))
    check("tài liệu: mọi tệp được nhắc đều có trong gói hoặc do init/migrate/lệnh tạo ra", not missing, missing)
    n_skill = text[os.path.join(pkg, "SKILL.md")].count("\n")
    hoso = [d for d in docs if os.sep + "hoso" + os.sep in d]
    over = [(os.path.basename(d), text[d].count("\n")) for d in hoso if text[d].count("\n") > 150]
    noneo = [os.path.basename(d) for d in hoso + [os.path.join(pkg, "references", "quy-tac-dich.md")] if "\n## NEO" not in text[d]]
    check("SKILL.md ≤250 dòng; mỗi hồ sơ ≤150 dòng và có mục NEO", n_skill <= 250 and not over and not noneo,
          (n_skill, over, noneo))




def test_ko_font(tmp, v):
    # nguon tieng Han: chu Hangul sot bi chan, ung vien ten bo tieu tu
    w = os.path.join(tmp, "Viet hoa game", "ko")
    os.makedirs(w)
    run([v, "init", "--name", "KO", "--lang", "ko", "--the-loai", "khac"], w)
    rows = [{"id": f"k{i}", "src": t, "speaker": "민수", "scene": "s1"} for i, t in
            enumerate(["지수는 어디 있어?", "지수가 왔어.", "지수를 봤어?", "지수는 착해.", "지수의 집이야."])]
    writefile(os.path.join(w, "src.jsonl"), jl(rows))
    run([v, "plan"], w)
    rc, out = run([v, "write", "-"], w, "@@ k0\nJisu ở đâu rồi? 지수\n")
    check("ko: chữ Hangul sót → chặn", rc == 2 and "còn chữ/dấu gốc" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ k0\nJisu ở đâu rồi?\n")
    check("ko: bản dịch sạch → ghi", rc == 0, out)
    rc, out = run([v, "term", "candidates", "--min", "5"], w)
    check("ko: ứng viên tên bỏ tiểu từ (지수는/지수가… → 지수)", "지수\t5" in out, out)
    # P4 chua du cap → chua dat
    writefile(os.path.join(w, "reports", "p.tsv"), "pair_id\tngu_canh\ta\tb\tchon\tcan\tnguon\np1\tx\ta\tb\tA\tB\tthử\n")
    writefile(os.path.join(w, "reports", "j.tsv"), "p1\tA\tB\n")
    rc, out = run([v, "qa", "calibrate", "--pairs", "reports/p.tsv", "--judge", "reports/j.tsv"], w)
    check("P4: chưa đủ 40 cặp → CHƯA ĐẠT", "CHƯA ĐẠT" in out and "cần ≥40 cặp" in out, out)
    # font --text: dung font co san tren may chay test (neu co)
    font = next((f for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:\\Windows\\Fonts\\arial.ttf")
                 if os.path.exists(f)), None)
    if not font:
        print("(bỏ qua kiểm font --text: không thấy font mẫu)")
        return
    writefile(os.path.join(w, "e1.json"), json.dumps({"a": "Thử tiếng Việt: ắ ặ ữ “…”", "b": "漢"}, ensure_ascii=False))
    writefile(os.path.join(w, "e2.json"), json.dumps({"a": "Thử tiếng Việt: ắ ặ ữ “…”"}, ensure_ascii=False))
    rc, out = run([v, "font", font, "--text", "e1.json"], w)
    rc2, out2 = run([v, "font", font, "--text", "e2.json"], w)
    check("font --text: ký tự đang dùng thiếu trong font → exit 1; đủ → exit 0",
          rc == 1 and "thiếu trong font 1" in out and rc2 == 0 and "thiếu trong font 0" in out2, out + out2)


# ---------------------------------------------------------------- 2.1.0
def test_v21(tmp, v):
    """Dau kieu Nhat bi chan, '……' tu chuan hoa, canh bao thieu dau ket / dau hoi / cau nen, cong dinh ky tat mac dinh."""
    w = os.path.join(tmp, "Viet hoa game", "v21")
    os.makedirs(w)
    run([v, "init", "--name", "V21", "--lang", "ja", "--the-loai", "vn", "--en-mode", "all"], w)
    setcfg(w, batch_dialogue=2, require_emotion=False, require_scene_summary=False)
    rows = [
        {"id": "a1", "src": "⸺⸺来る。", "speaker": "凛", "scene": "c1", "en": "It's coming."},
        {"id": "a2", "src": "そういうこと……", "speaker": "凛", "scene": "c1", "en": "That's how it is..."},
        {"id": "a3", "src": "見てたんでしょ", "speaker": "凛", "scene": "c1", "en": "You saw that, right?"},
        {"id": "a4", "src": "それでいい。", "speaker": "凛", "scene": "c1", "en": "That's fine."},
        {"id": "a5", "src": "だから他のマスターは外からやってくる連中が大半の筈。", "speaker": "凛", "scene": "c1",
         "en": "Most of the other Masters will be coming from the outside, so they wouldn't be at my school at all."},
        {"id": "a6", "src": "行くわよ、、", "speaker": "凛", "scene": "c1", "en": "Let's go"},
        {"id": "a7", "src": "それでは失礼します。", "speaker": "凛", "scene": "c1", "en": "Can I go play now?"},
        {"id": "a8", "src": "「⸺⸺⸺⸺」", "speaker": "凛", "scene": "c1"},
        {"id": "a9", "src": "……", "speaker": "凛", "scene": "c1"},
    ]
    for k in range(4):
        rows.append({"id": f"b{k}", "src": f"台詞{k}。", "speaker": "士郎", "scene": "c2"})
    writefile(os.path.join(w, "src.jsonl"), jl(rows))
    run([v, "plan"], w)
    rc, out = run([v, "write", "-"], w, "@@ a1\n⸺⸺Nó tới rồi.\n")
    check("2.1: ⸺ trong bản dịch → chặn 'dấu Nhật'", rc == 2 and "dấu Nhật" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ a1\n—Nó tới rồi.\n@@ a2\nThì ra là vậy……\n")
    tr = [json.loads(x) for x in open(os.path.join(w, "tr.jsonl"), encoding="utf-8")]
    a2 = [x for x in tr if x.get("id") == "a2"]
    check("2.1: '……' tự thành '…'; gạch đầu câu → cảnh báo", rc == 0 and a2 and a2[-1].get("vi") == "Thì ra là vậy…"
          and "mở câu bằng gạch" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ a3\nLúc đó cậu thấy rồi chứ gì\n@@ a4\nVậy là được.\n@@ a5\nMaster khác đến từ ngoài.\n"
                  "@@ a6\nĐi thôi nào\n@@ a7\nVậy em xin phép về.\n")
    check("2.1: thiếu dấu kết, thiếu dấu hỏi, câu nén → cảnh báo; gốc đứt bằng 、 → không báo thiếu dấu kết",
          rc == 0 and "thiếu dấu kết: 1 — a3" in out and "thiếu dấu hỏi: 1 — a3" in out and "câu nén: 1 — a5" in out
          and "a4" not in out and "a6" not in out and "a7" not in out, out)
    run([v, "write", "-"], w, "".join(f"@@ b{k}\nCâu {k}.\n" for k in range(4)))
    rc, out = run([v, "qa", "due"], w)
    check("2.1: cổng định kỳ T2/T3 tắt mặc định", "T2 (" not in out and "T3 (" not in out, out)
    run([v, "pair", "set", "凛", "士郎", "tao", "mày", "--note", "thử"], w)
    run([v, "pair", "set", "凛", "桜", "tôi", "em", "--note", "thử"], w)
    rc, out = run([v, "write", "-"], w, "@@ a4 >士郎,桜\nTao bảo mày rồi.\n")
    rc2, out2 = run([v, "write", "-"], w, "@@ a4 >士郎\nTao bảo mày rồi.\n@@term 魔術 = ma thuật\n")
    gl = open(os.path.join(w, "glossary.tsv"), encoding="utf-8").read()
    check("2.1: nhiều người nghe '>A,B' kiểm từng người; '@@term gốc = việt' được nhận",
          rc == 2 and "xưng hô cấm" in out and "'士郎,桜'" not in out and rc2 == 0
          and "魔術\tma thuật" in gl, out + out2 + gl)
    # hai tien trinh ghi cung WORK cung luc: khoa WORK giu cho ca hai deu duoc ghi, state.json con hop le
    procs = [subprocess.Popen([sys.executable, v, "write", "-"], cwd=w, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, encoding="utf-8") for _ in range(2)]
    procs[0].stdin.write("@@ b0\nCâu không một.\n"); procs[1].stdin.write("@@ b1\nCâu không hai.\n")
    # tien trinh 2 dang cho stdin: khong duoc giu khoa WORK trong luc cho (neu giu thi tien trinh 1 bi treo)
    procs[0].stdin.close()
    try:
        procs[0].wait(timeout=60)
        hung = False
    except subprocess.TimeoutExpired:
        hung = True
        procs[0].kill()
    procs[1].stdin.close(); procs[1].wait(timeout=60)
    check("2.1: không giữ khóa WORK trong lúc chờ stdin", not hung)
    trl = [json.loads(x) for x in open(os.path.join(w, "tr.jsonl"), encoding="utf-8") if x.strip()]
    last = {}
    for x in trl:
        last[x["id"]] = x.get("vi")
    okst = True
    try:
        json.load(open(os.path.join(w, "state.json"), encoding="utf-8"))
    except Exception:
        okst = False
    check("2.1: hai lệnh write cùng lúc trên một WORK đều được ghi, state.json hợp lệ",
          last.get("b0") == "Câu không một." and last.get("b1") == "Câu không hai." and okst, last)
    run([v, "write", "-", "--force", "b2,b3"], w, "@@ b2\n⸺⸺Nó tới rồi……\n@@ b3\nAnh ta lao tới⸺⸺⸺\n")
    rc, out = run([v, "fix-dau", "--apply"], w)
    trl = [json.loads(x) for x in open(os.path.join(w, "tr.jsonl"), encoding="utf-8") if x.strip()]
    last = {}
    for x in trl:
        last[x["id"]] = x.get("vi")
    check("2.1: fix-dau đổi dấu kiểu Nhật trong bản dịch cũ", last.get("b2") == "Nó tới rồi…" and last.get("b3") == "Anh ta lao tới—",
          out + str(last))
    rc, out = run([v, "export", "--out", "ex.json", "--allow-missing"], w)
    ex = json.load(open(os.path.join(w, "ex.json"), encoding="utf-8")) if os.path.exists(os.path.join(w, "ex.json")) else {}
    check("2.1: mục tự động chỉ có ⸺ / …… → “…” / …", ex.get("a8") == "“…”" and ex.get("a9") == "…", ex)
    rc, out = run([v, "version"], w)
    check("2.5: version", "2.5.0" in out, out)


def test_v22(tmp, v):
    """2.2: ho so va xung ho theo moc (khong lo tinh tiet), bi mat lo_tu, gioi tinh, phieu bao, doc lai,
    doc chuong, cau anh huong + sua, quet sot nghiem (nhi phan, goi, UTF-16, Shift-JIS), quet ban da va, ban danh dau."""
    w = os.path.join(tmp, "Viet hoa game", "v22")
    os.makedirs(w)
    run([v, "init", "--name", "V22", "--lang", "ja", "--the-loai", "vn", "--en-mode", "all"], w)
    check("2.2: init tạo sotay.md", os.path.exists(os.path.join(w, "sotay.md")))
    setcfg(w, batch_dialogue=4, require_emotion=False, require_scene_summary=False,
           doc_chuong_dau=6, doc_chuong_sau=6, phieu_toi_da=3)
    rows = [
        {"id": "x1", "src": "僕が君を守る。", "speaker": "晶", "scene": "s1", "en": "I'll protect you."},
        {"id": "x2", "src": "ありがとう。", "speaker": "凛", "scene": "s1"},
        {"id": "x3", "src": "行こう。", "speaker": "晶", "scene": "s1"},
        {"id": "x4", "src": "うん。", "speaker": "凛", "scene": "s1"},
        {"id": "x5", "src": "実は……私、女なの。", "speaker": "晶", "scene": "s2"},
        {"id": "x6", "src": "えっ。", "speaker": "凛", "scene": "s2"},
        {"id": "x7", "src": "明日香という名前を知ってる？", "speaker": "晶", "scene": "s2"},
        {"id": "x8", "src": "知らない。", "speaker": "凛", "scene": "s2"},
        {"id": "x9", "src": "明日香、ありがとう。", "speaker": "凛", "scene": "s3"},
        {"id": "x10", "src": "どういたしまして。", "speaker": "晶", "scene": "s3"},
        {"id": "x11", "src": "帰ろう。", "speaker": "凛", "scene": "s3"},
        {"id": "x12", "src": "うん。帰ろう。", "speaker": "晶", "scene": "s3"},
    ]
    writefile(os.path.join(w, "src.jsonl"), jl(rows))
    run([v, "plan"], w)
    run([v, "voice", "晶", "trầm, ít lời", "--gioi", "nam (vỏ)", "--tam-ly", "giấu thân phận"], w)
    rc, out = run([v, "voice", "晶", "--tu-canh", "s2", "--gioi", "nữ", "--tam-ly", "đã thú nhận là con gái"], w)
    run([v, "voice", "凛", "thẳng, ấm", "--gioi", "nữ"], w)
    rc2, out2 = run([v, "voice", "晶", "--tu-canh", "s9", "--gioi", "nữ"], w)
    check("2.2: hồ sơ theo mốc; mốc lạ bị từ chối", rc == 0 and "áp từ s2" in out and rc2 != 0 and "mốc 's9'" in out2, out + out2)
    run([v, "pair", "set", "晶", "凛", "tôi", "cậu"], w)
    run([v, "pair", "set", "晶", "凛", "tớ", "cậu", "--tu-canh", "s2"], w)
    run([v, "pair", "set", "凛", "晶", "tôi", "cậu"], w)
    rc, out = run([v, "pair", "set", "晶", "凛", "anh", "em", "--tu-canh", "s3"], w)
    check("2.2: pair set chặn xưng trái giới tính tại mốc", rc != 0 and "trái giới tính" in out, out)
    run([v, "term", "add", "明日香", "Asuka", "--type", "nhan_vat", "--note", "tên thật của 晶", "--lo-tu", "s3"], w)
    rc, out1 = run([v, "next", "--batch", "1"], w)
    rc, out2 = run([v, "next", "--batch", "2"], w)
    check("2.2: next chỉ in điều người đọc đã biết (trước mốc không lộ hồ sơ sau, ghi chú bí mật)",
          "nam (vỏ)" in out1 and "đã thú nhận" not in out1 and "xưng tớ" not in out1
          and "đã thú nhận" in out2 and "xưng tớ" in out2 and "明日香 = Asuka" in out2 and "tên thật" not in out2, out1 + out2)
    rc, out = run([v, "next", "--batch", "1"], w)
    rc, out = run([v, "write", "-"], w, "@@ ~1.1\nTớ sẽ bảo vệ cậu.\n@@ ~1.2\nLão phu cảm ơn.\n@@ ~1.3\nCậu ấy ngủ thiếp đi rồi, đi thôi.\n"
                  "@@ ~1.4\nỪ.\n@@bao ~1.2 Hồ sơ ghi 凛 thẳng mà cảnh này dịu hơn hẳn\n")
    check("2.2: tự xưng lệch bảng theo mốc; giới tính lệch hồ sơ; 'ngủ thiếp đi' không báo; @@bao thành phiếu",
          rc == 0 and "tự xưng khác bảng xưng hô: 1 — x1" in out and "giới tính lệch hồ sơ: 1 — x2" in out
          and "x3" not in out.split("giới tính lệch hồ sơ")[1] and "phiếu báo +1" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ x2\nCảm ơn cậu.\n@@ x3\nThiếp xin đi trước.\n")
    check("2.2: nhân vật đang mang vỏ nam xưng 'thiếp' → cảnh báo giới tính", "giới tính lệch hồ sơ: 1 — x3" in out, out)
    run([v, "write", "-"], w, "@@ x3\nĐi thôi.\n")
    rc, out = run([v, "phieu"], w)
    check("2.2: phieu liệt kê phiếu mở kèm id", "#1 [mở]" in out and "x2" in out and "dịu hơn" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ x5\nThật ra… tớ là con gái.\n@@ x6\nAsuka?\n")
    check("2.2: tên thật trước mốc lộ → chặn; câu sau mốc theo bảng mới không bị báo",
          rc == 2 and "lộ tình tiết" in out and "x6" in out and "tự xưng khác bảng" not in out, out)
    rc, out = run([v, "write", "-"], w, "@@ x6\nHả?\n@@ x7\nCậu có biết cái tên Asuka không?\n@@ x8\nKhông biết.\n")
    check("2.2: câu gốc có tên thật thì được dùng", rc == 0, out)
    rc, out = run([v, "doc-lai", "--n", "2"], w)
    check("2.2: doc-lai in N câu gần nhất", "ĐỌC LẠI 2" in out and "Không biết." in out and "Tớ sẽ" not in out, out)
    rc, out = run([v, "qa", "due"], w)
    check("2.2: đủ câu thoại mới → cổng đọc chương đến hạn", "C đọc chương" in out, out)
    rc, out = run([v, "doc-chuong"], w)
    check("2.2: doc-chuong in bài đọc, số đo, phiếu; tự chụp bible",
          "ĐỌC CHƯƠNG lần 1" in out and "BÀI ĐỌC" in out and "SỐ ĐO" in out and "PHIẾU MỞ" in out
          and os.path.exists(os.path.join(w, "bible_snap", "xungho.tsv")), out)
    run([v, "pair", "set", "凛", "晶", "tớ", "cậu", "--tu-canh", "s2"], w)
    run([v, "voice", "凛", "--tu-canh", "s2", "--tam-ly", "bối rối sau lời thú nhận"], w)
    rc, out = run([v, "anh-huong"], w)
    check("2.2: anh-huong thấy câu bị ảnh hưởng vì xưng hô và hồ sơ đổi",
          "Câu đã dịch bị ảnh hưởng: 2 · xưng hô đổi 2" in out, out)
    rc, out = run([v, "anh-huong", "--sua"], w)
    rc2, out2 = run([v, "sua", "next"], w)
    check("2.2: anh-huong --sua → sua next in câu cần sửa kèm bản hiện tại",
          "Đã thêm" in out and "SỬA LẠI" in out2 and "@@ x6" in out2 and "#> VI: Hả?" in out2 and "@@ x2" not in out2, out + out2)
    rc, out = run([v, "write", "-"], w, "@@ x6\nHả? Cậu nói gì cơ?\n@@ x8\nTớ không biết.\n")
    rc2, out2 = run([v, "sua", "status"], w)
    check("2.2: ghi lại câu thì rời danh sách sửa", rc == 0 and "Cần sửa: 0" in out2, out + out2)
    rc, out = run([v, "phieu", "dong", "1", "--tra-loi", "đã sửa hồ sơ"], w)
    rc2, out2 = run([v, "doc-chuong", "xong", "--ghi-chu", "thử"], w)
    rc3, out3 = run([v, "qa", "due"], w)
    rc4, out4 = run([v, "status"], w)
    check("2.2: đóng phiếu; doc-chuong xong ghi lần đọc, hết hạn cổng; status báo đọc chương",
          "Đã đóng 1" in out and "Đã ghi đọc chương lần 1" in out2 and "C đọc chương" not in out3 and "Đọc chương: 1 lần" in out4,
          out + out2 + out3 + out4)
    run([v, "write", "-"], w, "@@bao a\n@@bao b\n@@bao c\n")
    rc, out = run([v, "qa", "due"], w)
    check("2.2: nhiều phiếu mở → đọc chương sớm", "C đọc chương sớm (3 phiếu" in out, out)
    rc, out = run([v, "write", "-"], w, "@@ x9\nAsuka, cảm ơn cậu.\n")
    check("2.2: sau mốc lộ thì tên thật dùng tự do", rc == 0 and "lộ tình tiết" not in out, out)
    rc, out = run([v, "export", "--danh-dau", "--out", "dd.json"], w)
    ex = json.load(open(os.path.join(w, "dd.json"), encoding="utf-8"))
    check("2.2: export --danh-dau = ※ + câu gốc", ex.get("x1") == "※僕が君を守る。" and "bản đánh dấu" in out, out)
    with open(os.path.join(w, "xungho.tsv"), "a", encoding="utf-8") as f:
        f.write("凛\t*\t\tlão phu\tngươi\tthử\n")
    rc, out = run([v, "check"], w)
    check("2.2: check bắt bảng xưng hô trái giới tính", "xưng hô trái giới tính" in out, out)
    # --- quet sot nghiem
    g = os.path.join(tmp, "game22")
    writefile(os.path.join(g, "data", "Dialog.json"), json.dumps({"a": "僕が君を守る。", "b": "ありがとう。"}, ensure_ascii=False))
    writefile(os.path.join(g, "data", "System.json"), json.dumps({"yes": "はい", "no": "いいえ"}, ensure_ascii=False))
    os.makedirs(os.path.join(g, "bin"))
    with open(os.path.join(g, "bin", "strings.dat"), "wb") as f:
        f.write(b"\x00\x01\x02" * 50 + "ゲーム開始です".encode("utf-8") + b"\x00" * 40)
    with open(os.path.join(g, "bin", "Game.locres"), "wb") as f:
        f.write(b"\x00\x00\x07\x00" * 20 + (-4).to_bytes(4, "little", signed=True) + "開始だ".encode("utf-16-le") + b"\x00\x00" + b"\x00" * 16)
    with open(os.path.join(g, "bin", "old.dat"), "wb") as f:
        f.write(b"\x00\x05" * 60 + "こんにちは世界".encode("cp932") + b"\x00" * 30)
    import random as _r
    rr = _r.Random(7)
    with open(os.path.join(g, "data.pak"), "wb") as f:
        f.write(bytes(rr.randrange(256) for _ in range(70000)))
    with open(os.path.join(g, "img", "title_logo.png") if os.makedirs(os.path.join(g, "img")) is None else "", "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
    w2 = os.path.join(tmp, "Viet hoa game", "v22c")
    os.makedirs(w2)
    run([v, "init", "--name", "V22c", "--lang", "ja"], w2)
    writefile(os.path.join(w2, "src.jsonl"), jl([{"id": "d1", "src": "僕が君を守る。", "file": "data/Dialog.json"},
                                                 {"id": "d2", "src": "ありがとう。", "file": "data/Dialog.json"}]))
    rc, out = run([v, "coverage", g], w2)
    check("2.2: coverage nghiêm: nút ngắn sót, nhị phân có chữ (UTF-8, UTF-16 Unreal, Shift-JIS), tệp gói, ảnh",
          rc == 1 and "CHƯA TRÍCH 1" in out and "NHỊ PHÂN CÓ CHỮ 3" in out and "KHÔNG ĐỌC ĐƯỢC 1" in out
          and "data/System.json" in out and "Ảnh có thể có chữ: 1" in out and "Dialog.json" not in out.split("→")[1], out)
    writefile(os.path.join(w2, "coverage_skip.txt"), "data/System.json  # thử\nbin/*  # thử\n*.pak  # đã bung, thử\n")
    rc, out = run([v, "coverage", g], w2)
    check("2.2: coverage_skip (mẫu *) cho cả tệp gói → đạt", rc == 0 and "KHÔNG ĐỌC ĐƯỢC 0" in out, out)
    gv = os.path.join(tmp, "game22v")
    writefile(os.path.join(gv, "data", "Dialog.json"), json.dumps({"a": "Tớ sẽ bảo vệ cậu.", "b": "Cảm ơn."}, ensure_ascii=False))
    writefile(os.path.join(gv, "data", "Other.json"), json.dumps({"c": "まだ日本語"}, ensure_ascii=False))
    rc, out = run([v, "coverage", gv, "--sau-va"], w2)
    check("2.2: quét bản đã vá: còn chữ gốc → báo, exit 1", rc == 1 and "CÒN CHỮ GỐC 1 tệp" in out and "Other.json" in out, out)
    os.remove(os.path.join(gv, "data", "Other.json"))
    rc, out = run([v, "coverage", gv, "--sau-va"], w2)
    check("2.2: quét bản đã vá sạch → đạt", rc == 0 and "CÒN CHỮ GỐC 0 tệp" in out, out)


def test_v23(tmp, v):
    """2.3: khoi-dong in mot lan; write --tiep in lo ke; --phien khong in lai phan da in; cau lap o canh khac ('=', tu chep)."""
    root = os.path.join(tmp, "R23")
    ch = os.path.join(root, "_chung")
    os.makedirs(os.path.join(ch, "hoso"))
    shutil.copy(v, os.path.join(ch, "vgk.py"))
    got = []
    for nm in ("quy-tac-dich.md", "nguon-ja.md", "nguoi-lon.md"):
        for d in (os.path.join(HERE, "hoso"), os.path.join(HERE, "..", "references", "hoso"), os.path.join(HERE, "..", "references")):
            if os.path.isfile(os.path.join(d, nm)):
                shutil.copy(os.path.join(d, nm), os.path.join(ch, "hoso", nm))
                got.append(nm)
                break
    v3 = os.path.join(ch, "vgk.py")
    w = os.path.join(root, "v23")
    os.makedirs(w)
    run([v3, "init", "--name", "V23", "--lang", "ja", "--kind", "18"], w)
    setcfg(w, batch_dialogue=3, require_emotion=False, require_scene_summary=False)
    rows = [
        {"id": "a1", "src": "今日はいい天気ですね、本当に。", "speaker": "晶", "scene": "s1"},
        {"id": "a2", "src": "はい。", "speaker": "凛", "scene": "s1"},
        {"id": "a3", "src": "行こうか。", "speaker": "晶", "scene": "s1"},
        {"id": "b1", "src": "今日はいい天気ですね、本当に。", "speaker": "晶", "scene": "s2"},
        {"id": "b2", "src": "はい。", "speaker": "凛", "scene": "s2"},
        {"id": "b3", "src": "そうだね。", "speaker": "晶", "scene": "s2"},
        {"id": "c1", "src": "また明日。", "speaker": "凛", "scene": "s3"},
        {"id": "c2", "src": "うん。", "speaker": "晶", "scene": "s3"},
        {"id": "c3", "src": "はい。", "speaker": "凛", "scene": "s3"},
    ]
    writefile(os.path.join(w, "src.jsonl"), jl(rows))
    run([v3, "plan"], w)
    run([v3, "voice", "晶", "điềm đạm", "--gioi", "nam"], w)
    run([v3, "voice", "凛", "thẳng, ấm", "--gioi", "nữ"], w)
    run([v3, "pair", "set", "晶", "凛", "tớ", "cậu"], w)
    run([v3, "pair", "set", "凛", "晶", "tớ", "cậu"], w)
    rc, out = run([v3, "khoi-dong", "--batch", "1", "--den", "3", "--phien", "t1"], w)
    check("2.3: khoi-dong in một lần bible chung, hồ sơ nguồn, người lớn, sổ tay, đọc lại và lô đầu",
          rc == 0 and len(got) == 3 and all(f"===== {nm} =====" in out for nm in got) and "===== sotay.md" in out
          and "KHỞI ĐỘNG phiên t1" in out and "LÔ 1/3" in out and "HỒ SƠ NHÂN VẬT" in out and "--phien t1 --tiep" in out, out)
    rc, out = run([v3, "write", "-", "--phien", "t1", "--tiep"], w,
                  "@@ ~1.1\nHôm nay trời đẹp thật đấy.\n@@ ~1.2\nỪ.\n@@ ~1.3\nĐi thôi.\n")
    tail = out.split("LÔ KẾ TIẾP")[-1]
    check("2.3: write --tiep in luôn lô kế; câu lặp dài không xưng hô tự chép; lô kế không in lại hồ sơ, có gợi ý '='",
          rc == 0 and "tự chép 1 câu" in out and "LÔ 2/3" in tail and "HỒ SƠ NHÂN VẬT" not in tail
          and "Đã in ở lô trước trong phiên t1" in tail and "đã dịch ở cảnh khác: Ừ." in tail
          and "今日はいい天気" not in tail and "Ghi như lô trước" in tail, out)
    rc, out = run([v3, "write", "-", "--phien", "t1", "--tiep"], w, "@@ ~2.1\n=\n@@ ~2.2\nỪ nhỉ.\n")
    last = {}
    for ln in open(os.path.join(w, "tr.jsonl"), encoding="utf-8"):
        if ln.strip():
            r = json.loads(ln)
            last[r["id"]] = r["vi"]
    check("2.3: '=' dùng lại bản đã dịch ở cảnh khác; in lô 3",
          rc == 0 and last.get("b2") == "Ừ." and last.get("b1") == "Hôm nay trời đẹp thật đấy." and "LÔ 3/3" in out, out)
    rc, out = run([v3, "write", "-", "--phien", "t1", "--tiep"], w, "@@ ~3.1\n=\n")
    check("2.3: '=' khi không có bản ở cảnh khác → trả lại, chưa in lô kế",
          rc == 2 and "'=' chỉ dùng" in out and "CHƯA IN LÔ KẾ" in out, out)
    rc, out = run([v3, "write", "-", "--phien", "t1", "--tiep"], w, "@@ ~3.1\nHẹn mai gặp nhé.\n@@ ~3.2\nỪm.\n@@ ~3.3\n=\n")
    check("2.3: hết dải → báo dừng", rc == 0 and "HẾT DẢI" in out and last.get("c3") is None, out)
    rc, out = run([v3, "next", "--batch", "2", "--all"], w)
    check("2.3: next không --phien vẫn in đủ như cũ", "HỒ SƠ NHÂN VẬT" in out and "#> Ghi: vgk.py write -" in out, out)
    rc, out = run([v3, "status"], w)
    check("2.3: status đếm câu lặp ở cảnh khác", "lặp ở cảnh khác 3" in out, out)


def main():
    tmp = tempfile.mkdtemp(prefix="vgk-selftest-")
    try:
        chung = os.path.join(tmp, "Viet hoa game", "_chung")
        os.makedirs(chung)
        for f in ("vgk.py", "rpgmv_adapter.py"):
            shutil.copy(os.path.join(HERE, f), os.path.join(chung, f))
        kvsrc = os.path.join(HERE, "adapters", "kv", "kv_adapter.py")
        os.makedirs(os.path.join(chung, "adapters", "kv"))
        shutil.copy(kvsrc, os.path.join(chung, "adapters", "kv", "kv_adapter.py"))
        v = os.path.join(chung, "vgk.py")
        adp = os.path.join(chung, "rpgmv_adapter.py")
        kv = os.path.join(chung, "adapters", "kv", "kv_adapter.py")
        test_core(tmp, v)
        test_mz(tmp, v, adp)
        test_mv(tmp, v, adp)
        test_v2(tmp, v, chung)
        test_v2b(tmp, v, chung)
        test_v21(tmp, v)
        test_v22(tmp, v)
        test_v23(tmp, v)
        test_compat(tmp, v)
        test_patchkit2(tmp, v)
        test_migrate(tmp, v)
        test_games4(tmp, v, adp, kv)
        test_ko_font(tmp, v)
        test_docs()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"SELFTEST: {ok}/{ok + fail} đạt")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
