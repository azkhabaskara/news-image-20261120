#!/usr/bin/env python3
"""news-image-20261120: sum up the world's news of Friday 20 November 2026
in one image.

Pure Python 3.13 standard library only (math, os, struct, sys, zlib): no
network, no files read, no randomness, no clock. The program draws a
newspaper front page -- masthead with the date, one lead story, four
further stories and two short items -- pixel by pixel with an embedded
5x7 bitmap font, encodes it as a PNG, and writes /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png). Two runs write byte-identical output.

Stories (20 November 2026):
  Lead: Trump, Xi and Putin meet in Shenzhen -- first three-way summit;
        joint peace declaration, no deal on Ukraine or Iran.
  Ukraine: Russia's big overnight attack -- 110+ missiles, ~400 drones;
        8 dead, 28 hurt in Kyiv; Poland scrambles jets.
  Justice: ICJ finds Myanmar guilty of genocide against the Rohingya --
        first such ruling against a state; vote 9-6.
  Markets: Anthropic IPO closes at $97, up 17% on its $83 offer price;
        S&P and Nasdaq fall ~2%; Nikkei -4.8%; SoftBank -16%.
  Middle East: Houthi missile damages the Saudi PIF tower in Riyadh.
  Also: GTA 6 tops $2.3bn in sales, a launch record.
  Also: Kenya sends its last Ebola patient home, 37 days after the
        first case.
"""

