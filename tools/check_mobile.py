import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
OUT = os.path.join(os.environ["TEMP"], "opencode")

DEVICES = (
    ("iphone-390x844", 390, 844),
    ("android-360x640", 360, 640),
    ("pixel-412x915", 412, 915),
)


def main():
    for index, (name, width, height) in enumerate(DEVICES):
        with Headless(9500 + index, f"probe-{name}", width, height, mobile=True) as probe:
            probe.goto("file:///" + TARGET.replace("\\", "/"))
            time.sleep(4)
            evaluate(probe.ws, 20, "state.paused = true; state.t = 20.0; drawFrame(); true")
            info = evaluate(
                probe.ws,
                21,
                "JSON.stringify({view: VIEW, canvas: [canvas.width, canvas.height], css: [canvas.style.width, canvas.style.height], inner: [innerWidth, innerHeight], cells: visibleCells, letters: letterCount()})",
            )
            size = probe.shot(os.path.join(OUT, f"mobile-{name}.png"))
            print(f"{name}: {info}")
            print(f"  {size} bytes", flush=True)


if __name__ == "__main__":
    main()
