"""Pipeline C — transcribe the competitor video corpus.

Writes one JSONL line per video to content/_style-analysis/video-text.jsonl,
mirroring the shape of slide-text.jsonl so downstream tooling treats both the same.
Resumable: already-transcribed post ids are skipped, so it can be stopped and restarted.
"""
import argparse
import json, sys, time, glob, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT/"content/_style-analysis/video-text.jsonl"
MODEL = os.environ.get("WHISPER_MODEL", "small")


sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from claude_obsidian.paths import VaultSelectionError, resolve_vault_root


def vault_root() -> Path:
    """Resolve the vault to act on, failing closed when there is none.

    Never derive paths from __file__: under the installed product tree that
    resolves to the plugin directory, so writing there corrupts the install.
    """
    return resolve_vault_root(plugin_root=PLUGIN_ROOT).root


WhisperModel = None


def require_deps():
    """Import the optional dependency on demand, so --help needs no install."""
    global WhisperModel
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("needs faster-whisper: pip install faster-whisper")


if __name__ == "__main__":
    _parser = argparse.ArgumentParser(
        description="Pipeline C — transcribe the competitor video corpus"
    )
    _parser.add_argument(
        "limit", nargs="?", type=int, default=0,
        help="stop after this many videos (0 = no limit)",
    )
    LIMIT = _parser.parse_args().limit
    require_deps()

    vids = sorted(glob.glob(str(ROOT/"content/_style-analysis/tiktok/*/*/*.mp4")))
    done = set()
    if OUT.exists():
        for line in OUT.open():
            try: done.add(json.loads(line)["video"])
            except Exception: pass
    todo = [v for v in vids if Path(v).stem not in done]
    if LIMIT: todo = todo[:LIMIT]
    print(f"{len(vids)} videos · {len(done)} already done · {len(todo)} to run · model={MODEL}", flush=True)

    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    t0 = time.time(); audio_s = 0.0
    with OUT.open("a") as fh:
        for i, v in enumerate(todo, 1):
            p = Path(v)
            acct, post = p.parent.parent.name, p.parent.name
            try:
                segs, info = model.transcribe(v, beam_size=1, vad_filter=True,
                                              condition_on_previous_text=False)
                text = " ".join(s.text.strip() for s in segs).strip()
                audio_s += info.duration
                fh.write(json.dumps({"acct": acct, "post": post, "video": p.stem,
                                     "lang": info.language, "dur": round(info.duration,1),
                                     "text": text}, ensure_ascii=False) + "\n")
                fh.flush()
            except Exception as e:
                fh.write(json.dumps({"acct": acct, "post": post, "video": p.stem,
                                     "error": str(e)[:200]}) + "\n"); fh.flush()
            if i % 10 == 0 or i == len(todo):
                el = time.time()-t0
                rt = audio_s/el if el else 0
                rem = (len(todo)-i) * (el/i) if i else 0
                print(f"  {i}/{len(todo)}  {el/60:.1f}min elapsed  {rt:.1f}x realtime  ~{rem/60:.0f}min left",
                      flush=True)
    print(f"done: {len(todo)} videos in {(time.time()-t0)/60:.1f} min -> {OUT}")