import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 230)
WHITE = (255, 253, 246)
INK = (26, 26, 26)
GREY = (120, 120, 118)
DIMGREY = (64, 64, 64)
RED = (179, 38, 30)
BRIGHTRED = (214, 48, 24)
NAVY = (31, 78, 121)
DARKNAVY = (24, 40, 56)
BLUE = (47, 117, 181)
SKY = (214, 232, 240)
NIGHT = (18, 32, 58)
SAND = (232, 210, 160)
SEA = (58, 122, 158)
TEAL = (38, 110, 100)
GREEN = (46, 125, 58)
DARKGREEN = (46, 92, 58)
GOLD = (201, 162, 39)
YELLOW = (240, 200, 60)
ORANGE = (224, 122, 33)
PALE = (255, 248, 220)
PALEGREEN = (220, 235, 230)
BROWN = (146, 90, 32)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 pixels, '1' = ink. Uppercase + digits + punctuation.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def rect(x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def hline(x, y, w, color, t=1):
    rect(x, y, w, t, color)


def vline(x, y, h, color, t=1):
    rect(x, y, t, h, color)


def line(x0, y0, x1, y1, color, t=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        rect(x - t // 2, y - t // 2, t, t, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def circle(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(xx, yy, color)


def ring(cx, cy, r, color, t=3):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = math.hypot(xx - cx, yy - cy)
            if r - t <= d <= r:
                set_px(xx, yy, color)


def polygon(points, color):
    """Scanline fill of a simple polygon given as [(x, y), ...]."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(max(0, int(xs[i])), min(W, int(xs[i + 1]) + 1)):
                set_px(x, y, color)


def star(cx, cy, r_out, r_in, color, rot=-90):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    polygon(pts, color)


# ---------------------------------------------------------------- text
def text_w(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(x, y, s, scale, color, align="left"):
    s = s.upper()
    if align == "center":
        x -= text_w(s, scale) // 2
    elif align == "right":
        x -= text_w(s, scale)
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT['?'])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def wrap(text, width, scale):
    """Greedy word wrap; returns a list of lines fitting `width` px."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, text, width, scale, color, leading=None):
    lh = (leading if leading is not None else 7 * scale + 4)
    lines = wrap(text, width, scale)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, scale, color)
    return y + len(lines) * lh


# ---------------------------------------------------------------- pictures
def draw_flag_us(x, y, w, h):
    """Simplified Stars and Stripes."""
    rect(x, y, w, h, WHITE)
    for i in range(7):
        rect(x, y + i * (h // 7), w, h // 14 + 1, RED)
    cw, ch = int(w * 0.42), int(h * 0.54)
    rect(x, y, cw, ch, NAVY)
    for r in range(3):
        for c in range(4):
            set_px(x + 5 + c * 9, y + 5 + r * 7, WHITE)


def draw_flag_cn(x, y, w, h):
    rect(x, y, w, h, RED)
    star(x + 16, y + 15, 11, 4, GOLD)
    for sx, sy in ((36, 8), (44, 14), (44, 24), (36, 30)):
        circle(x + sx, y + sy, 2, GOLD)


def draw_flag_ru(x, y, w, h):
    rect(x, y, w, h // 3 + 1, WHITE)
    rect(x, y + h // 3, w, h // 3 + 1, BLUE)
    rect(x, y + 2 * h // 3, w, h - 2 * h // 3, RED)


def draw_lead_picture(x, y, w, h):
    """Three flags over the Shenzhen skyline at dawn."""
    rect(x, y, w, h, SKY)
    circle(x + 430, y + 30, 18, (224, 84, 48))  # rising sun
    base = y + h - 34
    skyline = [(0, 90), (52, 60), (104, 110), (156, 70), (208, 120),
               (260, 55), (312, 95), (364, 65), (416, 105), (468, 80)]
    for bx, bh in skyline:
        rect(x + bx, base - bh, 48, bh + 34, NAVY)
    for bx, bh in skyline:  # lit windows
        for wy in range(base - bh + 8, base - 6, 16):
            for wx in (x + bx + 10, x + bx + 28):
                rect(wx, wy, 5, 6, GOLD)
    rect(x, base, w, 34, DARKNAVY)  # ground
    poles = [(x + 78, draw_flag_us), (x + 238, draw_flag_cn),
             (x + 398, draw_flag_ru)]
    for px0, fn in poles:
        vline(px0, y + 22, base - y - 18, INK, 4)
        circle(px0, y + 20, 5, GOLD)
        fn(px0 + 4, y + 26, 96, 58)
    rect(x, y + h - 24, w, 24, NAVY)  # caption strip
    draw_text(x + 10, y + h - 19, "FIRST MEETING OF ITS KIND", 2, WHITE)


def draw_kyiv_picture(x, y, w, h):
    """Night over Kyiv: missile trails, drones, a blast on a bridge."""
    rect(x, y, w, h, NIGHT)
    for sx, sy in ((14, 12), (52, 26), (96, 10), (150, 20), (196, 12),
                   (30, 44), (120, 40), (180, 46), (210, 30)):
        set_px(x + sx, y + sy, WHITE)
        set_px(x + sx + 1, y + sy, WHITE)
    base = y + h - 26
    for bx, bh in ((0, 46), (44, 66), (88, 38), (132, 58), (176, 42)):
        rect(x + bx, base - bh, 40, bh + 26, DARKNAVY)
    for bx, bh in ((0, 46), (44, 66), (88, 38), (132, 58), (176, 42)):
        for wy in range(base - bh + 8, base - 4, 14):
            rect(x + bx + 8, wy, 4, 5, GOLD)
            rect(x + bx + 26, wy, 4, 5, GOLD)
    # bridge deck across the lower third
    hline(x + 4, base - 8, w - 8, INK, 5)
    rect(x + 30, base - 34, 8, 28, INK)
    rect(x + 190, base - 34, 8, 28, INK)
    # missile trails: bright heads streaking down from the sky
    for hx, hy, tx, ty in ((200, 22, 150, 66), (120, 14, 84, 52),
                           (60, 30, 36, 58)):
        line(hx + x, hy + y, tx + x, ty + y, YELLOW, 2)
        circle(hx + x, hy + y, 4, WHITE)
    # blast on the bridge
    star(x + 118, base - 12, 26, 11, YELLOW)
    star(x + 118, base - 12, 16, 6, ORANGE)
    circle(x + 140, base - 44, 9, GREY)
    circle(x + 154, base - 56, 7, GREY)


def draw_justice_picture(x, y, w, h):
    """Scales of justice on a pale green ground."""
    rect(x, y, w, h, PALEGREEN)
    cx = x + w // 2
    vline(cx, y + 16, 92, INK, 5)
    hline(cx - 62, y + 24, 124, INK, 5)
    circle(cx, y + 14, 7, GOLD)
    for sx in (cx - 62, cx + 62):
        line(sx, y + 26, sx - 20, y + 62, INK, 3)
        line(sx, y + 26, sx + 20, y + 62, INK, 3)
        polygon([(sx - 24, y + 62), (sx + 24, y + 62), (sx, y + 84)], GOLD)
    rect(cx - 34, y + 104, 68, 8, INK)
    rect(cx - 22, y + 112, 44, 6, INK)
    draw_text(x + 8, y + h - 16, "9 - 6", 2, TEAL)


def draw_markets_picture(x, y, w, h):
    """One green bar up, then red bars falling: IPO up, markets down."""
    rect(x, y, w, h, WHITE)
    rect(x + 8, y + 8, w - 16, 22, PALE)
    draw_text(x + 12, y + 13, "ANT +17%", 2, GREEN)
    bars = [(GREEN, 0.95), (RED, 0.62), (RED, 0.52), (RED, 0.40),
            (RED, 0.30)]
    bw = 30
    for i, (color, f) in enumerate(bars):
        bh = int((h - 44) * f)
        rect(x + 18 + i * (bw + 8), y + h - 12 - bh, bw, bh, color)
    line(x + 10, y + h - 12, x + w - 10, y + h - 12, INK, 2)
    # falling arrow over the red bars
    line(x + 62, y + 44, x + w - 18, y + h - 26, BRIGHTRED, 3)
    polygon([(x + w - 18, y + h - 26), (x + w - 34, y + h - 30),
             (x + w - 22, y + h - 40)], BRIGHTRED)


def draw_tower_picture(x, y, w, h):
    """A glass tower in Riyadh's financial district, hit at the top."""
    rect(x, y, w, h, (250, 222, 182))
    circle(x + 196, y + 22, 12, YELLOW)  # desert sun
    base = y + h
    for bx, bh, bw in ((6, 52, 34), (48, 78, 36), (168, 64, 34),
                       (206, 44, 20)):
        rect(x + bx, base - bh, bw, bh, NAVY)
    # the PIF tower: tall, glassy, centre
    tx = x + 96
    rect(tx, y + 34, 64, h - 34, (38, 68, 96))
    for wy in range(y + 44, base - 8, 12):
        for wx in (tx + 8, tx + 26, tx + 44):
            rect(wx, wy, 8, 6, SKY)
    # blast and smoke at the tower top
    star(tx + 32, y + 34, 24, 10, YELLOW)
    star(tx + 32, y + 34, 14, 6, ORANGE)
    circle(tx + 52, y + 16, 9, GREY)
    circle(tx + 66, y + 8, 7, GREY)
    rect(x, base - 10, w, 10, DARKNAVY)


def draw_gamepad(x, y, w, h, color):
    """Simple game controller."""
    rect(x, y + 8, w, h - 16, color)
    circle(x + 6, y + h - 8, 10, color)
    circle(x + w - 6, y + h - 8, 10, color)
    # d-pad
    rect(x + 14, y + 22, 8, 24, WHITE)
    rect(x + 6, y + 30, 24, 8, WHITE)
    # buttons
    for bx, by in ((x + w - 26, y + 24), (x + w - 38, y + 34),
                   (x + w - 14, y + 34), (x + w - 26, y + 44)):
        circle(bx, by, 4, YELLOW)


def draw_med_cross(x, y, r, color):
    circle(x, y, r, color)
    rect(x - 6, y - 18, 12, 36, WHITE)
    rect(x - 18, y - 6, 36, 12, WHITE)


# ---------------------------------------------------------------- layout
def panel(x, y, w, h, kicker, kcolor, headline, sub, picture):
    rect(x, y, w, h, WHITE)
    hline(x, y, w, INK, 3)
    hline(x, y + h - 3, w, INK, 3)
    vline(x, y, h, INK, 3)
    vline(x + w - 3, y, h, INK, 3)
    rect(x + 3, y + 3, w - 6, 26, kcolor)
    draw_text(x + 12, y + 10, kicker, 2, WHITE)
    picture(x + 3, y + 29, w - 6, 130)
    end = draw_para(x + 12, y + 170, headline, w - 24, 3, INK, leading=25)
    draw_para(x + 12, end + 6, sub, w - 24, 2, DIMGREY, leading=16)


def build():
    rect(0, 0, W, H, PAPER)
    hline(0, 0, W, INK, 5)
    hline(0, H - 5, W, INK, 5)
    vline(0, 0, H, INK, 5)
    vline(W - 5, 0, H, INK, 5)

    # ---- masthead
    draw_text(W // 2, 22, "THE WORLD TODAY", 8, INK, align="center")
    hline(120, 92, W - 240, RED, 4)
    draw_text(W // 2, 104, "FRIDAY, 20 NOVEMBER 2026", 5, RED,
              align="center")
    draw_text(W // 2, 146, "SEVEN STORIES THAT DEFINED THE DAY", 3, INK,
              align="center")

    # ---- lead story
    lx, ly, lw, lh = 16, 186, 992, 284
    rect(lx, ly, lw, lh, WHITE)
    hline(lx, ly, lw, INK, 3)
    hline(lx, ly + lh - 3, lw, INK, 3)
    vline(lx, ly, lh, INK, 3)
    vline(lx + lw - 3, ly, lh, INK, 3)
    rect(lx + 3, ly + 3, lw - 6, 30, NAVY)
    draw_text(lx + 14, ly + 11, "LEAD STORY  -  SHENZHEN, CHINA", 3, WHITE)
    draw_lead_picture(lx + 12, ly + 45, 520, 224)
    tx = lx + 556
    draw_para(tx, ly + 48, "TRUMP, XI AND PUTIN MEET IN SHENZHEN", 420, 5,
              INK, leading=40)
    draw_para(tx, ly + 48 + 3 * 40 + 8,
              "FIRST THREE-WAY SUMMIT. PEACE DECLARATION ISSUED. "
              "NO DEAL ON UKRAINE OR IRAN.", 420, 3,
              DIMGREY, leading=25)

    # ---- four stories
    py, ph, pw = 486, 320, 236
    panel(16, py, pw, ph, "UKRAINE", BLUE,
          "RUSSIA HITS KYIV OVERNIGHT",
          "110+ MISSILES, 400 DRONES. 8 DEAD, 28 HURT.",
          draw_kyiv_picture)
    panel(268, py, pw, ph, "JUSTICE", TEAL,
          "MYANMAR GUILTY OF GENOCIDE",
          "WORLD COURT RULES FOR THE ROHINGYA. VOTE 9-6.",
          draw_justice_picture)
    panel(520, py, pw, ph, "MARKETS", RED,
          "ANTHROPIC UP, MARKETS DOWN",
          "IPO CLOSES AT $97, UP 17%. NIKKEI -4.8%. SOFTBANK -16%.",
          draw_markets_picture)
    panel(772, py, pw, ph, "MIDDLE EAST", BROWN,
          "HOUTHI MISSILE HITS RIYADH",
          "SAUDI WEALTH FUND TOWER DAMAGED IN RIYADH.",
          draw_tower_picture)

    # ---- bottom strip: two short items
    by, bh = 822, 140
    for bx in (16, 524):
        rect(bx, by, 484, bh, PALE)
        hline(bx, by, 484, INK, 3)
        hline(bx, by + bh - 3, 484, INK, 3)
        vline(bx, by, bh, INK, 3)
        vline(bx + 481, by, bh, INK, 3)
    draw_text(30, by + 12, "GAMES", 2, RED)
    draw_text(30, by + 38, "GTA 6 TOPS $2.3BN", 3, INK)
    draw_text(30, by + 63, "IN SALES", 3, INK)
    draw_para(30, by + 96, "RECORD LAUNCH SALES.", 350, 2,
              DIMGREY, leading=16)
    draw_gamepad(400, by + 44, 76, 64, NAVY)
    draw_text(538, by + 12, "HEALTH", 2, RED)
    draw_text(538, by + 38, "KENYA'S LAST EBOLA", 3, INK)
    draw_text(538, by + 63, "PATIENT GOES HOME", 3, INK)
    draw_para(538, by + 96, "37 DAYS AFTER THE FIRST CASE.", 350, 2,
              DIMGREY, leading=16)
    draw_med_cross(940, by + 76, 34, GREEN)

    # ---- footer
    hline(120, 978, W - 240, INK, 3)
    draw_text(W // 2, 988, "20 NOVEMBER 2026 - THE WORLD IN ONE IMAGE", 2,
              INK, align="center")


# ---------------------------------------------------------------- PNG out
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += px[y * W * 3:(y + 1) * W * 3]

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    return 0


if __name__ == "__main__":
    sys.exit(main())
