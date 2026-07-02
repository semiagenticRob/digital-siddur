# Home Page Reorganization + Book Matter Integration — Design

**Date:** 2026-07-02
**Status:** Approved direction (Variant A chosen from mockup comparison); spec pending user review
**Mockups:** served from session scratchpad `mockups/` (Variant A = chosen layout; About + Glossary screens shared)

## Goal

Replace the flat 14-item home list with a purpose-grouped layout ("Variant A: Now Card + Grouped Scroll") that:

1. Groups services by how they're actually used (daily tefillos vs. special days vs. after eating vs. anytime).
2. Reserves a **"now" zone** at the top for future smart surfacing + zmanim — **designed and specced this round, not built**.
3. Brings the book's non-prayer material in-app: an **About this Siddur** screen (introductions, notes, dedications, acknowledgments) and a **browsable Glossary**.

Appendices 1–12 stay reachable only via inline links (user decision — no browsable hub).

## What ships this round vs. what is planned only

| | This round | Planned (next round) |
|---|---|---|
| Grouped home sections | ✅ build | — |
| Now card: civil + Hebrew date, "Continue where you left off" | ✅ build | — |
| Now card: suggested current service, "Daven now" CTA | ❌ | clock + Hebrew-calendar rules |
| Zmanim strip on the now card | ❌ | location permission + zmanim engine |
| "Today/Tonight" badges promoting Special Days entries | ❌ | Hebrew-calendar rules |
| About this Siddur screen + digitized front/back matter | ✅ build | — |
| Browsable Glossary (digitized from print) | ✅ build | — |

The now card is the **designated mount point** for the future CTA row and zmanim strip; it currently renders only the date line and resume link, and will extend downward as those features land rather than reserving their space in advance.

## Home screen (`app/daven/index.tsx`)

Order, top to bottom:

1. **Header** — unchanged: "Daven", bookmark (Notes & Highlights), gear (Settings).
2. **Now card** — surface card, 3px gold top border, rounded 16.
   - Row 1: `Wednesday · July 2` (left, muted) / Hebrew date in Frank Ruhl (right, RTL).
   - Row 2 (this round): **Continue** link — "Resume Shacharis →" (service-only) from the persisted `lastServiceId`; hidden if no service has been opened yet.
   - Future rows (space reserved, not rendered): suggested-service title + "Daven now" CTA; zmanim strip (4 cells: Krias Shema / Minchah Gedolah / Shkiah / Tzeis) as a full-bleed footer inside the card.
3. **Tefillos** — Shacharis, Minchah, Maariv. Full-size rows (current row style).
4. **Special Days** — Sefiras HaOmer, Maariv for Motzaei Shabbos, Mussaf for Rosh Chodesh, Mussaf for Chol Hamoed, Hallel, Netilas Lulav. Compact rows. Static order this round; future calendar logic adds badges/promotion but **never hides** an entry.
5. **After Eating** — Birkas HaMazon, Al HaMichyah, Borei Nefashos. Compact rows.
6. **Anytime** — Tefillas HaDerech, Krias Shema al HaMitah. Compact rows.
7. **From the Book** — two side-by-side cards: **About this Siddur** → `/about`; **Glossary** → `/glossary`.

Section labels: 11px uppercase letterspaced muted (same treatment as Notes screen section labels).

### Category data

New `src/content/categories.ts`: a static ordered list of `{ key, label, serviceIds[] }` consumed by the home screen. Service ids must exist in the loader registry (a unit test asserts every registered service appears in exactly one category, so adding a service without categorizing it fails loudly).

## About this Siddur screen (`app/about/index.tsx`)

Standalone stack screen (same pattern as `notes.tsx`: back link + title). Subtitle: "The Feigenbaum Siddur · The Cohen Family Edition · Nusach Ashkenaz · By Rabbi Yitzchak Feigenbaum · Mosaica Press".

TOC rows grouped for a reader (not print order):

