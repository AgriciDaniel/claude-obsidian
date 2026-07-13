#!/usr/bin/env python3
"""test_net_policy.py — hermetic tests for scripts/net-policy.py.

Covers the two asymmetric halves of the v2.0 "Live Core" boundary:

  INBOUND   default-live, plus the SSRF guard (loopback, link-local / cloud
            metadata, private, reserved, IPv6 loopback), scheme restriction,
            and the allow_private_addresses escape hatch.
  EGRESS    consent states, host-suffix allowlisting, and the secret-payload
            deny that must run BEFORE consent is even consulted.

Plus the two fail-closed properties: a corrupt policy file denies rather than
falling back to permissive defaults, and the CLI's exit codes carry the verdict.

Hermetic: the module's NET_PATH / META_DIR globals are monkeypatched at a
tempdir, and the CLI is exercised through a throwaway copy of the script whose
VAULT_ROOT resolves inside that tempdir. The real .vault-meta/ is never touched.
No network, no third-party deps, stdlib only.

Usage:
  python3 tests/test_net_policy.py
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "net-policy.py"

spec = importlib.util.spec_from_file_location("net_policy", HELPER)
np = importlib.util.module_from_spec(spec)
spec.loader.exec_module(np)


class Fail(SystemExit):
    pass


def assert_eq(label, expected, actual):
    if expected != actual:
        raise Fail(f"FAIL {label}: expected {expected!r}, got {actual!r}")
    print(f"OK   {label}")


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def fresh_policy(**overrides):
    """A deep copy of the shipped default, with optional section overrides."""
    policy = json.loads(json.dumps(np.DEFAULT_POLICY))
    for section, values in overrides.items():
        if isinstance(values, dict) and isinstance(policy.get(section), dict):
            policy[section].update(values)
        else:
            policy[section] = values
    return policy


# ─── Defaults when no config file exists ─────────────────────────────────────
def test_absent_config_is_live_inbound_explicit_egress():
    """A fresh vault reads freely and sends nothing without being asked."""
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.object(np, "NET_PATH", Path(tmp) / "nonexistent.json"):
            policy = np.load_policy()
            assert_eq("absent config → mode=live", "live", policy["mode"])
            assert_eq("absent config → egress consent=explicit",
                      "explicit", policy["egress"]["consent"])
            assert_eq("absent config → inbound always_on", True,
                      policy["inbound"]["always_on"])
            assert_eq("absent config → private addresses locked", False,
                      policy["inbound"]["allow_private_addresses"])


def test_load_does_not_mutate_the_default_policy():
    """load_policy() must hand back a copy; a caller mutating the returned dict
    must not poison DEFAULT_POLICY for the next load."""
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.object(np, "NET_PATH", Path(tmp) / "nonexistent.json"):
            first = np.load_policy()
            first["egress"]["allow_hosts"].append("evil.example")
            second = np.load_policy()
            assert_eq("DEFAULT_POLICY not poisoned by caller mutation",
                      [], second["egress"]["allow_hosts"])


def test_save_load_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        net_path = Path(tmp) / "net.json"
        with mock.patch.object(np, "NET_PATH", net_path), \
             mock.patch.object(np, "META_DIR", Path(tmp)):
            policy = np.load_policy()
            policy["mode"] = "ask"
            np.save_policy(policy)
            assert_true("net.json written", net_path.is_file())
            reloaded = np.load_policy()
            assert_eq("round-trip mode", "ask", reloaded["mode"])
            assert_true("save stamps configured_at",
                        bool(reloaded.get("configured_at")))


# ─── Corrupt policy fails CLOSED ─────────────────────────────────────────────
def test_corrupt_policy_fails_closed():
    """'I could not read the policy, so I allowed it' is the exact bug this
    module exists to prevent. A corrupt net.json must deny, not fall back."""
    with tempfile.TemporaryDirectory() as tmp:
        net_path = Path(tmp) / "net.json"
        net_path.write_text("{ this is not valid json", encoding="utf-8")
        with mock.patch.object(np, "NET_PATH", net_path):
            try:
                np.load_policy()
                raise Fail("expected SystemExit(1) on corrupt policy")
            except SystemExit as exc:
                assert_eq("corrupt policy → exit 1 (deny)", 1, exc.code)


def test_corrupt_policy_does_not_yield_permissive_defaults():
    """Belt and braces: assert the corrupt path never returns a live policy."""
    with tempfile.TemporaryDirectory() as tmp:
        net_path = Path(tmp) / "net.json"
        net_path.write_text("]]]not json[[[", encoding="utf-8")
        with mock.patch.object(np, "NET_PATH", net_path):
            returned = None
            try:
                returned = np.load_policy()
            except SystemExit:
                pass
            assert_eq("corrupt policy returns nothing usable", None, returned)


# ─── SSRF guard: every private range is denied inbound ───────────────────────
def test_ssrf_guard_denies_private_address_space():
    policy = fresh_policy()
    cases = [
        ("http://127.0.0.1/admin",            "loopback"),
        ("http://127.0.0.1:8080/",            "loopback with port"),
        ("http://169.254.169.254/latest/meta-data/", "cloud metadata (link-local)"),
        ("http://10.0.0.5/",                  "private 10/8"),
        ("http://192.168.1.1/",               "private 192.168/16"),
        ("http://172.16.0.1/",                "private 172.16/12"),
        ("http://240.0.0.1/",                 "reserved"),
        ("http://[::1]/",                     "IPv6 loopback"),
        ("http://[fe80::1]/",                 "IPv6 link-local"),
        ("http://[fd00::1]/",                 "IPv6 unique-local (private)"),
    ]
    for url, label in cases:
        v = np.check_fetch(url, policy)
        assert_eq(f"SSRF deny: {label}", "deny", v["verdict"])


def test_ssrf_guard_denies_encoded_ip_forms():
    """The canonical dotted-quad is only one spelling of an address. A real HTTP
    client resolves 2130706433, 0x7f.0.0.1, 0177.0.0.1 and 127.1 all to 127.0.0.1,
    so a guard that checks only the canonical form is bypassed by writing another.
    2852039166 is 169.254.169.254 (cloud metadata) in decimal, the one that hands
    out credentials. Every alternate encoding of a blocked address must also deny."""
    policy = fresh_policy()
    cases = [
        ("http://2130706433/",        "127.0.0.1 as decimal"),
        ("http://0x7f.0.0.1/",        "127.0.0.1 with a hex octet"),
        ("http://0177.0.0.1/",        "127.0.0.1 with an octal octet"),
        ("http://127.1/",             "127.0.0.1 short form"),
        ("http://0/",                 "0.0.0.0 as a bare integer"),
        ("http://127.0.0.1./",        "loopback with a trailing dot"),
        ("http://2852039166/",        "169.254.169.254 (metadata) as decimal"),
        ("http://0xA9FEA9FE/",        "169.254.169.254 (metadata) as hex"),
    ]
    for url, label in cases:
        v = np.check_fetch(url, policy)
        assert_eq(f"SSRF deny (encoded): {label}", "deny", v["verdict"])


def test_numeric_looking_public_hosts_are_not_over_blocked():
    """The encoded-IP guard must not swallow legitimate public hosts. 8.8.8.8 is a
    real public IP; 1e100.net is a hostname that merely looks numeric."""
    policy = fresh_policy()
    for url in ("https://8.8.8.8/", "https://1e100.net/"):
        v = np.check_fetch(url, policy)
        assert_eq(f"public host allowed: {url}", "allow", v["verdict"])


def test_ssrf_guard_denies_loopback_by_name():
    policy = fresh_policy()
    v = np.check_fetch("http://localhost:3000/", policy)
    assert_eq("localhost denied by name", "deny", v["verdict"])
    v = np.check_fetch("http://metadata.google.internal/", policy)
    assert_eq("metadata.google.internal denied by name", "deny", v["verdict"])


def test_public_host_allowed_in_live_mode():
    policy = fresh_policy()
    v = np.check_fetch("https://example.com/page", policy)
    assert_eq("public host allowed in live mode", "allow", v["verdict"])
    v = np.check_fetch("https://8.8.8.8/", policy)
    assert_eq("public literal IP allowed in live mode", "allow", v["verdict"])


def test_non_http_schemes_denied():
    policy = fresh_policy()
    for url in ("file:///etc/passwd", "ftp://example.com/x", "gopher://example.com/"):
        v = np.check_fetch(url, policy)
        assert_eq(f"scheme denied: {url}", "deny", v["verdict"])
        assert_true(f"reason names the scheme: {url}",
                    "scheme" in v["reason"], hint=v["reason"])


def test_allow_private_addresses_is_a_working_escape_hatch():
    """Someone running a local Ollama or a LAN wiki has to be able to opt in.
    The hatch must actually unlock, otherwise it is decoration."""
    policy = fresh_policy(inbound={"allow_private_addresses": True})
    for url in ("http://127.0.0.1:11434/api/tags", "http://192.168.1.1/", "http://[::1]/"):
        v = np.check_fetch(url, policy)
        assert_eq(f"escape hatch allows {url}", "allow", v["verdict"])


def test_escape_hatch_does_not_unlock_the_named_denylist():
    """allow_private_addresses relaxes the IP guard. It must not also relax the
    explicit deny_hosts list — those are two different decisions."""
    policy = fresh_policy(inbound={"allow_private_addresses": True})
    v = np.check_fetch("http://metadata.google.internal/", policy)
    assert_eq("named denylist survives the escape hatch", "deny", v["verdict"])


# ─── Modes ───────────────────────────────────────────────────────────────────
def test_offline_mode_denies_everything():
    policy = fresh_policy(mode="offline")
    v = np.check_fetch("https://example.com/", policy)
    assert_eq("offline denies inbound", "deny", v["verdict"])
    v = np.check_egress("https://example.com/", policy)
    assert_eq("offline denies egress", "deny", v["verdict"])
    # Even an allowlisted egress host stays denied while offline.
    policy = fresh_policy(mode="offline", egress={"allow_hosts": ["example.com"]})
    v = np.check_egress("https://example.com/", policy)
    assert_eq("offline denies even allowlisted egress", "deny", v["verdict"])


def test_ask_mode_returns_ask_for_inbound():
    policy = fresh_policy(mode="ask")
    v = np.check_fetch("https://example.com/", policy)
    assert_eq("ask mode → ask for inbound", "ask", v["verdict"])


def test_ask_mode_still_enforces_the_ssrf_guard():
    """'Ask' means ask the human about public pages, not 'ask before handing
    over the cloud metadata credentials'. The guard runs before the prompt."""
    policy = fresh_policy(mode="ask")
    v = np.check_fetch("http://169.254.169.254/", policy)
    assert_eq("ask mode still denies metadata IP", "deny", v["verdict"])


