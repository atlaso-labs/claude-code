# Changelog

## [0.1.14] - 2026-09-26

Forget now excludes a forgotten memory from Atlaso’s recall and export tools, cleans this device’s cache when possible, and deletes Ambient snapshots already on disk. The MCP result reports `local_cache_cleanup: "done"` or `"pending"`; pending cache cleanup retries when the cache opens or syncs. Memory skills now say that you can’t undo forget, and OpenCode installs the memory skill. A context load already in flight can still contain the forgotten text and make it available to new sessions for up to 15 minutes after that load finishes. The in-flight Ambient fence and the hosted MCP description are not part of this release. Product bytes equal the lab-gated emergence-lab commit 0578e74ac (CodeRedTeam bfe4497e, carried by byte identity 972f474e; DXCritic c27cb73e).

## [0.1.13] - 2026-09-25

Capture keeps corrections. A same-shape update ("we use npm" -> "we use bun") or a reverted decision is no longer dropped as a duplicate of the earlier note, and duplicate checks look only at live memories in the same project. Same-shape updates dropped on the synthetic bench fell from 29 of 106 to 2 of 106 and reverts from 26 of 26 to 0. The client cache gains plain nullable scope columns it fills itself, with no triggers and no SQLite JSON functions, so older plugin versions keep reading and writing the same file. Built from emergence-lab main 0f173e98c (lab gate cleared: LabDirector ruling 9b38478c, CodeRedTeam ec375bd7, DXCritic 6f7c6cf8). Known limit: a correction that only reassigns a value already named in the same note may still be treated as a duplicate; state the change in its own sentence.

## [0.1.12] - 2026-09-24

Intel Macs now get memory. On an Intel (x86_64) Mac the plugin's Python runtime failed to install, because the newest cryptography release has no Intel Mac wheel, and the hooks then ran silently with no memory. The runtime now asks for cryptography 48.x on Intel Macs only; every other platform keeps cryptography 50.x. No other behavior changes. This build was tested with unit and launcher tests; it was not run inside a live Claude Code session.

## [0.1.11] — 2026-09-21

Project-bound SessionStart context with fresh policy checks and a bounded hook deadline. Preserve reconnect notices until output is flushed. Prepared as an unpublished candidate; actual-host delivery remains a separate qualification gate.

All notable changes to the Atlaso Memory plugin.

## [0.1.10] — 2026-08-27

### Added
- **The plugin now proves its install actually works, instead of looking fine
  while half-dead.** A Claude Code plugin can be installed, appear healthy, and
  still have its automatic memory silently broken — the hooks are registered but
  the runtime behind them fails on import, or the credential is never accepted, so
  nothing ever reaches your account. Until now the only visible signal was "a
  memory got written", and that signal is misleading: the memory *tools* write on
  their own path and keep working even when automatic capture is completely dead.

  Two honest signals are now reported. The first is sent only after a session's
  memory sync has completed a real authenticated round-trip — not merely returned,
  which a failed sync also does — so it can only fire if the entire chain worked.
  The second is sent after one of the memory tools has actually run and returned,
  rather than when the tool server starts, because a server that starts and then
  fails is exactly the broken case worth catching.

  Both are sent in the background, carry no memory content, and cannot slow down,
  change, or break anything you do — a health check that can break what it watches
  is worse than none.

## [0.1.9] — 2026-08-03

### Fixed
- **The memory tools work again on a fresh install.** The plugin asked for "the
  MCP library, version 1.27 or newer". A version 2 of that library was published
  on 28 July which moved things around, so any *new* install picked it up and the
  memory tools (`remember`, `recall`, `forget`, `recent`, `status`) failed to
  start. Automatic recall and capture were unaffected — they don't use that
  library — so memory kept working; only the tools you call on purpose were
  broken. The version is now pinned so this cannot happen again.

## [0.1.8] — 2026-08-02

### Fixed
- **Memory recall no longer gives up too early on a busy machine.** Recall runs
  before your prompt is sent, and it was allowed only 15 seconds. That is plenty
  once it is warm (it normally takes about a second), but on a cold start — the
  first prompt after opening your editor, especially while your machine is busy —
  it could run out of time. When that happened the recall was discarded silently:
  no memory for that turn, and nothing to tell you why. The limit is now 30
  seconds, which clears a cold start with room to spare.

  The limit is deliberately kept, not removed: recall blocks your prompt while it
  runs, so an unbounded wait would turn a slow lookup into a frozen session.
