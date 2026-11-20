#!/usr/bin/env python3
"""Front page of "THE WORLD TODAY" for Friday 20 November 2026.

One self-contained program, standard library only (math, os, struct,
sys, zlib). It paints a 1024x1024 newspaper page -- a masthead with
the day's date, one big lead story, four more stories in a row, and a
pair of short items at the foot -- then saves it as a PNG.

Everything is drawn from scratch in code: a tiny 5x7 pixel typeface
kept as numbers, a small canvas that knows how to fill boxes, draw
lines and stars, and a hand-rolled PNG writer. Nothing is read from
disk, nothing comes from the network, and there is no clock or random
number anywhere, so running the program twice produces the exact
same bytes.

The seven stories on the page, all from 20 November 2026:

  * Lead -- Trump, Xi and Putin sit down together in Shenzhen, the
    first summit of the three; a joint peace declaration, but no
    agreement on Ukraine or Iran.
  * Ukraine -- Russia's heaviest overnight strike yet: 110+ missiles
    and about 400 drones; 8 people killed and 28 hurt in Kyiv.
  * Justice -- the world court finds Myanmar guilty of genocide
    against the Rohingya, the first such verdict against a state,
    decided 9-6.
  * Markets -- Anthropic's IPO closes at $97, up 17% on its $83
    offer; the S&P and Nasdaq slip about 2%, the Nikkei falls 4.8%
    and SoftBank drops 16%.
  * Middle East -- a Houthi missile damages the Saudi PIF tower in
    Riyadh.
  * Also -- GTA 6 passes $2.3bn in sales, a launch record.
  * Also -- Kenya's last Ebola patient goes home, 37 days after the
    first case was found.
"""

import math
import os
import struct
import sys
import zlib

SIZE = 1024  # the page is square, 1024 by 1024 pixels

# ------------------------------------------------------------------ colours
# One lookup table instead of a pile of loose constants. Every colour
# on the page comes from here, by name.
PAL = {
    "paper": (247, 242, 230),   # warm newsprint
    "card": (255, 253, 246),    # white of a story box
    "ink": (26, 26, 26),        # near-black text and rules
    "grey": (120, 120, 118),    # light grey (smoke, small marks)
    "dim": (64, 64, 64),        # dark grey body copy
    "red": (179, 38, 30),       # masthead rule, kicker bars
    "scarlet": (214, 48, 24),   # falling-market arrow
    "navy": (31, 78, 121),      # lead kicker, US canton, skyline
    "midnight": (24, 40, 56),   # ground strip under skylines
    "blue": (47, 117, 181),     # Ukraine kicker, Russian stripe
    "sky": (214, 232, 240),     # dawn sky, tower windows
    "night": (18, 32, 58),      # Kyiv night sky
    "sand": (232, 210, 160),    # desert ground behind the tower
    "sea": (58, 122, 158),      # unused spare, kept for balance
    "teal": (38, 110, 100),     # Justice kicker
    "green": (46, 125, 58),     # rising bar, medical cross
    "forest": (46, 92, 58),     # spare deep green
    "gold": (201, 162, 39),     # stars, lit windows
    "yellow": (240, 200, 60),   # blasts, missile heads, sun
    "orange": (224, 122, 33),   # inner blast
    "cream": (255, 248, 220),   # bottom strip background
    "mint": (220, 235, 230),    # Justice picture background
    "brown": (146, 90, 32),     # Middle East kicker
    "dawn": (224, 84, 48),      # rising sun over Shenzhen
    "glass": (38, 68, 96),      # PIF tower glass
    "pale": (250, 222, 182),    # Riyadh sky
}

