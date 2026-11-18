---
name: remotion-video-creator
description: Creates videos from a text brief by writing React code and rendering it to MP4 with Remotion - explainers, product demos, social clips, animated text and charts, captioned videos, templated or data-driven batches. Covers brief, storyboard, pacing checks, a scaffolded storyboard-driven project, per-scene still previews for visual review, rendering, and ffmpeg post-processing (trim, concat, captions, audio, vertical crops, compression). Use when the user asks to make, generate, animate or render a video, motion graphics, a title or lower-third, a slideshow or social media clip with code. Not for filming or editing live footage by hand, or photoreal AI video generation.
---

# Remotion Video Creator

Claude writes the video as React components; Remotion renders it frame by frame to MP4. Because the video is code driven by a storyboard file, changes (text, timing, brand) are quick, repeatable and reviewable.

## Workflow

1. **Brief.** Settle: purpose and audience, length (aim for under 60 to 90 s unless told otherwise), platform and aspect ratio (landscape 1920x1080, portrait 1080x1920, square 1080x1080), tone, brand colours/fonts/logo, assets and their usage rights, voiceover or music, captions yes or no.
2. **Storyboard.** Write `storyboard.json` (format in `scripts/storyboard.py`): a hook in the first 3 s, one idea per scene, 2 to 7 s per scene, at most 5 short bullets, a clear last-scene call to action. Narration at about 150 words per minute.
3. **Validate pacing:** `python scripts/storyboard.py storyboard.json [--assets public]` reports frames per scene, total duration, narration that does not fit its scene, too-short scenes, dense bullets and missing assets. Fix every error and consider every warning.
4. **Scaffold:** `python scripts/scaffold_remotion_project.py my-video --preset landscape|portrait|square --storyboard storyboard.json`, then `cd my-video && npm install`. Scene types out of the box: `title`, `bullets`, `image`; captions come from each scene's `narration`. Remotion is pinned to one exact version across all `remotion` and `@remotion/*` packages; keep them identical when upgrading.
5. **Customise.** Change content by editing `src/storyboard.json`. For a new visual (chart, code block, logo reveal, screen recording) add a scene type to `src/types.ts` and `src/scenes/SceneView.tsx`, keeping all motion frame-driven (see the rules below). Put media under `public/` and reference it relative to that folder.
6. **Look before rendering.** `npm run stills` (or `python scripts/render_stills.py --at all`) writes one PNG per scene to `out/stills/`. **View the images** and fix clipped or overflowing text, low contrast, small type (body text should be at least about 3% of the video width), elements outside the safe margins (about 5 to 8%), and caption collisions. Repeat until clean. The user can also preview motion with `npm run dev` (Remotion Studio).
7. **Render:** `npm run render` writes `out/video.mp4`. Useful flags: `--codec`, `--crf` (lower is higher quality), `--props` (JSON string or file), `--concurrency`, `--scale`, `--muted`; see `npx remotion help render`. Confirm length: `npx remotion ffprobe out/video.mp4` should match the storyboard's total.
8. **Post-process and deliver** with ffmpeg if needed (`references/video-production.md`). Tell the user where the file is, how to re-render, and what to edit to change it. State what you could not check (for example, audio sync or how fonts look on their screen).

## Rules that keep renders correct

- **Everything animates from the frame number.** Use `useCurrentFrame()`, `interpolate`, `spring`. No CSS transitions or animations, no `setTimeout`, no `Date.now()`, no `Math.random()` (use `random('seed')`); Remotion renders frames independently and out of order, so anything time-based will flicker or desync.
- **Frames = seconds x fps.** Inside a `Sequence`/`Series.Sequence`, `useCurrentFrame()` restarts at 0, so write each scene as if it starts at frame 0.
- **Media through Remotion components:** `<Img>`, `<Audio>`, `<OffthreadVideo>` with `staticFile('path')`; plain `<img>` and `<video>` can render before they load or stutter.
- **Fonts:** load them (`@remotion/google-fonts` or a local file with `@remotion/fonts`) so they are ready before the frame is captured.
- **Data:** fetch in `calculateMetadata` (or pass props) rather than inside components, so duration and content are known at render time.
- **Keep text legible:** high contrast, short lines, no more than about 12 words on screen at once, readable for at least as long as it takes to read aloud at about 3 words per second.

## Environment notes

- Needs Node 18+ and enough RAM (about 2 GB per concurrent browser tab); lower `--concurrency` on small machines or containers.
- If Remotion cannot download its own Chrome (offline or locked-down network), point it at an installed Chromium: `--browser-executable=/path/to/chrome` or `REMOTION_BROWSER` for `render_stills.py`.
- Remotion's bundled `npx remotion ffmpeg` is a minimal build (for example no `pad` filter); use a full system ffmpeg for editing recipes.
- Check Remotion's current licence terms for commercial use before delivering to a company client; they differ by company size. Use only fonts, music, footage and images you have the right to use, and say where the user must supply or license assets.

## Voiceover and music

Remotion does not generate speech. Options: the user records it, or any text-to-speech service they are licensed to use produces `public/audio/<scene-id>.mp3`; set `"audio": "audio/<scene-id>.mp3"` on the scene. Measure each file (`ffprobe -v error -show_entries format=duration -of csv=p=0 file.mp3`) and make the scene at least that long plus a short pause. Background music: low volume (about 0.15 to 0.3), fade out at the end (`references/remotion-essentials.md`).

## Files

- `scripts/storyboard.py` - validate a storyboard and report timing
- `scripts/scaffold_remotion_project.py` - generate the project (also copies the two helper scripts into it)
- `scripts/render_stills.py` - per-scene PNGs for visual review
- `references/remotion-essentials.md` - verified code snippets: sequences, easing, springs, seeded randomness, audio/video/images, transitions, fonts, data-driven duration, CLI
- `references/video-production.md` - script, pacing and layout guidance, platform sizes, verified ffmpeg recipes
