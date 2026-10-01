"""Shared plumbing for the Atlaso Claude Code hooks.

Every hook is a thin shim: read the event payload from stdin, build the
tool-agnostic ``atlaso_client.Client``, do one small thing, and NEVER break the
turn (all failures swallow → exit 0).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def read_payload() -> dict:
    """Parse the hook's stdin JSON; {} on anything malformed/empty."""
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def is_recursive() -> bool:
    """True inside our own nested model calls (future server/L2 enrichment), so
    memory never recalls/captures itself into a loop."""
    return bool(os.environ.get("ATLASO_EXTRACTING"))


# This connector's tool id — must match the agent id the web app / brain use.
# Env-overridable (parity with codex/antigravity, added 2026-09-01): Grok Build
# AUTO-READS Claude Code plugins with zero configuration, so a host other than
# Claude Code can execute these very bytes — a hardcoded id would then tag every
# capture "claude-code" (wrong Connections entry, wrong free-plan slot). The
# hook launchers of any such host must export ATLASO_TOOL; Claude Code itself
# sets nothing and keeps the default.
TOOL = os.environ.get("ATLASO_TOOL") or "claude-code"


def make_client():
    """Build the memory client (reads ~/.atlaso/auth.json; offline-safe).
    Imported lazily so the hook modules stay importable without the client dep
    (tests inject a fake client). Tagged with this tool id so the client's plan
    entitlement knows which tool is asking (free = only the active tool is
    cloud-linked; others run local-only)."""
    from atlaso_client import Client, _deadline

    client = Client(tool=TOOL)
    # Hooks bound the brain round trip by wall clock; past it recall answers from the
    # local cache (rung "hooks never hang").
    client.recall_network_budget = _deadline.NETWORK_BUDGET_S
    return client


def make_local_client():
    """The capture hooks' client: the local cache only, with NO network before the turn is
    written. Resolving the tool credential can mint one over the network (device exchange,
    8 s per read), and a capture worker cut off there used to lose the turn before it reached
    the cache (rung "hooks never hang", round 2). What reaches the cloud, and when, stays with
    sync, which builds the full client and applies the entitlement gate."""
    from atlaso_client import Client

    return Client(tool=TOOL, _auto_api=False)


def user_label() -> str:
    """A friendly user label for the recall block header (the connected user_id, or
    'you'). Cosmetic; never raises."""
    try:
        from atlaso_client import config
        return (config.load_auth() or {}).get("user_id") or "you"
    except Exception:
        return "you"


def maybe_autoconnect() -> bool:
    """If this machine isn't connected yet, spawn the (detached) browser-authorize
    flow. Fast + best-effort — never blocks the hook, never raises."""
    try:
        from atlaso_client.connect import maybe_autoconnect as _mc

        return _mc(tool=TOOL)
    except Exception:
        return False


def log(name: str, msg: str) -> None:
    """Opt-in debug log (set ATLASO_DEBUG=1). Off by default — hooks stay quiet."""
    if not os.environ.get("ATLASO_DEBUG"):
        return
    try:
        base = (
            os.environ.get("ATLASO_GLOBAL_PATH")
            or os.environ.get("ATLASO_PATH")
            or str(Path.home() / ".atlaso")
        )
        d = Path(base)
        d.mkdir(parents=True, exist_ok=True)
        with open(d / f"atlaso-{name}.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} {msg}\n")
    except Exception:
        pass
