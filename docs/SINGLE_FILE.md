# Single-file HTML build

One file, no server, no internet. Open `dist/ascii-christmas-tree.html` and the
tree runs — on a laptop, on a phone, on a plane.

## Build

```bash
python tools/build_single_file.py
```

Output: `dist/ascii-christmas-tree.html` (~576 KB).

## What is inside

| Part | How |
|---|---|
| Particle data | 11,398 particles packed to base64 — positions as `float32`, glyph/color/group as `uint8`, timing as `uint16`. |
| Font | Fira Mono embedded as a base64 `@font-face`. |
| Renderer | Plain JavaScript: rotation, perspective projection, per-cell z-buffer, depth shading, snow, banner. |
| Dependencies | None. No CDN, no network requests. |

## Verification

Checked in headless Chrome, loaded from `file:///` with the network set to
**offline**:

```
offline_state   object
offline_tree_n  11398
offline_font    True
offline_cells   912
fps             39.3
```

Frame-for-frame comparison against the pygame build at `t = 20 s`, ignoring the
HUD rows:

```
glyph_match 5803/5808  (99.91%)
color_match 5764/5808  (99.24%)
level_match 5805/5808  (99.95%)
```

The five remaining cells are sub-pixel tie-breaks where two particles land in
the same cell; they swap between adjacent glyphs and are not visible.

Timeline parity with the native build:

```
t=0.0  cells   5  letters  0
t=4.0  cells 615  letters  0
t=7.4  cells 722  letters  0
t=9.0  cells 773  letters 11
t=10.0 cells 808  letters 20
t=12.0 cells 949  letters 20
```

## Controls

| Input | Action |
|---|---|
| Tap / click | Pause or resume |
| `Space` | Pause or resume |
| `R` | Restart |
| `D` | Show FPS, particle count, visible cells |
| `Esc` | Stop the loop |

## Tools

| File | Purpose |
|---|---|
| `tools/build_single_file.py` | Builds `dist/ascii-christmas-tree.html` |
| `tools/single_file.html` | Template with `__CONFIG__`, `__BACKGROUND__`, `__FONT__`, `__PAYLOAD__` slots |
| `tools/check_single_file.py` | Headless Chrome: load, set time, screenshot, report FPS |
| `tools/dump_native_frame.py` | Dumps the pygame framebuffer at `t = 20 s` to JSON |
| `tools/compare_frames.py` | Compares the web frame against the native frame cell by cell |