def test_inbound_allowlist_when_non_empty_excludes_everything_else():
    policy = fresh_policy(inbound={"allow_hosts": ["example.com"]})
    assert_eq("allowlisted host allowed", "allow",
              np.check_fetch("https://example.com/", policy)["verdict"])
    assert_eq("non-allowlisted host denied", "deny",
              np.check_fetch("https://other.com/", policy)["verdict"])


# ─── Egress consent ──────────────────────────────────────────────────────────
def test_egress_unknown_host_asks():
    policy = fresh_policy()
    v = np.check_egress("https://unknown.example/", policy)
    assert_eq("unknown egress host → ask", "ask", v["verdict"])


def test_egress_allowlisted_host_allows():
    policy = fresh_policy(egress={"allow_hosts": ["example.com"]})
    v = np.check_egress("https://example.com/upload", policy)
    assert_eq("allowlisted egress host → allow", "allow", v["verdict"])


def test_egress_consent_never_denies():
    policy = fresh_policy(egress={"consent": "never", "allow_hosts": ["example.com"]})
    v = np.check_egress("https://example.com/upload", policy)
    assert_eq("consent=never → deny even for allowlisted host", "deny", v["verdict"])


def test_egress_benign_payload_to_allowlisted_host_is_allowed():
    """The happy path has to actually work. Regression guard: the secret-glob
    matcher once matched EVERY payload (Path('**/secrets/**').name is '**', and
    fnmatch(anything, '**') is True), so this verdict was 'deny' for all files
    and the whole consent flow was unreachable."""
    policy = fresh_policy(egress={"allow_hosts": ["example.com"]})
    v = np.check_egress("https://example.com/upload", policy,
                        payloads=["wiki/hot.md", "wiki/concepts/Compounding Vault.md",
                                  "README.md", "notes/keynote.md"])
    assert_eq("benign payloads to allowlisted host → allow", "allow", v["verdict"])


