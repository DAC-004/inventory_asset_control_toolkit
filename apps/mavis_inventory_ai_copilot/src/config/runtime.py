"""Runtime environment detection."""

from __future__ import annotations

import os
import sys


def is_browser_runtime() -> bool:
    """True when running inside Pyodide/Stlite (Vercel static deploy)."""
    if sys.platform == "emscripten":
        return True
    if "pyodide" in sys.modules:
        return True
    if os.getenv("STLITE_BROWSER") == "1":
        return True
    return False


def is_vercel_runtime() -> bool:
    """True on Vercel serverless or when explicitly flagged."""
    return bool(os.getenv("VERCEL")) or is_browser_runtime()
