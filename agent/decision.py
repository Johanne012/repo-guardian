#!/usr/bin/env python3
"""
Repo Guardian — Decision
يلخّص التقرير ويقرر هل يجب إرسال تنبيه (Critical فقط).
"""

from __future__ import annotations

import json
import os
from typing import Any


def should_notify(report: dict[str, Any]) -> bool:
    return report.get("critical_count", 0) > 0


def summary_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Repo Guardian Report",
        f"",
        f"**Generated:** {report.get('generated_at')}",
        f"**Owner:** {report.get('owner')}",
        f"**Authenticated:** {report.get('authenticated')}",
        f"",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total repos | {report.get('total')} |",
        f"| Critical | {report.get('critical_count')} |",
        f"| Warning | {report.get('warning_count')} |",
        f"| OK | {report.get('ok_count')} |",
        f"",
    ]

    if report.get("critical"):
        lines.append("## Critical")
        lines.append("")
        for r in report["critical"]:
            priv = " 🔒" if r.get("private") else ""
            lines.append(
                f"- **{r['name']}**{priv} (score {r['score']}): "
                f"{', '.join(r['issues'])} → `{r['action']}`"
            )
        lines.append("")

    if report.get("warning"):
        lines.append("## Warning")
        lines.append("")
        for r in report["warning"]:
            lines.append(f"- **{r['name']}**: {', '.join(r['issues'])}")
        lines.append("")

    lines.append("---")
    lines.append("*Notification only on Critical. Warnings logged only.*")
    return "\n".join(lines)


def main() -> None:
    report_path = os.environ.get("REPORT_PATH", "report.json")
    with open(report_path, encoding="utf-8") as f:
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


if __name__ == "__main__":
    main()
