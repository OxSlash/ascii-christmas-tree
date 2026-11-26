import argparse
import os

import numpy as np
import pygame
import segno

SNOW = (247, 250, 255)
DARK_TREE = ((12, 52, 30), (18, 72, 40), (26, 92, 50), (34, 112, 58))
DARK_NIGHT = ((8, 14, 26), (12, 20, 36))
DARK_ACCENT = ((198, 52, 64), (54, 104, 192), (150, 110, 30), (120, 78, 40))
LIGHT_TREE = ((196, 226, 202), (208, 234, 212), (220, 240, 222))
LIGHT_NIGHT = ((236, 242, 252), (243, 248, 255))
LIGHT_ACCENT = ((255, 236, 160), (255, 186, 192), (168, 198, 255))
FRAME = (232, 214, 150)
CAPTION = (26, 42, 64)
RAMP = "#%@*ox+=-"
TIERS = 5


def tree_mask(size):
    rows = np.arange(size, dtype=np.float64)[:, None] * np.ones((1, size))
    cols = np.ones((size, 1)) * np.arange(size, dtype=np.float64)[None, :]
    apex = size * 0.04
    base = size * 0.90
    v = np.clip((rows - apex) / (base - apex), 0.0, 1.0)
    tier = np.minimum((v * TIERS).astype(np.int32), TIERS - 1)
    frac = v * TIERS - tier
    grow = (0.16 + 0.84 * (tier / (TIERS - 1.0))) * (0.78 + 0.22 * frac)
    offset = np.abs(cols - (size - 1.0) / 2.0)
    body = (rows >= apex) & (rows <= base) & (offset <= size * 0.47 * grow)
    trunk = (rows > base) & (rows <= size * 0.965) & (offset <= size * 0.055)
    star = (rows < size * 0.10) & (offset <= size * 0.05)
    return body, trunk, star, v


def paint(matrix, rng):
    size = matrix.shape[0]
    body, trunk, star, v = tree_mask(size)
    inside = body | trunk | star

    depth = np.clip((v * len(DARK_TREE)).astype(np.int32), 0, len(DARK_TREE) - 1)
    night = rng.integers(0, len(DARK_NIGHT), size=(size, size))
    dark_tree = depth
    dark_night = len(DARK_TREE) + night
    light_tree = np.clip((v * len(LIGHT_TREE)).astype(np.int32), 0, len(LIGHT_TREE) - 1)
    light_night = rng.integers(0, len(LIGHT_NIGHT), size=(size, size))

    dark_index = np.where(inside, dark_tree, dark_night)
    light_index = np.where(inside, light_tree, light_night)

    accent = inside & (rng.random((size, size)) < 0.05)
    dark_pick = rng.integers(0, len(DARK_ACCENT), size=(size, size))
    light_pick = rng.integers(0, len(LIGHT_ACCENT), size=(size, size))
    dark_index = np.where(accent, len(DARK_TREE) + len(DARK_NIGHT) + dark_pick, dark_index)
    light_index = np.where(accent, len(LIGHT_TREE) + len(LIGHT_NIGHT) + light_pick, light_index)

    gold_star = star & (rng.random((size, size)) < 0.55)
    dark_index = np.where(gold_star, len(DARK_TREE) + len(DARK_NIGHT) + 2, dark_index)
    light_index = np.where(gold_star, len(LIGHT_TREE) + len(LIGHT_NIGHT), light_index)

    dark_colors = DARK_TREE + DARK_NIGHT + DARK_ACCENT
    light_colors = LIGHT_TREE + LIGHT_NIGHT + LIGHT_ACCENT
    colors = tuple(dark_colors) + tuple(light_colors)

    index = np.where(matrix, dark_index, light_index + len(dark_colors))
    mask = matrix | inside
    return index, colors, mask


def build_tiles(font, colors):
    tiles = {}
    for index, rgb in enumerate(colors):
        for ch in RAMP:
            glyph = font.render(ch, True, rgb)
            tile = pygame.Surface((glyph.get_width(), glyph.get_height()), pygame.SRCALPHA)
            tile.blit(glyph, (0, 0))
            tiles[(index, ch)] = tile
    return tiles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://github.com/OxSlash/ascii-christmas-tree")
    parser.add_argument("--out", default=os.path.join("docs", "qr-tree.png"))
    parser.add_argument("--seed", type=int, default=2512)
    parser.add_argument("--width", type=int, default=1400)
    parser.add_argument("--caption", default="SCAN ME")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    qr = segno.make(args.url, error="h", boost_error=False, micro=False)
    matrix = np.array(qr.matrix, dtype=bool)
    size = matrix.shape[0]

    quiet = 4
    border = 2
    module_px = max(10, args.width // (size + 2 * quiet + 2 * border))
    canvas = (size + 2 * quiet + 2 * border) * module_px
    caption_px = module_px * 3

    pygame.init()
    pygame.display.set_mode((1, 1))
    font = pygame.font.Font(os.path.join("web", "FiraMono-Regular.ttf"), int(module_px * 1.25))
    font.set_bold(True)
    label_font = pygame.font.Font(os.path.join("web", "FiraMono-Regular.ttf"), caption_px)
    label_font.set_bold(True)

    index, colors, mask = paint(matrix, rng)
    tiles = build_tiles(font, colors)

    surface = pygame.Surface((canvas, canvas + caption_px * 2))
    surface.fill(SNOW)

    origin = (border + quiet) * module_px
    for row in range(size):
        for col in range(size):
            if not mask[row, col]:
                continue
            x = origin + col * module_px
            y = origin + row * module_px
            slot = int(index[row, col])
            pygame.draw.rect(surface, colors[slot], (x, y, module_px, module_px))
            ch = RAMP[int(rng.integers(0, len(RAMP)))]
            tile = tiles[(slot, ch)]
            surface.blit(tile, (x + (module_px - tile.get_width()) // 2, y + (module_px - tile.get_height()) // 2))

    edge = max(2, module_px // 4)
    pygame.draw.rect(
        surface,
        FRAME,
        (border * module_px, border * module_px, canvas - 2 * border * module_px, canvas - 2 * border * module_px),
        edge,
    )

    label = label_font.render(args.caption, True, CAPTION)
    surface.blit(label, ((canvas - label.get_width()) // 2, canvas + caption_px // 2))

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    pygame.image.save(surface, args.out)
    pygame.quit()
    print(f"saved {args.out} {surface.get_width()}x{surface.get_height()} modules {size}x{size} url {args.url}")


if __name__ == "__main__":
    main()
