import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_single_file import WebSocket, call, evaluate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")


def run(port, profile_name, seconds=6.0):
    profile = os.path.join(os.environ["TEMP"], "opencode", profile_name)
    os.makedirs(profile, exist_ok=True)
    chrome = subprocess.Popen(
        [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "--headless=new",
            "--no-sandbox",
            "--hide-scrollbars",
            "--window-size=980,1160",
            f"--remote-debugging-port={port}",
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
                data = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=2))
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
        evaluate(ws, 4, "state.paused = false; state.t = 14.0; true")
        start = time.time()
        evaluate(ws, 5, "window.__f0 = 0; window.__t0 = performance.now(); true")
        evaluate(ws, 6, "window.__cnt = 0; (function tick(){ window.__cnt++; requestAnimationFrame(tick); })(); true")
        time.sleep(seconds)
        count = evaluate(ws, 7, "window.__cnt")
        elapsed = evaluate(ws, 8, "performance.now() - window.__t0")
        return count / (elapsed / 1000.0)
    finally:
        chrome.terminate()
        time.sleep(1)
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)


if __name__ == "__main__":
    results = []
    for i in range(3):
        fps = run(9300 + i, f"chrome-perf{i}")
        results.append(fps)
        print(f"run {i+1}: {fps:.1f} fps")
    print(f"median {sorted(results)[1]:.1f} fps  min {min(results):.1f}  max {max(results):.1f}")
