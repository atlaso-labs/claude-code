"""capture hook (Claude Code Stop): save the just-finished exchange to memory.

Pulls the last user/assistant exchange from the transcript and hands it to the
thin client's commodity capture pipeline (worth-keeping gate → secret scrub →
scope route → polarity hint → near-dup → tagged local write that syncs on
start/end). All commodity (no engine/IP); the smart ranking/gate stays on the
server. Never breaks the turn.
"""
from __future__ import annotations

import sys

from . import _shim
from .transcript import last_exchange


def run(payload: dict, client) -> bool:
    """Pure logic (testable): returns True if a memory was queued."""
    transcript = payload.get("transcript_path") or ""
    user_text, asst_text = last_exchange(transcript) if transcript else ("", "")
    if not user_text:
        user_text = (payload.get("prompt") or "").strip()
    if not user_text:
        return False
    return bool(client.capture(user_text, asst_text or None).get("saved"))


def main() -> int:
    if _shim.is_recursive():
        return 0
    payload = _shim.read_payload()
    try:
        client = _shim.make_client()
    except Exception:
        return 0
    try:
        saved = run(payload, client)
        _shim.log("capture", f"saved={saved}")
    except Exception as e:
        _shim.log("capture", f"error {e!r}")
    finally:
        try:
            client.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
