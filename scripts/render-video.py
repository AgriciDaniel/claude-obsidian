#!/usr/bin/env python3
"""Build a video from a deck: timed captions, motion, images. ffmpeg only.

Not a replacement for Adobe Express, and not trying to be. It produces the part
that is mechanical: slides held for the right duration, a slow push so the frame
is never static, captions burned in, and diagrams cut in where they exist. You
record voiceover over the top.

Timing comes from the copy. Each slide is held for the time it takes to say its
words at ~178 wpm, which is the pace measured from the competitor videos, with a
floor so short slides do not flash past.

Usage:
    python3 scripts/render-video.py content/<deck> --out /tmp/deck.mp4
    python3 scripts/render-video.py content/<deck> --palette carbon --wpm 170
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
FPS = 30


def words(s):
    return len([w for w in s.replace("|", " ").split() if w.strip()])


def build(deck, out, palette, wpm, size, mode):
    rows = list(csv.DictReader(open(os.path.join(deck, "04-slides.csv"))))
    tmp = tempfile.mkdtemp()

    # render the slides first, reusing the deck renderer so video and carousel
    # never drift apart visually
    frames = os.path.join(tmp, "frames")
    r = subprocess.run([sys.executable, os.path.join(HERE, "render-morph.py"), deck,
                        "--palette", palette, "--size", size, "--out", frames,
                        "--images", "few" if mode == "captions" else "mixed"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"slide render failed:\n{r.stdout}\n{r.stderr}")

    pngs = sorted(f for f in os.listdir(frames) if f.endswith(".png"))
    if not pngs:
        sys.exit("no slides rendered")

    clips = []
    for i, (png, row) in enumerate(zip(pngs, rows), 1):
        # 'captions' uses only the headline and punch, which is what actually
        # appears on screen in these videos. The body is written to be read in a
        # carousel; spoken at 178wpm it pushes a 13-slide deck past two minutes,
        # well outside the 45-90s band that performs.
        spoken = (f"{row.get('headline','')} {row.get('punch','')}" if mode == "captions"
                  else f"{row.get('headline','')} {row.get('body','')} {row.get('punch','')}")
        dur = max(2.4, round(words(spoken) / wpm * 60, 2))
        src = os.path.join(frames, png)
        clip = os.path.join(tmp, f"c{i:02d}.mp4")
        # slow push in. zoompan needs an explicit frame count, and z has to
        # increment per frame or the whole clip renders at a single zoom level.
        n = int(dur * FPS)
        vf = (f"scale={W*2}:{H*2},"
              f"zoompan=z='min(1.0+0.00055*on,1.10)':d={n}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
              f"format=yuv420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", src,
                        "-vf", vf, "-t", str(dur), "-r", str(FPS),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        clip], check=True)
        clips.append(clip)
        print(f"  slide {i:02d}  {dur:>5.1f}s")

    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as fh:
        for c in clips:
            fh.write(f"file '{c}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", out], check=True)

    total = sum(1 for _ in clips)
    dur = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                          "format=duration", "-of", "csv=p=0", out],
                         capture_output=True, text=True).stdout.strip()
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{total} clips -> {out}  ({float(dur):.1f}s)")
    if float(dur) < 45 or float(dur) > 90:
        print("note: 45-90s is the band that performed best in the scrape")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--out")
    ap.add_argument("--palette", default="carbon")
    ap.add_argument("--size", default="9:16")
    ap.add_argument("--wpm", type=float, default=178)
    ap.add_argument("--mode", choices=["captions","full"], default="captions")
    a = ap.parse_args()
    d = a.deck.rstrip("/")
    build(d, a.out or os.path.join(d, "10-video.mp4"), a.palette, a.wpm, a.size, a.mode)


if __name__ == "__main__":
    main()
