#!/usr/bin/env python3
"""news-image-20261121: draw a one-page newspaper front page summing up the
world news of Saturday 21 November 2026 and write it to /output/entry.png.

Pure Python 3 standard library only: no network, no fonts, no image
libraries. The whole poster is drawn from code (5x7 bitmap font, flat
vector shapes and small pictogram icons), so two runs produce
byte-identical output.

Run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---- palette (newsprint) -------------------------------------------------
PAPER = (247, 242, 228)
CARD = (255, 253, 247)
INK = (24, 24, 24)
RED = (168, 28, 32)
BLUE = (30, 76, 120)
TEAL = (13, 106, 106)
OCHRE = (190, 120, 24)
GREEN = (44, 106, 52)
SKY = (188, 216, 233)
SEA = (44, 106, 138)
SAND = (200, 160, 38)
LIGHT = (233, 225, 201)
GREY = (118, 118, 112)
WHITE = (255, 255, 255)
DARKBG = (30, 42, 52)
ORANGE = (212, 88, 18)
GOLD = (212, 164, 32)

# ---- 5x7 bitmap font ------------------------------------------------------
# Each glyph: 7 rows of 5 pixels, '1' = ink. Lowercase shares the grid.
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
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01110", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01001", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
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
    ';': ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    ':': ("00000", "01100", "00000", "00000", "01100", "00000", "00000"),
    '\u2022': ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '\u2019': ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '\u201c': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '\u201d': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


def adv(scale):
    """Horizontal advance of one glyph cell at the given scale."""
    return 5 * scale + max(1, scale // 3)


def twidth(s, scale):
    """Pixel width of string s rendered at scale."""
    if not s:
        return 0
    return len(s) * adv(scale) - max(1, scale // 3)


def wrap(s, maxw, scale):
    """Greedy word wrap; returns a list of lines fitting maxw pixels."""
    lines = []
    for para in s.split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if twidth(trial, scale) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# ---- canvas ----------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = c[0]
                self.buf[i + 1] = c[1]
                self.buf[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick(self, x0, y0, x1, y1, c, t=2):
        for k in range(-(t // 2), t // 2 + 1):
            self.line(x0, y0 + k, x1, y1 + k, c)

    def circle(self, cx, cy, r, c, fill=False):
        x = 0
        y = r
        d = 1 - r
        pts = set()
        while x <= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                pts.add((cx + sx, cy + sy))
            if fill:
                for xx in range(cx - x, cx + x + 1):
                    pts.add((xx, cy + y))
                    pts.add((xx, cy - y))
                for xx in range(cx - y, cx + y + 1):
                    pts.add((xx, cy + x))
                    pts.add((xx, cy - x))
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
        for px_, py_ in pts:
            self.px(px_, py_, c)

    def disc(self, cx, cy, r, c):
        self.circle(cx, cy, r, c, fill=True)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        # filled triangle via scanline interpolation
        ys = sorted(((y0, x0), (y1, x1), (y2, x2)))
        (ya, xa), (yb, xb), (yc, xc) = ys
        if yc == ya:
            return
        for y in range(ya, yc + 1):
            if y < yb:
                t1 = (y - ya) / (yb - ya) if yb != ya else 0.0
                xa_y = xa + (xb - xa) * t1
            else:
                t1 = (y - yb) / (yc - yb) if yc != yb else 0.0
                xa_y = xb + (xc - xb) * t1
            t2 = (y - ya) / (yc - ya)
            xb_y = xa + (xc - xa) * t2
            lo = int(min(xa_y, xb_y))
            hi = int(max(xa_y, xb_y))
            for xx in range(lo, hi + 1):
                self.px(xx, y, c)

    def glyph(self, ch, x, y, scale, c):
        g = FONT.get(ch, FONT['?'])
        for r, row in enumerate(g):
            for col, bit in enumerate(row):
                if bit == '1':
                    self.rect(x + col * scale, y + r * scale,
                              scale, scale, c)

    def text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            self.glyph(ch, cx, y, scale, c)
            cx += adv(scale)
        return cx

    def text_c(self, s, cx, y, scale, c):
        self.text(s, cx - twidth(s, scale) // 2, y, scale, c)

    def para(self, s, x, y, maxw, scale, c, lh=None):
        if lh is None:
            lh = 7 * scale + max(2, scale)
        for line in wrap(s, maxw, scale):
            self.text(line, x, y, scale, c)
            y += lh
        return y


# ---- PNG writer ------------------------------------------------------------
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---- pictogram icons (simple flat shapes) ----------------------------------
def icon_missile(cv, x, y, s):
    # a missile streaking down-right with a burst behind it
    cv.circle(x + 18, y + 14, 13, ORANGE)
    cv.circle(x + 18, y + 14, 8, GOLD)
    cv.disc(x + 18, y + 14, 3, WHITE)
    cv.thick(x + 30, y + 26, x + 62, y + 58, GREY, 7)
    cv.tri(x + 62, y + 58, x + 78, y + 52, x + 72, y + 72, INK)
    cv.thick(x + 44, y + 52, x + 34, y + 62, RED, 4)
    cv.thick(x + 52, y + 44, x + 62, y + 34, RED, 4)
    cv.disc(x + 84, y + 18, 3, RED)
    cv.disc(x + 70, y + 8, 2, RED)


def icon_skyline(cv, x, y, s):
    # Riyadh towers under an interception arc
    cv.rect(x + 6, y + 42, 16, 38, SEA)
    cv.rect(x + 28, y + 26, 18, 54, BLUE)
    cv.rect(x + 52, y + 48, 14, 32, SEA)
    cv.rect(x + 70, y + 36, 12, 44, BLUE)
    cv.tri(x + 28, y + 26, x + 46, y + 26, x + 37, y + 12, GOLD)
    cv.thick(x + 4, y + 80, x + 84, y + 80, INK, 3)
    cv.thick(x + 10, y + 14, x + 44, y + 4, RED, 3)
    cv.thick(x + 44, y + 4, x + 78, y + 14, RED, 3)
    cv.disc(x + 44, y + 4, 4, RED)


def icon_chart(cv, x, y, s):
    # falling market line with a down arrow
    cv.vline(x + 8, y + 8, 68, GREY, 2)
    cv.hline(x + 8, y + 76, 76, GREY, 2)
    pts = [(12, 18), (28, 30), (40, 26), (54, 48), (66, 44), (80, 70)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.thick(x + ax, y + ay, x + bx, y + by, RED, 4)
    cv.tri(x + 80, y + 70, x + 70, y + 62, x + 88, y + 62, RED)
    cv.disc(x + 12, y + 18, 3, INK)
    cv.disc(x + 40, y + 26, 3, INK)
    cv.disc(x + 66, y + 44, 3, INK)


def icon_flags(cv, x, y, s):
    # EU flag and UK flag side by side
    cv.rect(x + 4, y + 16, 36, 48, BLUE)
    for k in range(8):
        import math
        a = math.pi * 2 * k / 8
        cv.disc(x + 22 + int(11 * math.cos(a)),
                y + 40 + int(11 * math.sin(a)), 2, GOLD)
    cv.rect(x + 48, y + 16, 36, 48, WHITE)
    cv.rect(x + 48, y + 16, 36, 48, BLUE)  # border base
    cv.rect(x + 50, y + 18, 32, 44, WHITE)
    cv.rect(x + 63, y + 18, 6, 44, RED)
    cv.rect(x + 50, y + 37, 32, 6, RED)
    cv.rect(x + 4, y + 16, 36, 48, INK)  # outline pass (thin)
    cv.rect(x + 6, y + 18, 32, 44, BLUE)
    for k in range(8):
        import math
        a = math.pi * 2 * k / 8
        cv.disc(x + 22 + int(11 * math.cos(a)),
                y + 40 + int(11 * math.sin(a)), 2, GOLD)


def icon_globe(cv, x, y, s):
    # globe with a leaf: climate talks
    cv.circle(x + 42, y + 42, 34, TEAL)
    cv.circle(x + 42, y + 42, 28, SKY)
    cv.vline(x + 42, y + 14, 56, TEAL, 2)
    cv.hline(x + 14, y + 42, 56, TEAL, 2)
    cv.thick(x + 20, y + 22, x + 64, y + 62, TEAL, 2)
    cv.thick(x + 64, y + 22, x + 20, y + 62, TEAL, 2)
    cv.tri(x + 66, y + 66, x + 86, y + 58, x + 78, y + 80, GREEN)
    cv.thick(x + 66, y + 66, x + 82, y + 82, GREEN, 3)


def icon_scales(cv, x, y, s):
    # scales of justice
    cv.vline(x + 42, y + 8, 58, INK, 4)
    cv.hline(x + 12, y + 16, 60, INK, 4)
    cv.hline(x + 30, y + 66, 24, INK, 4)
    cv.thick(x + 14, y + 16, x + 6, y + 44, INK, 2)
    cv.thick(x + 14, y + 16, x + 22, y + 44, INK, 2)
    cv.thick(x + 70, y + 16, x + 62, y + 44, INK, 2)
    cv.thick(x + 70, y + 16, x + 78, y + 44, INK, 2)
    cv.tri(x + 2, y + 44, x + 26, y + 44, x + 14, y + 56, GOLD)
    cv.tri(x + 58, y + 44, x + 82, y + 44, x + 70, y + 56, GOLD)
    cv.disc(x + 42, y + 8, 4, RED)


# ---- stories: verified from AP / Reuters / WSJ / Al Jazeera / NPR ---------
# Early edition: only stories reported by ~09:00 WIB, Saturday 21 Nov 2026.
LEAD = {
    "kicker": "LEAD STORY  •  EUROPE",
    "color": RED,
    "headline": "RUSSIAN MISSILES LAND IN POLAND",
    "body": ("Two missiles and a suspected drone came down in Poland on "
             "Friday during a huge Russian attack on Ukraine. PM Tusk calls "
             "it an intentional provocation; NATO chief Rutte calls it a "
             "grave violation. Eight people were killed in Ukraine."),
    "icon": icon_missile,
}

GRID = [
    {
        "kicker": "MIDDLE EAST",
        "color": TEAL,
        "headline": "HOUTHI MISSILES AT RIYADH STOPPED",
        "body": ("Saudi defences shot down three ballistic missiles fired "
                 "at Riyadh early on Saturday, the second attack on the "
                 "capital in days after its tallest tower was hit on "
                 "Thursday."),
        "icon": icon_skyline,
    },
    {
        "kicker": "MARKETS",
        "color": RED,
        "headline": "WALL ST SINKS INTO CORRECTION",
        "body": ("The S&P 500 fell 3.7% on Friday and the Nasdaq 5.3%, "
                 "wiping out the year's gains as AI shares crashed. "
                 "Nvidia plunged 14%; Anthropic slid 9% a day after its "
                 "record IPO."),
        "icon": icon_chart,
    },
    {
        "kicker": "EUROPE",
        "color": BLUE,
        "headline": "UK AND EU SEAL POST-BREXIT RESET",
        "body": ("Britain and the EU agreed deals on food trade, youth "
                 "mobility for 100,000 young people a year and linking "
                 "carbon markets. PM Burnham called it a win-win worth "
                 "billions."),
        "icon": icon_flags,
    },
    {
        "kicker": "CLIMATE",
        "color": GREEN,
        "headline": "COP31 TALKS RUN INTO OVERTIME",
        "body": ("Climate talks in Antalya missed their Friday deadline "
                 "with no deal. The latest draft drops any mention of "
                 "fossil fuels and a $120bn adaptation target; a new text "
                 "is due on Saturday."),
        "icon": icon_globe,
    },
]

STRIP = {
    "kicker": "JUSTICE",
    "color": OCHRE,
    "headline": "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
    "body": ("The International Court of Justice ruled Myanmar's forces "
             "committed state-sponsored genocide against the Rohingya - the "
             "first time the court has held a state responsible. Myanmar "
             "called the ruling unfair."),
    "icon": icon_scales,
}


# ---- layout ----------------------------------------------------------------
MX = 26          # outer margin
CW = W - 2 * MX  # content width


def draw_masthead(cv):
    y = 30
    cv.hline(MX, y, CW, RED, 4)
    cv.text_c("THE WORLD TODAY", W // 2, y + 14, 11, INK)
    cv.text_c("SATURDAY 21 NOVEMBER 2026", W // 2, y + 92, 3, RED)
    cv.text_c("EARLY EDITION  •  SIX STORIES  •  REPORTED BY 09:00 WIB",
              W // 2, y + 118, 2, GREY)
    cv.hline(MX, y + 140, CW, INK, 3)
    cv.hline(MX, y + 146, CW, INK, 1)
    return y + 156


def draw_lead(cv, y):
    h = 226
    cv.rect(MX, y, CW, h, CARD)
    cv.rect(MX, y, CW, h, INK)  # outline via thin border trick
    cv.rect(MX + 2, y + 2, CW - 4, h - 4, CARD)
    tx = MX + 22
    tw = 660
    cy = y + 16
    cv.text(LEAD["kicker"], tx, cy, 2, LEAD["color"])
    cy += 26
    cy = cv.para(LEAD["headline"], tx, cy, tw, 4, INK, lh=34)
    cy += 8
    cv.para(LEAD["body"], tx, cy, tw, 2, INK, lh=19)
    cv.hline(tx, y + h - 34, tw, LIGHT, 2)
    cv.text("No one hurt in Poland; jets scrambled, Patriots ready.",
            tx, y + h - 26, 2, GREY)
    LEAD["icon"](cv, MX + CW - 268, y + 58, 1)
    return y + h + 12


def draw_cell(cv, x, y, w, h, st):
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, h, INK)
    cv.rect(x + 2, y + 2, w - 4, h - 4, CARD)
    cv.rect(x + 2, y + 2, w - 4, 5, st["color"])
    ix = x + w - 104
    iy = y + 14
    st["icon"](cv, ix, iy, 1)
    tx = x + 16
    tw = w - 132
    cy = y + 18
    cv.text(st["kicker"], tx, cy, 2, st["color"])
    cy += 26
    cy = cv.para(st["headline"], tx, cy, tw, 3, INK, lh=26)
    cy += 6
    cv.para(st["body"], tx, cy, tw, 2, INK, lh=19)


def draw_grid(cv, y):
    gap = 12
    cw = (CW - gap) // 2
    ch = 224
    for i, st in enumerate(GRID):
        gx = MX + (i % 2) * (cw + gap)
        gy = y + (i // 2) * (ch + gap)
        draw_cell(cv, gx, gy, cw, ch, st)
    return y + 2 * ch + gap + 12


def draw_strip(cv, y):
    h = 96
    cv.rect(MX, y, CW, h, DARKBG)
    tx = MX + 18
    cv.text(STRIP["kicker"], tx, y + 14, 2, GOLD)
    cv.text(STRIP["headline"], tx + 118, y + 12, 3, WHITE)
    cv.para(STRIP["body"], tx, y + 40, CW - 36, 2, (226, 226, 220), lh=18)
    return y + h + 10


def draw_footer(cv, y):
    cv.text_c("Sources: AP, Reuters, WSJ, Al Jazeera, NPR  •  "
              "Early edition, 09:00 WIB, 21 Nov 2026",
              W // 2, y, 2, GREY)


def main():
    cv = Canvas(W, H, PAPER)
    y = draw_masthead(cv)
    y = draw_lead(cv, y)
    y = draw_grid(cv, y)
    y = draw_strip(cv, y)
    draw_footer(cv, y + 2)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    write_png(cv, os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
