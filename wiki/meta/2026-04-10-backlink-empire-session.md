---
type: session
title: "Backlink Empire - Blog Posts, Karpathy Gist, GitHub Cross-Linking"
created: 2026-04-10
updated: 2026-04-10
tags:
  - session
  - backlinks
  - seo
  - github
  - blog
  - rankenstein
status: complete
related:
  - "Claude Obsidian"
  - "Claude Canvas"
  - "Rankenstein"
  - "Karpathy LLM Wiki Pattern"
decision_date: 2026-04-10
---

## What Was Done

### Blog Posts Created

Two blog posts written, deployed to Vercel, and submitted to Google Indexing API + Bing IndexNow:

1. **claude-obsidian-ai-second-brain** - "I Turned Obsidian Into a Self-Organizing AI Brain"
   - Focus keyword: "obsidian ai second brain"
   - ~2,800 words, 5 repo images/GIFs, 3 SVG charts, 8 sourced statistics
   - Images from `wiki/meta/` in the claude-obsidian repo (graph view, wiki map, welcome canvas GIF)
   - Live: agricidaniel.com/blog/claude-obsidian-ai-second-brain

2. **claude-canvas-ai-visual-production** - "Claude Code Just Turned Obsidian Canvas Into an AI Design Studio"
   - Focus keyword: "obsidian canvas ai"
   - ~2,500 words, 5 screenshots from repo, 2 SVG charts, 7 sourced statistics
   - Images from `assets/screenshots/` in the claude-canvas repo
   - Live: agricidaniel.com/blog/claude-canvas-ai-visual-production

### Karpathy Gist Comment

Comment posted on Andrej Karpathy's LLM Wiki gist (gist ID: 442a6bf555914893e9891c11519de94f). Links claude-obsidian (358 stars), claude-canvas, and the blog post. Highlights hot cache, contradiction flagging, 8-category lint, and autonomous research loops as differentiators.

### GitHub Backlink Empire (26 Repos Updated)

**Phase 1 - API updates (no README changes):**
- Set homepage URLs on 10 repos (on-page-seo, Keywordo-kun, claude-youtube, marketing-skill-pack, google-maps-scraper, claude-repurpose, claude-gif, claude-avatar, rankenstein-pro-latest, claude-canvas)
- Set topics/tags on 25 repos (grouped by category: SEO, content, marketing, obsidian, media, dev tools, n8n)

**Phase 2-5 - README updates:**
- Added standardized Author section to 25 repos with links to:
  - agricidaniel.com/about
  - agricidaniel.com/blog
  - skool.com/ai-marketing-hub
  - youtube.com/@AgriciDaniel
  - github.com/AgriciDaniel

**Rankenstein.pro backlinks (5 SEO-relevant repos only):**
- claude-seo: "Publishing Pipeline" section
- claude-blog: "Publishing Platform" section
- on-page-seo: blockquote before Author
- Keywordo-kun: blockquote before Author
- marketing-skill-pack: mentioned in Author context

### Verification Results

64/65 checks passed. 1 minor note: claude-obsidian uses footer-style attribution instead of formal `## Author` heading (intentional - already had custom attribution).

## Key Decisions

- **rankenstein.pro placement**: Only on SEO-relevant repos (5 of 26). Not spammed across video/image/dev tools. Keeps it natural.
- **Karpathy gist tone**: Technical, value-first. Led with the implementation, not marketing. Matched the collaborative tone of the comment thread.
- **Blog keyword strategy**: "obsidian ai second brain" (trending, moderate competition) and "obsidian canvas ai" (low competition, growing query). Both exploit competitor gaps - no existing article covers a specific tool in depth.
- **Cover images**: Used real repo assets (pixel-art covers, screenshots, GIFs) rather than stock photos. Converts better and is more authentic.

## Numbers

- ~87 new backlinks from github.com (DA 96) to agricidaniel.com
- ~6 backlinks to rankenstein.pro
- ~25 backlinks to skool.com/ai-marketing-hub
- 22 total pages in sitemap (was 20 at session start)
- 15 total blog posts (was 13)

## Workflow for Future Blog Posts

This session established a repeatable workflow:
1. Explore repo thoroughly (features, images, stats)
2. Keyword research + competitor analysis via web search
3. Write blog JSON with HTML content, SVG charts, repo images
4. Add to blogPosts.ts, sitemap.xml, llms.txt
5. Build + prerender + deploy to Vercel
6. Submit to Google Indexing API + Bing IndexNow
7. Set repo homepage to blog URL
8. Add blog backlink to repo README
9. Update README with Author/community section
