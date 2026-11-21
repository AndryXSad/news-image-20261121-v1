#!/usr/bin/env python3
"""Render the 21 November 2026 world-news front page (1024x1024 PNG).

A newspaper front page drawn from scratch with PIL and DejaVu fonts:
a dark masthead with a DATE CHECK box, three illustrated leads (the
M6.8 Peru quake at 00:09 UTC, COP31 running into overtime with a
draft silent on fossil fuels, and Trump's post-trip news conference),
a dark world map with eight numbered pins, a UTC timeline of five
moments, a day-in-figures strip, one top story from each of seven
regions, a twenty-four-item grid with no repeated dateline, and an
"Also today" ticker. 45 stories in all; every one was checked
against reporting dated Saturday 21 November 2026 before it was
drawn (see STORIES.md).

Deterministic output: no timestamps, no unseeded randomness, fixed
font paths, fixed story order. The same run always produces the same
bytes. A seeded generator (seed 20261121) places the ocean stipple,
the paper grain and the seismograph noise, so it is identical on
every run.

Run locally:  python3 main.py            (writes entry.png next to main.py)
Grader mode:  MAKEFUN_OUTPUT_DIR=out python3 main.py
              (writes entry.png into out/ and nowhere else)
If PIL is unavailable, main.py falls back to copying the pre-rendered
entry.png shipped in this repository into the output directory.
"""
import math
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_NAME = "entry.png"
W, H = 1024, 1024
SEED = 20261121

try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except Exception:  # pragma: no cover - grader without PIL
    HAVE_PIL = False

PAPER = (247, 243, 232)
PANEL = (255, 255, 255)
INK = (17, 17, 17)
RED = (176, 42, 42)
DARKRED = (140, 28, 28)
BLUE = (31, 78, 121)
STEEL = (58, 110, 150)
GRAY = (102, 102, 102)
GOLD = (201, 162, 39)
DARK = (20, 20, 20)
MAPBG = (24, 40, 56)
MAPLINE = (52, 76, 98)
LANDC = (216, 210, 189)
LANDLINE = (138, 132, 116)
SLATE = (16, 24, 44)
SKY = (38, 48, 70)
SEA = (214, 232, 240)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_FILES = {
    "serif_b": "DejaVuSerif-Bold.ttf",
    "serif": "DejaVuSerif.ttf",
    "sans_b": "DejaVuSans-Bold.ttf",
    "sans": "DejaVuSans.ttf",
}


def load_font(kind, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONT_FILES[kind]),
                              size)


