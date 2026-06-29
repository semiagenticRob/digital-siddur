# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ Expo has changed — check the versioned docs

This project is on **Expo SDK 56 / React Native 0.85 / React 19 / Expo Router v4**, which differs from older Expo APIs in your training data. Read the exact versioned docs at https://docs.expo.dev/versions/v56.0.0/ before writing app/runtime code. (`AGENTS.md` carries this same note.)

## What this is

A free, offline-first iOS/Android siddur for the *Feigenbaum Weekday Siddur* (Cohen Family Edition, Nusach Ashkenaz). Built for teens, with Hebrew / Both / English display modes, inline commentary, highlights, and notes. GitHub: `semiagenticRob/digital-siddur`.

There are **two tracks**, and most work is on the first:
- **Content** (the hard part): faithfully digitizing the print siddur from `feigenbaum-siddur-original.pdf` into structured JSON, then proofing it section-by-section against the print. Content fidelity is the highest-stakes risk — no real liturgical text ships without author + rav sign-off.
- **App**: the Expo reading client that renders that JSON.

## Commands

```bash
npm start            # Expo dev server (then i / a / w for ios / android / web)
npm run ios          # launch in iOS simulator
npm run typecheck    # tsc --noEmit
npm test             # jest (jest-expo preset)
npm run lint:content # content linter, full report (errors + advisory warnings)
npm run check        # typecheck + strict content lint + jest — run before committing
```

Run a single test: `npx jest src/store/__tests__/preferences.test.ts` (or `-t "name"`).

Render a PDF page for proofing: `pdftoppm -png -r 300 -f <pg> -l <pg> feigenbaum-siddur-original.pdf out -singlefile`. **`pdf_page = siddur_page + 24`.** To locate a section/header in the PDF, use the **Table of Contents** (front matter, pdf p.5–6): it lists every section's exact *siddur* page. Don't grep the body text for a header — it matches commentary and running-headers; the TOC is authoritative for "which page."

## App architecture

Expo Router (file-based) in `app/`: `index.tsx` (home) → `daven/[service].tsx` (the reader) plus `onboarding.tsx` and `settings.tsx`. `_layout.tsx` loads fonts (Frank Ruhl Libre = Hebrew, Newsreader = English serif, Inter = UI).

- **Content registry** — `src/content/loader.ts` statically imports every service JSON into a `Record<string, Service>`; `getService(id)` / `listServices()` are the entry points. Appendices load separately via `src/content/appendices.ts`. Adding a service = add the JSON + register it in `loader.ts`.
- **Reader** — `daven/[service].tsx` renders the service through a FlashList (`ServiceScroll`), one `SegmentRenderer` per segment.
- **State** — Zustand stores in `src/store/`, persisted to AsyncStorage: `preferences` (displayMode `he`/`both`/`en`, theme, fontStep, comfortLevel, onboarding flag), `annotations` (highlights + notes keyed by segment id), `appendix` (modal nav). Theme tokens in `src/theme/`.

## Content model & the rendering contract (read before touching any `src/content/*.json`)

Hierarchy: **`Service → Group → Prayer → Segment[]`** (appendices hold `Segment[]` directly). Types live in `src/content/types.ts`.

The critical, non-obvious rule: **each segment `type` renders only some of its fields — data in a field a type doesn't render is silently invisible.** This is the most common content bug.

| type | renders | invisible field |
|---|---|---|
| `prayer` | `heText` only (Hebrew, RTL) | `enText` |
| `commentary` / `insight` / `faq` | `enText` only (RichText markdown) | **`heText`** |
| `section_intro` / `transition` | `enText`, centered | `heText` |
| `rubric` | `heText` plain text (`*` literal) in he/both; else `enText` via **RichText** (markdown + links) in en | the other field |
| `header` | `heText` and/or `enText` | — |

