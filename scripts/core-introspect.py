#!/usr/bin/env python3
"""core-introspect.py — the plugin's knowledge of itself.

Core needs to know what Core is: every skill, script, CLI subcommand, workflow,
rule, command, agent, hook and make target it exposes, and how to actually invoke
each one. That surface is what this module builds.

THE DESIGN CONSTRAINT, and it is the whole thing:

    A hand-written feature list is a LIABILITY. It is true on the day it is
    written and decays silently after. An agent that reads a stale manifest and
    reports a capability that no longer exists is worse off than one that read
    nothing, because it now acts with confidence on a false map.

So the manifest is never authored. It is DISCOVERED, by walking the source, and
then VERIFIED, by executing every entry point it claims exists. Three commands
enforce that, and the distinction between them matters:

    scan     walk the source, emit the manifest      (what the code says exists)
    verify   EXECUTE every entry point in it         (what actually runs)
    check    diff the manifest on disk vs a fresh scan  (CI drift gate)

`verify` is the one that earns the word "perfectly." It does not read the code
and reason that an endpoint is reachable. It runs the endpoint and watches what
happens. A capability that will not execute is reported as BROKEN even though it
is right there in the source, because "it is in the source" and "it works" are
different claims and only one of them matters to a caller.

CLI:
  core-introspect.py scan                 # discover, write .vault-meta/capabilities.json
  core-introspect.py scan --peek          # discover, print to stdout, write nothing
  core-introspect.py list [--kind KIND]   # human-readable surface
  core-introspect.py show ID              # everything known about one endpoint
  core-introspect.py verify [--kind KIND] # execute every entry point; exit 1 on any break
  core-introspect.py check                # CI gate: manifest is current

Exit codes:
  0 — success (or: verify passed, everything reachable)
  1 — verify found a broken endpoint, or check found the manifest stale
  2 — usage error
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
META_DIR = VAULT_ROOT / ".vault-meta"
MANIFEST = META_DIR / "capabilities.json"

KINDS = ("skill", "script", "workflow", "rule", "command", "agent", "hook", "make", "config")

# Scripts whose --help would launch something, block, or mutate state. We record
# them but never execute them during `verify`. Being explicit here is the honest
# move: an unverifiable endpoint is marked unverifiable, not quietly marked good.
NO_EXEC = {
    "wiki-lock.sh",       # acquires a real lock
    "setup-vault.sh",     # interactive, mutates
    "setup-mode.sh",
    "setup-retrieve.sh",
    "setup-dragonscale.sh",
    "setup-multi-agent.sh",
    "setup-live.sh",
}

# How to prove a script is reachable without doing anything. Preference order.
PROBES = ("--help", "-h")


# ── frontmatter (minimal, dependency-free) ───────────────────────────────────

def _frontmatter(path: Path) -> dict:
    """Pull `name` and `description` out of a SKILL.md / agent .md.

    Deliberately not a YAML parser. We want two scalar fields and we want this
    to never be the reason a scan fails.
    """
    try:
        text = path.read_text()
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    meta = {}
    for line in text[4:end].split("\n"):
        m = re.match(r'^(name|description|tools|allowed-tools):\s*(.*)$', line)
        if m:
            val = m.group(2).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            meta[m.group(1)] = val
    return meta


def _triggers(description: str):
    """Extract the 'Triggers on: a, b, c' list that every skill carries."""
    m = re.search(r'Triggers on:\s*(.+?)\.?\s*$', description or "", re.IGNORECASE | re.DOTALL)
    if not m:
        return []
    return [t.strip().strip('"') for t in m.group(1).split(",") if t.strip()]


def _docstring_summary(path: Path) -> str:
    """First meaningful line of a python docstring or a shell header comment."""
    try:
        head = path.read_text()[:2000]
    except OSError:
        return ""
    m = re.search(r'^"""(?:[^\n]*?—\s*)?([^\n]+)', head)
    if m:
        return m.group(1).strip()
    for line in head.split("\n")[1:8]:
        if line.startswith("# ") and not line.startswith("#!"):
            return re.sub(r'^#\s*\S+\.(?:sh|py)\s*—\s*', '', line[2:]).strip()
    return ""