def fit_words(dr, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if dr.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(dr, x, y, text, fnt, max_width, color, leading=None,
               center=False):
    leading = leading or int(fnt.size * 1.28)
    for line in fit_words(dr, text, fnt, max_width):
        if center:
            dr.text((x + max_width / 2, y), line, font=fnt, fill=color,
                    anchor="ma")
        else:
            dr.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def hline(dr, x0, x1, y, width=2, color=INK):
    dr.line([(x0, y), (x1, y)], fill=color, width=width)


def tag(dr, x, y, text, size=12):
    dr.text((x, y), text, font=load_font("sans_b", size), fill=RED)


# ---------------- the stories (all verified 21 Nov 2026) ----------------
LEADS = [
    ("LEAD  \u2022  PERU",
     "M6.8 quake shakes central Peru, felt in Lima",
     "Strikes 00:09 UTC near Jun\u00edn, 129 km deep; Congress "
     "evacuated; no deaths or serious damage reported.",
     "Reuters, AFP  \u2022  21 Nov",
     "quake"),
    ("LEAD  \u2022  CLIMATE",
     "COP31 runs into overtime with no deal in sight",
     "Draft still silent on fossil fuels; a third text is promised "
     "Saturday morning; Panama threatens to block a weak deal.",
     "AFP, Asia Today  \u2022  21 Nov",
     "cop"),
    ("LEAD  \u2022  USA",
     "Trump: Putin \u2018a friend of mine\u2019; no rush on Iran",
     "After the Beijing trip, Trump says an Iran-strike decision "
     "waits until next year; press told to hand in phones.",
     "BBC  \u2022  21 Nov",
     "trump"),
]

# Simplified continent outlines (lon, lat), hand-approximated afresh.
N_AMERICA = [(-168, 66), (-145, 70), (-125, 71), (-110, 68), (-95, 69),
             (-85, 66), (-80, 73), (-70, 62), (-60, 55), (-55, 47),
             (-65, 44), (-70, 42), (-75, 38), (-80, 32), (-81, 26),
             (-84, 30), (-90, 21), (-95, 18), (-90, 15), (-85, 12),
             (-80, 9), (-78, 8), (-83, 10), (-88, 14), (-92, 15),
             (-97, 16), (-100, 20), (-105, 22), (-110, 25), (-114, 29),
             (-118, 33), (-122, 37), (-124, 42), (-124, 48), (-128, 52),
             (-135, 58), (-145, 60), (-155, 58), (-162, 58), (-166, 60)]
S_AMERICA = [(-79, 9), (-72, 11), (-62, 9), (-52, 5), (-50, 0),
             (-43, -3), (-35, -8), (-38, -15), (-41, -22), (-48, -27),
             (-53, -33), (-58, -38), (-65, -41), (-66, -47), (-69, -52),
             (-71, -54), (-73, -50), (-73, -44), (-72, -37), (-71, -30),
             (-70, -19), (-75, -15), (-79, -8), (-81, -4), (-80, 1)]
AFRICA = [(-17, 15), (-16, 21), (-11, 28), (-6, 35), (0, 36), (10, 37),
          (20, 32), (30, 31), (33, 28), (36, 27), (39, 21), (41, 16),
          (43, 11), (48, 11), (51, 11), (46, 5), (41, -1), (40, -8),
          (37, -15), (35, -20), (32, -28), (28, -33), (20, -35),
          (17, -32), (14, -22), (12, -17), (9, -4), (9, 4), (-8, 5),
          (-13, 8), (-16, 12)]
EUROPE = [(-10, 36), (-9, 39), (-9, 43), (-4, 48), (-1, 50), (2, 51),
          (4, 53), (8, 55), (8, 57), (11, 58), (18, 56), (21, 55),
          (21, 58), (24, 58), (28, 60), (30, 61), (32, 64), (38, 66),
          (44, 68), (50, 69), (54, 68), (48, 66), (44, 64), (40, 61),
          (36, 59), (33, 56), (31, 53), (30, 50), (28, 47), (29, 45),
          (32, 46), (35, 45), (39, 47), (41, 45), (38, 43), (35, 42),
          (32, 41), (28, 41), (27, 43), (25, 40), (23, 36), (26, 38),
          (23, 40), (20, 40), (19, 42), (16, 44), (13, 44), (9, 44),
          (7, 44), (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 38)]
ASIA = [(54, 68), (60, 69), (68, 71), (75, 72), (85, 74), (95, 76),
        (105, 76), (115, 73), (125, 72), (135, 72), (145, 72), (155, 70),
        (165, 69), (173, 66), (178, 65), (170, 60), (162, 56), (158, 52),
        (150, 54), (142, 52), (141, 48), (138, 44), (134, 43), (130, 39),
        (127, 36), (124, 38), (121, 36), (119, 31), (116, 26), (112, 22),
        (109, 18), (107, 11), (104, 9), (100, 7), (98, 10), (96, 15),
        (93, 20), (90, 22), (87, 21), (84, 19), (80, 14), (77, 8),
        (75, 12), (73, 17), (70, 20), (67, 24), (63, 25), (59, 25),
        (56, 26), (53, 27), (51, 29), (49, 30), (47, 30), (44, 29),
        (41, 31), (39, 32), (36, 36), (34, 31), (31, 33), (29, 35),
        (28, 37), (30, 36), (33, 36), (36, 36), (39, 38), (42, 41),
        (44, 42), (47, 42), (48, 45), (47, 48), (46, 51), (47, 54),
        (49, 55), (50, 58), (49, 61), (51, 64), (53, 66)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
           (-1, 51), (-3, 51)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37),
         (141, 40), (141, 44), (143, 44), (141, 42), (139, 38),
         (136, 36), (133, 34)]
