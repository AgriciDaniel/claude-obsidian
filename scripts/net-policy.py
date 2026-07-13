#!/usr/bin/env python3
"""net-policy.py — the network policy gate for v2.0 "Live Core".

v2.0 gives the vault always-on internet. That is a capability AND a liability,
and the two halves are not symmetric:

  INBOUND  (fetch a public page, run a search) — reading the world.
           Low risk. Always-on by default. This is the capability.

  EGRESS   (send vault content to a third party) — writing to the world.
           This is how private notes leak. Gated by consent, always.

The v1.7.0 audit's BLOCKER B1 was a data-egress consent gap. Turning on the
network without re-deriving that boundary would reopen it. So the boundary is
re-derived here, in one place, as code, and every skill that touches the network
asks this module first.

Two guards that matter for an always-on fetcher:

  SSRF     An agent that will fetch any URL handed to it will happily fetch
           http://169.254.169.254/ (cloud metadata) or http://127.0.0.1:8080/
           (your local admin panel). Private, loopback, link-local and reserved
           address space is DENIED inbound by default, in every encoding a real
           fetch would resolve: dotted-quad, decimal, hex, octal and short forms
           are all canonicalized before the check (see _as_ip).

  SECRETS  Egress payloads are scanned against deny globs (.env, secrets/, keys)
           before they can leave, independent of consent.

Honest limitation: hostname checks here do NOT resolve DNS. A hostname that
resolves to a private IP (DNS rebinding) is not caught at this layer. Blocking
that requires resolving at connect time, inside the fetcher, which is where it
belongs. This module gates POLICY, and it says so rather than implying a
guarantee it does not provide. See `docs/live-core-guide.md` §Threat model.

CLI:
  net-policy.py get                          # print current mode
  net-policy.py config                       # print full policy JSON
  net-policy.py set-mode MODE                # live | ask | offline
  net-policy.py check-fetch URL              # inbound verdict
  net-policy.py check-egress URL [--payload PATH ...]   # outbound verdict
  net-policy.py grant HOST                   # add HOST to the egress allowlist
  net-policy.py revoke HOST                  # remove HOST from the egress allowlist

Verdicts are printed as JSON to stdout: {"verdict": "allow|ask|deny", "reason": "..."}

Exit codes:
  0 — allow
  1 — deny
  2 — usage error
  3 — ask (consent required; caller must prompt the human)
  4 — invalid mode
"""

import argparse
import fnmatch
import ipaddress
import json
import os
import socket
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

VAULT_ROOT = Path(__file__).resolve().parent.parent
META_DIR = VAULT_ROOT / ".vault-meta"
NET_PATH = META_DIR / "net.json"

VALID_MODES = ("live", "ask", "offline")

# Hostnames that are never fetched, regardless of mode. Loopback and cloud
# metadata endpoints. Literal IPs are handled separately by _ip_verdict().
DEFAULT_DENY_HOSTS = [
    "localhost",
    "metadata.google.internal",
    "metadata.goog",
]

# Payload paths that may never leave the machine, regardless of consent.
# Consent covers "may I send the vault to X". It does not cover "may I send
# your AWS keys to X", because nobody means that when they say yes.
DEFAULT_SECRET_GLOBS = [
    "**/.env",
    "**/.env.*",
    "**/secrets/**",
    "**/*.pem",
    "**/*.key",
    "**/id_rsa*",
    "**/.aws/**",
    "**/.ssh/**",
    "**/credentials*",
]

DEFAULT_POLICY = {
    "schema_version": 1,
    "mode": "live",
    "configured_at": None,
    "inbound": {
        "always_on": True,
        "allow_hosts": [],  # empty = allow all except deny_hosts + private IPs
        "deny_hosts": list(DEFAULT_DENY_HOSTS),
        "allow_private_addresses": False,
    },
    "egress": {
        # explicit — ask the human, unless the host was `grant`ed earlier (default)
        # never    — no vault content ever leaves; egress always denied
        # ("ask once then remember" is `explicit` + `grant`: a grant persists in
        #  allow_hosts, which is stronger than a session and needs no session state.)
        "consent": "explicit",
        "allow_hosts": [],
        "deny_payload_globs": list(DEFAULT_SECRET_GLOBS),
    },
}


