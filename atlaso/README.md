# Atlaso — memory for Claude Code

**Claude Code forgets everything the moment a session ends. Atlaso remembers** —
it recalls your decisions, conventions, and context before every prompt and
captures what's new after every turn. Fully automatic; nothing to type.

## Install

1. Create a free account at [app.atlaso.ai](https://app.atlaso.ai/sign-in) and
   follow the connect flow for Claude Code (it authorizes this device), then:

```
/plugin marketplace add atlaso-labs/claude-code
/plugin install atlaso@atlaso
```

**What you get**

- One memory across every AI tool you use — what Claude Code learns, Cursor, Codex, and the rest already know
- Personal memory that follows you, plus per-project memory keyed to each repo
- Secrets scrubbed client-side before anything is stored; your memory is never trained on or sold
- Free for one device and one tool — no credit card ([pricing](https://www.atlaso.ai/pricing))

**Links:** [Why Atlaso for Claude Code](https://www.atlaso.ai/for/claude-code) ·
[Setup guide](https://docs.atlaso.ai/tools/claude-code) ·
[What is an AI memory layer?](https://www.atlaso.ai/what-is-an-ai-memory-layer) ·
[Dashboard](https://app.atlaso.ai/sign-in)

---

## How it's built (for the curious)

The Claude Code connector for Atlaso memory. Lives under `platform/tools/<tool>/`
— one folder per tool we support (Claude Code first, then Claude Desktop, Codex, …).

It's deliberately thin: every hook just calls the tool-agnostic core
(`platform/client` → `atlaso_client.Client`). Nothing smart lives here; the engine
stays on the server.

## The four hooks

Claude Code's event names are fixed; we brand our side (script names + the block
we inject). Each hook → one Atlaso action:

| Atlaso hook | Claude Code event | What it does |
|---|---|---|
| **recall** (`hooks/recall.sh`) | `UserPromptSubmit` | Inject recalled memory before each prompt. Synchronous, fast. |
| **capture** (`hooks/capture.sh`) | `Stop` | Save the just-finished exchange. Instant **local** write (no network), synced later. |
| **start** (`hooks/start.sh`) | `SessionStart` | Sync the cache with the cloud. Detached — never delays session open. |
| **end** (`hooks/end.sh`) | `SessionEnd` | Flush this session's memories up + pull new ones. Detached. |

Injected block (no instructions — the model decides how to use it):

```
=== Atlaso Memory ===
- recalled note
- recalled note
=== Atlaso Memory ===
```

Hooks **fail open**: a missing interpreter or any error → silent no-op, the turn
proceeds. A light commodity filter skips trivial acks ("ok", "thanks") on capture;
the real "worth keeping" gate runs server-side.

## Layout

```
tools/claude-code/
  hooks/         recall.sh · capture.sh · start.sh · end.sh   (shims)
  atlaso_cc/     recall.py · capture.py · sync.py · transcript.py · _shim.py
  tests/         test_recall · test_capture · test_transcript
```

Later: `.mcp.json` (active memory tools), a `SKILL.md`, and a `plugin.json` to
bundle all of it as the installable `atlaso` plugin.

## Dev / test

Hooks resolve the SDK venv (it has `httpx`) and the `atlaso_client` package by
relative path. Run the tests:

```bash
cd platform/tools/claude-code
PYTHONPATH=".:../../client" ../../sdk/.venv/bin/python -m pytest tests -q
```

Manual end-to-end (offline, throwaway dir):
```bash
export ATLASO_GLOBAL_PATH=/tmp/atlaso-hooktest   # redirects auth + cache here
printf '{"type":"user","message":{"content":"always use pnpm not npm"}}\n' > /tmp/t.jsonl
echo '{"transcript_path":"/tmp/t.jsonl"}' | ./hooks/capture.sh
echo '{"prompt":"which package manager"}' | ./hooks/recall.sh   # → injects the block
```

`ATLASO_DEBUG=1` writes per-hook logs to `<atlaso dir>/atlaso-*.log`.
