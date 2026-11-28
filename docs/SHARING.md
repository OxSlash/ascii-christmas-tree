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

The single-file build sizes itself to the device. On anything narrower than
560 px it crops the sides; only empty sky is removed, the tree stays whole. The
crop width is derived from the viewport aspect ratio, clamped between 54 and 88
columns, so the greeting banner always fits.

| Viewport | View width | CSS size | Scale |
|---|---|---|---|
| 360 × 640 (small Android) | 580 × 1036 | 358 × 640 | 0.62 |
| 375 × 667 (iPhone SE) | 540 × 1036 | 375 × 719 | 0.69 |
| 390 × 844 (iPhone) | 540 × 1036 | 390 × 748 | 0.72 |
| 393 × 852 (iPhone 15) | 540 × 1036 | 393 × 754 | 0.73 |
| 412 × 915 (Pixel) | 540 × 1036 | 412 × 790 | 0.76 |
| 430 × 932 (iPhone Max) | 540 × 1036 | 430 × 825 | 0.80 |
| 768 × 1024 (tablet) | 880 × 1036 | 744 × 876 | 0.85 |
| 1280 × 1000 (desktop) | 880 × 1036 | 846 × 996 | 0.96 |

Without the crop, a 390 px phone would render at 0.44, giving a 5 px glyph
height that makes the banner unreadable.

The banner has two layouts. Wide screens use two lines, `MERRY` over
`CHRISTMAS 2026`, 80 columns wide. Narrow screens use three lines, `MERRY` over
`CHRISTMAS` over `2026`, 53 columns wide. The renderer picks whichever fits the
current view.

Other mobile fixes:

- Text is anchored to the visible crop, not to the full grid, so nothing is cut
  off at the edges.
- Tap to pause requires a short press with less than 10 px of movement, so
  scrolling does not trigger it.
- Height uses `100dvh`; orientation changes re-run the layout after a short
  delay.

## Rendering performance

The first version composited the grid with one `drawImage` call per cell, which
cost 4.4 to 5.6 ms per frame and was the whole bottleneck. Drawing the tree
itself took only 0.4 ms.

The renderer now writes glyph tiles straight into a `Uint32Array` backing an
`ImageData`, then blits that surface once:

| Viewport | Before | After |
|---|---|---|
| Desktop | 24.2 ms | 6.1 ms |
| iPhone 390 × 844 | 18.3 ms | 6.1 ms |
| Android 360 × 640 | 18.0 ms | 6.0 ms |

That is roughly 164 fps of headroom, so the animation stays smooth even on
phones that cannot hit the display refresh rate.

## Verification

All checks run in headless Edge, so a browser you are using stays untouched.

```
iphone-390x844   view 540x1036  css 390x748  cells 912  letters 20
android-360x640  view 580x1036  css 358x640  cells 912  letters 20
pixel-412x915    view 540x1036  css 412x790  cells 912  letters 20
desktop          view 880x1036  css 846x996  cells 912  letters 20  fira True
index redirect   pathname .../dist/ascii-christmas-tree.html  state object
```

Frame fidelity against the pygame build at `t = 20 s` is unchanged at 99.91%
glyph agreement.

## Caveats

- WhatsApp caches link previews aggressively. If the card does not update after
  a change, send the URL with `?v=2` appended.
- `og:image` must be an absolute URL. Relative paths are ignored by every
  crawler that matters.
- The preview shows the same card for everyone; per-recipient cards would need a
  server, not a static host.
- Rendering inside WhatsApp's in-app browser has not been tested on a physical
  device. If something breaks there, the exact error message is what matters.
