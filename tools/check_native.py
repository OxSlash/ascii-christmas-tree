import importlib.util
import os
import sys

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["SDL_VIDEODRIVER"] = "dummy"
spec = importlib.util.spec_from_file_location("treeapp", os.path.join(ROOT, "web", "main.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

pygame.init()
pygame.display.set_mode((mod.WIDTH, mod.HEIGHT_PX))
app = mod.App(mod.SEED_DEFAULT, 30)


def report(t):
    app.t = t
    app.framebuffer.clear()
    app.background.draw(app.framebuffer, app.t)
    app.tree.draw(app.framebuffer, app.t)
    app.background.draw_front(app.framebuffer, app.t)
    app.bursts.draw(app.framebuffer)
    app.draw_overlay()
    glyph = app.framebuffer.glyph
    rows, cols = (glyph >= 0).nonzero()
    return {
        "t": t,
        "cells": int(rows.size),
        "top": int(rows.min()),
        "bottom": int(rows.max()),
        "left": int(cols.min()),
        "right": int(cols.max()),
        "letters": app.letter_count(),
    }


print("banner", mod.BANNER_TOP, mod.BANNER_BOTTOM, mod.GREETING)
for t in (0.0, 5.0, 10.0, 20.0, 40.0):
    print(report(t))

app.bursts.spawn(44, 40)
app.bursts.update(0.2)
print("bursts", len(app.bursts.col))
app.step(0.033)
print("step ok")

for key in (pygame.K_r, pygame.K_d, pygame.K_s, pygame.K_SPACE):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
app.handle_events()
print("keys ok paused", app.paused)

pygame.quit()
