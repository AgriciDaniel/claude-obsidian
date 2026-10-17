"""Pipeline C — transcribe the competitor video corpus.

Writes one JSONL line per video to content/_style-analysis/video-text.jsonl,
mirroring the shape of slide-text.jsonl so downstream tooling treats both the same.
Resumable: already-transcribed post ids are skipped, so it can be stopped and restarted.
"""
import json, sys, time, glob, os
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT/"content/_style-analysis/video-text.jsonl"
MODEL = os.environ.get("WHISPER_MODEL", "small")
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 0

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
