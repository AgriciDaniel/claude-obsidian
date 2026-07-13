---
name: youtube
description: >
  Fetch a YouTube video's transcript as clean plaintext, summarize it, and file both
  as wiki sources via wiki-ingest. Pulls captions/subtitles via the youtube-transcript-api
  package run through uvx — no install needed. Use when the user wants the spoken text,
  transcript, or captions from a YouTube video, or asks "what does this video say".
  Triggers: "youtube transcript", "get captions", "video text", "subtitles from",
  "transcribe this video", "what does this youtube say", any YouTube URL dropped
  into a vault session.
---

# YouTube Transcript Fetcher

Extract spoken-text transcript from any YouTube video that has captions (manual or auto-generated). Tightly coupled to `wiki-ingest`: every run files both the raw transcript and a synthesized summary as wiki sources.

## Tool

`youtube-transcript-api` Python package. Run via `uvx` — no global install required. Package ships binary `youtube_transcript_api` (underscore).

## Extract video ID

YouTube URLs come in several forms. Parse the 11-char video ID before calling the API:

| URL form | ID location |
|---|---|
| `youtube.com/watch?v=XXXXXXXXXXX` | `v=` param |
| `youtu.be/XXXXXXXXXXX` | path segment |
| `youtube.com/shorts/XXXXXXXXXXX` | after `/shorts/` |
| `youtube.com/embed/XXXXXXXXXXX` | after `/embed/` |
| bare 11-char string | use as-is |

Regex catch-all: `[A-Za-z0-9_-]{11}`.

## Fetch clean plaintext

The raw CLI output is a Python list of snippet objects. For clean readable text, run a one-liner that joins only the `.text` fields and strips timestamps. **Note the API shape for v1.x:** instantiate the class and call `.fetch()` (the older `get_transcript` classmethod no longer exists):

```powershell
uvx --from youtube-transcript-api python -c "from youtube_transcript_api import YouTubeTranscriptApi; print(' '.join(s.text for s in YouTubeTranscriptApi().fetch('<ID>')))"
```

If `.fetch()` ever errors with a missing `video_id` argument, you called it as a classmethod — instantiate first: `YouTubeTranscriptApi().fetch(...)`. For language forcing: `YouTubeTranscriptApi().fetch('<ID>', languages=['en'])`.

`>>` markers (speaker shifts) and `[music]` tags appear inline — leave them; they convey structure.

## Save to file (transcript-only requests)

When the transcript is large (>2KB preview truncated in tool output) or the user wants it kept as a standalone file (not a wiki ingest — see below for the default wiki-filing path), write directly to a file instead of stdout:

```powershell
uvx --from youtube-transcript-api python -c "from youtube_transcript_api import YouTubeTranscriptApi; open('transcript.txt','w',encoding='utf-8').write(' '.join(s.text for s in YouTubeTranscriptApi().fetch('<ID>')))"
```

Default filename `transcript.txt` in cwd, or use a descriptive name `<video-id>-transcript.txt`. Always set `encoding='utf-8'`.

## Language

Default = first available caption track (usually English auto). To force a language, pass `languages=['en']` (or other codes like `es`, `de`, `hi`) to `YouTubeTranscriptApi().fetch('<ID>', languages=['en'])`.

## Video title + author (for filenames)

Fetch the human-readable title and channel via YouTube's free oEmbed endpoint (no auth, no extra dependency) right after extracting the ID:

```powershell
uvx --from youtube-transcript-api python -c "import urllib.request,json; d=json.load(urllib.request.urlopen('https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=<ID>&format=json',timeout=15)); print(d['title']); print(d['author_name'])"
```

Store the **verbatim title in frontmatter** (`title:`) for fidelity and attribution. **Do NOT use the title as the filename.** Clickbait titles ("WOW Didn't know THIS happened", "They STILL Wouldn't Stop...") are ambiguous and useless for finding the note later.

**Filename = generated from the summary's actual content**, after you've written the summary. Derive a short, descriptive, unambiguous name from what the video is actually about:
- Bad filename (from title): `They STILL Wouldn't Stop Driving Through... So We Secured Everything.md`
- Good filename (from content): `DIY 800ft Conduit & Water Hydrant Install (The Zaytsevs).md`

Filename rules:
- Describe the substance: topic + key detail, ~40-70 chars.
- Append `(Author)` for disambiguation when the topic is generic.
- Sanitize for Windows/POSIX: strip `\ / : * ? " < > |`, trim trailing dots/spaces. Keep commas, apostrophes, `-`, `&`, `()`.
- If two videos would collide on the generated name, append the `youtube_id`.

Keep `youtube_id` + `url` + `author` + `title` in frontmatter so the original title and ID are never lost.

If oEmbed fails (private/age-restricted/blocked), set `title: unknown` in frontmatter and fall back to `<video-id>` as filename only if you can't summarize content.

## Failure modes

- **No transcript available** (`NoTranscriptFound`, `CouldNotRetrieveTranscript`): video has no captions of any kind. Tell the user; suggest Whisper transcription (download audio via `yt-dlp`, transcribe).
- **Video is private/age-restricted/region-blocked**: API can't access. Surface the error verbatim.
- **Cookie/consent wall**: rare; if hit, suggest the user provide cookies or use `yt-dlp` subtitle download instead.

