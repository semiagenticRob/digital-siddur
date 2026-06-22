# Content Guide — the rendering contract

How siddur content must be authored so it renders correctly and matches the
print. This file is the source of truth the linter (`scripts/lint_content.py`)
enforces. If you change a rendering rule in `SegmentRenderer.tsx`, update this
file and the linter together.

## Schema

`Service → Group → Prayer → Segment[]` (appendices hold `Segment[]` directly).
A `Segment` has a `type` and the fields `heText` / `enText` (plus `condition`,
`xref`, `enPrimary`, `plain`, `optional`, `display`).

## What each segment type actually renders

This is the part that bites. A field that a type doesn't render is **invisible**
— data put there is silently lost.

| type | renders | ignores | notes |
|---|---|---|---|
| `prayer` | `heText` only | `enText` | hidden in English-only mode; right-aligned RTL. With `display: true` → oversized & centered (Kedushah climax verses) |
| `commentary` | `enText` only (RichText) | **`heText`** | hidden in Hebrew-only; the EXPLANATION box |
| `insight` | `enText` (RichText) | `heText` | collapsible "Insight" |
| `faq` | `enText` (RichText) | `heText` | collapsible "FAQ" |
| `section_intro` | `enText` (RichText) | `heText` | **centered**; the bridge/preamble style |
| `transition` | `enText` | `heText` | centered, glowing bridge |
| `rubric` | `heText` if present else `enText` — **plain `Text`, NOT markdown** | the other field | a rubric with both fields only shows in "both" mode |
| `header` | `heText` and/or `enText` | — | **English caps label on top, Hebrew title beneath** (default). `enPrimary` = big English title over small Hebrew subtitle. `heTop` = keep Hebrew first (English is a mere transliteration). `plain` = quiet incipit. |

## Conventions (matched to the print)

1. **Lemmas live inline in the gloss, never in `commentary.heText`.** Commentary
   renders `enText` only. Put the cited Hebrew at the start of `enText`, em-dash
   separated. `heText` on a commentary is a bug (the Hebrew won't show).
2. **Lemmas are bold; parentheticals are italic.** The print bolds every cited
   Hebrew run before an em-dash (`**לֶמָּא**—gloss`) and italicizes asides
   (`*(like this)*`). Emphasized English words are sometimes bold too (e.g.
   "Hashem **is** קדוש", "in **all** worlds").
3. **Em-dash, no surrounding space** is the lemma separator (`לֶמָּא—gloss`).
   (Some legacy text uses `לֶמָּא — gloss`; acceptable but not preferred.)
4. **Bridges are `section_intro`, not `commentary`.** A connective line ("Next,
   the Torah tells us:", "…Therefore, we continue:") is centered in the print,
   not a boxed explanation.
5. **Rubrics carry no markdown.** They render as plain text, so `*…*` shows
   literal asterisks. Hebrew speaker labels stay Hebrew (חזן / קהל), set inline
   in the prayer's `heText` where the print does (cf. Barchu, Hallel).
6. **Derive Hebrew, never retype it.** When splitting/moving a lemma, slice it
   from the existing prayer string. Retyping drops nikud/letters (the Atah Hu
   missing-vav bug).
7. **PDF page = siddur page + 24.** `pdftoppm -png -r 300 -f N -l N file.pdf out`.

## The linter

`scripts/lint_content.py` encodes the table + conventions above.

- `npm run lint:content` — full report (errors + advisory warnings).
- `npm run lint:content:strict` — exit 1 on error-severity findings (the gate).
- Errors (block commits): stranded `commentary.heText`, `*` in rubrics,
  unbalanced markdown, empty `prayer.heText`.
- Warnings (advisory): unbolded lemma, lemma-not-found-in-prayer (garble
  detector — consonant-level), bridge-looks-like-commentary, dead `prayer.enText`.

A **pre-commit hook** (`scripts/hooks/pre-commit`, wired via `core.hooksPath`)
runs the strict gate. Bypass with `git commit --no-verify`. New clones must run
`git config core.hooksPath scripts/hooks` once.

## Proactive per-section audit (before human review)

Don't wait to be told a section is wrong. Before reviewing a section:

1. `python3 scripts/audit_prep.py <file.json> <prayer-id> <siddur-page-start> <siddur-page-end>`
   — renders the print pages to `/tmp/audit/` and dumps the app segments.
2. Dispatch parallel vision subagents: each reads a rendered page + the segment
   dump and reports discrepancies (missing Hebrew, missing/wrong words,
   formatting gaps, mis-segmentation). Mark up *existing* text — don't retype.
3. Verify any agent edits by stripping markdown and diffing against the current
   text (so wording can't drift); apply; re-lint; `npm run check`.

This shifts the human from *detector* to *adjudicator* of the subtle calls.
