import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, call, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")

STATE = "JSON.stringify({paused: state.paused, bursts: bursts.length})"


def touch(probe, ident, kind, points):
    call(
        probe.ws,
        ident,
        "Input.dispatchTouchEvent",
        {"type": kind, "touchPoints": points},
    )


def count(probe, ident):
    raw = evaluate(probe.ws, ident, STATE)
    return int(raw.split('"bursts":')[1].rstrip("}"))


def main():
    failures = []
    with Headless(9641, "probe-touch", 390, 844, mobile=True) as probe:
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        evaluate(probe.ws, 19, "state.paused = true; true")
        ident = 100

        for label, x, y, expected in (
            ("tap centre", 195, 420, True),
            ("tap left sky", 20, 420, True),
            ("tap right sky", 370, 420, True),
        ):
            evaluate(probe.ws, ident, "bursts.length = 0; true")
            ident += 1
            touch(probe, ident, "touchStart", [{"x": x, "y": y, "id": 1}])
            ident += 1
            touch(probe, ident, "touchEnd", [])
            ident += 1
            time.sleep(0.15)
            got = count(probe, ident)
            ident += 1
            ok = (got > 0) == expected
            if not ok:
                failures.append(label)
            print(f"{label:18s} bursts={got:3d} {'OK' if ok else 'FAIL'}", flush=True)

        evaluate(probe.ws, ident, "bursts.length = 0; true")
        ident += 1
        touch(probe, ident, "touchStart", [{"x": 60, "y": 500, "id": 1}])
        ident += 1
        for step in range(8):
            touch(probe, ident, "touchMove", [{"x": 60 + step * 40, "y": 500, "id": 1}])
            ident += 1
            time.sleep(0.06)
        touch(probe, ident, "touchEnd", [])
        ident += 1
        dragged = count(probe, ident)
        ident += 1
        ok = dragged > 34
        if not ok:
            failures.append("touch drag")
        print(f"{'touch drag':18s} bursts={dragged:3d} {'OK' if ok else 'FAIL'}", flush=True)

        paused = evaluate(probe.ws, ident, "state.paused")
        ident += 1
        if paused is not True:
            failures.append("pause")
        print(f"{'stays paused':18s} paused={paused} {'OK' if paused is True else 'FAIL'}", flush=True)

    print("FAILURES", failures, flush=True)


if __name__ == "__main__":
    main()