# ─── Egress secrets: denied BEFORE consent is consulted ──────────────────────
SECRET_PAYLOADS = [
    ".env",
    ".env.production",
    "wiki/.env",
    "id_rsa",
    "id_rsa.pub",
    "~/.ssh/id_rsa",
    "foo.pem",
    "certs/server.pem",
    "server.key",
    ".aws/credentials",
    "home/victor/.aws/credentials",
    "secrets/tokens.md",
    "config/secrets/api.json",
    ".ssh/known_hosts",
    "credentials.json",
]


def test_egress_secret_payloads_denied():
    policy = fresh_policy()
    for payload in SECRET_PAYLOADS:
        v = np.check_egress("https://unknown.example/", policy, payloads=[payload])
        assert_eq(f"secret payload denied: {payload}", "deny", v["verdict"])


def test_egress_secrets_denied_even_when_host_is_allowlisted():
    """THE ordering property. Consent to send the vault is not consent to send
    an SSH key, so the secret scan must run BEFORE the consent check. If it ran
    after, an allowlisted host would short-circuit to 'allow' and exfiltrate."""
    policy = fresh_policy(egress={"allow_hosts": ["example.com"]})
    for payload in SECRET_PAYLOADS:
        v = np.check_egress("https://example.com/upload", policy, payloads=[payload])
        assert_eq(f"secret denied despite allowlist: {payload}", "deny", v["verdict"])
        assert_true(f"deny reason names the secret pattern: {payload}",
                    "secret pattern" in v["reason"], hint=v["reason"])


