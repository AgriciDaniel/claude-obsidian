---
name: browser
description: "Browser automation for the Compound Vault (v2.0 'Live Core'). WebFetch is blind to JS-rendered, login-gated and cookie-walled pages, and it fails SILENTLY by returning the page shell and reporting success. This skill drives a real browser instead. Fallback chain: playwright (full interaction) > cdp (headless Chrome render, screenshot, dump-dom) > fetch (plain HTTP, always available). Detection via `scripts/detect-browser.sh`, snapshot at `.vault-meta/browser.json`. Every navigation still clears `net-policy.py` first. Triggers on: browser, headless, playwright, chrome, chromium, CDP, devtools, screenshot this page, render this page, this page needs JS, the fetch came back empty, page is behind a login, cookie wall, dump the DOM, click, wait for selector, detect browser, which browser."
allowed-tools: Read, Write, Bash, WebFetch
---

# browser: Rendering the Web the Vault Cannot Otherwise See

## Why this exists

WebFetch retrieves HTML. That is all it does.

A large share of the modern web renders its content in JavaScript, sits behind a login, or serves a cookie wall before the article. To those pages **WebFetch is blind, and it fails SILENTLY**: it returns the shell of the page, finds no error, and reports success. You get a `<div id="root"></div>`, a consent banner, or a headline with no body, and nothing anywhere says "this went wrong."

That silent-success failure is the reason this skill exists. A loud failure you would have caught. This one ships a hollow page straight into the wiki, where it sits looking like knowledge.

**Smell test.** Escalate to the browser when a fetch comes back with any of these:
- Body far shorter than the page obviously is
- A cookie or consent banner as the main content
- "Enable JavaScript to continue" or an empty root div
- A title and byline with no article text
- A login form where the content should be

---

## The fallback chain

| Rank | Transport | Can do | Cannot do |
|---|---|---|---|
| 1 | **playwright** | Full interaction: click, type, authenticate, wait for a selector, scroll, intercept requests. | Nothing relevant. This is the ceiling. |
| 2 | **cdp** | Headless Chrome over DevTools protocol: execute JS, render, screenshot, dump the DOM. | Scripted interaction. No clicking, no typing, no auth flow. |
| 3 | **fetch** | Plain HTTP. Always available. The floor. | JavaScript. Auth. Anything the page does after load. |

Higher is strictly better. Use the highest available; never reach past a working transport for a lower one.

---

## Detection

```bash
bash scripts/detect-browser.sh            # detect and write .vault-meta/browser.json
bash scripts/detect-browser.sh --peek     # print without writing
bash scripts/detect-browser.sh --force    # refresh a snapshot younger than 7 days
```

Snapshot at `.vault-meta/browser.json`:

```json
{
  "preferred": "cdp",
  "fallback_chain": ["cdp", "fetch"],
  "available": {
    "playwright": {"present": false, "how": "", "note": "full interaction: click, type, auth, wait-for-selector"},
    "cdp": {"present": true, "binary": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "flavor": "chrome"},
    "fetch": {"present": true, "note": "ultimate fallback; plain HTTP, no JS execution."},
    "chrome_devtools_mcp": {"present": null, "detection": "deferred"}
  }
}
```

**Consult `preferred` before acting.** Read the snapshot; do not guess which transport exists.

MCP servers are deliberately NOT auto-probed. Calling `claude mcp list` from inside a running Claude session has the reentrancy problem `detect-transport.sh` already documents. MCP stays user-declared: set `preferred` by hand if you want it.

---

## The macOS gotcha (read this before you write any browser probe)

**On macOS, browsers live inside `.app` bundles and do NOT symlink their binary onto PATH.**

So this:

```bash
command -v google-chrome   # nothing
which chromium             # nothing
```

reports "no browser installed" on a Mac with Google Chrome sitting right there in `/Applications`. A PATH-only probe is not a conservative probe. It is a wrong one, and it is wrong in the direction that silently disables the feature.

`detect-browser.sh` probes bundle paths FIRST, PATH second:

```
/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
/Applications/Chromium.app/Contents/MacOS/Chromium
/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge
/Applications/Brave Browser.app/Contents/MacOS/Brave Browser
~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
```

This is the same bug class that made the **Obsidian CLI transport silently never engage on any Mac** (see `wiki/hot.md`, 2026-07-12). It cost real time once. It does not get to cost it twice. If you are adding a new browser flavor, add its bundle path, not just its PATH name.

---

## The policy gate is not optional

**Every navigation goes through `net-policy.py check-fetch` first**, exactly as a plain WebFetch would.

```bash
python3 scripts/net-policy.py check-fetch "$URL" || exit $?   # 1=deny, 3=ask
```

