"""Patch Viet hoa: chi chua file da dich + script cai/go, khong chep ca game.

<Translation>/<Ten game>/          (patch.dir trong config.yaml cua du an)
  CAI_VIETHOA.bat, GO_VIETHOA.bat  (nguoi dung chi thay 2 file nay)
  _viethoa/  (an)
    vgt_patch.ps1                  (cai: sao luu file goc sap bi de vao _backup roi chep; go: tra lai, xoa _backup)
    vgt_patch.json                 (duong dan, sha256 goc / sha256 da dich tung file)
    files/<duong dan tuong doi trong game>
    _backup/                       (chi ton tai khi dang cai; chi chua file bi de, khong sao luu ca game)
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

DATA = "_viethoa"
MANIFEST = "vgt_patch.json"
BACKUP = "_backup"


def sha256(p: Path) -> str | None:
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def files_dir(patch_dir: Path) -> Path:
    return patch_dir / DATA / "files"


def installed_files(game: Path, patch_dir: Path) -> list[str]:
    """File trong game dang la ban da dich (theo manifest cu). Rong = game sach."""
    if (patch_dir / DATA / BACKUP).exists():
        return [BACKUP]
    mf = patch_dir / DATA / MANIFEST
    if not mf.is_file():
        return []
    files = json.loads(mf.read_text("utf-8"))["files"]
    return [f["path"] for f in files
            if f["new"] != f["orig"] and sha256(game / f["path"]) == f["new"]]


def guard_clean(game: Path, patch_dir: Path):
    """Doc/build tu game da cai patch = lay ban dich lam goc (G-004). Chan lai."""
    bad = installed_files(game, patch_dir)
    if bad:
        raise SystemExit(f"Game dang cai Viet hoa ({bad[0]}...). Chay {patch_dir / 'GO_VIETHOA.bat'} truoc.")


def build(game: Path, staging: Path, written: list[Path], probe: str | None = None,
          hide: list[str] | None = None) -> Path:
    """files_dir(staging) da co file adapter ghi ra; them manifest + script.
    hide: file trong game phai cat vao _backup khi cai (vd WOLF: Data/BasicData.wolf khi patch la ban giai nen),
    tra lai khi go."""
    root = files_dir(staging)
    root.mkdir(parents=True, exist_ok=True)
    files = []
    for p in sorted(set(written)):
        rel = p.relative_to(root).as_posix()
        files.append({"path": rel, "orig": sha256(game / rel), "new": sha256(p)})
    # probe: file co san trong game de script nhan ra thu muc game khi patch chi them file moi.
    manifest = {"game_default": str(game), "probe": probe, "files": files}
    if hide:
        manifest["hide"] = [{"path": h, "orig": sha256(game / h)} for h in hide]
    (staging / DATA / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")
    here = Path(__file__).parent / "patch_scripts"
    for name, dst in (("vgt_patch.ps1", staging / DATA), ("CAI_VIETHOA.bat", staging), ("GO_VIETHOA.bat", staging)):
        # CRLF cho .bat/.ps1 tren Windows.
        text = (here / name).read_text("utf-8").replace("\r\n", "\n").replace("\n", "\r\n")
        (dst / name).write_bytes(text.encode("ascii"))
    return staging


def replace_dir(staging: Path, patch_dir: Path):
    if (patch_dir / DATA / BACKUP).exists():
        raise SystemExit(f"{patch_dir} dang cai vao game. Chay GO_VIETHOA.bat truoc.")
    if patch_dir.exists():
        shutil.rmtree(patch_dir)
    staging.rename(patch_dir)
    if os.name == "nt":  # nguoi dung chi thay CAI/GO_VIETHOA.bat
        subprocess.run(["attrib", "+h", str(patch_dir / DATA)], check=False)
