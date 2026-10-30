# Print fidelity check

Letter-for-letter comparison of the app's content with `feigenbaum-siddur-original.pdf`
(the sole authority). Hebrew and English, nikud and punctuation included.

## Setup (once)

```bash
python3 -m venv .venv-fidelity && .venv-fidelity/bin/pip install -r scripts/fidelity/requirements.txt
```

## Run

```bash
cd scripts/fidelity
../../.venv-fidelity/bin/python fidelity.py            # counts per section (~20s, whole book)
../../.venv-fidelity/bin/python report.py              # docs/fidelity/SUMMARY.md, findings/, ledger.json
../../.venv-fidelity/bin/python missing.py             # docs/fidelity/missing-from-app.md
../../.venv-fidelity/bin/python test_mutation.py 80    # proof: planted errors must all be caught
../../.venv-fidelity/bin/python crop.py <finding id>   # print image of any finding
```

## How it works

1. **Print extraction from glyph geometry** (`pdftext.py`). The PDF's own text layer
   puts some Hebrew lines in visual word order and scrambles letter+mark ligatures in
   the commentary font, so text is rebuilt from the drawing trace:
   - a ligature continuation (glyph id -1) belongs to the glyph before it; a standalone
     vowel mark belongs to the next letter drawn (marks whose letter is in the next
     drawing run carry over; any left over are placed by position);
   - lines are read by position (Hebrew right-to-left; English left-to-right with
     embedded Hebrew runs reversed per Unicode bidi rules);
   - word spaces come from ink gaps (>0.125em, or >=0.075em where a space glyph is
     drawn — never next to a dash, where spaces are kerned away), measured over the
     whole book;
   - text flows are separated by typeface class and size (sidebar / intro / commentary),
     read column by column, continuing across pages.
2. **App side** (`fidelity.py`): every rendered field, markdown stripped, with each
   character mapped back to its offset in the JSON string.
3. **Matching**: each field is located by anchor voting, the best of several candidate
   spans is chosen by real alignment, matches below 50% are rejected rather than
   diffed, and spans extend to whole words.
4. **Coverage**: print text that no field claimed is reported (`missing.py` splits it
   into missing / present elsewhere in the app / heavily changed).

### What counts as "the same" (identical on both sides)

Only encoding differences that cannot be seen in print: Unicode canonical form and mark
order; invisible controls (soft hyphen, bidi marks); hair/thin spaces; Latin ligature
glyphs; whitespace runs; a cholam stored on the letter before a bare vav vs on the vav.
Everything visible — letters, nikud, meteg, maqaf, punctuation, quote style, dashes,
case, word spacing — is compared. A hyphen or space at a line break after `-`, `/` or a
dash is not counted (it cannot be seen in print).

### Applying corrections

- `apply_english.py [--apply]` — English differences the print decides, only when safe
  (English on both sides, strong match, local, not next to Hebrew, not touching links
  or markdown, not a page reference the app deliberately rewrote, not a likely print
  typo). Everything else is listed in `docs/fidelity/english-held.json`.
- `apply_divine_name.py` / `apply_divine_name_from_print.py` — the Divine Name as
  printed (יְהֹוָה), checked token by token against the print.
- Other Hebrew differences are never changed automatically: they wait for the rav
  (`decision: rav-review` in `docs/fidelity/ledger.json`).

### Ledger

`docs/fidelity/ledger.json` maps each finding's fingerprint to a decision. Set
`"by": "human"` with a decision (`accepted`, `fix`, `print-typo`, ...) and re-runs keep it.
