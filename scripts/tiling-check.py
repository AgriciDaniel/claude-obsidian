#!/usr/bin/env python3
"""tiling-check.py — DragonScale Mechanism 3: semantic tiling lint.

Computes per-page embeddings via a local ollama instance and reports
candidate duplicate page pairs. Read-only; never modifies wiki pages.

Security model:
- Defaults to http://127.0.0.1:11434. Remote ollama endpoints require
  --allow-remote-ollama explicitly (vault bodies are POSTed as embedding
  input; a hostile env var would otherwise exfiltrate content).
- Rejects symlinked page files to prevent escape outside the vault root.

Feature-gated: exits 10 if ollama is unreachable or 11 if the embedding
model is not pulled, so the calling skill can no-op gracefully. Exits 0
on success. Exit 3 on cache corruption. Exit 2 on usage error.

Concurrency:
- Locks `.vault-meta/.tiling.lock` (flock exclusive) around cache I/O.
- Per-PID temp file to avoid shared-tempfile races.

Usage:
  tiling-check.py                      # run; exit 10/11 if ollama/model missing
  tiling-check.py --report PATH        # also write report to PATH
  tiling-check.py --rebuild-cache      # ignore cached embeddings
  tiling-check.py --peek               # structured diagnostics; no compute
  tiling-check.py --allow-remote-ollama # accept non-localhost OLLAMA_URL
"""

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "nomic-embed-text"
OLLAMA_TIMEOUT_SEC = 3
EMBED_TIMEOUT_SEC = 30
MAX_RESPONSE_BYTES = 4 * 1024 * 1024  # 4 MB; embeddings can be ~10 KB each

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _vault import resolve_vault_or_die

VAULT_ROOT = resolve_vault_or_die()
WIKI_DIR = VAULT_ROOT / "wiki"
META_DIR = VAULT_ROOT / ".vault-meta"
CACHE_PATH = META_DIR / "tiling-cache.json"
CACHE_LOCK = META_DIR / ".tiling.lock"
THRESHOLDS_PATH = META_DIR / "tiling-thresholds.json"

EXCLUDE_TYPES = {"meta", "fold"}
EXCLUDE_FILENAMES = {
    "_index.md", "index.md", "log.md", "hot.md", "overview.md",
    "dashboard.md", "Wiki Map.md", "getting-started.md",
}
EXCLUDE_PATH_PREFIXES = ("wiki/folds/", "wiki/meta/")
MAX_BODY_BYTES = 128 * 1024
SCALE_WARN_PAGES = 500
SCALE_HARD_FAIL_PAGES = 5000

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_CACHE_CORRUPT = 3
EXIT_SCALE_EXCEEDED = 4
EXIT_NO_OLLAMA = 10
EXIT_NO_MODEL = 11

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
TYPE_RE = re.compile(r"^type:\s*(\S+)", re.MULTILINE)


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def _is_local_url(url: str) -> bool:
    try:
        host = urllib.parse.urlparse(url).hostname or ""
    except ValueError:
        return False
    return host in ("127.0.0.1", "localhost", "::1")


def _http_get_json(url: str, timeout: float) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw = resp.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("response exceeded size limit")
    return json.loads(raw.decode("utf-8"))


def _http_post_json(url: str, payload: dict, timeout: float) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("response exceeded size limit")
    return json.loads(raw.decode("utf-8"))


def detect_ollama(url: str) -> bool:
    try:
        _http_get_json(f"{url}/api/version", OLLAMA_TIMEOUT_SEC)
        return True
    except (urllib.error.URLError, OSError, ValueError, TimeoutError, RuntimeError):
        return False


def detect_model(url: str, model: str) -> bool:
    try:
        data = _http_get_json(f"{url}/api/tags", OLLAMA_TIMEOUT_SEC)
    except (urllib.error.URLError, OSError, ValueError, TimeoutError, RuntimeError):
        return False
    models = data.get("models")
    if not isinstance(models, list):
        return False
    for entry in models:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name", "")
        if isinstance(name, str) and (name == model or name.startswith(f"{model}:")):
            return True
    return False


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_raw = m.group(1)
    body = text[m.end():]
    fm: dict = {}
    tm = TYPE_RE.search(fm_raw)
    if tm:
        fm["type"] = tm.group(1).strip().strip('"').strip("'")
    return fm, body


