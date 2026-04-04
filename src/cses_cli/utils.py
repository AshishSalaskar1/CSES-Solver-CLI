"""Utility helpers for CSES CLI."""

from __future__ import annotations

from rich.text import Text


def format_time(seconds: float) -> str:
    """Format elapsed time for display."""
    if seconds < 0.01:
        return "<0.01s"
    return f"{seconds:.2f}s"


def verdict_icon(verdict_name: str) -> str:
    """Return an emoji icon for a verdict."""
    icons = {
        "ACCEPTED": "✅",
        "WRONG ANSWER": "❌",
        "RUNTIME ERROR": "💥",
        "TIME LIMIT EXCEEDED": "⏱️",
    }
    return icons.get(verdict_name, "❓")


def verdict_style(verdict_name: str) -> str:
    """Return a Rich style string for a verdict."""
    styles = {
        "ACCEPTED": "green",
        "WRONG ANSWER": "red",
        "RUNTIME ERROR": "yellow",
        "TIME LIMIT EXCEEDED": "magenta",
    }
    return styles.get(verdict_name, "white")
