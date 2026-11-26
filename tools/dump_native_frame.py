import json
import os
import sys

import numpy as np
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["SDL_VIDEODRIVER"] = "dummy"
import importlib.util

spec = importlib.util.spec_from_file_location("treeapp", os.path.join(ROOT, "web", "main.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

pygame.init()
pygame.display.set_mode((mod.WIDTH, mod.HEIGHT_PX))

seed = mod.SEED_DEFAULT
data = mod.build_tree(seed, 12000)
tree = mod.Tree(data, seed)
bg = mod.Background(seed, 150, 300, 130)
fb = mod.Framebuffer()
app = mod.App(seed, 30)
app.tree = tree
app.background = bg
app.framebuffer = fb

t = 20.0
fb.clear()
bg.draw(fb, t)
tree.draw(fb, t)
bg.draw_front(fb, t)
app.t = t
app.draw_overlay()

out = {
    "t": t,
    "glyph": fb.glyph.astype(int).tolist(),
    "color": fb.color.astype(int).tolist(),
    "level": fb.level.astype(int).tolist(),
    "cells": int((fb.glyph >= 0).sum()),
}
path = os.path.join(os.environ["TEMP"], "opencode", "native_frame.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(out, handle)
print("saved", path, "cells", out["cells"])
pygame.quit()
