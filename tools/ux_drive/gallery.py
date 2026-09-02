from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from tools.ux_drive import ARTIFACTS_ROOT, SESSION_PATH


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slug(label: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", label.strip()).strip("-").lower()
    return cleaned or "shot"


def ensure_run_dir(run_id: str | None = None) -> Path:
    ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = ARTIFACTS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    index = run_dir / "INDEX.md"
    if not index.exists():
        index.write_text(f"# UX run `{run_id}`\n\n| # | Label | File | When | Note |\n|---|-------|------|------|------|\n", encoding="utf-8")
    return run_dir


def next_index(run_dir: Path) -> int:
    existing = list(run_dir.glob("[0-9][0-9]-*.png"))
    if not existing:
        return 1
    nums = []
    for path in existing:
        try:
            nums.append(int(path.name.split("-", 1)[0]))
        except ValueError:
            continue
    return max(nums, default=0) + 1


def write_state(run_dir: Path, payload: dict) -> Path:
    path = run_dir / "STATE.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def append_index(run_dir: Path, number: int, label: str, filename: str, note: str = "") -> None:
    index = run_dir / "INDEX.md"
    line = f"| {number:02d} | {label} | `{filename}` | {utc_now()} | {note.replace('|', '/')} |\n"
    with index.open("a", encoding="utf-8") as handle:
        handle.write(line)


def add_screenshot(run_dir: Path, label: str, source: Path, note: str = "") -> Path:
    number = next_index(run_dir)
    filename = f"{number:02d}-{slug(label)}.png"
    dest = run_dir / filename
    shutil.copy2(source, dest)
    append_index(run_dir, number, label, filename, note)
    return dest


def write_findings(run_dir: Path, text: str) -> Path:
    path = run_dir / "FINDINGS.md"
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def load_session() -> dict:
    if not SESSION_PATH.exists():
        return {}
    return json.loads(SESSION_PATH.read_text(encoding="utf-8"))


def save_session(data: dict) -> None:
    ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def clear_session() -> None:
    if SESSION_PATH.exists():
        SESSION_PATH.unlink()
