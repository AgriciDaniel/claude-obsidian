---
name: defuddle
description: "Strip clutter from web pages before ingesting into the wiki. Removes ads, navigation, headers, footers, and boilerplate: leaving clean readable markdown that saves 40-60% tokens. Triggers on: defuddle, clean this page, strip this url, fetch and clean, clean web content before ingesting, strip ads, remove clutter, clean URL content, readable markdown from URL."
allowed-tools: Read Bash
---

# defuddle: Web Page Cleaner

Defuddle extracts the meaningful content from a web page and drops everything else: ads, cookie banners, nav bars, related articles, footers, social sharing buttons. What remains is the article body as clean markdown.

Use this before any URL ingestion. It is optional but strongly recommended. It cuts token usage by 40-60% on typical web articles and produces cleaner wiki pages.

**Substrate note (v1.7+)**: Unlike `obsidian-markdown` / `obsidian-bases` / `json-canvas` (where we defer to kepano/obsidian-skills as upstream), the `defuddle` skill is original to claude-obsidian — kepano's marketplace does not ship a defuddle skill. This is the canonical version. The underlying `defuddle-cli` is independent of either marketplace and lives at [github.com/kepano/defuddle](https://github.com/kepano/defuddle).

---

## Install

```bash
npm install -g defuddle-cli
```

Verify: `defuddle --version`

---

## Usage

### Clean a URL directly
```bash
defuddle https://example.com/article
```
Outputs clean markdown to stdout.

### Save to .raw/
```bash
defuddle https://example.com/article > .raw/articles/article-slug-$(date +%Y-%m-%d).md
```

### Add frontmatter header after saving
After running defuddle, prepend the source URL and fetch date:
```bash
SLUG="article-slug-$(date +%Y-%m-%d)"
{ echo "---"; echo "source_url: https://example.com/article"; echo "fetched: $(date +%Y-%m-%d)"; echo "---"; echo ""; defuddle https://example.com/article; } > .raw/articles/$SLUG.md
```

### Clean a local HTML file
```bash
defuddle page.html
```

---

## When to Use

**Use defuddle when:**
- Ingesting a news article, blog post, or documentation page from a URL
- The page has a lot of surrounding content (most web pages do)
- You want to stay within token budget on a long article

**Skip defuddle when:**
- The source is already a clean markdown or PDF file
- The page is a dashboard, app, or structured data (defuddle expects article-style content)
- defuddle is not installed and the article is short enough to process raw

---

## Fallback

If defuddle is not installed, check:

```bash
which defuddle 2>/dev/null || echo "not installed"
```

If not installed: use WebFetch directly. The content will be less clean but still workable.

---

## Integration with /wiki-ingest

The `/wiki-ingest` skill checks for defuddle automatically when a URL is passed. You do not need to run defuddle manually before ingesting a URL. The ingest skill will call it if available.

To manually clean a page and save before ingesting:
1. Run the save command above
2. Then: `ingest .raw/articles/[slug].md`

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Which URL? What's actually on the page? Don't assume the title matches the content. |
| 2 | OBSERVE (int) | Am I assuming the page has the content the user expects? Verify before extracting. |
| 3 | LISTEN | Did the user say "the article" (main content only) or "the link" (everything visible)? |
| 4 | THINK | Strip boilerplate, preserve structure, capture metadata. Quote URLs in shell to avoid injection. |
| 5 | CONNECT (lat) | How does this domain typically render? Some sites mangle defuddle's heuristics; track those. |
| 6 | CONNECT (sys) | Shells out to defuddle-cli (kepano); output lands in `.raw/` for wiki-ingest pickup. |
| 7 | FEEL | Clean markdown that reads like the original, not boilerplate residue. |
| 8 | ACCEPT | Some pages don't extract well. Flag and move on; don't force when the heuristic loses. |
| 9 | CREATE | Markdown to stdout, redirected to `.raw/articles/<slug>-<date>.md`. |
| 10 | GROW | Extraction failures suggest defuddle-cli upgrade or alternative extractor — track them as backlog. |
