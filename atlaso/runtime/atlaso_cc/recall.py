"""recall hook (Claude Code UserPromptSubmit): inject recalled memory.

Queries the memory client for the current prompt and injects the hits as a plain,
branded block:

    === Atlaso Memory ===
    - recalled note
    - recalled note
    === Atlaso Memory ===

No instructions, no warnings — just the brand at top and bottom. The model decides
how to use it. Synchronous + cheap (server recall, or local cache when offline).
Fails open: any error → no injection, the turn proceeds.
"""
from __future__ import annotations

import json
import os
import sys

from atlaso_client import _project, _render

from . import _shim


def run(payload: dict, client) -> dict | None:
    """Pure logic (testable): payload + client → the hookSpecificOutput dict or None.
    Recall is per-project-scoped (personal + THIS project) and rendered as the
    plain branded memory block with [personal]/[project] labels — no internal ids
    leaked."""
    prompt = (payload.get("prompt") or payload.get("message") or "").strip()
    if not prompt:
        return None
    try:
        limit = int(os.environ.get("ATLASO_RECALL_LIMIT", "5"))
    except ValueError:
        limit = 5
    # Claude Code provides session_id in the hook payload; threading it lets the
    # server record which memories were injected this session so the SessionEnd
    # usefulness judge can later grade them (the recall-usefulness feedback loop).
    session = payload.get("session_id") or payload.get("session")
    res = client.recall(prompt, limit=limit, project=_project.project_key(), session=session)
    block = _render.recall_block(res, uid=_shim.user_label())
    if not block:
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": block,
        }
    }


def main() -> int:
    if _shim.is_recursive():
        return 0
    # If not connected yet, kick off the (detached) browser-authorize in the
    # background — so the user's next prompt after installing the plugin triggers
    # it automatically. Recall still proceeds (local) meanwhile.
    _shim.maybe_autoconnect()
    payload = _shim.read_payload()
    try:
        client = _shim.make_client()
    except Exception:
        return 0
    out = None
    try:
        out = run(payload, client)
    except Exception as e:
        _shim.log("recall", f"error {e!r}")
    finally:
        try:
            client.close()
        except Exception:
            pass
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
