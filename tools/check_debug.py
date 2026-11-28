import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
OUT = os.path.join(os.environ["TEMP"], "opencode")


def main():
    with Headless(9540, "probe-debug", 390, 844, mobile=True) as probe:
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        clean = evaluate(
            probe.ws,
            20,
            "(() => { state.paused = true; state.t = 20.0; state.debug = false; drawFrame(); return JSON.stringify({cells: visibleCells, letters: letterCount()}); })()",
        )
        print("clean", clean)
        probe.shot(os.path.join(OUT, "debug-off.png"))
        debug = evaluate(
            probe.ws,
            21,
            "(() => { state.debug = true; drawFrame(); return JSON.stringify({debug: state.debug}); })()",
        )
        print("debug", debug)
        probe.shot(os.path.join(OUT, "debug-on.png"))


if __name__ == "__main__":
    main()
