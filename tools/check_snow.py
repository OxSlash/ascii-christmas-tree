import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, call, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
OUT = os.path.join(os.environ["TEMP"], "opencode")

STATE = "JSON.stringify({paused: state.paused, bursts: bursts.length})"


def mouse(probe, ident, kind, x, y, button):
    call(
        probe.ws,
        ident,
        "Input.dispatchMouseEvent",
        {
            "type": kind,
            "x": x,
            "y": y,
            "button": button,
            "buttons": 0 if kind == "mouseReleased" else {"left": 1, "right": 2, "middle": 4}[button],
            "clickCount": 1,
            "pointerType": "mouse",
        },
    )


def click(probe, ident, x, y, button):
    mouse(probe, ident, "mousePressed", x, y, button)
    mouse(probe, ident + 1, "mouseReleased", x, y, button)


def clear(probe, ident):
    evaluate(probe.ws, ident, "bursts.length = 0; true")


def count(probe, ident):
    return evaluate(probe.ws, ident, STATE)


def main():
    failures = []
    with Headless(9640, "probe-snow", 1510, 590) as probe:
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        evaluate(probe.ws, 19, "state.paused = true; true")
        geom = evaluate(
            probe.ws,
            20,
            "JSON.stringify({w: canvas.width, h: canvas.height, grid: GRID})",
        )
        print("geom", geom, flush=True)

        cases = (
            ("left far-left sky", 60, 300, "left", True),
            ("left far-right sky", 1450, 300, "left", True),
            ("left centre", 755, 300, "left", True),
            ("right button", 755, 300, "right", False),
            ("middle button", 755, 300, "middle", False),
        )
        ident = 100
        for label, x, y, button, expected in cases:
            clear(probe, ident)
            ident += 1
            click(probe, ident, x, y, button)
            ident += 2
            time.sleep(0.15)
            raw = count(probe, ident)
            ident += 1
            got = int(raw.split('"bursts":')[1].rstrip("}"))
            ok = (got > 0) == expected
            if not ok:
                failures.append(label)
            print(f"{label:22s} button={button:6s} bursts={got:3d} expected={'some' if expected else 'none':4s} {'OK' if ok else 'FAIL'}", flush=True)

        clear(probe, ident)
        ident += 1
        mouse(probe, ident, "mousePressed", 755, 300, "left")
        ident += 1
        time.sleep(1.0)
        held = count(probe, ident)
        ident += 1
        mouse(probe, ident, "mouseReleased", 755, 300, "left")
        ident += 1
        held_count = int(held.split('"bursts":')[1].rstrip("}"))
        ok = 0 < held_count <= 34
        if not ok:
            failures.append("long left press")
        print(f"{'long left press':22s} button=left   bursts={held_count:3d} expected=<=34 {'OK' if ok else 'FAIL'}", flush=True)

        clear(probe, ident)
        ident += 1
        mouse(probe, ident, "mousePressed", 200, 300, "left")
        ident += 1
        for step in range(10):
            mouse(probe, ident, "mouseMoved", 200 + step * 40, 300, "left")
            ident += 1
            time.sleep(0.06)
        mouse(probe, ident, "mouseReleased", 560, 300, "left")
        ident += 1
        dragged = count(probe, ident)
        ident += 1
        dragged_count = int(dragged.split('"bursts":')[1].rstrip("}"))
        ok = dragged_count > 34
        if not ok:
            failures.append("drag")
        print(f"{'drag across sky':22s} button=left   bursts={dragged_count:3d} expected= >34 {'OK' if ok else 'FAIL'}", flush=True)

        evaluate(probe.ws, ident, "bursts.length = 0; state.paused = true; state.t = 20; true")
        ident += 1
        click(probe, ident, 90, 260, "left")
        ident += 2
        time.sleep(0.1)
        evaluate(probe.ws, ident, "drawFrame(); true")
        ident += 1
        probe.shot(os.path.join(OUT, "snow-left-sky.png"))
        evaluate(probe.ws, ident, "bursts.length = 0; true")
        ident += 1
        click(probe, ident, 1430, 260, "left")
        ident += 2
        time.sleep(0.1)
        evaluate(probe.ws, ident, "drawFrame(); true")
        ident += 1
        probe.shot(os.path.join(OUT, "snow-right-sky.png"))

    print("FAILURES", failures, flush=True)


if __name__ == "__main__":
    main()
