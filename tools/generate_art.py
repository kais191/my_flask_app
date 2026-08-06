#!/usr/bin/env python3
"""Procedural SVG artwork generator for Nested Blooms.

The shop has no external image dependencies: every bouquet, category tile and
hero illustration on the site is drawn by this script from the recipes in
``nestedblooms.catalog``.

Each flower species is emitted once into ``<defs>`` as a ``<symbol>`` and then
stamped with ``<use>`` elements, which keeps a 90-stem arrangement to roughly
15KB instead of several hundred.

Run from the project root:

    python3 tools/generate_art.py
"""

from __future__ import annotations

import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _load_catalog():
    """Import the catalogue without pulling in the Flask app package.

    ``nestedblooms/__init__.py`` imports Flask, which this script does not
    need — loading the module directly keeps the generator runnable with a
    bare Python install.
    """
    import importlib.util

    path = os.path.join(ROOT, "nestedblooms", "catalog.py")
    spec = importlib.util.spec_from_file_location("nb_catalog", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


catalog = _load_catalog()

IMG_DIR = os.path.join(ROOT, "static", "img")

# Symbols are drawn in a local coordinate system centred on (0, 0) with a
# nominal radius of 50 units, so a stamped instance of scale s has diameter s.
UNIT = 50.0


# ---------------------------------------------------------------------------
# Small colour helpers
# ---------------------------------------------------------------------------

def _hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def shade(colour, amount):
    """Lighten (amount > 0) or darken (amount < 0) a hex colour."""
    r, g, b = _hex_to_rgb(colour)
    if amount >= 0:
        r += (255 - r) * amount
        g += (255 - g) * amount
        b += (255 - b) * amount
    else:
        f = 1 + amount
        r, g, b = r * f, g * f, b * f
    return _rgb_to_hex((r, g, b))


def n(value):
    """Format a float compactly — SVG files get large fast otherwise."""
    return f"{value:.1f}".rstrip("0").rstrip(".") or "0"


# ---------------------------------------------------------------------------
# Drawing surface
# ---------------------------------------------------------------------------

class Drawing:
    def __init__(self, width, height, seed=0):
        self.width = width
        self.height = height
        self.defs = []
        self.body = []
        self.rng = random.Random(seed)
        self._counter = 0
        self._symbol_cache = {}
        self._paint_cache = {}
        self._path_cache = {}

    def uid(self, prefix="a"):
        self._counter += 1
        return f"{prefix}{self._counter}"

    def radial(self, inner, outer, cx="45%", cy="35%"):
        key = ("r", inner, outer, cx, cy)
        if key not in self._paint_cache:
            gid = self.uid("g")
            self._paint_cache[key] = gid
            self.defs.append(
                f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="72%">'
                f'<stop offset="0" stop-color="{inner}"/>'
                f'<stop offset="1" stop-color="{outer}"/>'
                f"</radialGradient>"
            )
        return self._paint_cache[key]

    def linear(self, start, end, x1=0, y1=0, x2=0, y2=1):
        key = ("l", start, end, x1, y1, x2, y2)
        if key not in self._paint_cache:
            gid = self.uid("g")
            self._paint_cache[key] = gid
            self.defs.append(
                f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
                f'<stop offset="0" stop-color="{start}"/>'
                f'<stop offset="1" stop-color="{end}"/>'
                f"</linearGradient>"
            )
        return self._paint_cache[key]

    def blur(self, deviation):
        """Register a gaussian blur filter and return its id."""
        key = ("blur", deviation)
        if key not in self._paint_cache:
            fid = self.uid("f")
            self._paint_cache[key] = fid
            self.defs.append(
                f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="160%">'
                f'<feGaussianBlur stdDeviation="{n(deviation)}"/></filter>'
            )
        return self._paint_cache[key]

    def shape(self, path_data):
        """Register a reusable path outline and return its id.

        Petals repeat heavily within a bloom, so referencing one definition
        with <use> rather than repeating the geometry keeps files small.
        """
        if path_data not in self._path_cache:
            pid = self.uid("p")
            self._path_cache[path_data] = pid
            self.defs.append(f'<path id="{pid}" d="{path_data}"/>')
        return self._path_cache[path_data]

    def symbol(self, key, builder):
        """Register a symbol once per key and return its id."""
        if key not in self._symbol_cache:
            sid = self.uid("s")
            self._symbol_cache[key] = sid
            self.defs.append(f'<g id="{sid}">{builder()}</g>')
        return self._symbol_cache[key]

    def use(self, sid, x, y, scale, rotation=0.0, opacity=None):
        transform = f"translate({n(x)} {n(y)})"
        if rotation:
            transform += f" rotate({n(rotation)})"
        if abs(scale - 1.0) > 0.001:
            transform += f" scale({scale:.3f})"
        extra = f' opacity="{opacity:.2f}"' if opacity is not None else ""
        self.body.append(f'<use href="#{sid}" transform="{transform}"{extra}/>')

    def add(self, markup):
        self.body.append(markup)

    def render(self, title=""):
        # SVG is XML: an unescaped "&" in a product name such as
        # "Bloom & Bubbles" makes the whole file unparseable and the browser
        # silently renders nothing.
        safe = (
            title.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}" '
            f'role="img" aria-label="{safe}">'
        )
        return (
            head
            + f"<title>{safe}</title>"
            + "<defs>" + "".join(self.defs) + "</defs>"
            + "".join(self.body)
            + "</svg>"
        )


# ---------------------------------------------------------------------------
# Flower symbols
# ---------------------------------------------------------------------------
#
# Every builder draws into a local space centred on the origin, with petals
# reaching roughly UNIT (50) units out, i.e. a nominal diameter of 100.
# ---------------------------------------------------------------------------

def _petal_path(length, width, tip=0.0):
    """A teardrop petal pointing up the -Y axis, rooted at the origin."""
    half = width / 2.0
    return (
        f"M0 0 C{n(-half)} {n(-length * 0.25)} {n(-half)} {n(-length * 0.72)} "
        f"{n(-tip)} {n(-length)} C{n(half)} {n(-length * 0.72)} "
        f"{n(half)} {n(-length * 0.25)} 0 0 Z"
    )


def _round_petal(length, width):
    """A petal with a broad, rounded tip.

    Roses, peonies and carnations all have cupped petals that flare at the
    edge. The pointed teardrop used for lilies and daisies makes them read as
    dahlias instead.
    """
    half = width / 2.0
    return (
        f"M0 0 "
        f"C{n(-half)} {n(-length * 0.22)} {n(-half * 1.12)} {n(-length * 0.66)} "
        f"{n(-half * 0.5)} {n(-length * 0.93)} "
        f"C{n(-half * 0.18)} {n(-length * 1.06)} {n(half * 0.18)} "
        f"{n(-length * 1.06)} {n(half * 0.5)} {n(-length * 0.93)} "
        f"C{n(half * 1.12)} {n(-length * 0.66)} {n(half)} "
        f"{n(-length * 0.22)} 0 0 Z"
    )


