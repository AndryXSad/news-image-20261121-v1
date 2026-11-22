#!/usr/bin/env python3
"""Render the 21 November 2026 world-news front page (1024x1024 PNG).

A newspaper front page drawn from scratch with PIL and DejaVu fonts:
a dark masthead with a DATE CHECK box, three illustrated leads (the
M6.8 Peru quake at 00:09 UTC, COP31 running into overtime with a
draft silent on fossil fuels, and Iran's night strikes on US bases
in Bahrain), a dark world map with eight numbered pins, a UTC
timeline of five moments, a day-in-figures strip, one top story
from each of seven regions, a twenty-four-item grid with no
repeated dateline, and an "Also today" ticker. 45 stories in all;
every one was checked against reporting dated Saturday
21 November 2026 before it was drawn (see STORIES.md).

Fix 2 (22 Nov 2026): the third lead is now the Bahrain night
strikes, with the El Chapo capture, the Riyadh intercept and
Zelensky's "killer" reply woven into the regions, grid, timeline
and ticker; the lead art is taller (76 px) and richer, the
figures strip has five boxes, and the map carries more stipple
and a compass rose. The Trump podium art was retired with the
lead it illustrated; Trump survives as a grid item.

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
    ("LEAD  \u2022  MIDDLE EAST",
     "Iran hits US bases in Bahrain; Gulf on edge",
     "IRGC says missiles and drones hit two Patriot radars; "
     "Bahrain reports a factory fire, no casualties.",
     "Reuters, Xinhua  \u2022  21 Nov",
     "bahrain"),
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
        ("5", 34.5, 31.5, -8, 6), ("6", 50.6, 26.2, 10, 0),
        ("7", 77.2, 28.6, 0, 0), ("8", 174.8, -41.3, 0, -2)]
KEY = ["1  JUN\u00cdN \u2014 M6.8 quake; Lima shaken; no deaths",
       "2  ANTALYA \u2014 COP31 overtime; fossil-fuel row",
       "3  WASHINGTON \u2014 Trump delays Iran-strike decision",
       "4  TALLINN \u2014 Estonia to shut Russia border crossings",
       "5  GAZA \u2014 22,000 Palestinian children dead, ministry says",
       "6  BAHRAIN \u2014 Iran hits US bases; factory fire, no dead",
       "7  NEW DELHI \u2014 Record \u20b91.22 lakh crore foreign inflow",
       "8  WELLINGTON \u2014 KL Rahul completes the SENA set"]

TIMES = [("00:09 UTC", "M6.8 quake strikes central Peru"),
         ("02:34 UTC", "BBC: RAF-base villagers to vote on 'leaving UK'"),
         ("MORNING", "Mexico captures 'El Chapo Isidro'"),
         ("AFTERNOON", "COP31 presidency promises a third draft text"),
         ("EVENING", "Iran strikes US bases in Bahrain")]

FIGS = [("6.8", "magnitude of the Peru quake"),
        ("357,000", "displaced in Yemen since August"),
        ("\u20b91.22 lakh cr", "record inflow into Indian shares"),
        ("0", "fossil fuels named in COP31 draft"),
        ("11", "killed in the Sinaloa raid")]

REGIONS = [("NORTH AMERICA", "Mexico captures 'El Chapo Isidro'"),
           ("SOUTH AMERICA", "Peru: Congress evacuated in quake"),
           ("EUROPE", "Hungary lifts block on Ukraine EU talks"),
           ("AFRICA", "Ebola hits ~100 schools in Congo"),
           ("MIDDLE EAST", "Iran strikes US bases in Bahrain"),
           ("ASIA", "Record cash floods Indian shares"),
           ("OCEANIA", "Cyclone Xavier fades over Cook Islands")]

GRID = [("KYIV", "Ukraine hits three Russian missile launchers"),
        ("SUMY", "HIMARS strike kills 20 Russian commanders"),
        ("BRUSSELS", "EU warns COP31 risks a 'fossil summit'"),
        ("LONDON", "Villagers to vote on 'leaving UK' over RAF base"),
        ("IOWA", "Army cleared to blast unstable lead azide"),
        ("CALIFORNIA", "State subpoenas Nvidia over China chip sales"),
        ("LAS VEGAS", "Antonelli fastest, but Verstappen takes pole"),
        ("WASHINGTON", "Trump: Putin 'a friend'; Zelensky: 'he's a killer'"),
        ("RIYADH", "Saudi force downs three Houthi missiles"),
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

TICKER = ("England rout New Zealand 37\u201312 at Twickenham  \u2022  "
          "Verstappen on pole in Vegas as Antonelli takes penalty  "
          "\u2022  L7 announce final Australia\u2013NZ tour")

# ---------------- illustrations ----------------
def art_quake(dr, x, y):
    """Seismograph trace: quiet line, then a violent spike, then calm,
    over a cracked street with a shaken skyline at the foot."""
    w, h = 312, 76
    dr.rectangle([x, y, x + w, y + h], fill=SLATE)
    # graticule: vertical time divisions + faint horizontals
    for gx in range(x + 28, x + w, 28):
        dr.line([(gx, y + 4), (gx, y + 58)], fill=SKY, width=1)
    for gy in (y + 14, y + 30, y + 46):
        dr.line([(x + 6, gy), (x + w - 6, gy)], fill=SKY, width=1)
    rng = random.Random(SEED + 11)
    mid = y + 30
    pts = []
    for i in range(0, w - 4, 3):
        px = x + 4 + i
        if i < 120:
            amp = rng.uniform(-2.5, 2.5)
        elif i < 200:
            amp = rng.uniform(-22, 22)
        else:
            amp = rng.uniform(-4, 4)
        pts.append((px, mid + amp))
    # glow under the trace, then the crisp white line
    dr.line(pts, fill=(96, 118, 150), width=5)
    dr.line(pts, fill=(247, 243, 232), width=2)
    # red ring + dot at the biggest jolt
    dr.ellipse([x + 148, mid - 26, x + 164, mid - 10], outline=RED,
               width=2)
    dr.ellipse([x + 152, mid - 22, x + 160, mid - 14], fill=RED)
    dr.text((x + 8, y + 5), "M6.8", font=load_font("sans_b", 16),
            fill=(247, 243, 232))
    # depth label right-aligned inside the box (was clipped at the edge)
    dr.text((x + w - 8, y + 5), "DEPTH 129 KM",
            font=load_font("sans_b", 11), fill=GOLD, anchor="ra")
    # cracked street at the foot: dark band, a jagged crack, and a
    # small skyline — one tower leaning — with lit windows
    dr.rectangle([x, y + 62, x + w, y + h], fill=(10, 14, 24))
    crack = [(x + 4, y + 62), (x + 60, y + 64), (x + 110, y + 62),
             (x + 160, y + 65), (x + 210, y + 62), (x + 260, y + 64),
             (x + w - 4, y + 62)]
    dr.line(crack, fill=(120, 130, 150), width=1)
    for bx, bw, bt in ((x + 14, 26, y + 48), (x + 252, 28, y + 50),
                       (x + 284, 18, y + 56)):
        dr.rectangle([bx, bt, bx + bw, y + 62], fill=(24, 32, 48),
                     outline=(70, 82, 104))
        for wy in (bt + 4, bt + 9):
            for wx in (bx + 4, bx + bw - 6):
                dr.rectangle([wx, wy, wx + 2, wy + 2], fill=GOLD)
    # one tower leaning over the crack
    dr.polygon([(x + 44, y + 62), (x + 48, y + 44), (x + 62, y + 48),
                (x + 58, y + 62)], fill=(24, 32, 48),
               outline=(70, 82, 104))
    dr.rectangle([x + 50, y + 50, x + 52, y + 52], fill=GOLD)
    dr.rectangle([x + 53, y + 55, x + 55, y + 57], fill=GOLD)


def star(dr, cx, cy, r, fill):
    """A small five-point star centred on (cx, cy)."""
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    dr.polygon(pts, fill=fill)


def art_cop(dr, x, y):
    """A warming globe: blue circle, land blobs, a rising thermometer
    with its mercury past the 1.5 C mark."""
    w, h = 312, 76
    # two-tone sky: pale top band, deeper below
    dr.rectangle([x, y, x + w, y + 36], fill=(226, 238, 244))
    dr.rectangle([x, y + 36, x + w, y + h], fill=SEA)
    cx, cy = x + 62, y + 38
    # soft shadow under the globe
    dr.ellipse([cx - 32, cy + 26, cx + 32, cy + 34], fill=(190, 208, 220))
    dr.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=STEEL,
               outline=INK, width=2)
    # land blobs on the globe
    dr.ellipse([cx - 21, cy - 17, cx - 2, cy - 2], fill=LANDC)
    dr.ellipse([cx + 2, cy + 2, cx + 19, cy + 19], fill=LANDC)
    dr.ellipse([cx - 6, cy + 8, cx + 8, cy + 21], fill=LANDC)
    # graticule arcs + highlight on the upper-left limb
    dr.arc([cx - 30, cy - 30, cx + 30, cy + 30], 200, 340, fill=MAPLINE,
           width=1)
    dr.ellipse([cx - 13, cy - 30, cx + 13, cy + 30], outline=MAPLINE)
    dr.arc([cx - 30, cy - 30, cx + 30, cy + 30], 150, 260,
           fill=(220, 235, 245), width=2)
    # two thin cloud swirls
    dr.arc([cx - 19, cy - 11, cx + 2, cy + 4], 200, 340,
           fill=(247, 247, 247), width=2)
    dr.arc([cx - 4, cy + 6, cx + 17, cy + 19], 20, 160,
           fill=(247, 247, 247), width=2)
    # thermometer, mercury climbing past the 1.5 C mark, tick marks
    tx = x + 148
    dr.rectangle([tx, y + 8, tx + 12, y + 58], fill=PANEL, outline=INK,
                 width=1)
    dr.rectangle([tx + 2, y + 14, tx + 10, y + 56], fill=RED)
    dr.ellipse([tx - 3, y + 52, tx + 15, y + 70], fill=RED, outline=INK)
    for ty in (y + 14, y + 26, y + 38, y + 50):
        dr.line([(tx - 3, ty), (tx, ty)], fill=INK, width=1)
    for ty, lab in ((y + 8, "1.5\u00b0C"), (y + 28, "1.0\u00b0C"),
                    (y + 48, "0.5\u00b0C")):
        dr.text((tx + 18, ty), lab, font=load_font("sans", 9), fill=INK)
    # the zero that matters: no fossil fuels named (right-aligned:
    # the old "NAMED: 0" ran past the panel's right edge)
    dr.text((x + 216, y + 8), "FOSSIL FUELS", font=load_font("sans_b", 11),
            fill=INK)
    dr.text((x + w - 8, y + 26), "NAMED: 0", font=load_font("sans_b", 17),
            fill=RED, anchor="ra")
    dr.text((x + 216, y + 50), "in the draft text",
            font=load_font("sans", 10), fill=GRAY)


def art_bahrain(dr, x, y):
    """Missiles over the Gulf at night: a Manama skyline under
    ascending trails and interceptor bursts, crescent moon above.

    Two accounts of the night are kept apart in the words: the IRGC
    says it hit two US Patriot radars; Bahrain says a factory
    burned. The picture shows the attack itself, not the claims."""
    w, h = 312, 76
    # night sky: a dark gradient, band by band (deterministic)
    top, bot = (10, 16, 34), (34, 56, 96)
    for i in range(h):
        t = i / (h - 1)
        col = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        dr.line([(x, y + i), (x + w, y + i)], fill=col)
    # stars (seeded) + a crescent moon, top right
    rng = random.Random(SEED + 41)
    for _ in range(42):
        sx = x + rng.randint(4, w - 8)
        sy = y + rng.randint(3, 44)
        if sx < x + 132 and sy < y + 18:
            continue  # keep the top-left label clear of stars
        dr.point((sx, sy), fill=(247, 243, 232))
    dr.ellipse([x + 284, y + 4, x + 302, y + 22], fill=(240, 234, 210))
    dr.ellipse([x + 289, y + 2, x + 305, y + 20], fill=(22, 32, 60))
    # Manama skyline silhouette along the foot, with lit windows
    dr.rectangle([x, y + 58, x + w, y + h], fill=(8, 12, 24))
    sky = [(x + 6, 22), (x + 34, 30), (x + 58, 18), (x + 86, 34),
           (x + 112, 24), (x + 140, 32), (x + 168, 20), (x + 196, 30),
           (x + 224, 16), (x + 252, 28), (x + 282, 22)]
    for bx, bt in sky:
        dr.rectangle([bx, y + 58 - bt, bx + 22, y + 58], fill=(8, 12, 24),
                     outline=(52, 66, 96))
    # twin towers with wind turbines between them (Bahrain WTC)
    dr.rectangle([x + 224, y + 58 - 16, x + 238, y + 58],
                 fill=(8, 12, 24), outline=(52, 66, 96))
    dr.rectangle([x + 244, y + 58 - 16, x + 258, y + 58],
                 fill=(8, 12, 24), outline=(52, 66, 96))
    for ty in (y + 44, y + 50):
        dr.ellipse([x + 238, ty, x + 244, ty + 5], outline=GOLD)
    # a minaret, left of the towers
    dr.polygon([(x + 200, y + 58), (x + 203, y + 30), (x + 206, y + 58)],
               fill=(8, 12, 24), outline=(52, 66, 96))
    # lit windows, seeded
    wr = random.Random(SEED + 43)
    for _ in range(46):
        wx = x + wr.randint(8, w - 12)
        wy = y + wr.randint(30, 56)
        dr.point((wx, wy), fill=GOLD)
    # sea strip at the very foot, with a small patrol ship
    dr.rectangle([x, y + 70, x + w, y + h], fill=(16, 32, 56))
    dr.polygon([(x + 96, y + 70), (x + 128, y + 70), (x + 122, y + 75),
                (x + 102, y + 75)], fill=(8, 12, 24))
    dr.line([(x + 112, y + 70), (x + 112, y + 62)], fill=(8, 12, 24),
            width=2)
    # two ascending missile trails: a faint glow, then a bright core
    for p0, p1, p2 in (((x + 92, y + 58), (x + 136, y + 32),
                        (x + 180, y + 14)),
                       ((x + 216, y + 58), (x + 232, y + 36),
                        (x + 248, y + 20))):
        dr.line([p0, p1, p2], fill=(120, 110, 70), width=5)
        dr.line([p0, p1, p2], fill=(247, 238, 190), width=2)
    # interceptor bursts where the trails end: irregular ray bursts
    # with sparks, not tidy suns
    for bx, by in ((x + 180, y + 14), (x + 248, y + 20)):
        dr.ellipse([bx - 9, by - 9, bx + 9, by + 9],
                   fill=(226, 120, 40))
        for k, rl in enumerate((15, 11, 16, 10, 14, 12, 15, 11)):
            ang = k * math.pi / 4 + 0.3
            ex = bx + rl * math.cos(ang)
            ey = by + rl * math.sin(ang)
            dr.line([(bx, by), (ex, ey)], fill=(240, 160, 60), width=2)
        dr.ellipse([bx - 4, by - 4, bx + 4, by + 4],
                   fill=(247, 243, 232))
        sr = random.Random(SEED + 47 + bx)
        for _ in range(6):
            sx = bx + sr.randint(-20, 20)
            sy = by + sr.randint(-16, 16)
            dr.point((sx, sy), fill=(240, 160, 60))
    dr.text((x + 8, y + 5), "BAHRAIN \u2014 SAT NIGHT",
            font=load_font("sans_b", 9), fill=(247, 243, 232))


ART = {"quake": art_quake, "cop": art_cop, "bahrain": art_bahrain}

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
    for _ in range(16000):
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
        draw_block(dr, x, 266, deck, load_font("sans", 12), colw, INK,
                   leading=13)
        dr.text((x, 308), src, font=load_font("sans", 11), fill=GRAY)
    hline(dr, 28, 996, 322, 2)

    # ---------- dark world map + key ----------
    tag(dr, 28, 328, "THE WORLD \u2014 EIGHT PLACES IN THE NEWS", 13)
    dr.rectangle([MX, MY, MX + MW, MY + MH], fill=MAPBG, outline=INK,
                 width=1)
    # stippled ocean (seeded: identical every run), drawn before land
    rng = random.Random(SEED)
    for _ in range(2500):
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
    for _ in range(900):
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
    # compass rose in the open South Atlantic
    ccx, ccy = MX + 232, MY + 100
    dr.ellipse([ccx - 11, ccy - 11, ccx + 11, ccy + 11], outline=MAPLINE,
               width=1)
    dr.polygon([(ccx, ccy - 10), (ccx + 3, ccy), (ccx, ccy + 10),
                (ccx - 3, ccy)], fill=(247, 243, 232))
    dr.text((ccx, ccy - 19), "N", font=load_font("sans_b", 9),
            fill=(247, 243, 232), anchor="ma")
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
        x = 28 + i * 194
        dr.rectangle([x, 560, x + 184, 606], fill=PANEL, outline=INK,
                     width=1)
        dr.line([(x, 560), (x + 184, 560)], fill=RED, width=3)
        dr.text((x + 10, 566), num, font=load_font("serif_b", 18),
                fill=INK)
        dr.text((x + 10, 590), lab, font=load_font("sans", 10), fill=GRAY)
        # tiny chart at the right of each box
        gx0, gy0 = x + 136, 570
        if i == 0:  # quake: mini seismograph zigzag
            zr = random.Random(SEED + 31)
            zpts = [(gx0 + k * 4, gy0 + 8 + zr.uniform(-7, 7))
                    for k in range(10)]
            dr.line(zpts, fill=RED, width=1)
        elif i == 1:  # displaced: three rising bars
            for b, bh in enumerate((6, 10, 15)):
                dr.rectangle([gx0 + b * 12, gy0 + 16 - bh,
                              gx0 + b * 12 + 8, gy0 + 16], fill=STEEL)
        elif i == 2:  # inflow: rising line with arrowhead, kept clear
            # of the long "1.22 lakh cr" figure: it starts further right
            dr.line([(gx0 + 12, gy0 + 14), (gx0 + 36, gy0 + 2)],
                    fill=STEEL, width=2)
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
    draw_block(dr, 28, 986,
               "The Daily Globe  \u2022  Saturday 21 November 2026  "
               "\u2022  45 stories, every one first reported 21 Nov 2026",
               load_font("sans", 11), 968, GRAY, center=True)
    draw_block(dr, 28, 1000,
               "Sources: Reuters, AFP, BBC, Xinhua, Asia Today, "
               "The News PK, EIN Presswire, USGS",
               load_font("sans", 10), 968, GRAY, center=True)
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