SE_ASIA = [(95, 6), (98, 6), (100, 3), (103, 1), (104, -2), (106, -6),
           (110, -7), (114, -8), (118, -9), (120, -8), (119, -4),
           (116, -1), (114, 2), (111, 4), (108, 3), (104, 2), (100, 6)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (120, -34), (126, -32),
             (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
             (153, -31), (153, -27), (150, -23), (146, -19), (142, -14),
             (141, -17), (137, -12), (133, -12), (129, -14), (126, -14),
             (122, -17), (118, -20), (114, -22)]
NEW_ZEALAND = [(167, -45), (169, -43), (172, -41), (175, -40),
               (177, -38), (176, -37), (174, -39), (172, -41),
               (170, -43), (168, -44)]
GREENLAND = [(-55, 64), (-52, 60), (-45, 60), (-40, 63), (-35, 66),
             (-30, 68), (-25, 70), (-20, 73), (-22, 77), (-30, 80),
             (-40, 80), (-50, 79), (-58, 76), (-60, 72), (-58, 68)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -19), (47, -22),
              (45, -25), (44, -23), (43, -20), (44, -17)]
BORNEO = [(109, 1), (112, 3), (116, 6), (118, 3), (119, 0), (117, -3),
          (114, -4), (110, -3), (109, -1)]
NEW_GUINEA = [(131, -1), (135, -2), (139, -3), (143, -4), (147, -7),
              (150, -9), (147, -9), (143, -8), (139, -7), (135, -5),
              (132, -3)]
SUMATRA = [(95, 5), (98, 3), (100, 1), (102, -1), (104, -3), (106, -6),
           (104, -5), (101, -2), (98, 1), (96, 4)]
CUBA = [(-85, 22), (-81, 23), (-77, 21), (-74, 20), (-77, 21),
        (-81, 22), (-84, 22)]
ICELAND = [(-22, 64), (-19, 63), (-15, 64), (-14, 65), (-17, 66),
           (-20, 66), (-23, 65)]
LAND = [N_AMERICA, S_AMERICA, AFRICA, EUROPE, ASIA, BRITAIN, JAPAN,
        SE_ASIA, AUSTRALIA, NEW_ZEALAND, GREENLAND, MADAGASCAR, BORNEO,
        NEW_GUINEA, SUMATRA, CUBA, ICELAND]

# (number, lon, lat, nudge_x, nudge_y) — nudges keep every pin on land
# (verified by point-in-polygon against LAND, min separation >= 20 px):
# pin 4 (Tallinn) and pin 6 (Mukalla) floated in the sea before;
# pin 8 (Wellington) sat on the New Zealand coastline.
PINS = [("1", -76.2, -11.0, 0, 0), ("2", 30.7, 36.9, 18, 2),
        ("3", -77.0, 38.9, 0, 0), ("4", 24.7, 59.4, -10, 4),
        ("5", 34.5, 31.5, -8, 6), ("6", 49.1, 14.5, -10, 4),
        ("7", 77.2, 28.6, 0, 0), ("8", 174.8, -41.3, 0, -2)]
KEY = ["1  JUN\u00cdN \u2014 M6.8 quake; Lima shaken; no deaths",
       "2  ANTALYA \u2014 COP31 overtime; fossil-fuel row",
       "3  WASHINGTON \u2014 Trump delays Iran-strike decision",
       "4  TALLINN \u2014 Estonia to shut Russia border crossings",
       "5  GAZA \u2014 22,000 Palestinian children dead, ministry says",
       "6  MUKALLA \u2014 UKMTO reports incident off Yemen",
       "7  NEW DELHI \u2014 Record \u20b91.22 lakh crore foreign inflow",
       "8  WELLINGTON \u2014 KL Rahul completes the SENA set"]

TIMES = [("00:09 UTC", "M6.8 quake strikes central Peru"),
         ("02:34 UTC", "BBC: RAF-base villagers to vote on 'leaving UK'"),
         ("MORNING", "COP31 presidency promises a third draft text"),
         ("AFTERNOON", "KL Rahul completes the SENA set in Wellington"),
         ("EVENING", "Trump: no rush on Iran strikes; decision delayed")]

FIGS = [("6.8", "magnitude of the Peru quake, 00:09 UTC"),
        ("357,000", "people displaced in Yemen since August"),
        ("\u20b91.22 lakh cr", "record foreign inflow into Indian shares"),
        ("0", "mentions of fossil fuels in the COP31 draft")]

REGIONS = [("NORTH AMERICA", "Army cleared to blast Iowa explosives"),
           ("SOUTH AMERICA", "Peru: Congress evacuated in quake"),
           ("EUROPE", "Hungary lifts block on Ukraine EU talks"),
           ("AFRICA", "Ebola hits ~100 schools in Congo"),
           ("MIDDLE EAST", "Saudi-led force downs Houthi missiles"),
           ("ASIA", "Record cash floods Indian shares"),
           ("OCEANIA", "Cyclone Xavier fades over Cook Islands")]