- **Read First** — "But I Don't Do Davening!" (Introduction for Teens); "How to Read the Translation" (the *Note Regarding This "Translation"* — italics convention; ברוך/קדוש/שם translation choices).
- **For Parents & Teachers** — Introduction for Parents, Mechanchim, and Mechanchos; A Personal Note from Rabbi Feigenbaum (both notes, pp. 239–240).
- **The People Behind It** — Dedications (Cohen Family Edition memorial, Sara Goldman, Tobias tribute, ואלו יעמדו על הברכה); Acknowledgments.

Tapping a row pushes a stack screen `app/about/[piece].tsx` that renders the piece's `Segment[]` with the shared `ProseSegments` prose renderer (extracted from AppendixModal) (not a modal — these are long-form reads). The pieces are `section_intro`/`commentary`-style English prose with occasional inline Hebrew.

### Content model

New `src/content/book-matter.json`: `{ pieces: [{ id, title, subtitle?, segments: Segment[] }] }` + `src/content/bookMatter.ts` accessor (mirror of `appendices.ts`). Digitized from pdf pp. 7–24 (dedications, acknowledgments, both introductions incl. translation note) and siddur pp. 239–240 (personal notes), **proofed against the print per the content workflow** (deterministic scripts, lint, PDF verification). The teen intro and translation note contain inline Hebrew phrases — derive by slicing from `pdftotext` output, verify nikud against the page render.

## Glossary screen (`app/glossary.tsx`)

The print glossary (siddur p. 269 ff.) is ~70 entries of `term — definition` in **transliteration only (no Hebrew script column)** — the screen follows the print: no Hebrew column, unlike the early mockup.

- New `src/content/glossary.json`: `{ entries: [{ term, definition }] }`, print order preserved within letter; grouped by first letter at render time.
- Screen: back link + title + one-line subtitle ("Hebrew terms used throughout the translations"), alphabet jump bar (only letters that exist), letter-grouped list of entry cards (term semibold, definition in Newsreader).
- Jump bar taps scroll to the letter section (SectionList `scrollToLocation`).

## Data / store changes

- **Resume line:** service-only — "Resume Shacharis →" from a new persisted
  `lastServiceId` in the reading-position store (the offset restore already
  works on open). Prayer-level naming ("…at Ashrei") needs a viewability
  callback through FlashList and is deferred as polish.
- **Hebrew date:** hand-rolled converter in `src/lib/hebrewDate.ts` (Dershowitz–Reingold
  algorithm, ~100 lines, tested against Hebcal converter-API reference values). We cannot
  bundle `@hebcal/core` (GPL-2.0) or `kosher-zmanim` (LGPL-3.0): the app ships copyrighted
  book content that can never be open-sourced. `Intl` Hebrew-calendar support on Hermes is
  unverifiable in jest, so it is not an option either.

## Future plan (documented, not built): smart surfacing + zmanim

- **Zmanim source:** Hebcal hosted Zmanim REST API — free, no API key, JSON, batch up to
  180 days (`https://www.hebcal.com/zmanim?cfg=json&latitude=..&longitude=..&tzid=..&start=..&end=..`).
  Output is CC-BY 4.0: the app must credit Hebcal.com (Settings/About line). Offline-first:
  prefetch a 30-day batch when online, cache in AsyncStorage, render from cache; no
  cache + no network → strip hidden. Suggested-service rules run on the same cached data
  plus the local Hebrew-date converter.
- Promotion rule: a relevant Special Days entry gets a badge and moves to the top of its section — it never leaves the section, and nothing is ever hidden.

## Testing

- `categories.test.ts`: every loader service in exactly one category; no unknown ids.
- Glossary grouping util test (letter grouping, jump-bar letters).
- Existing suites unaffected (`npm run check` green).
- Content: new JSON passes `lint_content.py`; book-matter + glossary proofed against print pages before merge.

## Explicitly out of scope this round

Zmanim computation, location permission, suggested-service logic, Today badges, any reader-screen changes, appendix browsing hub (permanently out per user decision).
