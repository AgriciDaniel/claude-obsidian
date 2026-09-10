# Attributions

claude-obsidian is an original work. The following third-party patterns, tools, and creators informed its design.

---

## LLM Wiki Pattern

**Author:** Andrej Karpathy
**Source:** https://github.com/karpathy
**Use:** The core architecture of claude-obsidian — using an LLM to build and maintain a structured wiki from raw sources — is based on the LLM Wiki pattern Karpathy described publicly. claude-obsidian is an independent implementation; no code or content from Karpathy's repositories was copied.

---

## ITS CSS Snippets

**Author:** SlRvb
**Source:** https://github.com/SlRvb/Obsidian--ITS-Theme
**License:** GPL-2.0
**Files:**
- `.obsidian/snippets/ITS-Dataview-Cards.css`
- `.obsidian/snippets/ITS-Image-Adjustments.css`

These snippets exist only in the private contributor-vault state. They are not
selected into the deterministic public product artifact and are not installed
by the vault template. The project-owned `templates/vault/.obsidian/snippets/vault-colors.css`
is the only snippet distributed by claude-obsidian.

---

## Historical contributor-vault plugins

The source repository has contained the following Obsidian community plugins in
its contributor-vault state. They are not included in the deterministic public
product artifact or installed by the vault template. Install and review them
through Obsidian under their respective licenses.

| Plugin | Author | Repository |
|--------|--------|-----------|
| Calendar | Liam Cain | https://github.com/liamcain/obsidian-calendar-plugin |
| Thino | Boninall (Quorafind) | https://github.com/Quorafind/Obsidian-Thino |
| Obsidian Excalidraw | Zsolt Viczian | https://github.com/zsviczian/obsidian-excalidraw-plugin |
| Obsidian Banners | Danny Hernandez | https://github.com/noatpad/obsidian-banners |

`scripts/setup-vault.sh` does not download unverified plugin binaries. It prints
manual installation guidance instead.

---

## Adopted contributor designs

Two community pull requests diagnosed retrieval bugs and proposed fixes that
the v2.0.0 refoundation implemented in near-identical form. The pull requests
were not merged as submitted because the surrounding files were rewritten, but
the designs are theirs.

| Change | Contributor | Pull request |
|--------|-------------|--------------|
| Nomic `search_query` and `search_document` task prefixes in the reranker, including the `with_task_prefix` helper and cache-scheme invalidation | maartengoet | https://github.com/AgriciDaniel/claude-obsidian/pull/77 |
| BM25 fallback order preserved in reranker no-op paths (`bm25_score` before `score`) | vinsocci | https://github.com/AgriciDaniel/claude-obsidian/pull/62 |

---

## claude-obsidian

**Author:** AgriciDaniel / AI Marketing Hub
**License:** MIT (see [LICENSE](LICENSE))
**Repository (public canonical):** https://github.com/AgriciDaniel/claude-obsidian
**Community early-access mirror (Pro):** https://github.com/AI-Marketing-Hub
