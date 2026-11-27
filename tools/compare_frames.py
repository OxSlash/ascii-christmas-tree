import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
NATIVE = os.path.join(os.environ["TEMP"], "opencode", "native_frame.json")


def main():
    native = json.load(open(NATIVE, encoding="utf-8"))
    with Headless(9511, "probe-compare", 1280, 1160) as probe:
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        evaluate(probe.ws, 20, "state.paused = true; state.t = 20.0; drawFrame(); true")
        payload = evaluate(
            probe.ws,
            21,
            "JSON.stringify({glyph: Array.from(fb.glyph), color: Array.from(fb.color), level: Array.from(fb.level), cells: visibleCells})",
        )
        web = json.loads(payload)

    gh, gc, gl = web["glyph"], web["color"], web["level"]
    nh = [v for row in native["glyph"] for v in row]
    nc = [v for row in native["color"] for v in row]
    nl = [v for row in native["level"] for v in row]

    skip = set()
    for r in (0, 1):
        for c in range(88):
            skip.add(r * 88 + c)
    for r in range(68, 74):
        for c in range(88):
            skip.add(r * 88 + c)

    glyph_same = color_same = level_same = checked = both_lit = 0
    mismatch = []
    for i in range(len(nh)):
        if i in skip:
            continue
        checked += 1
        if gh[i] == nh[i]:
            glyph_same += 1
        else:
            mismatch.append((i // 88, i % 88, nh[i], gh[i], nl[i], gl[i]))
        if gc[i] == nc[i]:
            color_same += 1
        if gl[i] == nl[i]:
            level_same += 1
        if gh[i] >= 0 and nh[i] >= 0:
            both_lit += 1

    print(f"native_cells {native['cells']}  web_cells {web['cells']}")
    print(f"compared {checked} cells")
    print(f"glyph_match {glyph_same}/{checked} ({100*glyph_same/checked:.2f}%)")
    print(f"color_match {color_same}/{checked} ({100*color_same/checked:.2f}%)")
    print(f"level_match {level_same}/{checked} ({100*level_same/checked:.2f}%)")
    print(f"both_lit {both_lit}  glyph_mismatches {len(mismatch)}")
    for m in mismatch[:10]:
        print("  row", m[0], "col", m[1], "native", m[2], m[4], "web", m[3], m[5])


if __name__ == "__main__":
    main()
