#!/usr/bin/env python3
"""Repo Guardian — Decision"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def should_notify(report: dict[str, Any]) -> bool:
    return report.get("critical_count", 0) > 0


def summary_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Repo Guardian Report",
        "",
        f"**Generated:** {report.get('generated_at')}",
        f"**Owner:** {report.get('owner')}",
        f"**Authenticated:** {report.get('authenticated')}",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total repos | {report.get('total', 0)} |",
        f"| Critical | {report.get('critical_count', 0)} |",
        f"| Warning | {report.get('warning_count', 0)} |",
        f"| OK | {report.get('ok_count', 0)} |",
        "",
    ]

    if report.get("error"):
        lines.append(f"> Error during fetch: `{report['error']}`")
        lines.append("")

    if report.get("critical"):
        lines.append("## Critical")
        lines.append("")
        for r in report["critical"]:
            priv = " (private)" if r.get("private") else ""
            lines.append(
                f"- **{r['name']}**{priv} (score {r['score']}): "
                f"{', '.join(r.get('issues') or [])} -> `{r.get('action')}`"
            )
        lines.append("")

    if report.get("warning"):
        lines.append("## Warning")
        lines.append("")
        for r in report["warning"]:
            lines.append(f"- **{r['name']}**: {', '.join(r.get('issues') or [])}")
        lines.append("")

    lines.append("---")
    lines.append("*Notification only on Critical. Warnings logged only.*")
    return "\n".join(lines)


def main() -> None:
    report_path = os.environ.get("REPORT_PATH", "report.json")
    p = Path(report_path)

    if not p.exists():
        print(f"ERROR: {report_path} not found — creating empty report")
        report = {
            "generated_at": None,
            "owner": os.environ.get("GITHUB_OWNER", "unknown"),
            "authenticated": False,
            "total": 0,
            "critical_count": 0,
            "warning_count": 0,
            "ok_count": 0,
            "critical": [],
            "warning": [],
            "all": [],
            "error": "report.json missing",
        }
    else:
        with open(p, encoding="utf-8") as f:
            report = json.load(f)

    md = summary_markdown(report)
    out = os.environ.get("SUMMARY_PATH", "summary.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)

    notify = should_notify(report)
    print(md)
    print()
    print(f"NOTIFY={notify}")

    with open("notify.flag", "w") as f:
        f.write("yes" if notify else "no")

    sys.exit(0)


if __name__ == "__main__":
    main()