def _petal_ring(d, count, length, width, colour, offset=0.0, opacity=1.0,
                stroke=None, jitter=0.0, rng=None, rounded=True):
    """A ring of outward-facing petals rooted at the origin.

    Petals radiate from the centre so the bloom keeps a scalloped silhouette
    rather than reading as a flat disc.
    """
    # Keep the light-to-dark range narrow: heavy shading turns white and cream
    # varieties grey, which is exactly the wrong look for a florist.
    fill = d.radial(shade(colour, 0.2), shade(colour, -0.1))
    stroke_attr = (
        f' stroke="{stroke}" stroke-width="0.6" stroke-opacity="0.5"'
        if stroke else ""
    )
    shape = _round_petal if rounded else _petal_path
    out = []
    for i in range(count):
        angle = offset + i * (360.0 / count)
        if jitter and rng:
            angle += rng.uniform(-jitter, jitter)
        pid = d.shape(shape(length, width))
        out.append(
            f'<use href="#{pid}" fill="url(#{fill})"{stroke_attr} '
            f'transform="rotate({n(angle)})" opacity="{opacity}"/>'
        )
    return out


def build_rose(d, colours, variant):
    base, mid, dark = _triad(colours)
    rng = random.Random(hash((variant, "rose")) & 0xFFFF)
    spin = rng.uniform(0, 45)
    parts = [f'<circle r="{n(UNIT * 0.5)}" fill="{shade(dark, -0.05)}"/>']
    # Four rings of progressively smaller petals, each offset from the last.
    # Petals are nearly as wide as they are long — a narrow petal reads as a
    # dahlia or a chrysanthemum rather than a rose.
    for ring, (count, length, width, colour) in enumerate((
        (8, 1.0, 0.92, base),
        (7, 0.76, 0.74, mid),
        (6, 0.55, 0.58, base),
        (5, 0.37, 0.44, mid),
    )):
        parts += _petal_ring(
            d, count, UNIT * length, UNIT * width, colour,
            offset=spin + ring * 24, opacity=0.98,
            stroke=shade(dark, 0.3),
        )
    # Tightly furled centre.
    for i, r in enumerate((0.22, 0.14, 0.07)):
        parts.append(
            f'<circle r="{n(UNIT * r)}" fill="none" '
            f'stroke="{shade(dark, 0.16 + i * 0.1)}" '
            f'stroke-width="{n(UNIT * 0.07)}" opacity="0.9"/>'
        )
    parts.append(f'<circle r="{n(UNIT * 0.045)}" fill="{shade(dark, -0.2)}"/>')
    return "".join(parts)


def build_peony(d, colours, variant):
    base, mid, dark = _triad(colours)
    rng = random.Random(hash((variant, "peony")) & 0xFFFF)
    spin = rng.uniform(0, 40)
    parts = [f'<circle r="{n(UNIT * 0.55)}" fill="{shade(dark, -0.02)}"/>']
    # Peonies are ruffled: more petals per ring, wider, and slightly irregular.
    for ring, (count, length, width, colour) in enumerate((
        (12, 1.04, 0.58, base),
        (10, 0.82, 0.5, mid),
        (9, 0.62, 0.42, base),
        (7, 0.44, 0.36, mid),
        (5, 0.28, 0.3, base),
    )):
        parts += _petal_ring(
            d, count, UNIT * length, UNIT * width, colour,
            offset=spin + ring * 17, opacity=0.95,
            jitter=6, rng=rng,
        )
    parts.append(
        f'<circle r="{n(UNIT * 0.1)}" fill="{shade(base, 0.45)}" opacity="0.9"/>'
    )
    return "".join(parts)


def build_ranunculus(d, colours, variant):
    base, mid, dark = _triad(colours)
    rng = random.Random(hash((variant, "ranun")) & 0xFFFF)
    parts = [f'<circle r="{n(UNIT * 0.55)}" fill="{shade(dark, -0.02)}"/>']
    # Many tightly packed, shallow petals — the whorl reads as layered petals
    # rather than as concentric rings.
    for ring, (count, length, width) in enumerate((
        (10, 1.0, 0.72), (10, 0.82, 0.62), (9, 0.66, 0.52),
        (8, 0.5, 0.44), (7, 0.36, 0.36), (5, 0.24, 0.28),
    )):
        parts += _petal_ring(
            d, count, UNIT * length, UNIT * width,
            base if ring % 2 == 0 else mid,
            offset=ring * 19 + rng.uniform(0, 12), opacity=0.97,
            stroke=shade(dark, 0.28),
        )
    parts.append(f'<circle r="{n(UNIT * 0.08)}" fill="{shade(dark, -0.1)}"/>')
    return "".join(parts)


def _tulip_petal(height, width):
    """A closed, cup-shaped tulip petal rooted below the origin."""
    return (
        f"M0 {n(height * 0.5)} "
        f"C{n(-width)} {n(height * 0.3)} {n(-width * 0.95)} {n(-height * 0.6)} "
        f"0 {n(-height)} "
        f"C{n(width * 0.95)} {n(-height * 0.6)} {n(width)} {n(height * 0.3)} "
        f"0 {n(height * 0.5)} Z"
    )


def build_tulip(d, colours, variant):
    base, mid, dark = _triad(colours)
    parts = []
    # Three overlapping petals: two flared behind, one cupped in front.
    for angle, height, width, colour in (
        (-24, 0.9, 0.4, dark),
        (24, 0.9, 0.4, mid),
        (0, 1.0, 0.46, base),
    ):
        pid = d.shape(_tulip_petal(UNIT * height, UNIT * width))
        fill = d.radial(shade(colour, 0.28), shade(colour, -0.12), "50%", "30%")
        parts.append(
            f'<use href="#{pid}" fill="url(#{fill})" '
            f'stroke="{shade(dark, -0.05)}" stroke-width="0.7" '
            f'transform="rotate({n(angle)})"/>'
        )
    # A highlight down the centre petal reads as the fold between petals.
    parts.append(
        f'<path d="M0 {n(UNIT * 0.34)} C{n(-UNIT * 0.14)} {n(-UNIT * 0.1)} '
        f'{n(-UNIT * 0.12)} {n(-UNIT * 0.6)} 0 {n(-UNIT * 0.92)}" '
        f'fill="none" stroke="{shade(base, 0.4)}" stroke-width="{n(UNIT * 0.07)}" '
        f'opacity="0.5" stroke-linecap="round"/>'
    )
    return "".join(parts)