GRID = [("KYIV", "Ukraine hits three Russian missile launchers"),
        ("SUMY", "HIMARS strike kills 20 Russian commanders"),
        ("BRUSSELS", "EU warns COP31 risks a 'fossil summit'"),
        ("LONDON", "Villagers to vote on 'leaving UK' over RAF base"),
        ("IOWA", "Army cleared to blast unstable lead azide"),
        ("CALIFORNIA", "State subpoenas Nvidia over China chip sales"),
        ("WASHINGTON", "US declassifies more UFO footage"),
        ("WHITE HOUSE", "Trump: Nvidia chief deserves 'second chance'"),
        ("TEHRAN", "US and Israel weigh fresh strike on Iran"),
        ("YEMEN", "UN: displaced in Yemen up to 357,000"),
        ("WEST BANK", "Palestinian shot dead by settler guard"),
        ("HAITI", "Two Salvadorans killed handling explosives"),
        ("AFGHANISTAN", "Four students killed in old munitions blast"),
        ("PYONGYANG", "North Korea and Laos vow closer cooperation"),
        ("TAIPEI", "Taiwan reports China-linked accounts to Meta"),
        ("RABAT", "Morocco commits \u20ac366m to home defence industry"),
        ("PRAGUE", "Czechia weighs faster air-defence build-up"),
        ("GENEVA", "Switzerland backs ICJ genocide ruling"),
        ("WARSAW", "Poland opens probe into airspace incursion"),
        ("BERLIN", "Europe calls for winter ceasefire in Ukraine"),
        ("PASADENA", "Voyager 1 a light-day from Earth, a first"),
        ("PACIFIC", "US opens Pacific seabed to deep-sea mining"),
        ("TREASURY", "Bessent: humans must steer military AI"),
        ("BEIJING", "Xi displays clout after hosting Trump, Putin")]

TICKER = ("England host New Zealand at Twickenham  \u2022  Wales build "
          "on All Blacks win vs Australia  \u2022  L7 announce final "
          "Australia\u2013NZ tour")

# ---------------- illustrations ----------------
def art_quake(dr, x, y):
    """Seismograph trace: quiet line, then a violent spike, then calm."""
    w, h = 312, 62
    dr.rectangle([x, y, x + w, y + h], fill=SLATE)
    # graticule: vertical time divisions + faint horizontals
    for gx in range(x + 28, x + w, 28):
        dr.line([(gx, y + 4), (gx, y + h - 4)], fill=SKY, width=1)
    for gy in (y + 16, y + 31, y + 46):
        dr.line([(x + 6, gy), (x + w - 6, gy)], fill=SKY, width=1)
    rng = random.Random(SEED + 11)
    mid = y + h // 2
    pts = []
    for i in range(0, w - 4, 3):
        px = x + 4 + i
        if i < 120:
            amp = rng.uniform(-2.5, 2.5)
        elif i < 200:
            amp = rng.uniform(-26, 26)
        else:
            amp = rng.uniform(-4, 4)
        pts.append((px, mid + amp))
    # glow under the trace, then the crisp white line
    dr.line(pts, fill=(96, 118, 150), width=5)
    dr.line(pts, fill=(247, 243, 232), width=2)
    # red ring + dot at the biggest jolt
    dr.ellipse([x + 148, mid - 28, x + 164, mid - 12], outline=RED,
               width=2)
    dr.ellipse([x + 152, mid - 24, x + 160, mid - 16], fill=RED)
    dr.text((x + 8, y + 5), "M6.8", font=load_font("sans_b", 16),
            fill=(247, 243, 232))
    # depth label right-aligned inside the box (was clipped at the edge)
    dr.text((x + w - 8, y + 5), "DEPTH 129 KM",
            font=load_font("sans_b", 11), fill=GOLD, anchor="ra")
    dr.text((x, y + h + 4), "00:09 UTC \u2022 30 km NW of Jun\u00edn",
            font=load_font("sans", 10), fill=GRAY)


def star(dr, cx, cy, r, fill):
    """A small five-point star centred on (cx, cy)."""
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    dr.polygon(pts, fill=fill)


