"""Thu cach 'Claude tu lam' (02/11): dich 1 canh trong bo de bang prompt cua nguoi dung (docs/prompt_dich_18.md
hoac prompt_dich_thuong.md), Opus, khong luat vgt, khong chi dao. Ket qua luu dang ket qua eval de so mu voi ban vgt.
Chay tren Windows (can claude -p)."""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vgt import evalset  # noqa: E402
from vgt.backend import ClaudeCodeBackend, MockBackend  # noqa: E402
from vgt.config import load_config  # noqa: E402
from vgt.prompts import TRANSLATE_SCHEMA  # noqa: E402

KEEP = ("name_vi", "gender", "age", "role", "personality", "speech_style", "catchphrases")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", required=True)
    ap.add_argument("--prompt", default="docs/prompt_dich_18.md")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--nhan", default="prompt_moi")
    ap.add_argument("--backend", default="claude", choices=["claude", "mock"])
    a = ap.parse_args()
    cfg = load_config(None)
    cfg["claude"] = dict(cfg["claude"], replace_system_prompt=False)  # giu system mac dinh cua Claude Code
    be = MockBackend() if a.backend == "mock" else ClaudeCodeBackend(cfg, evalset.EVAL / ".claude_work")
    system = (ROOT / a.prompt).read_text(encoding="utf-8")
    rep = {"nhan": a.nhan, "luc": time.strftime("%Y-%m-%d %H:%M"), "cau_hinh": {"prompt": a.prompt, "model": a.model},
           "case": [], "chi_phi": 0.0}
    for case in evalset.load_cases(a.case):
        pl = case["payload"]
        names = {c.get("id"): c.get("name_vi") for c in pl.get("characters") or []}
        data = {
            "tac_pham": (case.get("fixed") or {}).get("work") or {},
            "nhan_vat": [{k: c[k] for k in KEEP if c.get(k)} for c in pl.get("characters") or []],
            "xung_ho_da_co": pl.get("relations") or [],
            "thuat_ngu_da_co": pl.get("glossary") or [],
            "canh": {k: v for k, v in (pl.get("scene") or {}).items() if k in ("summary", "mood")},
            "lines": [{"id": x["id"], **({"sp": names.get(x["sp"], x["sp"])} if x.get("sp") else {}),
                       "s": m["source"]} for x, m in zip(pl["lines"], case["meta"])],
        }
        data["yeu_cau"] = ("Đây là dữ liệu hiện có của dự án và một cảnh cần dịch. Dịch MỌI dòng trong lines sang "
                           "tiếng Việt, giữ nguyên mọi mã điều khiển dạng \\N[n], \\C[n], \\V[n], \\G và các dấu "
                           "\\ khác đúng như gốc. Trả về t: [{id, v}].")
        prompt = "#JSON\n" + json.dumps(data, ensure_ascii=False)
        r = be.call(system, prompt, TRANSLATE_SCHEMA, a.model, None)
        got = {str(x.get("id")): x.get("v", "") for x in r["data"].get("t", [])}
        rep["case"].append({"id": case["id"], "ban_dich": [got.get(str(i), "") for i in range(len(case["meta"]))],
                            "chi_phi": r.get("cost") or 0.0})
        rep["chi_phi"] += r.get("cost") or 0.0
        print(f"  {case['id']}: {len(got)}/{len(case['meta'])} dong, ${r.get('cost') or 0:.2f}")
    out = evalset.EVAL / "ket_qua" / f"{time.strftime('%Y%m%d_%H%M%S')}_{a.nhan}.json"
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
