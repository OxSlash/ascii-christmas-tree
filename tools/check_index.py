import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
OUT = os.path.join(os.environ["TEMP"], "opencode")


def main():
    with Headless(9530, "probe-index", 390, 844, mobile=True) as probe:
        probe.goto("file:///" + INDEX.replace("\\", "/"))
        time.sleep(5)
        url = evaluate(probe.ws, 20, "location.pathname")
        ready = evaluate(probe.ws, 21, "typeof state")
        print("pathname", url)
        print("state_type", ready)
        if ready == "object":
            evaluate(probe.ws, 22, "state.paused = true; state.t = 20.0; drawFrame(); true")
            cells = evaluate(probe.ws, 23, "visibleCells")
            letters = evaluate(probe.ws, 24, "letterCount()")
            print("cells", cells, "letters", letters)
        size = probe.shot(os.path.join(OUT, "index-redirect.png"))
        print("saved", size, "bytes")


if __name__ == "__main__":
    main()
