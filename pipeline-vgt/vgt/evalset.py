"""Bo de kiem tra CHUNG cho moi game (vgt eval): cac loi THAT da gap, chup san boi canh, chay lai bang
cau hinh hien tai (hoac cau hinh thu) de biet: loi cu co quay lai khong, thay doi co lam hong cho khac khong.

eval/cases/<id>.json (trong git, tu chua du): payload dich cua ca canh (nhu luc dich that, khong co
'before'), ho so co dinh (style/premise), su that game + ma bai hoc da khop (de tinh lai luat dich HIEN TAI),
ma dieu khien tung dong (de unmask), va cac phep kiem tu dong:
  {"line": i, "cam": [regex], "phai": [regex]}   tren ban dich cuoi cua dong i
  {"xung_ho_nhat_quan": true}                    scan.scene_hints khong bao gi tren ca canh
Moi lan chay con dem them: canh bao giong may (scan.line_hints) tren moi dong.
Ket qua: eval/ket_qua/<thoi diem>_<nhan>.json (khong vao git) + so voi lan chay truoc.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from types import SimpleNamespace

import yaml

from . import bible as biblemod
from . import fixapply
from . import lessons as lessonsmod
from . import scan
from .config import _merge, load_config
from .prompts import TRANSLATE_SCHEMA
from .protect import mask, unmask
from .textfit import norm_punct

EVAL = Path(__file__).resolve().parent.parent / "eval"


def add_case(project, grp: str, case_id: str, loai: str, mo_ta: str, checks: list[dict],
             bang_chung: str = "") -> Path:
    bidx = biblemod.BibleIndex(biblemod.load(project.path))
    scenes = biblemod.load_scene_ctx(project.path)
    es = [e for e in project.store.entries("grp=?", (grp,)) if e.kind in ("dialogue", "choice")]
    if not es:
        raise SystemExit(f"Khong co dong thoai trong canh {grp}")
    src_lang = project.store.get_meta("source_lang", "ja")
    lines, meta = [], []
    for i, e in enumerate(es):
        m, codes = mask(e.source)
        row = {"id": str(i), "k": e.kind, "s": m}
        if e.ref:
            row["en"] = e.ref
        sp = bidx.speaker_label(e) if e.kind == "dialogue" else None
        if sp:
            row["sp"] = sp
        lines.append(row)
        meta.append({"speaker": e.speaker, "face": e.face, "codes": codes, "source": e.source,
                     "ban_hien_tai": e.target})
    from .prompts import lang_line
    payload = {"lang": lang_line(src_lang), **bidx.context_for(es), "scene": scenes.get(grp), "lines": lines}
    payload = {k: v for k, v in payload.items() if v not in ([], {}, None, "")}
    role = next((project.route(e, bidx) for e in es if e.kind == "dialogue"), "dialogue")
    m = lessonsmod.match(project)
    f = lessonsmod.facts(project)
    proj_rules = []
    if (project.path / "LESSONS.md").exists():
        proj_rules = [l["Luật dịch"] for l in lessonsmod.parse_file(project.path / "LESSONS.md")
                      if l.get("Loại") == "chat-luong-dich" and l.get("Luật dịch")]
    case = {"id": case_id, "loai": loai, "mo_ta": mo_ta, "bang_chung": bang_chung,
            "game": project.path.name, "grp": grp, "src_lang": src_lang, "role": role,
            "engine": sorted(f.get("engine", [])), "facts": {k: sorted(v) for k, v in f.items() if k != "plugin"},
            "lesson_codes": [l["_code"] for l in m["ap_dung"] + m["chan_bang_code"]],
            "project_rules": proj_rules, "fixed": bidx.fixed_context(), "adult": project.is_adult(),
            "payload": payload,
            "meta": meta, "checks": checks, "tao_luc": time.strftime("%Y-%m-%d")}
    out = EVAL / "cases" / f"{case_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(case, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def _with_xh(case: dict) -> dict:
    """Them xung/goi theo tung dong (G-023) - tinh luc chay, theo code hien tai (khong luu trong case)."""
    from .config import load_config
    if not (load_config(None).get("xung_ho") or {}).get("theo_dong", True) or case.get("_no_xh"):
        return case["payload"]
    if (((case["payload"].get("scene") or {}).get("mach")) or {}).get("xung_ho"):
        return case["payload"]  # chi dao canh quyet xung ho (02/11)
    bidx = biblemod.BibleIndex({"characters": case["payload"].get("characters") or [],
                                "relations": case["payload"].get("relations") or []})
    es = [SimpleNamespace(id=str(i), kind=case["payload"]["lines"][i]["k"], speaker=m["speaker"], face=m["face"])
          for i, m in enumerate(case["meta"])]
    h = bidx.address_hints(es)
    pl = dict(case["payload"])
    pl["lines"] = [{**x, **({"xh": h[x["id"]]} if x["id"] in h else {})} for x in case["payload"]["lines"]]
    return pl


def _sys_ctx(base: str, case: dict, cfg: dict | None = None) -> str:
    """Giong Project.system_prompt: ho so co dinh + (game nguoi lon, content.chuan_18) thang tu ngu 18+."""
    from .pipeline import add_adult, add_fixed
    from .prompts import SYSTEM_REVIEW, SYSTEM_REVIEW_NGHIA, mach_block, phuong_ngu_block, van_phong_block
    if ((case.get("payload") or {}).get("scene") or {}).get("mach"):
        if base.startswith((SYSTEM_REVIEW[:60], SYSTEM_REVIEW_NGHIA[:60])):
            base = base + "\n\n" + mach_block("review")
        else:  # dich gia: chi dao dat len dau (nguon hieu chinh), nhu Project.system_prompt
            base = mach_block("dich") + "\n\n" + base
    s = add_fixed(base, case.get("fixed") or {})
    pn = phuong_ngu_block(cfg or load_config(None))
    if pn:
        s = s + "\n\n" + pn
    vp = "" if base.startswith(SYSTEM_REVIEW_NGHIA[:60]) else van_phong_block(bool(case.get("adult")))
    if vp:
        s = s + "\n\n" + vp
    on = ((cfg or {}).get("content") or {}).get("chuan_18", True)
    return add_adult(s, case.get("src_lang")) if case.get("adult") and on else s


def _rules(case: dict) -> list[str]:
    """Luat dich HIEN TAI ap cho game cua case (bai hoc moi them sau khi tao case cung duoc tinh)."""
    files = [lessonsmod.LESSONS / "global.md"] + [lessonsmod.LESSONS / "engines" / f"{e}.md"
                                                   for e in case.get("engine") or [] if e]
    facts = {k: set(v) for k, v in (case.get("facts") or {}).items()}
    out = []
    for p in files:
        if not p.exists():
            continue
        for l in lessonsmod.parse_file(p):
            if l.get("Trạng thái", "").startswith(lessonsmod.INACTIVE):
                continue
            if any(k in facts and not (facts[k] & v) for k, v in lessonsmod.parse_tags(l.get("Thẻ", "")).items()):
                continue
            det = l.get("Dò", "").strip()
            if det and det != "luon" and l["_code"] not in case.get("lesson_codes", []):
                continue
            if l.get("Loại") == "chat-luong-dich" and l.get("Luật dịch"):
                out.append(l["Luật dịch"])
    return out + list(case.get("project_rules") or [])


def load_cases(ids=None) -> list[dict]:
    out = []
    for p in sorted((EVAL / "cases").glob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        if not ids or c["id"] in ids:
            out.append(c)
    return out


def _check(case: dict, finals: list[str]) -> list[dict]:
    res = []
    for ck in case["checks"]:
        if "line" in ck:
            t = finals[ck["line"]] or ""
            bad = [r for r in ck.get("cam", []) if re.search(r, t, re.I)]
            miss = [r for r in ck.get("phai", []) if not re.search(r, t, re.I)]
            res.append({"kiem": f"dong {ck['line']}", "dat": not bad and not miss, "ban_dich": t,
                        "vi_pham": bad + [f"thieu: {m}" for m in miss], "ghi_chu": ck.get("ghi_chu", "")})
        elif ck.get("thang_18"):
            from .adult import check_levels
            bad = []
            for i, m in enumerate(case["meta"]):
                for w in check_levels(m["source"], finals[i], case.get("src_lang")):
                    bad.append(f"dong {i}: {w[3:].split(' (G-022)')[0]} | {finals[i][:70]}")
            res.append({"kiem": "muc tu 18+ ca canh", "dat": not bad, "vi_pham": bad, "ghi_chu": ck.get("ghi_chu", "")})
        elif ck.get("xung_ho_nhat_quan"):
            bidx = biblemod.BibleIndex({"characters": case["payload"].get("characters") or [],
                                        "relations": case["payload"].get("relations") or []})
            es = [SimpleNamespace(id=str(i), kind=case["payload"]["lines"][i]["k"], speaker=m["speaker"],
                                  face=m["face"], target=finals[i]) for i, m in enumerate(case["meta"])]
            h = scan.scene_hints(es, bidx)
            res.append({"kiem": "xung ho ca canh", "dat": not h,
                        "vi_pham": [f"dong {k}: {v[0].split(scan.TAG)[-1].strip()} | {finals[int(k)][:70]}"
                                    for k, v in h.items()], "ghi_chu": ck.get("ghi_chu", "")})
    return res


def run(backend, cfg_over: dict | None = None, ids=None, label: str = "hien_tai", review: bool = False,
        log=print) -> dict:
    from .pipeline import add_adult, add_fixed, add_rules, translate_system
    cfg = _merge(load_config(None), cfg_over or {})
    sysbase = translate_system(cfg)
    report = {"nhan": label, "luc": time.strftime("%Y-%m-%d %H:%M"), "cau_hinh": cfg_over or {}, "case": [],
              "chi_phi": 0.0}
    cases = load_cases(ids)
    for n, case in enumerate(cases, 1):
        log(f"  [{n}/{len(cases)}] {case['id']}: dang dich ({case['role']}){' + cham' if review else ''}...")
        system = add_rules(_sys_ctx(sysbase, case, cfg), _rules(case))
        model, effort = cfg["models"][case["role"]], (cfg.get("effort") or {}).get(case["role"])
        pl = _with_xh(case)
        prompt = "#JSON\n" + json.dumps(pl, ensure_ascii=False, separators=(",", ":"))
        r = backend.call(system, prompt, TRANSLATE_SCHEMA, model, effort)
        got = {str(x.get("id")): x.get("v", "") for x in r["data"].get("t", [])}
        finals = [scan.space_codes(unmask(norm_punct(got.get(str(i), "")), m["codes"]))
                  for i, m in enumerate(case["meta"])]
        checks = _check(case, finals)
        may = []
        for i, m in enumerate(case["meta"]):
            e = SimpleNamespace(kind=case["payload"]["lines"][i]["k"], source=m["source"], target=finals[i])
            may += [f"dong {i}: {h.split(scan.TAG)[-1].strip()}" for h in scan.line_hints(e, case["src_lang"], ((case.get("fixed") or {}).get("style") or {}).get("genre", ""))]
        xh = _check({**case, "checks": [{"xung_ho_nhat_quan": True}]}, finals)[0]["vi_pham"]
        item = {"id": case["id"], "loai": case["loai"], "dat": all(c["dat"] for c in checks), "kiem": checks,
                "giong_may": may, "xung_ho": xh, "model": model, "effort": effort, "chi_phi": r.get("cost") or 0.0,
                "ban_dich": finals}
        if review:
            item["cham"] = _review(backend, cfg, case, finals)
            item["chi_phi"] += item["cham"].pop("_cost", 0.0)
            crit = fixapply.criteria(cfg)
            if crit:  # ap cau sua loi nhe cua kiem dinh vien roi CHAM LAI de do tac dung
                fixed, n = list(finals), 0
                for x in item["cham"].get("loi") or []:
                    i = int(x.get("id", -1)) if str(x.get("id", "")).isdigit() else -1
                    if x.get("severity") == "major" or x.get("criterion") not in crit or not 0 <= i < len(fixed):
                        continue
                    new = fixapply.candidate(fixed[i], x.get("fix") or "")
                    if new:
                        fixed[i], n = new, n + 1
                item["ap_sua"] = n
                item["ban_dich_sau_sua"] = fixed
                if n:
                    item["cham_sau_sua"] = _review(backend, cfg, case, fixed)
                    item["chi_phi"] += item["cham_sau_sua"].pop("_cost", 0.0)
                else:
                    item["cham_sau_sua"] = {k: v for k, v in item["cham"].items()}
        report["chi_phi"] += item["chi_phi"]
        report["case"].append(item)
        log(f"  {case['id']}: {'DAT' if item['dat'] else 'TRUOT'}  giong_may={len(may)}  xung_ho={len(xh)}"
            f"  ${item['chi_phi']:.2f}")
    out = EVAL / "ket_qua" / f"{time.strftime('%Y%m%d_%H%M%S')}_{label}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    report["_file"] = str(out)
    return report


def _review(backend, cfg, case, finals) -> dict:
    from .pipeline import add_rules
    from .prompts import REVIEW_SCHEMA, REVIEW_STRICT_MACHINE, REVIEW_STRICT_MACHINE_V3, review_system
    # Thuoc do co dinh: kiem dinh vien LUON co chuan 18+ (so sanh cong bang giua cac cau hinh dich).
    system = add_rules(_sys_ctx(review_system(cfg), case, None), _rules(case))
    gm = (cfg.get("review") or {}).get("giong_may")
    if (cfg.get("review") or {}).get("che_do", "nghia") == "nghia":
        pass
    elif gm == "major":
        system += "\n\n" + REVIEW_STRICT_MACHINE
    elif gm == "ngang":
        system += "\n\n" + REVIEW_STRICT_MACHINE_V3
    pl = dict(case["payload"])
    xs = _with_xh(case)["lines"]
    pl["lines"] = [{"id": x["id"], "k": x["k"], "s": m["source"], "v": finals[i], **({"sp": x["sp"]} if "sp" in x else {}),
                    **({"xh": xs[i]["xh"]} if "xh" in xs[i] else {})}
                   for i, (x, m) in enumerate(zip(case["payload"]["lines"], case["meta"]))]
    r = backend.call(system, "#JSON\n" + json.dumps(pl, ensure_ascii=False, separators=(",", ":")),
                     REVIEW_SCHEMA, cfg["models"]["review"], (cfg.get("effort") or {}).get("review"))
    iss = r["data"].get("issues") or []
    return {"diem": r["data"].get("scores") or {}, "loi": iss,
            "loi_nang": sum(1 for x in iss if x.get("severity") == "major"),
            "loi_nhe": sum(1 for x in iss if x.get("severity") != "major"), "_cost": r.get("cost") or 0.0}


def report_files() -> list[Path]:
    """Chi file ket qua cua `vgt eval` (YYYYMMDD_HHMMSS_<nhan>.json); bo du lieu doc mu, khoa, trang sua...
    nam chung thu muc (loi 02/11: compare doc nham doc_thu_sach.json)."""
    return sorted(p for p in (EVAL / "ket_qua").glob("*.json") if re.match(r"\d{8}_\d{6}_.+\.json$", p.name))


def compare(report: dict) -> str:
    """Bang ket qua + so voi lan chay truoc (file ket qua gan nhat khac file nay)."""
    files = report_files()
    prev = None
    for p in reversed(files):
        if str(p) != report.get("_file"):
            prev = json.loads(p.read_text(encoding="utf-8"))
            break
    pv = {c["id"]: c for c in (prev or {}).get("case", [])}
    rows = [f"Bo de: {len(report['case'])} case, nhan '{report['nhan']}', chi phi ${report['chi_phi']:.2f} quy doi"
            + (f" | so voi '{prev['nhan']}' ({prev['luc']})" if prev else "")]
    for c in report["case"]:
        o = pv.get(c["id"])
        trend = ""
        if o:
            trend = " (truoc: " + ("DAT" if o["dat"] else "TRUOT") + f", giong_may {len(o['giong_may'])})"
        diem = f" diem {c['cham']['diem']} nang {c['cham']['loi_nang']} nhe {c['cham']['loi_nhe']}" if "cham" in c else ""
        rows.append(f"- {c['id']} [{c['loai']}]: {'DAT' if c['dat'] else 'TRUOT'}, giong_may {len(c['giong_may'])}, "
                    f"xung_ho {len(c.get('xung_ho', []))}{diem}{trend}")
        for k in c["kiem"]:
            if not k["dat"]:
                rows.append(f"    x {k['kiem']}: {'; '.join(k['vi_pham'])[:200]} | {k.get('ban_dich', '')[:90]}")
    return "\n".join(rows)


def load_over(path: str | None) -> dict:
    if not path:
        return {}
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def html(a: Path, b: Path, out: Path) -> Path:
    """Bang doc song song 2 lan chay bo de (0 token): moi case, moi dong: goc | lan A | lan B."""
    import html as h
    ra, rb = (json.loads(Path(p).read_text(encoding="utf-8")) for p in (a, b))
    cb = {c["id"]: c for c in rb["case"]}
    rows = ["<!doctype html><meta charset='utf-8'><title>So sanh bo de</title><style>body{font:15px/1.5 "
            "system-ui,sans-serif;margin:16px;max-width:1300px}table{border-collapse:collapse;width:100%}"
            "td,th{border:1px solid #ccc;padding:5px;vertical-align:top}th{background:#eee}.k{background:#fff3cd}"
            ".n{color:#666;font-size:13px}</style>",
            f"<h1>Bộ đề: {h.escape(ra['nhan'])} ↔ {h.escape(rb['nhan'])}</h1>"]
    for ca in ra["case"]:
        c2 = cb.get(ca["id"])
        if not c2:
            continue
        case = load_cases([ca["id"]])[0]
        mark = {k.get("line") for k in case["checks"] if "line" in k}
        def stat(c):
            ch = c.get("cham") or {}
            return (f"{'ĐẠT' if c['dat'] else 'TRƯỢT'} · giọng máy {len(c['giong_may'])} · xưng hô "
                    f"{len(c.get('xung_ho', []))} · KĐV nặng {ch.get('loi_nang', '-')} nhẹ {ch.get('loi_nhe', '-')}")
        rows.append(f"<h2>{h.escape(ca['id'])}</h2><p class='n'>{h.escape(case['mo_ta'])}<br>"
                    f"{h.escape(ra['nhan'])}: {stat(ca)}<br>{h.escape(rb['nhan'])}: {stat(c2)}</p>"
                    f"<table><tr><th>#</th><th>Gốc</th><th>{h.escape(ra['nhan'])}</th><th>{h.escape(rb['nhan'])}</th></tr>")
        for i, m in enumerate(case["meta"]):
            cls = " class='k'" if i in mark else ""
            rows.append(f"<tr{cls}><td>{i}</td>" + "".join(f"<td>{h.escape(x or '')}</td>" for x in (
                m["source"], ca["ban_dich"][i], c2["ban_dich"][i])) + "</tr>")
        rows.append("</table>")
    out.write_text("\n".join(rows), encoding="utf-8")
    return out


def summary_runs(prefixes: list[str]) -> str:
    """Tong hop nhieu lan chay theo nhan (vd A_lan1, A_lan2 -> nhom A): trung binh + khoang dao dong."""
    from .adult import check_levels
    files = sorted((EVAL / "ket_qua").glob("*.json"))
    groups: dict[str, list] = {}
    for f in files:
        r = json.loads(f.read_text(encoding="utf-8"))
        for p in prefixes:
            if r["nhan"].startswith(p):
                groups.setdefault(p, []).append(r)
    cases = {c["id"]: c for c in load_cases()}

    def stats(r, key="cham", bd="ban_dich"):
        n_major = n_minor = adult = may = xh = dat = 0
        for c in r["case"]:
            ch = c.get(key) or c.get("cham") or {}
            n_major += ch.get("loi_nang", 0) or 0
            n_minor += ch.get("loi_nhe", 0) or 0
            case = cases.get(c["id"])
            fin = c.get(bd) or c["ban_dich"]
            if case:
                adult += sum(len(check_levels(m["source"], fin[i], case.get("src_lang")))
                             for i, m in enumerate(case["meta"]))
                es = [SimpleNamespace(kind=case["payload"]["lines"][i]["k"], source=m["source"], target=fin[i])
                      for i, m in enumerate(case["meta"])]
                may += sum(len(scan.line_hints(e, case.get("src_lang"), ((case.get("fixed") or {}).get("style") or {}).get("genre", ""))) for e in es)
                xh += len(_check({**case, "checks": [{"xung_ho_nhat_quan": True}]}, fin)[0]["vi_pham"])
            dat += 1 if c["dat"] else 0
        return {"case": len(r["case"]), "dat": dat, "nang": n_major, "nhe": n_minor, "lam_nhe_18": adult,
                "giong_may": may, "xung_ho": xh, "chi_phi": round(r["chi_phi"], 2)}

    def agg(rows):
        out = {}
        for k in rows[0]:
            vals = [x[k] for x in rows]
            mean = sum(vals) / len(vals)
            out[k] = f"{mean:.1f}" + (f" ({min(vals)}–{max(vals)})" if len(vals) > 1 and min(vals) != max(vals) else "")
        return out

    head = "| Cấu hình | Số lần | Case đạt | Lỗi nặng | Lỗi nhẹ | Làm nhẹ 18+ (code) | Giọng máy (code) | Xưng hô (code) | Chi phí/lần |"
    lines = [head, "|" + "---|" * 9]
    for p, runs in groups.items():
        variants = [(p, "cham", "ban_dich")]
        if any("cham_sau_sua" in c for r in runs for c in r["case"]):
            variants.append((p + " + áp sửa", "cham_sau_sua", "ban_dich_sau_sua"))
        for name, key, bd in variants:
            a = agg([stats(r, key, bd) for r in runs])
            lines.append(f"| {name} | {len(runs)} | {a['dat']}/{a['case']} | {a['nang']} | {a['nhe']} | {a['lam_nhe_18']} | "
                         f"{a['giong_may']} | {a['xung_ho']} | ${a['chi_phi']} |")
    return "\n".join(lines) + "\n\nSố trong ngoặc: thấp nhất–cao nhất giữa các lần chạy (độ dao động)."


def recapture(project, game: str, out_dir: Path | None = None, ids: list[str] | None = None) -> list[str]:
    """Chup lai boi canh (payload: ho so, quan he...) cua moi case thuoc `game` tu du an `project`
    (vd ban sao da duyet xung ho). Giu id, loai, mo ta, phep kiem. out_dir: ghi ra thu muc khac (thu nghiem)."""
    done = []
    for c in load_cases():
        if c.get("game") != game or (ids and c["id"] not in ids):
            continue
        p = add_case(project, c["grp"], c["id"], c["loai"], c["mo_ta"], c["checks"], c.get("bang_chung", ""))
        nc = json.loads(p.read_text(encoding="utf-8"))
        nc["game"] = game
        target = (Path(out_dir) / p.name) if out_dir else p
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(nc, ensure_ascii=False, indent=1), encoding="utf-8")
        if out_dir:
            p.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")  # tra lai ban cu
        done.append(c["id"])
    return done


def latest_report(pat: str) -> Path:
    """Duong dan file ket qua; neu khong ton tai thi coi la nhan -> file moi nhat eval/ket_qua/*_<nhan>.json."""
    p = Path(pat)
    if p.exists():
        return p
    fs = [f for f in report_files() if f.name.endswith(f"_{pat}.json")]
    if not fs:
        raise SystemExit(f"Khong co ket qua '{pat}' trong eval/ket_qua")
    return fs[-1]


def blind_data(report_file: Path, seed: int = 7, old_report: Path | None = None) -> dict:
    """Du lieu doc mu cho nguoi dung: moi canh 2 ban (cu = ban v2 trong case, hoac ban cua lan chay old_report;
    moi = ban sau ap sua cua lan chay), dao ngau nhien X/Y; khoa giai ma luu rieng."""
    import random
    rnd = random.Random(None if old_report else seed)  # so 2 lan chay: dao moi lan, khoa luu rieng
    r = json.loads(Path(report_file).read_text(encoding="utf-8"))
    olds = {}
    if old_report:
        olds = {c["id"]: c.get("ban_dich_sau_sua") or c["ban_dich"]
                for c in json.loads(Path(old_report).read_text(encoding="utf-8"))["case"]}
    scenes, key = [], {}
    for c in r["case"]:
        case = load_cases([c["id"]])[0]
        new = c.get("ban_dich_sau_sua") or c["ban_dich"]
        old = olds.get(c["id"]) if old_report else [m.get("ban_hien_tai") or "" for m in case["meta"]]
        if old is None:
            continue
        flip = rnd.random() < 0.5
        x, y = (new, old) if flip else (old, new)
        key[c["id"]] = {"X": "moi" if flip else "cu", "Y": "cu" if flip else "moi"}
        sc = case["payload"].get("scene") or {}
        scenes.append({"id": c["id"], "tom_tat": sc.get("summary", ""), "khong_khi": sc.get("mood", ""),
                       "dong": [{"X": x[i], "Y": y[i]} for i in range(len(case["meta"]))]})
    return {"scenes": scenes, "key": key}
