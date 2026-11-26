import base64
import json
import os
import socket
import struct
import subprocess
import time
import urllib.request
from urllib.parse import urlparse

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9224
PROFILE = os.path.join(os.environ["TEMP"], "opencode", "chrome-single")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "dist", "ascii-christmas-tree.html")
OUT = os.path.join(os.environ["TEMP"], "opencode", "single_shot.png")


class WebSocket:
    def __init__(self, url):
        parts = urlparse(url)
        self.sock = socket.create_connection((parts.hostname, parts.port), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        path = parts.path or "/"
        if parts.query:
            path += "?" + parts.query
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {parts.hostname}:{parts.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(request.encode())
        buffer = b""
        while b"\r\n\r\n" not in buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("handshake closed")
            buffer += chunk
        if b"101" not in buffer.split(b"\r\n", 1)[0]:
            raise RuntimeError(buffer.decode(errors="replace"))

    def send(self, text):
        payload = text.encode()
        header = bytearray([0x81])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", length)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", length)
        mask = os.urandom(4)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def _read(self, n):
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise RuntimeError("socket closed")
            data += chunk
        return data

    def recv(self):
        while True:
            first = self._read(2)
            opcode = first[0] & 0x0F
            masked = first[1] & 0x80
            length = first[1] & 0x7F
            if length == 126:
                length = struct.unpack(">H", self._read(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self._read(8))[0]
            mask = self._read(4) if masked else None
            payload = self._read(length)
            if mask:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            if opcode == 0x9:
                self.sock.sendall(b"\x8a\x80" + os.urandom(4))
                continue
            if opcode in (0x1, 0x2):
                return payload.decode(errors="replace")


def call(ws, ident, method, params=None):
    ws.send(json.dumps({"id": ident, "method": method, "params": params or {}}))
    while True:
        message = json.loads(ws.recv())
        if message.get("id") == ident:
            return message


def evaluate(ws, ident, expression):
    result = call(ws, ident, "Runtime.evaluate", {"expression": expression, "returnByValue": True})
    return result.get("result", {}).get("result", {}).get("value")


def main():
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
    time.sleep(1)
    os.makedirs(PROFILE, exist_ok=True)
    chrome = subprocess.Popen(
        [
            CHROME,
            "--headless=new",
            "--no-sandbox",
            "--hide-scrollbars",
            "--window-size=980,1160",
            f"--remote-debugging-port={PORT}",
            f"--user-data-dir={PROFILE}",
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
                data = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=2))
                pages = [t for t in data if t.get("type") == "page"]
                if pages:
                    target = pages[0]
                    break
            except Exception:
                pass
            time.sleep(0.5)
        if target is None:
            raise RuntimeError("no chrome target")
        ws = WebSocket(target["webSocketDebuggerUrl"])
        call(ws, 1, "Page.enable")
        call(ws, 2, "Runtime.enable")
        call(ws, 3, "Page.navigate", {"url": "file:///" + TARGET.replace("\\", "/")})
        time.sleep(4)
        errors = evaluate(ws, 4, "window.__errs ? JSON.stringify(window.__errs) : 'none'")
        state_info = evaluate(ws, 5, "typeof state")
        print("state_type", state_info, "errors", errors)
        if state_info != "object":
            raise RuntimeError("script did not initialise")
        evaluate(ws, 6, "state.t = 20.0; true")
        time.sleep(1.5)
        info = evaluate(
            ws,
            7,
            "JSON.stringify({t: state.t, fps: Math.round(fpsValue*10)/10, cells: visibleCells, n: TREE.n, tiles: atlas.tiles.size, letters: letterCount(), fira: document.fonts.check('bold 12px FiraMonoEmbedded'), fonts: document.fonts.size})",
        )
        print("info", info)
        shot = call(ws, 8, "Page.captureScreenshot", {"format": "png"})
        data = shot.get("result", {}).get("data")
        if not data:
            raise RuntimeError(json.dumps(shot)[:400])
        with open(OUT, "wb") as handle:
            handle.write(base64.b64decode(data))
        print("saved", OUT, os.path.getsize(OUT))
    finally:
        chrome.terminate()
        time.sleep(1)
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)


if __name__ == "__main__":
    main()
