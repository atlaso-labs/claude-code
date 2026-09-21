#!/usr/bin/env bash
# Atlaso Memory — start hook (Claude Code SessionStart).
# Syncs in the BACKGROUND (detached) without waiting for the full sync. In built
# mode the first uv run here also warms the runtime env for the session.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
# Foreground + bounded (fresh ambient policy validation): emit the local-only banner
# (systemMessage) AND the project-aware Ambient Memory orientation block
# (additionalContext) in one SessionStart result. Both optional.
atlaso_run atlaso_cc.start
# Then sync in the BACKGROUND (detached) without waiting for the full sync.
( atlaso_run atlaso_cc.sync ) >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
