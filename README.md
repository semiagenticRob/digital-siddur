# Digital Siddur

A free, offline-first iOS/Android siddur for the *Feigenbaum Weekday Siddur*
(Cohen Family Edition, Nusach Ashkenaz). Built for teens, with Hebrew / Both /
English display modes, inline commentary, highlights, and notes.

iOS is on TestFlight; Android support is in progress.

## Two tracks

- **Content** (the hard part): faithfully digitizing the print siddur into
  structured JSON, then proofing it section-by-section against the print.
  The print PDF (`feigenbaum-siddur-original.pdf`) is the sole authority for
  content — every change is verified against the actual page, not against
  training-data memory of the text.
- **App**: the Expo reading client that renders that JSON.

## Quick start

```bash
npm install
npm start        # Expo dev server (then i / a / w for ios / android / web)
npm run check    # tsc --noEmit && python3 scripts/lint_content.py --strict --errors && jest
```

One-time setup for a new clone — wires up the content linter as a pre-commit
gate:

```bash
git config core.hooksPath scripts/hooks
```

Other commands:

```bash
npm run ios          # launch in iOS simulator
npm run typecheck    # tsc --noEmit
npm test             # jest (jest-expo preset)
npm run lint:content  # content linter, full report (errors + advisory warnings)
```

Run a single test: `npx jest src/store/__tests__/preferences.test.ts` (or
`-t "name"`).

## Repo map

- `app/` — Expo Router (file-based) screens: `daven/index.tsx` (home) →
  `daven/[service].tsx` (the reader), plus `index.tsx` (redirect),
  `onboarding.tsx`, and `settings.tsx`.
- `src/content/` — the siddur content as structured JSON, loaded through
  `src/content/loader.ts`. The exact rendering contract (which segment
  fields are actually shown, header ordering, etc.) is documented in
  `docs/CONTENT_GUIDE.md` — read it before touching any `src/content/*.json`.
- `src/store/` — Zustand stores (preferences, annotations, appendix
  navigation), persisted to AsyncStorage.
- `scripts/` — content tooling: the linter (`lint_content.py`) that enforces
  `docs/CONTENT_GUIDE.md`, and the many deterministic `fix_*.py` /
  `add_*.py` scripts used to edit content JSON (content JSON is edited via
  these scripts, not by hand).
- `docs/` — `CONTENT_GUIDE.md` (rendering contract), `REVIEW_QUEUE.md`
  (deferred content decisions), `solutions/` (documented past problem/fix
  write-ups), and project plans.

For the full architecture and content-editing workflow, see `CLAUDE.md`.

## Content rights

The siddur text itself is © its rightsholders; it is included here for
digitization/proofing against the print edition and is not covered by this
repository's software license.