# ── policy load / save ───────────────────────────────────────────────────────

def load_policy() -> dict:
    """Load .vault-meta/net.json, or return the default policy if absent.

    Absent config is not an error. A fresh vault is 'live' inbound and
    'explicit' egress, which is the safe pairing: read freely, send nothing
    without being asked.
    """
    if not NET_PATH.exists():
        return json.loads(json.dumps(DEFAULT_POLICY))
    try:
        with NET_PATH.open() as fh:
            loaded = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        # A corrupt policy file must FAIL CLOSED, not fall back to permissive
        # defaults. "Could not read the policy, so I allowed it" is exactly the
        # class of bug this module exists to prevent.
        print(
            json.dumps({
                "verdict": "deny",
                "reason": f"policy file unreadable ({exc.__class__.__name__}); failing closed",
            }),
            file=sys.stderr,
        )
        sys.exit(1)

    # Merge over defaults so a policy written by an older schema still has every
    # key the current code reads.
    policy = json.loads(json.dumps(DEFAULT_POLICY))
    for section in ("inbound", "egress"):
        if isinstance(loaded.get(section), dict):
            policy[section].update(loaded[section])
    for key in ("schema_version", "mode", "configured_at"):
        if key in loaded:
            policy[key] = loaded[key]
    return policy


