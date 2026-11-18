#!/usr/bin/env python3
"""render_stills.py - render one PNG per scene (or several frames per scene) so the layout can be reviewed
by eye before spending time on a full render.

Usage (run from the Remotion project root, or pass --project):
  python scripts/render_stills.py [--project DIR] [--at mid|first|last|all] [--out out/stills]
                                  [--browser-executable PATH] [--scale 0.5]

Frames come from src/storyboard.json with the same rule the video uses (frames = max(1, round(seconds*fps))).
Output files: <out>/<NN>-<scene-id>-<first|mid|last>.png. Open them (or have Claude view them) and fix
overflow, clipped text, low contrast and tiny type before rendering the MP4.
Needs Node deps installed (npm install). Exit code 1 if any still fails to render.
"""
import argparse
import json
import os
import subprocess
import sys


def frames(seconds, fps):
    return max(1, round(seconds * fps))


def main():
    ap = argparse.ArgumentParser(description="Render per-scene stills for visual review.")
    ap.add_argument("--project", default=".")
    ap.add_argument("--at", choices=["mid", "first", "last", "all"], default="mid")
    ap.add_argument("--out", default="out/stills")
    ap.add_argument("--browser-executable", default=os.environ.get("REMOTION_BROWSER"),
                    help="path to Chrome/Chromium (or set REMOTION_BROWSER) instead of Remotion's own download")
    ap.add_argument("--scale", type=float, default=0.5, help="output scale, 0.5 renders faster (default 0.5)")
    args = ap.parse_args()

    sb_path = os.path.join(args.project, "src", "storyboard.json")
    try:
        with open(sb_path, encoding="utf-8") as fh:
            sb = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: cannot read {sb_path}: {exc}", file=sys.stderr)
        return 2

    fps = sb["fps"]
    os.makedirs(os.path.join(args.project, args.out), exist_ok=True)
    wanted = ["first", "mid", "last"] if args.at == "all" else [args.at]
    start, failures, done = 0, 0, []
    for i, scene in enumerate(sb["scenes"], 1):
        n = frames(scene["seconds"], fps)
        # The composition's own frame numbers are global, so offset by the scene start.
        pick = {"first": start + min(n - 1, 8), "mid": start + n // 2, "last": start + n - 1}
        for where in wanted:
            target = os.path.join(args.out, f"{i:02d}-{scene['id']}-{where}.png")
            cmd = ["npx", "remotion", "still", "src/index.ts", "Main", target, f"--frame={pick[where]}", f"--scale={args.scale}"]
            if args.browser_executable:
                cmd.append(f"--browser-executable={args.browser_executable}")
            result = subprocess.run(cmd, cwd=args.project, capture_output=True, text=True)
            if result.returncode != 0:
                failures += 1
                print(f"FAILED {target}\n{(result.stderr or result.stdout)[-600:]}", file=sys.stderr)
            else:
                done.append(os.path.join(args.project, target))
                print(f"ok  {target}  (frame {pick[where]})")
        start += n
    print(f"\n{len(done)} still(s) written to {os.path.join(args.project, args.out)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
