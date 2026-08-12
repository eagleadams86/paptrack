#!/usr/bin/env python3
"""Recolour the app's mark, and write every copy of it the page needs.

    python3 make_favicon.py

This writes `favicon.ico` AND rewrites the two base64 PNG data URIs in
`index.html` (the `rel="icon"` one at 64px and the `apple-touch-icon` at
180px), because those three are one picture and hand-editing a base64 blob is
how they drift apart. Nothing else in the page is touched.

## Why this recolours rather than redraws

The mark is the airflow motif from the shipped iOS and Android icons: a source
dot with three arcs radiating rightward, on the midnight page with two darker
corner circles. It is NOT redrawn here, and that is deliberate. The Android
vector (`ic_launcher_foreground.xml`) and the iOS render are different
compositions — the Android one is laid out around the adaptive-icon safe zone,
with a bigger dot, fatter strokes and equal angular spans, while the shipped
iOS art sits further right with a smaller dot and arcs whose spans narrow as
they go out (52 degrees, then 46, then 40). Porting the Android coordinates was
tried first and produced a visibly different icon. So this script takes the
SHIPPED PIXELS as its master and changes nothing but their colour: the geometry
cannot drift because it is never re-derived.

## What actually changed, and why

The native icon fades each ring by ALPHA over the page — full accent, then 72%,
then 45% — which bottoms the outer arc out at about #40477e. On a phone home
screen, seen whole and at size, that reads as a signal weakening. In a 16px row
of browser tabs beside five sibling apps it just read dim, and that was the
complaint. The ramp here runs between the family's own two accent tones
instead, so the falloff survives (the outer ring is still the quietest) while
every ring stays a colour the rest of the family actually uses.

The phone icons still fade to alpha and are deliberately left alone: changing
those means a new build and, for iOS, a new submission.

## The recolour, exactly

Every pixel of a ring is `bg + a * (accent - bg)`, where `a` is the ring's alpha
times its antialiasing coverage at that pixel, and `bg` is whichever flat
background sits under it. Projecting `px - bg` onto `accent - bg` recovers `a`;
dividing by the ring's known alpha leaves the coverage alone; re-compositing the
NEW colour at that same coverage repaints the ring without touching a single
edge. `bg` is read from the master itself, by stepping radially out of the ring
until the pixel stops being part of the mark — so the corner circles underneath
survive untouched too.

Which ring a pixel belongs to is decided by its distance from the source dot,
which every arc is centred on. That is measured from the master, not assumed.
"""

import base64
import io
import math
import pathlib
import re

from PIL import Image

# The master: the shipped iOS app icon, which is what the web icons were cut
# from. It lives in the sibling repo on this machine; nothing here is fetched.
MASTER = pathlib.Path.home() / (
    'claude-paptrack-ios/PAPTrack/Assets.xcassets/AppIcon.appiconset/icon-1024.png')

ACCENT = (129, 140, 248)        # #818cf8 — what the native rings are made of

# Measured from the master, in its own 1024px space: the source dot every arc
# is centred on, then each ring's radius, half-width and native alpha.
CENTRE = (429.5, 511.5)
DOT_R = 45.5
RINGS = [                       # (radius, half-width, native alpha, new colour)
    (0,   DOT_R, 1.00, (165, 180, 252)),    # the dot — #a5b4fc
    (190, 23,    1.00, (165, 180, 252)),    # inner arc, matches the dot as it always has
    (340, 21,    0.72, (147, 160, 250)),    # middle — the midpoint of the two tones
    (490, 19,    0.45, (129, 140, 248)),    # outer — --accent, was a 45% wash
]
BAND_PAD = 14                   # radial slack, so antialiased edges are included

ICO_SIZES = [16, 32, 48, 64, 128, 256]
PAGE_ICON = 64                  # the rel="icon" data URI
TOUCH_ICON = 180                # the apple-touch-icon data URI


def is_mark(px):
    """Is this pixel part of the blue mark, rather than page or corner circle?"""
    return px[2] > 90 and px[2] - px[0] > 40


def ring_of(r):
    """Which ring a radius falls in, or None."""
    for i, (rad, half, _, _) in enumerate(RINGS):
        lo = 0 if i == 0 else rad - half - BAND_PAD
        if lo <= r <= rad + half + BAND_PAD:
            return i
    return None


PAGE = (10, 14, 26)             # #0a0e1a — the tile
CORNER = (18, 24, 41)           # #121829 — the two corner circles

