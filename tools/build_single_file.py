import base64
import importlib.util
import json
import os
import struct

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("treeapp", os.path.join(ROOT, "web", "main.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PARTICLES = 12000
SCALE_TIME = 100.0
SCALE_ANGLE = 10000.0
SCALE_FREQ = 10000.0


def pack_tree(data):
    n = int(data["x"].size)
    out = bytearray(struct.pack("<I", n))
    xs = data["x"].astype("<f4")
    ys = data["y"].astype("<f4")
    zs = data["z"].astype("<f4")
    gl = data["glyph"].astype(np.uint8)
    co = data["color"].astype(np.uint8)
    gr = data["group"].astype(np.uint8)
    ap = np.clip(np.round(data["appear"] * SCALE_TIME), 0, 65535).astype("<u2")
    ph = np.clip(np.round(data["phase"] * SCALE_ANGLE), 0, 65535).astype("<u2")
    fr = np.clip(np.round(data["freq"] * SCALE_FREQ), 0, 65535).astype("<u2")
    out += xs.tobytes() + ys.tobytes() + zs.tobytes()
    out += gl.tobytes() + co.tobytes() + gr.tobytes()
    out += ap.tobytes() + ph.tobytes() + fr.tobytes()
    return bytes(out), n


def pack_background(bg):
    stars = {
        "col": bg.star_col.tolist(),
        "row": bg.star_row.tolist(),
        "phase": [round(float(v), 4) for v in bg.star_phase],
        "freq": [round(float(v), 4) for v in bg.star_freq],
        "power": [round(float(v), 4) for v in bg.star_power],
    }

    def flakes(store):
        return {
            "col": [round(float(v), 3) for v in store["col"]],
            "row": [round(float(v), 3) for v in store["row"]],
            "speed": [round(float(v), 3) for v in store["speed"]],
            "drift": [round(float(v), 3) for v in store["drift"]],
            "sway": [round(float(v), 3) for v in store["sway"]],
            "phase": [round(float(v), 4) for v in store["phase"]],
            "glyph": [int(v) for v in store["glyph"]],
            "level": int(store["level"]),
        }

    return {"stars": stars, "far": flakes(bg.far), "near": flakes(bg.near)}


def banner_bounds(cells):
    first = min(cell[2] for cell in cells)
    last = max(cell[2] for cell in cells) + mod.BANNER_STEP - 2
    return first, last


def build():
    seed = mod.SEED_DEFAULT
    data = mod.build_tree(seed, PARTICLES)
    blob, count = pack_tree(data)
    bg = mod.Background(seed, 150, 300, 130)
    bg_data = pack_background(bg)

    payload = base64.b64encode(blob).decode("ascii")
    banner_cells = [[int(i), str(ch), int(col), int(top)] for i, ch, col, top in mod.BANNER_CELLS]
    banner_font = {k: list(v) for k, v in mod.BANNER_FONT.items()}
    banner_first, banner_last = banner_bounds(banner_cells)

    config = {
        "cols": mod.COLS,
        "rows": mod.ROWS,
        "cw": mod.CELL_W,
        "ch": mod.CELL_H,
        "focus": mod.FOCUS,
        "zOffset": mod.Z_OFFSET,
        "scaleX": mod.SCALE_X,
        "omega": mod.OMEGA,
        "levels": mod.LEVELS,
        "treeRadius": mod.TREE_RADIUS,
        "centerX": mod.CENTER_X,
        "centerY": mod.CENTER_Y,
        "tText": mod.T_TEXT,
        "text": mod.TEXT,
        "letterDelay": mod.LETTER_DELAY,
        "bannerCells": banner_cells,
        "bannerFirst": banner_first,
        "bannerLast": banner_last,
        "bannerFont": banner_font,
        "palette": [list(c) for c in mod.PALETTE],
        "glyphs": mod.GLYPH_CHARS,
        "snow": int(mod.SNOW),
        "white": int(mod.WHITE),
        "warm": int(mod.WARM),
        "goldLight": int(mod.GOLD_LIGHT),
        "silver": int(mod.SILVER),
        "gold": int(mod.GOLD),
        "bg": list(mod.BG),
        "light": int(mod.LIGHT),
        "star": int(mod.STAR),
        "scaleTime": SCALE_TIME,
        "scaleAngle": SCALE_ANGLE,
        "scaleFreq": SCALE_FREQ,
    }

    here = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(ROOT, "web", "FiraMono-Regular.ttf")
    with open(font_path, "rb") as handle:
        font_b64 = base64.b64encode(handle.read()).decode("ascii")

    template = open(os.path.join(here, "single_file.html"), encoding="utf-8").read()
    html = template.replace("__CONFIG__", json.dumps(config, separators=(",", ":")))
    html = html.replace("__BACKGROUND__", json.dumps(bg_data, separators=(",", ":")))
    html = html.replace("__FONT__", font_b64)
    html = html.replace("__PAYLOAD__", payload)

    out_dir = os.path.join(ROOT, "dist")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ascii-christmas-tree.html")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(html)
    print(f"saved {out_path} {os.path.getsize(out_path)} bytes particles {count}")


if __name__ == "__main__":
    build()
