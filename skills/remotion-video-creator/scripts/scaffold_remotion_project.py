#!/usr/bin/env python3
"""scaffold_remotion_project.py - create a storyboard-driven Remotion (React) video project.

Usage:
  python scaffold_remotion_project.py my-video [--preset landscape|portrait|square] [--fps 30]
                                      [--storyboard story.json] [--force]

Creates my-video/ with: package.json (Remotion pinned to one exact version), tsconfig.json,
remotion.config.ts, src/{index,Root,Video,timing,types,theme}.ts(x), src/scenes/*, src/storyboard.json,
public/, README.md. The video is driven entirely by src/storyboard.json: edit the storyboard, not the code,
to change text, timing and order. Scene types: title, bullets, image.

Then: cd my-video && npm install && npm run dev        (Remotion Studio preview)
      npm run still -- --frame=45  /  npm run render     (PNG / MP4 into out/)
Standard library only.
"""
import argparse
import json
import os
import shutil
import sys
import textwrap

REMOTION_VERSION = "4.0.544"   # all remotion / @remotion/* packages must share one exact version; bump them together
PRESETS = {"landscape": (1920, 1080), "portrait": (1080, 1920), "square": (1080, 1080)}
dedent = lambda t: textwrap.dedent(t).lstrip("\n")  # noqa: E731


def sample_storyboard(title, fps, width, height):
    return {
        "title": title, "fps": fps, "width": width, "height": height, "captions": True,
        "theme": {"background": "#0b1020", "text": "#ffffff", "accent": "#4f8cff", "font": "system-ui, -apple-system, 'Segoe UI', sans-serif"},
        "scenes": [
            {"id": "hook", "type": "title", "title": "Ship faster with Acme", "subtitle": "The 60-second tour", "seconds": 3,
             "narration": "Meet Acme, the fastest way to ship."},
            {"id": "points", "type": "bullets", "title": "Why teams switch",
             "bullets": ["One-click deploys", "A preview for every pull request", "Rollbacks in seconds"], "seconds": 7,
             "narration": "Teams switch because deploys take one click, every pull request gets a preview, and rollbacks take seconds."},
            {"id": "cta", "type": "title", "title": "Try it free", "subtitle": "acme.example", "seconds": 3},
        ],
    }


