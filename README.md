# ASCII Christmas Tree

A rotating 3D Christmas tree drawn entirely with colored ASCII characters, rendered in
real time with Python and [pygame-ce](https://pyga.me/). Snow falls in front of and
behind the tree, a star lights up at the top, and a pixel-art greeting builds itself
letter by letter.

![ASCII Christmas Tree preview](docs/preview.png)

## What you get

- A procedural spruce built from ~11,500 particles: needles, trunk, garland, baubles,
  fairy lights, gift boxes, and a star topper.
- Real 3D: the tree rotates on the Y axis with perspective projection, a per-cell
  z-buffer, and depth shading, so nearer branches are brighter and correctly cover
  farther ones.
- A timeline instead of a static scene: the trunk appears first, then branches grow,
  the garland wraps around, ornaments and lights switch on, gifts drop in, the star
  flashes, and the greeting types itself out.
- Two layers of falling snow, twinkling background stars, and a bitmap banner that
  spells **MERRY CHRISTMAS 2026**.
- Locked 30 FPS, an 88 × 74 character grid, and no external assets beyond the bundled
  monospace font.

## Controls

| Key | Action |
| --- | --- |
| `Space` | Pause / resume |
| `R` | Restart the animation |
| `S` | Save a screenshot (desktop build only) |
| `D` | Toggle debug readouts |
| `Esc` | Quit |

## Run it on your computer

Python 3.12 or newer is required.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install pygame-ce numpy
python web/main.py
```

On macOS or Linux use `source .venv/bin/activate` instead. Optional flags:

```bash
python web/main.py --seed 8412 --fps 60
```

`--seed` changes the random layout (the same seed always produces the same tree), and
`--fps` changes the frame cap. Both flags are ignored in the browser build.

## Run it in the browser

The web version is built with [pygbag](https://pygame-web.github.io/), which compiles
the Python source to WebAssembly.

```bash
pip install pygbag
python tools/build_web.py
```

The script runs pygbag and copies the generated site into `public/`. Serve it locally
with:

```bash
python -m http.server 8000 --directory public
```

Then open <http://localhost:8000>. See [docs/DEPLOY.md](docs/DEPLOY.md) for publishing
to GitHub and Vercel.

## Project layout

```
web/main.py                the entire program
web/FiraMono-Regular.ttf   bundled monospace font
web/OFL.txt                SIL Open Font License for the font
tools/build_web.py         pygbag build + copy into public/
public/                    ready-to-deploy browser build
docs/preview.png           screenshot used by this README
docs/DEPLOY.md             publishing steps for GitHub and Vercel
```

## How it works

Every frame the particle cloud is rotated, projected with a pinhole camera, and
splatted into a character grid. Each cell keeps the smallest depth seen so far, which
acts as a z-buffer; only the winning particle contributes its glyph, color, and
brightness level. Glyphs are rendered once per (character, color, level) combination
into a texture atlas and blitted to the screen, which keeps the frame time low even
with thousands of particles.

## License

MIT. See [LICENSE](LICENSE).
