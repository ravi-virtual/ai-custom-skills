#!/usr/bin/env python3
"""storyboard.py - validate a video storyboard and report timing/pacing before any rendering.

Usage:
  python storyboard.py storyboard.json [--wpm 150] [--json]

Storyboard format (also what the scaffolded Remotion project reads from src/storyboard.json):
{
  "title": "Product launch",
  "fps": 30, "width": 1920, "height": 1080, "captions": true,
  "theme": {"background": "#0b1020", "text": "#ffffff", "accent": "#4f8cff", "font": "system-ui, sans-serif"},
  "scenes": [
    {"id": "hook", "type": "title", "title": "...", "subtitle": "...", "seconds": 3, "narration": "...", "audio": "audio/hook.mp3"},
    {"id": "points", "type": "bullets", "title": "...", "bullets": ["..."], "seconds": 6},
    {"id": "shot", "type": "image", "src": "images/app.png", "caption": "...", "seconds": 4}
  ]
}
Frames per scene = max(1, round(seconds * fps)) - the same rule the Remotion template uses.
Checks: required fields, unique ids, scene types, durations (0.8s minimum), narration length vs duration
(words / (wpm/60) must fit), bullet count and text length for legibility, missing local assets with --assets DIR.
Exit code 1 if there are errors; warnings do not fail.
"""
import argparse
import json
import os
import re
import sys

SCENE_TYPES = {"title", "bullets", "image"}
REQUIRED = {"title": ["title"], "bullets": ["title", "bullets"], "image": ["src"]}


def frames(seconds, fps):
    return max(1, round(seconds * fps))


def validate(sb, wpm=150, assets=None):
    errors, warnings, rows = [], [], []
    for key in ("fps", "width", "height"):
        if not isinstance(sb.get(key), int) or sb[key] <= 0:
            errors.append(f"'{key}' must be a positive integer")
    scenes = sb.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("'scenes' must be a non-empty list")
        return errors, warnings, rows
    fps = sb.get("fps") if isinstance(sb.get("fps"), int) and sb["fps"] > 0 else 30
    seen, start = set(), 0
    for i, s in enumerate(scenes, 1):
        sid = s.get("id", f"#{i}")
        if sid in seen:
            errors.append(f"scene {sid}: duplicate id")
        seen.add(sid)
        typ = s.get("type")
        if typ not in SCENE_TYPES:
            errors.append(f"scene {sid}: type must be one of {sorted(SCENE_TYPES)} (got {typ!r})")
            continue
        for field in REQUIRED[typ]:
            if not s.get(field):
                errors.append(f"scene {sid}: '{field}' is required for type '{typ}'")
        secs = s.get("seconds")
        if not isinstance(secs, (int, float)) or secs <= 0:
            errors.append(f"scene {sid}: 'seconds' must be a positive number")
            continue
        if secs < 0.8:
            warnings.append(f"scene {sid}: {secs}s is too short to read or register (use 0.8s or more)")
        words = len(re.findall(r"\w+", s.get("narration", "")))
        need = words / (wpm / 60) if words else 0
        if need > secs + 0.25:
            warnings.append(f"scene {sid}: narration needs about {need:.1f}s at {wpm} wpm but the scene lasts {secs}s")
        bullets = s.get("bullets", [])
        if typ == "bullets":
            if len(bullets) > 5:
                warnings.append(f"scene {sid}: {len(bullets)} bullets is a lot; keep to 5 or fewer")
            if any(len(b) > 70 for b in bullets):
                warnings.append(f"scene {sid}: a bullet is over 70 characters; shorten it")
            read = sum(len(re.findall(r"\w+", b)) for b in bullets) / 3.0  # ~3 words/second to read on screen
            if read > secs:
                warnings.append(f"scene {sid}: reading the bullets needs about {read:.1f}s; scene lasts {secs}s")
        if typ == "title" and len(s.get("title", "")) > 60:
            warnings.append(f"scene {sid}: title over 60 characters will wrap on small screens")
        if assets is not None:
            for ref in (s.get("src"), s.get("audio")):
                if ref and not os.path.exists(os.path.join(assets, ref)):
                    errors.append(f"scene {sid}: asset not found: {os.path.join(assets, ref)}")
        n = frames(secs, fps)
        rows.append({"id": sid, "type": typ, "seconds": secs, "frames": n, "start": start, "mid": start + n // 2, "narration_words": words})
        start += n
    total = start
    if rows and total / fps > 180:
        warnings.append(f"total length {total / fps:.0f}s; short-form platforms and attention drop-off favour under 60 to 90s")
    return errors, warnings, rows


def main():
    ap = argparse.ArgumentParser(description="Validate a video storyboard and report timing.")
    ap.add_argument("file")
    ap.add_argument("--wpm", type=int, default=150, help="narration pace, words per minute (default 150)")
    ap.add_argument("--assets", help="directory (usually public/) to check asset paths against")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    try:
        with open(args.file, encoding="utf-8") as fh:
            sb = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: cannot read {args.file}: {exc}", file=sys.stderr)
        return 2
    errors, warnings, rows = validate(sb, args.wpm, args.assets)
    fps = sb.get("fps", 30)
    total = sum(r["frames"] for r in rows)
    if args.json:
        print(json.dumps({"errors": errors, "warnings": warnings, "scenes": rows, "totalFrames": total, "totalSeconds": round(total / fps, 2)}, indent=2))
    else:
        print(f"{sb.get('title', 'Untitled')}: {len(rows)} scene(s), {total} frames, {total / fps:.1f}s at {fps} fps "
              f"({sb.get('width')}x{sb.get('height')})\n")
        print(f"{'scene':<14}{'type':<9}{'sec':>6}{'frames':>8}{'start':>8}{'mid':>7}{'words':>7}")
        for r in rows:
            print(f"{str(r['id']):<14}{r['type']:<9}{r['seconds']:>6}{r['frames']:>8}{r['start']:>8}{r['mid']:>7}{r['narration_words']:>7}")
        for e in errors:
            print("ERROR  ", e)
        for w in warnings:
            print("WARNING", w)
        if not errors and not warnings:
            print("\nNo problems found.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