def build_lily(d, colours, variant):
    base, mid, dark = _triad(colours)
    parts = []
    for layer, (count, length, width, opacity) in enumerate(
        ((6, 1.0, 0.5, 1.0), (6, 0.74, 0.36, 0.9))
    ):
        for i in range(count):
            angle = i * (360.0 / count) + layer * 30
            fill = d.radial(shade(base, 0.22), shade(mid, -0.06))
            pid = d.shape(_petal_path(UNIT * length, UNIT * width, UNIT * 0.02))
            parts.append(
                f'<use href="#{pid}" fill="url(#{fill})" stroke="{shade(dark, 0.1)}" '
                f'stroke-width="0.6" transform="rotate({n(angle)})" '
                f'opacity="{opacity}"/>'
            )
    # Stamens.
    for i in range(6):
        angle = i * 60 + 15
        tip = UNIT * 0.52
        px = math.sin(math.radians(angle)) * tip
        py = -math.cos(math.radians(angle)) * tip
        parts.append(
            f'<line x1="0" y1="0" x2="{n(px)}" y2="{n(py)}" '
            f'stroke="{shade(dark, -0.1)}" stroke-width="{n(UNIT * 0.045)}" '
            f'opacity="0.75"/>'
            f'<ellipse cx="{n(px)}" cy="{n(py)}" rx="{n(UNIT * 0.1)}" '
            f'ry="{n(UNIT * 0.06)}" fill="#c98b3a" '
            f'transform="rotate({n(angle)} {n(px)} {n(py)})"/>'
        )
    parts.append(f'<circle r="{n(UNIT * 0.1)}" fill="{shade(dark, 0.05)}"/>')
    return "".join(parts)


def build_orchid(d, colours, variant):
    base, mid, dark = _triad(colours)
    fill = d.radial(shade(base, 0.2), shade(mid, -0.04))
    parts = []
    # Two broad upper wings, two narrower laterals, one lip.
    for angle, length, width in (
        (-52, 0.95, 0.78), (52, 0.95, 0.78),
        (-118, 0.82, 0.6), (118, 0.82, 0.6),
        (180, 0.7, 0.66),
    ):
        pid = d.shape(_petal_path(UNIT * length, UNIT * width))
        parts.append(
            f'<use href="#{pid}" fill="url(#{fill})" stroke="{shade(dark, 0.08)}" '
            f'stroke-width="0.6" transform="rotate({n(angle)})"/>'
        )
    parts.append(
        f'<ellipse cy="{n(UNIT * 0.3)}" rx="{n(UNIT * 0.2)}" ry="{n(UNIT * 0.26)}" '
        f'fill="{shade("#b0578d", 0.25)}" opacity="0.8"/>'
    )
    parts.append(f'<circle r="{n(UNIT * 0.14)}" fill="{shade("#e8c86a", 0.1)}"/>')
    return "".join(parts)


def build_daisy(d, colours, variant):
    base, mid, dark = _triad(colours)
    parts = []
    count = 13
    for i in range(count):
        angle = i * (360.0 / count)
        fill = shade(base, 0.12) if i % 2 == 0 else shade(mid, -0.02)
        pid = d.shape(_petal_path(UNIT * 0.98, UNIT * 0.3))
        parts.append(
            f'<use href="#{pid}" fill="{fill}" '
            f'stroke="{shade(dark, -0.02)}" stroke-width="0.5" '
            f'transform="rotate({n(angle)})"/>'
        )
    parts.append(
        f'<circle r="{n(UNIT * 0.28)}" fill="url(#{d.radial("#f3c73f", "#c9962a")})"/>'
    )
    parts.append(
        f'<circle r="{n(UNIT * 0.16)}" fill="none" stroke="#b8842355" '
        f'stroke-width="{n(UNIT * 0.1)}"/>'
    )
    return "".join(parts)


def build_sunflower(d, colours, variant):
    base, mid, dark = _triad(colours)
    parts = []
    for layer, (count, length, width) in enumerate(((16, 1.0, 0.34), (14, 0.76, 0.28))):
        for i in range(count):
            angle = i * (360.0 / count) + layer * 12
            fill = shade(base, 0.1 - layer * 0.14)
            pid = d.shape(_petal_path(UNIT * length, UNIT * width, UNIT * 0.03))
            parts.append(
                f'<use href="#{pid}" fill="{fill}" stroke="{shade(dark, -0.05)}" '
                f'stroke-width="0.5" transform="rotate({n(angle)})"/>'
            )
    parts.append(f'<circle r="{n(UNIT * 0.42)}" fill="url(#{d.radial("#6b4a22", "#33210f")})"/>')
    for i in range(34):
        angle = i * 137.5
        r = UNIT * 0.4 * math.sqrt((i + 0.5) / 34)
        parts.append(
            f'<circle cx="{n(math.cos(math.radians(angle)) * r)}" '
            f'cy="{n(math.sin(math.radians(angle)) * r)}" '
            f'r="{n(UNIT * 0.045)}" fill="#8a6330" opacity="0.75"/>'
        )
    return "".join(parts)


def build_carnation(d, colours, variant):
    base, mid, dark = _triad(colours)
    rng = random.Random(hash((variant, "carn")) & 0xFFFF)
    parts = [f'<circle r="{n(UNIT * 0.5)}" fill="{shade(dark, -0.02)}"/>']
    # Many narrow, slightly uneven petals give the characteristic frilled edge.
    for ring, (count, length, width) in enumerate((
        (16, 1.0, 0.34), (14, 0.78, 0.3), (11, 0.56, 0.26), (8, 0.34, 0.22),
    )):
        parts += _petal_ring(
            d, count, UNIT * length, UNIT * width,
            base if ring % 2 == 0 else mid,
            offset=ring * 13, opacity=0.95, jitter=8, rng=rng, rounded=False,
            stroke=shade(dark, 0.3),
        )
    return "".join(parts)


def build_hydrangea(d, colours, variant):
    base, mid, dark = _triad(colours)
    rng = random.Random(hash((variant, "hyd")) & 0xFFFF)
    parts = [
        f'<circle r="{n(UNIT * 0.98)}" fill="url(#{d.radial(shade(mid, .1), shade(dark, -.05))})" '
        f'opacity="0.55"/>'
    ]
    # A mophead is a cluster of small four-petal florets.
    florets = 17
    for i in range(florets):
        angle = i * 137.5
        r = UNIT * 0.78 * math.sqrt((i + 0.4) / florets)
        fx = math.cos(math.radians(angle)) * r
        fy = math.sin(math.radians(angle)) * r
        colour = shade(base if i % 3 else mid, rng.uniform(-0.08, 0.16))
        spin = rng.uniform(0, 90)
        petals = []
        for p in range(4):
            petals.append(
                f'<ellipse cx="0" cy="{n(-UNIT * 0.17)}" rx="{n(UNIT * 0.13)}" '
                f'ry="{n(UNIT * 0.17)}" fill="{colour}" '
                f'transform="rotate({p * 90})"/>'
            )
        parts.append(
            f'<g transform="translate({n(fx)} {n(fy)}) rotate({n(spin)})">'
            + "".join(petals)
            + f'<circle r="{n(UNIT * 0.05)}" fill="{shade(colour, -0.3)}"/></g>'
        )
    return "".join(parts)


