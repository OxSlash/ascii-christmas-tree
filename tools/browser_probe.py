import base64
import json
import os
import socket
import struct
import subprocess
import time
import urllib.request
from urllib.parse import urlparse

EDGE_PATHS = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)
CHROME_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
)
TEMP = os.path.join(os.environ["TEMP"], "opencode")


def find_browser():
    for path in EDGE_PATHS:
        if os.path.exists(path):
            return path
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path
    raise RuntimeError("no browser found")


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


class Headless:
    def __init__(self, port, profile_name, width=980, height=1160, mobile=False):
        self.port = port
        self.profile = os.path.join(TEMP, profile_name)
        self.width = width
        self.height = height
        self.mobile = mobile
        self.proc = None
        self.ws = None

    def __enter__(self):
        os.makedirs(self.profile, exist_ok=True)
        args = [
            find_browser(),
            "--headless=new",
            "--no-sandbox",
            "--hide-scrollbars",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=Translate",
            f"--window-size={self.width},{self.height}",
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profile}",
            "--allow-file-access-from-files",
            "about:blank",
        ]
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        target = None
        for _ in range(80):
            try:
                data = json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/list", timeout=2))
                pages = [t for t in data if t.get("type") == "page"]
                if pages:
                    target = pages[0]
                    break
            except Exception:
                pass
            time.sleep(0.4)
        if target is None:
            self.close()
            raise RuntimeError("browser did not expose a debug target")
        self.ws = WebSocket(target["webSocketDebuggerUrl"])
        call(self.ws, 1, "Page.enable")
        call(self.ws, 2, "Runtime.enable")
        if self.mobile:
            call(
                self.ws,
                3,
                "Emulation.setDeviceMetricsOverride",
                {
                    "width": self.width,
                    "height": self.height,
                    "deviceScaleFactor": 2,
                    "mobile": True,
                },
            )
        return self

    def goto(self, url):
        call(self.ws, 10, "Page.navigate", {"url": url})

    def shot(self, path):
        result = call(self.ws, 90, "Page.captureScreenshot", {"format": "png"})
        data = result.get("result", {}).get("data")
        if not data:
            raise RuntimeError(json.dumps(result)[:300])
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(base64.b64decode(data))
        return os.path.getsize(path)

    def close(self):
        if self.ws is not None:
            try:
                self.ws.sock.close()
            except Exception:
                pass
            self.ws = None
        if self.proc is not None:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                capture_output=True,
            )
            self.proc = None

    def __exit__(self, *args):
        self.close()
        return False