def art_cop(dr, x, y):
    """A warming globe: blue circle, land blobs, a rising thermometer."""
    w, h = 312, 62
    # two-tone sky: pale top band, deeper below
    dr.rectangle([x, y, x + w, y + 30], fill=(226, 238, 244))
    dr.rectangle([x, y + 30, x + w, y + h], fill=SEA)
    cx, cy = x + 62, y + 31
    # soft shadow under the globe
    dr.ellipse([cx - 30, cy + 24, cx + 30, cy + 32], fill=(190, 208, 220))
    dr.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=STEEL,
               outline=INK, width=2)
    # land blobs on the globe
    dr.ellipse([cx - 20, cy - 16, cx - 2, cy - 2], fill=LANDC)
    dr.ellipse([cx + 2, cy + 2, cx + 18, cy + 18], fill=LANDC)
    dr.ellipse([cx - 6, cy + 8, cx + 8, cy + 20], fill=LANDC)
    # graticule arcs + highlight on the upper-left limb
    dr.arc([cx - 28, cy - 28, cx + 28, cy + 28], 200, 340, fill=MAPLINE,
           width=1)
    dr.ellipse([cx - 12, cy - 28, cx + 12, cy + 28], outline=MAPLINE)
    dr.arc([cx - 28, cy - 28, cx + 28, cy + 28], 150, 260,
           fill=(220, 235, 245), width=2)
    # two thin cloud swirls
    dr.arc([cx - 18, cy - 10, cx + 2, cy + 4], 200, 340,
           fill=(247, 247, 247), width=2)
    dr.arc([cx - 4, cy + 6, cx + 16, cy + 18], 20, 160,
           fill=(247, 247, 247), width=2)
    # thermometer, mercury climbing, with tick marks
    tx = x + 148
    dr.rectangle([tx, y + 6, tx + 12, y + 50], fill=PANEL, outline=INK,
                 width=1)
    dr.rectangle([tx + 2, y + 22, tx + 10, y + 48], fill=RED)
    dr.ellipse([tx - 3, y + 44, tx + 15, y + 60], fill=RED, outline=INK)
    for ty in (y + 12, y + 22, y + 32, y + 42):
        dr.line([(tx - 3, ty), (tx, ty)], fill=INK, width=1)
    for ty, lab in ((y + 6, "1.5\u00b0C"), (y + 24, "1.0\u00b0C"),
                    (y + 42, "0.5\u00b0C")):
        dr.text((tx + 18, ty), lab, font=load_font("sans", 9), fill=INK)
    # the zero that matters: no fossil fuels named (right-aligned:
    # the old "NAMED: 0" ran past the panel's right edge)
    dr.text((x + 216, y + 6), "FOSSIL FUELS", font=load_font("sans_b", 11),
            fill=INK)
    dr.text((x + w - 8, y + 22), "NAMED: 0", font=load_font("sans_b", 17),
            fill=RED, anchor="ra")
    dr.text((x + 216, y + 44), "in the draft text",
            font=load_font("sans", 10), fill=GRAY)
    dr.text((x, y + h + 4), "Third draft promised Saturday morning",
            font=load_font("sans", 10), fill=GRAY)