def build_thistle(d, colours, variant):
    base, mid, dark = _triad(colours)
    parts = []
    # Spiky bracts radiating from a textured cone.
    for i in range(14):
        angle = i * (360.0 / 14)
        parts.append(
            f'<path d="M0 0 L{n(-UNIT * 0.14)} {n(-UNIT * 0.55)} '
            f'L0 {n(-UNIT * 1.0)} L{n(UNIT * 0.14)} {n(-UNIT * 0.55)} Z" '
            f'fill="{shade(mid, 0.1 if i % 2 else -0.05)}" '
            f'transform="rotate({n(angle)})"/>'
        )
    parts.append(f'<ellipse rx="{n(UNIT * 0.4)}" ry="{n(UNIT * 0.46)}" '
                 f'fill="url(#{d.radial(shade(base, .2), shade(dark, -.1))})"/>')
    for i in range(22):
        angle = i * 137.5
        r = UNIT * 0.36 * math.sqrt((i + 0.5) / 22)
        parts.append(
            f'<circle cx="{n(math.cos(math.radians(angle)) * r)}" '
            f'cy="{n(math.sin(math.radians(angle)) * r * 1.15)}" '
            f'r="{n(UNIT * 0.055)}" fill="{shade(base, 0.35)}" opacity="0.8"/>'
        )
    return "".join(parts)


def build_gyp(d, colours, variant):
    """Gypsophila — a tiny airy cluster rather than a single bloom."""
    base, mid, dark = _triad(colours)
    rng = random.Random(hash((variant, "gyp")) & 0xFFFF)
    parts = []
    for _ in range(7):
        px = rng.uniform(-UNIT * 0.8, UNIT * 0.8)
        py = rng.uniform(-UNIT * 0.8, UNIT * 0.8)
        r = rng.uniform(UNIT * 0.16, UNIT * 0.3)
        parts.append(
            f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(r)}" fill="{base}" '
            f'opacity="0.95"/>'
            f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(r * 0.35)}" '
            f'fill="{shade(mid, -0.16)}" opacity="0.6"/>'
        )
    return "".join(parts)


def build_berry(d, colours, variant):
    base, mid, dark = _triad(colours)
    rng = random.Random(hash((variant, "berry")) & 0xFFFF)
    parts = []
    for _ in range(5):
        px = rng.uniform(-UNIT * 0.55, UNIT * 0.55)
        py = rng.uniform(-UNIT * 0.55, UNIT * 0.55)
        r = rng.uniform(UNIT * 0.24, UNIT * 0.36)
        parts.append(
            f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(r)}" '
            f'fill="url(#{d.radial(shade(base, .35), shade(dark, -.15))})"/>'
        )
    return "".join(parts)


FLOWER_BUILDERS = {
    "rose": build_rose,
    "peony": build_peony,
    "ranunculus": build_ranunculus,
    "tulip": build_tulip,
    "lily": build_lily,
    "orchid": build_orchid,
    "daisy": build_daisy,
    "sunflower": build_sunflower,
    "carnation": build_carnation,
    "hydrangea": build_hydrangea,
    "thistle": build_thistle,
    "gyp": build_gyp,
    "berry": build_berry,
}

# Nominal on-canvas diameters, before per-position scaling.
FLOWER_SIZES = {
    "rose": 96, "peony": 118, "ranunculus": 82, "tulip": 84, "lily": 108,
    "orchid": 104, "daisy": 74, "sunflower": 124, "carnation": 88,
    "hydrangea": 132, "thistle": 54, "gyp": 46, "berry": 40,
}


def _triad(colours):
    """Expand a recipe's colour list into (base, mid, dark)."""
    base = colours[0]
    mid = colours[1] if len(colours) > 1 else shade(base, -0.1)
    dark = colours[2] if len(colours) > 2 else shade(mid, -0.28)
    return base, mid, dark


# ---------------------------------------------------------------------------
# Foliage
# ---------------------------------------------------------------------------

def build_leaf(d, colour, kind="pointed"):
    if kind == "round":
        # Eucalyptus-style sprig: paired round leaves along a stem.
        parts = [
            f'<path d="M0 0 C{n(UNIT * 0.1)} {n(-UNIT * 0.6)} {n(-UNIT * 0.1)} '
            f'{n(-UNIT * 1.2)} 0 {n(-UNIT * 1.8)}" fill="none" '
            f'stroke="{shade(colour, -0.2)}" stroke-width="{n(UNIT * 0.07)}"/>'
        ]
        for i in range(5):
            y = -UNIT * (0.3 + i * 0.32)
            r = UNIT * (0.3 - i * 0.035)
            for side in (-1, 1):
                parts.append(
                    f'<ellipse cx="{n(side * r * 0.85)}" cy="{n(y)}" rx="{n(r)}" '
                    f'ry="{n(r * 0.82)}" fill="{shade(colour, 0.06 * i)}" '
                    f'opacity="0.95"/>'
                )
        return "".join(parts)
    # Pointed leaf with a centre vein.
    leaf = (
        f"M0 0 C{n(-UNIT * 0.42)} {n(-UNIT * 0.6)} {n(-UNIT * 0.3)} "
        f"{n(-UNIT * 1.35)} 0 {n(-UNIT * 1.75)} "
        f"C{n(UNIT * 0.3)} {n(-UNIT * 1.35)} {n(UNIT * 0.42)} "
        f"{n(-UNIT * 0.6)} 0 0 Z"
    )
    return (
        f'<path d="{leaf}" fill="url(#{d.linear(shade(colour, 0.16), shade(colour, -0.22))})"/>'
        f'<path d="M0 {n(-UNIT * 0.08)} L0 {n(-UNIT * 1.6)}" fill="none" '
        f'stroke="{shade(colour, -0.3)}" stroke-width="{n(UNIT * 0.045)}" '
        f'opacity="0.55"/>'
    )


# ---------------------------------------------------------------------------
# Vessels
# ---------------------------------------------------------------------------

def draw_hatbox(d, cx, top, width, height, colours, ribbon):
    body, dark = colours[0], colours[1]
    half = width / 2.0
    lip = height * 0.16
    grad = d.linear(shade(body, 0.14), shade(dark, -0.05), 0, 0, 1, 0)
    d.add(
        f'<path d="M{n(cx - half)} {n(top + lip)} '
        f'L{n(cx - half * 0.9)} {n(top + height)} '
        f'Q{n(cx)} {n(top + height + height * 0.11)} '
        f'{n(cx + half * 0.9)} {n(top + height)} '
        f'L{n(cx + half)} {n(top + lip)} Z" fill="url(#{grad})"/>'
    )
    # Lid rim.
    d.add(
        f'<ellipse cx="{n(cx)}" cy="{n(top + lip)}" rx="{n(half)}" '
        f'ry="{n(lip * 0.86)}" fill="{shade(body, 0.2)}"/>'
        f'<ellipse cx="{n(cx)}" cy="{n(top + lip)}" rx="{n(half * 0.9)}" '
        f'ry="{n(lip * 0.7)}" fill="{shade(dark, -0.12)}"/>'
    )
    # Ribbon band and bow.
    band_y = top + height * 0.62
    d.add(
        f'<path d="M{n(cx - half * 0.955)} {n(band_y)} '
        f'L{n(cx + half * 0.955)} {n(band_y)} '
        f'L{n(cx + half * 0.94)} {n(band_y + height * 0.16)} '
        f'L{n(cx - half * 0.94)} {n(band_y + height * 0.16)} Z" '
        f'fill="{ribbon}" opacity="0.95"/>'
    )
    bow_y = band_y + height * 0.08
    for side in (-1, 1):
        d.add(
            f'<path d="M{n(cx)} {n(bow_y)} '
            f'C{n(cx + side * width * 0.2)} {n(bow_y - height * 0.16)} '
            f'{n(cx + side * width * 0.26)} {n(bow_y + height * 0.12)} '
            f'{n(cx)} {n(bow_y)} Z" fill="{shade(ribbon, 0.16)}" '
            f'stroke="{shade(ribbon, -0.2)}" stroke-width="1"/>'
        )
    d.add(f'<circle cx="{n(cx)}" cy="{n(bow_y)}" r="{n(width * 0.035)}" '
          f'fill="{shade(ribbon, -0.12)}"/>')


