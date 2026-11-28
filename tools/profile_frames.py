import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")

PROFILE = """
(() => {
  const N = 40;
  state.paused = true;
  state.t = 20.0;
  let t0 = performance.now();
  for (let i = 0; i < N; i++) {
    fb.clear();
    drawBackground(state.t);
    drawFront(state.t);
    drawOverlay();
  }
  let t1 = performance.now();
  for (let i = 0; i < N; i++) drawTree(state.t);
  let t2 = performance.now();
  for (let i = 0; i < N; i++) compose();
  let t3 = performance.now();
  return JSON.stringify({
    bg_overlay_ms: +((t1 - t0) / N).toFixed(2),
    tree_ms: +((t2 - t1) / N).toFixed(2),
    compose_ms: +((t3 - t2) / N).toFixed(2),
    cells: visibleCells,
    tiles: atlas.tiles.size
  });
})()
"""

RAF = """
(() => new Promise((resolve) => {
  const times = [];
  let last = performance.now();
  let n = 0;
  function tick(now) {
    times.push(now - last);
    last = now;
    if (++n < 90) requestAnimationFrame(tick);
    else {
      const sorted = times.slice(5).sort((a, b) => a - b);
      const mid = sorted[Math.floor(sorted.length / 2)];
      const worst = sorted[sorted.length - 1];
      resolve(JSON.stringify({ median_ms: +mid.toFixed(2), worst_ms: +worst.toFixed(2), fps: +(1000 / mid).toFixed(1) }));
    }
  }
  requestAnimationFrame(tick);
}))()
"""


def main():
    sizes = (("desktop", 1280, 1000, False), ("iphone", 390, 844, True), ("android", 360, 640, True))
    for index, (name, w, h, mobile) in enumerate(sizes):
        with Headless(9600 + index, f"perf-{name}", w, h, mobile=mobile) as probe:
            probe.goto("file:///" + TARGET.replace("\\", "/"))
            time.sleep(4)
            print(name, "profile", evaluate(probe.ws, 20, PROFILE), flush=True)
            probe.ws.send('{"id":30,"method":"Runtime.evaluate","params":{"expression":' + repr(RAF).replace("'", '"') + ',"awaitPromise":true,"returnByValue":true}}')
            while True:
                import json
                msg = json.loads(probe.ws.recv())
                if msg.get("id") == 30:
                    print(name, "raf", msg.get("result", {}).get("result", {}).get("value"))
                    break


if __name__ == "__main__":
    main()