SECRET_PAYLOADS_MIXED_CASE = [
    ".ENV",
    ".Env",
    "wiki/.ENV",
    "id_RSA",
    "server.KEY",
    "cert.PEM",
    ".AWS/credentials",
    "config/SECRETS/api.json",
    ".SSH/id_ed25519",
    "CREDENTIALS.json",
]


def test_egress_secrets_denied_regardless_of_case():
    """On macOS (APFS) and Windows the filesystem folds case, so `.ENV` and `.env`
    are the same file. A case-sensitive secret filter lets `.ENV` egress a secret
    the policy swears can never leave. Every case-variant of a secret must deny,
    including when the host is allowlisted (secrets outrank consent)."""
    policy = fresh_policy(egress={"allow_hosts": ["example.com"]})
    for payload in SECRET_PAYLOADS_MIXED_CASE:
        v = np.check_egress("https://example.com/upload", policy, payloads=[payload])
        assert_eq(f"mixed-case secret denied: {payload}", "deny", v["verdict"])


SECRETS_INSIDE_SECRET_DIRS = [
    "foo/.env/token",              # a file INSIDE a directory named .env
    "app/.ENV/prod",              # same, case-folded
    "vault/credentials/aws.txt",   # inside a credentials/ directory
    "x/secrets/y/z.md",           # already covered by **/secrets/**, kept as a guard
]


def test_egress_secrets_inside_secret_named_directories_denied():
    """The default globs are file patterns (**/.env, **/credentials*). A secret is
    just as exposed sitting INSIDE a directory named .env or credentials/, so a
    bare-name secret glob matches any path segment, not only the basename."""
    policy = fresh_policy(egress={"allow_hosts": ["example.com"]})
    for payload in SECRETS_INSIDE_SECRET_DIRS:
        v = np.check_egress("https://example.com/upload", policy, payloads=[payload])
        assert_eq(f"secret dir denied: {payload}", "deny", v["verdict"])


BENIGN_SECRET_LOOKALIKES = [
    "wiki/notes/env-vars-guide.md",   # 'env' as a substring, not a .env file
    "docs/pemberton.md",              # 'pem' inside a word
    "src/keyboard.rs",                # 'key' inside a word
    "wiki/secretsauce-recipe.md",     # 'secrets' inside a word, not a path segment
]


def test_egress_secret_lookalikes_are_not_over_blocked():
    """The case-insensitive fix must not start denying ordinary notes that merely
    contain 'env', 'key', 'pem' or 'secrets' as substrings."""
    policy = fresh_policy(egress={"allow_hosts": ["example.com"]})
    for payload in BENIGN_SECRET_LOOKALIKES:
        v = np.check_egress("https://example.com/upload", policy, payloads=[payload])
        assert_true(f"lookalike not treated as secret: {payload}",
                    v["verdict"] != "deny", hint=v.get("reason", ""))


def test_egress_one_secret_among_many_benign_payloads_denies_the_whole_batch():
    policy = fresh_policy(egress={"allow_hosts": ["example.com"]})
    v = np.check_egress("https://example.com/upload", policy,
                        payloads=["wiki/hot.md", "wiki/index.md", ".env", "README.md"])
    assert_eq("one secret poisons the batch", "deny", v["verdict"])


