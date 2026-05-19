---
name: defuddle
description: "Strip clutter from web pages before ingesting into the wiki. Removes ads, navigation, headers, footers, and boilerplate: leaving clean readable markdown that saves 40-60% tokens. Triggers on: defuddle, clean this page, strip this url, fetch and clean, clean web content before ingesting, strip ads, remove clutter, clean URL content, readable markdown from URL."
allowed-tools: Read Bash
---

# defuddle: Web Page Cleaner

Defuddle extracts the meaningful content from a web page and drops everything else: ads, cookie banners, nav bars, related articles, footers, social sharing buttons. What remains is the article body as clean markdown.

Use this before any URL ingestion. It is optional but strongly recommended. It cuts token usage by 40-60% on typical web articles and produces cleaner wiki pages.

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

### Save to raw/
```bash
defuddle https://example.com/article > raw/articles/article-slug-$(date +%Y-%m-%d).md
```

### Add frontmatter header after saving
After running defuddle, prepend the source URL and fetch date:
```bash
SLUG="article-slug-$(date +%Y-%m-%d)"
{ echo "---"; echo "source_url: https://example.com/article"; echo "fetched: $(date +%Y-%m-%d)"; echo "---"; echo ""; defuddle https://example.com/article; } > raw/articles/$SLUG.md
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
2. Then: `ingest raw/articles/[slug].md`
