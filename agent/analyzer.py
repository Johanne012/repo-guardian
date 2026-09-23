"""
Repo Guardian — Analyzer
يحلل بيانات المستودع ويعطي درجة صحة + مستوى خطورة
"""

from __future__ import annotations
from typing import Any


def analyze_repo(repo: dict[str, Any], rules: dict) -> dict[str, Any]:
    """
    يرجع:
    {
      "score": 0-100,
      "severity": "info" | "warning" | "critical" | "confirm",
      "issues": ["..."],
      "recommended_action": "..."
    }
    """
    issues = []
    severity = "info"

    name = repo.get("name", "")
    if "Repository-name" in name or name.startswith("temp-"):
        issues.append("اسم مستودع مؤقت")
        severity = "critical"

    # TODO: المزيد من القواعد من rules.yaml

    return {
        "score": 50 if issues else 85,
        "severity": severity,
        "issues": issues,
        "recommended_action": "confirm_rename" if severity == "critical" else "none",
    }
