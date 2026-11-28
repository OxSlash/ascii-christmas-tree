import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")

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
      resolve(JSON.stringify({
        median_ms: +sorted[Math.floor(sorted.length / 2)].toFixed(2),
        worst_ms: +sorted[sorted.length - 1].toFixed(2),
        fps: +(1000 / sorted[Math.floor(sorted.length / 2)]).toFixed(1)
      }));
    }
  }
  requestAnimationFrame(tick);
}))()
"""

STAGES = """
(() => {
  const N = 30;
  state.paused = true;
  state.t = 20.0;
  let t0 = performance.now();
  for (let i = 0; i < N; i++) drawSky(state.t);
  let t1 = performance.now();
  for (let i = 0; i < N; i++) { fb.clear(); drawBackground(state.t); drawTree(state.t); drawFront(state.t); drawBursts(); drawOverlay(); }
  let t2 = performance.now();
  for (let i = 0; i < N; i++) compose();
  let t3 = performance.now();
  return JSON.stringify({
    sky_ms: +((t1 - t0) / N).toFixed(2),
    frame_build_ms: +((t2 - t1) / N).toFixed(2),
    compose_ms: +((t3 - t2) / N).toFixed(2)
  });
})()
"""


def raf(probe, ident):
    probe.ws.send(
        '{"id":%d,"method":"Runtime.evaluate","params":{"expression":%s,"awaitPromise":true,"returnByValue":true}}'
        % (ident, repr(RAF).replace("'", '"'))
    )
    import json

    while True:
        msg = json.loads(probe.ws.recv())
        if msg.get("id") == ident:
            return msg.get("result", {}).get("result", {}).get("value")


def main():
    sizes = (
        ("laptop-1536x730", 1536, 730),
        ("macbook-1440x900", 1440, 900),
        ("desktop-1920x1080", 1920, 1080),
        ("ipad-1024x768", 1024, 768),
    )
    for index, (name, w, h) in enumerate(sizes):
        with Headless(9850 + index, f"perfwide-{name}", w, h) as probe:
            probe.goto("file:///" + TARGET.replace("\\", "/"))
            time.sleep(4)
            print(name, "stages", evaluate(probe.ws, 20, STAGES), flush=True)
            print(name, "raf", raf(probe, 30), flush=True)


if __name__ == "__main__":
    main()
