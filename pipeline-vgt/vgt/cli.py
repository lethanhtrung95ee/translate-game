"""Dong lenh: python -m vgt <lenh> ..."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .pipeline import Project


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="vgt", description="Dich game sang tieng Viet")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="tao du an cho 1 game")
    s.add_argument("game_dir")
    s.add_argument("project_dir")
    s.add_argument("--adapter", choices=["rpgmaker_mvmz", "unreal_locres", "linguagacha", "table"])
    s.add_argument("--name", help='ten game -> ban Viet hoa o Translation/<ten>/ (vd "Cursed Armor")')

    for name, hlp in [("extract", "trich xuat text tu game"), ("status", "tien do + muc dung"),
                      ("estimate", "uoc tinh so lan goi theo model"),
                      ("review-export", "xuat danh sach dong can duyet"),
                      ("review-import", "nhan ban sua tay tu review.csv")]:
        s = sub.add_parser(name, help=hlp)
        s.add_argument("project_dir")

    s = sub.add_parser("bible", help="ho so tac pham: Opus doc TOAN BO kich ban -> bible.yaml + scenes.yaml")
    s.add_argument("project_dir")
    s.add_argument("--backend", default="claude", choices=["claude", "mock"])
    s.add_argument("--quick", action="store_true", help="cach cu: chi doc --sample-chars ky tu dau")
    s.add_argument("--sample-chars", type=int, default=60000)

    s = sub.add_parser("translate", help="dich cac dong chua dich")
    s.add_argument("project_dir")
    s.add_argument("--backend", default="claude", choices=["claude", "mock"])
    s.add_argument("--limit", type=int, help="chi dich N dong (de chay thu)")
    s.add_argument("--kind", choices=["dialogue", "choice", "ui", "name", "description"])
    s.add_argument("--grp", action="append", help="chi dich canh nay (lap lai duoc)")
    s.add_argument("--force", action="store_true", help="bo qua yeu cau bible da duyet")

    s = sub.add_parser("review", help="kiem dinh vien cham tung canh da dich (5 tieu chi)")
    s.add_argument("project_dir")
    s.add_argument("--backend", default="claude", choices=["claude", "mock"])
    s.add_argument("--limit", type=int, help="toi da N lan goi")
    s.add_argument("--grp", action="append", help="chi cham canh nay (lap lai duoc)")

    s = sub.add_parser("run", help="chay tiep tu cho dang do, tu dung o cac cua (bible, ban thu, xong)")
    s.add_argument("project_dir")
    s.add_argument("--backend", default="claude", choices=["claude", "mock"])
    s.add_argument("--force", action="store_true", help="chay du TIEN_DO bao dang chay o phien khac")

    s = sub.add_parser("list", help="cac game con viec (dang lam / cho ban); --all: ca da xong, tam dung, luu tru")
    s.add_argument("--root", default="projects")
    s.add_argument("--all", action="store_true")
    s.add_argument("--plain", action="store_true", help="moi dong: so ten (cho BAT_DAU.bat)")

    s = sub.add_parser("mark", help="dat trang thai du an: dang_lam | cho_nguoi_dung | xong | tam_dung | luu_tru")
    s.add_argument("project_dir")
    s.add_argument("state")
    s.add_argument("--ten", help="ten hien thi, vd 'Cursed Armor (dich lai v0.2)'")

    s = sub.add_parser("trial", help="dat 2-3 canh lam ban thu")
    s.add_argument("project_dir")
    s.add_argument("--grp", action="append", required=True)
    s.add_argument("--force", action="store_true", help="bo qua yeu cau canh nguoi lon cho game 18+")

    s = sub.add_parser("approve-trial", help="nguoi dung da doc va dong y ban thu")
    s.add_argument("project_dir")

    s = sub.add_parser("lessons", help="bai hoc KHOP voi game nay (khong in bai khong lien quan)")
    s.add_argument("project_dir")

    s = sub.add_parser("check-font", help="tang 1: font co ve du moi ky tu cua ban dich khong (0 token)")
    s.add_argument("project_dir")
    s.add_argument("--font", help="file .ttf/.otf/.ttc can kiem (mac dinh: font patch/game)")

    s = sub.add_parser("fork", help="tao du an thu (cung game, chua dich) de dich lai vai canh va so sanh")
    s.add_argument("src_project")
    s.add_argument("dst_project")

    s = sub.add_parser("xung-ho", help="kiem xung ho trong bible (0 token); --de-xuat: Opus chot cap thieu/mo ho")
    s.add_argument("project_dir")
    s.add_argument("--backend", default="claude", choices=["claude", "mock"])
    s.add_argument("--de-xuat", action="store_true")
    s.add_argument("--chap-nhan", action="store_true", help="chap nhan phan con lai, mo cua CAN_SUA_XUNG_HO")
    s.add_argument("--duyet", action="store_true", help="bien tap truong doc lap chot xung ho cac cap noi nhieu nhat")
    s.add_argument("--top", type=int, help="chi duyet N cap nhieu luot nhat (mac dinh: moi cap >= xung_ho.duyet_min_luot)")

    s = sub.add_parser("eval", help="chay bo de kiem tra chung (eval/cases) bang cau hinh hien tai / cau hinh thu")
    s.add_argument("--case", action="append", help="chi chay case nay (lap lai duoc)")
    s.add_argument("--cau-hinh", help="file yaml ghi de cau hinh de thu (vd prompt_version: 3)")
    s.add_argument("--nhan", default="hien_tai", help="ten lan chay (de so sanh)")
    s.add_argument("--cham", action="store_true", help="kiem dinh vien cham them (ton them han muc)")
    s.add_argument("--backend", default="claude", choices=["claude", "mock"])

    s = sub.add_parser("eval-tonghop", help="tong hop nhieu lan chay bo de theo tien to nhan (trung binh + dao dong)")
    s.add_argument("nhan", nargs="+")

    s = sub.add_parser("eval-chup-lai", help="chup lai boi canh cac case cua 1 game tu du an (vd sau khi duyet xung ho)")
    s.add_argument("project_dir")
    s.add_argument("--game", required=True, help="ten game trong case, vd cursed_armor_v2")
    s.add_argument("--case", action="append", help="chi chup lai case nay (lap lai duoc)")

    s = sub.add_parser("dich-lai", help="dua dong thoai/lua chon da dich ve 'new' de dich lai theo luong moi (co sao luu)")
    s.add_argument("project_dir")
    s.add_argument("--giu", action="store_true", help="giu ban da dich theo luong cu, khong hoi lai (cua CAN_DICH_LAI_LUONG_MOI)")

    s = sub.add_parser("chi-dao", help="dong y lam chi dao cho moi canh con thieu (cua CAN_DONG_Y_CHI_DAO)")
    s.add_argument("project_dir")
    s.add_argument("--dong-y", action="store_true")

    s = sub.add_parser("mach", help="bien kich truong viet chi dao tung canh (mach_canh.yaml) cho dich gia")
    s.add_argument("project_dir")
    s.add_argument("--grp", action="append", default=[], help="id canh (lap lai duoc)")
    s.add_argument("--case", action="append", default=[], help="lay canh cua case bo de (lap lai duoc)")
    s.add_argument("--force", action="store_true", help="viet lai canh da co")
    s.add_argument("--backend", default="claude", choices=["claude", "mock"])

    s = sub.add_parser("eval-doc", help="xuat du lieu doc mu (ban cu/moi) tu 1 lan chay bo de")
    s.add_argument("ket_qua", help="file ket qua hoac nhan (lay file moi nhat)")
    s.add_argument("--so-voi", help="ban 'cu' lay tu lan chay nay (file hoac nhan) thay vi ban v2 trong case")
    s.add_argument("--out", required=True)

    s = sub.add_parser("eval-them", help="them 1 loi that vao bo de chung (chup boi canh canh do)")
    s.add_argument("project_dir")
    s.add_argument("--grp", required=True)
    s.add_argument("--id", required=True, help="ten case, vd zh_may_tien_thuong")
    s.add_argument("--loai", required=True, help="loai loi, vd giong_may / xung_ho / lam_nhe / ky_thuat")
    s.add_argument("--mo-ta", required=True)
    s.add_argument("--kiem", required=True, help='JSON list phep kiem, vd [{"line":3,"cam":["được rồi$"]}]')
    s.add_argument("--bang-chung", default="")

    s = sub.add_parser("thuat-ngu", help="bien tap truong doc lap ra bang thuat ngu (tranh ghep Han-Viet), ap bang vgt term")
    s.add_argument("project_dir")
    s.add_argument("--backend", default="claude", choices=["claude", "mock"])
    s.add_argument("--dry", action="store_true")

    s = sub.add_parser("quet", help="do loi chung tren dong DA dich (0 token): sua dau cach ma ten, canh bao giong may / xung ho")
    s.add_argument("project_dir")
    s.add_argument("--dry", action="store_true")
    s.add_argument("--force", action="store_true")

    s = sub.add_parser("term", help="doi 1 thuat ngu/ten da dich tren ca du an (0 token, khong cham lai ca game)")
    s.add_argument("project_dir")
    s.add_argument("--src", required=True, help="thuat ngu goc, vd 獵天使")
    s.add_argument("--old", required=True, help="ban dich cu")
    s.add_argument("--new", required=True, help="ban dich moi")
    s.add_argument("--dry", action="store_true", help="chi xem se doi gi")
    s.add_argument("--force", action="store_true", help="bo qua kiem tra phien khac dang chay")

    s = sub.add_parser("compare", help="bang so sanh ban cu/moi theo canh (HTML)")
    s.add_argument("old_project")
    s.add_argument("new_project")
    s.add_argument("--grp", action="append")
    s.add_argument("--out")

    s = sub.add_parser("apply", help="tao patch Viet hoa (projects/<game>/patch: CAI/GO_VIETHOA.bat), khong sua game goc")
    s.add_argument("project_dir")
    s.add_argument("--out")

    a = ap.parse_args(argv)
    if a.cmd == "init":
        Project.init(Path(a.game_dir), Path(a.project_dir), a.adapter, name=a.name)
        return 0
    if a.cmd == "list":
        ps = Project.list_projects(Path(a.root), a.all)
        if not ps and not a.plain:
            print("Khong co game nao dang do. (python -m vgt list --all de xem ca game da xong)")
        for i, x in enumerate(ps, 1):
            if a.plain:
                print(i, x["ten"])
            else:
                run = " [DANG CHAY]" if x["dang_chay"] else ""
                print(f"{i:>2}. {x['ten_hien_thi']}  —  {Project.STATES[x['trang_thai']]}{run}, buoc {x['buoc']}"
                      f", cap nhat {x['cap_nhat']}   (thu muc: {x['ten']})")
        return 0
    if a.cmd == "mark":
        p = Project(Path(a.project_dir))
        p.mark(a.state, a.ten)
        return 0
    if a.cmd == "fork":
        Project.fork(Path(a.src_project), Path(a.dst_project))
        return 0
    if a.cmd == "compare":
        print(Project.compare(Path(a.old_project), Path(a.new_project),
                              Path(a.out) if a.out else None, a.grp))
        return 0
    if a.cmd == "eval-tonghop":
        from . import evalset
        out = evalset.summary_runs(a.nhan)
        (evalset.EVAL / "ket_qua" / "tong_hop.md").write_text(out, encoding="utf-8")
        print(out)
        return 0
    if a.cmd == "eval-doc":
        import json as _j
        from . import evalset
        d = evalset.blind_data(evalset.latest_report(a.ket_qua),
                               old_report=evalset.latest_report(a.so_voi) if a.so_voi else None)
        Path(a.out).write_text(_j.dumps(d["scenes"], ensure_ascii=False), encoding="utf-8")
        Path(a.out).with_suffix(".khoa.json").write_text(_j.dumps(d["key"], ensure_ascii=False), encoding="utf-8")
        print(a.out)
        return 0
    if a.cmd == "eval":
        from . import evalset
        from .backend import ClaudeCodeBackend, MockBackend
        from .config import _merge, load_config
        over = evalset.load_over(a.cau_hinh)
        be = MockBackend() if a.backend == "mock" else ClaudeCodeBackend(
            _merge(load_config(None), over), evalset.EVAL / ".claude_work")
        rep = evalset.run(be, over, a.case, a.nhan, a.cham)
        print(evalset.compare(rep))
        return 0
    p = Project(Path(a.project_dir))
    if a.cmd == "eval-chup-lai":
        from . import evalset
        print(evalset.recapture(p, a.game, ids=a.case))
        return 0
    if a.cmd == "dich-lai":
        why = p.busy()
        if why:
            raise SystemExit(f"Khong lam: {why}. Tat phien dang chay game nay truoc.")
        if a.giu:
            p.store.set_meta("giu_luong_cu", time.strftime("%Y-%m-%d %H:%M"))
            print("giu ban cu")
        else:
            print(p.dich_lai())
        return 0
    if a.cmd == "chi-dao":
        if a.dong_y:
            p.store.set_meta("chi_dao_dong_y", time.strftime("%Y-%m-%d %H:%M"))
        print("dong y:", p.store.get_meta("chi_dao_dong_y"))
        return 0
    if a.cmd == "mach":
        from . import evalset, mach
        grps = list(a.grp) + [c["grp"] for c in evalset.load_cases(a.case)] if a.case else list(a.grp)
        if not grps:
            raise SystemExit("Can --grp hoac --case")
        print(mach.build(p, p.backend(a.backend), list(dict.fromkeys(grps)), force=a.force))
        return 0
    if a.cmd == "eval-them":
        import json as _j
        from . import evalset
        print(evalset.add_case(p, a.grp, a.id, a.loai, a.mo_ta, _j.loads(a.kiem), a.bang_chung))
        return 0
    if a.cmd == "thuat-ngu":
        from . import thuatngu
        why = None if a.dry else p.busy()
        if why:
            raise SystemExit(f"Khong sua: {why}. Tat phien dang chay game nay truoc.")
        print(thuatngu.review(p, p.backend(a.backend), dry=a.dry))
        return 0
    if a.cmd == "quet":
        from . import scan
        why = None if (a.force or a.dry) else p.busy()
        if why:
            raise SystemExit(f"Khong quet: {why}. Tat phien dang chay game nay truoc.")
        print(scan.quet(p, a.dry))
        return 0
    if a.cmd == "xung-ho":
        from . import biblecheck, xungho
        if a.duyet:
            why = p.busy()
            if why:
                raise SystemExit(f"Khong sua bible: {why}. Tat phien dang chay game nay truoc.")
            print(xungho.review(p, p.backend(a.backend), a.top))
        if a.de_xuat:
            why = p.busy()
            if why:
                raise SystemExit(f"Khong sua bible: {why}. Tat phien dang chay game nay truoc.")
            print(xungho.propose(p, p.backend(a.backend), xungho.issues(p)))
        if a.chap_nhan:
            p.store.set_meta("xung_ho_ok", True)
            print("Da chap nhan xung ho hien tai (mo cua CAN_SUA_XUNG_HO).")
        print(biblecheck.summary(xungho.issues(p)))
        return 0
    if a.cmd == "term":
        from . import term
        why = None if (a.force or a.dry) else p.busy()
        if why:
            raise SystemExit(f"Khong doi: {why}. Tat phien dang chay game nay truoc.")
        import json as _j
        print(_j.dumps(term.rename(p, a.src, a.old, a.new, a.dry), ensure_ascii=False, indent=1))
        return 0
    if not p.adapter and a.cmd != "status":
        print("Chua init du an nay.")
        return 2
    if a.cmd == "extract":
        p.extract()
    elif a.cmd == "bible":
        p.draft_bible(a.backend, a.sample_chars, full=not a.quick)
    elif a.cmd == "translate":
        p.translate(a.backend, a.limit, a.force, a.kind, a.grp)
        print(p.status())
    elif a.cmd == "review":
        p.review(a.backend, a.limit, a.grp)
        print(p.status())
    elif a.cmd == "run":
        print(p.run(a.backend, a.force))
    elif a.cmd == "trial":
        p.set_trial(a.grp, a.force)
    elif a.cmd == "approve-trial":
        p.approve_trial()
    elif a.cmd == "check-font":
        from .fontcheck import report as fontreport
        ok, msg = fontreport(p, Path(a.font) if a.font else None)
        print(msg)
        return 0 if ok else 1
    elif a.cmd == "lessons":
        from .lessons import report
        print(report(p))
    elif a.cmd == "status":
        print(p.status())
    elif a.cmd == "estimate":
        print(p.estimate())
    elif a.cmd == "review-export":
        p.export_review()
    elif a.cmd == "review-import":
        p.import_review()
    elif a.cmd == "apply":
        p.apply(Path(a.out) if a.out else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
