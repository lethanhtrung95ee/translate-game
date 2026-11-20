"""Thu cach 'Claude tu dich' (prompt nguoi dung, Opus, khong luat vgt) tren 1 canh cua game DA CO ban dich tot
(vd Legend of Mortal), roi xuat du lieu doc mu: ban moi vs ban da co. Ho so (bang xung ho, thuat ngu) lay tu file
HANDOFF cua game (vd docs/tham_khao/LOM_HANDOFF_mau.md muc 5) = dung thu phien dich that da co."""
import argparse
import json
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vgt import evalset  # noqa: E402
from vgt.backend import ClaudeCodeBackend, MockBackend  # noqa: E402
from vgt.config import load_config  # noqa: E402
from vgt.prompts import TRANSLATE_SCHEMA  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", required=True)
    ap.add_argument("--canh", required=True, help="regex key cua canh can dich")
    ap.add_argument("--truoc", default="", help="regex key cac cau ngay truoc (ngu canh, da dich)")
    ap.add_argument("--ho-so", help="file ho so (bang xung ho/thuat ngu), vd HANDOFF muc 5")
    ap.add_argument("--prompt", default="docs/prompt_dich_thuong.md")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--ten", required=True)
    ap.add_argument("--backend", default="claude", choices=["claude", "mock"])
    a = ap.parse_args()
    cap = json.loads(Path(a.cap).read_text(encoding="utf-8"))
    zh, vi = cap["zh"], cap["vi"]
    keys = sorted(k for k in zh if re.search(a.canh, k))
    truoc = sorted(k for k in zh if a.truoc and re.search(a.truoc, k) and k not in keys)[-60:]
    cfg = load_config(None)
    cfg["claude"] = dict(cfg["claude"], replace_system_prompt=False)
    be = MockBackend() if a.backend == "mock" else ClaudeCodeBackend(cfg, evalset.EVAL / ".claude_work")
    data = {"ho_so_du_an": Path(a.ho_so).read_text(encoding="utf-8") if a.ho_so else "",
            "cac_cau_ngay_truoc": [{"s": zh[k]} for k in truoc],
            "yeu_cau": "Dịch MỌI dòng trong lines (theo thứ tự trong cảnh) sang tiếng Việt. Giữ nguyên thẻ {...} và "
                       "đúng số chuỗi \\n như câu gốc. Trả về t: [{id, v}].",
            "lines": [{"id": str(i), "s": zh[k]} for i, k in enumerate(keys)]}
    r = be.call((ROOT / a.prompt).read_text(encoding="utf-8"), "#JSON\n" + json.dumps(data, ensure_ascii=False),
                TRANSLATE_SCHEMA, a.model, None)
    got = {str(x.get("id")): x.get("v", "") for x in r["data"].get("t", [])}
    flip = random.random() < 0.5
    dong = []
    for i, k in enumerate(keys):
        moi, cu = got.get(str(i), ""), vi.get(k, "")
        x, y = (moi, cu) if flip else (cu, moi)
        dong.append({"X": x, "Y": y})
    od = evalset.EVAL / "ket_qua"
    (od / f"doc_{a.ten}_data.json").write_text(json.dumps([{"id": a.ten, "dong": dong}], ensure_ascii=False),
                                               encoding="utf-8")
    (od / f"doc_{a.ten}_data.khoa.json").write_text(json.dumps({a.ten: {"X": "moi" if flip else "cu",
                                                                         "Y": "cu" if flip else "moi"}}),
                                                    encoding="utf-8")
    (od / f"{time.strftime('%Y%m%d_%H%M%S')}_{a.ten}.json").write_text(json.dumps(
        {"nhan": a.ten, "chi_phi": r.get("cost") or 0.0, "keys": keys, "ban_dich": [got.get(str(i), "") for i in range(len(keys))]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Xong: {len(got)}/{len(keys)} dong, ${r.get('cost') or 0:.2f} -> eval/ket_qua/doc_{a.ten}_data.json")


if __name__ == "__main__":
    main()
