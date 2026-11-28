# /// script
# dependencies = ["numpy"]
# ///

import asyncio
import math
import os
import sys

import numpy as np
import pygame

COLS, ROWS = 88, 74
CELL_W, CELL_H = 10, 14
WIDTH, HEIGHT_PX = COLS * CELL_W, ROWS * CELL_H
FPS = 30
TITLE = "ASCII Christmas Tree"
SEED_DEFAULT = 8412
BG = (7, 10, 18)
IS_WEB = sys.platform == "emscripten"
PARTICLES = 6000 if IS_WEB else 12000

FOCUS = 620.0
Z_OFFSET = 900.0
SCALE_X = 0.279
SCALE_Y = SCALE_X * CELL_W / CELL_H
CENTER_X = COLS * 0.5
CENTER_Y = ROWS - 7.0
TREE_HEIGHT = 472.0
TREE_RADIUS = 190.0
OMEGA = 0.55
LEVELS = 12

T_GROW_END = 4.5
T_GARLAND = 4.5
T_BAUBLE = 7.5
T_GIFT = 9.0
T_STAR = 11.5
T_TEXT = 7.8
TEXT = "MERRY CHRISTMAS 2026"
GREETING = ("MERRY", "CHRISTMAS", "2026")
LETTER_DELAY = 0.11

BANNER_TOP = 1
BANNER_ROWS = 5
BANNER_STEP = 5
BANNER_LINE_GAP = 1
BANNER_FONT = {
    "M": ("#..#", "####", "#..#", "#..#", "#..#"),
    "E": ("####", "#...", "###.", "#...", "####"),
    "R": ("###.", "#..#", "###.", "#..#", "#..#"),
    "Y": ("#..#", "#..#", ".##.", "..#.", "..#."),
    "C": (".###", "#...", "#...", "#...", ".###"),
    "H": ("#..#", "#..#", "####", "#..#", "#..#"),
    "I": ("####", ".##.", ".##.", ".##.", "####"),
    "S": (".###", "#...", ".##.", "...#", "###."),
    "T": ("####", ".##.", ".##.", ".##.", ".##."),
    "A": (".##.", "#..#", "####", "#..#", "#..#"),
    "2": (".##.", "#..#", "..#.", ".#..", "####"),
    "0": (".##.", "#..#", "#..#", "#..#", ".##."),
    "6": (".##.", "#...", "###.", "#..#", ".##."),
}


def banner_cells():
    cells = []
    index = 0
    for line_no, line in enumerate(GREETING):
        width = len(line) * BANNER_STEP - 1
        start = (COLS - width) // 2
        top = BANNER_TOP + line_no * (BANNER_ROWS + BANNER_LINE_GAP)
        for pos, ch in enumerate(line):
            cells.append((index, ch, start + pos * BANNER_STEP, top))
            index += 1
        index += 1
    return cells


BANNER_CELLS = banner_cells()
BANNER_BOTTOM = BANNER_TOP + len(GREETING) * (BANNER_ROWS + BANNER_LINE_GAP)

PALETTE = [
    (40, 104, 60),
    (58, 140, 76),
    (84, 180, 96),
    (116, 214, 116),
    (164, 240, 156),
    (216, 252, 196),
    (232, 246, 255),
    (255, 255, 255),
    (88, 56, 32),
    (140, 94, 54),
    (255, 186, 48),
    (255, 232, 152),
    (232, 62, 72),
    (255, 128, 132),
    (64, 120, 255),
    (132, 182, 255),
    (46, 208, 132),
    (162, 255, 202),
    (208, 220, 240),
    (255, 150, 60),
    (255, 246, 222),
]

PINE_DEEP, PINE_DARK, PINE, PINE_MID, PINE_LIGHT, PINE_PALE = range(6)
SNOW, WHITE = 6, 7
BARK, BARK_LIGHT = 8, 9
GOLD, GOLD_LIGHT = 10, 11
RUBY, RUBY_LIGHT = 12, 13
SAPPHIRE, SAPPHIRE_LIGHT = 14, 15
EMERALD, EMERALD_LIGHT = 16, 17
SILVER = 18
AMBER = 19
WARM = 20

