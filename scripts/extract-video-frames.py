#!/usr/bin/env python3
"""Pull readable frames out of a video so its script can be analysed.

I can't watch video or transcribe audio. But TikToks almost always burn their
captions in, so sampling frames recovers the spoken script visually.

The trick is only keeping frames where something changed. Sampling one frame a
second on a 60 second video gives 60 images, most of them identical. ffmpeg's
mpdecimate filter drops near-duplicates, so a 60 second video usually collapses
to 15-25 frames: roughly one per caption change.

Also reports pacing, which is a real stylistic variable: duration, caption
count, and seconds per caption.

Usage:
    python3 scripts/extract-video-frames.py path/to/video.mp4
    python3 scripts/extract-video-frames.py <dir>          # every video in it
"""
import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from claude_obsidian.paths import VaultSelectionError, resolve_vault_root


def vault_root() -> Path:
    """Resolve the vault to act on, failing closed when there is none.

    Never derive paths from __file__: under the installed product tree that
    resolves to the plugin directory, and writing there corrupts the install.
    """
    return resolve_vault_root(plugin_root=PLUGIN_ROOT).root

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}


def probe(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", path],
            capture_output=True, text=True, timeout=60).stdout
        d = json.loads(out)
        dur = float(d.get("format", {}).get("duration", 0))
        v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
        return dur, v.get("width"), v.get("height")
    except Exception:
        return 0, None, None


def extract(path, outdir, fps, threshold):
    os.makedirs(outdir, exist_ok=True)
    for old in glob.glob(os.path.join(outdir, "f*.jpg")):
        os.remove(old)
    # sample, then drop near-identical neighbours so only changed frames survive
    vf = f"fps={fps},mpdecimate=hi={threshold}:lo={threshold//2}:frac=0.33"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", vf,
         "-fps_mode", "vfr", "-q:v", "3", os.path.join(outdir, "f%03d.jpg")],
        capture_output=True, timeout=600)
    # -vsync is deprecated in ffmpeg 7+ and stalls; -fps_mode vfr is the replacement
    return sorted(glob.glob(os.path.join(outdir, "f*.jpg")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="a video file, or a directory of them")
    ap.add_argument("--fps", type=float, default=1.0,
                    help="frames sampled per second before dedupe (default 1)")
    ap.add_argument("--threshold", type=int, default=640,
                    help="mpdecimate sensitivity; lower keeps more frames")
    a = ap.parse_args()

    if os.path.isdir(a.target):
        vids = [p for p in sorted(glob.glob(os.path.join(a.target, "**", "*"), recursive=True))
                if os.path.splitext(p)[1].lower() in VIDEO_EXTS]
    else:
        vids = [a.target]
    if not vids:
        sys.exit(f"no video files found in {a.target}")

    for v in vids:
        dur, w, h = probe(v)
        outdir = os.path.splitext(v)[0] + "-frames"
        frames = extract(v, outdir, a.fps, a.threshold)
        name = os.path.basename(v)
        print(f"\n{name}")
        print(f"  {dur:.1f}s  {w}x{h}")
        print(f"  {len(frames)} distinct frames -> {outdir}")
        if frames and dur:
            print(f"  ~{dur/len(frames):.1f}s per caption change")
            # 150 wpm is normal speech; captions usually run 3-6 words
            print(f"  implied pace: ~{len(frames)*4.5/dur*60:.0f} words/min if ~4-5 words per caption")


if __name__ == "__main__":
    main()