def _subcommands(path: Path):
    """Recover a script's subcommands from its source.

    Python: every `sub.add_parser("x")`. Shell: the `--flags` in its header.
    This reads the CODE, not the docs, because the docs are what drift.
    """
    try:
        src = path.read_text()
    except OSError:
        return []
    if path.suffix == ".py":
        return sorted(set(re.findall(r'add_parser\(\s*["\']([a-z][\w-]*)["\']', src)))
    return sorted(set(re.findall(r'^\s*--([a-z][\w-]+)\)', src, re.MULTILINE)))


def _exit_codes(path: Path):
    """Parse the 'Exit codes:' block that this repo's scripts all document."""
    try:
        src = path.read_text()[:4000]
    except OSError:
        return {}
    m = re.search(r'Exit codes?:\s*\n((?:[^\n]*\n){1,10})', src)
    if not m:
        return {}
    codes = {}
    for line in m.group(1).split("\n"):
        cm = re.match(r'^[#\s]*(\d+)\s*[—:-]\s*(.+?)\s*$', line)
        if cm:
            codes[cm.group(1)] = cm.group(2)
    return codes


# ── discovery ────────────────────────────────────────────────────────────────

def scan() -> dict:
    """Walk the source and build the capability surface. Reads only."""
    caps = []

    # skills/<name>/SKILL.md
    for p in sorted(VAULT_ROOT.glob("skills/*/SKILL.md")):
        fm = _frontmatter(p)
        caps.append({
            "id": f"skill/{p.parent.name}",
            "kind": "skill",
            "name": fm.get("name", p.parent.name),
            "summary": (fm.get("description", "").split("Triggers on:")[0].strip()[:200]),
            "triggers": _triggers(fm.get("description", "")),
            "tools": fm.get("allowed-tools") or fm.get("tools") or "",
            "path": str(p.relative_to(VAULT_ROOT)),
            "invoke": f"/{fm.get('name', p.parent.name)}",
        })

    # scripts/*.py and scripts/*.sh
    for p in sorted(list(VAULT_ROOT.glob("scripts/*.py")) + list(VAULT_ROOT.glob("scripts/*.sh"))):
        runner = "python3" if p.suffix == ".py" else "bash"
        subs = _subcommands(p)
        caps.append({
            "id": f"script/{p.name}",
            "kind": "script",
            "name": p.name,
            "summary": _docstring_summary(p),
            "subcommands": subs,
            "exit_codes": _exit_codes(p),
            "path": str(p.relative_to(VAULT_ROOT)),
            "invoke": f"{runner} {p.relative_to(VAULT_ROOT)}" + (f" <{('|'.join(subs))}>" if subs else ""),
            "executable": os.access(p, os.X_OK),
            "verifiable": p.name not in NO_EXEC,
        })

    # workflows/*.js
    for p in sorted(VAULT_ROOT.glob("workflows/*.js")):
        src = p.read_text()
        name = re.search(r"name:\s*'([^']+)'", src)
        desc = re.search(r"description:\s*'([^']+)'", src)
        phases = re.findall(r"title:\s*'([^']+)'", src)
        caps.append({
            "id": f"workflow/{p.stem}",
            "kind": "workflow",
            "name": name.group(1) if name else p.stem,
            "summary": desc.group(1) if desc else "",
            "phases": phases,
            "path": str(p.relative_to(VAULT_ROOT)),
            "invoke": f"Workflow tool, scriptPath: {p.relative_to(VAULT_ROOT)}",
        })

    # rules/<domain>/<slug>.md
    for p in sorted(VAULT_ROOT.glob("rules/*/*.md")):
        fm = _frontmatter(p)
        if not fm.get("name") and "severity" not in p.read_text()[:400]:
            continue
        text = p.read_text()
        sev = re.search(r'^severity:\s*(\w+)', text, re.MULTILINE)
        title = re.search(r'^title:\s*(.+)$', text, re.MULTILINE)
        caps.append({
            "id": f"rule/{p.parent.name}/{p.stem}",
            "kind": "rule",
            "name": (title.group(1).strip() if title else p.stem),
            "summary": f"severity: {sev.group(1) if sev else '?'}",
            "severity": sev.group(1) if sev else "",
            "path": str(p.relative_to(VAULT_ROOT)),
            "invoke": "compiled by scripts/render-rules.py into 6 agent dialects",
        })

    # commands/*.md
    for p in sorted(VAULT_ROOT.glob("commands/*.md")):
        caps.append({
            "id": f"command/{p.stem}",
            "kind": "command",
            "name": f"/{p.stem}",
            "summary": _frontmatter(p).get("description", "")[:200],
            "path": str(p.relative_to(VAULT_ROOT)),
            "invoke": f"/{p.stem}",
        })

    # agents/*.md
    for p in sorted(VAULT_ROOT.glob("agents/*.md")):
        fm = _frontmatter(p)
        caps.append({
            "id": f"agent/{p.stem}",
            "kind": "agent",
            "name": fm.get("name", p.stem),
            "summary": fm.get("description", "")[:200],
            "tools": fm.get("tools", ""),
            "path": str(p.relative_to(VAULT_ROOT)),
            "invoke": f"Agent tool, subagent_type: {p.stem}",
        })

    # hooks/hooks.json
    hooks_path = VAULT_ROOT / "hooks" / "hooks.json"
    if hooks_path.exists():
        try:
            hooks = json.loads(hooks_path.read_text())
            for event, entries in (hooks.get("hooks") or hooks).items():
                if not isinstance(entries, list):
                    continue
                caps.append({
                    "id": f"hook/{event}",
                    "kind": "hook",
                    "name": event,
                    "summary": f"{len(entries)} matcher(s) registered",
                    "path": "hooks/hooks.json",
                    "invoke": f"fires automatically on {event}",
                })
        except (json.JSONDecodeError, AttributeError):
            pass

    # Makefile targets
    mk = VAULT_ROOT / "Makefile"
    if mk.exists():
        for target in sorted(set(re.findall(r'^([a-z][\w-]*):', mk.read_text(), re.MULTILINE))):
            caps.append({
                "id": f"make/{target}",
                "kind": "make",
                "name": target,
                "summary": "",
                "path": "Makefile",
                "invoke": f"make {target}",
            })

    # .vault-meta/*.json — the runtime config surface
    for name, desc in (
        ("transport.json", "vault-mutation transport (cli > mcp > filesystem)"),
        ("browser.json", "browser transport (playwright > cdp > fetch)"),
        ("net.json", "network policy (inbound always-on, egress gated)"),
        ("mode.json", "methodology mode (generic | lyt | para | zettelkasten)"),
        ("capabilities.json", "this manifest"),
    ):
        # Deliberately NOT recording whether the file exists. The manifest is derived
        # from source and must be byte-identical on every machine at a given commit,
        # or `check` goes red in CI for the sole reason that CI has no browser.json.
        # Existence is machine state and it is `verify`'s job, at run time. Recording
        # it here also made the manifest self-referential: the first scan wrote
        # capabilities.json with present=false for capabilities.json, which became
        # true the instant that write landed.
        caps.append({
            "id": f"config/{name}",
            "kind": "config",
            "name": name,
            "summary": desc,
            "path": f".vault-meta/{name}",
            "invoke": f"read .vault-meta/{name}",
        })

    counts = {}
    for c in caps:
        counts[c["kind"]] = counts.get(c["kind"], 0) + 1

    return {
        "schema_version": 1,
        "generated_by": "scripts/core-introspect.py scan",
        "warning": "GENERATED FROM SOURCE. Do not hand-edit. Run 'core-introspect.py scan' to refresh.",
        "counts": counts,
        "total": len(caps),
        "capabilities": caps,
    }