FILES = {
"package.json": lambda name: json.dumps({
    "name": name, "version": "0.1.0", "private": True, "type": "module",
    "scripts": {
        "dev": "remotion studio src/index.ts",
        "still": "remotion still src/index.ts Main out/still.png",
        "render": "remotion render src/index.ts Main out/video.mp4",
        "typecheck": "tsc -p .",
        "validate": "python3 scripts/storyboard.py src/storyboard.json --assets public",
        "stills": "python3 scripts/render_stills.py",
    },
    "dependencies": {"remotion": REMOTION_VERSION, "@remotion/cli": REMOTION_VERSION, "react": "^19.0.0", "react-dom": "^19.0.0"},
    "devDependencies": {"typescript": "^5.5.0", "@types/react": "^19.0.0"},
}, indent=2) + "\n",

"tsconfig.json": lambda name: dedent('''
    {
      "compilerOptions": {
        "target": "ES2022",
        "module": "ESNext",
        "moduleResolution": "Bundler",
        "jsx": "react-jsx",
        "strict": true,
        "noEmit": true,
        "skipLibCheck": true,
        "resolveJsonModule": true,
        "lib": ["ES2022", "DOM"]
      },
      "include": ["src", "remotion.config.ts"]
    }
'''),

"remotion.config.ts": lambda name: dedent('''
    import { Config } from '@remotion/cli/config';

    Config.setOverwriteOutput(true);
    // Low-RAM or container machines: Config.setConcurrency(2);
    // Use an existing Chrome/Chromium instead of downloading one: pass --browser-executable=/path/to/chrome
'''),

".gitignore": lambda name: "node_modules/\nout/\n.DS_Store\n",

"src/index.ts": lambda name: dedent('''
    import { registerRoot } from 'remotion';
    import { Root } from './Root';

    registerRoot(Root);
'''),

"src/types.ts": lambda name: dedent('''
    export type Theme = { background: string; text: string; accent: string; font: string };

    type Base = { id: string; seconds: number; narration?: string; audio?: string };
    export type TitleScene = Base & { type: 'title'; title: string; subtitle?: string };
    export type BulletsScene = Base & { type: 'bullets'; title: string; bullets: string[] };
    export type ImageScene = Base & { type: 'image'; src: string; caption?: string };
    export type Scene = TitleScene | BulletsScene | ImageScene;

    export type Storyboard = {
      title: string;
      fps: number;
      width: number;
      height: number;
      captions?: boolean;
      theme: Theme;
      scenes: Scene[];
    };
'''),

"src/timing.ts": lambda name: dedent('''
    import type { Scene, Storyboard } from './types';

    // Same rule as scripts/storyboard.py: frames = max(1, round(seconds * fps)).
    export const sceneFrames = (scene: Scene, fps: number): number => Math.max(1, Math.round(scene.seconds * fps));

    export const totalFrames = (sb: Storyboard): number =>
      sb.scenes.reduce((sum, scene) => sum + sceneFrames(scene, sb.fps), 0);
'''),

"src/Root.tsx": lambda name: dedent('''
    import { Composition, type CalculateMetadataFunction } from 'remotion';
    import storyboardJson from './storyboard.json';
    import { totalFrames } from './timing';
    import type { Storyboard } from './types';
    import { Video, type VideoProps } from './Video';

    const storyboard = storyboardJson as Storyboard;

    // Duration and size come from the storyboard, so editing the JSON is enough.
    const calculateMetadata: CalculateMetadataFunction<VideoProps> = ({ props }) => ({
      durationInFrames: totalFrames(props.storyboard),
      fps: props.storyboard.fps,
      width: props.storyboard.width,
      height: props.storyboard.height,
    });

    export const Root = () => (
      <Composition
        id="Main"
        component={Video}
        durationInFrames={totalFrames(storyboard)}
        fps={storyboard.fps}
        width={storyboard.width}
        height={storyboard.height}
        defaultProps={{ storyboard }}
        calculateMetadata={calculateMetadata}
      />
    );
'''),

"src/Video.tsx": lambda name: dedent('''
    import { AbsoluteFill, Audio, Series, staticFile } from 'remotion';
    import { Caption } from './scenes/Caption';
    import { SceneView } from './scenes/SceneView';
    import { sceneFrames } from './timing';
    import type { Storyboard } from './types';

    export type VideoProps = { storyboard: Storyboard };

    export const Video = ({ storyboard }: VideoProps) => (
      <AbsoluteFill style={{ backgroundColor: storyboard.theme.background }}>
        <Series>
          {storyboard.scenes.map((scene) => (
            <Series.Sequence key={scene.id} durationInFrames={sceneFrames(scene, storyboard.fps)}>
              <SceneView scene={scene} theme={storyboard.theme} />
              {scene.audio ? <Audio src={staticFile(scene.audio)} /> : null}
              {storyboard.captions && scene.narration ? <Caption text={scene.narration} theme={storyboard.theme} /> : null}
            </Series.Sequence>
          ))}
        </Series>
      </AbsoluteFill>
    );
'''),

"src/scenes/anim.ts": lambda name: dedent('''
    import { interpolate, spring } from 'remotion';

    // All animation is driven by the frame number (never CSS transitions) so renders are deterministic.
    export const fadeIn = (frame: number, delay = 0, duration = 15): number =>
      interpolate(frame - delay, [0, duration], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

    export const popIn = (frame: number, fps: number, delay = 0): number =>
      spring({ frame: frame - delay, fps, config: { damping: 200 } });
'''),

"src/scenes/SceneView.tsx": lambda name: dedent('''
    import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
    import type { BulletsScene, ImageScene, Scene, Theme, TitleScene } from '../types';
    import { fadeIn, popIn } from './anim';

    const Title = ({ scene, theme }: { scene: TitleScene; theme: Theme }) => {
      const frame = useCurrentFrame();
      const { fps, width } = useVideoConfig();
      const size = Math.round(width * 0.06);
      return (
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: '8%', textAlign: 'center', fontFamily: theme.font }}>
          <h1 style={{ color: theme.text, fontSize: size, margin: 0, transform: `scale(${popIn(frame, fps)})`, opacity: fadeIn(frame) }}>
            {scene.title}
          </h1>
          {scene.subtitle ? (
            <p style={{ color: theme.accent, fontSize: size * 0.45, marginTop: size * 0.3, opacity: fadeIn(frame, 10) }}>{scene.subtitle}</p>
          ) : null}
        </AbsoluteFill>
      );
    };

    const Bullets = ({ scene, theme }: { scene: BulletsScene; theme: Theme }) => {
      const frame = useCurrentFrame();
      const { width } = useVideoConfig();
      const size = Math.round(width * 0.03);
      return (
        <AbsoluteFill style={{ justifyContent: 'center', padding: '8%', fontFamily: theme.font }}>
          <h2 style={{ color: theme.text, fontSize: size * 1.6, margin: 0, opacity: fadeIn(frame) }}>{scene.title}</h2>
          <ul style={{ color: theme.text, fontSize: size, lineHeight: 1.5, marginTop: size, paddingLeft: size, listStyle: 'none' }}>
            {scene.bullets.map((b, i) => (
              <li key={b} style={{ opacity: fadeIn(frame, 12 + i * 12), transform: `translateX(${(1 - fadeIn(frame, 12 + i * 12)) * 40}px)` }}>
                <span style={{ color: theme.accent }}>{'\\u25CF'} </span>
                {b}
              </li>
            ))}
          </ul>
        </AbsoluteFill>
      );
    };

    const ImageView = ({ scene, theme }: { scene: ImageScene; theme: Theme }) => {
      const frame = useCurrentFrame();
      const { durationInFrames, width } = useVideoConfig();
      const zoom = 1 + (frame / durationInFrames) * 0.06;      // slow push-in keeps a still image alive
      return (
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', fontFamily: theme.font }}>
          <Img src={staticFile(scene.src)} style={{ maxWidth: '84%', maxHeight: '78%', objectFit: 'contain', transform: `scale(${zoom})` }} />
          {scene.caption ? (
            <p style={{ position: 'absolute', top: '4%', color: theme.text, fontSize: Math.round(width * 0.025), opacity: fadeIn(frame) }}>{scene.caption}</p>
          ) : null}
        </AbsoluteFill>
      );
    };

    export const SceneView = ({ scene, theme }: { scene: Scene; theme: Theme }) => {
      switch (scene.type) {
        case 'title':
          return <Title scene={scene} theme={theme} />;
        case 'bullets':
          return <Bullets scene={scene} theme={theme} />;
        case 'image':
          return <ImageView scene={scene} theme={theme} />;
      }
    };
'''),

"src/scenes/Caption.tsx": lambda name: dedent('''
    import { AbsoluteFill, useVideoConfig } from 'remotion';
    import type { Theme } from '../types';

    // Burned-in caption in the bottom safe area (kept clear of platform UI overlays).
    export const Caption = ({ text, theme }: { text: string; theme: Theme }) => {
      const { width } = useVideoConfig();
      return (
        <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: '7%' }}>
          <div style={{ maxWidth: '80%', textAlign: 'center', fontFamily: theme.font, fontSize: Math.round(width * 0.022), color: '#fff',
                        background: 'rgba(0,0,0,0.55)', padding: '0.4em 0.8em', borderRadius: 12 }}>
            {text}
          </div>
        </AbsoluteFill>
      );
    };
'''),

"public/.gitkeep": lambda name: "",
}


