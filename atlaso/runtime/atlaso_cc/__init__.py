"""Atlaso × Claude Code connector.

Thin hooks that wire Claude Code's lifecycle to the tool-agnostic memory core
(``atlaso_client.Client``). Nothing tool-specific lives in the core; nothing smart
lives here — each hook just reads the event and calls the client.

  recall  (UserPromptSubmit) → inject recalled memory as an "Atlaso Memory" block
  capture (Stop)             → save the just-finished exchange (instant, local)
  start   (SessionStart)     → sync the local cache with the cloud (background)
  end     (SessionEnd)       → flush + sync (background)
"""
__version__ = "0.1.0"

import time as _time

#: When this hook process started running Python code (monotonic). The hook deadline counts
#: from here, so interpreter imports spend the budget too (atlaso_client._deadline.run_hook).
STARTED = _time.monotonic()
