"""Read a Claude Code transcript JSONL and pull message text.

Each line is a message object: {"type": "user"|"assistant"|..., "message": {"content": ...}}.
``content`` is a string or a list of blocks; only ``{"type":"text"}`` blocks carry
prose (tool_use / tool_result / thinking blocks are skipped).
"""
from __future__ import annotations

import json


def _flatten(content: object) -> str:
    if isinstance(content, list):
        parts = [
            el.get("text", "")
            for el in content
            if isinstance(el, dict) and el.get("type") == "text"
        ]
        return " ".join(p for p in parts if p).strip()
    if isinstance(content, str):
        return content.strip()
    return ""


def last_exchange(path: str) -> tuple[str, str]:
    """Return (last_user_text, assistant_reply_to_it); either may be ''.

    The assistant text is ONLY a reply AFTER the last user message — never an
    earlier turn's, so a Stop hook firing before the reply is flushed pairs the
    new question with '' rather than a stale answer.
    """
    msgs: list[tuple[str, str]] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                typ = obj.get("type")
                if typ not in ("user", "assistant"):
                    continue
                text = _flatten((obj.get("message") or {}).get("content"))
                if text:
                    msgs.append((typ, text))
    except (FileNotFoundError, OSError):
        return "", ""

    last_user_idx = None
    for i, (typ, _) in enumerate(msgs):
        if typ == "user":
            last_user_idx = i
    if last_user_idx is None:
        return "", ""

    last_user = msgs[last_user_idx][1]
    asst = ""
    for typ, text in msgs[last_user_idx + 1:]:
        if typ == "assistant":
            asst = text
    return last_user, asst
