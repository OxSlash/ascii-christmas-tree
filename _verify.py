import importlib.util
import os
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
OUT = os.path.join(os.environ["TEMP"], "opencode")
os.makedirs(OUT, exist_ok=True)

import numpy as np
import pygame

spec = importlib.util.spec_from_file_location("treeapp", os.path.join("web", "main.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

pygame.init()
pygame.display.set_mode((module.WIDTH, module.HEIGHT_PX))

app = module.App(8412, 30)
print("particles", app.tree.count)
print("grid", module.COLS, module.ROWS, "canvas", module.WIDTH, module.HEIGHT_PX)

hud = module.TITLE + module.TEXT + "space pause   R restart   S shot   D debug   Esc quit"
missing = sorted({c for c in hud if c not in module.GLYPH_INDEX})
print("missing_glyphs", missing)


def dump(label):
    fb = app.framebuffer
    lines = []
    for r in range(module.ROWS):
        row = "".join(module.GLYPH_CHARS[g] if g >= 0 else " " for g in fb.glyph[r])
        lines.append(row.rstrip())
    print(f"----- {label} cells={app.tree.visible_cells} -----")
    print("\n".join(lines))


for label, moment in (("t02", 2.0), ("t06", 6.0), ("t10", 10.0), ("t16", 16.0), ("t24", 24.0)):
    app.t = moment
    app.draw()
    pygame.image.save(app.screen, os.path.join(OUT, f"_shot_{label[1:]}.png"))

app.t = 24.0
app.draw()
dump("t24")

fb = app.framebuffer
rows, cols = np.nonzero(fb.glyph >= 0)
print("bbox rows", int(rows.min()), int(rows.max()), "cols", int(cols.min()), int(cols.max()))

app.t = 16.0
frames = 150
start = time.perf_counter()
for _ in range(frames):
    app.step(1.0 / 30.0)
elapsed = time.perf_counter() - start
print(f"native_fps {frames / elapsed:.1f}")
print(f"frame_ms {elapsed / frames * 1000:.2f}")
print("atlas_tiles", len(app.atlas.tiles))


def probe(depth, color, glyph):
    inv = module.FOCUS / (module.FOCUS + depth + module.Z_OFFSET)
    y = 24.5 / (module.SCALE_Y * inv)
    return inv, y


inv_near, y_near = probe(-200.0, module.WHITE, module.GLYPH_INDEX["@"])
inv_far, y_far = probe(200.0, module.PINE_DEEP, module.GLYPH_INDEX["."])
units = {
    "x": np.array([0.0, 0.0], dtype=np.float32),
    "y": np.array([y_near, y_far], dtype=np.float32),
    "z": np.array([-200.0, 200.0], dtype=np.float32),
    "glyph": np.array([module.GLYPH_INDEX["@"], module.GLYPH_INDEX["."]], dtype=np.int16),
    "color": np.array([module.WHITE, module.PINE_DEEP], dtype=np.int16),
    "group": np.array([module.NEEDLE, module.NEEDLE], dtype=np.int8),
    "appear": np.zeros(2, dtype=np.float32),
    "phase": np.zeros(2, dtype=np.float32),
    "freq": np.zeros(2, dtype=np.float32),
}
probe_tree = module.Tree(units, 1)
probe_fb = module.Framebuffer()
probe_tree.draw(probe_fb, 0.0)
row, col = 40, 44
print("probe_inv_near", round(inv_near, 4), "probe_inv_far", round(inv_far, 4))
print("probe_cell_glyph", module.GLYPH_CHARS[probe_fb.glyph[row, col]])
print("probe_cell_color", int(probe_fb.color[row, col]), "near_is", module.WHITE, "far_is", module.PINE_DEEP)
print("probe_level", int(probe_fb.level[row, col]))
print("probe_cells", probe_tree.visible_cells)
assert probe_fb.color[row, col] == module.WHITE, "z-buffer kept the far particle"
assert inv_near > inv_far, "perspective scale not larger for nearer point"
assert probe_fb.level[row, col] > 6, "near particle not brighter"
print("probe_ok z-buffer near-wins, perspective, depth shading")

pygame.quit()
