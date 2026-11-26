import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_single_file import WebSocket, call, evaluate

TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
NATIVE = os.path.join(os.environ["TEMP"], "opencode", "native_frame.json")


def main():
    import subprocess
    import time
    import urllib.request

    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
    time.sleep(1)
    profile = os.path.join(os.environ["TEMP"], "opencode", "chrome-cmp")
    os.makedirs(profile, exist_ok=True)
    chrome = subprocess.Popen(
        [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "--headless=new",
            "--no-sandbox",
            "--window-size=980,1160",
            "--remote-debugging-port=9225",
            f"--user-data-dir={profile}",
            "--allow-file-access-from-files",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        target = None
        for _ in range(60):
            try:
                data = json.load(urllib.request.urlopen("http://127.0.0.1:9225/json/list", timeout=2))
                pages = [t for t in data if t.get("type") == "page"]
                if pages:
                    target = pages[0]
                    break
            except Exception:
                pass
            time.sleep(0.5)
        ws = WebSocket(target["webSocketDebuggerUrl"])
        call(ws, 1, "Page.enable")
        call(ws, 2, "Runtime.enable")
        call(ws, 3, "Page.navigate", {"url": "file:///" + TARGET.replace("\\", "/")})
        time.sleep(4)
        evaluate(ws, 4, "state.paused = true; state.t = 20.0; drawFrame(); true")
        payload = evaluate(
            ws,
            5,
            "JSON.stringify({glyph: Array.from(fb.glyph), color: Array.from(fb.color), level: Array.from(fb.level), cells: visibleCells})",
        )
        web = json.loads(payload)
        native = json.load(open(NATIVE, encoding="utf-8"))

        gh = web["glyph"]
        gc = web["color"]
        gl = web["level"]
        nh = [v for row in native["glyph"] for v in row]
        nc = [v for row in native["color"] for v in row]
        nl = [v for row in native["level"] for v in row]

        total = len(nh)
        skip = set()
        for r in (0, 1):
            for c in range(88):
                skip.add(r * 88 + c)
        for r in range(68, 74):
            for c in range(88):
                skip.add(r * 88 + c)

        glyph_same = 0
        color_same = 0
        level_same = 0
        checked = 0
        both_lit = 0
        mismatch = []
        for i in range(total):
            if i in skip:
                continue
            checked += 1
            if gh[i] == nh[i]:
                glyph_same += 1
            else:
                mismatch.append((i // 88, i % 88, nh[i], gh[i], nl[i], gl[i]))
            if gc[i] == nc[i]:
                color_same += 1
            if gl[i] == nl[i]:
                level_same += 1
            if gh[i] >= 0 and nh[i] >= 0:
                both_lit += 1

        print(f"native_cells {native['cells']}  web_cells {web['cells']}")
        print(f"compared {checked} cells (tree, snow, banner)")
        print(f"glyph_match {glyph_same}/{checked} ({100*glyph_same/checked:.2f}%)")
        print(f"color_match {color_same}/{checked} ({100*color_same/checked:.2f}%)")
        print(f"level_match {level_same}/{checked} ({100*level_same/checked:.2f}%)")
        print(f"both_lit {both_lit}  glyph_mismatches {len(mismatch)}")
        for m in mismatch[:15]:
            print("  row", m[0], "col", m[1], "native", m[2], m[4], "web", m[3], m[5])
    finally:
        chrome.terminate()
        time.sleep(1)
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)


if __name__ == "__main__":
    main()