# ─── Host suffix matching: the allowlist must not become a wildcard ──────────
def test_host_suffix_matching_boundary():
    """'example.com' matches itself and its subdomains. It must NOT match
    'notexample.com' — the boundary is a dot, not a substring. Getting this
    wrong silently converts an allowlist into an allow-all."""
    patterns = ["example.com"]
    assert_true("exact match", np._host_matches("example.com", patterns))
    assert_true("subdomain match", np._host_matches("api.example.com", patterns))
    assert_true("deep subdomain match", np._host_matches("a.b.example.com", patterns))
    assert_true("suffix impostor NOT matched",
                not np._host_matches("notexample.com", patterns))
    assert_true("prefix impostor NOT matched",
                not np._host_matches("example.com.evil.net", patterns))
    assert_true("bare-word impostor NOT matched",
                not np._host_matches("example.community", patterns))
    assert_true("empty pattern list matches nothing",
                not np._host_matches("example.com", []))


def test_host_suffix_boundary_end_to_end_on_egress():
    """The boundary property has to hold through the real verdict, not just in
    the helper: an impostor host must still be asked about, never allowed."""
    policy = fresh_policy(egress={"allow_hosts": ["example.com"]})
    assert_eq("egress allows api.example.com", "allow",
              np.check_egress("https://api.example.com/", policy)["verdict"])
    assert_eq("egress does NOT allow notexample.com", "ask",
              np.check_egress("https://notexample.com/", policy)["verdict"])


def test_host_matching_is_case_insensitive_and_dot_tolerant():
    assert_true("uppercase host matches", np._host_matches("api.example.com", ["EXAMPLE.COM"]))
    assert_true("leading-dot pattern matches", np._host_matches("api.example.com", [".example.com"]))
    v = np.check_egress("https://API.Example.COM/", fresh_policy(egress={"allow_hosts": ["example.com"]}))
    assert_eq("mixed-case URL host allowed", "allow", v["verdict"])


# ─── CLI exit codes, against a throwaway vault ───────────────────────────────

def _sandbox_cli(tmp: str) -> Path:
    """Copy net-policy.py into a temp vault so its VAULT_ROOT (and therefore its
    .vault-meta/net.json) resolves inside the tempdir. The real vault stays clean."""
    scripts = Path(tmp) / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    dest = scripts / "net-policy.py"
    shutil.copy2(HELPER, dest)
    return dest


def _run(cli: Path, *args):
    return subprocess.run([sys.executable, str(cli), *args],
                          capture_output=True, text=True, timeout=10)


def test_cli_exit_codes():
    """allow=0, deny=1, ask=3. The exit code IS the verdict for shell callers."""
    with tempfile.TemporaryDirectory() as tmp:
        cli = _sandbox_cli(tmp)

        r = _run(cli, "check-fetch", "https://example.com/")
        assert_eq("cli allow → exit 0", 0, r.returncode)
        assert_eq("cli allow → verdict json", "allow", json.loads(r.stdout)["verdict"])

        r = _run(cli, "check-fetch", "http://169.254.169.254/")
        assert_eq("cli deny → exit 1", 1, r.returncode)
        assert_eq("cli deny → verdict json", "deny", json.loads(r.stdout)["verdict"])

        r = _run(cli, "check-egress", "https://unknown.example/")
        assert_eq("cli ask → exit 3", 3, r.returncode)
        assert_eq("cli ask → verdict json", "ask", json.loads(r.stdout)["verdict"])

        r = _run(cli, "check-egress", "https://unknown.example/", "--payload", ".env")
        assert_eq("cli secret payload → exit 1", 1, r.returncode)


def test_cli_no_subcommand_is_usage_error():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _sandbox_cli(tmp)
        r = _run(cli)
        assert_eq("cli no args → exit 2", 2, r.returncode)


def test_cli_set_mode_rejects_invalid():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _sandbox_cli(tmp)
        r = _run(cli, "set-mode", "bogus")
        assert_eq("cli invalid mode → exit 4", 4, r.returncode)
        assert_true("no net.json written on invalid mode",
                    not (Path(tmp) / ".vault-meta" / "net.json").exists())


def test_cli_set_mode_then_get_and_offline_denies():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _sandbox_cli(tmp)

        assert_eq("cli get (no config) → live", "live", _run(cli, "get").stdout.strip())

        r = _run(cli, "set-mode", "offline")
        assert_eq("cli set-mode offline rc=0", 0, r.returncode)
        assert_true("net.json written", (Path(tmp) / ".vault-meta" / "net.json").is_file())
        assert_eq("cli get → offline", "offline", _run(cli, "get").stdout.strip())

        r = _run(cli, "check-fetch", "https://example.com/")
        assert_eq("offline mode → cli exit 1", 1, r.returncode)


