#!/usr/bin/env python3
"""
Repo Guardian — Healer
ينشئ Issues للحالات الحرجة مع منع التكرار (dedupe).
لا يحذف ولا يؤرشف تلقائياً.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

OWNER = os.environ.get("GITHUB_OWNER", "Johanne012")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
API = "https://api.github.com"


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-guardian/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def api_get(path: str) -> Any:
    req = urllib.request.Request(f"{API}{path}", headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def list_open_issues(repo: str) -> list[dict]:
    try:
        return api_get(f"/repos/{OWNER}/{repo}/issues?state=open&per_page=50")
    except Exception as e:
        print(f"  warn: cannot list issues for {repo}: {e}")
        return []


def already_has_guardian_issue(repo: str, marker: str) -> bool:
    """يتجنب إنشاء Issue مكررة إذا وُجدت مفتوحة بنفس العلامة."""
    for issue in list_open_issues(repo):
        title = issue.get("title") or ""
        body = issue.get("body") or ""
        if marker in title or marker in body or "Repo Guardian" in body:
            if any(k in title for k in ("CRITICAL", "أرشفة", "إعادة تسمية", "ARCHIVE", "rename")):
                return True
    return False


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
    except urllib.error.HTTPError as e:
        print(f"Failed to create issue in {repo}: HTTP {e.code} {e.read()[:200]}")
        return None
    except Exception as e:
        print(f"Failed to create issue in {repo}: {e}")
        return None


def process_report(report: dict[str, Any], auto_issue: bool = True) -> list[str]:
    actions_taken: list[str] = []

    for item in report.get("critical", []):
        name = item["name"]
        action = item.get("action", "none")
        issues = item.get("issues", [])

        if action == "none":
            continue

        marker = f"repo-guardian:{action}:{name}"

        if already_has_guardian_issue(name, "Repo Guardian"):
            actions_taken.append(f"skipped_dedupe:{name}")
            print(f"  skip (existing guardian issue): {name}")
            continue

        if action == "confirm_rename":
            title = f"[CRITICAL] إعادة تسمية المستودع — اسم مؤقت: {name}"
            body = (
                f"## مشكلة مكتشفة تلقائياً\n\n"
                f"المستودع `{name}` يحمل اسماً مؤقتاً أو غير مناسب.\n\n"
                f"**الإجراء المطلوب:** Settings → Repository name → اختر اسماً احترافياً.\n\n"
                f"المشاكل: {', '.join(issues)}\n\n"
                f"<!-- {marker} -->\n"
                f"— Repo Guardian"
            )
            if auto_issue:
                result = create_issue(name, title, body)
                if result:
                    actions_taken.append(f"issue_created:{name}#{result.get('number')}")

        elif action in ("confirm_archive", "confirm_archive_or_fix", "review_or_archive"):
            title = f"[CRITICAL] مراجعة / أرشفة مطلوبة — {name}"
            body = (
                f"## مشكلة مكتشفة تلقائياً\n\n"
                f"المستودع `{name}` يحتاج مراجعة.\n\n"
                f"- المشاكل: {', '.join(issues)}\n"
                f"- أيام منذ آخر push: {item.get('days_since_push')}\n"
                f"- Vercel: {item.get('vercel')}\n"
                f"- الحجم: {item.get('size')}\n\n"
                f"**الإجراء المقترح:** أرشفة من Settings → Danger Zone، أو إصلاح المشكلة.\n\n"
                f"<!-- {marker} -->\n"
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

    auto = os.environ.get("AUTO_ISSUE", "true").lower() == "true"
    actions = process_report(report, auto_issue=auto)
    print("Healer actions:", actions or "none")

    # حفظ سجل الإجراءات
    with open("healer_actions.json", "w", encoding="utf-8") as f:
        json.dump({"actions": actions}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
