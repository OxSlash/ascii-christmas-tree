import base64
import glob
import io
import json
import os
import struct

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "dist", "stickers")
LIMIT = 500 * 1024
MAX_TOTAL = 1024 * 1024


def riff_chunks(data):
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    pos = 12
    chunks = []
    while pos + 8 <= len(data):
        name = data[pos : pos + 4].decode("ascii", "replace")
        size = struct.unpack("<I", data[pos + 4 : pos + 8])[0]
        chunks.append(name)
        pos += 8 + size + (size & 1)
    return chunks


def main():
    meta = json.load(open(os.path.join(DIR, "pack.json"), encoding="utf-8"))
    print(f"pack: {meta['name']} by {meta['publisher']}  {meta['size']}px  {meta['fps']}fps  {meta['duration']:.2f}s")
    ok = True
    total = 0
    for item in meta["stickers"]:
        path = os.path.join(DIR, item["file"])
        data = open(path, "rb").read()
        total += len(data)
        chunks = riff_chunks(data)
        image = Image.open(path)
        frames = getattr(image, "n_frames", 1)
        image.seek(0)
        frame_ms = image.info.get("duration") or round(1000 / meta["fps"])
        checks = {
            "riff": chunks is not None,
            "anim": bool(chunks) and "ANIM" in chunks,
            "frames": frames == meta["frames"],
            "size": image.size == (meta["size"], meta["size"]),
            "weight": len(data) <= LIMIT,
        }
        state = "OK" if all(checks.values()) else "FAIL " + ",".join(k for k, v in checks.items() if not v)
        if state != "OK":
            ok = False
        print(
            f"{item['file']:20s} {len(data)/1024:7.1f}KB {image.size[0]}x{image.size[1]} "
            f"frames={frames} frame={frame_ms}ms total={frame_ms*frames}ms chunks={len(chunks)} -> {state}"
        )

    was_path = os.path.join(DIR, "pack.wastickers")
    pack = json.load(open(was_path, encoding="utf-8"))
    packs = pack.get("sticker_packs", [])
    valid = len(packs) == 1 and len(packs[0].get("stickers", [])) == len(meta["stickers"])
    decoded_ok = True
    for sticker in packs[0]["stickers"]:
        raw = base64.b64decode(sticker["image_data"])
        if raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
            decoded_ok = False
        im = Image.open(io.BytesIO(raw))
        if getattr(im, "n_frames", 1) != meta["frames"]:
            decoded_ok = False
    print(
        f"pack.wastickers {os.path.getsize(was_path)/1024:.1f}KB "
        f"packs={len(packs)} stickers={len(packs[0]['stickers']) if packs else 0} "
        f"payload_ok={decoded_ok} -> {'OK' if valid and decoded_ok else 'FAIL'}"
    )
    if not (valid and decoded_ok):
        ok = False
    print(f"total sticker bytes {total/1024:.1f}KB")
    print("ALL_OK" if ok else "PROBLEMS_FOUND")


if __name__ == "__main__":
    main()