def body_hash(body: str, model: str) -> str:
    h = hashlib.sha256()
    h.update(f"model={model}\n".encode("utf-8"))
    h.update(body.encode("utf-8"))
    return h.hexdigest()


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"dim mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _lock_cache():
    META_DIR.mkdir(exist_ok=True)
    fd = os.open(str(CACHE_LOCK), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
    except OSError:
        os.close(fd)
        raise
    return fd


def _unlock_cache(fd: int) -> None:
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def load_cache(current_model: str) -> dict:
    if not CACHE_PATH.exists():
        return {"version": 1, "model": current_model, "embeddings": {}}
    try:
        with CACHE_PATH.open() as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        log(f"ERR: cache read failed: {exc}")
        sys.exit(EXIT_CACHE_CORRUPT)
    if data.get("version") != 1:
        log(f"ERR: unknown cache version: {data.get('version')}")
        sys.exit(EXIT_CACHE_CORRUPT)
    cached_model = data.get("model", "")
    if cached_model != current_model:
        log(f"INFO: cached model '{cached_model}' differs from current '{current_model}'; invalidating cache")
        return {"version": 1, "model": current_model, "embeddings": {}}
    if not isinstance(data.get("embeddings"), dict):
        log("ERR: cache.embeddings is not a dict")
        sys.exit(EXIT_CACHE_CORRUPT)
    return data


def save_cache(cache: dict) -> None:
    META_DIR.mkdir(exist_ok=True)
    tmp = CACHE_PATH.with_name(f"{CACHE_PATH.stem}.{os.getpid()}.tmp")
    with tmp.open("w") as f:
        json.dump(cache, f, indent=2)
    tmp.replace(CACHE_PATH)


def load_thresholds() -> dict:
    if not THRESHOLDS_PATH.exists():
        return {
            "version": 1, "model": DEFAULT_MODEL,
            "bands": {"error": 0.90, "review": 0.80},
            "calibrated": False, "calibration_pairs_labeled": 0,
        }
    with THRESHOLDS_PATH.open() as f:
        return json.load(f)


def included(path: Path, fm: dict) -> tuple[bool, str]:
    rel = path.relative_to(VAULT_ROOT).as_posix()
    if path.is_symlink():
        return False, "symlink"
    resolved = path.resolve()
    try:
        resolved.relative_to(VAULT_ROOT.resolve())
    except ValueError:
        return False, "escapes vault"
    if path.name in EXCLUDE_FILENAMES:
        return False, "excluded filename"
    for prefix in EXCLUDE_PATH_PREFIXES:
        if rel.startswith(prefix):
            return False, f"under {prefix}"
    if fm.get("type") in EXCLUDE_TYPES:
        return False, f"type={fm['type']}"
    return True, "included"


def embed(text: str, model: str, url: str) -> list[float]:
    data = _http_post_json(
        f"{url}/api/embeddings",
        {"model": model, "prompt": text},
        EMBED_TIMEOUT_SEC,
    )
    emb = data.get("embedding")
    if not isinstance(emb, list) or not emb:
        raise RuntimeError(f"ollama returned no embedding: {str(data)[:200]}")
    for v in emb:
        if not isinstance(v, (int, float)):
            raise RuntimeError("embedding contains non-numeric values")
    return emb


def run_check(
    rebuild: bool,
    report_path: Path | None,
    ollama_url: str,
    model: str,
) -> int:
    if not detect_ollama(ollama_url):
        log(f"ollama not reachable at {ollama_url}; skipping tiling check")
        return EXIT_NO_OLLAMA
    if not detect_model(ollama_url, model):
        log(f"model '{model}' not pulled; run: ollama pull {model}")
        return EXIT_NO_MODEL

    thresholds = load_thresholds()

    lock_fd = _lock_cache()
    try:
        cache = (load_cache(model) if not rebuild
                 else {"version": 1, "model": model, "embeddings": {}})

        pages: list[tuple[str, list[float]]] = []
        scanned = 0
        computed = 0
        cached_hits = 0
        skipped_counts: dict[str, int] = {}
        live_paths: set[str] = set()

        candidates = sorted(WIKI_DIR.rglob("*.md"))
        scale_n = len(candidates)
        if scale_n > SCALE_HARD_FAIL_PAGES:
            log(f"ERR: {scale_n} pages exceed hard-fail limit {SCALE_HARD_FAIL_PAGES}")
            return EXIT_SCALE_EXCEEDED
        if scale_n > SCALE_WARN_PAGES:
            log(f"WARN: {scale_n} pages; cold-cache embed will issue ~{scale_n} POSTs to ollama")

        for md in candidates:
            scanned += 1
            # Symlink and vault-root guards must run BEFORE read_text so a
            # hostile symlink cannot cause off-vault content to be read and
            # POSTed to the embedding endpoint.
            if md.is_symlink():
                skipped_counts["symlink"] = skipped_counts.get("symlink", 0) + 1
                continue
            try:
                resolved = md.resolve(strict=True)
                resolved.relative_to(VAULT_ROOT.resolve())
            except (OSError, ValueError):
                skipped_counts["escapes vault"] = skipped_counts.get("escapes vault", 0) + 1
                continue
            try:
                text = md.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                skipped_counts["read_error"] = skipped_counts.get("read_error", 0) + 1
                continue
            if len(text.encode("utf-8")) > MAX_BODY_BYTES:
                skipped_counts["too_large"] = skipped_counts.get("too_large", 0) + 1
                continue
            fm, body = parse_frontmatter(text)
            ok, reason = included(md, fm)
            if not ok:
                skipped_counts[reason] = skipped_counts.get(reason, 0) + 1
                continue
            rel = md.relative_to(VAULT_ROOT).as_posix()
            live_paths.add(rel)
            h = body_hash(body, model)
            entry = cache["embeddings"].get(rel)
            if entry and entry.get("hash") == h:
                pages.append((rel, entry["embedding"]))
                cached_hits += 1
                continue
            try:
                emb = embed(body, model, ollama_url)
            except Exception as exc:
                log(f"ERR embedding {rel}: {exc}")
                skipped_counts["embed_error"] = skipped_counts.get("embed_error", 0) + 1
                continue
            cache["embeddings"][rel] = {
                "hash": h,
                "embedding": emb,
                "computed_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
            pages.append((rel, emb))
            computed += 1

        # Orphan GC: drop cache entries for paths that no longer exist.
        orphans = [k for k in cache["embeddings"] if k not in live_paths]
        for k in orphans:
            del cache["embeddings"][k]

        save_cache(cache)
    finally:
        _unlock_cache(lock_fd)

    review = thresholds["bands"]["review"]
    error_ = thresholds["bands"]["error"]
    pairs: list[tuple[float, str, str]] = []
    for i in range(len(pages)):
        for j in range(i + 1, len(pages)):
            a_path, a_emb = pages[i]
            b_path, b_emb = pages[j]
            try:
                sim = cosine(a_emb, b_emb)
            except ValueError as exc:
                log(f"WARN cosine skip ({a_path}, {b_path}): {exc}")
                continue
            if sim >= review:
                pairs.append((sim, a_path, b_path))
    pairs.sort(reverse=True)

    errors = [p for p in pairs if p[0] >= error_]
    reviews = [p for p in pairs if review <= p[0] < error_]

    out_lines: list[str] = []
    out_lines.append("# Semantic Tiling Report")
    out_lines.append("")
    out_lines.append(f"- generated: {datetime.utcnow().isoformat(timespec='seconds')}Z")
    out_lines.append(f"- model: {model}")
    out_lines.append(f"- ollama_url: {ollama_url}")
    out_lines.append(f"- thresholds: error>={error_}, review={review}-{error_}")
    out_lines.append(f"- calibrated: {thresholds.get('calibrated', False)}"
                     + (" (using uncalibrated defaults)" if not thresholds.get("calibrated") else ""))
    out_lines.append(f"- pages scanned: {scanned}; embedded: {len(pages)}; skipped: {sum(skipped_counts.values())}")
    if skipped_counts:
        out_lines.append("- skipped reasons: " + ", ".join(f"{k}={v}" for k, v in sorted(skipped_counts.items())))
    out_lines.append(f"- cache hits: {cached_hits}; recomputed: {computed}; orphans pruned: {len(orphans)}")
    out_lines.append("")
    out_lines.append(f"## Errors (similarity >= {error_})")
    out_lines.append("")
    if not errors:
        out_lines.append("- none")
    else:
        for sim, a, b in errors:
            out_lines.append(f"- `{sim:.4f}` {a} -- {b}")
    out_lines.append("")
    out_lines.append(f"## Review ({review} <= similarity < {error_})")
    out_lines.append("")
    if not reviews:
        out_lines.append("- none")
    else:
        for sim, a, b in reviews:
            out_lines.append(f"- `{sim:.4f}` {a} -- {b}")
    report = "\n".join(out_lines) + "\n"

    print(report)
    if report_path is not None:
        # Confine report writes to VAULT_ROOT. A path that resolves outside
        # the vault is refused (prevents `--report /etc/passwd` style
        # accidents or hostile args from writing outside the repo).
        try:
            resolved_report = (
                report_path if report_path.is_absolute() else (Path.cwd() / report_path)
            ).resolve()
            resolved_report.relative_to(VAULT_ROOT.resolve())
        except ValueError:
            log(f"ERR: --report path '{report_path}' escapes vault root {VAULT_ROOT}")
            return EXIT_USAGE
        resolved_report.parent.mkdir(parents=True, exist_ok=True)
        resolved_report.write_text(report, encoding="utf-8")
        log(f"report written: {resolved_report}")

    return EXIT_OK


def cmd_peek(ollama_url: str, model: str) -> int:
    """Structured diagnostics. Prints a JSON object and a plain summary."""
    diag: dict = {}
    script_path = Path(__file__).resolve()
    diag["script_path"] = str(script_path)
    diag["script_executable"] = os.access(script_path, os.X_OK)
    diag["python"] = sys.executable
    diag["vault_root"] = str(VAULT_ROOT)
    diag["ollama_url"] = ollama_url
    diag["ollama_reachable"] = detect_ollama(ollama_url)
    diag["model_requested"] = model
    diag["model_present"] = detect_model(ollama_url, model) if diag["ollama_reachable"] else False
    diag["cache_present"] = CACHE_PATH.exists()
    diag["cache_readable"] = False
    diag["cache_entries"] = 0
    diag["cache_model"] = None
    if diag["cache_present"]:
        try:
            with CACHE_PATH.open() as f:
                c = json.load(f)
            diag["cache_readable"] = (c.get("version") == 1
                                      and isinstance(c.get("embeddings"), dict))
            diag["cache_entries"] = len(c.get("embeddings", {}))
            diag["cache_model"] = c.get("model")
        except (OSError, json.JSONDecodeError) as exc:
            diag["cache_readable"] = False
            diag["cache_error"] = str(exc)
    diag["thresholds_present"] = THRESHOLDS_PATH.exists()
    diag["thresholds_readable"] = False
    if diag["thresholds_present"]:
        try:
            with THRESHOLDS_PATH.open() as f:
                t = json.load(f)
            diag["thresholds_readable"] = True
            diag["thresholds_calibrated"] = bool(t.get("calibrated", False))
            diag["thresholds_bands"] = t.get("bands", {})
        except (OSError, json.JSONDecodeError):
            diag["thresholds_readable"] = False
    print(json.dumps(diag, indent=2))
    if not diag["ollama_reachable"]:
        return EXIT_NO_OLLAMA
    if not diag["model_present"]:
        return EXIT_NO_MODEL
    if diag["cache_present"] and not diag["cache_readable"]:
        return EXIT_CACHE_CORRUPT
    return EXIT_OK


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--report", type=Path, default=None)
    p.add_argument("--rebuild-cache", action="store_true")
    p.add_argument("--peek", action="store_true")
    p.add_argument("--allow-remote-ollama", action="store_true",
                   help="allow OLLAMA_URL env override pointing outside localhost")
    p.add_argument("--model", default=DEFAULT_MODEL)
    args = p.parse_args(argv)

    env_url = os.environ.get("OLLAMA_URL")
    ollama_url = env_url or DEFAULT_OLLAMA_URL
    if env_url and not _is_local_url(ollama_url) and not args.allow_remote_ollama:
        log(f"ERR: OLLAMA_URL={ollama_url!r} is not localhost. "
            f"Vault content would be POSTed to a non-local host. "
            f"Pass --allow-remote-ollama to override.")
        return EXIT_USAGE

    if args.peek:
        return cmd_peek(ollama_url, args.model)
    return run_check(
        rebuild=args.rebuild_cache,
        report_path=args.report,
        ollama_url=ollama_url,
        model=args.model,
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