def draw_vase(d, cx, top, width, height, colours, ribbon):
    body, dark = colours[0], colours[1]
    half = width / 2.0
    neck = half * 0.62
    grad = d.linear(shade(body, 0.3), shade(dark, -0.02), 0, 0, 1, 0)
    d.add(
        f'<path d="M{n(cx - neck)} {n(top)} '
        f'C{n(cx - half * 1.02)} {n(top + height * 0.45)} '
        f'{n(cx - half)} {n(top + height * 0.75)} '
        f'{n(cx - half * 0.8)} {n(top + height)} '
        f'L{n(cx + half * 0.8)} {n(top + height)} '
        f'C{n(cx + half)} {n(top + height * 0.75)} '
        f'{n(cx + half * 1.02)} {n(top + height * 0.45)} '
        f'{n(cx + neck)} {n(top)} Z" fill="url(#{grad})" opacity="0.9"/>'
    )
    # Water line and glass highlight.
    water_y = top + height * 0.34
    d.add(
        f'<path d="M{n(cx - half * 0.93)} {n(water_y)} '
        f'C{n(cx - half * 1.0)} {n(top + height * 0.7)} '
        f'{n(cx - half * 0.94)} {n(top + height * 0.86)} '
        f'{n(cx - half * 0.76)} {n(top + height * 0.97)} '
        f'L{n(cx + half * 0.76)} {n(top + height * 0.97)} '
        f'C{n(cx + half * 0.94)} {n(top + height * 0.86)} '
        f'{n(cx + half * 1.0)} {n(top + height * 0.7)} '
        f'{n(cx + half * 0.93)} {n(water_y)} Z" '
        f'fill="{shade(dark, 0.1)}" opacity="0.45"/>'
        f'<ellipse cx="{n(cx)}" cy="{n(water_y)}" rx="{n(half * 0.93)}" '
        f'ry="{n(half * 0.16)}" fill="{shade(body, 0.42)}" opacity="0.5"/>'
    )
    d.add(
        f'<path d="M{n(cx - half * 0.55)} {n(top + height * 0.14)} '
        f'C{n(cx - half * 0.78)} {n(top + height * 0.45)} '
        f'{n(cx - half * 0.7)} {n(top + height * 0.7)} '
        f'{n(cx - half * 0.55)} {n(top + height * 0.9)}" fill="none" '
        f'stroke="#ffffff" stroke-width="{n(width * 0.05)}" stroke-linecap="round" '
        f'opacity="0.45"/>'
    )
    d.add(
        f'<ellipse cx="{n(cx)}" cy="{n(top)}" rx="{n(neck)}" '
        f'ry="{n(neck * 0.26)}" fill="{shade(body, 0.34)}" opacity="0.8"/>'
    )


def draw_basket(d, cx, top, width, height, colours, ribbon):
    body, dark = colours[0], colours[1]
    half = width / 2.0
    grad = d.linear(shade(body, 0.16), shade(dark, -0.08), 0, 0, 1, 0)
    d.add(
        f'<path d="M{n(cx - half)} {n(top)} '
        f'L{n(cx - half * 0.72)} {n(top + height)} '
        f'Q{n(cx)} {n(top + height + height * 0.16)} '
        f'{n(cx + half * 0.72)} {n(top + height)} '
        f'L{n(cx + half)} {n(top)} Z" fill="url(#{grad})"/>'
    )
    # Woven texture.
    rows = 5
    for i in range(1, rows):
        y = top + height * (i / rows)
        inset = half * (1 - 0.28 * (i / rows))
        d.add(
            f'<path d="M{n(cx - inset)} {n(y)} Q{n(cx)} {n(y + height * 0.05)} '
            f'{n(cx + inset)} {n(y)}" fill="none" stroke="{shade(dark, -0.16)}" '
            f'stroke-width="{n(height * 0.035)}" opacity="0.55"/>'
        )
    cols = 9
    for i in range(cols + 1):
        x = cx - half + (width * i / cols)
        d.add(
            f'<line x1="{n(x)}" y1="{n(top)}" x2="{n(cx + (x - cx) * 0.74)}" '
            f'y2="{n(top + height)}" stroke="{shade(body, 0.2)}" '
            f'stroke-width="{n(width * 0.012)}" opacity="0.5"/>'
        )
    # Rim and handle.
    d.add(
        f'<ellipse cx="{n(cx)}" cy="{n(top)}" rx="{n(half)}" ry="{n(height * 0.13)}" '
        f'fill="{shade(body, 0.26)}" stroke="{shade(dark, -0.1)}" stroke-width="1.5"/>'
    )
    d.add(
        f'<path d="M{n(cx - half * 0.78)} {n(top - height * 0.02)} '
        f'A{n(half * 0.8)} {n(height * 0.95)} 0 0 1 '
        f'{n(cx + half * 0.78)} {n(top - height * 0.02)}" fill="none" '
        f'stroke="{shade(dark, -0.05)}" stroke-width="{n(width * 0.035)}" '
        f'stroke-linecap="round" opacity="0.9"/>'
    )


