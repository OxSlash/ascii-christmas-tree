import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_probe import Headless, call, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")


def main():
    with Headless(9610, "probe-diag", 390, 844, mobile=True) as probe:
        call(probe.ws, 5, "Log.enable")
        probe.goto("file:///" + TARGET.replace("\\", "/"))
        time.sleep(4)
        print("state:", evaluate(probe.ws, 20, "typeof state"))
        print("atlas_keys:", evaluate(probe.ws, 21, "atlas.pixels.size"))
        print("try_tile:", evaluate(probe.ws, 22, "(() => { try { const d = atlas.tile(3, 2, 9); return 'len ' + d.length; } catch (e) { return 'ERR ' + e.message; } })()"))
        print("canvas:", evaluate(probe.ws, 23, "JSON.stringify({w: canvas.width, h: canvas.height, cw: CW, ch: CH, view: VIEW})"))
        print("compose:", evaluate(probe.ws, 24, "(() => { try { state.t = 20; drawFrame(); return 'ok'; } catch (e) { return 'ERR ' + e.message + ' | ' + e.stack.split('\\n')[1]; } })()"))
        print("pixels_sample:", evaluate(probe.ws, 25, "(() => { const d = sctx.getImageData(0,0,20,20).data; let sum=0; for (let i=0;i<d.length;i++) sum+=d[i]; return sum; })()"))


if __name__ == "__main__":
    main()
