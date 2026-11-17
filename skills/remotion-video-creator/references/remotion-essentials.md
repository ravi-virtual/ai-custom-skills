# Remotion Essentials

Snippets below were compile-checked (TypeScript strict) against Remotion 4.0.544 with `@remotion/transitions` and `@remotion/google-fonts` at the same version.

## Contents
- [Sequence and Series](#sequence-and-series)
- [Interpolate, easing, spring](#interpolate-easing-spring)
- [Deterministic randomness](#deterministic-randomness)
- [Audio, images, video](#audio-images-video)
- [Transitions](#transitions)
- [Fonts](#fonts)
- [Props and data-driven duration](#props-and-data-driven-duration)
- [CLI](#cli)
- [Troubleshooting](#troubleshooting)

Common imports: `import { AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, Series, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';`

## Sequence and Series

```tsx
<AbsoluteFill>
  <Sequence from={0} durationInFrames={60}><Intro /></Sequence>
  <Sequence from={45} durationInFrames={90} layout="none"><Overlay /></Sequence>   {/* overlaps the first */}
</AbsoluteFill>

<Series>                                                   {/* back to back, no manual offsets */}
  <Series.Sequence durationInFrames={60}><Intro /></Series.Sequence>
  <Series.Sequence durationInFrames={60} offset={-10}><Overlay /></Series.Sequence>   {/* starts 10 frames early */}
</Series>
```

Inside a sequence `useCurrentFrame()` starts at 0. `useVideoConfig()` returns `{ fps, width, height, durationInFrames }` (the composition's, not the sequence's).

## Interpolate, easing, spring

```tsx
const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const x = interpolate(frame, [0, 30], [-200, 0], { easing: Easing.out(Easing.cubic), extrapolateRight: 'clamp' });
const progress = interpolate(frame, [0, 90], [0, 100], { extrapolateRight: 'clamp' });  // clamp or values run past the range
const pop = spring({ frame: frame - 10, fps, config: { damping: 12, stiffness: 120 } });  // delay by subtracting frames
// damping 200 = no bounce (smooth settle); lower damping = bouncier
```

Stagger lists by delaying each item (`frame - i * 8`). Prefer short entrances (10 to 20 frames) so text is readable early.

## Deterministic randomness

```tsx
const dots = Array.from({ length: 20 }, (_, i) => ({ x: random(`x-${i}`) * 100, y: random(`y-${i}`) * 100 }));
```

`Math.random()` changes on every frame render and breaks the video; `random('seed')` returns the same value every time.

## Audio, images, video

```tsx
const { durationInFrames } = useVideoConfig();
<Audio src={staticFile('audio/music.mp3')} startFrom={30}
       volume={(f) => interpolate(f, [durationInFrames - 30, durationInFrames], [0.3, 0], { extrapolateLeft: 'clamp' })} />
<Img src={staticFile('images/logo.png')} style={{ width: 200 }} />
<OffthreadVideo src={staticFile('clips/demo.mp4')} muted startFrom={60} endAt={180} />
```

Files live in `public/`; `staticFile('x/y.png')` refers to `public/x/y.png`. Put `<Audio>` inside the `Sequence` where it should start. Remote URLs work for `src` but can fail or change; download assets you depend on.

## Transitions

```tsx
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { slide } from '@remotion/transitions/slide';

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}><Intro /></TransitionSeries.Sequence>
  <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
  <TransitionSeries.Sequence durationInFrames={90}><Overlay /></TransitionSeries.Sequence>
  <TransitionSeries.Transition presentation={slide({ direction: 'from-right' })} timing={linearTiming({ durationInFrames: 20 })} />
  <TransitionSeries.Sequence durationInFrames={90}><Intro /></TransitionSeries.Sequence>
</TransitionSeries>
```

A transition overlaps its neighbours, so the total length is the sum of sequence durations minus the sum of transition durations. Update the composition's `durationInFrames` accordingly (the scaffold's `timing.ts` is the place).

## Fonts

```tsx
import { loadFont } from '@remotion/google-fonts/Inter';
const { fontFamily } = loadFont();     // then style={{ fontFamily }}
```

Install with `npm i @remotion/google-fonts@<same version as remotion>`. For local files use `@remotion/fonts`.

## Props and data-driven duration

```tsx
type Props = { items: string[] };       // use a type alias, not an interface
const calc: CalculateMetadataFunction<Props> = async ({ props }) => ({
  durationInFrames: Math.max(1, props.items.length) * 60,   // may await fetch() for remote data
});
<Composition id="Report" component={Report} durationInFrames={60} fps={30} width={1080} height={1920}
             defaultProps={{ items: ['a', 'b'] }} calculateMetadata={calc} />
```

Render variations without code changes: `npx remotion render src/index.ts Report out/a.mp4 --props='{"items":["x","y","z"]}'` (or a path to a JSON file). Loop over a list of props in a shell or Node script for batches (personalised videos, one per row of a CSV).

## CLI

```bash
npx remotion studio src/index.ts                       # live preview
npx remotion compositions src/index.ts                 # list ids, fps, size, duration
npx remotion still src/index.ts Main out/f.png --frame=45
npx remotion render src/index.ts Main out/video.mp4    # H.264 MP4 by default
npx remotion render src/index.ts Main out/clip.gif --codec=gif --every-nth-frame=2
npx remotion render src/index.ts Main out/v.mp4 --concurrency=2 --crf=20 --browser-executable=/path/to/chrome
npx remotion ffprobe out/video.mp4                     # inspect the result
```

Run `npx remotion help render` for the full flag list of your installed version.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Flickering or jumping animation | CSS transition/animation, `Math.random`, `Date`, or state set in effects | Drive everything from `useCurrentFrame` |
| Image/font missing in a frame | Plain `<img>`/unloaded font | `<Img>` + `staticFile`; `loadFont()` |
| Render shows a different length than planned | Transitions overlap, or `durationInFrames` not updated | Recompute with the overlap; use `calculateMetadata` |
| "Cannot find module" for an `@remotion/*` package | Version mismatch between remotion packages | Same exact version for all; reinstall |
| Chrome download fails | Restricted network | `--browser-executable=/path/to/chrome` |
| Out of memory or very slow render | Too much concurrency/high resolution | `--concurrency=2`, `--scale=0.5` for drafts |
| Type error on `defaultProps` | Props declared as `interface` | Use a `type` alias |
