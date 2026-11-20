"""Thu A/B can bang chi phi - chat luong: dich lai vai canh theo nhieu cau hinh, kiem dinh vien cham mu.

Chay (tu thu muc vgt):
  python tools/thu_ab.py setup  projects/_ab/<ten>/ab.yaml   -> tao du an thu cho tung phuong an + chay_thu.bat
  python tools/thu_ab.py report projects/_ab/<ten>/ab.yaml   -> bang token + diem + loi (ket_qua.md)

ab.yaml:
  src: projects/<game>            du an goc (chi DOC, chup ban sao db)
  groups: {key: [grp...], normal: [grp...]}
  variants:
    A:  {reset: [], config: {}}                               ban goc, chi cham
    V1: {targets_from: projects/<ban cu>}                     cham ban dich cua du an khac (cung id dong),
                                                              nhung bang ho so/bible cua du an goc (cong bang)
  compare: [[A, B, [key]], ...]                               bang doc song song (vgt compare) cho nguoi dung
    B:  {reset: [key], config: {effort: {key_scene: medium}}} dich lai nhom key voi cau hinh nay
Moi phuong an la mot du an rieng (ban sao db cua goc: giu ban dich goc, bible, scenes, tham khao en);
dong cua cac canh `reset` bi xoa ban dich roi dich lai. TM/nhat ky/kiem dinh cu bi xoa de do sach.
Kiem dinh vien cham tung canh mot lan goi (cung dieu kien cho moi phuong an), khong biet phuong an nao.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _load(plan: Path) -> dict:
    ab = yaml.safe_load(plan.read_text(encoding="utf-8"))
    ab["_dir"] = plan.parent
    return ab


def _grps(ab: dict, names: list[str]) -> list[str]:
    out = []
    for n in names:
        out += ab["groups"][n]
    return out


def _all(ab: dict) -> list[str]:
    return [g for gs in ab["groups"].values() for g in gs]


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out.get(k) or {}, v) if isinstance(v, dict) else v
    return out


def setup(plan: Path, snap_from: Path | None = None) -> None:
    ab = _load(plan)
    src = ROOT / ab["src"]
    snap = ab["_dir"] / "_goc.db"
    if snap_from:
        shutil.copyfile(snap_from, snap)
    else:
        s = sqlite3.connect(f"file:{src / 'project.db'}?mode=ro", uri=True)
        d = sqlite3.connect(snap)
        s.backup(d)
        s.close()
        d.close()
    d = sqlite3.connect(snap)
    assert d.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "ban sao db hong"
    d.close()
    base_cfg = yaml.safe_load((src / "config.yaml").read_text(encoding="utf-8")) or {}
    base_cfg.pop("patch", None)
    rel = str(ab["_dir"].relative_to(ROOT)).replace("/", "\\")
    bat = ["@echo off", "chcp 65001 >nul", "cd /d %~dp0..\\..\\..",
           f"echo Thu A/B: {len(ab['variants'])} phuong an. Tien do luu trong tung du an, chay lai duoc."]
    for name, v in ab["variants"].items():
        pd = ab["_dir"] / name
        reset = _grps(ab, v.get("reset") or [])
        if (pd / "project.db").exists():
            print(f"{name}: da co, bo qua (xoa thu muc de tao lai)")
        else:
            pd.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(snap, pd / "project.db")
            for f in ("bible.yaml", "scenes.yaml", "research.md"):
                if (src / f).exists():
                    shutil.copyfile(src / f, pd / f)
            cfg = _merge(base_cfg, v.get("config") or {})
            (pd / "config.yaml").write_text(
                f"# Du an thu A/B '{name}' tach tu {ab['src']} (tools/thu_ab.py). KHONG apply.\n"
                + yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
            db = sqlite3.connect(pd / "project.db")
            for t in ("tm", "runs", "reviewed", "reviews"):
                db.execute(f"DELETE FROM {t}")
            if v.get("targets_from"):
                o = sqlite3.connect(f"file:{ROOT / v['targets_from'] / 'project.db'}?mode=ro", uri=True)
                q = ",".join("?" * len(_all(ab)))
                old = o.execute(f"SELECT id, target, status FROM entries WHERE grp IN ({q})", _all(ab)).fetchall()
                o.close()
                db.executemany("UPDATE entries SET target=?, status=?, model='ban_cu', attempts=0, qa=NULL "
                               "WHERE id=?", [(t, st, i) for i, t, st in old])
                print(f"{name}: lay {len(old)} dong ban dich tu {v['targets_from']}")
            if reset:
                q = ",".join("?" * len(reset))
                db.execute(f"UPDATE entries SET target=NULL, status='new', model=NULL, attempts=0, qa=NULL "
                           f"WHERE grp IN ({q})", reset)
            db.commit()
            db.close()
            print(f"{name}: tao xong, dich lai {len(reset)} canh")
        p = f"{rel}\\{name}"
        bat.append(f"echo === {name} ===")
        if reset:
            bat.append(f"python -m vgt translate {p} " + " ".join(f'--grp "{g}"' for g in reset)
                       + " || goto loi")
        for g in (reset or _all(ab)):
            bat.append(f'python -m vgt review {p} --grp "{g}" || goto loi')
    snap.unlink()
    for a, b, gs in ab.get("compare") or []:
        bat.append(f"python -m vgt compare {rel}\\{a} {rel}\\{b} "
                   + " ".join(f'--grp "{g}"' for g in _grps(ab, gs))
                   + f" --out {rel}\\so_sanh_{a}__{b}.html")
    bat += [f"python tools\\thu_ab.py report {rel}\\ab.yaml",
            "echo Xong. Bao Claude doc ket_qua.md.", "pause", "exit /b 0",
            ":loi", "echo LOI - chup man hinh gui Claude. Chay lai file nay se lam tiep.", "pause", "exit /b 1"]
    (ab["_dir"] / "chay_thu.bat").write_text("\r\n".join(bat) + "\r\n", encoding="utf-8")
    print(f"Da viet {ab['_dir'] / 'chay_thu.bat'}")


def report(plan: Path) -> str:
    ab = _load(plan)
    rows = ["| Phuong an | Canh | Dong dich lai | Token ra | Chi phi dich ($ quy doi) | $/dong | Ket qua cham | Diem TB {chi tiet} | Loi nang | Loi nhe |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    detail = []
    for name, v in ab["variants"].items():
        db = sqlite3.connect(ab["_dir"] / name / "project.db")
        reset = _grps(ab, v.get("reset") or [])
        n = db.execute(f"SELECT COUNT(*) FROM entries WHERE grp IN ({','.join('?' * len(reset))})",
                       reset).fetchone()[0] if reset else 0
        tr = db.execute("SELECT COALESCE(SUM(output_tokens),0), COALESCE(SUM(cost_est),0) "
                        "FROM runs WHERE purpose='translate'").fetchone()
        rv = db.execute("SELECT COALESCE(SUM(cost_est),0) FROM runs WHERE purpose='review'").fetchone()[0]
        first = True
        for grps, cnt, verdict, scores, issues in db.execute(
                "SELECT grps, n, verdict, scores, issues FROM reviews ORDER BY ts"):
            sc = json.loads(scores or "{}")
            iss = json.loads(issues or "[]")
            maj = sum(1 for x in iss if x.get("severity") == "major")
            nums = [x for x in sc.values() if isinstance(x, (int, float))]
            avg = round(sum(nums) / len(nums), 2) if nums else "-"
            try:
                g = ",".join(json.loads(grps))
            except (TypeError, ValueError):
                g = grps
            cost = f"{n} | {tr[0]} | {round(tr[1], 2)} | {round(tr[1] / n, 4) if n else '-'}" \
                if reset and first else "- | - | - | -"
            first = False
            rows.append(f"| {name} | {g} | {cost} | {verdict} ({cnt} dong) | {avg} {sc} | {maj} | {len(iss) - maj} |")
            for x in iss:
                detail.append(f"- {name} | {g} | [{x.get('severity')}] {x.get('criterion')}: "
                              f"{x.get('problem')} -> {x.get('fix', '')}")
        allg = reset or _all(ab)
        left = db.execute(f"SELECT COUNT(*) FROM entries WHERE grp IN ({','.join('?' * len(allg))}) "
                          "AND status NOT IN ('done','tm','manual')", allg).fetchone()[0]
        rows.append(f"| {name} | (chi phi cham{'; ' + str(left) + ' dong chua dat QA -> canh do chua cham' if left else ''})"
                    f" | | | {round(rv, 2)} | | | | | |")
        db.close()
    out = ("# Ket qua thu A/B\n\nChi phi = gia API quy doi do `claude -p` bao (so sanh ti le, khong phai tien that).\n\n"
           + "\n".join(rows) + "\n\n## Loi kiem dinh vien bao\n" + "\n".join(detail) + "\n")
    (ab["_dir"] / "ket_qua.md").write_text(out, encoding="utf-8")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, plan = sys.argv[1], Path(sys.argv[2])
    if not plan.is_absolute():
        plan = ROOT / plan
    if cmd == "setup":
        setup(plan, Path(sys.argv[3]) if len(sys.argv) > 3 else None)
    elif cmd == "report":
        print(report(plan))
    else:
        raise SystemExit(__doc__)
