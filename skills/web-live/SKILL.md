---
name: web-live
description: "Always-on internet for the Compound Vault (v2.0 'Live Core'). The vault may READ the public web at any time without asking; SENDING vault content to a third party is gated by explicit consent, always. Every network call consults `scripts/net-policy.py` first. Ships an SSRF guard (private, loopback, link-local and reserved address space denied) and an unconditional secret-payload block. Modes: live | ask | offline. Triggers on: web-live, go online, fetch this url, read the web, search the web, is the vault online, network policy, net policy, net mode, offline mode, live mode, allow this host, grant egress, revoke egress, can you access the internet, SSRF, why was that url blocked, network denied."
allowed-tools: Read, Bash, WebFetch, WebSearch
---

# web-live: The Always-On Internet Capability

The vault is **LIVE by default**. It may read the public web at any time, without asking, as part of answering a question or ingesting a source. That is the capability v2.0 ships.

The capability is also a liability, and the two halves are not symmetric. That asymmetry is the entire design.

---

## The asymmetry

| | What it is | Risk | Default |
|---|---|---|---|
| **INBOUND** | Fetching a public page, running a search. Reading the world. | Low. The page was already public. | **Always on.** No prompt. |
| **EGRESS** | Sending vault content to a third party. Writing to the world. | This is how private notes leak. | **Gated by explicit consent.** Every time. |

Reading the world is not the same act as writing to it. Do not collapse the two because both happen to use a socket. The v1.7.0 audit's BLOCKER B1 was a data-egress consent gap; turning the network on without re-deriving that boundary would have reopened it. The boundary is re-derived in one place, as code, in `scripts/net-policy.py`, and every skill that touches the network asks that module first.

---

## The gate: consult the policy BEFORE every call

Every network call, without exception, consults the policy first.

```bash
# Inbound: may I READ this URL?
python3 scripts/net-policy.py check-fetch "https://example.com/article"

# Outbound: may I SEND vault content to this URL?
python3 scripts/net-policy.py check-egress "https://api.example.com/upload" \
  --payload wiki/concepts/Foo.md
```

Both print a JSON verdict to stdout and signal via exit code:

| Exit | Verdict | What you do |
|---|---|---|
| `0` | `allow` | Proceed. |
| `1` | `deny` | **Stop.** Report the `reason` to the user. Do not retry with a different tool. |
| `3` | `ask` | **Prompt the human.** Wait for an answer. You may not proceed on your own authority. |
| `2` | usage error | Fix the invocation. |
| `4` | invalid mode | Bad mode name passed to `set-mode`. |

Idiom for a consumer skill:

```bash
if python3 scripts/net-policy.py check-fetch "$URL" >/tmp/verdict.json; then
  : # exit 0, allowed, fetch it
else
  rc=$?
  # rc=3 means ASK: surface the reason to the human and stop.
  # rc=1 means DENY: report and stop.
  cat /tmp/verdict.json
  exit $rc
fi
```

**Exit code 3 is not a soft warning.** It means consent is required and you do not have it. Prompting the human is the only correct response. Deciding for them, retrying through the browser, or routing around the check with `curl` are all the same violation wearing different clothes.

---

## Modes

```bash
python3 scripts/net-policy.py get                # current mode
python3 scripts/net-policy.py config            # full policy JSON
python3 scripts/net-policy.py set-mode live     # read freely (default)
python3 scripts/net-policy.py set-mode ask      # confirm every fetch
python3 scripts/net-policy.py set-mode offline  # no network at all
```

- **live** (default): inbound fetches proceed without a prompt. Egress still asks.
- **ask**: every inbound fetch returns `ask` (exit 3). For sensitive vaults, or a session where the user wants to see every outbound request.
- **offline**: everything is denied, inbound and outbound. Air-gapped.

Policy lives at `.vault-meta/net.json`. Absent config is not an error: a fresh vault is `live` inbound and `explicit` egress, which is the safe pairing. Read freely, send nothing without being asked.

A **corrupt** policy file fails CLOSED. "Could not read the policy, so I allowed it" is exactly the bug class this module exists to prevent.

---

## SSRF guard

Private, loopback, link-local and reserved addresses are DENIED inbound.

**Why:** an agent that will fetch any URL handed to it will happily fetch `http://169.254.169.254/`, the cloud metadata endpoint, and hand over the machine's credentials to whoever asked. The same agent pointed at `http://127.0.0.1:8080/` reaches every admin panel bound to loopback. A URL in a source document is attacker-controlled input, and this is the guard that treats it that way.

