"""
AEONRIFT CLI Cross-Platform Terminal Utilities & Path Normalizer

Provides color formatting, UTF-8/ASCII fallback handling, and path normalization
compatible with Windows (cmd.exe, PowerShell), macOS, and Linux.
"""

import sys
import os
import platform


def supports_color() -> bool:
    """Check if the terminal environment supports ANSI colors."""
    if os.environ.get("NO_COLOR"):
        return False
    if platform.system() == "Windows":
        return "ANSICON" in os.environ or "WT_SESSION" in os.environ or os.environ.get("TERM") == "xterm"
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def is_utf8_terminal() -> bool:
    """Check if stdout encoding supports full UTF-8 emojis."""
    encoding = getattr(sys.stdout, "encoding", "") or ""
    return "UTF" in encoding.upper() or "utf" in encoding.lower()


def style(text: str, color: str = "", bold: bool = False) -> str:
    """Format text with ANSI codes if supported, else return raw text."""
    if not supports_color():
        return text

    colors = {
        "green": "\033[32m",
        "red": "\033[31m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "gray": "\033[90m",
        "neon": "\033[92m",
    }

    reset = "\033[0m"
    bold_code = "\033[1m" if bold else ""
    color_code = colors.get(color, "")

    return f"{bold_code}{color_code}{text}{reset}"


def symbol(name: str) -> str:
    """Return appropriate symbol based on terminal UTF-8 support."""
    utf8_symbols = {
        "ok": "✓",
        "fail": "✗",
        "sparkles": "✨",
        "bolt": "⚡️",
        "doctor": "🩺",
        "save": "💾",
        "fire": "🔥",
        "graph": "📊",
    }
    ascii_symbols = {
        "ok": "[OK]",
        "fail": "[FAIL]",
        "sparkles": "[*]",
        "bolt": "[>]",
        "doctor": "[DOC]",
        "save": "[SAVED]",
        "fire": "[CHAOS]",
        "graph": "[GRAPH]",
    }

    if is_utf8_terminal():
        return utf8_symbols.get(name, "")
    return ascii_symbols.get(name, "")


def normalize_path(path: str) -> str:
    """Cross-platform path normalizer."""
    return os.path.normpath(os.path.abspath(path))
