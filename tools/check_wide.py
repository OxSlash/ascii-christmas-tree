import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
OUT = os.path.join(os.environ["TEMP"], "opencode")

DEVICES = (
    ("laptop-1536x730", 1536, 730, False),
    ("macbook-1440x900", 1440, 900, False),
    ("ipad-land-1024x768", 1024, 768, False),
    ("ipad-port-768x1024", 768, 1024, False),
    ("desktop-1920x1080", 1920, 1080, False),
)

PROBE = """
JSON.stringify({
  inner: [innerWidth, innerHeight],
  canvas: [canvas.width, canvas.height],
  grid: GRID,
  view: VIEW,
  cells: visibleCells,
  letters: letterCount()
})
"""


def main():
    for index, (name, w, h, mobile) in enumerate(DEVICES):
        with Headless(9800 + index, f"wide-{name}", w, h, mobile=mobile) as probe:
            probe.goto("file:///" + TARGET.replace("\\", "/"))
            time.sleep(4)
            evaluate(probe.ws, 20, "state.paused = true; state.t = 20.0; drawFrame(); true")
            info = evaluate(probe.ws, 21, PROBE)
            probe.shot(os.path.join(OUT, f"wide-{name}.png"))
            print(f"{name}: {info}", flush=True)


if __name__ == "__main__":
    main()
