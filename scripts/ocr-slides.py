#!/usr/bin/env python3
"""Transcribe competitor slides using macOS Vision. Local, free, no API tokens.

The scrape holds 2,232 slide images. Reading them with a vision model would
cost roughly 2.7M tokens. macOS has an OCR engine built into Vision.framework,
so this does the same job locally for nothing, and the resulting text corpus can
then be analysed at scale.

Vision returns detections unordered, so results are sorted top-to-bottom then
left-to-right to recover reading order. Without that the output is a bag of
words.

Usage:
    python3 scripts/ocr-slides.py content/_style-analysis/tiktok --out /tmp/slides.jsonl
    python3 scripts/ocr-slides.py <dir> --limit 200
"""
import argparse
import glob
import json
import os
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

Vision = None
Quartz = None
NSURL = None


def require_deps():
    """Import the optional dependencies on demand.

    Kept out of module scope so that --help, and any other argument parsing,
    works on a machine where these are not installed.
    """
    global Vision, Quartz, NSURL
    try:
        import Vision
        import Quartz
        from Foundation import NSURL
    except ImportError:
        sys.exit('needs pyobjc: .venv/bin/pip install pyobjc-framework-Vision')


def ocr(path):
    url = NSURL.fileURLWithPath_(path)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    if src is None:
        return ""
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    if img is None:
        return ""
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(1)          # 1 = accurate
    req.setUsesLanguageCorrection_(True)
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    ok, _ = handler.performRequests_error_([req], None)
    if not ok:
        return ""
    lines = []
    for r in req.results() or []:
        cands = r.topCandidates_(1)
        if not cands:
            continue
        bb = r.boundingBox()
        # Vision's origin is bottom-left, so 1 - y sorts top-to-bottom
        lines.append((round(1 - bb.origin.y, 3), round(bb.origin.x, 3),
                      cands[0].string()))
    lines.sort()
    # merge fragments that sit on the same visual line
    out, cur_y, buf = [], None, []
    for y, x, txt in lines:
        if cur_y is not None and abs(y - cur_y) < 0.012:
            buf.append(txt)
        else:
            if buf:
                out.append(" ".join(buf))
            buf, cur_y = [txt], y
    if buf:
        out.append(" ".join(buf))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", default="/tmp/slides.jsonl")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    require_deps()

    imgs = sorted(glob.glob(os.path.join(a.root, "*", "*", "*.jpg")))
    if a.limit:
        imgs = imgs[:a.limit]
    if not imgs:
        sys.exit(f"no images under {a.root}")

    done = 0
    with open(a.out, "w") as fh:
        for p in imgs:
            parts = p.split(os.sep)
            rec = {"acct": parts[-3], "post": parts[-2],
                   "slide": os.path.basename(p).split("_")[0],
                   "text": ocr(p)}
            fh.write(json.dumps(rec) + "\n")
            done += 1
            if done % 200 == 0:
                print(f"  {done}/{len(imgs)}", flush=True)
    print(f"\n{done} slides transcribed -> {a.out}")


if __name__ == "__main__":
    main()
