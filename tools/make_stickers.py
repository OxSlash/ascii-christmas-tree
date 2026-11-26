import base64
import importlib.util
import io
import json
import os

import pygame
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

spec = importlib.util.spec_from_file_location("treeapp", os.path.join(ROOT, "web", "main.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

STICKER = 512
FPS = 15
FRAMES = 30
QUALITY = 55
METHOD = 4
LIMIT = 500 * 1024
CROP_SIZE = 880
CROP_CX = 440
CROP_CY = 480

PLAN = (
    ("tree-grow", 1.4, "Tree grows", "\U0001F384"),
    ("tree-lights", 7.0, "Lights on", "\u2728"),
    ("tree-star", 11.7, "Star topper", "\u2b50"),
)


def capture(app, start, frames):
    x = max(0, min(mod.WIDTH - CROP_SIZE, CROP_CX - CROP_SIZE // 2))
    y = max(0, min(mod.HEIGHT_PX - CROP_SIZE, CROP_CY - CROP_SIZE // 2))
    images = []
    for k in range(frames):
        app.t = start + k / FPS
        fb = app.framebuffer
        fb.clear()
        app.background.draw(fb, app.t)
        app.tree.draw(fb, app.t)
        app.background.draw_front(fb, app.t)
        app.compose()
        crop = app.screen.subsurface((x, y, CROP_SIZE, CROP_SIZE))
        raw = pygame.image.tostring(crop, "RGB")
        images.append(Image.frombytes("RGB", (CROP_SIZE, CROP_SIZE), raw).resize((STICKER, STICKER), Image.LANCZOS))
    return images


def encode(images, quality):
    buffer = io.BytesIO()
    images[0].save(
        buffer,
        format="WEBP",
        save_all=True,
        append_images=images[1:],
        duration=int(1000 / FPS),
        loop=0,
        quality=quality,
        method=METHOD,
    )
    return buffer.getvalue()


def main():
    pygame.init()
    pygame.display.set_mode((mod.WIDTH, mod.HEIGHT_PX))
    app = mod.App(mod.SEED_DEFAULT, FPS)

    out_dir = os.path.join(ROOT, "dist", "stickers")
    os.makedirs(out_dir, exist_ok=True)

    entries = []
    for name, start, label, emoji in PLAN:
        images = capture(app, start, FRAMES)
        quality = QUALITY
        data = encode(images, quality)
        while len(data) > LIMIT and quality > 20:
            quality -= 5
            data = encode(images, quality)
        with open(os.path.join(out_dir, f"{name}.webp"), "wb") as handle:
            handle.write(data)
        entries.append({"name": label, "file": f"{name}.webp", "emoji": emoji, "bytes": len(data), "quality": quality})
        print(f"{name} start={start}s {FRAMES} frames {len(data)} bytes q{quality}", flush=True)

    pygame.quit()

    meta = {
        "name": "ASCII Christmas Tree",
        "publisher": "OxSlash",
        "size": STICKER,
        "fps": FPS,
        "frames": FRAMES,
        "duration": FRAMES / FPS,
        "stickers": entries,
    }
    with open(os.path.join(out_dir, "pack.json"), "w", encoding="utf-8") as handle:
        json.dump(meta, handle, indent=2, ensure_ascii=False)

    icons = []
    for item in entries:
        with open(os.path.join(out_dir, item["file"]), "rb") as handle:
            icons.append(
                {
                    "image_data": base64.b64encode(handle.read()).decode("ascii"),
                    "emojis": [item["emoji"]],
                }
            )
    wastickers = {
        "android_play_store_link": "",
        "ios_app_store_link": "",
        "sticker_packs": [
            {
                "identifier": "asciichristmastree",
                "name": meta["name"],
                "publisher": meta["publisher"],
                "publisher_email": "",
                "publisher_website": "https://github.com/OxSlash/ascii-christmas-tree",
                "privacy_policy_website": "",
                "license_agreement_website": "",
                "animated_sticker_pack": True,
                "image_data_version": "1",
                "avoid_cache": False,
                "stickers": [
                    {
                        "image_data": icon["image_data"],
                        "emojis": icon["emojis"],
                        "accessibility_text": entry["name"],
                    }
                    for icon, entry in zip(icons, entries)
                ],
            }
        ],
    }
    with open(os.path.join(out_dir, "pack.wastickers"), "w", encoding="utf-8") as handle:
        json.dump(wastickers, handle)

    print("pack.json and pack.wastickers written")


if __name__ == "__main__":
    main()