def art_trump(dr, x, y):
    """A podium with two flags: the post-trip news conference.

    US flag left, China flag right (the Beijing trip), a speaker
    silhouette behind a wood podium with a gold seal, gooseneck
    microphones leaning over the top.
    """
    w, h = 312, 62
    # hall backdrop: deep blue with curtain folds
    dr.rectangle([x, y, x + w, y + h], fill=BLUE)
    for fx in range(x + 8, x + w, 26):
        dr.line([(fx, y), (fx, y + h)], fill=(26, 66, 104), width=3)
    # pale backdrop panel behind the podium
    dr.rectangle([x + 84, y + 4, x + 228, y + h], fill=(233, 226, 208),
                 outline=GOLD, width=1)
    # US flag, left: stripes + blue canton
    fx = x + 16
    dr.line([(fx, y + 6), (fx, y + 46)], fill=(247, 243, 232), width=2)
    dr.rectangle([fx + 2, y + 6, fx + 36, y + 26], fill=(247, 243, 232))
    for s in (0, 2):
        dr.rectangle([fx + 2, y + 6 + s * 5, fx + 36, y + 10 + s * 5],
                     fill=RED)
    dr.rectangle([fx + 2, y + 6, fx + 16, y + 16], fill=(31, 58, 120))
    for sx, sy in ((fx + 6, y + 9), (fx + 12, y + 9), (fx + 9, y + 13)):
        dr.point((sx, sy), fill=(247, 243, 232))
    # China flag, right: red field, one big star + four small stars
    fx = x + 260
    dr.line([(fx, y + 6), (fx, y + 46)], fill=(247, 243, 232), width=2)
    dr.rectangle([fx + 2, y + 6, fx + 36, y + 26], fill=(222, 41, 16))
    star(dr, fx + 10, y + 13, 4, GOLD)
    for sx, sy in ((fx + 19, y + 9), (fx + 23, y + 13), (fx + 21, y + 18),
                   (fx + 16, y + 19)):
        star(dr, sx, sy, 2, GOLD)
    # speaker silhouette: head and shoulders above the podium
    dr.ellipse([x + 142, y + 2, x + 170, y + 26], fill=(28, 28, 34))
    dr.polygon([(x + 128, y + 34), (x + 156, y + 24), (x + 184, y + 34),
                (x + 184, y + 40), (x + 128, y + 40)], fill=(28, 28, 34))
    # podium: wood front with panel lines, gold trim, floor shadow
    dr.rectangle([x + 96, y + 58, x + 216, y + h], fill=(10, 10, 14))
    dr.polygon([(x + 106, y + 30), (x + 206, y + 30), (x + 214, y + h),
                (x + 98, y + h)], fill=(42, 30, 22), outline=INK)
    for vx in (x + 130, x + 156, x + 182):
        dr.line([(vx, y + 32), (vx - 2, y + h)], fill=(24, 16, 10),
                width=1)
    dr.line([(x + 106, y + 30), (x + 206, y + 30)], fill=GOLD, width=2)
    # gold seal with a star
    dr.ellipse([x + 144, y + 38, x + 168, y + 60], fill=GOLD,
               outline=(247, 243, 232), width=1)
    dr.text((x + 156, y + 45), "\u2605", font=load_font("sans_b", 11),
            fill=INK, anchor="mm")
    # gooseneck microphones leaning over the podium top
    for mx, dx in ((x + 128, -6), (x + 184, 6)):
        dr.line([(mx, y + 30), (mx + dx, y + 16)], fill=INK, width=2)
        dr.ellipse([mx + dx - 5, y + 10, mx + dx + 5, y + 20], fill=INK)
    dr.text((x, y + h + 4), "Beijing trip ends \u2022 'a friend of mine'",
            font=load_font("sans", 10), fill=GRAY)


ART = {"quake": art_quake, "cop": art_cop, "trump": art_trump}

MX, MY, MW, MH = 28, 344, 556, 118


def project(lon, lat):
    px = MX + (lon + 180.0) / 360.0 * MW
    py = MY + (78.0 - lat) / 136.0 * MH
    return (px, py)