README = '''# {title}

Storyboard-driven video built with [Remotion](https://www.remotion.dev). Edit `src/storyboard.json` (text, order, seconds, theme); the code reads it.

```bash
npm install
npm run dev                     # Remotion Studio: live preview
npm run validate                # pacing and asset checks (needs python3)
npm run stills                  # one PNG per scene -> out/stills/ (review before rendering)
npm run still -- --frame=45     # PNG of one frame -> out/still.png
npm run render                  # MP4 -> out/video.mp4
```

Assets (images, audio, fonts) go in `public/` and are referenced relative to it, e.g. `"src": "images/app.png"`. Only use media you have the rights to use.
Remotion packages must all use the same exact version (see `package.json`). Check Remotion's licence terms for your use before commercial work.
'''


def main():
    ap = argparse.ArgumentParser(description="Scaffold a storyboard-driven Remotion project.")
    ap.add_argument("name")
    ap.add_argument("--preset", choices=sorted(PRESETS), default="landscape")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--storyboard", help="use this storyboard JSON instead of the sample")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if os.path.isdir(args.name) and os.listdir(args.name) and not args.force:
        print(f"Error: {args.name} is not empty (use --force).", file=sys.stderr)
        return 1
    width, height = PRESETS[args.preset]
    if args.storyboard:
        with open(args.storyboard, encoding="utf-8") as fh:
            storyboard = json.load(fh)
    else:
        storyboard = sample_storyboard(args.name, args.fps, width, height)

    for rel, make in FILES.items():
        path = os.path.join(args.name, rel)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(make(args.name))
    with open(os.path.join(args.name, "src", "storyboard.json"), "w", encoding="utf-8") as fh:
        json.dump(storyboard, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    # Ship the helper scripts inside the project so it stays usable without the skill folder.
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(args.name, "scripts"), exist_ok=True)
    for helper in ("storyboard.py", "render_stills.py"):
        shutil.copy(os.path.join(here, helper), os.path.join(args.name, "scripts", helper))
    with open(os.path.join(args.name, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(README.format(title=storyboard.get("title", args.name)))
    print(f"Created {args.name}/ ({args.preset} {width}x{height} @ {args.fps}fps, Remotion {REMOTION_VERSION})")
    print(f"Next: cd {args.name} && npm install && npm run dev")
    return 0


if __name__ == "__main__":
    sys.exit(main())
