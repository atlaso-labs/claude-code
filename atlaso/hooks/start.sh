#!/usr/bin/env bash
# Atlaso Memory — start hook (Claude Code SessionStart).
# Syncs in the BACKGROUND (detached) so the session opens instantly. In built
# mode the first uv run here also warms the runtime env for the session.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
# Foreground + fast (file-only, no network): emit the local-only banner
# (systemMessage) AND the cached Ambient Memory orientation block
# (additionalContext) in one SessionStart result. Both optional.
atlaso_run atlaso_cc.start
# Then sync in the BACKGROUND (detached) so the session opens instantly.
( atlaso_run atlaso_cc.sync ) >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
