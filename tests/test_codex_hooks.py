#!/usr/bin/env python3
"""Exercise the commands Codex receives with its JSON input on stdin."""

import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def copy_hook_config(plugin):
    shutil.copytree(ROOT / "hooks", plugin / "hooks")
    manifest = ROOT / ".codex-plugin"
    if manifest.is_dir():
        shutil.copytree(manifest, plugin / manifest.name)


def run_hook(root, vault, event, **settings):
    manifest = root / ".codex-plugin/plugin.json"
    hook_file = "hooks/hooks.json"
    if manifest.is_file():
        hook_file = json.loads(manifest.read_text(encoding="utf-8"))["hooks"]
    hooks = json.loads((root / hook_file).read_text(encoding="utf-8"))["hooks"]
    handler = hooks[event][0]["hooks"][0]
    command = handler["command"]
    if os.name == "nt":
        command = handler.get("commandWindows", command) + "\nexit $LASTEXITCODE"
        encoded = base64.b64encode(command.encode("utf-16-le")).decode("ascii")
        argv = ["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded]
    else:
        argv = ["/bin/sh", "-c", command]
    env = {
        k: v for k, v in os.environ.items()
        if not k.startswith("CLAUDE_OBSIDIAN_") and k != "CLAUDE_PROJECT_DIR"
    }
    env.update(settings, PLUGIN_ROOT=str(root))
    return subprocess.run(
        argv, cwd=vault, env=env, input=json.dumps({
            "cwd": str(vault), "hook_event_name": event, "transcript_path": None,
            "session_id": "fixture", "source": "startup", "stop_hook_active": False,
        }), capture_output=True, encoding="utf-8", timeout=15,
    )


class CodexHooksTests(unittest.TestCase):
    def test_hook_commands_isolate_python_imports(self):
        """A repository working directory must stay off the Python import path."""
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            plugin = vault / "plugin with spaces"
            entry = plugin / "scripts/claude-obsidian.py"
            entry.parent.mkdir(parents=True)
            copy_hook_config(plugin)
            entry.write_text(
                "import sys\n"
                "from pathlib import Path\n"
                "assert sys.flags.isolated\n"
                "assert all(Path(item).resolve() != Path.cwd().resolve() for item in sys.path)\n"
                "print('isolated')\n",
                encoding="utf-8",
            )
            for event in ("SessionStart", "Stop"):
                run = run_hook(plugin, vault, event)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stdout.strip(), "isolated")

    def test_lifecycle_commands_resolve_a_plugin_path_with_spaces(self):
        """A dropped script argument must not make Python execute the event JSON."""
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            plugin = base / "plugin with spaces"
            (plugin / "scripts").mkdir(parents=True)
            shutil.copy(ROOT / "scripts/claude-obsidian.py", plugin / "scripts")
            shutil.copytree(ROOT / "claude_obsidian", plugin / "claude_obsidian")
            copy_hook_config(plugin)
            vault = base / "vault"
            for folder in (".obsidian", "wiki", ".raw", ".vault-meta/transactions/example"):
                (vault / folder).mkdir(parents=True)
            (vault / "wiki/hot.md").write_text("HOOK_FIXTURE_Å\n", encoding="utf-8")
            journal = vault / ".vault-meta/transactions/example/journal.json"
            journal.write_text('{"state":"applying"}', encoding="utf-8")
            start = run_hook(plugin, vault, "SessionStart")
            self.assertEqual(start.returncode, 0, start.stderr)
            self.assertEqual(start.stdout, "")
            opted_in = run_hook(plugin, vault, "SessionStart", CLAUDE_OBSIDIAN_SESSION_CONTEXT="1")
            self.assertEqual(opted_in.returncode, 0, opted_in.stderr)
            self.assertIn("HOOK_FIXTURE_Å", opted_in.stdout)
            stop = run_hook(plugin, vault, "Stop")
            self.assertEqual(stop.returncode, 0, stop.stderr)
            message = json.loads(stop.stdout)["systemMessage"]
            self.assertIn("need recovery (applying=1)", message)
            self.assertNotIn("example", message)
            journal.unlink()
            clean = run_hook(plugin, vault, "Stop")
            self.assertEqual(clean.returncode, 0, clean.stderr)
            self.assertEqual(clean.stdout, "")


if __name__ == "__main__":
    unittest.main()
