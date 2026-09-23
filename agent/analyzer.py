"""
Analyzer logic is integrated into monitor.py (function `analyze`).
This file documents the contract only.
"""

# Contract (implemented in monitor.py):
#
# def analyze(repo: dict) -> dict:
#     returns {
#       name, severity, score, issues, action,
#       days_since_push, vercel, private, stars, language, html_url, archived
#     }
#
# severity: info | warning | critical
# action: none | confirm_rename | confirm_archive | confirm_archive_or_fix | review_or_archive