def save_policy(policy: dict) -> None:
    """Atomically write the policy. Staged to a tempfile, then renamed."""
    META_DIR.mkdir(parents=True, exist_ok=True)
    policy["configured_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fd, tmp = tempfile.mkstemp(dir=str(META_DIR), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(policy, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, NET_PATH)
    except BaseException:
        # Never leave a half-written policy behind; a truncated net.json would
        # fail closed on next read and lock the user out of the network.
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ── verdicts ─────────────────────────────────────────────────────────────────

def _verdict(kind: str, reason: str) -> dict:
    return {"verdict": kind, "reason": reason}


def _as_ip(host: str):
    """Return an ipaddress object if `host` is a literal IP in ANY form a real
    fetch would resolve, else None.

    `ipaddress.ip_address` only accepts canonical dotted-quad and IPv6. The C
    resolver every HTTP client actually calls is far more lenient: 2130706433,
    0x7f.0.0.1, 0177.0.0.1 and 127.1 all reach 127.0.0.1. A guard that checks
    only the canonical form is not a guard, because the attacker simply writes
    the other form. So the host is canonicalized through the same lenient parser
    (inet_aton) the OS uses, and the verdict is taken on the result.
    """
    h = host.strip().rstrip(".")  # a trailing dot is a valid FQDN root; libc ignores it
    try:
        return ipaddress.ip_address(h)
    except ValueError:
        pass
    # inet_aton mirrors libc: decimal, hex, octal, and short (a / a.b / a.b.c) forms.
    # It rejects real hostnames ("example.com" raises), so a success here means the
    # string genuinely denotes an IPv4 address, just not in canonical notation.
    try:
        return ipaddress.IPv4Address(socket.inet_aton(h))
    except (OSError, UnicodeError, ValueError):
        return None


def _ip_verdict(host: str, allow_private: bool):
    """If `host` is a literal IP, return a verdict. Otherwise None.

    This is the SSRF guard. An always-on fetcher pointed at 169.254.169.254
    hands over cloud credentials; pointed at 127.0.0.1 it reaches every admin
    panel bound to loopback. Both are denied unless explicitly unlocked.
    """
    ip = _as_ip(host)
    if ip is None:
        return None  # not a literal IP; hostname rules apply
    if allow_private:
        return None
    if ip.is_loopback:
        return _verdict("deny", f"{host} is a loopback address (SSRF guard)")
    if ip.is_link_local:
        return _verdict("deny", f"{host} is link-local; this is the cloud metadata range (SSRF guard)")
    if ip.is_private:
        return _verdict("deny", f"{host} is a private address (SSRF guard)")
    if ip.is_reserved or ip.is_multicast:
        return _verdict("deny", f"{host} is reserved or multicast (SSRF guard)")
    return None


def _host_of(url: str):
    parsed = urlparse(url if "://" in url else f"https://{url}")
    if parsed.scheme not in ("http", "https"):
        return None, _verdict("deny", f"scheme {parsed.scheme!r} is not http(s)")
    if not parsed.hostname:
        return None, _verdict("deny", f"cannot parse a host out of {url!r}")
    return parsed.hostname.lower(), None


def _host_matches(host: str, patterns) -> bool:
    """Match a host against a pattern list. A bare domain matches its subdomains.

    'example.com' matches 'example.com' and 'api.example.com', but NOT
    'notexample.com' — the boundary is a dot, not a substring. Getting this
    wrong turns an allowlist into a wildcard.
    """
    for pat in patterns:
        pat = pat.lower().lstrip(".")
        if host == pat or host.endswith("." + pat):
            return True
        if "*" in pat and fnmatch.fnmatch(host, pat):
            return True
    return False


def check_fetch(url: str, policy: dict) -> dict:
    """Inbound: may we READ this URL?"""
    mode = policy.get("mode", "live")
    if mode == "offline":
        return _verdict("deny", "vault is in offline mode")

    host, bad = _host_of(url)
    if bad:
        return bad

    inbound = policy["inbound"]
    if _host_matches(host, inbound.get("deny_hosts", [])):
        return _verdict("deny", f"{host} is on the inbound denylist")

    ip_v = _ip_verdict(host, inbound.get("allow_private_addresses", False))
    if ip_v:
        return ip_v

    allow = inbound.get("allow_hosts", [])
    if allow and not _host_matches(host, allow):
        return _verdict("deny", f"{host} is not on the inbound allowlist")

    if mode == "ask":
        return _verdict("ask", f"mode is 'ask'; confirm before fetching {host}")

    return _verdict("allow", f"inbound fetch of {host} permitted (mode=live)")


def _matches_secret_glob(payload: str, glob: str) -> bool:
    """Does `payload` match a secret-deny glob?

    fnmatch has no notion of a path separator: `*` and `**` both happily match
    across `/`. So `fnmatch(x, "**")` is True for EVERY x, and any naive basename
    comparison against a directory glob like `**/secrets/**` (whose basename is
    literally `**`) denies the entire vault. The globs are interpreted here
    explicitly instead:

      **/NAME     NAME at any depth, including depth zero (`.env` matches).
      **/DIR/**   anything underneath a path segment named DIR.

    Matching is case-INSENSITIVE, deliberately. On macOS (APFS) and Windows the
    filesystem folds case, so `.ENV` and `.env` are the same file, and a
    case-sensitive match would let `.ENV` egress a secret the policy swears can
    never leave. `fnmatch.fnmatch` folds case via os.path.normcase, which is a
    no-op on POSIX, so both sides are lowercased here and matched with
    fnmatchcase, which is deterministic across platforms. This only ever denies
    MORE, never less, so it cannot introduce a leak.
    """
    p = payload.replace("\\", "/").lower()
    g = glob.replace("\\", "/").lower()

    if fnmatch.fnmatchcase(p, g):
        return True

    if not g.startswith("**/"):
        return False
    tail = g[3:]

    if tail.endswith("/**"):
        dir_pat = tail[:-3]
        segments = p.split("/")[:-1]  # every parent segment; the file itself is not a dir
        return any(fnmatch.fnmatchcase(seg, dir_pat) for seg in segments)

    if "/" in tail:
        return False

    # A bare-name glob. Match the basename, the whole path (so a depth-zero
    # payload like ".env" or "id_rsa" is caught), AND any path segment (so a file
    # *inside* a directory named .env or credentials/ is caught too, not just a
    # file so named). Matching more path shapes here can only deny more secrets.
    if fnmatch.fnmatchcase(p.rsplit("/", 1)[-1], tail) or fnmatch.fnmatchcase(p, tail):
        return True
    return any(fnmatch.fnmatchcase(seg, tail) for seg in p.split("/"))


def check_egress(url: str, policy: dict, payloads=None) -> dict:
    """Outbound: may we SEND vault content to this URL?

    Ordering matters. Secrets are checked BEFORE consent, because consent to
    send the vault is not consent to send your SSH key.
    """
    payloads = payloads or []
    mode = policy.get("mode", "live")
    if mode == "offline":
        return _verdict("deny", "vault is in offline mode")

    host, bad = _host_of(url)
    if bad:
        return bad

    egress = policy["egress"]

    # 1. Secret payloads: denied unconditionally, ahead of any consent check.
    for payload in payloads:
        for glob in egress.get("deny_payload_globs", []):
            if _matches_secret_glob(payload, glob):
                return _verdict(
                    "deny",
                    f"payload {payload!r} matches secret pattern {glob!r}; never egressed",
                )

    # 2. Consent.
    consent = egress.get("consent", "explicit")
    if consent == "never":
        return _verdict("deny", "egress consent is set to 'never'")

    if _host_matches(host, egress.get("allow_hosts", [])):
        return _verdict("allow", f"{host} is on the egress allowlist (granted previously)")

    return _verdict(
        "ask",
        f"sending vault content to {host} requires explicit consent. "
        f"Grant with: scripts/net-policy.py grant {host}",
    )


# ── CLI ──────────────────────────────────────────────────────────────────────

EXIT = {"allow": 0, "deny": 1, "ask": 3}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="net-policy.py", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("get", help="print current mode")
    sub.add_parser("config", help="print full policy JSON")

    p_mode = sub.add_parser("set-mode", help="live | ask | offline")
    p_mode.add_argument("mode")

    p_fetch = sub.add_parser("check-fetch", help="inbound verdict for URL")
    p_fetch.add_argument("url")

    p_egress = sub.add_parser("check-egress", help="outbound verdict for URL")
    p_egress.add_argument("url")
    p_egress.add_argument("--payload", action="append", default=[],
                          help="path being sent; repeatable")

    p_grant = sub.add_parser("grant", help="add HOST to the egress allowlist")
    p_grant.add_argument("host")

    p_revoke = sub.add_parser("revoke", help="remove HOST from the egress allowlist")
    p_revoke.add_argument("host")

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 2

    policy = load_policy()

    if args.cmd == "get":
        print(policy.get("mode", "live"))
        return 0

    if args.cmd == "config":
        print(json.dumps(policy, indent=2))
        return 0

    if args.cmd == "set-mode":
        if args.mode not in VALID_MODES:
            print(f"ERR: invalid mode {args.mode!r}; want one of {', '.join(VALID_MODES)}",
                  file=sys.stderr)
            return 4
        policy["mode"] = args.mode
        save_policy(policy)
        print(f"mode = {args.mode}")
        return 0

    if args.cmd == "grant":
        host = args.host.lower().lstrip(".")
        if host not in policy["egress"]["allow_hosts"]:
            policy["egress"]["allow_hosts"].append(host)
            save_policy(policy)
        print(f"egress granted: {host}")
        return 0

    if args.cmd == "revoke":
        host = args.host.lower().lstrip(".")
        policy["egress"]["allow_hosts"] = [
            h for h in policy["egress"]["allow_hosts"] if h != host
        ]
        save_policy(policy)
        print(f"egress revoked: {host}")
        return 0

    if args.cmd == "check-fetch":
        v = check_fetch(args.url, policy)
    elif args.cmd == "check-egress":
        v = check_egress(args.url, policy, args.payload)
    else:
        parser.print_help()
        return 2

    print(json.dumps(v))
    return EXIT[v["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