# Offsets on a disc, used to vote on what sits under a ring. Ordered by distance
# so the nearest evidence is gathered first.
_VOTE = sorted(((dx, dy) for dx in range(-30, 31, 2) for dy in range(-30, 31, 2)
                if 6 <= (dx * dx + dy * dy) ** 0.5 <= 30),
               key=lambda o: o[0] * o[0] + o[1] * o[1])


def background_at(px_at, x, y):
    """The flat colour under a mark pixel: a MAJORITY VOTE of its neighbours.

    The backdrop is only ever two flat colours, so this is a two-way vote. It
    is a vote rather than a nearest-pixel probe because of the handful of places
    where a ring crosses the edge of a corner circle: there, "the first non-mark
    pixel going outwards" is page on one side of the ring and corner circle on
    the other, and which one you hit first flips back and forth along the ring —
    which painted a row of vertical stripes down the outer arc. A vote over a
    disc changes its mind once, where the edge actually is.
    """
    page = corner = 0
    for dx, dy in _VOTE:
        q = px_at(x + dx, y + dy)
        if q is None or is_mark(q):
            continue
        if abs(q[0] - CORNER[0]) + abs(q[1] - CORNER[1]) + abs(q[2] - CORNER[2]) < \
           abs(q[0] - PAGE[0]) + abs(q[1] - PAGE[1]) + abs(q[2] - PAGE[2]):
            corner += 1
        else:
            page += 1
        if page + corner >= 60:
            break
    return CORNER if corner > page else PAGE


def recolour(img):
    img = img.convert('RGB')
    W, H = img.size
    src = img.load()
    out = img.copy()
    dst = out.load()
    cx, cy = CENTRE

    def px_at(x, y):
        return src[x, y] if 0 <= x < W and 0 <= y < H else None

    touched = 0
    for y in range(H):
        for x in range(W):
            p = src[x, y]
            if not is_mark(p):
                continue
            r = math.hypot(x - cx, y - cy)
            idx = ring_of(r)
            if idx is None:
                continue
            _, _, alpha, new = RINGS[idx]
            bg = background_at(px_at, x, y)
            # Recover a = alpha * coverage by projecting onto (accent - bg).
            dv = [ACCENT[c] - bg[c] for c in range(3)]
            den = sum(v * v for v in dv)
            if den == 0:
                continue
            a = sum((p[c] - bg[c]) * dv[c] for c in range(3)) / den
            cov = max(0.0, min(1.0, a / alpha))
            dst[x, y] = tuple(round(bg[c] + cov * (new[c] - bg[c])) for c in range(3))
            touched += 1
    print(f'{touched} mark pixels recoloured')
    return out


def png_data_uri(art, size):
    buf = io.BytesIO()
    art.resize((size, size), Image.LANCZOS).save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def rewrite_page(art, path='index.html'):
    p = pathlib.Path(path)
    html = p.read_text()
    for pattern, size, what in [
            (r'(<link rel="icon" type="image/png" href=")[^"]*(">)',
             PAGE_ICON, 'rel="icon"'),
            (r'(<link rel="apple-touch-icon" href=")[^"]*(">)',
             TOUCH_ICON, 'apple-touch-icon')]:
        uri = png_data_uri(art, size)
        html, n = re.subn(pattern, lambda m: m.group(1) + uri + m.group(2),
                          html, count=1)
        if n != 1:
            raise SystemExit(f'could not find the {what} link in {path} — the '
                             'markup changed shape; fix this script rather than '
                             'editing the base64 by hand')
        print(f'{what} rewritten at {size}px')
    p.write_text(html)


def main():
    if not MASTER.exists():
        raise SystemExit(
            f'master icon not found at {MASTER}\n'
            'This script recolours the shipped iOS app icon rather than '
            'redrawing the mark, so it needs the claude-paptrack-ios repo '
            'checked out beside this one.')
    art = recolour(Image.open(MASTER))
    frames = [art.resize((s, s), Image.LANCZOS) for s in ICO_SIZES]
    frames[-1].save('favicon.ico', format='ICO',
                    sizes=[(s, s) for s in ICO_SIZES])
    print('favicon.ico written at ' + ', '.join(f'{s}px' for s in ICO_SIZES))
    rewrite_page(art)
    print('Now bump the ?v= on any favicon.ico reference in index.html — '
          'browsers cache an icon for a long time. (The data URIs need no '
          'version: their content IS the URL.)')


if __name__ == '__main__':
    main()
