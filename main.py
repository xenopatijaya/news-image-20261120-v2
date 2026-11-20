#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Friday 20 November 2026.

Draws a single-image front page (1024x1024 PNG) summing up the world's
news of Friday 20 November 2026, and writes it as entry.png inside the
make.fun output directory (MAKEFUN_OUTPUT_DIR, default /output).

Python standard library + Pillow only. No network, no randomness, no
clock: two runs produce a byte-identical entry.png. The output
directory itself is never deleted; only entry.png inside it is
written.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

W, H = 1024, 1024
M = 24                      # page margin
CW = W - 2 * M              # content width = 976

PAPER = (247, 241, 227)
CARD = (253, 250, 242)
INK = (26, 23, 20)
GRAY = (102, 95, 86)
LINE = (70, 62, 52)
RED = (179, 0, 27)
DARKRED = (128, 0, 20)
NAVY = (15, 25, 48)
TEAL = (10, 74, 84)
GOLD = (176, 124, 32)
GREEN = (46, 110, 52)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF = FD + "/DejaVuSerif.ttf"
SERIFB = FD + "/DejaVuSerif-Bold.ttf"
SANS = FD + "/DejaVuSans.ttf"
SANSB = FD + "/DejaVuSans-Bold.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


# ---------------------------------------------------------------- data

STATS = [
    ("300,000+", "EVACUATED BEFORE AKVAN"),
    ("~30", "MISSILES AT KYIV IN ONE NIGHT"),
    ("-4.9%", "NIKKEI 225 FALL IN TOKYO"),
    ("2.2%", "JAPAN CORE CPI, YEAR ON YEAR"),
    ("118", "PHILLIPS CENTURY, NZ v INDIA"),
    ("8 yrs", "BEPICOLOMBO VOYAGE TO MERCURY"),
]

CHIPS = [
    "ASIA-PACIFIC 11", "EUROPE 5", "MIDDLE EAST 2", "AFRICA 3",
    "AMERICAS 7", "OCEANIA 2", "WORLD & SPACE 6",
]

KICKER = ("AKVAN MAKES LANDFALL - 300,000+ EVACUATED   ///   "
          "KYIV UNDER FIRE - ~30 MISSILES   ///   "
          "ASIA STOCKS ROUT - NIKKEI -4.9%")

LEADS = [
    {
        "tag": "1 - GOPALPUR, INDIA - BAY OF BENGAL",
        "head": "Cyclone Akvan slams ashore",
        "body": ("Landfall near Gopalpur with gusts to 110 km/h. More "
                 "than 300,000 people were evacuated ahead of the storm."),
        "src": "Source: Reuters, IMD",
        "art": "akvan",
        "chip": "LANDFALL - GUSTS 110 KM/H",
    },
    {
        "tag": "2 - KYIV, UKRAINE",
        "head": "Kyiv under heaviest fire in weeks",
        "body": ("About 30 missiles in a single night; three people "
                 "killed as strikes hit homes and power sites."),
        "src": "Sources: Reuters, AP",
        "art": "kyiv",
        "chip": "~30 MISSILES - 3 KILLED",
    },
    {
        "tag": "3 - TOKYO - ASIA MARKETS",
        "head": "AI sell-off sweeps Asia",
        "body": ("Nikkei -4.9%, Kospi -5.4% and Taiex -6.8% as chip "
                 "shares lead a global technology rout."),
        "src": "Source: Reuters",
        "art": "chart",
        "chip": "",
    },
]