Never fabricate transcript content. If fetch fails, report the failure — do not guess what the video says.

## Default output (URL only, no other instruction)

When the user provides **only a YouTube URL** with nothing else, the skill's job is NOT to dump raw transcript. Fetch the transcript, then write back a **concise summary** of the video. See "Save to wiki (always)" below for when this summary is actually emitted to chat — after all file writes, not before.

- **1–3 sentence TL;DR** of what the video is about.
- **Valuable bullet points** — the substantive points, steps, facts, or claims. Not a line-by-line recap; distill what a viewer would want to remember. Group logically.
- **Table** if the content is structured (steps, comparisons, specs, parts/lists, timestamps, pros/cons). Use markdown table. Skip if content doesn't fit a table.
- **Remarks** (optional) — only if genuinely valuable: key takeaways, things to verify, notable claims, or context the user should know. Keep to 1–3 lines. Omit entirely if nothing adds value.

If the user asks for something specific (full text, save to file, single quote, language X, a question about the content), that request overrides this default.

Do not include the raw transcript unless the user asks for it. Do not pad with filler. Keep it tight.

## Save to wiki (always)

Every run persists **both** artifacts to the wiki — no exceptions, even on URL-only default run. This skill operates on the vault at the current working directory, same as every other skill in this plugin (`CO_VAULT_ROOT` env var overrides; see `src/claude_obsidian/_vault.py`). Architecture: `.raw/` = immutable source docs, `wiki/` = generated knowledge base.

**Route filing through the `wiki-ingest` skill** — it is purpose-built for ingesting external sources: reads the source, creates/updates wiki pages, extracts entities/concepts, cross-references existing pages, and logs the operation with correct transport (wiki-cli / MCP / filesystem) and methodology-mode paths.

Two artifacts per video, **named by content (not title), filed under a domain subfolder**. Use `<filename>` below = the content-derived name from the "Video title + author" rules:

1. **Raw transcript** — immutable source document. Write to `.raw/youtube/<filename>.md` (frontmatter: `source: youtube`, `youtube_id`, `url`, `author`, `title` [verbatim original], `date_fetched`; body = the joined plaintext). This is the `.raw/` layer the wiki reads from.

2. **Summary** — the derived knowledge note, filed at `wiki/sources/<domain>/<filename>.md` (same `<filename>`), frontmatter: `type: source`, `source: youtube`, `youtube_id`, `url`, `author`, `title` [verbatim original], `date_fetched`, `transcript: "[[<filename>]]"`.

**Domain subfolder** — `wiki/sources/` is split by topic so unrelated content doesn't pile up flat. Pick `<domain>` by content:
- Matches an existing theme already present in this vault (check `wiki/sources/` subfolders and `wiki/index.md`) → use that folder, e.g. a vault with an established `sources/UE/` theme keeps Unreal-Engine videos there.
- Otherwise → `sources/Generic/` (the catch-all default).
- If the user names a domain in the request, use exactly that.
Create the subfolder if it doesn't exist (`sources/Generic/`, etc.).

Workflow per run. **Do all file work first — the chat summary is the LAST thing you output, never interrupted by further tool calls:**

1. Extract ID → fetch verbatim title + author (oEmbed) for frontmatter.
2. **Check if already processed.** Before fetching transcript, search the vault for an existing note with this `youtube_id`:
   - Grep `.raw/youtube/` and `wiki/sources/` for the ID in frontmatter (`youtube_id: <ID>`).
   - If a match exists: the video was already processed. **STOP and ask the user** whether to re-process it anyway (or just re-read/show the existing note). Default = assume no until confirmed.
3. Fetch + clean transcript. Read it.
4. Draft the summary content (TL;DR + bullets + table + remarks) internally — do not print it to chat yet.
5. **Derive `<filename>` from the summary content** (descriptive, unambiguous; see "Video title + author" rules).
6. Pick domain subfolder (default `Generic/`).
7. Write raw transcript to `.raw/youtube/<filename>.md`.
8. Invoke `wiki-ingest` on the raw file with the summary as the synthesized note, target path `wiki/sources/<domain>/<filename>.md`. Let it own transport, frontmatter, cross-refs, index/log/hot.
9. **Only now, once every write above is done**, output one chat message: the full summary (TL;DR + bullets + table + remarks) followed by the landed file paths. This is the single final message for the run — no tool calls after it.

Fallback (if `wiki-ingest` unavailable): write summary to `wiki/sources/<domain>/<filename>.md` and raw to `.raw/youtube/<filename>.md` directly via `Write`, append a line to `wiki/log.md`, cross-link the two with `[[wikilinks]]`. Same rule applies: finish all writes, then output the summary once.

If a save fails, finish whatever writes still succeed, then deliver the summary to chat and report which file(s) failed — still as one final message, not before the save attempt. If the user explicitly says "don't save" / "just tell me", skip wiki save for that run only (summary is then the only step, so ordering is moot).