def draw_wrap(d, cx, top, width, height, colours, ribbon):
    """A hand-tied bouquet's paper cone."""
    body, dark = colours[0], colours[1]
    half = width / 2.0
    grad = d.linear(shade(body, 0.2), shade(dark, -0.12), 0, 0, 1, 0)
    d.add(
        f'<path d="M{n(cx - half)} {n(top)} '
        f'L{n(cx - width * 0.11)} {n(top + height)} '
        f'L{n(cx + width * 0.11)} {n(top + height)} '
        f'L{n(cx + half)} {n(top)} Z" fill="url(#{grad})"/>'
    )
    # Paper folds.
    for frac in (-0.62, -0.28, 0.05, 0.38, 0.7):
        x = cx + half * frac
        d.add(
            f'<line x1="{n(x)}" y1="{n(top)}" '
            f'x2="{n(cx + width * 0.11 * frac)}" y2="{n(top + height)}" '
            f'stroke="{shade(dark, -0.1)}" stroke-width="{n(width * 0.012)}" '
            f'opacity="0.4"/>'
        )
    # Upper edge of the paper, sitting behind the stems.
    d.add(
        f'<path d="M{n(cx - half)} {n(top)} Q{n(cx)} {n(top + height * 0.14)} '
        f'{n(cx + half)} {n(top)} Q{n(cx)} {n(top - height * 0.06)} '
        f'{n(cx - half)} {n(top)} Z" fill="{shade(body, 0.3)}"/>'
    )
    # Ribbon tie.
    tie_y = top + height * 0.45
    tie_w = width * 0.3
    d.add(
        f'<path d="M{n(cx - tie_w / 2)} {n(tie_y)} L{n(cx + tie_w / 2)} {n(tie_y)} '
        f'L{n(cx + tie_w * 0.42)} {n(tie_y + height * 0.14)} '
        f'L{n(cx - tie_w * 0.42)} {n(tie_y + height * 0.14)} Z" fill="{ribbon}"/>'
    )
    for side in (-1, 1):
        d.add(
            f'<path d="M{n(cx)} {n(tie_y + height * 0.06)} '
            f'C{n(cx + side * width * 0.2)} {n(tie_y - height * 0.1)} '
            f'{n(cx + side * width * 0.24)} {n(tie_y + height * 0.2)} '
            f'{n(cx)} {n(tie_y + height * 0.06)} Z" '
            f'fill="{shade(ribbon, 0.18)}" stroke="{shade(ribbon, -0.22)}" '
            f'stroke-width="1"/>'
        )
        d.add(
            f'<path d="M{n(cx)} {n(tie_y + height * 0.08)} '
            f'Q{n(cx + side * width * 0.1)} {n(tie_y + height * 0.34)} '
            f'{n(cx + side * width * 0.16)} {n(tie_y + height * 0.5)}" fill="none" '
            f'stroke="{shade(ribbon, 0.05)}" stroke-width="{n(width * 0.028)}" '
            f'stroke-linecap="round"/>'
        )


def draw_pot(d, cx, top, width, height, colours, ribbon):
    body, dark = colours[0], colours[1]
    half = width / 2.0
    grad = d.linear(shade(body, 0.16), shade(dark, -0.06), 0, 0, 1, 0)
    d.add(
        f'<path d="M{n(cx - half)} {n(top)} L{n(cx - half * 0.78)} {n(top + height)} '
        f'Q{n(cx)} {n(top + height + height * 0.12)} '
        f'{n(cx + half * 0.78)} {n(top + height)} '
        f'L{n(cx + half)} {n(top)} Z" fill="url(#{grad})"/>'
    )
    d.add(
        f'<ellipse cx="{n(cx)}" cy="{n(top)}" rx="{n(half)}" ry="{n(height * 0.16)}" '
        f'fill="{shade(body, 0.24)}"/>'
        f'<ellipse cx="{n(cx)}" cy="{n(top)}" rx="{n(half * 0.86)}" '
        f'ry="{n(height * 0.13)}" fill="{shade(dark, -0.2)}"/>'
    )
    # Moss dressing.
    for i in range(16):
        rr = d.rng.uniform(-half * 0.8, half * 0.8)
        d.add(
            f'<ellipse cx="{n(cx + rr)}" cy="{n(top + d.rng.uniform(-3, 4))}" '
            f'rx="{n(d.rng.uniform(width * 0.05, width * 0.11))}" '
            f'ry="{n(height * 0.05)}" fill="{shade("#6d7f4a", d.rng.uniform(-.2, .2))}" '
            f'opacity="0.85"/>'
        )


VESSEL_DRAWERS = {
    "hatbox": draw_hatbox,
    "vase": draw_vase,
    "basket": draw_basket,
    "wrap": draw_wrap,
    "pot": draw_pot,
}

# vessel -> (vessel top y, vessel width, vessel height, dome cy, dome rx, dome ry)
# expressed as fractions of the canvas, for a 4:5 portrait frame. The dome is
# positioned so its lower edge sits *inside* the vessel mouth — a bouquet that
# hovers above its container is the single most artificial-looking mistake here.
VESSEL_LAYOUT = {
    "hatbox": (0.615, 0.50, 0.28, 0.470, 0.300, 0.175),
    "vase":   (0.545, 0.28, 0.38, 0.375, 0.305, 0.195),
    "basket": (0.635, 0.54, 0.235, 0.490, 0.320, 0.170),
    "wrap":   (0.575, 0.48, 0.35, 0.415, 0.305, 0.200),
    "pot":    (0.685, 0.32, 0.20, 0.490, 0.250, 0.210),
}

# Blooms with an obvious "up" — a tulip lying on its side looks broken, whereas
# a rose is radially symmetric and can spin freely.
UPRIGHT_FLOWERS = {"tulip", "sunflower", "orchid", "lily"}

# Roughly what fraction of its own bounding circle each species actually inks
# in. A hydrangea mophead is nearly solid; a daisy is mostly gaps between
# petals. Without this the airy species leave visible holes in the dome.
FILL_FACTOR = {
    "rose": 0.85, "peony": 0.85, "ranunculus": 0.85, "carnation": 0.78,
    "hydrangea": 0.8, "tulip": 0.5, "lily": 0.5, "orchid": 0.5,
    "daisy": 0.45, "sunflower": 0.6, "thistle": 0.35, "gyp": 0.25,
    "berry": 0.4,
}

# Target inked area inside the dome, as a multiple of the dome's own area.
DOME_COVERAGE = 1.45


# ---------------------------------------------------------------------------
# Arrangement composition
# ---------------------------------------------------------------------------

def dome_positions(rng, count, cx, cy, rx, ry):
    """Phyllotaxis-style scatter inside an ellipse, jittered for naturalness."""
    positions = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(count):
        t = (i + 0.5) / count
        radius = math.sqrt(t)
        angle = i * golden + rng.uniform(-0.35, 0.35)
        px = cx + math.cos(angle) * radius * rx * rng.uniform(0.9, 1.06)
        py = cy + math.sin(angle) * radius * ry * rng.uniform(0.9, 1.06)
        positions.append((px, py, radius))
    return positions


