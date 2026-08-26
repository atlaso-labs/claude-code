"""start hook (SessionStart) + end hook (SessionEnd): sync the local cache.

Both push any queued local memories up and pull new ones down (other devices,
this session's captures). Launched DETACHED by the shim so it never delays the
session opening or closing. Same entrypoint for both events — the work is identical.

THIS IS ALSO WHERE THE INSTALL CANARY FIRES. See _attest() below — and read that
comment before moving the call, because where it sits is the whole point.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from . import _shim


def run(client) -> dict:
    return client.sync_once()


def _attest() -> None:
    """Report that the HOOK CAPTURE PATH is genuinely alive — the install canary.

    WHY HERE AND NOWHERE EARLIER. This call sits AFTER `client.sync_once()` has
    reported `synced: True` — a completed authenticated round-trip, not merely a
    return — and that ordering AND that condition are both load-bearing. Reaching this
    line means the whole chain worked: the agent host executed the hook, _resolve.sh
    found a runtime, the Python shim imported, atlaso_client built, the credential
    was accepted, and a real authenticated round-trip to the brain completed. Emitted
    at hook LAUNCH instead, it would prove none of that — a hook can be registered,
    start, and have its shim throw on import, which is an ordinary partial install
    that a launch-time proof would report as healthy.

    WHY A MEMORY WRITE CANNOT SUBSTITUTE. The install surface already treats "a
    memory write landed" as evidence of a working install, and it is not: the MCP
    path writes memory on its own, so that signal fires with hooks completely dead.
    THIS is the signal that distinguishes "hooks working" from "device authorized" —
    it can only be produced by code the host actually ran as a hook.

    Never raises, never delays: this runs detached, after the sync it observes.
    """
    try:
        from atlaso_client import attest, config
    except Exception:
        return
    auth = config.load_tool_auth(_shim.TOOL) or config.load_auth() or {}
    token, server = auth.get("token"), auth.get("server")
    if not token or not server:
        return
    try:
        attest.prove(attest.HOOK_CAPTURE, tool=_shim.TOOL, server=server, token=token)
    except Exception:
        pass

    # skill_present: a FILE-PRESENCE claim, and deliberately the weakest of the
    # three. The hook reports it because the hook is the only one of our processes
    # that knows its own plugin root — the installer does not (the host chooses the
    # root, it is versioned per update, and it may not exist until after install).
    # Grade it lower wherever it is rendered; it must never lift an aggregate verdict
    # on its own, because a skill file sitting on disk says nothing about whether the
    # model ever loaded it.
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if root and (Path(root) / "skills" / "memory" / "SKILL.md").is_file():
        try:
            attest.prove(attest.SKILL_PRESENT, tool=_shim.TOOL, server=server, token=token)
        except Exception:
            pass


def main() -> int:
    # On session start/end, also kick off connect if this machine isn't linked yet.
    _shim.maybe_autoconnect()
    # Sync lease: Claude Code + Codex share one cache/outbox on a machine; a fresh
    # lease means another sync is already in flight — skip instead of stampeding.
    from atlaso_client import _flush
    with _flush.lease() as acquired:
        if not acquired:
            return 0
        try:
            client = _shim.make_client()
        except Exception:
            return 0
        try:
            out = run(client)
            _shim.log("sync", f"{out}")
            # ONLY after a sync that ACTUALLY REACHED THE BRAIN — see _attest(),
            # and note that `run()` returning is not that. sync_once catches its
            # own transport failures and returns the same {pushed: 0, pulled: 0}
            # shape a healthy empty sync returns, and in local-only it returns it
            # without a single network call. Gating on "it returned" therefore
            # certifies the hook capture path on precisely the two failures the
            # canary exists to catch. `synced is True` — identity, not truthiness,
            # and fail-closed on a missing key so an older bundled runtime reads
            # as unknown rather than as success.
            if isinstance(out, dict) and out.get("synced") is True:
                _attest()
        except Exception as e:
            _shim.log("sync", f"error {e!r}")
        finally:
            try:
                client.close()
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
