#!/usr/bin/env python3
"""Assemble the final video: character clip + voiceover + diagrams + captions.

The pipeline this fits into:
  1. script                 written here, from the deck's brief
  2. ElevenLabs             audio from the script (see --tts below)
  3. Character Animator     lip-syncs the character to that audio. Manual, but
                            the sync is automatic so it is a short step
  4. this script            everything else

Give it the character export and the audio and it produces the finished file:
diagrams cut in on cue, captions burned in and timed, correct duration, right
aspect ratio.

Cue file (03-video-cues.txt in the deck) says what appears when:

    # start  end   image (relative to the deck's 03-images/)
    12.0     18.5  slide-03.svg
    24.0     31.0  studies/study-01.png

Captions come from a plain text file, one line per caption, timed evenly across
the audio unless a cue file gives explicit timings.

Usage:
    python3 scripts/assemble-video.py content/<deck> \\
        --character char.mov --audio vo.mp3 --out final.mp4
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                          "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0


def rasterise(path, tmp):
    """ffmpeg has no SVG decoder, so any SVG cue is rendered to PNG first."""
    if not path.lower().endswith(".svg"):
        return path
    try:
        import pymupdf
    except ImportError:
        print(f"  cannot rasterise {os.path.basename(path)}: pymupdf missing")
        return None
    out = os.path.join(tmp, os.path.basename(path)[:-4] + ".png")
    d = pymupdf.open(path)
    d[0].get_pixmap(dpi=200).save(out)
    return out


def read_cues(path, imgdir, tmp):
    cues = []
    if not path or not os.path.exists(path):
        return cues
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 2)
        if len(parts) != 3:
            continue
        start, end, img = parts
        full = os.path.join(imgdir, img)
        if os.path.exists(full):
            r = rasterise(full, tmp)
            if r:
                cues.append((float(start), float(end), r))
        else:
            print(f"  cue image missing: {img}")
    return cues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--character", required=True,
                    help="Character Animator export. Transparent .mov keeps the "
                         "alpha; a green-screen file is keyed automatically.")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out")
    ap.add_argument("--bg", default="#E8E9E6")
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--cues")
    ap.add_argument("--subs", help="an .srt or .ass to burn in")
    ap.add_argument("--chroma", metavar="HEX",
                    help="key this colour out of the character clip, e.g. 00FF00")
    a = ap.parse_args()

    deck = a.deck.rstrip("/")
    for f in (a.character, a.audio):
        if not os.path.exists(f):
            sys.exit(f"missing: {f}")
    W, H = (int(x) for x in a.size.split("x"))
    dur = duration(a.audio)
    if dur <= 0:
        sys.exit("could not read audio duration")

    imgdir = os.path.join(deck, "03-images")
    tmp = tempfile.mkdtemp()
    cues = read_cues(a.cues or os.path.join(deck, "03-video-cues.txt"), imgdir, tmp)
    out = a.out or os.path.join(deck, "11-final.mp4")

    # inputs: 0 solid background, 1 character, 2 audio, then one per cue image
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-f", "lavfi", "-i", f"color=c={a.bg}:s={W}x{H}:d={dur}",
           "-stream_loop", "-1", "-i", a.character,
           "-i", a.audio]
    for _, _, img in cues:
        cmd += ["-loop", "1", "-i", img]

    # character sits bottom-centre, roughly two thirds frame height, as in the
    # reference videos
    ch = f"[1:v]scale=-1:{int(H*0.62)}"
    if a.chroma:
        ch += f",chromakey=0x{a.chroma}:0.30:0.10"
    ch += "[ch];"
    chain = ch + f"[0:v][ch]overlay=(W-w)/2:H-h:shortest=0[base];"

    last = "base"
    for i, (start, end, _) in enumerate(cues):
        inp = 3 + i
        tag = f"v{i}"
        # fade the diagram in and out so it does not snap
        chain += (f"[{inp}:v]scale={int(W*0.86)}:-1,"
                  f"fade=t=in:st=0:d=0.35:alpha=1,"
                  f"fade=t=out:st={max(0.4, end-start-0.35):.2f}:d=0.35:alpha=1[{tag}];"
                  f"[{last}][{tag}]overlay=(W-w)/2:{int(H*0.13)}:"
                  f"enable='between(t,{start},{end})'[o{i}];")
        last = f"o{i}"

    if a.subs and os.path.exists(a.subs):
        esc = a.subs.replace(":", r"\:").replace("'", r"\'")
        chain += f"[{last}]subtitles='{esc}'[vout]"
    else:
        chain += f"[{last}]null[vout]"

    cmd += ["-filter_complex", chain, "-map", "[vout]", "-map", "2:a",
            "-t", str(dur), "-r", "30",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out]

    print(f"  audio {dur:.1f}s, {len(cues)} image cues")
    r = subprocess.run(cmd, capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{r.stderr[-1500:]}")
    print(f"  -> {out}  ({duration(out):.1f}s)")


if __name__ == "__main__":
    main()