FEATURES = [
    {"n": 4, "tag": "SPACE - DEEP SPACE", "icon": "mercury",
     "head": "BepiColombo reaches Mercury",
     "body": "ESA-JAXA probe ends an 8-year cruise; orbit capture is set for Saturday.",
     "src": "ESA"},
    {"n": 5, "tag": "TOKYO, JAPAN", "icon": "yen",
     "head": "Japan core CPI holds at 2.2%",
     "body": "Core prices rose 2.2% in a year, matching forecasts; the BOJ watches on.",
     "src": "Reuters"},
    {"n": 6, "tag": "BEIJING, CHINA", "icon": "bank",
     "head": "China holds LPR steady",
     "body": "One-year LPR kept at 3.0% and five-year at 3.5% as policy stays put.",
     "src": "Reuters"},
    {"n": 7, "tag": "COP31 - FINAL DAY", "icon": "globe",
     "head": "Climate talks deadlocked",
     "body": "Fossil-fuel wording stalls the draft deal as the summit overruns.",
     "src": "Reuters"},
    {"n": 8, "tag": "DAKAR, SENEGAL", "icon": "boat",
     "head": "Migrant boat sinks: 4 dead",
     "body": "A pirogue capsized off the coast; rescuers search for survivors.",
     "src": "AFP"},
    {"n": 9, "tag": "ROME, ITALY", "icon": "placard",
     "head": "General strike grips Italy",
     "body": "CGIL walkout halts trains and flights in protest at the budget.",
     "src": "ANSA"},
    {"n": 10, "tag": "NEW ZEALAND", "icon": "cricket",
     "head": "Phillips smashes 118",
     "body": "Glenn Phillips' century puts New Zealand on top against India.",
     "src": "AP"},
    {"n": 11, "tag": "SAN SALVADOR", "icon": "ballot",
     "head": "Bukele files for third term",
     "body": "El Salvador's president registers to run again; assembly debates.",
     "src": "Reuters"},
    {"n": 12, "tag": "STRAIT OF HORMUZ", "icon": "tanker",
     "head": "Hormuz shut, Brent $92.50",
     "body": "Tanker traffic halted and insurers pull cover as oil jumps.",
     "src": "Bloomberg"},
    {"n": 13, "tag": "BOSTON - HEALTH", "icon": "pill",
     "head": "Cancer pill cuts tumours 60.7% [CLAIM]",
     "body": "Early trial reports pancreatic tumours shrinking by 60.7%; wider tests to come.",
     "src": "Reuters"},
]

BRIEFS = [
    "Malawi fuel crisis deepens, queues grow (Reuters)",
    "Rohingya camps react to ICJ verdict (AP)",
    "Fiona the hippo dies, Cincinnati Zoo (AP)",
    "Russell fastest in Vegas F1 practice (Reuters)",
    "Seoul: opposition files impeachment bid (Reuters)",
    "Gold closes at record $3,526 an ounce (Reuters)",
    "EU calls emergency talks on Kyiv strikes (Reuters)",
    "Aid convoys reach Akvan-hit coast (AFP)",
    "Kyiv blackouts after missile wave (AP)",
    "UN chief urges COP31 compromise (AFP)",
    "BepiColombo: capture burn due Saturday (ESA)",
    "Wall Street opens lower in AI rout (AP)",
    "Chip shares lead Asia sell-off (Bloomberg)",
    "Italy strike cancels flights, trains (ANSA)",
    "Senegal boat survivors tell of capsize (AFP)",
    "El Salvador assembly debates term bill (Reuters)",
    "Insurers halt Hormuz tanker cover (Bloomberg)",
    "Phillips 118 puts NZ on top v India (AP)",
    "BOJ watches as core CPI holds 2.2% (Reuters)",
    "LPR hold signals steady China policy (Reuters)",
    "Cancer-pill patients await wider trial (Reuters)",
    "Akvan floods displace thousands inland (AFP)",
    "COP31 talks run past midnight deadline (Reuters)",
]

DATE_CHECK = ("First reported Thursday 19 Nov, so NOT shown as Friday's "
              "news: the Shenzhen summit itself - Anthropic's IPO pricing "
              "and Nasdaq debut - the ICJ Rohingya verdict itself - GTA "
              "VI's midnight launch - the Riyadh tower attack - Voyager "
              "1's light-day (18 Nov).")

