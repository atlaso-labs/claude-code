#!/usr/bin/env bash
# Atlaso Memory — recall hook (Claude Code UserPromptSubmit).
# Injects recalled memory. Resolver picks built (uv runtime) or dev mode.
# Never breaks the turn (best-effort, always exit 0).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
atlaso_run atlaso_cc.recall
exit 0
