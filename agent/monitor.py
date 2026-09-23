#!/usr/bin/env python3
"""
Repo Guardian — Monitor
يجمع بيانات المستودعات من GitHub API ويفحص Vercel.

التوكن:
  - GITHUB_TOKEN (Actions الافتراضي): محدود غالباً بمستودع واحد
  - GUARDIAN_PAT (اختياري): Personal Access Token بصلاحية repo لرؤية كل المستودعات
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
TOKEN = (
    os.environ.get("GUARDIAN_PAT")
    or os.environ.get("GITHUB_TOKEN")
    or os.environ.get("GH_TOKEN")
)
API = "https://api.github.com"


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-guardian/1.1",
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
        req = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "repo-guardian/1.1"}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            return "ok" if r.status < 400 else f"http_{r.status}"
    except urllib.error.HTTPError as e:
        return f"http_{e.code}"
    except Exception:
        return "error"


def fetch_all_repos() -> list[dict[str, Any]]:
    repos: list[dict] = []
    page = 1

    # جرّب /user/repos أولاً (يحتاج PAT كامل)، وإلا العامة
    use_user_endpoint = bool(TOKEN)

    while True:
        if use_user_endpoint:
            path = f"/user/repos?per_page=100&page={page}&sort=updated&affiliation=owner"
        else:
            path = f"/users/{OWNER}/repos?per_page=100&page={page}&sort=updated"

        try:
            batch = api_get(path)
        except urllib.error.HTTPError as e:
            if use_user_endpoint and e.code in (401, 403):
                print(f"warn: /user/repos failed ({e.code}), falling back to public list")
                use_user_endpoint = False
                page = 1
                repos = []
                continue
            raise

        if not batch:
            break

        if use_user_endpoint:
            batch = [r for r in batch if r.get("owner", {}).get("login") == OWNER]

        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    return repos


def analyze(repo: dict[str, Any]) -> dict[str, Any]:
    name = repo["name"]
    pushed = repo.get("pushed_at")
    days = days_since(pushed)
    homepage = (repo.get("homepage") or "").strip()
    desc = (repo.get("description") or "").strip()
    size = repo.get("size") or 0
    archived = repo.get("archived", False)
    open_issues = repo.get("open_issues_count") or 0
    private = repo.get("private", False)

    issues: list[str] = []
    severity = "info"
    action = "none"

    if archived:
        return {
            "name": name,
            "severity": "info",
            "score": 100,
            "issues": ["archived"],
            "action": "none",
            "days_since_push": days,
            "vercel": "skipped",
            "private": private,
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language"),
            "html_url": repo.get("html_url"),
            "archived": True,
            "size": size,
        }

    bad_name_patterns = ("Repository-name", "temp-", "untitled", "test-repo")
    if any(p.lower() in name.lower() for p in bad_name_patterns):
        issues.append(f"bad_name:{name}")
        severity = "critical"
        action = "confirm_rename"

    if size < 10 and not desc:
        issues.append("nearly_empty")
        if severity == "info":
            severity = "warning"
        if action == "none":
            action = "review_or_archive"

    if size <= 10 and days is not None and days > 45:
        issues.append("skeleton_stale")
        severity = "critical"
        if action == "none":
            action = "confirm_archive"

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

    score = 95 if not issues else (20 if severity == "critical" else 55)

    return {
        "name": name,
        "severity": severity,
        "score": score,
        "issues": issues,
        "action": action,
        "days_since_push": days,
        "vercel": vercel_status,
        "private": private,
        "stars": repo.get("stargazers_count", 0),
        "language": repo.get("language"),
        "html_url": repo.get("html_url"),
        "archived": archived,
        "size": size,
    }


def run() -> dict[str, Any]:
    try:
        repos = fetch_all_repos()
    except Exception as e:
        print(f"ERROR fetching repos: {e}")
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "owner": OWNER,
            "authenticated": bool(TOKEN),
            "error": str(e),
            "total": 0,
            "critical_count": 0,
            "warning_count": 0,
            "ok_count": 0,
            "critical": [],
            "warning": [],
            "all": [],
        }

    results = [analyze(r) for r in repos]
    critical = [r for r in results if r["severity"] == "critical"]
    warning = [r for r in results if r["severity"] == "warning"]
    ok = [r for r in results if r["severity"] == "info"]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": OWNER,
        "authenticated": bool(TOKEN),
        "total": len(results),
        "critical_count": len(critical),
        "warning_count": len(warning),
        "ok_count": len(ok),
        "critical": critical,
        "warning": warning,
        "all": results,
    }


def main() -> None:
    report = run()
    out_path = os.environ.get("REPORT_PATH", "report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Repo Guardian Report — {report['generated_at']}")
    print(
        f"Auth: {report['authenticated']} | Total: {report['total']} | "
        f"Critical: {report['critical_count']} | Warning: {report['warning_count']} | OK: {report['ok_count']}"
    )
    if report.get("error"):
        print(f"ERROR: {report['error']}")

    if report["critical"]:
        print("=== CRITICAL ===")
        for r in report["critical"]:
            priv = " [private]" if r.get("private") else ""
            print(f"  [{r['score']}] {r['name']}{priv}: {', '.join(r['issues'])} → {r['action']}")

    if report["warning"]:
        print("=== WARNING ===")
        for r in report["warning"]:
            print(f"  [{r['score']}] {r['name']}: {', '.join(r['issues'])}")

    # لا نخرج بـ exit 1 حتى لا نكسر الـ pipeline؛ القرار في decision.py
    sys.exit(0)


if __name__ == "__main__":
    main()