Header order and display verses are **per-PDF, never a blanket default**:
- **`display: true`** (prayer only) → oversized & centered, enlarging the *whole* segment. Used for verses the print sets large+centered (Kedushah climaxes; the chasimos of the six framework Amidah brachos). To enlarge only a closing chasimah inside a longer prayer, **split the segment** so the chasimah is its own `display` prayer — `display` can't keep a small inline label/parenthetical small (a known renderer limit; same reason inline Kedushah speaker-tags can't sit on a display verse).
- Headers default **Hebrew-on-top** (the print's majority). **`enTop`** = English-on-top, set ONLY where the PDF prints the English first — **verify each at its TOC page**, there is no derivable rule (catchy English titles like "OUR REQUESTS" / "My Body Works!" are English-first; formal-Hebrew-name sections like שֵׁשׁ זְכִירוֹת / לְדָוִד ה׳ are Hebrew-first with the English as a *subtitle*). `enPrimary` = big English title over a small Hebrew name-list.

So: cited Hebrew lemmas go **inline at the start of `commentary.enText`** (bold, em-dash separated: `**לֶמָּא**—gloss`), never in `commentary.heText`. Parentheticals are italic. Connective/bridge lines are `section_intro` (centered), not boxed `commentary`. **Derive Hebrew by slicing existing strings — never retype it** (retyping drops nikud/letters).

The full contract, conventions, and proofing workflow are in **`docs/CONTENT_GUIDE.md`** — the source of truth that `scripts/lint_content.py` enforces. If you change a rendering rule in `SegmentRenderer.tsx`, update the guide and the linter together.

## Content tooling & workflow

- **Linter** (`scripts/lint_content.py`) encodes the table above. Errors (block commits): stranded `commentary.heText`, `*` in rubric.heText, unbalanced markdown (incl. rubric `enText`), empty `prayer.heText`. Warnings are advisory (unbolded lemma, lemma-not-found-in-prayer garble detector, etc.).
- **Pre-commit gate**: `scripts/hooks/pre-commit` runs the strict linter. Wired via `core.hooksPath` — **new clones must run `git config core.hooksPath scripts/hooks` once.** Bypass with `git commit --no-verify`.
- **Edit JSON via deterministic Python scripts in `scripts/`**, not by hand — each asserts its target exists before editing, so a stale assumption fails loudly instead of corrupting text. Verify formatting changes by stripping markdown (`**`/`*`) and diffing against the current text so wording can't drift. The many `fix_*.py` scripts are the record of past section fixes; follow their pattern.
- **Proactive per-section audit** before asking for human review: `python3 scripts/audit_prep.py <file.json> <prayer-id> <siddur-start> <siddur-end>` renders the print pages and dumps segments, then dispatch vision subagents to diff app-vs-print. **Vision agents are unreliable for two dimensions specifically — visual size (`display`) and header order — they both over- and under-report there.** Verify every display-flag and header-order call, plus all Hebrew-letter/word changes, **by hand at 300 DPI** on the TOC-located page. Treat agent output as a lead, not a verdict.
- **Editing Hebrew: derive by slicing, match nikud-insensitively.** When splitting/relocating a lemma or chasimah, slice it from the existing string (retyping drops nikud). To locate a split/replace point in vocalized Hebrew, match on the **consonant skeleton** (strip U+0591–U+05C7) and map back to the raw index — typed nikud rarely byte-matches the stored text.
- **`docs/REVIEW_QUEUE.md`** tracks intentionally-deferred items (e.g. the siddur-wide Divine Name spelling, held for rav sign-off; masoretic maqaf in Torah passages). Check it before "finishing" a section.
- **`docs/solutions/`** — documented solutions to past problems (bugs, conventions, workflow patterns), organized by category with YAML frontmatter (`module`, `tags`, `problem_type`). Relevant when implementing or debugging in a documented area.

## Plan

`docs/superpowers/plans/2026-06-15-digital-siddur-v1.md`.
