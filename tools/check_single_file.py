import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
OUT = os.path.join(os.environ["TEMP"], "opencode")


def main():
    with Headless(9510, "probe-desktop", 1280, 1160) as probe:
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        state = evaluate(probe.ws, 20, "typeof state")
        print("state_type", state)
        evaluate(probe.ws, 21, "state.paused = true; state.t = 20.0; drawFrame(); true")
        info = evaluate(
            probe.ws,
            22,
            "JSON.stringify({view: VIEW, canvas: [canvas.width, canvas.height], css: [canvas.style.width, canvas.style.height], cells: visibleCells, letters: letterCount(), fira: document.fonts.check('bold 12px FiraMonoEmbedded')})",
        )
        print("info", info)
        size = probe.shot(os.path.join(OUT, "desktop-single.png"))
        print("saved", size, "bytes", flush=True)


if __name__ == "__main__":
    main()
