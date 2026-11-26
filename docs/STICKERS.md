# Sticker pack

Three animated stickers cut from the real renderer, ready to import into
WhatsApp.

## Build

```bash
python tools/make_stickers.py
python tools/check_stickers.py
```

## Output

`dist/stickers/`

| File | Frames | Size | Weight |
|---|---|---|---|
| `tree-grow.webp` | 30 | 512 × 512 | 274.0 KB |
| `tree-lights.webp` | 30 | 512 × 512 | 407.6 KB |
| `tree-star.webp` | 30 | 512 × 512 | 485.6 KB |
| `pack.json` | — | — | metadata |
| `pack.wastickers` | — | — | importable pack |

All three sit under WhatsApp's 500 KB per-sticker ceiling. Each is 2.00 s at
15 fps, looping forever.

## How they are made

`make_stickers.py` imports `web/main.py` and drives `App` directly, so the
stickers are frames of the actual program, not a re-creation:

- Frames are drawn with `App.background`, `App.tree`, and
  `App.background.draw_front` only — no HUD, no banner, no greeting text.
- The canvas is cropped to a centred 880 × 880 square, then resized to 512 × 512
  with Lanczos. Cropping rather than stretching keeps the tree's proportions.
- Frames are encoded as animated WebP with `quality=55`, `method=4`. Quality
  steps down automatically if a sticker crosses 500 KB.
- `pack.wastickers` wraps the same bytes in base64 with the field names
  WhatsApp expects.

## Scenes

| Sticker | Start time | What happens |
|---|---|---|
| Tree grows | 1.4 s | Trunk and branches fill in, needles still spreading |
| Lights on | 7.0 s | Garlands and fairy lights switch on, no greeting yet |
| Star topper | 11.7 s | Star flashes at the apex, rays expand |

Start times were chosen so each sticker has motion for its whole 2 seconds. An
earlier attempt starting at 0.0 s produced a nearly empty first frame, and
starting the star sticker at 11.3 s caught the greeting banner covering the
star.

## Verification

`check_stickers.py` reads the bytes back and asserts:

```
pack: ASCII Christmas Tree by OxSlash  512px  15fps  2.00s
tree-grow.webp         274.0KB 512x512 frames=30 frame=67ms total=2010ms chunks=32 -> OK
tree-lights.webp       407.6KB 512x512 frames=30 frame=67ms total=2010ms chunks=32 -> OK
tree-star.webp         485.6KB 512x512 frames=30 frame=67ms total=2010ms chunks=32 -> OK
pack.wastickers 1556.9KB packs=1 stickers=3 payload_ok=True -> OK
ALL_OK
```

Checks per sticker: valid RIFF/WEBP container, `ANIM` chunk present, 30 frames,
512 × 512, and under 500 KB. The `.wastickers` file is decoded back from base64
and re-opened to confirm the embedded payloads are real animations.

## Importing into WhatsApp

1. Install a sticker importer such as **Sticker Maker** on Android or iOS.
2. Create an empty pack, then use **Import .wastickers** and pick
   `dist/stickers/pack.wastickers`.
3. Add the pack to WhatsApp when prompted.

Alternatively, drop the three `.webp` files into a new pack manually.

## Dependencies

`pillow` is installed in the local `.venv` only and is deliberately **not** in
`requirements.txt`. It is used solely for WebP encoding.