GLYPH_CHARS = " .`':~-+xv*Oo%@#|=" + "MERYCHISTA026"
GLYPH_CHARS += "".join(c for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" if c not in GLYPH_CHARS)
GLYPH_INDEX = {ch: i for i, ch in enumerate(GLYPH_CHARS)}

NEEDLE, TRUNK, GARLAND, BAUBLE, LIGHT, GIFT, STAR = range(7)


def envelope(y):
    v = min(max(y / TREE_HEIGHT, 0.0), 1.0)
    return TREE_RADIUS * (1.0 - v) ** 0.86


class Builder:
    __slots__ = ("rng", "xs", "ys", "zs", "glyphs", "colors", "groups", "appear", "phase", "freq")

    def __init__(self, rng):
        self.rng = rng
        self.xs = []
        self.ys = []
        self.zs = []
        self.glyphs = []
        self.colors = []
        self.groups = []
        self.appear = []
        self.phase = []
        self.freq = []

    def add(self, x, y, z, glyph, color, group, appear, phase=0.0, freq=0.0):
        self.xs.append(x)
        self.ys.append(y)
        self.zs.append(z)
        self.glyphs.append(glyph)
        self.colors.append(color)
        self.groups.append(group)
        self.appear.append(appear)
        self.phase.append(phase)
        self.freq.append(freq)

    def count(self):
        return len(self.xs)

    def freeze(self):
        return {
            "x": np.array(self.xs, dtype=np.float32),
            "y": np.array(self.ys, dtype=np.float32),
            "z": np.array(self.zs, dtype=np.float32),
            "glyph": np.array(self.glyphs, dtype=np.int16),
            "color": np.array(self.colors, dtype=np.int16),
            "group": np.array(self.groups, dtype=np.int8),
            "appear": np.array(self.appear, dtype=np.float32),
            "phase": np.array(self.phase, dtype=np.float32),
            "freq": np.array(self.freq, dtype=np.float32),
        }


def needle_style(rng, fraction):
    roll = rng.random()
    if fraction > 0.88:
        if roll < 0.28:
            return GLYPH_INDEX["."], SNOW
        if roll < 0.62:
            return GLYPH_INDEX["*"], PINE_LIGHT
        if roll < 0.84:
            return GLYPH_INDEX["+"], PINE_MID
        return GLYPH_INDEX["x"], PINE
    if fraction > 0.60:
        if roll < 0.26:
            return GLYPH_INDEX["+"], PINE_MID
        if roll < 0.44:
            return GLYPH_INDEX["*"], PINE_LIGHT
        if roll < 0.72:
            return GLYPH_INDEX["x"], PINE
        return GLYPH_INDEX["v"], PINE_MID
    if roll < 0.24:
        return GLYPH_INDEX["%"], PINE_DARK
    if roll < 0.46:
        return GLYPH_INDEX["#"], PINE_DEEP
    if roll < 0.76:
        return GLYPH_INDEX["x"], PINE
    return GLYPH_INDEX["v"], PINE_DARK


def emit_branch(builder, rng, angle, y_base, reach, droop, samples, radius):
    ca = math.cos(angle)
    sa = math.sin(angle)
    for s in range(samples):
        f = (s + 1) / samples
        r = reach * f ** 0.9
        spread = 0.8 + 3.0 * f
        x = ca * r + rng.normal(0.0, spread)
        z = sa * r + rng.normal(0.0, spread)
        yy = y_base - droop * f ** 1.7 + rng.normal(0.0, 1.4)
        appear = T_GROW_END * min(1.0, max(0.0, yy / TREE_HEIGHT)) ** 0.9
        glyph, color = needle_style(rng, r / max(radius, 1.0))
        builder.add(x, yy, z, glyph, color, NEEDLE, appear + rng.uniform(0.0, 0.12))


def build_needles(builder, target):
    rng = builder.rng
    tiers = 10
    tier_y = []
    tier_r = []
    for w in range(tiers):
        v = w / (tiers - 1)
        y = TREE_HEIGHT * (0.10 + 0.88 * v ** 1.05)
        tier_y.append(y)
        tier_r.append(max(envelope(y), 16.0))
    weights = np.array(tier_r, dtype=np.float64)
    weights /= weights.sum()
    budget = int(target * 0.95)
    for w in range(tiers):
        v = w / (tiers - 1)
        y_base = tier_y[w]
        radius = tier_r[w]
        per_tier = max(1, int(budget * weights[w]))
        branches = max(6, int(round(20 - 13 * v)))
        angle_offset = rng.uniform(0.0, math.tau)
        for b in range(branches):
            angle = angle_offset + math.tau * b / branches + rng.normal(0.0, 0.07)
            reach = radius * rng.uniform(0.82, 1.20)
            droop = max(8.0, reach * rng.uniform(0.10, 0.17))
            main = max(3, int(per_tier * 0.66) // branches)
            emit_branch(builder, rng, angle, y_base, reach, droop, main, radius)
            side = max(2, int(per_tier * 0.34) // branches)
            sub_angle = angle + math.pi / branches + rng.normal(0.0, 0.10)
            sub_reach = reach * rng.uniform(0.40, 0.68)
            emit_branch(builder, rng, sub_angle, y_base, sub_reach, droop * 0.65, side, radius)
    guard = 0
    while builder.count() < target and guard < target * 6:
        guard += 1
        v = rng.random() ** 0.8
        y = TREE_HEIGHT * (0.04 + 0.96 * v)
        radius = envelope(y)
        r = radius * rng.random() ** 0.7
        angle = rng.uniform(0.0, math.tau)
        x = math.cos(angle) * r
        z = math.sin(angle) * r
        appear = T_GROW_END * min(1.0, max(0.0, y / TREE_HEIGHT)) ** 0.9
        glyph, color = needle_style(rng, r / max(radius, 1.0))
        builder.add(x, y, z, glyph, color, NEEDLE, appear + rng.uniform(0.0, 0.12))


def build_trunk(builder, budget):
    rng = builder.rng
    for _ in range(budget):
        v = rng.random()
        y = -6.0 + TREE_HEIGHT * 0.34 * v
        radius = 15.0 - 5.0 * v
        angle = rng.uniform(0.0, math.tau)
        rr = radius * rng.uniform(0.86, 1.0)
        x = math.cos(angle) * rr
        z = math.sin(angle) * rr
        glyph = GLYPH_INDEX["%"] if rng.random() < 0.5 else GLYPH_INDEX["#"]
        color = BARK if rng.random() < 0.7 else BARK_LIGHT
        appear = T_GROW_END * min(1.0, max(0.0, y / TREE_HEIGHT)) ** 0.9
        builder.add(x, y, z, glyph, color, TRUNK, appear)


def build_garland(builder, budget):
    rng = builder.rng
    turns = 3.8
    total = max(2, budget)
    for i in range(total):
        f = i / (total - 1)
        v = 0.10 + 0.86 * f
        y = TREE_HEIGHT * v
        radius = envelope(y) * 1.07
        angle = math.tau * turns * f
        wobble = 5.0 * math.sin(angle * 3.0) + 3.0 * math.sin(angle * 7.0)
        x = math.cos(angle) * radius
        z = math.sin(angle) * radius
        roll = rng.random()
        if roll < 0.55:
            glyph, color = GLYPH_INDEX["*"], GOLD
        elif roll < 0.85:
            glyph, color = GLYPH_INDEX["o"], GOLD_LIGHT
        else:
            glyph, color = GLYPH_INDEX["~"], AMBER
        builder.add(x, y + wobble, z, glyph, color, GARLAND, T_GARLAND + 2.5 * f)


def build_baubles(builder, budget):
    rng = builder.rng
    colors = (RUBY, GOLD, SILVER, SAPPHIRE, EMERALD)
    total = max(1, budget // 7)
    for _ in range(total):
        v = rng.uniform(0.08, 0.93)
        y = TREE_HEIGHT * v
        radius = envelope(y) * rng.uniform(0.70, 1.02)
        angle = rng.uniform(0.0, math.tau)
        cx = math.cos(angle) * radius
        cz = math.sin(angle) * radius
        color = colors[int(rng.integers(0, len(colors)))]
        appear = T_BAUBLE + rng.uniform(0.0, 2.3)
        for k in range(7):
            ox, oy, oz = rng.normal(0.0, 2.8, 3)
            if k == 0:
                glyph = GLYPH_INDEX["O"]
            elif rng.random() < 0.5:
                glyph = GLYPH_INDEX["@"]
            else:
                glyph = GLYPH_INDEX["o"]
            shade = color if rng.random() < 0.7 else color + 1
            builder.add(cx + ox, y + oy, cz + oz, glyph, shade, BAUBLE, appear)


def build_lights(builder, budget):
    rng = builder.rng
    colors = (AMBER, GOLD_LIGHT, RUBY_LIGHT, EMERALD_LIGHT, SAPPHIRE_LIGHT, WARM)
    total = max(1, budget // 3)
    for _ in range(total):
        v = rng.uniform(0.10, 0.96)
        y = TREE_HEIGHT * v
        radius = envelope(y) * rng.uniform(0.85, 1.04)
        angle = rng.uniform(0.0, math.tau)
        cx = math.cos(angle) * radius
        cz = math.sin(angle) * radius
        color = colors[int(rng.integers(0, len(colors)))]
        phase = rng.uniform(0.0, math.tau)
        freq = rng.uniform(1.1, 3.2)
        appear = T_BAUBLE + rng.uniform(0.0, 2.2)
        for _ in range(3):
            ox, oy, oz = rng.normal(0.0, 1.5, 3)
            builder.add(cx + ox, y + oy, cz + oz, GLYPH_INDEX["*"], color, LIGHT, appear, phase, freq)


def build_gifts(builder, budget):
    rng = builder.rng
    boxes = 4
    steps = max(3, budget // (boxes * 18) - 1)
    pairs = ((RUBY, GOLD), (SAPPHIRE, SILVER), (EMERALD, GOLD_LIGHT), (RUBY, SILVER))
    for b in range(boxes):
        angle = math.tau * b / boxes + rng.uniform(-0.26, 0.26)
        dist = TREE_RADIUS * rng.uniform(1.02, 1.20)
        cx = math.cos(angle) * dist
        cz = math.sin(angle) * dist
        hw = rng.uniform(12.0, 17.0)
        hd = rng.uniform(12.0, 17.0)
        hh = rng.uniform(16.0, 28.0)
        body, ribbon = pairs[b % len(pairs)]
        appear = T_GIFT + rng.uniform(0.0, 2.2)
        corners = ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))
        for k in range(4):
            x0, z0 = corners[k]
            x1, z1 = corners[(k + 1) % 4]
            for s in range(steps + 1):
                f = s / steps
                x = cx + x0 + (x1 - x0) * f
                z = cz + z0 + (z1 - z0) * f
                builder.add(x, 0.0, z, GLYPH_INDEX["#"], body, GIFT, appear)
                builder.add(x, hh, z, GLYPH_INDEX["="], body, GIFT, appear)
        for k in range(4):
            x0, z0 = corners[k]
            for s in range(steps + 1):
                builder.add(cx + x0, hh * s / steps, cz + z0, GLYPH_INDEX["%"], body, GIFT, appear)
        for s in range(steps + 1):
            f = s / steps
            builder.add(cx - hw, hh * f, cz, GLYPH_INDEX["|"], ribbon, GIFT, appear)
            builder.add(cx + hw, hh * f, cz, GLYPH_INDEX["|"], ribbon, GIFT, appear)
            builder.add(cx, hh * f, cz - hd, GLYPH_INDEX["|"], ribbon, GIFT, appear)
            builder.add(cx, hh * f, cz + hd, GLYPH_INDEX["|"], ribbon, GIFT, appear)
            builder.add(cx - hw + 2.0 * hw * f, hh, cz, GLYPH_INDEX["="], ribbon, GIFT, appear)
            builder.add(cx, hh, cz - hd + 2.0 * hd * f, GLYPH_INDEX["="], ribbon, GIFT, appear)


def build_star(builder, budget):
    rng = builder.rng
    top = TREE_HEIGHT + 26.0
    core = max(20, budget // 2)
    for _ in range(core):
        r = abs(rng.normal(0.0, 6.5))
        a = rng.uniform(0.0, math.tau)
        b = rng.uniform(0.0, math.pi)
        x = r * math.cos(a) * math.sin(b)
        y = top + r * math.cos(b)
        z = r * math.sin(a) * math.sin(b)
        roll = rng.random()
        if roll < 0.34:
            glyph, color = GLYPH_INDEX["#"], GOLD
        elif roll < 0.7:
            glyph, color = GLYPH_INDEX["@"], GOLD_LIGHT
        else:
            glyph, color = GLYPH_INDEX["%"], WHITE
        builder.add(x, y, z, glyph, color, STAR, T_STAR, 0.0, 3.1)

    steps = 6
    for plane in range(2):
        verts = []
        for k in range(10):
            angle = math.pi / 2.0 + math.tau * k / 10.0
            radius = 52.0 if k % 2 == 0 else 22.0
            verts.append((math.cos(angle) * radius, math.sin(angle) * radius))
        for k in range(10):
            x0, y0 = verts[k]
            x1, y1 = verts[(k + 1) % 10]
            for s in range(steps):
                f = s / steps
                px = x0 + (x1 - x0) * f
                py = y0 + (y1 - y0) * f
                jitter = rng.normal(0.0, 0.7)
                if plane == 0:
                    builder.add(px, top + py, jitter, GLYPH_INDEX["*"], GOLD_LIGHT, STAR, T_STAR, 0.0, 3.1)
                else:
                    builder.add(jitter, top + py, px, GLYPH_INDEX["*"], GOLD_LIGHT, STAR, T_STAR, 0.0, 3.1)

    rays = (
        (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0),
        (0.7, 0.7, 0.0), (-0.7, 0.7, 0.0), (0.7, -0.7, 0.0), (-0.7, -0.7, 0.0),
        (0.0, 0.7, 0.7), (0.0, 0.7, -0.7), (0.0, -0.7, 0.7), (0.0, -0.7, -0.7),
    )
    for dx, dy, dz in rays:
        for s in range(9):
            f = (s + 1) / 9
            r = 8.0 + 78.0 * f
            builder.add(
                dx * r, top + dy * r, dz * r,
                GLYPH_INDEX["."] if f > 0.7 else GLYPH_INDEX["-"],
                GOLD_LIGHT if f > 0.5 else AMBER,
                STAR, T_STAR + 0.35, 0.0, 4.4,
            )


def build_tree(seed, target):
    rng = np.random.default_rng(seed)
    builder = Builder(rng)
    build_trunk(builder, int(target * 0.035))
    build_garland(builder, int(target * 0.075))
    build_baubles(builder, int(target * 0.052))
    build_lights(builder, int(target * 0.040))
    build_gifts(builder, int(target * 0.048))
    build_star(builder, int(target * 0.030))
    build_needles(builder, max(0, target - builder.count()))
    return builder.freeze()


class Tree:
    def __init__(self, data, seed):
        self.seed = seed
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.glyph = data["glyph"]
        self.color = data["color"]
        self.group = data["group"]
        self.appear = data["appear"]
        self.phase = data["phase"]
        self.freq = data["freq"]
        self.count = int(self.x.size)
        self.visible_cells = 0
        self.lights_ratio = 0.0

    def draw(self, framebuffer, t):
        theta = OMEGA * t
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        rx = self.x * cos_t - self.z * sin_t
        rz = self.x * sin_t + self.z * cos_t
        inv = FOCUS / (FOCUS + rz + Z_OFFSET)
        col = CENTER_X + rx * SCALE_X * inv
        row = CENTER_Y - self.y * SCALE_Y * inv

        live = self.appear <= t
        inside = live & (col >= 0.0) & (col < COLS) & (row >= 0.0) & (row < ROWS)
        selected = np.nonzero(inside)[0]
        if selected.size == 0:
            self.visible_cells = 0
            return

        ci = col[selected].astype(np.int32)
        ri = row[selected].astype(np.int32)
        depth = rz[selected]
        cell = ri * COLS + ci

        order = np.lexsort((depth, cell))
        cell_sorted = cell[order]
        first = np.empty(cell_sorted.size, dtype=bool)
        first[0] = True
        first[1:] = cell_sorted[1:] != cell_sorted[:-1]
        pick = order[first]
        chosen = selected[pick]

        depth_values = rz[chosen]
        span = TREE_RADIUS * 2.30
        shade = np.clip((depth_values + TREE_RADIUS * 1.15) / span, 0.0, 1.0)
        brightness = 1.0 - 0.34 * shade

        group = self.group[chosen]
        blink = 0.72 + 0.28 * (0.5 + 0.5 * np.sin(self.freq[chosen] * t + self.phase[chosen]))
        is_light = group == LIGHT
        is_star = group == STAR
        brightness = np.where(is_light, 1.0, brightness)
        star_pulse = 0.78 + 0.22 * math.sin(t * 3.1)
        brightness = np.where(is_star, brightness * star_pulse, brightness)

        color = self.color[chosen].copy()
        glyph = self.glyph[chosen].copy()
        peak = is_light & (blink > 0.82)
        glyph[is_light] = GLYPH_INDEX["*"]
        glyph[peak] = GLYPH_INDEX["@"]
        color[peak] = WARM

        level = np.clip((brightness * (LEVELS - 1)).astype(np.int32), 0, LEVELS - 1)
        level[is_light] = LEVELS - 1

        framebuffer.glyph[ri[pick], ci[pick]] = glyph
        framebuffer.color[ri[pick], ci[pick]] = color
        framebuffer.level[ri[pick], ci[pick]] = level

        if peak.any():
            glow_rows = ri[pick][peak]
            glow_cols = ci[pick][peak]
            glow_colors = color[peak]
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                nr = glow_rows + dr
                nc = glow_cols + dc
                ok = (nr >= 0) & (nr < ROWS) & (nc >= 0) & (nc < COLS)
                nr = nr[ok]
                nc = nc[ok]
                cc = glow_colors[ok]
                free = framebuffer.glyph[nr, nc] < 0
                framebuffer.glyph[nr[free], nc[free]] = GLYPH_INDEX["."]
                framebuffer.color[nr[free], nc[free]] = cc[free]
                framebuffer.level[nr[free], nc[free]] = 7

        self.visible_cells = int(chosen.size)
        if is_light.any():
            self.lights_ratio = float(np.count_nonzero(blink[is_light] > 0.9)) / float(np.count_nonzero(is_light))


class Background:
    def __init__(self, seed, stars, far_snow, near_snow):
        rng = np.random.default_rng(seed + 991)
        self.star_col = rng.integers(0, COLS, stars)
        self.star_row = rng.integers(0, ROWS, stars)
        self.star_phase = rng.uniform(0.0, math.tau, stars)
        self.star_freq = rng.uniform(0.6, 2.4, stars)
        self.star_power = rng.uniform(0.35, 1.0, stars)
        self.far = self.flake_set(rng, far_snow, 1.6, 4.6, 9)
        self.near = self.flake_set(rng, near_snow, 3.4, 8.4, 11)

    @staticmethod
    def flake_set(rng, count, slow, fast, level):
        return {
            "col": rng.uniform(0.0, COLS, count),
            "row": rng.uniform(0.0, ROWS, count),
            "speed": rng.uniform(slow, fast, count),
            "drift": rng.uniform(-1.8, 1.8, count),
            "sway": rng.uniform(0.4, 1.6, count),
            "phase": rng.uniform(0.0, math.tau, count),
            "glyph": rng.integers(0, 4, count),
            "level": level,
        }

    def draw(self, framebuffer, t):
        twinkle = 0.5 + 0.5 * np.sin(self.star_freq * t + self.star_phase)
        level = np.clip(2 + (twinkle * self.star_power * (LEVELS - 4)).astype(np.int32), 2, LEVELS - 2)
        glyph = np.where(self.star_power > 0.72, GLYPH_INDEX["*"], GLYPH_INDEX["."])
        framebuffer.glyph[self.star_row, self.star_col] = glyph
        framebuffer.color[self.star_row, self.star_col] = SNOW
        framebuffer.level[self.star_row, self.star_col] = level
        self.fall(framebuffer, self.far, t, False)

    def draw_front(self, framebuffer, t):
        self.fall(framebuffer, self.near, t, True)

    def fall(self, framebuffer, flakes, t, overwrite):
        rows = ((flakes["row"] + t * flakes["speed"]) % ROWS).astype(np.int32)
        sway = flakes["sway"] * np.sin(t * 0.9 + flakes["phase"])
        cols = ((flakes["col"] + t * flakes["drift"] + sway) % COLS).astype(np.int32)
        glyph = np.array([GLYPH_INDEX["."], GLYPH_INDEX["'"], GLYPH_INDEX["*"], GLYPH_INDEX["+"]], dtype=np.int16)
        picked = glyph[flakes["glyph"]]
        if overwrite:
            framebuffer.glyph[rows, cols] = picked
        else:
            free = framebuffer.glyph[rows, cols] < 0
            framebuffer.glyph[rows[free], cols[free]] = picked[free]
        framebuffer.color[rows, cols] = WHITE
        framebuffer.level[rows, cols] = flakes["level"]


class Framebuffer:
    def __init__(self):
        self.glyph = np.full((ROWS, COLS), -1, dtype=np.int16)
        self.color = np.zeros((ROWS, COLS), dtype=np.int16)
        self.level = np.zeros((ROWS, COLS), dtype=np.int16)

    def clear(self):
        self.glyph.fill(-1)
        self.color.fill(0)
        self.level.fill(0)

    def put(self, col, row, glyph, color, level):
        if 0 <= col < COLS and 0 <= row < ROWS:
            self.glyph[row, col] = glyph
            self.color[row, col] = color
            self.level[row, col] = level


class Atlas:
    def __init__(self, font):
        self.font = font
        self.tiles = {}
        self.shades = {}

    def shade(self, color_index, level):
        key = (color_index, level)
        cached = self.shades.get(key)
        if cached is None:
            base = PALETTE[color_index]
            factor = 0.55 + 0.45 * (level / (LEVELS - 1))
            cached = (
                min(255, int(base[0] * factor)),
                min(255, int(base[1] * factor)),
                min(255, int(base[2] * factor)),
            )
            self.shades[key] = cached
        return cached

    def tile(self, glyph_index, color_index, level):
        key = (glyph_index, color_index, level)
        cached = self.tiles.get(key)
        if cached is None:
            rgb = self.shade(color_index, level)
            rendered = self.font.render(GLYPH_CHARS[glyph_index], True, rgb, BG)
            tile = pygame.Surface((CELL_W, CELL_H))
            tile.fill(BG)
            tile.blit(
                rendered,
                (
                    (CELL_W - rendered.get_width()) // 2,
                    (CELL_H - rendered.get_height()) // 2,
                ),
            )
            cached = tile.convert()
            self.tiles[key] = cached
        return cached


def load_font(size, bold=False):
    here = os.path.dirname(os.path.abspath(__file__))
    for path in (os.path.join(here, "FiraMono-Regular.ttf"), "FiraMono-Regular.ttf"):
        if os.path.exists(path):
            try:
                font = pygame.font.Font(path, size)
                font.set_bold(bold)
                return font
            except (pygame.error, OSError):
                pass
    font = pygame.font.Font(None, size + 6)
    font.set_bold(bold)
    return font


def parse_args(argv):
    seed = SEED_DEFAULT
    fps = FPS
    if IS_WEB:
        return seed, fps
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--seed" and index + 1 < len(argv):
            seed = int(argv[index + 1])
            index += 1
        elif arg == "--fps" and index + 1 < len(argv):
            fps = max(1, int(argv[index + 1]))
            index += 1
        index += 1
    return seed, fps


class Bursts:
    def __init__(self):
        self.col = []
        self.row = []
        self.vx = []
        self.vy = []
        self.age = []
        self.life = []
        self.glyph = []
        self.rng = np.random.default_rng(2026)

    def spawn(self, col, row):
        count = 46
        angle = self.rng.uniform(0.0, math.tau, count)
        speed = self.rng.uniform(3.0, 17.0, count)
        self.col.extend([col] * count)
        self.row.extend([row] * count)
        self.vx.extend((np.cos(angle) * speed).tolist())
        self.vy.extend((np.sin(angle) * speed * 0.8 - 4.0).tolist())
        self.age.extend([0.0] * count)
        self.life.extend(self.rng.uniform(0.9, 1.9, count).tolist())
        self.glyph.extend(self.rng.integers(0, 4, count).tolist())

    def update(self, dt):
        if not self.col:
            return
        keep = []
        for i in range(len(self.col)):
            age = self.age[i] + dt
            if age >= self.life[i]:
                continue
            col = self.col[i] + self.vx[i] * dt
            row = self.row[i] + self.vy[i] * dt
            vy = self.vy[i] + 24.0 * dt
            if row > ROWS + 3 or col < -3 or col > COLS + 3:
                continue
            keep.append((col, row, self.vx[i], vy, age, self.life[i], self.glyph[i]))
        self.col = [k[0] for k in keep]
        self.row = [k[1] for k in keep]
        self.vx = [k[2] for k in keep]
        self.vy = [k[3] for k in keep]
        self.age = [k[4] for k in keep]
        self.life = [k[5] for k in keep]
        self.glyph = [k[6] for k in keep]

    def draw(self, framebuffer):
        flake = (GLYPH_INDEX["."], GLYPH_INDEX["'"], GLYPH_INDEX["*"], GLYPH_INDEX["+"])
        for i in range(len(self.col)):
            fade = 1.0 - self.age[i] / self.life[i]
            level = max(4, min(LEVELS - 1, int(3 + fade * 8)))
            framebuffer.put(int(self.col[i]), int(self.row[i]), flake[self.glyph[i]], WHITE, level)


class App:
    def __init__(self, seed, fps):
        self.fps = fps
        self.seed = seed
        self.t = 0.0
        self.paused = False
        self.running = True
        self.clock = pygame.time.Clock()
        self.font = load_font(12, bold=True)
        self.atlas = Atlas(self.font)
        self.framebuffer = Framebuffer()
        self.bursts = Bursts()
        self.screen = pygame.display.get_surface()
        self.tree = None
        self.background = None
        self.rebuild(seed)

    def rebuild(self, seed):
        self.seed = seed
        data = build_tree(seed, PARTICLES)
        self.tree = Tree(data, seed)
        self.background = Background(seed, 150, 300, 130)
        self.t = 0.0

    def letter_count(self):
        elapsed = self.t - T_TEXT
        if elapsed <= 0.0:
            return 0
        return min(len(TEXT), int(elapsed / LETTER_DELAY) + 1)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                col = event.pos[0] / CELL_W
                row = event.pos[1] / CELL_H
                self.bursts.spawn(col, row)

    def step(self, dt):
        if not self.paused:
            self.t += dt
        self.bursts.update(dt)
        self.draw()

    def draw(self):
        self.framebuffer.clear()
        self.background.draw(self.framebuffer, self.t)
        self.tree.draw(self.framebuffer, self.t)
        self.background.draw_front(self.framebuffer, self.t)
        self.bursts.draw(self.framebuffer)
        self.draw_overlay()
        self.compose()
        pygame.display.flip()

    def draw_overlay(self):
        fb = self.framebuffer
        letters = self.letter_count()
        if letters <= 0:
            return
        cycle = (GOLD_LIGHT, RUBY_LIGHT, EMERALD_LIGHT, SAPPHIRE_LIGHT, SILVER, AMBER)
        for index, ch, col, top in BANNER_CELLS:
            if index >= letters:
                continue
            pattern = BANNER_FONT.get(ch)
            if pattern is None:
                continue
            color = cycle[index % len(cycle)]
            for r, line in enumerate(pattern):
                for c, mark in enumerate(line):
                    if mark == "#":
                        fb.put(col + c, top + r, GLYPH_INDEX["#"], color, LEVELS - 1)

    def compose(self):
        fb = self.framebuffer
        self.screen.fill(BG)
        rows, cols = np.nonzero(fb.glyph >= 0)
        if rows.size == 0:
            return
        glyphs = fb.glyph[rows, cols]
        colors = fb.color[rows, cols]
        levels = fb.level[rows, cols]
        blits = [
            (
                self.atlas.tile(int(glyphs[i]), int(colors[i]), int(levels[i])),
                (int(cols[i]) * CELL_W, int(rows[i]) * CELL_H),
            )
            for i in range(rows.size)
        ]
        self.screen.blits(blits, doreturn=False)


async def main():
    seed, fps = parse_args(sys.argv[1:])
    pygame.init()
    pygame.display.set_caption(TITLE)
    try:
        pygame.display.set_mode((WIDTH, HEIGHT_PX), pygame.SCALED)
    except pygame.error:
        pygame.display.set_mode((WIDTH, HEIGHT_PX))
    app = App(seed, fps)
    while app.running:
        app.handle_events()
        app.step(app.clock.tick(fps) / 1000.0)
        await asyncio.sleep(0)
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
