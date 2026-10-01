#!/usr/bin/env bash
# Atlaso Memory — start hook (Claude Code SessionStart).
# Syncs in the BACKGROUND (detached) without waiting for the full sync. In built
# mode a runtime that is not ready yet is warmed in the background, never inside this hook.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
# Foreground + bounded (fresh ambient policy validation): emit the local-only banner
# (systemMessage) AND the project-aware Ambient Memory orientation block
# (additionalContext) in one SessionStart result. Both optional.
atlaso_fg claude-code start "$ATLASO_START_BUDGET" atlaso_cc.start
# Then sync in the BACKGROUND (detached) without waiting for the full sync.
atlaso_bg claude-code start atlaso_cc.sync
exit 0
