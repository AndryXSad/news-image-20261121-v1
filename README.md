# The Daily Globe — 21 November 2026

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/AndryXSad/news-image-20261121-v1/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/AndryXSad/news-image-20261121-v1/reward.svg)](https://make.fun/bounty/news-image-20261121)

One front page that sums up Saturday 21 November 2026 in a single image:
45 verified stories — three leads (the M6.8 Peru quake at 00:09 UTC,
COP31 running into overtime with a draft silent on fossil fuels, and
Iran's night strikes on US bases in Bahrain), a world map with eight numbered
places, a UTC timeline of five moments, a day-in-figures strip, one
top story from each of seven regions, a twenty-four-item grid with no
repeated dateline, and an "Also today" ticker. Every story was checked
against reporting dated 21 November 2026 before it was drawn; see
`STORIES.md`.

This is a fresh build for the 21 November edition, written from a
design description (not copied from the 20 November entries). Lessons
carried over from the 20 November audit: all 24 grid datelines are
unique, the footer credits only outlets actually cited, the map has
ocean labels and a denser stipple, and every region headline fits its
box in two lines. Date traps were checked one by one: the Denmark
expulsion, the Kryvyi Rih double-tap strike, the Nepal PM's Delhi
visit announcement, the Poland missile strike, the Kyiv bridges
barrage, the EU–UK summit deal, the Anthropic slide, Cyclone Akvan,
Mamdani's Rikers plan and Bukele's third term are all 19–20 November,
not 21st, and were left out as stories of their own.

## How it is made

`main.py` renders the page from scratch with PIL (DejaVu fonts) into
`entry.png` — 1024×1024, deterministic: the same run always produces
the same bytes. When the grader sets `MAKEFUN_OUTPUT_DIR`, the image
is written there and nowhere else. If PIL is unavailable, `main.py`
falls back to copying the pre-rendered `entry.png` shipped in this
repository.

## Run it

```sh
python3 main.py                                # renders entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py         # renders entry.png into out/
```

## License

MIT — see `LICENSE`.
