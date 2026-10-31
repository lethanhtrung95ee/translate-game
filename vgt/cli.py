"""Dong lenh: python -m vgt <lenh> ..."""
from __future__ import annotations

import argparse
import sys
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
    s.add_argument("--adapter", choices=["rpgmaker_mvmz", "unreal_locres", "table"])
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

    s = sub.add_parser("fork", help="tao du an thu (cung game, chua dich) de dich lai vai canh va so sanh")
    s.add_argument("src_project")
    s.add_argument("dst_project")

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
    if a.cmd == "fork":
        Project.fork(Path(a.src_project), Path(a.dst_project))
        return 0
    if a.cmd == "compare":
        print(Project.compare(Path(a.old_project), Path(a.new_project),
                              Path(a.out) if a.out else None, a.grp))
        return 0
    p = Project(Path(a.project_dir))
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
