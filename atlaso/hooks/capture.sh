#!/usr/bin/env bash
# Atlaso Memory — capture hook (Claude Code Stop).
# Saves the just-finished exchange (instant local; synced later). Best-effort.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
atlaso_run atlaso_cc.capture
exit 0
