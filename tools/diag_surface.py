import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")

PROBE = """
(() => {
  state.paused = true;
  state.t = 20.0;
  fb.clear();
  drawBackground(state.t);
  drawTree(state.t);
  drawFront(state.t);
  drawOverlay();
  const c0 = 0, c1 = COLS, r0 = 0, r1 = ROWS;
  let lit = 0, minR = 1e9, maxR = -1;
  for (let r = r0; r < r1; r++) {
    for (let c = c0; c < c1; c++) {
      if (fb.glyph[r * COLS + c] >= 0) {
        lit++;
        if (r < minR) minR = r;
        if (r > maxR) maxR = r;
      }
    }
  }
  compose();
  const d = sctx.getImageData(0, 0, surface.width, surface.height).data;
  let sMinY = 1e9, sMaxY = -1, sMinX = 1e9, sMaxX = -1;
  const bg = [CFG.bg[0], CFG.bg[1], CFG.bg[2]];
  for (let y = 0; y < surface.height; y++) {
    for (let x = 0; x < surface.width; x++) {
      const i = (y * surface.width + x) * 4;
      if (Math.abs(d[i] - bg[0]) > 12 || Math.abs(d[i+1] - bg[1]) > 12 || Math.abs(d[i+2] - bg[2]) > 12) {
        if (x < sMinX) sMinX = x; if (x > sMaxX) sMaxX = x;
        if (y < sMinY) sMinY = y; if (y > sMaxY) sMaxY = y;
      }
    }
  }
  return JSON.stringify({
    fbLit: lit, fbRows: [minR, maxR],
    surface: [surface.width, surface.height],
    surfaceBox: [sMinX, sMinY, sMaxX, sMaxY],
    canvas: [canvas.width, canvas.height],
    view: VIEW
  });
})()
"""


def main():
    with Headless(9621, "probe-surface", 390, 844, mobile=True) as probe:
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        print(evaluate(probe.ws, 20, PROBE))


if __name__ == "__main__":
    main()