FOOTER1 = ("Every story here happened, or was first reported, on Friday "
           "20 November 2026 in at least one time zone. Claims are "
           "attributed, not stated as fact.")
FOOTER2 = ("Sources: Reuters, AP, AFP, Bloomberg, ANSA, ESA. All "
           "illustrations are original vector drawings made with Python "
           "and Pillow for this page.")
FOOTER3 = "THE WORLD IN ONE DAY - news-image-20261120-v2 - Built for make.fun"


# ------------------------------------------------------------- helpers

def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, maxw):
    """Greedy word wrap by pixel width; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if tw(d, trial, font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, font, maxw, maxlines):
    """Wrap and clamp to maxlines, ending the last line with '...'."""
    lines = wrap(d, text, font, maxw)
    if len(lines) <= maxlines:
        return lines
    lines = lines[:maxlines]
    last = lines[-1]
    while last and tw(d, last + "...", font) > maxw:
        last = last[:-1]
    lines[-1] = last.rstrip() + "..."
    return lines


def block(d, x, y, text, font, fill, maxw, maxlines, lh):
    for i, ln in enumerate(fit(d, text, font, maxw, maxlines)):
        d.text((x, y + i * lh), ln, font=font, fill=fill)
    return y + maxlines * lh


def italic(img, x, y, text, font, fill):
    """Fake-italic: render the text, shear it, paste it back."""
    wpx = int(img.width and 0)  # placeholder, real width below
    tmp_d = ImageDraw.Draw(img)
    wpx = int(tmp_d.textlength(text, font=font)) + 8
    hpx = font.size + 6
    layer = Image.new("RGBA", (wpx + hpx // 3, hpx), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((2, 2), text, font=font, fill=fill + (255,))
    layer = layer.transform(layer.size, Image.AFFINE,
                            (1, 0.28, -0.28 * hpx, 0, 1, 0))
    img.paste(layer, (int(x), int(y)), layer)


def chip_bar(d, x, y, text, fg, bg):
    f = F(SANSB, 10)
    wpx = tw(d, text, f) + 16
    d.rectangle([x, y, x + wpx, y + 17], fill=bg)
    d.text((x + 8, y + 3), text, font=f, fill=fg)
    return wpx


# ------------------------------------------------------------ masthead

def masthead(img, d):
    f_eye = F(SANSB, 12)
    eye = "T H E   W O R L D   I N   O N E   D A Y"
    d.text(((W - tw(d, eye, f_eye)) / 2, 14), eye, font=f_eye, fill=INK)
    d.text((M, 14), "No. 47", font=f_eye, fill=GRAY)
    r = "ONE IMAGE - ONE DAY"
    d.text((W - M - tw(d, r, f_eye), 14), r, font=f_eye, fill=GRAY)
    d.line([M, 36, W - M, 36], fill=LINE, width=1)

    f_title = F(SERIFB, 57)
    title = "Friday 20 November 2026"
    d.text(((W - tw(d, title, f_title)) / 2, 44), title,
           font=f_title, fill=INK)
    d.line([M, 112, W - M, 112], fill=INK, width=3)
    d.line([M, 117, W - M, 117], fill=INK, width=1)

    d.rectangle([M, 123, W - M, 151], fill=RED)
    f_k = F(SANSB, 13)
    d.text(((W - tw(d, KICKER, f_k)) / 2, 130), KICKER, font=f_k,
           fill=(255, 255, 255))


def stats(d):
    f_num = F(SERIFB, 27)
    f_lab = F(SANSB, 9)
    cell = CW / 6.0
    for i, (num, lab) in enumerate(STATS):
        cx = M + i * cell
        if i:
            d.line([cx, 162, cx, 200], fill=LINE, width=1)
        d.text((cx + (cell - tw(d, num, f_num)) / 2, 160), num,
               font=f_num, fill=RED)
        for j, ln in enumerate(fit(d, lab, f_lab, cell - 10, 2)):
            d.text((cx + (cell - tw(d, ln, f_lab)) / 2, 196 + j * 11),
                   ln, font=f_lab, fill=INK)
    d.line([M, 222, W - M, 222], fill=LINE, width=1)


def chips(d):
    f = F(SANSB, 10)
    widths = [tw(d, c, f) + 18 for c in CHIPS]
    total = sum(widths) + 8 * (len(CHIPS) - 1)
    x = (W - total) / 2
    for c, wpx in zip(CHIPS, widths):
        d.rounded_rectangle([x, 230, x + wpx, 252], radius=9,
                            outline=RED, width=1)
        d.text((x + 9, 236), c, font=f, fill=DARKRED)
        x += wpx + 8


# --------------------------------------------------------- lead panels

def art_akvan(d, x, y, w, h):
    for i in range(h):
        t = i / h
        col = (int(16 + 30 * t), int(70 + 40 * t), int(96 + 30 * t))
        d.line([x, y + i, x + w, y + i], fill=col)
    cx, cy = x + 104, y + h // 2
    for r in range(44, 6, -6):
        start = (r * 47) % 360
        shade = (225, 232, 235) if (r // 6) % 2 else (168, 196, 205)
        d.arc([cx - r, cy - r * 0.78, cx + r, cy + r * 0.78],
              start=start, end=start + 235, fill=shade, width=4)
    d.ellipse([cx - 7, cy - 6, cx + 7, cy + 6], fill=GOLD)
    land = [(x + 218, y + h), (x + 232, y + 44), (x + 252, y + 30),
            (x + 276, y + 38), (x + w, y + 26), (x + w, y + h)]
    d.polygon(land, fill=(196, 164, 102))
    d.line([(x + 232, y + 44), (x + 252, y + 30), (x + 276, y + 38),
            (x + w, y + 26)], fill=(120, 92, 48), width=2)
    for gx in range(x + 238, x + w - 8, 26):
        gy = y + 52 + (gx // 7) % 12
        d.line([gx, gy, gx - 5, gy - 13], fill=(60, 92, 44), width=2)
        d.arc([gx - 10, gy - 20, gx + 3, gy - 8], 180, 330,
              fill=(60, 92, 44), width=2)
        d.arc([gx - 3, gy - 20, gx + 10, gy - 8], 210, 360,
              fill=(60, 92, 44), width=2)
    for rx in range(x + 12, x + 190, 22):
        d.line([rx, y + 8, rx - 6, y + 22], fill=(170, 205, 220),
               width=1)
    d.rectangle([x, y + h - 19, x + 168, y + h], fill=RED)
    d.text((x + 7, y + h - 15), "LANDFALL - GUSTS 110 KM/H",
           font=F(SANSB, 10), fill=(255, 255, 255))


def art_kyiv(d, x, y, w, h):
    for i in range(h):
        t = i / h
        col = (int(10 + 12 * t), int(16 + 14 * t), int(38 + 22 * t))
        d.line([x, y + i, x + w, y + i], fill=col)
    for sx, sy in [(30, 12), (70, 22), (150, 8), (205, 18), (262, 10),
                   (96, 30), (238, 30), (180, 26)]:
        d.point((x + sx, y + sy), fill=(230, 230, 220))
    d.ellipse([x + 278, y + 8, x + 296, y + 26], fill=(232, 226, 200))
    base = y + h
    blocks = [(0, 34), (26, 48), (52, 30), (76, 56), (108, 38),
              (132, 50), (160, 32), (184, 58), (216, 40), (242, 52),
              (272, 36), (296, 46)]
    for bx, bh in blocks:
        d.rectangle([x + bx, base - bh, x + bx + 22, base],
                    fill=(5, 7, 14))
    d.pieslice([x + 80, base - 74, x + 104, base - 44], 180, 360,
               fill=(5, 7, 14))
    d.rectangle([x + 90, base - 76, x + 94, base - 58], fill=(5, 7, 14))
    for wx, wy in [(34, 66), (84, 52), (140, 60), (196, 48), (252, 62),
                   (60, 74), (222, 72)]:
        d.rectangle([x + wx, y + wy, x + wx + 3, y + wy + 4],
                    fill=(250, 205, 90))
    trails = [((x + 300, y + 2), (x + 210, y + 62)),
              ((x + 262, y + 0), (x + 150, y + 58)),
              ((x + 316, y + 20), (x + 262, y + 66))]
    for (ax, ay), (bx2, by2) in trails:
        d.line([ax, ay, bx2, by2], fill=(255, 120, 50), width=5)
        d.line([ax, ay, bx2, by2], fill=(255, 226, 170), width=2)
        d.ellipse([bx2 - 9, by2 - 9, bx2 + 9, by2 + 9],
                  fill=(255, 140, 50))
        d.ellipse([bx2 - 5, by2 - 5, bx2 + 5, by2 + 5],
                  fill=(255, 205, 110))
        for k in range(8):
            ang = k * 0.785
            px = bx2 + int(13 * math.cos(ang))
            py = by2 + int(13 * math.sin(ang))
            d.line([bx2, by2, px, py], fill=(255, 170, 80), width=2)
    d.rectangle([x, y + h - 19, x + 148, y + h], fill=RED)
    d.text((x + 7, y + h - 15), "~30 MISSILES - 3 KILLED",
           font=F(SANSB, 10), fill=(255, 255, 255))


def art_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 246, 236))
    for gy in range(12, h - 8, 14):
        d.line([x + 8, y + gy, x + w - 8, y + gy],
               fill=(214, 206, 188), width=1)
    pts = [(8, 16), (52, 20), (92, 15), (128, 26), (162, 24),
           (196, 40), (228, 52), (258, 68), (292, 82), (308, 88)]
    xy = [(x + px, y + py) for px, py in pts]
    d.line(xy, fill=RED, width=3)
    for px, py in xy[::3]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    ex, ey = xy[-1]
    d.polygon([(ex, ey), (ex - 11, ey - 3), (ex - 4, ey - 11)],
              fill=RED)
    f = F(SANSB, 11)
    d.text((x + 12, y + 30), "NIKKEI -4.9%", font=f, fill=RED)
    d.text((x + 12, y + 48), "KOSPI -5.4%", font=f, fill=DARKRED)
    d.text((x + 12, y + 66), "TAIEX -6.8%", font=f, fill=(90, 20, 20))
    d.text((x + w - 92, y + 6), "FRI 20 NOV", font=F(SANSB, 9),
           fill=GRAY)


ARTS = {"akvan": art_akvan, "kyiv": art_kyiv, "chart": art_chart}


def lead_panels(img, d):
    pw, ph, gap, y0 = 317, 224, 12, 262
    f_tag, f_head = F(SANSB, 9), F(SERIFB, 16)
    f_body, f_src = F(SANS, 10), F(SERIF, 9)
    for i, lead in enumerate(LEADS):
        x = M + i * (pw + gap)
        d.rectangle([x, y0, x + pw, y0 + ph], fill=CARD, outline=LINE,
                    width=1)
        ARTS[lead["art"]](d, x + 1, y0 + 1, pw - 2, 94)
        d.text((x + 10, y0 + 104), lead["tag"], font=f_tag, fill=RED)
        block(d, x + 10, y0 + 120, lead["head"], f_head, INK,
              pw - 20, 2, 20)
        block(d, x + 10, y0 + 164, lead["body"], f_body, INK,
              pw - 20, 3, 13)
        italic(img, x + 10, y0 + 206, lead["src"], f_src, GRAY)


# ------------------------------------------------------- feature cards

def icon_mercury(d, x, y):
    d.ellipse([x + 8, y + 10, x + 34, y + 36], fill=(168, 160, 148),
              outline=INK, width=1)
    for cx, cy, r in [(16, 18, 3), (26, 26, 4), (20, 30, 2)]:
        d.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                  fill=(140, 132, 118))
    d.arc([x + 2, y + 2, x + 40, y + 22], 200, 330, fill=GOLD, width=2)
    d.rectangle([x + 30, y + 4, x + 37, y + 11], fill=NAVY)
    d.line([x + 33, y + 11, x + 27, y + 17], fill=INK, width=1)


def icon_yen(d, x, y):
    d.ellipse([x + 7, y + 6, x + 35, y + 34], fill=(232, 196, 92),
              outline=(146, 110, 30), width=2)
    d.text((x + 15, y + 11), "Y", font=F(SANSB, 15), fill=(120, 88, 20))
    d.line([x + 14, y + 22, x + 28, y + 22], fill=(120, 88, 20),
           width=2)
    d.line([x + 14, y + 26, x + 28, y + 26], fill=(120, 88, 20),
           width=2)


def icon_bank(d, x, y):
    d.polygon([(x + 4, y + 12), (x + 36, y + 12), (x + 20, y + 3)],
              fill=RED)
    for cx in (9, 17, 25):
        d.rectangle([x + cx, y + 16, x + cx + 4, y + 30], fill=NAVY)
    d.rectangle([x + 4, y + 32, x + 36, y + 36], fill=INK)
    d.text((x + 15, y + 17), "%", font=F(SANSB, 11), fill=(255, 255, 255))


def icon_globe(d, x, y):
    d.ellipse([x + 6, y + 5, x + 36, y + 35], outline=TEAL, width=2)
    d.ellipse([x + 15, y + 5, x + 27, y + 35], outline=TEAL, width=1)
    d.line([x + 6, y + 20, x + 36, y + 20], fill=TEAL, width=1)
    d.polygon([(x + 24, y + 24), (x + 33, y + 30), (x + 25, y + 33)],
              fill=GREEN)
    d.line([x + 25, y + 31, x + 30, y + 24], fill=GREEN, width=2)


def icon_boat(d, x, y):
    d.polygon([(x + 5, y + 22), (x + 35, y + 22), (x + 30, y + 30),
               (x + 10, y + 30)], fill=(122, 78, 40))
    d.line([x + 20, y + 22, x + 20, y + 6], fill=INK, width=2)
    d.polygon([(x + 21, y + 7), (x + 21, y + 21), (x + 31, y + 21)],
              fill=(240, 236, 224), outline=INK)
    for wx in (4, 16, 28):
        d.arc([x + wx, y + 31, x + wx + 10, y + 39], 0, 180,
              fill=TEAL, width=2)


def icon_placard(d, x, y):
    d.rectangle([x + 6, y + 4, x + 34, y + 22], fill=CARD, outline=RED,
                width=2)
    d.line([x + 11, y + 10, x + 29, y + 10], fill=RED, width=2)
    d.line([x + 11, y + 15, x + 26, y + 15], fill=INK, width=2)
    d.line([x + 20, y + 22, x + 20, y + 36], fill=(122, 78, 40),
           width=3)


def icon_cricket(d, x, y):
    d.polygon([(x + 10, y + 4), (x + 17, y + 6), (x + 13, y + 26),
               (x + 7, y + 24)], fill=(206, 170, 105), outline=INK)
    d.rectangle([x + 11, y + 25, x + 15, y + 35], fill=(90, 60, 30))
    d.ellipse([x + 24, y + 22, x + 37, y + 35], fill=RED, outline=INK)
    d.arc([x + 27, y + 24, x + 34, y + 33], 100, 260, fill=(255, 255, 255),
          width=1)


def icon_ballot(d, x, y):
    d.rectangle([x + 6, y + 18, x + 34, y + 36], fill=NAVY)
    d.rectangle([x + 14, y + 21, x + 26, y + 24], fill=(255, 255, 255))
    d.rectangle([x + 13, y + 3, x + 27, y + 19], fill=(255, 255, 255),
                outline=INK, width=1)
    d.line([x + 16, y + 10, x + 19, y + 14], fill=GREEN, width=2)
    d.line([x + 19, y + 14, x + 25, y + 6], fill=GREEN, width=2)
    d.text((x + 28, y + 26), "3", font=F(SANSB, 11), fill=GOLD)


def icon_tanker(d, x, y):
    d.polygon([(x + 3, y + 24), (x + 37, y + 24), (x + 33, y + 32),
               (x + 8, y + 32)], fill=(60, 60, 66))
    d.rectangle([x + 6, y + 21, x + 37, y + 24], fill=RED)
    d.rectangle([x + 10, y + 15, x + 20, y + 21], fill=(150, 150, 156))
    d.rectangle([x + 23, y + 15, x + 30, y + 21], fill=(150, 150, 156))
    d.rectangle([x + 31, y + 10, x + 35, y + 21], fill=INK)
    for wx in (4, 16, 28):
        d.arc([x + wx, y + 32, x + wx + 10, y + 39], 0, 180,
              fill=TEAL, width=2)


def icon_pill(d, x, y):
    d.rounded_rectangle([x + 2, y + 8, x + 26, y + 20], radius=6,
                        fill=(240, 238, 232), outline=INK, width=1)
    d.rounded_rectangle([x + 14, y + 8, x + 26, y + 20], radius=6,
                        fill=RED)
    d.rectangle([x + 14, y + 9, x + 20, y + 19], fill=RED)
    for cx, cy, r in [(31, 27, 6), (36, 33, 4), (38, 37, 2)]:
        d.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                  fill=(214, 120, 110), outline=DARKRED, width=1)


ICONS = {"mercury": icon_mercury, "yen": icon_yen, "bank": icon_bank,
         "globe": icon_globe, "boat": icon_boat, "placard": icon_placard,
         "cricket": icon_cricket, "ballot": icon_ballot,
         "tanker": icon_tanker, "pill": icon_pill}


def feature_cards(img, d):
    cw2, ch2, gap = 188, 122, 9
    f_tag, f_head = F(SANSB, 8), F(SANSB, 11)
    f_body, f_src = F(SANS, 9), F(SERIF, 8)
    for idx, feat in enumerate(FEATURES):
        row, col = divmod(idx, 5)
        x = M + col * (cw2 + gap)
        y = 494 + row * 128
        d.rectangle([x, y, x + cw2, y + ch2], fill=CARD, outline=LINE,
                    width=1)
        d.rectangle([x + 7, y + 7, x + 23, y + 23], fill=RED)
        d.text((x + 10 if feat["n"] < 10 else x + 8, y + 10),
               str(feat["n"]), font=F(SANSB, 10), fill=(255, 255, 255))
        d.text((x + 28, y + 10), feat["tag"], font=f_tag, fill=RED)
        ICONS[feat["icon"]](d, x + 7, y + 28)
        block(d, x + 52, y + 29, feat["head"], f_head, INK,
              cw2 - 59, 3, 13)
        block(d, x + 7, y + 74, feat["body"], f_body, INK,
              cw2 - 14, 3, 11)
        italic(img, x + 7, y + 108, feat["src"], f_src, GRAY)


# ------------------------------------------------------------- map etc

LAND = [
    (-100, 52, 42, 13), (-95, 33, 26, 9), (-42, 74, 12, 5),
    (-62, -8, 13, 9), (-64, -24, 8, 11),
    (16, 50, 22, 8), (18, 12, 24, 11), (24, -14, 13, 9),
    (88, 54, 58, 10), (80, 22, 12, 9), (103, 16, 9, 8),
    (138, 37, 5, 4), (134, -25, 15, 6), (172, -42, 4, 4),
]

PINS = [
    (1, 86.4, 19.3), (2, 30.5, 50.4), (3, 139.7, 35.7),
    (5, 128.0, 32.5), (6, 116.4, 39.9), (7, 30.7, 36.9),
    (8, -17.4, 14.7), (9, 12.5, 41.9), (10, 172.6, -40.5),
    (11, -89.2, 13.7), (12, 56.3, 26.5), (13, -71.1, 42.3),
]


def world_map(d):
    d.text((M, 752), "WHERE FRIDAY HAPPENED", font=F(SANSB, 11),
           fill=INK)
    x0, y0, w, h = 28, 770, 372, 114
    cols, rows = 62, 19
    for r in range(rows):
        lat = 80 - (r + 0.5) * 140.0 / rows
        for c in range(cols):
            lon = -180 + (c + 0.5) * 360.0 / cols
            land = False
            for cx, cy, rx, ry in LAND:
                if ((lon - cx) / rx) ** 2 + ((lat - cy) / ry) ** 2 <= 1:
                    land = True
                    break
            if not land and -4 < lat < 4 and 95 < lon < 140:
                land = (c + r) % 3 != 0
            if land:
                px = x0 + (c + 0.5) * w / cols
                py = y0 + (r + 0.5) * h / rows
                d.ellipse([px - 1.7, py - 1.7, px + 1.7, py + 1.7],
                          fill=(122, 106, 78))
    f_pin = F(SANSB, 8)
    for n, lon, lat in PINS:
        px = x0 + (lon + 180) / 360.0 * w
        py = y0 + (80 - lat) / 140.0 * h
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        s = str(n)
        d.text((px - tw(d, s, f_pin) / 2, py - 4), s, font=f_pin,
               fill=(255, 255, 255))
    mx, my = x0 + w - 12, y0 - 8
    d.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=(168, 160, 148),
              outline=GOLD, width=2)
    d.text((mx - tw(d, "4", f_pin) / 2, my - 4), "4", font=f_pin,
           fill=INK)
    d.text((M, 890), "Pins 1-13 = pictured stories. 4 = BepiColombo "
           "at Mercury (space).", font=F(SANS, 8), fill=GRAY)


def briefs(d):
    d.text((416, 752), "ALSO ON FRIDAY", font=F(SANSB, 12), fill=RED)
    note = "23 more stories"
    d.text((W - M - tw(d, note, F(SANS, 9)), 755), note,
           font=F(SANS, 9), fill=GRAY)
    d.line([416, 770, W - M, 770], fill=LINE, width=1)
    f_num, f_txt = F(SANSB, 9), F(SANS, 9)
    for i, item in enumerate(BRIEFS):
        col, row = divmod(i, 12)
        x = 416 + col * 298
        y = 778 + row * 11
        num = "%d." % (14 + i)
        d.text((x, y), num, font=f_num, fill=RED)
        d.text((x + tw(d, num, f_num) + 4, y), item, font=f_txt,
               fill=INK)


def date_check(d):
    y0 = 912
    d.rectangle([M, y0, W - M, y0 + 48], fill=(250, 238, 228),
                outline=RED, width=2)
    d.text((M + 10, y0 + 6), "DATE CHECK", font=F(SANSB, 10), fill=RED)
    block(d, M + 10, y0 + 22, DATE_CHECK, F(SANS, 9), INK, CW - 20, 2,
          12)


def footer(d):
    d.line([M, 970, W - M, 970], fill=LINE, width=1)
    f1, f2, f3 = F(SERIF, 9), F(SERIF, 9), F(SANSB, 8)
    for y, txt, f in ((978, FOOTER1, f1), (991, FOOTER2, f2),
                      (1005, FOOTER3, f3)):
        d.text(((W - tw(d, txt, f)) / 2, y), txt, font=f,
               fill=GRAY if f is f3 else INK)


# ---------------------------------------------------------------- main

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(img, d)
    stats(d)
    chips(d)
    lead_panels(img, d)
    feature_cards(img, d)
    world_map(d)
    briefs(d)
    date_check(d)
    footer(d)
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, "entry.png"), format="PNG", optimize=True)


if __name__ == "__main__":
    build()
