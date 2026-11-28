import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
OUT = os.path.join(os.environ["TEMP"], "opencode")

DEVICES = (
    ("iphone-se-375x667", 375, 667),
    ("iphone-15-393x852", 393, 852),
    ("iphone-max-430x932", 430, 932),
    ("android-360x800", 360, 800),
    ("android-412x915", 412, 915),
    ("tablet-768x1024", 768, 1024),
    ("landscape-844x390", 844, 390),
)


def main():
    for index, (name, width, height) in enumerate(DEVICES):
        with Headless(9700 + index, f"resp-{name}", width, height, mobile=True) as probe:
            probe.goto("file:///" + TARGET.replace("\\", "/"))
            time.sleep(3.5)
            evaluate(probe.ws, 20, "state.paused = true; state.t = 20.0; drawFrame(); true")
            info = evaluate(
                probe.ws,
                21,
                "JSON.stringify({inner: [innerWidth, innerHeight], view: [VIEW.w, VIEW.h], css: [canvas.style.width, canvas.style.height], scale: +(canvas.style.width.replace('px','') / VIEW.w).toFixed(2), cells: visibleCells})",
            )
            probe.shot(os.path.join(OUT, f"resp-{name}.png"))
            print(f"{name}: {info}", flush=True)


if __name__ == "__main__":
    main()
