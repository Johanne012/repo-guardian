#!/usr/bin/env python3
"""
Repo Guardian — Notify
يرسل تنبيهاً فقط عند Critical.

القنوات المدعومة عبر متغيرات البيئة:
  - DISCORD_WEBHOOK_URL
  - SLACK_WEBHOOK_URL
  - (البريد عبر GitHub Issue كقناة افتراضية — من healer)

لا يرسل شيئاً إذا notify.flag = no
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


def _post_json(url: str, payload: dict) -> bool:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "repo-guardian/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status < 300
    except Exception as e:
        print(f"notify failed: {e}")
        return False


def main() -> None:
    flag = Path("notify.flag")
    if not flag.exists() or flag.read_text().strip() != "yes":
        print("No notification needed (flag != yes)")
        return

    summary = Path("summary.md")
    text = summary.read_text(encoding="utf-8") if summary.exists() else "Critical issues found."

    # اقتطاع للنص الطويل
    if len(text) > 1800:
        text = text[:1800] + "\n\n...(truncated)"

    sent = False

    discord = os.environ.get("DISCORD_WEBHOOK_URL")
    if discord:
        ok = _post_json(discord, {"content": f"**Repo Guardian CRITICAL**\n```\n{text[:1500]}\n```"})
        print(f"Discord: {'ok' if ok else 'fail'}")
        sent = sent or ok

    slack = os.environ.get("SLACK_WEBHOOK_URL")
    if slack:
        ok = _post_json(slack, {"text": f"Repo Guardian CRITICAL\n{text[:1500]}"})
        print(f"Slack: {'ok' if ok else 'fail'}")
        sent = sent or ok

    if not sent:
        print("No webhook configured — GitHub Issues remain the primary channel")


if __name__ == "__main__":
    main()
