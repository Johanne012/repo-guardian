"""
Repo Guardian — Monitor module
يجمع بيانات المستودعات من GitHub API + حالة Vercel
"""

from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import Any

# هذا الملف هو الهيكل الأولي.
# سيتم توسيعه لاحقاً ليعمل مع GitHub API و Vercel.

def fetch_repos(owner: str) -> list[dict[str, Any]]:
    """جلب قائمة المستودعات مع البيانات الأساسية."""
    # TODO: استدعاء GitHub API
    raise NotImplementedError("سيتم ربطه بـ GitHub API في الخطوة التالية")


def check_vercel(url: str | None) -> str:
    """فحص حالة رابط Vercel. يرجع 'ok' أو '404' أو 'error'."""
    if not url:
        return "no_url"
    # TODO: طلب HEAD
    raise NotImplementedError


def days_since(iso_date: str) -> int:
    dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return (now - dt).days


if __name__ == "__main__":
    print("Repo Guardian Monitor — skeleton ready")
