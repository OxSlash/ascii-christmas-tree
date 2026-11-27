# Shareable link

The repo is ready to be published as a static site on GitHub Pages, with a link
preview that shows the tree instead of a bare URL.

## What is here

| File | Purpose |
|---|---|
| `index.html` | Landing page: Open Graph tags plus a redirect to the single-file build |
| `.nojekyll` | Tells GitHub Pages to serve files as-is, no Jekyll processing |
| `docs/social-card-a.png` | Cinematic card: ASCII greeting left, tree right |
| `docs/social-card-b.png` | Macro card: characters as texture |
| `docs/social-card-c.png` | Two faces: solid blocks left, characters right |
| `docs/social-card-d.png` | All-ASCII card: no images anywhere |
| `docs/qr-tree.png` | Regenerated to point at the GitHub Pages URL |
| `tools/make_social_cards.py` | Builds all four cards at 1200 × 630 |

## Enable GitHub Pages

```
Repository → Settings → Pages
Source : Deploy from a branch
Branch : main
Folder : / (root)
Save
```

Wait about a minute, then the site is live at:

```
https://oxslash.github.io/ascii-christmas-tree/
```

`index.html` immediately redirects to `dist/ascii-christmas-tree.html`, so the
visitor lands on the tree with no extra click.

## Choosing a card

All four are 1200 × 630, the size WhatsApp, Telegram, and X expect. Only one can
be the preview, chosen by the `og:image` tag in `index.html`:

```html
<meta property="og:image" content="https://oxslash.github.io/ascii-christmas-tree/docs/social-card-a.png">
```

Change the filename to `-b`, `-c`, or `-d` to switch. Update the `twitter:image`
tag to match.

### The four designs

| Card | Approach | What it says |
|---|---|---|
| **A** | Cinematic | Greeting left, tree right, like a film poster |
| **B** | Macro | Characters become texture; you realise it is text second |
| **C** | Two faces | Solid blocks left, characters right; explains the concept in one look |
| **D** | All ASCII | The card itself is drawn from characters; no images anywhere |

Rebuild them with:

```bash
python tools/make_social_cards.py
```

Each card is rendered from the real program at `t = 20 s`, not a mockup.

## Mobile layout

The single-file build crops the sides when the viewport is narrower than 560 px.
Only empty sky is removed; the tree, banner, and HUD stay whole.

| Viewport | Backing store | CSS size | Scale |
|---|---|---|---|
| 390 × 844 (iPhone) | 620 × 1036 | 390 × 651 | 0.63 |
| 360 × 640 (Android) | 620 × 1036 | 360 × 601 | 0.58 |
| 412 × 915 (Pixel) | 620 × 1036 | 412 × 688 | 0.66 |
| 1280 × 1160 (desktop) | 880 × 1036 | 827 × 974 | 0.94 |

Without the crop, the same phones would render at 0.44, giving a 5 px glyph
height that makes the banner unreadable.

Other mobile fixes:

- HUD text is anchored to the visible crop, not to the full grid, so nothing is
  cut off at the edges.
- Tap to pause now requires a short press with less than 10 px of movement, so
  scrolling does not trigger it.
- Height uses `100dvh` and the hint respects `env(safe-area-inset-bottom)`.
- Orientation changes re-run the layout after a short delay.

## Verification

All checks run in headless Edge, so a browser you are using stays untouched.

```
iphone-390x844   view 620x1036  css 390x651  cells 912  letters 20
android-360x640  view 620x1036  css 360x601  cells 912  letters 20
pixel-412x915    view 620x1036  css 412x688  cells 912  letters 20
desktop          view 880x1036  css 827x974  cells 912  letters 20  fira True
index redirect   pathname .../dist/ascii-christmas-tree.html  state object
```

Frame fidelity against the pygame build at `t = 20 s` is unchanged at 99.91%
glyph agreement. Frame rate on desktop is 48.4 fps (median of three runs).

## Caveats

- WhatsApp caches link previews aggressively. If the card does not update after
  a change, send the URL with `?v=2` appended.
- `og:image` must be an absolute URL. Relative paths are ignored by every
  crawler that matters.
- The preview shows the same card for everyone; per-recipient cards would need a
  server, not a static host.
- Rendering inside WhatsApp's in-app browser has not been tested on a physical
  device. If something breaks there, the exact error message is what matters.
