# Changelog

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

## 0.1.11 (2026-09-21)
- Project-aware Ambient Memory: scoped first-session context, enrichment lineage fixes. Qualified against emergence-lab a895cf5e (core a0a461ff).
