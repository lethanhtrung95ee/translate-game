"""Goi model qua Claude Code (`claude -p`) bang goi dang ky Pro/Max cua ban.

Khong dung --bare: che do do bo qua dang nhap goi dang ky va doi API key.
Tiet kiem han muc moi lan goi:
- --system-prompt-file: thay HET system prompt mac dinh cua Claude Code (rat dai) bang prompt dich ngan.
- --tools "" + --disallowedTools "mcp__*" + --strict-mcp-config: khong nap mo ta cong cu/MCP.
- --disable-slash-commands: khong nap danh sach skill.
- chay trong thu muc rong: khong nap CLAUDE.md cua du an nao.
- --json-schema: ket qua co cau truc, khong ton luot sua dinh dang.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

LIMIT_RX = re.compile(r"(usage|rate)[ _-]?limit|limit (reached|exceeded)|out of (usage|extra usage)"
                      r"|resets? (at|in)|hit your limit|429", re.I)


class LimitReached(Exception):
    pass


class BackendError(Exception):
    pass


class ClaudeCodeBackend:
    def __init__(self, cfg: dict, workdir: Path, log=print):
        self.c = cfg["claude"]
        # Tuyet doi: claude chay voi cwd=workdir, duong dan tuong doi se bi nhan doi.
        self.workdir = Path(workdir).resolve()
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.log = log
        exe = self.c["executable"]
        self.exe = shutil.which(exe) or exe

    def _cmd(self, model: str, schema: dict, system_file: Path, effort: str | None = None) -> list[str]:
        cmd = [self.exe, "-p", "--model", model, "--output-format", "json",
               "--json-schema", json.dumps(schema, ensure_ascii=False),
               "--max-turns", str(self.c["max_turns"])]
        if effort:
            cmd += ["--effort", effort]
        if self.c.get("replace_system_prompt", True):
            cmd += ["--system-prompt-file", str(system_file)]
        else:
            cmd += ["--append-system-prompt-file", str(system_file)]
        if self.c.get("disable_tools", True):
            cmd += ["--tools", "", "--disallowedTools", "mcp__*", "--strict-mcp-config",
                    "--disable-slash-commands"]
        if self.c.get("no_session_persistence", True):
            cmd += ["--no-session-persistence"]
        return cmd + list(self.c.get("extra_args") or [])

    def call(self, system: str, prompt: str, schema: dict, model: str,
             effort: str | None = None, timeout: int | None = None) -> dict:
        sysf = self.workdir / f"system_{hashlib.sha1(system.encode()).hexdigest()[:10]}.txt"
        if not sysf.exists():
            sysf.write_text(system, encoding="utf-8")
        waits = 0
        while True:
            try:
                return self._once(self._cmd(model, schema, sysf, effort), prompt, timeout)
            except LimitReached as e:
                if not self.c.get("wait_on_limit") or waits >= self.c["max_limit_waits"]:
                    raise
                waits += 1
                mins = self.c["limit_wait_minutes"]
                self.log(f"[han muc] {e} -> cho {mins} phut roi thu lai ({waits}/"
                         f"{self.c['max_limit_waits']}). Tien do da luu, co the tat va chay lai sau.")
                time.sleep(mins * 60)

    def _once(self, cmd: list[str], prompt: str, timeout: int | None = None) -> dict:
        try:
            p = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               encoding="utf-8", cwd=self.workdir,
                               timeout=timeout or self.c["timeout_sec"])
        except FileNotFoundError as e:
            raise BackendError(f"Khong tim thay Claude Code ('{self.exe}'). Cai dat va dang nhap truoc.") from e
        except subprocess.TimeoutExpired as e:
            raise BackendError("Het thoi gian cho phan hoi") from e
        out = (p.stdout or "").strip()
        try:
            data = json.loads(out.splitlines()[-1] if out else "{}")
        except json.JSONDecodeError:
            data = {}
        msg = f"{data.get('result') or ''} {p.stderr or ''}".strip()
        if data.get("is_error") or p.returncode != 0 or not data:
            if LIMIT_RX.search(msg) or data.get("subtype") == "error_rate_limit":
                raise LimitReached(msg[:200])
            raise BackendError(f"claude -p loi (exit {p.returncode}): {msg[:300]}")
        so = data.get("structured_output")
        if so is None:
            raise BackendError(f"Khong co structured_output: {str(data.get('result'))[:200]}")
        return {"data": so, "usage": data.get("usage") or {},
                "cost": data.get("total_cost_usd") or 0.0}


class MockBackend:
    """Backend gia de kiem thu pipeline ma khong ton han muc."""

    def __init__(self, *a, **k):
        self.calls = []

    def call(self, system: str, prompt: str, schema: dict, model: str,
             effort: str | None = None, timeout: int | None = None) -> dict:
        self.calls.append((model, len(prompt)))
        payload = json.loads(prompt.split("\n", 1)[1]) if prompt.startswith("#JSON") else {}
        props = schema.get("properties", {})
        if "scenes" in props:  # bien tap truong doc 1 phan kich ban
            data = {"summary": f"mock phan {payload.get('part')}", "chars_seen": [],
                    "scenes": [{"grp": g, "summary": "mock canh", "mood": "vui",
                                "effect": "cuoi", "key": False} for g in payload.get("scene_ids", [])]}
        elif "issues" in props:  # kiem dinh vien: dong co chu BAD -> loi nang
            data = {"scores": {"dung_y": 5}, "issues": [
                {"id": x["id"], "severity": "major", "criterion": "dung_y", "problem": "sai nghia",
                 "fix": "sua"} for x in payload.get("lines", []) if "BAD" in (x.get("v") or "")]}
        elif "characters" in props:
            sp = payload.get("speakers", [])
            data = {"style": {"tone": "mock"},
                    "characters": [{"id": f"c{i}", "names": [s["name"]], "name_vi": s["name"],
                                    "gender": "unknown", "self": "tôi"} for i, s in enumerate(sp)],
                    "relations": [], "glossary": [], "work": {"premise": "mock premise"}}
        else:
            data = {"t": [{"id": x["id"], "v": "VI: " + x["s"]} for x in payload.get("lines", [])]}
        return {"data": data, "usage": {"input_tokens": len(prompt) // 3, "output_tokens": 50},
                "cost": 0.0}