Denied by default: loopback (`127.0.0.0/8`, `::1`), link-local (`169.254.0.0/16`, the metadata range), private (`10/8`, `172.16/12`, `192.168/16`), reserved and multicast. Plus the hostnames `localhost`, `metadata.google.internal`, `metadata.goog`.

Unlock deliberately, per-vault, by setting `inbound.allow_private_addresses: true` in `.vault-meta/net.json`. Only do this when the user has asked for it and knows what it opens.

### Honest limitation

**Hostname checks do not resolve DNS.** A hostname that resolves to a private IP (DNS rebinding) is not caught at this layer. Blocking that requires resolving at connect time, inside the fetcher, which is where it belongs.

This module gates POLICY. It says so rather than implying a guarantee it does not provide. Do not tell a user that the SSRF guard makes arbitrary URL fetching safe. It makes it safer, and the residual hole has a name.

---

## Secrets never egress

Egress payloads are scanned against deny globs BEFORE the consent check, and the scan is unconditional.

```
**/.env      **/.env.*     **/secrets/**     **/*.pem
**/*.key     **/id_rsa*    **/.aws/**        **/.ssh/**
**/credentials*
```

A payload matching any of these is denied even when the destination host is on the egress allowlist, even when the user just said yes.

**Consent to send the vault is not consent to send an SSH key.** Nobody means that when they say yes. The ordering in `check_egress` is deliberate: secrets first, consent second, so no answer to the consent prompt can ever unlock a secret.

---

## Granting and revoking egress

When `check-egress` returns `ask`, surface the reason and let the user decide. If they grant it:

```bash
python3 scripts/net-policy.py grant api.example.com
python3 scripts/net-policy.py revoke api.example.com
```

A grant is per-host and persists in `.vault-meta/net.json`. A bare domain matches its subdomains (`example.com` covers `api.example.com`) but not lookalikes (`notexample.com` does not match). The boundary is a dot, not a substring: getting that wrong turns an allowlist into a wildcard.

Set `egress.consent: "never"` to make the vault permanently read-only against the network.

---

## What this pairs with

- **`defuddle`**: strip ads, nav, cookie walls and boilerplate from a fetched page before it enters the vault. Cuts 40 to 60 percent of the tokens and produces a cleaner page. Run it on every article-shaped URL.
- **`browser`**: WebFetch is blind to JS-rendered and auth-gated pages, and it fails silently by returning the page shell and reporting success. When a fetch comes back suspiciously thin, escalate to the browser transport.
- **`wiki-ingest`**: the destination. A fetched, cleaned page gets filed per the vault's methodology mode.

The typical live path: `check-fetch` → fetch (or browser) → `defuddle` → `ingest`.

---

## Cross-reference

- Policy gate: [`scripts/net-policy.py`](../../scripts/net-policy.py)
- Browser escalation: [`skills/browser/SKILL.md`](../browser/SKILL.md)
- Page cleaner: [`skills/defuddle/SKILL.md`](../defuddle/SKILL.md)
- The egress gap this closes: `docs/audits/v1.7.0-audit-2026-05-17.md` BLOCKER B1

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Read the actual verdict from `net-policy.py`. Do not assume a URL is fine because it looks fine. |
| 2 | OBSERVE (int) | Am I about to treat an egress as an inbound because both are "just a request"? That collapse is the failure mode. |
| 3 | LISTEN | Exit 3 means the human decides. Prompt, then wait. Their silence is not a yes. |
| 4 | THINK | Inbound is cheap and reversible; egress is neither. Weigh them differently because they are different acts. |
| 5 | CONNECT (lat) | A URL inside an ingested source is attacker-controlled input, exactly like a URL a stranger typed. Treat it that way. |
| 6 | CONNECT (sys) | Every network-touching skill funnels through this one gate. One policy, one place, no side doors. |
| 7 | FEEL | A denial should read like an explanation, not a wall. Print the `reason`, and print the command that would grant it. |
| 8 | ACCEPT | The DNS-rebinding hole is real and is not closed here. Say so. Never imply a guarantee this layer does not provide. |
| 9 | CREATE | Deliver the fetched page cleaned and cited, with its source URL and fetch date attached. |
| 10 | GROW | Every deny worth overriding is a policy bug. Fix the policy, not the call site. |
