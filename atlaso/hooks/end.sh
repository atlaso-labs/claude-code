#!/usr/bin/env bash
# Atlaso Memory — end hook (Claude Code SessionEnd).
# Flushes this session's memories up + pulls new ones, in the BACKGROUND (detached).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_resolve.sh"
( atlaso_run atlaso_cc.sync ) >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