# ------------------------------------------------------------------ typeface
# A 5x7 bitmap face for capitals, digits and common punctuation. Each
# glyph is seven numbers, one per row, read top to bottom; inside a
# number the five bits are the five pixels left to right, so 0x0E
# means 01110 and 0x1F means 11111. A set bit paints ink, a clear bit
# leaves the paper alone. Anything not in the table prints as "?".
GLYPHS = {
    ' ': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '%': (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '*': (0x00, 0x15, 0x0E, 0x1F, 0x0E, 0x15, 0x00),
    '+': (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    '-': (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ':': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ';': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    '=': (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    '?': (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '_': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
}


# ------------------------------------------------------------------ canvas
class Sheet:
    """A square sheet of RGB pixels with a small drawing vocabulary.

    Everything is clipped to the sheet, so callers never have to worry
    about running off an edge. Coordinates are plain ints; colours are
    (r, g, b) triples taken from PAL.
    """

    def __init__(self, size, background):
        self.size = size
        self.buf = bytearray(size * size * 3)
        self.box(0, 0, size, size, background)

    # -- single pixels and rectangles -------------------------------
    def dot(self, x, y, rgb):
        if 0 <= x < self.size and 0 <= y < self.size:
            at = (y * self.size + x) * 3
            self.buf[at:at + 3] = bytes(rgb)

    def box(self, x, y, w, h, rgb):
        left = max(0, x)
        top = max(0, y)
        right = min(self.size, x + w)
        bottom = min(self.size, y + h)
        if right <= left or bottom <= top:
            return
        row = bytes(rgb) * (right - left)
        for yy in range(top, bottom):
            at = (yy * self.size + left) * 3
            self.buf[at:at + len(row)] = row

    def hbar(self, x, y, w, rgb, thick=1):
        self.box(x, y, w, thick, rgb)

    def vbar(self, x, y, h, rgb, thick=1):
        self.box(x, y, thick, h, rgb)

    # -- lines, discs, polygons -------------------------------------
    def seg(self, x0, y0, x1, y1, rgb, thick=1):
        """A straight segment, Bresenham's walk, square brush."""
        run = abs(x1 - x0)
        rise = abs(y1 - y0)
        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1
        drift = run - rise
        half = thick // 2
        x, y = x0, y0
        while True:
            self.box(x - half, y - half, thick, thick, rgb)
            if x == x1 and y == y1:
                return
            twice = 2 * drift
            if twice > -rise:
                drift -= rise
                x += step_x
            if twice < run:
                drift += run
                y += step_y

    def disc(self, cx, cy, r, rgb):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.dot(xx, yy, rgb)

    def halo(self, cx, cy, r, rgb, thick=3):
        """A ring: pixels whose distance from the centre is near r."""
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = math.hypot(xx - cx, yy - cy)
                if r - thick <= d <= r:
                    self.dot(xx, yy, rgb)

    def poly(self, corners, rgb):
        """Fill a simple polygon, one scanline at a time."""
        if len(corners) < 3:
            return
        top = max(0, min(c[1] for c in corners))
        bottom = min(self.size - 1, max(c[1] for c in corners))
        count = len(corners)
        for y in range(top, bottom + 1):
            cuts = []
            for i in range(count):
                ax, ay = corners[i]
                bx, by = corners[(i + 1) % count]
                if (ay <= y < by) or (by <= y < ay):
                    cuts.append(ax + (y - ay) * (bx - ax) / (by - ay))
            cuts.sort()
            for i in range(0, len(cuts) - 1, 2):
                start = max(0, int(cuts[i]))
                stop = min(self.size - 1, int(cuts[i + 1]))
                for x in range(start, stop + 1):
                    self.dot(x, y, rgb)

    def burst(self, cx, cy, outer, inner, rgb):
        """A ten-pointed starburst (explosion, blast, sparkle)."""
        tips = []
        for i in range(10):
            radius = outer if i % 2 == 0 else inner
            angle = math.radians(-90 + i * 36)
            tips.append((int(cx + radius * math.cos(angle)),
                         int(cy + radius * math.sin(angle))))
        self.poly(tips, rgb)

    # -- text --------------------------------------------------------
    @staticmethod
    def measure(text, size):
        """Pixel width of a line at a given glyph scale."""
        if not text:
            return 0
        return len(text) * 6 * size - size

    def write(self, x, y, text, size, rgb, align="left"):
        """Paint one line; returns the x just past its last glyph."""
        text = text.upper()
        if align == "center":
            x -= self.measure(text, size) // 2
        elif align == "right":
            x -= self.measure(text, size)
        pen = x
        for ch in text:
            rows = GLYPHS.get(ch, GLYPHS["?"])
            for row in range(7):
                bits = rows[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.box(pen + col * size, y + row * size,
                                 size, size, rgb)
            pen += 6 * size
        return pen

    def flow(self, x, y, text, width, size, rgb, gap=None):
        """Wrap a paragraph greedily and paint it; returns the y just
        below the last line."""
        step = gap if gap is not None else 7 * size + 4
        words = text.upper().split(" ")
        lines = []
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if self.measure(trial, size) <= width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        for i, line_text in enumerate(lines):
            self.write(x, y + i * step, line_text, size, rgb)
        return y + len(lines) * step


# ------------------------------------------------------------------ pictures
# Each picture fills the rectangle it is given: (x, y, w, h) on the
# sheet. They are small editorial illustrations, drawn with the same
# vocabulary as the rest of the page.

def paint_us_flag(s, x, y, w, h):
    """Stars and Stripes, simplified to seven stripes and a canton."""
    s.box(x, y, w, h, PAL["card"])
    stripe = h // 7
    for i in range(0, 7, 2):
        s.box(x, y + i * stripe, w, stripe, PAL["red"])
    canton_w, canton_h = int(w * 0.42), int(h * 0.54)
    s.box(x, y, canton_w, canton_h, PAL["navy"])
    for row in range(3):
        for col in range(4):
            s.dot(x + 5 + col * 9, y + 5 + row * 7, PAL["card"])


def paint_cn_flag(s, x, y, w, h):
    """China: one big gold star and four small ones in its corner."""
    s.box(x, y, w, h, PAL["red"])
    s.burst(x + 16, y + 15, 11, 4, PAL["gold"])
    for sx, sy in ((36, 8), (44, 14), (44, 24), (36, 30)):
        s.disc(x + sx, y + sy, 2, PAL["gold"])


def paint_ru_flag(s, x, y, w, h):
    """Russia: white over blue over red, three equal bands."""
    third = h // 3
    s.box(x, y, w, third + 1, PAL["card"])
    s.box(x, y + third, w, third + 1, PAL["blue"])
    s.box(x, y + 2 * third, w, h - 2 * third, PAL["red"])


def paint_lead_art(s, x, y, w, h):
    """Shenzhen at dawn: three flags on poles above the skyline."""
    s.box(x, y, w, h, PAL["sky"])
    s.disc(x + 430, y + 30, 18, PAL["dawn"])
    ground = y + h - 34
    towers = [(0, 90), (52, 60), (104, 110), (156, 70), (208, 120),
              (260, 55), (312, 95), (364, 65), (416, 105), (468, 80)]
    for bx, bh in towers:
        s.box(x + bx, ground - bh, 48, bh + 34, PAL["navy"])
    for bx, bh in towers:
        wy = ground - bh + 8
        while wy < ground - 6:
            s.box(x + bx + 10, wy, 5, 6, PAL["gold"])
            s.box(x + bx + 28, wy, 5, 6, PAL["gold"])
            wy += 16
    s.box(x, ground, w, 34, PAL["midnight"])
    for pole_x, flag_fn in ((x + 78, paint_us_flag),
                            (x + 238, paint_cn_flag),
                            (x + 398, paint_ru_flag)):
        s.vbar(pole_x, y + 22, ground - y - 18, PAL["ink"], 4)
        s.disc(pole_x, y + 20, 5, PAL["gold"])
        flag_fn(s, pole_x + 4, y + 26, 96, 58)
    s.box(x, y + h - 24, w, 24, PAL["navy"])
    s.write(x + 10, y + h - 19, "FIRST MEETING OF ITS KIND", 2,
            PAL["card"])


def paint_kyiv(s, x, y, w, h):
    """Kyiv by night: missiles streaking down, a blast on a bridge."""
    s.box(x, y, w, h, PAL["night"])
    for sx, sy in ((14, 12), (52, 26), (96, 10), (150, 20), (196, 12),
                   (30, 44), (120, 40), (180, 46), (210, 30)):
        s.dot(x + sx, y + sy, PAL["card"])
        s.dot(x + sx + 1, y + sy, PAL["card"])
    ground = y + h - 26
    blocks = [(0, 46), (44, 66), (88, 38), (132, 58), (176, 42)]
    for bx, bh in blocks:
        s.box(x + bx, ground - bh, 40, bh + 26, PAL["midnight"])
    for bx, bh in blocks:
        wy = ground - bh + 8
        while wy < ground - 4:
            s.box(x + bx + 8, wy, 4, 5, PAL["gold"])
            s.box(x + bx + 26, wy, 4, 5, PAL["gold"])
            wy += 14
    s.hbar(x + 4, ground - 8, w - 8, PAL["ink"], 5)
    s.box(x + 30, ground - 34, 8, 28, PAL["ink"])
    s.box(x + 190, ground - 34, 8, 28, PAL["ink"])
    for hx, hy, tx, ty in ((200, 22, 150, 66), (120, 14, 84, 52),
                           (60, 30, 36, 58)):
        s.seg(x + hx, y + hy, x + tx, y + ty, PAL["yellow"], 2)
        s.disc(x + hx, y + hy, 4, PAL["card"])
    s.burst(x + 118, ground - 12, 26, 11, PAL["yellow"])
    s.burst(x + 118, ground - 12, 16, 6, PAL["orange"])
    s.disc(x + 140, ground - 44, 9, PAL["grey"])
    s.disc(x + 154, ground - 56, 7, PAL["grey"])


def paint_scales(s, x, y, w, h):
    """The scales of justice on a pale green ground."""
    s.box(x, y, w, h, PAL["mint"])
    cx = x + w // 2
    s.vbar(cx, y + 16, 92, PAL["ink"], 5)
    s.hbar(cx - 62, y + 24, 124, PAL["ink"], 5)
    s.disc(cx, y + 14, 7, PAL["gold"])
    for arm in (cx - 62, cx + 62):
        s.seg(arm, y + 26, arm - 20, y + 62, PAL["ink"], 3)
        s.seg(arm, y + 26, arm + 20, y + 62, PAL["ink"], 3)
        s.poly([(arm - 24, y + 62), (arm + 24, y + 62), (arm, y + 84)],
               PAL["gold"])
    s.box(cx - 34, y + 104, 68, 8, PAL["ink"])
    s.box(cx - 22, y + 112, 44, 6, PAL["ink"])
    s.write(x + 8, y + h - 16, "9 - 6", 2, PAL["teal"])


def paint_bars(s, x, y, w, h):
    """One green bar up for the IPO, then red bars falling away."""
    s.box(x, y, w, h, PAL["card"])
    s.box(x + 8, y + 8, w - 16, 22, PAL["cream"])
    s.write(x + 12, y + 13, "ANT +17%", 2, PAL["green"])
    heights = [(PAL["green"], 0.95), (PAL["red"], 0.62),
               (PAL["red"], 0.52), (PAL["red"], 0.40),
               (PAL["red"], 0.30)]
    bar_w = 30
    for i, (colour, frac) in enumerate(heights):
        bh = int((h - 44) * frac)
        s.box(x + 18 + i * (bar_w + 8), y + h - 12 - bh, bar_w, bh,
              colour)
    s.hbar(x + 10, y + h - 12, w - 20, PAL["ink"], 2)
    s.seg(x + 62, y + 44, x + w - 18, y + h - 26, PAL["scarlet"], 3)
    s.poly([(x + w - 18, y + h - 26), (x + w - 34, y + h - 30),
            (x + w - 22, y + h - 40)], PAL["scarlet"])


def paint_tower(s, x, y, w, h):
    """Riyadh's financial district: the PIF tower, hit at its top."""
    s.box(x, y, w, h, PAL["pale"])
    s.disc(x + 196, y + 22, 12, PAL["yellow"])
    ground = y + h
    for bx, bh, bw in ((6, 52, 34), (48, 78, 36), (168, 64, 34),
                       (206, 44, 20)):
        s.box(x + bx, ground - bh, bw, bh, PAL["navy"])
    tx = x + 96
    s.box(tx, y + 34, 64, h - 34, PAL["glass"])
    wy = y + 44
    while wy < ground - 8:
        for wx in (tx + 8, tx + 26, tx + 44):
            s.box(wx, wy, 8, 6, PAL["sky"])
        wy += 12
    s.burst(tx + 32, y + 34, 24, 10, PAL["yellow"])
    s.burst(tx + 32, y + 34, 14, 6, PAL["orange"])
    s.disc(tx + 52, y + 16, 9, PAL["grey"])
    s.disc(tx + 66, y + 8, 7, PAL["grey"])
    s.box(x, ground - 10, w, 10, PAL["midnight"])


def paint_pad(s, x, y, w, h, colour):
    """A simple game controller: body, two grips, d-pad, buttons."""
    s.box(x, y + 8, w, h - 16, colour)
    s.disc(x + 6, y + h - 8, 10, colour)
    s.disc(x + w - 6, y + h - 8, 10, colour)
    s.box(x + 14, y + 22, 8, 24, PAL["card"])
    s.box(x + 6, y + 30, 24, 8, PAL["card"])
    for bx, by in ((x + w - 26, y + 24), (x + w - 38, y + 34),
                   (x + w - 14, y + 34), (x + w - 26, y + 44)):
        s.disc(bx, by, 4, PAL["yellow"])


def paint_cross(s, x, y, r, colour):
    """A medical cross: green disc with a white plus on it."""
    s.disc(x, y, r, colour)
    s.box(x - 6, y - 18, 12, 36, PAL["card"])
    s.box(x - 18, y - 6, 36, 12, PAL["card"])


# ------------------------------------------------------------------ layout
# The page is built top to bottom: masthead, lead story, four stories
# in a row, two short items, footer. Every box below is positioned
# against the 1024 square, with a 16 px margin at the sides.

def frame(s, x, y, w, h, thick=3):
    """A white story box with a thick ink border."""
    s.box(x, y, w, h, PAL["card"])
    s.hbar(x, y, w, PAL["ink"], thick)
    s.hbar(x, y + h - thick, w, PAL["ink"], thick)
    s.vbar(x, y, h, PAL["ink"], thick)
    s.vbar(x + w - thick, y, h, PAL["ink"], thick)


def story_card(s, x, y, w, h, tag, tag_rgb, head, deck, art):
    """One of the four middle stories: coloured tag bar, picture,
    headline, then a short deck in dark grey."""
    frame(s, x, y, w, h)
    s.box(x + 3, y + 3, w - 6, 26, tag_rgb)
    s.write(x + 12, y + 10, tag, 2, PAL["card"])
    art(s, x + 3, y + 29, w - 6, 130)
    below_head = s.flow(x + 12, y + 170, head, w - 24, 3, PAL["ink"],
                        gap=25)
    s.flow(x + 12, below_head + 6, deck, w - 24, 2, PAL["dim"], gap=16)


def masthead(s):
    s.write(SIZE // 2, 22, "THE WORLD TODAY", 8, PAL["ink"],
            align="center")
    s.hbar(120, 92, SIZE - 240, PAL["red"], 4)
    s.write(SIZE // 2, 104, "FRIDAY, 20 NOVEMBER 2026", 5, PAL["red"],
            align="center")
    s.write(SIZE // 2, 146, "SEVEN STORIES THAT DEFINED THE DAY", 3,
            PAL["ink"], align="center")


def lead(s):
    x, y, w, h = 16, 186, 992, 284
    frame(s, x, y, w, h)
    s.box(x + 3, y + 3, w - 6, 30, PAL["navy"])
    s.write(x + 14, y + 11, "LEAD STORY  -  SHENZHEN, CHINA", 3,
            PAL["card"])
    paint_lead_art(s, x + 12, y + 45, 520, 224)
    tx = x + 556
    s.flow(tx, y + 48, "TRUMP, XI AND PUTIN MEET IN SHENZHEN", 420, 5,
           PAL["ink"], gap=40)
    s.flow(tx, y + 48 + 3 * 40 + 8,
           "FIRST THREE-WAY SUMMIT. PEACE DECLARATION ISSUED. "
           "NO DEAL ON UKRAINE OR IRAN.", 420, 3, PAL["dim"], gap=25)


def four_stories(s):
    y, h, w = 486, 320, 236
    story_card(s, 16, y, w, h, "UKRAINE", PAL["blue"],
               "RUSSIA HITS KYIV OVERNIGHT",
               "110+ MISSILES, 400 DRONES. 8 DEAD, 28 HURT.",
               paint_kyiv)
    story_card(s, 268, y, w, h, "JUSTICE", PAL["teal"],
               "MYANMAR GUILTY OF GENOCIDE",
               "WORLD COURT RULES FOR THE ROHINGYA. VOTE 9-6.",
               paint_scales)
    story_card(s, 520, y, w, h, "MARKETS", PAL["red"],
               "ANTHROPIC UP, MARKETS DOWN",
               "IPO CLOSES AT $97, UP 17%. NIKKEI -4.8%. SOFTBANK -16%.",
               paint_bars)
    story_card(s, 772, y, w, h, "MIDDLE EAST", PAL["brown"],
               "HOUTHI MISSILE HITS RIYADH",
               "SAUDI WEALTH FUND TOWER DAMAGED IN RIYADH.",
               paint_tower)


def bottom_strip(s):
    y, h = 822, 140
    for bx in (16, 524):
        s.box(bx, y, 484, h, PAL["cream"])
        s.hbar(bx, y, 484, PAL["ink"], 3)
        s.hbar(bx, y + h - 3, 484, PAL["ink"], 3)
        s.vbar(bx, y, h, PAL["ink"], 3)
        s.vbar(bx + 481, y, h, PAL["ink"], 3)
    s.write(30, y + 12, "GAMES", 2, PAL["red"])
    s.write(30, y + 38, "GTA 6 TOPS $2.3BN", 3, PAL["ink"])
    s.write(30, y + 63, "IN SALES", 3, PAL["ink"])
    s.flow(30, y + 96, "RECORD LAUNCH SALES.", 350, 2, PAL["dim"],
           gap=16)
    paint_pad(s, 400, y + 44, 76, 64, PAL["navy"])
    s.write(538, y + 12, "HEALTH", 2, PAL["red"])
    s.write(538, y + 38, "KENYA'S LAST EBOLA", 3, PAL["ink"])
    s.write(538, y + 63, "PATIENT GOES HOME", 3, PAL["ink"])
    s.flow(538, y + 96, "37 DAYS AFTER THE FIRST CASE.", 350, 2,
           PAL["dim"], gap=16)
    paint_cross(s, 940, y + 76, 34, PAL["green"])


def footer(s):
    s.hbar(120, 978, SIZE - 240, PAL["ink"], 3)
    s.write(SIZE // 2, 988, "20 NOVEMBER 2026 - THE WORLD IN ONE IMAGE",
            2, PAL["ink"], align="center")


def compose():
    """Paint the whole page and hand back the finished sheet."""
    s = Sheet(SIZE, PAL["paper"])
    s.hbar(0, 0, SIZE, PAL["ink"], 5)
    s.hbar(0, SIZE - 5, SIZE, PAL["ink"], 5)
    s.vbar(0, 0, SIZE, PAL["ink"], 5)
    s.vbar(SIZE - 5, 0, SIZE, PAL["ink"], 5)
    masthead(s)
    lead(s)
    four_stories(s)
    bottom_strip(s)
    footer(s)
    return s


# ------------------------------------------------------------------ PNG out
def _chunk(kind, payload):
    body = kind + payload
    return (struct.pack(">I", len(payload)) + body +
            struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))


def encode_png(s):
    """Raw scanlines (filter none) + zlib, wrapped in PNG chunks."""
    raw = bytearray()
    for row in range(s.size):
        raw.append(0)
        start = row * s.size * 3
        raw += s.buf[start:start + s.size * 3]
    header = struct.pack(">IIBBBBB", s.size, s.size, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            _chunk(b"IEND", b""))


def main():
    sheet = compose()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png(sheet))
    return 0


if __name__ == "__main__":
    sys.exit(main())