def draw_arrangement(d, art, cx, cy_frame, width, height, seed=0):
    """Draw a complete vessel + bouquet composition inside the given frame."""
    rng = random.Random(seed)
    d.rng = rng
    vessel = art["vessel"]
    v_top_f, v_w_f, v_h_f, dome_cy_f, dome_rx_f, dome_ry_f = VESSEL_LAYOUT[vessel]

    v_top = cy_frame + height * v_top_f
    v_width = width * v_w_f
    v_height = height * v_h_f
    dome_cx = cx
    dome_cy = cy_frame + height * dome_cy_f
    dome_rx = width * dome_rx_f
    dome_ry = height * dome_ry_f

    foliage_colour = art.get("foliage", "#5d7f52")
    px_scale = width / 800.0

    # Contact shadow beneath the vessel.
    d.add(
        f'<ellipse cx="{n(cx)}" cy="{n(v_top + v_height * 1.02)}" '
        f'rx="{n(v_width * 0.66)}" ry="{n(v_height * 0.11)}" fill="#3a2f28" '
        f'opacity="0.16"/>'
    )

    leaf_round = d.symbol(
        ("leaf", foliage_colour, "round"),
        lambda: build_leaf(d, foliage_colour, "round"),
    )
    leaf_point = d.symbol(
        ("leaf", foliage_colour, "pointed"),
        lambda: build_leaf(d, shade(foliage_colour, -0.08), "pointed"),
    )

    # --- foliage fanning out behind the blooms ---------------------------
    for i in range(20):
        angle = -170 + i * (340.0 / 19) + rng.uniform(-6, 6)
        rad = math.radians(angle)
        reach = rng.uniform(0.88, 1.1)
        px = dome_cx + math.sin(rad) * dome_rx * reach
        py = dome_cy - math.cos(rad) * dome_ry * reach * 0.94
        sym = leaf_round if i % 2 == 0 else leaf_point
        d.use(
            sym, px, py,
            rng.uniform(0.62, 0.95) * px_scale,
            angle + rng.uniform(-14, 14),
            opacity=rng.uniform(0.85, 1.0),
        )

    # A soft mass behind the blooms, so any gap between stems reads as depth
    # rather than as a hole through to the background. It is heavily blurred —
    # a hard-edged ellipse here shows through as an obvious green dome.
    d.add(
        f'<ellipse cx="{n(dome_cx)}" cy="{n(dome_cy + dome_ry * 0.14)}" '
        f'rx="{n(dome_rx * 0.72)}" ry="{n(dome_ry * 0.7)}" '
        f'fill="{shade(foliage_colour, -0.3)}" opacity="0.32" '
        f'filter="url(#{d.blur(dome_rx * 0.1)})"/>'
    )
    # Dark filler leaves inside the mass fill the gaps between blooms.
    for _ in range(16):
        angle = rng.uniform(0, 360)
        radius = math.sqrt(rng.random())
        px = dome_cx + math.sin(math.radians(angle)) * dome_rx * radius * 0.95
        py = dome_cy - math.cos(math.radians(angle)) * dome_ry * radius * 0.95
        d.use(
            leaf_point, px, py,
            rng.uniform(0.4, 0.62) * px_scale,
            rng.uniform(0, 360),
            opacity=0.85,
        )

    # --- blooms ---------------------------------------------------------
    # Scale every bloom so the recipe's stem counts actually fill the dome.
    # Writing exact counts per product by hand never survives a layout tweak;
    # solving for coverage does.
    dome_area = math.pi * dome_rx * dome_ry
    natural_area = sum(
        count * math.pi * ((FLOWER_SIZES[kind] * px_scale) / 2.0) ** 2
        * FILL_FACTOR[kind]
        for kind, _colours, count in art["blooms"]
    )
    wanted = math.sqrt(dome_area * DOME_COVERAGE / natural_area) if natural_area else 1.0
    # Prefer resizing the blooms, but only within a believable range. Beyond
    # that, add more stems rather than growing individual flowers absurdly.
    fit = max(0.75, min(1.45, wanted))
    stem_multiplier = max(1.0, (wanted / fit) ** 2)

    stamps = []
    for bloom_index, (kind, colours, count) in enumerate(art["blooms"]):
        builder = FLOWER_BUILDERS[kind]
        count = max(1, round(count * stem_multiplier))
        base_size = FLOWER_SIZES[kind] * px_scale * fit
        variants = [
            d.symbol(
                (kind, tuple(colours), v),
                lambda k=kind, c=colours, v=v, b=builder: b(d, c, v),
            )
            for v in range(2)
        ]
        upright = kind in UPRIGHT_FLOWERS
        # Later bloom types sit slightly tighter, which layers them forward.
        spread = 1.0 - bloom_index * 0.05
        for px, py, radial in dome_positions(
            rng,
            count,
            dome_cx,
            dome_cy,
            dome_rx * spread,
            dome_ry * spread,
        ):
            # Blooms shrink slightly towards the edge to imply a domed surface.
            size = base_size * (1.0 - 0.18 * radial) * rng.uniform(0.88, 1.12)
            rotation = rng.uniform(-22, 22) if upright else rng.uniform(0, 360)
            stamps.append((py, rng.choice(variants), px, py, size / 100.0, rotation))

    # Painter's algorithm: higher on the canvas means further back.
    stamps.sort(key=lambda s: s[0])
    for _, sym, px, py, scale, rot in stamps:
        d.use(sym, px, py, scale, rot)

    # --- a few foliage tips in front ------------------------------------
    for i in range(6):
        angle = -135 + i * 54 + rng.uniform(-12, 12)
        rad = math.radians(angle)
        px = dome_cx + math.sin(rad) * dome_rx * rng.uniform(0.8, 1.02)
        py = dome_cy - math.cos(rad) * dome_ry * rng.uniform(0.7, 0.95)
        d.use(
            leaf_round, px, py,
            rng.uniform(0.42, 0.6) * px_scale,
            angle + rng.uniform(-20, 20),
            opacity=0.9,
        )

    # --- vessel on top so the stems disappear behind it ------------------
    VESSEL_DRAWERS[vessel](
        d, cx, v_top, v_width, v_height,
        art.get("vessel_colors", ["#d8cfc2", "#b8ad9c"]),
        art.get("ribbon", "#b8934a"),
    )


def backdrop(d, colours, width, height, seed=0):
    rng = random.Random(seed + 991)
    inner, outer = colours[0], colours[1]
    gid = d.radial(inner, outer, "50%", "38%")
    d.add(f'<rect width="{width}" height="{height}" fill="url(#{gid})"/>')
    # Soft out-of-focus circles for depth.
    for _ in range(7):
        d.add(
            f'<circle cx="{n(rng.uniform(0, width))}" '
            f'cy="{n(rng.uniform(0, height * 0.75))}" '
            f'r="{n(rng.uniform(width * 0.06, width * 0.2))}" fill="#ffffff" '
            f'opacity="{rng.uniform(0.05, 0.13):.2f}"/>'
        )
    # Table line.
    d.add(
        f'<rect y="{n(height * 0.86)}" width="{width}" height="{n(height * 0.14)}" '
        f'fill="{shade(outer, -0.1)}" opacity="0.4"/>'
    )


# ---------------------------------------------------------------------------
# Output builders
# ---------------------------------------------------------------------------

def render_product(product, width=800, height=1000):
    seed = abs(hash(product["slug"])) % 10_000
    d = Drawing(width, height, seed)
    art = product["art"]
    backdrop(d, art.get("backdrop", ["#faf5ef", "#eadfd3"]), width, height, seed)
    draw_arrangement(d, art, width / 2.0, 0, width, height, seed)
    return d.render(f'{product["name"]} — Nested Blooms')


