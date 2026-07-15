#!/usr/bin/env python3
"""Hermetic validation of hooks/hooks.json against Claude Code hook-type rules.

No network, no external services. Parses the shipped hooks.json and asserts the
hook type registered under each event is one the harness accepts for that event.

The specific regression this guards: prompt-type hooks are NOT supported for
SessionStart (no conversation context exists at startup), so registering one
makes the harness error on every session start. Command-type hooks are fine
there. Prompt-type hooks remain valid for PostCompact and Stop.
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS_JSON = os.path.join(REPO_ROOT, "hooks", "hooks.json")

# Hook types the harness accepts, per event. Keep in sync with hooks/README.md.
# SessionStart runs before any conversation context exists, so only command
# hooks are legal there.
ALLOWED_TYPES = {
    "SessionStart": {"command"},
    "PostCompact": {"command", "prompt"},
    "PostToolUse": {"command", "prompt"},
    "Stop": {"command", "prompt"},
    "UserPromptSubmit": {"command", "prompt"},
    "PreToolUse": {"command", "prompt"},
    "SubagentStop": {"command", "prompt"},
    "Notification": {"command", "prompt"},
    "PreCompact": {"command", "prompt"},
    "SessionEnd": {"command"},
}

passed = 0
failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {name}")


def iter_hooks(event_blocks):
    """Yield every leaf hook dict for an event's list of matcher-blocks."""
    for block in event_blocks:
        for hook in block.get("hooks", []):
            yield hook


def main():
    check("hooks.json exists", os.path.isfile(HOOKS_JSON))
    with open(HOOKS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    events = data.get("hooks", {})
    check("hooks.json has a 'hooks' object", isinstance(events, dict) and bool(events))

    # Every hook under every event uses a type allowed for that event.
    for event, blocks in events.items():
        allowed = ALLOWED_TYPES.get(event)
        check(f"{event} is a known event", allowed is not None)
        if allowed is None:
            continue
        for hook in iter_hooks(blocks):
            htype = hook.get("type")
            check(
                f"{event} hook type {htype!r} is allowed (expected one of {sorted(allowed)})",
                htype in allowed,
            )

    # Targeted regression assertions for the reported bug.
    session_start = events.get("SessionStart", [])
    check("SessionStart is present", bool(session_start))
    ss_types = [h.get("type") for h in iter_hooks(session_start)]
    check(
        "SessionStart contains NO prompt-type hook (issue: startup hook error)",
        "prompt" not in ss_types,
    )
    check(
        "SessionStart still restores hot cache via a command hook",
        "command" in ss_types,
    )

    # Guard against over-deletion: prompt hooks are legitimate elsewhere and
    # should be left intact. PostCompact re-loads the hot cache after compaction.
    post_compact = events.get("PostCompact", [])
    pc_types = [h.get("type") for h in iter_hooks(post_compact)]
    check("PostCompact retains its prompt-type hook", "prompt" in pc_types)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
