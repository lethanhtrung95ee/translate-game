"""Doc cau hinh: config.default.yaml (trong repo) + <project>/config.yaml (ghi de)."""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "config.default.yaml"


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(project_dir: Path | None = None) -> dict:
    cfg = yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    if project_dir:
        p = Path(project_dir) / "config.yaml"
        if p.exists():
            cfg = _merge(cfg, yaml.safe_load(p.read_text(encoding="utf-8")) or {})
    return cfg
