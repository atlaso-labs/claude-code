"""capture hook (Claude Code Stop): save the just-finished exchange to memory.

Pulls the last user/assistant exchange from the transcript and hands it to the
thin client's commodity capture pipeline (worth-keeping gate → secret scrub →
scope route → polarity hint → near-dup → tagged local write). All commodity
(no engine/IP); the smart ranking/gate stays on the server. Never breaks the turn.

After the local write we kick a DEBOUNCED detached background sync (the WAF/
outbox incident proved that session-boundary-only sync strands memories for
hours in long-lived sessions). SessionStart/SessionEnd remain the backstops.
"""
from __future__ import annotations

import os
import subprocess
import sys

from . import _shim
from .transcript import last_exchange


def _flush_detached_if_due(client) -> None:
    """Spawn a background sync when the debounce/lease heuristics say it's time.
    Detached + best-effort — never blocks or breaks the turn."""
    try:
        from atlaso_client import _flush
        if not _flush.should_flush(client.cache):
            return
        subprocess.Popen(
            [sys.executable, "-m", "atlaso_cc.sync"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env=dict(os.environ),
        )
    except Exception:
        pass


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
        _flush_detached_if_due(client)
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
