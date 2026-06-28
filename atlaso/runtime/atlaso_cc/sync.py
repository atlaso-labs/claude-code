"""start hook (SessionStart) + end hook (SessionEnd): sync the local cache.

Both push any queued local memories up and pull new ones down (other devices,
this session's captures). Launched DETACHED by the shim so it never delays the
session opening or closing. Same entrypoint for both events — the work is identical.
"""
from __future__ import annotations

import sys

from . import _shim


def run(client) -> dict:
    return client.sync_once()


def main() -> int:
    # On session start/end, also kick off connect if this machine isn't linked yet.
    _shim.maybe_autoconnect()
    try:
        client = _shim.make_client()
    except Exception:
        return 0
    try:
        out = run(client)
        _shim.log("sync", f"{out}")
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
