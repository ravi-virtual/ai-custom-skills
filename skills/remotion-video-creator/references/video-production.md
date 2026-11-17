# Video Production Guide

## Contents
- [Script and structure](#script-and-structure)
- [Pacing](#pacing)
- [Layout and typography](#layout-and-typography)
- [Platform sizes](#platform-sizes)
- [Audio](#audio)
- [ffmpeg recipes](#ffmpeg-recipes)

## Script and structure

- **Hook (0 to 3 s):** the result or the problem, in one line. No logo animation first.
- **Body:** one idea per scene, in the order the viewer needs it (problem, how it works, proof, result).
- **Close:** one call to action only, held long enough to read (3 s or more).
- Write narration as it will be spoken: short sentences, plain words, numbers rounded.
- Show, do not just tell: when a sentence names a thing, put that thing on screen.

## Pacing

| Element | Guide |
|---|---|
| Narration speed | 140 to 160 words per minute (about 2.5 words per second) |
| Scene length | 2 to 7 s; under 0.8 s cannot be read |
| On-screen text | Readable at about 3 words per second; at most 12 words visible at once |
| Entrance animation | 10 to 20 frames; leave the text static after it lands |
| Total length | Social: 15 to 60 s; explainers: 60 to 120 s; longer needs a reason |

`python scripts/storyboard.py` checks these automatically.

## Layout and typography

- Safe margins: keep important content 5 to 8% in from every edge; for vertical video leave the bottom 15% and top 10% free of key text (platform UI overlays).
- Type size: titles about 6% of the video width, body about 3% (86 px and 58 px at 1920 wide). Weight 600 or higher for titles.
- Contrast: light text on dark (or reverse) with at least a 4.5:1 ratio; add a translucent panel behind captions.
- Limit to one or two typefaces and a three-colour palette (background, text, accent). Align to a grid; use consistent spacing.
- Captions: burned-in captions help silent autoplay; keep to two lines, about 40 characters per line.

## Platform sizes

| Use | Size | Aspect |
|---|---|---|
| YouTube, web, presentations | 1920x1080 (or 3840x2160) | 16:9 |
| Reels, Shorts, TikTok, Stories | 1080x1920 | 9:16 |
| Feed posts | 1080x1080 or 1080x1350 | 1:1 or 4:5 |

Use 30 fps for most work; 60 fps only for fast motion; 24 fps for a filmic feel. Rendering at `--scale=0.5` makes quick drafts.

## Audio

- Voiceover is the priority: music at roughly 15 to 30% volume under speech and fading out at the end.
- Target about -16 LUFS integrated loudness for web/social, true peak at or below -1.5 dB (see the loudnorm recipe).
- Leave 0.3 to 0.5 s of silence before the first word and after the last.
- Use only licensed or original music, sounds and voices.

## ffmpeg recipes

All verified on a full ffmpeg build (Remotion's bundled ffmpeg is minimal and lacks some filters such as `pad`). Replace file names as needed.

```bash
# Trim 1s to 4s (re-encode for exact cut points)
ffmpeg -ss 00:00:01 -to 00:00:04 -i in.mp4 -c:v libx264 -c:a aac trim.mp4

# Join clips with the same codec/size/fps (list.txt lines:  file 'a.mp4')
ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4

# Extract audio
ffmpeg -i in.mp4 -vn -c:a libmp3lame -q:a 2 audio.mp3

# Add or replace the audio track (video stream copied)
ffmpeg -i silent.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest out.mp4

# Burn in subtitles from an .srt file
ffmpeg -i in.mp4 -vf "subtitles=subs.srt" -c:a copy out.mp4

# Compress for sharing (lower crf = better quality, bigger file)
ffmpeg -i in.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k small.mp4

# Thumbnail at 2 s
ffmpeg -ss 00:00:02 -i in.mp4 -frames:v 1 thumb.png

# Fit landscape into 9:16 with bars (1080x1920)
ffmpeg -i in.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:a copy vertical.mp4

# Centre-crop to a square
ffmpeg -i in.mp4 -vf "crop=ih:ih" square.mp4

# Normalise loudness
ffmpeg -i in.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy loud.mp4

# Lower volume by 6 dB
ffmpeg -i in.mp4 -af "volume=-6dB" -c:v copy quiet.mp4

# Speed up 1.25x (picture and sound)
ffmpeg -i in.mp4 -vf "setpts=PTS/1.25" -af "atempo=1.25" fast.mp4

# GIF (12 fps, 480 px wide, first 3 s)
ffmpeg -i in.mp4 -vf "fps=12,scale=480:-1:flags=lanczos" -t 3 out.gif
```
