#!/usr/bin/env python3
"""
Repo Guardian — Monitor
يجمع بيانات كل المستودعات من GitHub API ويحسب مؤشرات الصحة.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

OWNER = os.environ.get("GITHUB_OWNER", "Johanne012")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
API = "https://api.github.com"


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-guardian",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def api_get(path: str) -> Any:
    req = urllib.request.Request(f"{API}{path}", headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def days_since(iso: str | None) -> int | None:
    if not iso:
        return None
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - dt).days


def check_url(url: str | None) -> str:
    if not url:
        return "no_url"
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as r:
            return "ok" if r.status < 400 else f"http_{r.status}"
    except urllib.error.HTTPError as e:
        return f"http_{e.code}"
    except Exception:
        return "error"


def fetch_all_repos() -> list[dict[str, Any]]:
    repos: list[dict] = []
    page = 1
    while True:
        batch = api_get(f"/users/{OWNER}/repos?per_page=100&page={page}&sort=updated")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def analyze(repo: dict[str, Any]) -> dict[str, Any]:
    name = repo["name"]
    pushed = repo.get("pushed_at")
    days = days_since(pushed)
    homepage = repo.get("homepage") or ""
    desc = (repo.get("description") or "").strip()
    size = repo.get("size") or 0
    archived = repo.get("archived", False)
    open_issues = repo.get("open_issues_count") or 0

    issues: list[str] = []
    severity = "info"
    action = "none"

    # --- Rules ---
    if archived:
        return {
            "name": name,
            "severity": "info",
            "score": 100,
            "issues": ["archived"],
            "action": "none",
            "days_since_push": days,
            "vercel": "skipped",
        }

    bad_name_patterns = ("Repository-name", "temp-", "untitled", "test-repo")
    if any(p in name for p in bad_name_patterns):
        issues.append(f"bad_name:{name}")
        severity = "critical"
        action = "confirm_rename"

    if size < 10 and not desc:
        issues.append("nearly_empty")
        if severity == "info":
            severity = "warning"
        if action == "none":
            action = "review_or_archive"

    if days is not None and days > 90:
        issues.append(f"stale_{days}d")
        if severity == "info":
            severity = "warning"

    if days is not None and days > 180 and size < 50:
        issues.append("very_stale_and_small")
        severity = "critical"
        action = "confirm_archive"

    vercel_status = "no_url"
    if "vercel.app" in homepage:
        vercel_status = check_url(homepage)
        if vercel_status.startswith("http_4") or vercel_status == "error":
            issues.append(f"vercel_{vercel_status}")
            severity = "critical"
            action = "confirm_archive_or_fix"

    if open_issues > 5:
        issues.append(f"many_open_issues:{open_issues}")
        if severity == "info":
            severity = "warning"

    score = 100
    if severity == "warning":
        score = 60
    if severity == "critical":
        score = 25
    if not issues:
        score = 90

    return {
        "name": name,
        "severity": severity,
        "score": score,
        "issues": issues,
        "action": action,
        "days_since_push": days,
        "vercel": vercel_status,
        "stars": repo.get("stargazers_count", 0),
        "language": repo.get("language"),
        "html_url": repo.get("html_url"),
        "archived": archived,
    }


def run() -> dict[str, Any]:
    repos = fetch_all_repos()
    results = [analyze(r) for r in repos]

    critical = [r for r in results if r["severity"] == "critical"]
    warning = [r for r in results if r["severity"] == "warning"]
    ok = [r for r in results if r["severity"] == "info"]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": OWNER,
        "total": len(results),
        "critical_count": len(critical),
        "warning_count": len(warning),
        "ok_count": len(ok),
        "critical": critical,
        "warning": warning,
        "all": results,
    }
    return report


def main() -> None:
    report = run()
    out_path = os.environ.get("REPORT_PATH", "report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Repos Guardian Report — {report['generated_at']}")
    print(f"Total: {report['total']} | Critical: {report['critical_count']} | Warning: {report['warning_count']} | OK: {report['ok_count']}")
    print()

    if report["critical"]:
        print("=== CRITICAL ===")
        for r in report["critical"]:
            print(f"  [{r['score']}] {r['name']}: {', '.join(r['issues'])} → {r['action']}")
        print()

    if report["warning"]:
        print("=== WARNING ===")
        for r in report["warning"]:
            print(f"  [{r['score']}] {r['name']}: {', '.join(r['issues'])}")
        print()

    # Exit code 1 if critical (useful for CI)
    if report["critical_count"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