def render_square(art, slug, size=700):
    """Square framing used for collection and occasion tiles."""
    seed = abs(hash(slug)) % 10_000
    d = Drawing(size, size, seed)
    backdrop(d, art.get("backdrop", ["#faf5ef", "#eadfd3"]), size, size, seed)
    # Tiles carry a caption gradient across the bottom quarter, so the
    # composition is compressed to finish above it rather than being clipped.
    draw_arrangement(d, art, size / 2.0, -size * 0.05, size, size * 0.95, seed)
    return d.render(slug)


def render_hero(width=1600, height=1000):
    """Wide studio scene: three arrangements at different depths."""
    d = Drawing(width, height, 77)
    gid = d.radial("#fdf8f2", "#e9d9cc", "42%", "30%")
    d.add(f'<rect width="{width}" height="{height}" fill="url(#{gid})"/>')
    for _ in range(11):
        d.add(
            f'<circle cx="{n(d.rng.uniform(0, width))}" '
            f'cy="{n(d.rng.uniform(0, height * 0.7))}" '
            f'r="{n(d.rng.uniform(60, 230))}" fill="#ffffff" '
            f'opacity="{d.rng.uniform(0.05, 0.14):.2f}"/>'
        )
    d.add(
        f'<rect y="{n(height * 0.78)}" width="{width}" height="{n(height * 0.22)}" '
        f'fill="#c9ae97" opacity="0.45"/>'
    )

    left = {
        "vessel": "vase",
        "vessel_colors": ["#cfe0e8", "#a9c4d1"],
        "ribbon": "#7fa3b8",
        "foliage": "#5b8168",
        "blooms": [
            ["hydrangea", ["#8fa8d8", "#7592c9"], 4],
            ["rose", ["#fdfdfb", "#f0eee6"], 7],
            ["gyp", ["#ffffff"], 12],
        ],
    }
    right = {
        "vessel": "basket",
        "vessel_colors": ["#c69a63", "#a67a45"],
        "ribbon": "#8d9d72",
        "foliage": "#6e8f52",
        "blooms": [
            ["rose", ["#f4a06a", "#ef8b52"], 8],
            ["daisy", ["#fdfaf0"], 7],
            ["gyp", ["#fffdf6"], 12],
        ],
    }
    centre = {
        "vessel": "hatbox",
        "vessel_colors": ["#2a2622", "#171412"],
        "ribbon": "#b8934a",
        "foliage": "#3d6b4f",
        "blooms": [
            ["peony", ["#f0b3c2", "#e59bae"], 8],
            ["rose", ["#c0173c", "#a01230", "#87102a"], 12],
            ["ranunculus", ["#f8ddd8", "#eec6c3"], 7],
            ["gyp", ["#ffffff"], 16],
        ],
    }

    # Back arrangements first, slightly faded to sit behind the hero piece.
    d.add('<g opacity="0.82">')
    draw_arrangement(d, left, width * 0.19, height * 0.1, width * 0.42, height * 0.78, 21)
    d.add("</g>")
    d.add('<g opacity="0.85">')
    draw_arrangement(d, right, width * 0.83, height * 0.12, width * 0.4, height * 0.76, 34)
    d.add("</g>")
    draw_arrangement(d, centre, width * 0.5, height * 0.02, width * 0.48, height, 12)
    return d.render("Nested Blooms hand-tied arrangements")


def render_logo():
    """A compact mark: a single bloom nested inside a ring."""
    d = Drawing(120, 120, 5)
    d.add('<circle cx="60" cy="60" r="55" fill="none" stroke="#2f5d4a" '
          'stroke-width="4"/>')
    rose = d.symbol(("logo", "rose"), lambda: build_rose(d, ["#d98da0", "#c4758a"], 0))
    leaf = d.symbol(("logo", "leaf"), lambda: build_leaf(d, "#3f6b4f", "pointed"))
    d.use(leaf, 34, 84, 0.4, -52)
    d.use(leaf, 86, 84, 0.4, 52)
    d.use(leaf, 60, 92, 0.34, 0)
    d.use(rose, 60, 54, 0.78, 0)
    return d.render("Nested Blooms")


def render_pattern():
    """A tileable botanical pattern used behind newsletter/footer panels."""
    d = Drawing(240, 240, 3)
    d.add('<rect width="240" height="240" fill="none"/>')
    leaf = d.symbol(("pat", "leaf"), lambda: build_leaf(d, "#2f5d4a", "round"))
    for x, y, rot in ((40, 70, -20), (150, 40, 30), (95, 165, 12),
                      (205, 150, -35), (10, 190, 45)):
        d.use(leaf, x, y, 0.28, rot, opacity=0.5)
    return d.render("Botanical pattern")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return len(content)


def main():
    total = 0
    largest = ("", 0)

    for product in catalog.PRODUCTS:
        path = os.path.join(IMG_DIR, "products", f'{product["slug"]}.svg')
        size = write(path, render_product(product))
        total += size
        if size > largest[1]:
            largest = (product["slug"], size)

    # Collection tiles reuse the first product in each collection.
    for collection in catalog.COLLECTIONS:
        member = next(
            (p for p in catalog.PRODUCTS if p["collection"] == collection["slug"]),
            None,
        )
        if member:
            path = os.path.join(IMG_DIR, "collections", f'{collection["slug"]}.svg')
            total += write(path, render_square(member["art"], collection["slug"]))

    # Occasion tiles: assign each occasion a *different* product, so the grid
    # on the homepage does not show the same red hatbox four times over.
    # Scarcest occasions choose first, since they have the fewest candidates.
    candidates = {
        occasion["slug"]: [
            p for p in catalog.PRODUCTS if occasion["slug"] in p["occasions"]
        ]
        for occasion in catalog.OCCASIONS
    }
    taken = set()
    chosen = {}
    for slug in sorted(candidates, key=lambda s: len(candidates[s])):
        pick = next(
            (p for p in candidates[slug] if p["slug"] not in taken),
            candidates[slug][0] if candidates[slug] else None,
        )
        if pick:
            chosen[slug] = pick
            taken.add(pick["slug"])

    for occasion in catalog.OCCASIONS:
        member = chosen.get(occasion["slug"])
        if member:
            path = os.path.join(IMG_DIR, "occasions", f'{occasion["slug"]}.svg')
            total += write(path, render_square(member["art"], occasion["slug"], 560))

    total += write(os.path.join(IMG_DIR, "scenes", "hero.svg"), render_hero())
    total += write(os.path.join(IMG_DIR, "logo.svg"), render_logo())
    total += write(os.path.join(IMG_DIR, "pattern.svg"), render_pattern())

    count = len(catalog.PRODUCTS) + len(catalog.COLLECTIONS) + len(catalog.OCCASIONS) + 3
    print(f"Wrote {count} SVG files, {total / 1024:.0f}KB total")
    print(f"Largest product file: {largest[0]} at {largest[1] / 1024:.1f}KB")


if __name__ == "__main__":
    main()
