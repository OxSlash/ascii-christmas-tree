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

## Screen layout

The canvas always fills the whole viewport, so there are no letterbox bars and no
visible frame around the picture. The grid is drawn centred inside it at a
uniform scale, and everything outside the grid is filled with the same starfield
and snow, so the sky runs edge to edge.

The grid is 88 x 74 cells, which is portrait (aspect 0.85). A wide window cannot
show it full width without cutting the tree in half, so the grid keeps its aspect
and the sides are sky.

| Viewport | Canvas | Grid drawn | Sky fills |
|---|---|---|---|
| 1510 x 590 (laptop) | 1510 x 590 | 501 x 590 | 1009 px of sides |
| 1414 x 760 (MacBook) | 1414 x 760 | 646 x 760 | 768 px of sides |
| 998 x 628 (iPad landscape) | 998 x 628 | 533 x 628 | 465 px of sides |
| 742 x 884 (iPad portrait) | 742 x 884 | 742 x 884 | none needed |
| 1894 x 940 (1920 desktop) | 1894 x 940 | 798 x 940 | 1096 px of sides |

On phones the view is cropped first, because a 390 px phone would otherwise
render at 0.44 and the greeting would be unreadable. The crop width comes from
the viewport aspect ratio, with a floor wide enough to hold the greeting plus a
six column margin on each side.

| Viewport | View width | CSS size | Scale |
|---|---|---|---|
| 360 x 640 (small Android) | 560 x 1036 | 360 x 640 | 0.64 |
| 390 x 844 (iPhone) | 560 x 1036 | 390 x 844 | 0.70 |
| 412 x 915 (Pixel) | 560 x 1036 | 412 x 915 | 0.74 |

The greeting is one layout everywhere: three lines, `MERRY` over `CHRISTMAS`
over `2026`, 44 columns wide, drawn in a 4x5 pixel font. It sits 22 columns in
from the left edge of the full grid, so it keeps a margin on every device and
never touches the sides. The text has no background band; the letters are drawn
straight onto the starfield.

Other layout notes:

- The canvas is sized in device pixels (`devicePixelRatio`, capped at 2) so text
  stays sharp on retina screens instead of being stretched by CSS.
- Text is centred on the banner, not on the full grid, so cropping never cuts it.
- Left click or tap throws a burst of snow, anywhere on the canvas, including the
  sky at the sides. Only the primary button counts; right and middle click are
  ignored, and the context menu is suppressed.
- Holding the button down throws one burst, not a stream. Dragging throws more,
  but only after the pointer has moved 14 px and 45 ms have passed, so a slow
  press stays a single burst.
- The canvas sets `touch-action: none`, so dragging a finger throws snow instead
  of being stolen by the browser as a scroll or zoom gesture.
- Snow is drawn straight onto the canvas in pixel space, so it works outside the
  grid instead of being clipped to the 88 x 74 cell buffer.
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
| Desktop 1920 x 1080 | 24.2 ms | 6.1 ms |
| MacBook 1440 x 900 | 21.0 ms | 6.1 ms |
| Laptop 1536 x 730 | 20.4 ms | 6.1 ms |
| iPhone 390 x 844 | 18.3 ms | 6.1 ms |
| Android 360 x 640 | 18.0 ms | 6.1 ms |

That is roughly 164 fps of headroom, so the animation stays smooth even on
phones that cannot hit the display refresh rate.

Filling the sides with sky costs almost nothing. The first attempt redrew a
full-screen `ImageData` every frame, which cost 4.1 ms at 1920 x 1080 and pulled
that size down to 82 fps. It now draws one `fillRect` per star and flake
straight onto the canvas, which costs 0.37 to 1.17 ms depending on width.

## Verification

All checks run in headless Edge, so a browser you are using stays untouched.

```
laptop-1536x730   canvas 1510x590   grid 501x590    cells 912  letters 20
macbook-1440x900  canvas 1414x760   grid 646x760    cells 912  letters 20
ipad-1024x768     canvas  998x628   grid 533x628    cells 912  letters 20
desktop-1920x1080 canvas 1894x940   grid 798x940    cells 912  letters 20
iphone-390x844    view 560x1036     css 390x844     cells 912  letters 20
android-360x640   view 580x1036     css 360x640     cells 912  letters 20
pixel-412x915     view 560x1036     css 412x915     cells 912  letters 20
index redirect    pathname .../dist/ascii-christmas-tree.html  state object
```

Click behaviour, measured with synthetic pointer events at 1510 x 590:

```
left far-left sky    bursts 34   OK
left far-right sky   bursts 34   OK
left centre          bursts 34   OK
right button         bursts  0   OK
middle button        bursts  0   OK
long left press      bursts 34   OK
drag across sky      bursts 340  OK
```

Touch behaviour on a 390 x 844 phone viewport, with synthetic touch events:

```
tap centre           bursts 34   OK
tap left sky         bursts 34   OK
tap right sky        bursts 34   OK
touch drag           bursts 272  OK
stays paused         paused True OK
```

Frame fidelity against the pygame build at `t = 20 s` is unchanged at 99.95%
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
