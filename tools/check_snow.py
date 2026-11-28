import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, call, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
OUT = os.path.join(os.environ["TEMP"], "opencode")


def main():
    with Headless(9640, "probe-snow", 390, 844, mobile=True) as probe:
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        before = evaluate(
            probe.ws,
            20,
            "JSON.stringify({paused: state.paused, t: +state.t.toFixed(2), bursts: bursts.length})",
        )
        print("before", before)
        probe.shot(os.path.join(OUT, "snow-before.png"))
        for i in range(3):
            call(
                probe.ws,
                30 + i,
                "Input.dispatchMouseEvent",
                {
                    "type": "mousePressed",
                    "x": 200,
                    "y": 400,
                    "button": "left",
                    "clickCount": 1,
                    "pointerType": "mouse",
                },
            )
            call(
                probe.ws,
                40 + i,
                "Input.dispatchMouseEvent",
                {
                    "type": "mouseReleased",
                    "x": 200,
                    "y": 400,
                    "button": "left",
                    "clickCount": 1,
                    "pointerType": "mouse",
                },
            )
            time.sleep(0.2)
        time.sleep(0.3)
        after = evaluate(
            probe.ws,
            21,
            "JSON.stringify({paused: state.paused, t: +state.t.toFixed(2), bursts: bursts.length, first: bursts[0] ? [+bursts[0].col.toFixed(1), +bursts[0].row.toFixed(1)] : null})",
        )
        print("after", after)
        probe.shot(os.path.join(OUT, "snow-after.png"))


if __name__ == "__main__":
    main()