The browser is a better fetcher. It is not a way around the network policy. Reaching for Chrome because WebFetch got denied is a policy violation with extra steps, and the SSRF guard exists precisely because a real browser will cheerfully load `http://169.254.169.254/` and render the cloud credentials for you.

On exit 3 (`ask`), prompt the human. Do not navigate on your own authority.

---

## Workflow

```
check-fetch  →  navigate  →  wait for render  →  screenshot into _attachments/
                                              →  extract DOM
                                              →  defuddle
                                              →  ingest into the wiki
```

The screenshot is evidence: it is what the page actually looked like, and it goes in `_attachments/` so a wiki page can embed it. The DOM extract is the content. Run it through `defuddle` before ingesting, same as any other web source.

---

## CDP recipes

Read the binary out of the snapshot rather than hardcoding a path:

```bash
CHROME="$(python3 -c 'import json; print(json.load(open(".vault-meta/browser.json"))["available"]["cdp"]["binary"])')"
```

### Dump the rendered DOM

```bash
"$CHROME" --headless --disable-gpu --dump-dom "$URL" > /tmp/page.html
```

This is the payoff: `--dump-dom` returns the DOM **after** JavaScript has run, which is the thing WebFetch cannot give you.

### Screenshot into `_attachments/`

```bash
SHOT="_attachments/$(date +%Y-%m-%d)-$(echo "$URL" | shasum | cut -c1-8).png"
"$CHROME" --headless --disable-gpu \
  --screenshot="$SHOT" \
  --window-size=1280,900 \
  "$URL"
```

### Clean the rendered DOM, then ingest

```bash
"$CHROME" --headless --disable-gpu --dump-dom "$URL" > /tmp/page.html
defuddle /tmp/page.html > ".raw/articles/$SLUG.md"
# then: ingest .raw/articles/$SLUG.md
```

### Always use a throwaway profile

```bash
PROFILE="$(mktemp -d)"
"$CHROME" --headless --disable-gpu --user-data-dir="$PROFILE" --dump-dom "$URL"
rm -rf "$PROFILE"
```

`--headless` against the user's **real** profile can hang on a keychain prompt, a profile-lock conflict with a running Chrome, or a restore-session dialog. A temp `--user-data-dir` sidesteps all three and leaves the user's browser untouched. Do this by default.

---

## Playwright

When `preferred` is `playwright`, you have real interaction: `click`, `fill`, `wait_for_selector`, `goto` with `wait_until="networkidle"`. Use it for pages that need a button pressed before the content appears, an infinite scroll driven to the bottom, or a session the user has authenticated.

Everything above still holds: `check-fetch` first, throwaway context by default, screenshot into `_attachments/`, `defuddle` before ingest.

---

## The line you do not cross

**Never bypass a paywall. Never defeat an auth wall the user does not have credentials for.**

Not by scraping the JSON-LD behind the wall, not by spoofing a crawler user-agent, not by stripping the overlay from the DOM, not by pulling the article out of a cache. That a technique works is not an argument that it is permitted.

Log in **as the user**, **with the user's consent**, or **not at all**. If the user has a subscription and asks you to use it, that is fine and that is what Playwright's auth support is for. If they do not, the correct output is "this is paywalled," and you stop.

---

## Cross-reference

- Detection script: [`scripts/detect-browser.sh`](../../scripts/detect-browser.sh)
- Network policy gate: [`skills/web-live/SKILL.md`](../web-live/SKILL.md)
- Page cleaner: [`skills/defuddle/SKILL.md`](../defuddle/SKILL.md)
- Same bug class, prior occurrence: `wiki/hot.md` (Obsidian CLI never engaged on macOS, 2026-07-12)

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Read `.vault-meta/browser.json`. Look at what actually came back from the fetch, not at whether it returned 200. |
| 2 | OBSERVE (int) | A successful fetch is not a complete fetch. Am I about to file a page shell as if it were an article? |
| 3 | LISTEN | "It's behind a login" means log in as them, with consent. It never means find a way around. |
| 4 | THINK | Pick the lowest transport that actually renders the page. Do not launch Chrome for static HTML. |
| 5 | CONNECT (lat) | The PATH-only probe failing on macOS is the same bug that killed the Obsidian CLI transport. Bundle paths first, every time. |
| 6 | CONNECT (sys) | Browser output flows into defuddle, then wiki-ingest. It is a fetcher, not a destination. |
| 7 | FEEL | A hollow page feels hollow. Trust that. Thin body, consent banner, empty root div: escalate. |
| 8 | ACCEPT | Some pages will not yield. Paywalled is a legitimate final answer. Say it and stop. |
| 9 | CREATE | Rendered DOM plus a screenshot in `_attachments/`, cleaned and cited, ready to ingest. |
| 10 | GROW | Every page that defeats the current transport is a detection gap. File it; upgrade the chain. |
