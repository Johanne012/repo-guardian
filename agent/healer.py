#!/usr/bin/env python3
"""
Repo Guardian — Healer
يقترح أو ينفّذ إصلاحات محدودة (إنشاء Issues، تحديث ملفات بسيطة).
لا يحذف ولا يؤرشف تلقائياً — يحتاج تأكيد بشري.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

OWNER = os.environ.get("GITHUB_OWNER", "Johanne012")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
API = "https://api.github.com"


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-guardian",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def create_issue(repo: str, title: str, body: str, labels: list[str] | None = None) -> dict | None:
    if not TOKEN:
        print(f"[dry-run] would create issue in {repo}: {title}")
        return None
    data = json.dumps({"title": title, "body": body, "labels": labels or []}).encode()
    req = urllib.request.Request(
        f"{API}/repos/{OWNER}/{repo}/issues",
        data=data,
        headers=_headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except Exception as e:
        print(f"Failed to create issue in {repo}: {e}")
        return None


def process_report(report: dict[str, Any], auto_issue: bool = True) -> list[str]:
    """يعالج التقرير وينشئ Issues للحالات الحرجة إذا لزم."""
    actions_taken: list[str] = []

    for item in report.get("critical", []):
        name = item["name"]
        action = item.get("action", "none")
        issues = item.get("issues", [])

        if action == "confirm_rename":
            title = f"[CRITICAL] إعادة تسمية المستودع — اسم مؤقت: {name}"
            body = (
                f"## مشكلة مكتشفة تلقائياً\n\n"
                f"المستودع `{name}` يحمل اسماً مؤقتاً أو غير مناسب.\n\n"
                f"**الإجراء المطلوب:** Settings → Repository name → اختر اسماً احترافياً.\n\n"
                f"المشاكل: {', '.join(issues)}\n\n"
                f"— Repo Guardian"
            )
            if auto_issue:
                result = create_issue(name, title, body, ["documentation"])
                if result:
                    actions_taken.append(f"issue_created:{name}#{result.get('number')}")

        elif action in ("confirm_archive", "confirm_archive_or_fix", "review_or_archive"):
            title = f"[CRITICAL] مراجعة / أرشفة مطلوبة — {name}"
            body = (
                f"## مشكلة مكتشفة تلقائياً\n\n"
                f"المستودع `{name}` يحتاج مراجعة.\n\n"
                f"- المشاكل: {', '.join(issues)}\n"
                f"- أيام منذ آخر push: {item.get('days_since_push')}\n"
                f"- Vercel: {item.get('vercel')}\n\n"
                f"**الإجراء المقترح:** أرشفة من Settings → Danger Zone، أو إصلاح المشكلة.\n\n"
                f"— Repo Guardian"
            )
            if auto_issue:
                result = create_issue(name, title, body)
                if result:
                    actions_taken.append(f"issue_created:{name}#{result.get('number')}")

    return actions_taken


def main() -> None:
    report_path = os.environ.get("REPORT_PATH", "report.json")
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    actions = process_report(report, auto_issue=os.environ.get("AUTO_ISSUE", "true").lower() == "true")
    print("Healer actions:", actions or "none")


if __name__ == "__main__":
    main()