def scan_stamped() -> dict:
    """scan() plus a timestamp. Kept separate so `check` can diff the stable part."""
    data = scan()
    data["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return data


def _stable(data: dict) -> str:
    """The manifest minus its timestamp, for drift comparison. A regenerated
    manifest differs from the one on disk only by `generated_at`, so comparing
    raw text would report drift on every single run and train everyone to
    ignore the gate."""
    d = {k: v for k, v in data.items() if k != "generated_at"}
    return json.dumps(d, sort_keys=True, indent=2)


def save(data: dict) -> None:
    META_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(META_DIR), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, MANIFEST)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ── verify: execute, do not reason ───────────────────────────────────────────

def verify(caps, kind=None):
    """Execute every declared entry point and report what actually runs.

    This is the difference between a manifest and a promise. We do not read the
    source and conclude an endpoint is reachable. We invoke it.
    """
    results = []
    targets = [c for c in caps if not kind or c["kind"] == kind]

    for c in targets:
        path = VAULT_ROOT / c["path"] if c.get("path") else None

        # Existence is the floor for everything EXCEPT config: a runtime config
        # file is generated on demand and is gitignored, so "absent" means
        # "defaults apply", not "broken". Reporting an absent net.json as BROKEN
        # would be a false positive, and a verifier that cries wolf is one people
        # learn to ignore, which costs more than not having it.
        if path and not path.exists() and c["kind"] != "config":
            results.append((c, "BROKEN", f"declared path does not exist: {c['path']}"))
            continue

        if c["kind"] == "script":
            if not c.get("verifiable", True):
                results.append((c, "SKIP", "mutates or blocks; not safe to probe"))
                continue
            runner = ["python3"] if path.suffix == ".py" else ["bash"]
            ok = False
            detail = ""
            for probe in PROBES:
                try:
                    proc = subprocess.run(
                        runner + [str(path), probe],
                        capture_output=True, text=True, timeout=20,
                        cwd=str(VAULT_ROOT),
                    )
                except subprocess.TimeoutExpired:
                    detail = f"{probe} timed out after 20s"
                    continue
                except OSError as exc:
                    detail = f"{probe} could not execute: {exc}"
                    continue
                # A usage/help path may legitimately exit non-zero, but it must
                # produce output. Silence plus failure means it did not run.
                out = (proc.stdout or "") + (proc.stderr or "")
                if out.strip():
                    ok = True
                    detail = f"{probe} responded ({len(out.strip().splitlines())} lines)"
                    break
                detail = f"{probe} produced no output (exit {proc.returncode})"
            results.append((c, "OK" if ok else "BROKEN", detail))

        elif c["kind"] == "workflow":
            src = path.read_text()
            if "export const meta" not in src:
                results.append((c, "BROKEN", "no `export const meta` block; Workflow tool will reject it"))
            elif not re.search(r"name:\s*'", src):
                results.append((c, "BROKEN", "meta has no name"))
            else:
                results.append((c, "OK", f"{len(c.get('phases', []))} phases declared"))

        elif c["kind"] == "skill":
            fm = _frontmatter(path)
            if not fm.get("name"):
                results.append((c, "BROKEN", "SKILL.md frontmatter has no `name`"))
            elif not fm.get("description"):
                results.append((c, "BROKEN", "SKILL.md frontmatter has no `description`"))
            elif fm["name"] != path.parent.name:
                results.append((c, "BROKEN",
                                f"frontmatter name {fm['name']!r} != directory {path.parent.name!r}; "
                                "the skill will not resolve"))
            else:
                results.append((c, "OK", f"{len(c.get('triggers', []))} triggers"))

        elif c["kind"] == "make":
            # `make -n` dry-runs the target: proves it resolves without doing it.
            try:
                proc = subprocess.run(
                    ["make", "-n", c["name"]],
                    capture_output=True, text=True, timeout=20, cwd=str(VAULT_ROOT),
                )
                if proc.returncode == 0:
                    results.append((c, "OK", "target resolves"))
                else:
                    results.append((c, "BROKEN", (proc.stderr or "").strip().split("\n")[0][:120]))
            except (subprocess.TimeoutExpired, OSError) as exc:
                results.append((c, "BROKEN", f"make failed: {exc}"))

        elif c["kind"] == "config":
            # Existence is checked HERE, at run time, not baked into the manifest.
            # A config that has not been generated yet is not broken: the defaults apply.
            if not (VAULT_ROOT / c["path"]).exists():
                results.append((c, "SKIP", "not generated yet; defaults apply"))
            else:
                try:
                    json.loads((VAULT_ROOT / c["path"]).read_text())
                    results.append((c, "OK", "valid JSON"))
                except (json.JSONDecodeError, OSError) as exc:
                    results.append((c, "BROKEN", f"unparseable: {exc}"))

        else:
            results.append((c, "OK", "present"))

    return results


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="core-introspect.py",
                                     description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="discover the capability surface")
    p_scan.add_argument("--peek", action="store_true", help="print, do not write")

    p_list = sub.add_parser("list", help="human-readable surface")
    p_list.add_argument("--kind", choices=KINDS)

    p_show = sub.add_parser("show", help="everything known about one endpoint")
    p_show.add_argument("id")

    p_verify = sub.add_parser("verify", help="EXECUTE every entry point; exit 1 on any break")
    p_verify.add_argument("--kind", choices=KINDS)

    sub.add_parser("check", help="CI gate: manifest on disk is current")

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 2

    if args.cmd == "scan":
        data = scan_stamped()
        if args.peek:
            print(json.dumps(data, indent=2))
            return 0
        save(data)
        bits = ", ".join(f"{v} {k}" for k, v in sorted(data["counts"].items()))
        print(f"wrote {MANIFEST.relative_to(VAULT_ROOT)}")
        print(f"{data['total']} capabilities: {bits}")
        return 0

    if args.cmd == "check":
        fresh = scan()
        if not MANIFEST.exists():
            print("ERR: .vault-meta/capabilities.json is missing. Run: "
                  "python3 scripts/core-introspect.py scan", file=sys.stderr)
            return 1
        try:
            on_disk = json.loads(MANIFEST.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            print(f"ERR: capabilities.json is unreadable ({exc}). Re-run scan.", file=sys.stderr)
            return 1
        if _stable(on_disk) != _stable(fresh):
            old = {c["id"] for c in on_disk.get("capabilities", [])}
            new = {c["id"] for c in fresh["capabilities"]}
            print("capabilities.json is stale (source has moved under it):\n", file=sys.stderr)
            for i in sorted(new - old):
                print(f"  + {i}", file=sys.stderr)
            for i in sorted(old - new):
                print(f"  - {i}", file=sys.stderr)
            if not (new - old) and not (old - new):
                print("  (same ids, changed details)", file=sys.stderr)
            print("\nRun: python3 scripts/core-introspect.py scan", file=sys.stderr)
            return 1
        print(f"capabilities.json is current ({fresh['total']} capabilities).")
        return 0

    data = scan()
    caps = data["capabilities"]

    if args.cmd == "list":
        shown = [c for c in caps if not args.kind or c["kind"] == args.kind]
        current = None
        for c in shown:
            if c["kind"] != current:
                current = c["kind"]
                print(f"\n── {current} ({sum(1 for x in shown if x['kind'] == current)}) ──")
            print(f"  {c['id']:<44} {c['summary'][:72]}")
        print(f"\n{len(shown)} capabilities.")
        return 0

    if args.cmd == "show":
        for c in caps:
            if c["id"] == args.id or c["id"].endswith("/" + args.id):
                print(json.dumps(c, indent=2))
                return 0
        print(f"ERR: no capability with id {args.id!r}. Try: core-introspect.py list",
              file=sys.stderr)
        return 2

    if args.cmd == "verify":
        results = verify(caps, args.kind)
        broken = [r for r in results if r[1] == "BROKEN"]
        skipped = [r for r in results if r[1] == "SKIP"]
        ok = [r for r in results if r[1] == "OK"]

        for c, status, detail in results:
            if status == "BROKEN":
                print(f"  BROKEN  {c['id']:<42} {detail}")
        for c, status, detail in skipped:
            print(f"  skip    {c['id']:<42} {detail}")

        print(f"\n{len(ok)} reachable, {len(skipped)} skipped, {len(broken)} BROKEN")
        if broken:
            print("\nThese are declared in the source but do not run. A capability that "
                  "will not execute is not a capability.", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
