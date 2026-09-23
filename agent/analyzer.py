"""
Analyzer logic is integrated into monitor.py (analyze function).
This file is kept as a thin re-export for compatibility.
"""

from agent.monitor import analyze  # noqa: F401

__all__ = ["analyze"]
