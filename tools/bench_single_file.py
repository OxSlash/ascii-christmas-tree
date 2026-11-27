import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")


def measure(port, profile, seconds=6.0):
    with Headless(port, profile, 1280, 1160) as probe:
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        evaluate(probe.ws, 20, "state.paused = false; state.t = 14.0; true")
        evaluate(probe.ws, 21, "window.__cnt = 0; window.__t0 = performance.now(); (function tick(){ window.__cnt++; requestAnimationFrame(tick); })(); true")
        time.sleep(seconds)
        count = evaluate(probe.ws, 22, "window.__cnt")
        elapsed = evaluate(probe.ws, 23, "performance.now() - window.__t0")
        return count / (elapsed / 1000.0)


def main():
    results = []
    for index in range(3):
        fps = measure(9520 + index, f"probe-bench{index}")
        results.append(fps)
        print(f"run {index+1}: {fps:.1f} fps", flush=True)
    ordered = sorted(results)
    print(f"median {ordered[1]:.1f} fps  min {ordered[0]:.1f}  max {ordered[2]:.1f}")


if __name__ == "__main__":
    main()