def test_cli_grant_then_revoke():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _sandbox_cli(tmp)

        assert_eq("before grant → ask (exit 3)", 3,
                  _run(cli, "check-egress", "https://api.example.com/").returncode)

        assert_eq("grant rc=0", 0, _run(cli, "grant", "example.com").returncode)
        assert_eq("after grant, subdomain → allow (exit 0)", 0,
                  _run(cli, "check-egress", "https://api.example.com/").returncode)
        assert_eq("after grant, impostor host still asks (exit 3)", 3,
                  _run(cli, "check-egress", "https://notexample.com/").returncode)
        assert_eq("after grant, secret payload still denied (exit 1)", 1,
                  _run(cli, "check-egress", "https://api.example.com/",
                       "--payload", "id_rsa").returncode)

        assert_eq("revoke rc=0", 0, _run(cli, "revoke", "example.com").returncode)
        assert_eq("after revoke → ask again (exit 3)", 3,
                  _run(cli, "check-egress", "https://api.example.com/").returncode)


def test_cli_config_is_valid_json():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _sandbox_cli(tmp)
        r = _run(cli, "config")
        assert_eq("cli config rc=0", 0, r.returncode)
        cfg = json.loads(r.stdout)
        assert_eq("config schema_version", 1, cfg["schema_version"])
        assert_true("config has inbound + egress",
                    "inbound" in cfg and "egress" in cfg)


def test_cli_corrupt_policy_fails_closed():
    """End-to-end fail-closed: a corrupt net.json must exit 1, print no 'allow'
    verdict on stdout, and say so on stderr."""
    with tempfile.TemporaryDirectory() as tmp:
        cli = _sandbox_cli(tmp)
        meta = Path(tmp) / ".vault-meta"
        meta.mkdir(parents=True, exist_ok=True)
        (meta / "net.json").write_text("{ truncated", encoding="utf-8")

        r = _run(cli, "check-fetch", "https://example.com/")
        assert_eq("corrupt policy → cli exit 1", 1, r.returncode)
        assert_true("corrupt policy → no allow on stdout",
                    "allow" not in r.stdout, hint=r.stdout)
        assert_true("corrupt policy → deny reason on stderr",
                    "deny" in r.stderr, hint=r.stderr)


def main():
    print("=== test_net_policy.py ===")
    test_absent_config_is_live_inbound_explicit_egress()
    test_load_does_not_mutate_the_default_policy()
    test_save_load_roundtrip()
    test_corrupt_policy_fails_closed()
    test_corrupt_policy_does_not_yield_permissive_defaults()
    test_ssrf_guard_denies_private_address_space()
    test_ssrf_guard_denies_encoded_ip_forms()
    test_numeric_looking_public_hosts_are_not_over_blocked()
    test_ssrf_guard_denies_loopback_by_name()
    test_public_host_allowed_in_live_mode()
    test_non_http_schemes_denied()
    test_allow_private_addresses_is_a_working_escape_hatch()
    test_escape_hatch_does_not_unlock_the_named_denylist()
    test_offline_mode_denies_everything()
    test_ask_mode_returns_ask_for_inbound()
    test_ask_mode_still_enforces_the_ssrf_guard()
    test_inbound_allowlist_when_non_empty_excludes_everything_else()
    test_egress_unknown_host_asks()
    test_egress_allowlisted_host_allows()
    test_egress_consent_never_denies()
    test_egress_benign_payload_to_allowlisted_host_is_allowed()
    test_egress_secret_payloads_denied()
    test_egress_secrets_denied_regardless_of_case()
    test_egress_secrets_inside_secret_named_directories_denied()
    test_egress_secret_lookalikes_are_not_over_blocked()
    test_egress_secrets_denied_even_when_host_is_allowlisted()
    test_egress_one_secret_among_many_benign_payloads_denies_the_whole_batch()
    test_host_suffix_matching_boundary()
    test_host_suffix_boundary_end_to_end_on_egress()
    test_host_matching_is_case_insensitive_and_dot_tolerant()
    test_cli_exit_codes()
    test_cli_no_subcommand_is_usage_error()
    test_cli_set_mode_rejects_invalid()
    test_cli_set_mode_then_get_and_offline_denies()
    test_cli_grant_then_revoke()
    test_cli_config_is_valid_json()
    test_cli_corrupt_policy_fails_closed()
    print("\nAll net-policy tests passed.")


if __name__ == "__main__":
    main()
