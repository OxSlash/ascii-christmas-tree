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
  drawFrame();
  const d = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
  let minX = 1e9, minY = 1e9, maxX = -1, maxY = -1;
  const bg = [CFG.bg[0], CFG.bg[1], CFG.bg[2]];
  for (let y = 0; y < canvas.height; y++) {
    for (let x = 0; x < canvas.width; x++) {
      const i = (y * canvas.width + x) * 4;
      if (Math.abs(d[i] - bg[0]) > 12 || Math.abs(d[i+1] - bg[1]) > 12 || Math.abs(d[i+2] - bg[2]) > 12) {
        if (x < minX) minX = x; if (x > maxX) maxX = x;
        if (y < minY) minY = y; if (y > maxY) maxY = y;
      }
    }
  }
  return JSON.stringify({
    canvas: [canvas.width, canvas.height],
    view: VIEW,
    contentBox: [minX, minY, maxX, maxY],
    surface: [surface.width, surface.height],
    fbCells: visibleCells
  });
})()
"""


def main():
    with Headless(9620, "probe-bounds", 390, 844, mobile=True) as probe:
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        print(evaluate(probe.ws, 20, PROBE))


if __name__ == "__main__":
    main()
