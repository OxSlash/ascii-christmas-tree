import importlib.util
import os

import numpy as np
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

spec = importlib.util.spec_from_file_location("treeapp", os.path.join(ROOT, "web", "main.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CARD_W, CARD_H = 1200, 630
SEED = mod.SEED_DEFAULT
MOMENT = 20.0
FONT_PATH = os.path.join(ROOT, "web", "FiraMono-Regular.ttf")
OUT_DIR = os.path.join(ROOT, "docs")

GOLD = (255, 214, 120)
WHITE = (245, 250, 255)
DIM = (150, 168, 190)


def boot():
    pygame.init()
    pygame.display.set_mode((mod.WIDTH, mod.HEIGHT_PX))
    return mod.App(SEED, 30)


def tree_screen(app, t):
    fb = app.framebuffer
    fb.clear()
    app.background.draw(fb, t)
    app.tree.draw(fb, t)
    app.background.draw_front(fb, t)
    app.compose()
    return app.screen


def banner_block(surface, text, left, top, unit, color):
    for index, ch in enumerate(text):
        pattern = mod.BANNER_FONT.get(ch)
        if pattern is None:
            continue
        col = left + index * 6 * unit
        for r, line in enumerate(pattern):
            for c, mark in enumerate(line):
                if mark == "#":
                    pygame.draw.rect(
                        surface,
                        color,
                        (col + c * unit, top + r * unit, unit - 1, unit - 1),
                    )


def banner_width(text, unit):
    return len(text) * 6 * unit - unit


def shade_color(color_index, level):
    base = mod.PALETTE[color_index]
    factor = 0.55 + 0.45 * (level / (mod.LEVELS - 1))
    return (
        min(255, int(base[0] * factor)),
        min(255, int(base[1] * factor)),
        min(255, int(base[2] * factor)),
    )


def draw_grid(surface, fb, col0, col1, row0, row1, cell, origin_x, origin_y, solid=False, dim=1.0):
    font = pygame.font.Font(FONT_PATH, int(cell * 1.35))
    font.set_bold(True)
    for row in range(row0, row1):
        for col in range(col0, col1):
            glyph = int(fb.glyph[row, col])
            if glyph < 0:
                continue
            rgb = shade_color(int(fb.color[row, col]), int(fb.level[row, col]))
            if dim != 1.0:
                rgb = (int(rgb[0] * dim), int(rgb[1] * dim), int(rgb[2] * dim))
            x = origin_x + (col - col0) * cell
            y = origin_y + (row - row0) * cell
            if solid:
                pygame.draw.rect(surface, rgb, (x, y, cell, cell))
            else:
                glyph_surface = font.render(mod.GLYPH_CHARS[glyph], True, rgb)
                surface.blit(
                    glyph_surface,
                    (x + (cell - glyph_surface.get_width()) // 2, y + (cell - glyph_surface.get_height()) // 2),
                )


def card_cinematic(app):
    card = pygame.Surface((CARD_W, CARD_H))
    card.fill(mod.BG)
    screen = tree_screen(app, MOMENT)
    crop = screen.subsurface((120, 40, 640, 940)).copy()
    scale = 630 / 940
    scaled = pygame.transform.smoothscale(crop, (int(640 * scale), 630))
    card.blit(scaled, (CARD_W - scaled.get_width() + 40, 0))

    unit = 7
    lines = ("MERRY", "CHRISTMAS", "2026")
    tops = (150, 232, 314)
    colors = (GOLD, WHITE, (232, 62, 72))
    for line, top, color in zip(lines, tops, colors):
        banner_block(card, line, 70, top, unit, color)

    small = pygame.font.Font(FONT_PATH, 22)
    small.set_bold(True)
    caption = small.render("A rotating 3D Christmas tree drawn in ASCII", True, DIM)
    card.blit(caption, (72, 430))
    hint = small.render("pygame-ce  ·  numpy  ·  WebAssembly", True, (110, 126, 148))
    card.blit(hint, (72, 468))
    return card


def card_macro(app):
    card = pygame.Surface((CARD_W, CARD_H))
    screen = tree_screen(app, MOMENT)
    crop = screen.subsurface((300, 520, 300, 158)).copy()
    zoom = pygame.transform.scale(crop, (CARD_W, CARD_H))
    card.blit(zoom, (0, 0))

    pygame.draw.rect(card, (5, 7, 13), (0, CARD_H - 170, CARD_W, 170))

    unit = 5
    banner_block(card, "MERRY CHRISTMAS", 48, CARD_H - 140, unit, GOLD)
    font = pygame.font.Font(FONT_PATH, 22)
    font.set_bold(True)
    caption = font.render("every pixel here is a character", True, DIM)
    card.blit(caption, (50, CARD_H - 58))
    return card


def card_two_faces(app):
    card = pygame.Surface((CARD_W, CARD_H))
    card.fill(mod.BG)
    fb = app.framebuffer
    fb.clear()
    app.background.draw(fb, MOMENT)
    app.tree.draw(fb, MOMENT)
    app.background.draw_front(fb, MOMENT)

    cell = 7
    col0, col1 = 6, 82
    row0, row1 = 0, mod.ROWS
    width = (col1 - col0) * cell
    height = (row1 - row0) * cell
    y0 = (CARD_H - height) // 2 + 16

    draw_grid(card, fb, col0, col1, row0, row1, cell, 14, y0, solid=True, dim=0.55)
    draw_grid(card, fb, col0, col1, row0, row1, cell, 614, y0, solid=False)

    pygame.draw.line(card, (58, 74, 96), (600, 30), (600, CARD_H - 30), 2)

    font = pygame.font.Font(FONT_PATH, 24)
    font.set_bold(True)
    left_label = font.render("SOLID BLOCKS", True, GOLD)
    right_label = font.render("CHARACTERS", True, WHITE)
    card.blit(left_label, (14 + width // 2 - left_label.get_width() // 2, y0 - 36))
    card.blit(right_label, (614 + width // 2 - right_label.get_width() // 2, y0 - 36))
    return card


def card_all_ascii(app):
    card = pygame.Surface((CARD_W, CARD_H))
    card.fill(mod.BG)
    fb = app.framebuffer
    fb.clear()
    app.background.draw(fb, MOMENT)
    app.tree.draw(fb, MOMENT)
    app.background.draw_front(fb, MOMENT)

    cell = 8
    draw_grid(card, fb, 0, mod.COLS, 0, mod.ROWS, cell, 4, (CARD_H - mod.ROWS * cell) // 2, solid=False)

    unit = 6
    left = 4 + mod.COLS * cell + 20
    tops = (140, 200, 260)
    for line, top, color in zip(("MERRY", "CHRISTMAS", "2026"), tops, (GOLD, WHITE, (232, 62, 72))):
        banner_block(card, line, left, top, unit, color)

    font = pygame.font.Font(FONT_PATH, 19)
    font.set_bold(True)
    caption = font.render("no images inside", True, DIM)
    card.blit(caption, (left + 4, 352))
    return card


def main():
    app = boot()
    os.makedirs(OUT_DIR, exist_ok=True)
    builders = (
        ("social-card-a.png", card_cinematic),
        ("social-card-b.png", card_macro),
        ("social-card-c.png", card_two_faces),
        ("social-card-d.png", card_all_ascii),
    )
    for name, builder in builders:
        card = builder(app)
        path = os.path.join(OUT_DIR, name)
        pygame.image.save(card, path)
        print(f"{name} {card.get_width()}x{card.get_height()} {os.path.getsize(path)} bytes", flush=True)
    pygame.quit()


if __name__ == "__main__":
    main()
