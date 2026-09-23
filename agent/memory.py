#!/usr/bin/env python3
"""
Repo Guardian — Memory
يسجّل القرارات السابقة (Issues مغلقة، أرشفة، إعادة تسمية)
لتجنب إعادة فتح نفس المشاكل.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

MEMORY_PATH = os.environ.get("MEMORY_PATH", "memory/decisions.json")


def load() -> dict:
    p = Path(MEMORY_PATH)
    if not p.exists():
        return {"decisions": [], "updated_at": None}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(data: dict) -> None:
    p = Path(MEMORY_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record(repo: str, action: str, note: str = "") -> None:
    data = load()
    data["decisions"].append({
        "repo": repo,
        "action": action,
        "note": note,
        "at": datetime.now(timezone.utc).isoformat(),
    })
    # احتفظ بآخر 200 قرار فقط
    data["decisions"] = data["decisions"][-200:]
    save(data)


def was_handled(repo: str, action: str) -> bool:
    data = load()
    for d in reversed(data.get("decisions", [])):
        if d.get("repo") == repo and d.get("action") == action:
            return True
    return False


if __name__ == "__main__":
    record("repo-guardian", "system_init", "memory module online")
    print(json.dumps(load(), ensure_ascii=False, indent=2))