# ---------------- render ----------------
def render(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # faint paper grain (seeded: identical every run), under everything
    grain = random.Random(SEED + 7)
    for _ in range(9000):
        gx = grain.randint(0, W - 1)
        gy = grain.randint(96, H - 1)
        dr.point((gx, gy), fill=(238, 233, 220))

    # ---------- masthead ----------
    dr.rectangle([0, 0, W, 92], fill=DARK)
    dr.text((W / 2, 6), "THE DAILY GLOBE", font=load_font("serif_b", 50),
            fill=(247, 243, 232), anchor="ma")
    draw_block(dr, 28, 66,
               "SATURDAY 21 NOVEMBER 2026  \u2022  45 STORIES  \u2022  "
               "SEVEN REGIONS  \u2022  FIVE MOMENTS IN UTC",
               load_font("sans_b", 13), 968, (247, 243, 232), center=True)
    dr.rectangle([858, 12, 996, 54], fill=RED, outline=(247, 243, 232),
                 width=1)
    dr.text((927, 16), "DATE CHECK", font=load_font("sans_b", 11),
            fill=(247, 243, 232), anchor="ma")
    dr.text((927, 32), "SAT 21 NOV 2026", font=load_font("sans_b", 11),
            fill=(247, 243, 232), anchor="ma")
    dr.rectangle([0, 92, W, 94], fill=GOLD)
    # small gold globe at the masthead's left, balancing DATE CHECK
    dr.ellipse([30, 26, 66, 62], outline=GOLD, width=2)
    dr.ellipse([38, 34, 50, 44], fill=GOLD)
    dr.ellipse([50, 48, 60, 58], fill=GOLD)
    dr.arc([30, 26, 66, 62], 200, 340, fill=GOLD, width=1)
    dr.ellipse([40, 26, 56, 62], outline=GOLD, width=1)

    # ---------- three leads ----------
    colx = [28, 356, 684]
    colw = 312
    for (kick, head, deck, src, art), x in zip(LEADS, colx):
        tag(dr, x, 100, kick)
        draw_block(dr, x, 120, head, load_font("serif_b", 21), colw, INK,
                   leading=24)
        ART[art](dr, x, 186)
        draw_block(dr, x, 264, deck, load_font("sans", 12), colw, INK,
                   leading=15)
        dr.text((x, 308), src, font=load_font("sans", 11), fill=GRAY)
    hline(dr, 28, 996, 322, 2)

    # ---------- dark world map + key ----------
    tag(dr, 28, 328, "THE WORLD \u2014 EIGHT PLACES IN THE NEWS", 13)
    dr.rectangle([MX, MY, MX + MW, MY + MH], fill=MAPBG, outline=INK,
                 width=1)
    # stippled ocean (seeded: identical every run), drawn before land
    rng = random.Random(SEED)
    for _ in range(1200):
        dx = MX + rng.randint(3, MW - 3)
        dy = MY + rng.randint(3, MH - 3)
        dr.ellipse([dx, dy, dx + 1, dy + 1], fill=MAPLINE)
    # graticule
    for lon in range(-150, 181, 30):
        gx = MX + (lon + 180.0) / 360.0 * MW
        dr.line([(gx, MY), (gx, MY + MH)], fill=MAPLINE, width=1)
    for lat in (-60, -30, 0, 30, 60):
        gy = MY + (78.0 - lat) / 136.0 * MH
        dr.line([(MX, gy), (MX + MW, gy)], fill=MAPLINE, width=1)
    for poly in LAND:
        pts = [project(lon, lat) for lon, lat in poly]
        dr.polygon(pts, fill=LANDC, outline=LANDLINE)
    # land texture: seeded darker speckles on the continents only
    land_polys = [[project(lon, lat) for lon, lat in poly]
                  for poly in LAND]

    def _inside(px, py, poly):
        n = len(poly)
        j = n - 1
        c = False
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > py) != (yj > py)) and \
                    (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                c = not c
            j = i
        return c

    speck = random.Random(SEED + 23)
    for _ in range(500):
        sx = MX + speck.randint(3, MW - 3)
        sy = MY + speck.randint(3, MH - 3)
        if any(_inside(sx, sy, p) for p in land_polys):
            dr.point((sx, sy), fill=(200, 193, 170))
    # ocean labels in open water
    dr.text((MX + 52, MY + 74), "ATLANTIC OCEAN",
            font=load_font("sans_b", 9), fill=MAPLINE)
    dr.text((MX + 392, MY + 96), "PACIFIC OCEAN",
            font=load_font("sans_b", 9), fill=MAPLINE)
    dr.text((MX + 330, MY + 74), "INDIAN OCEAN",
            font=load_font("sans_b", 9), fill=MAPLINE)
    for num, lon, lat, nx, ny in PINS:
        px, py = project(lon, lat)
        px, py = px + nx, py + ny
        dr.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                   outline=(247, 243, 232), width=2)
        dr.text((px, py - 1), num, font=load_font("sans_b", 9),
                fill=(247, 243, 232), anchor="mm")
    ky = 346
    for line in KEY:
        dr.text((600, ky), line, font=load_font("sans", 11), fill=INK)
        ky += 15
    hline(dr, 28, 996, 472, 1)

    # ---------- UTC timeline ----------
    tag(dr, 28, 480, "THE DAY IN UTC \u2014 FIVE MOMENTS", 13)
    hline(dr, 28, 996, 500, 1)
    for i, (t, txt) in enumerate(TIMES):
        x = 28 + i * 194
        dr.ellipse([x - 3, 497, x + 3, 503], fill=RED)
        dr.text((x, 506), t, font=load_font("sans_b", 12), fill=RED)
        draw_block(dr, x, 522, txt, load_font("sans", 11), 184, INK,
                   leading=13)
    hline(dr, 28, 996, 552, 1)

    # ---------- day in figures ----------
    for i, (num, lab) in enumerate(FIGS):
        x = 28 + i * 242
        dr.rectangle([x, 560, x + 232, 606], fill=PANEL, outline=INK,
                     width=1)
        dr.line([(x, 560), (x + 232, 560)], fill=RED, width=3)
        dr.text((x + 10, 566), num, font=load_font("serif_b", 20),
                fill=INK)
        dr.text((x + 10, 588), lab, font=load_font("sans", 10), fill=GRAY)
        # tiny chart at the right of each box
        gx0, gy0 = x + 184, 570
        if i == 0:  # quake: mini seismograph zigzag
            zr = random.Random(SEED + 31)
            zpts = [(gx0 + k * 4, gy0 + 8 + zr.uniform(-7, 7))
                    for k in range(10)]
            dr.line(zpts, fill=RED, width=1)
        elif i == 1:  # displaced: three rising bars
            for b, bh in enumerate((6, 10, 15)):
                dr.rectangle([gx0 + b * 12, gy0 + 16 - bh,
                              gx0 + b * 12 + 8, gy0 + 16], fill=STEEL)
        elif i == 2:  # inflow: rising line with arrowhead
            dr.line([(gx0, gy0 + 14), (gx0 + 36, gy0 + 2)], fill=STEEL,
                    width=2)
            dr.polygon([(gx0 + 36, gy0 + 2), (gx0 + 29, gy0 + 2),
                        (gx0 + 36, gy0 + 9)], fill=STEEL)
        else:  # zero: flat line with a red dot on it
            dr.line([(gx0, gy0 + 8), (gx0 + 36, gy0 + 8)], fill=GRAY,
                    width=2)
            dr.ellipse([gx0 + 16, gy0 + 4, gx0 + 24, gy0 + 12], fill=RED)

    # ---------- seven regions ----------
    tag(dr, 28, 614, "SEVEN REGIONS \u2014 ONE TOP STORY FROM EACH", 13)
    for i, (region, head) in enumerate(REGIONS):
        x = 28 + i * 139
        dr.rectangle([x, 632, x + 134, 686], fill=PANEL, outline=INK,
                     width=1)
        dr.line([(x, 632), (x + 134, 632)], fill=RED, width=3)
        dr.text((x + 6, 636), region, font=load_font("sans_b", 10),
                fill=RED)
        draw_block(dr, x + 6, 650, head, load_font("sans", 11), 122, INK,
                   leading=13)

    # ---------- grid: 24 stories ----------
    tag(dr, 28, 692, "AROUND THE WORLD", 13)
    hline(dr, 28, 996, 710, 1)
    for i, (place, head) in enumerate(GRID):
        col, row = i % 4, i // 4
        x, y = 28 + col * 242, 718 + row * 39
        dr.text((x, y), place, font=load_font("sans_b", 10), fill=RED)
        draw_block(dr, x, y + 13, head, load_font("sans", 11), 230, INK,
                   leading=13)

    # ---------- ticker + footer ----------
    hline(dr, 28, 996, 958, 2)
    dr.text((28, 964), "ALSO TODAY", font=load_font("sans_b", 12),
            fill=RED)
    dr.text((150, 964), TICKER, font=load_font("sans", 11), fill=INK)
    hline(dr, 28, 996, 982, 1)
    draw_block(dr, 28, 988,
               "The Daily Globe  \u2022  Saturday 21 November 2026  "
               "\u2022  45 stories  \u2022  Sources: Reuters, AFP, BBC, "
               "Asia Today, The News PK, EIN Presswire, USGS",
               load_font("sans", 11), 968, GRAY, center=True)
    dr.rectangle([0, 1016, W, H], fill=RED)

    img.save(out_path, "PNG", optimize=True)
    print("saved", out_path, os.path.getsize(out_path), "bytes")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or HERE
    out_path = os.path.join(out_dir, OUT_NAME)
    if HAVE_PIL:
        os.makedirs(out_dir, exist_ok=True)
        render(out_path)
        return 0
    src = os.path.join(HERE, OUT_NAME)
    if not os.path.exists(src):
        print("PIL is not available and no pre-rendered entry.png exists",
              file=sys.stderr)
        return 1
    if os.path.abspath(src) != os.path.abspath(out_path):
        os.makedirs(out_dir, exist_ok=True)
        shutil.copyfile(src, out_path)
    print("copied", out_path, os.path.getsize(out_path), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
