"""Ambient Memory for Claude Code — fetch the orientation block from the brain
(the single source every tool shares) and inject it as SessionStart
additionalContext. Reads the CACHED block (file-only, instant); the background
sync refreshes it. Never raises.
"""
from __future__ import annotations


def run(client) -> dict | None:
    try:
        block = client.ambient_cached()
    except Exception:
        return None
    if not block:
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": block,
        }
    }
