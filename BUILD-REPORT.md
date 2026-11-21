# Build report — news-image-20261121 v1 ("The Daily Globe", 21 Nov 2026)

## What was built

Fresh implementation, written from a design description (not a copy of
the 20 Nov v3 renderer): a single self-contained `main.py` (PIL +
DejaVu) that renders a 1024×1024 front page. Structure follows the
winning pattern seen on the live leaderboard: front-page newspaper,
many stories, date-checked, drawn illustrations, UTC timeline,
per-region grouping, day-in-figures strip.

- 45 stories: 3 leads + 8 map places + 7 regions + 24 grid + 3 ticker.
- 3 drawn lead illustrations, all new for this edition: a seismograph
  trace for the Peru quake (M6.8, depth 129 km, 00:09 UTC), a warming
  globe with a thermometer and "FOSSIL FUELS NAMED: 0" for COP31, and
  a podium with two flags and microphones for Trump's post-trip news
  conference.
- Dark world map with 17 land polygons (Europe and Asia split, with
  a Mediterranean/Black Sea outline), a seeded 700-dot stipple ocean,
  a graticule, ocean labels, and 8 pins (minimum centre distance
  ~22 px, no overlaps).
- UTC timeline (5 moments, spine with red dots), day-in-figures strip
  (6.8, 357,000, ₹1.22 lakh cr, 0), seven regions, 24-item grid with
  all datelines unique, "Also today" ticker.
- Faint seeded paper grain (6,000 dots) and a gold rule under the
  masthead.

## Date discipline

Every story was checked against reporting dated Saturday 21 November
2026. Excluded as stories of their own (all 19–20 Nov): the Denmark
expulsion, the Kryvyi Rih double-tap strike, the Nepal PM's Delhi
visit announcement, the Poland missile strike, the Kyiv bridges
barrage, the EU–UK summit deal, the Anthropic slide, Cyclone Akvan,
Mamdani's Rikers plan, Bukele's third term, the ICJ ruling (only the
21 Nov Swiss reaction is used), South Korea's cholera case. F1 Las
Vegas qualifying and England–New Zealand rugby were still to come
when this edition was built, so only the Twickenham fixture is
carried in the ticker. See STORIES.md for the full list and the
"Deliberately NOT used" section.

## Verification (local, 21 Nov 2026 ~10:40 WIB)

- `python3 main.py` run twice + grader mode
  `MAKEFUN_OUTPUT_DIR=/tmp/v21_out4 python3 -P -s main.py`:
  byte-identical output every time.
  sha256 `ee2e1b9192ac166510684df698c62dc27e8f4dc803aba932504f7b6ae0e7b85e`
  (184,844 bytes).
- Dimensions 1024×1024 RGB — under the 1 MiB limit.
- Visual check of the rendered PNG at full size and in a leads-row
  crop: masthead, leads, map, timeline, figures, regions, grid,
  ticker and footer all legible. Three defects found on first render
  and fixed: region headlines running to three lines and touching the
  box bottom border (all seven shortened to two lines), the footer
  crediting outlets not cited in STORIES.md (replaced with the cited
  set only), and the Trump podium art reading as disconnected shapes
  (redrawn: wider podium, gold seal, two mics, flags flanking a pale
  backdrop; a LIVE bug that collided with the left flag was removed).

## Repo gates

- Repo: https://github.com/AndryXSad/news-image-20261121-v1
- README carries the 3 live make.fun badges (competition, rank,
  reward) as links to the bounty page.
- About homepage: https://make.fun/bounty/news-image-20261121;
  topic: `makefun`.
- LICENSE: canonical MIT text starting with "MIT License", no SPDX
  line on top (verified via `gh api .../license` → MIT).

## Self-judging vs the live top-50 bar

Live leaderboard, 21 Nov 2026 ~10:25 WIB: 1,740 submissions. Rank 1
at 98.9886%; rank 50 (the bar) at 98.4018%. The same layout family
scored 94.2401% on the 20 Nov edition (v1/v2, rank #4,154–4,951) and
the 19 Nov v3 pipeline reached 96.0239% (rank #10,410/15,883). This
v1 is strictly stronger than the 20 Nov v1/v2 — the date traps are
all excluded, the grid datelines are unique, the footer sources are
accurate, the illustrations are richer and the map is denser — so it
should score above 94.2401%. How far above is unknowable locally:
the jump from 94% to 98.40% means winning pairwise games this layout
family has consistently lost against the strongest reference images,
and at 185 KB it is still a flat PIL-drawn page while the top entries
run 286–743 KB with visibly richer rendering. Honest estimate:
roughly 95–97%, plausibly in the top few thousand, but NOT plausibly
clearing the 98.4018% top-50 bar. It remains a long shot; the
coordinator decides whether the slot is worth spending.

## Kit check (21 Nov 2026 ~10:50 WIB)

Ran the competition's own kit
(`/tmp/kit21/news-image-20261121-kit/cli/makefun.mjs check --kit ...
--repo . --commit HEAD`): 3 passed, 2 failed, 14 skipped, 5
checked at submission. Passes: competition_open, snapshot,
entrypoint (main.py → Python 3.13). Fails:

- **license_osi** — the kit wants an `SPDX-License-Identifier:` line
  in the root LICENSE. The LICENSE was deliberately written the
  canonical way (starting "MIT License", no SPDX line on top) because
  an SPDX line on top made GitHub's license API return NOASSERTION
  on the 20 Nov v3 repo; `gh api .../license` on this repo returns
  `{"license": "MIT"}`. The SPDX line was NOT added: the build brief
  forbids it above the text, and the kit's own fix text concedes
  GitHub may still detect the license from its text for a repository
  entry. If a future submit is attempted, the coordinator must decide
  whether to try the SPDX line at the END of the file (text still
  starts "MIT License") and re-verify both `gh api .../license` and
  the kit check — or submit as-is and let the site decide.
- **transcripts_present** — expected before submission: no bundle
  exists yet. Transcripts are bundled at submit time by the
  coordinator (this builder's session id is
  86c39386-12d4-4d63-a5b5-c40abf5190ef); re-run check with
  `--transcripts <bundle>` then. All thinking_* checks are skipped
  until transcripts exist, so no thinking_reproduces figure is
  available locally.

At-submission items: repo is public, created 21 Nov ~03:31 UTC
(after the 00:00 UTC opening), commit 52020d3 is pushed, files are
fresh work (no duplicate snapshot). Repo owner is AndryXSad, the
same GitHub login used for the accepted 20 Nov submissions.

## Submission status

NOT SUBMITTED — **NO-GO, coordinator's call**. Quota verified 21 Nov
10:21 WIB: can_submit=true, day cap 3/3 remaining. Honest estimate
95–97% vs the live top-50 bar of 98.4018% (rank 50, ~10:25 WIB);
the gap is ~1.4–3.4 points in a scale where this layout family has
scored 94.24% (20 Nov v1/v2) and 96.02% (19 Nov v3). Spending one of
the 3 remaining day slots on this entry is unlikely to reach the
prize zone. The slot is better kept for a materially richer rebuild
or a later edition. Do NOT use `makefun record` — news-image
competitions reject recorded transcripts (HTTP 400); submit via
bundle/loose-files only.
