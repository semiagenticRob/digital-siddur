---
title: "Carve-out optional boxing follows the print's two-tier treatment, not blanket-applied to all conditional liturgy"
date: 2026-06-30
category: conventions
module: content-corpus
problem_type: convention
component: documentation
severity: medium
applies_when:
  - "Adding or auditing `optional: true` on any liturgical segment"
  - "Writing a RUNS entry in a carve-out script (fix_carveout_optional.py pattern)"
  - "Adding new conditional/seasonal liturgy to a service JSON"
  - "Deciding whether a conditional insert should render boxed vs inline"
tags:
  - optional-flag
  - conditional-liturgy
  - pdf-fidelity
  - carveout
  - rendering-contract
  - inline-insert
  - shaded-box
  - siddur-content
---

# Carve-out `optional` boxing follows the print's two-tier treatment, not blanket-applied to all conditional liturgy

## Context

The corpus-wide carve-out pass (`scripts/fix_carveout_optional.py`) set `optional: true` on every conditional/seasonal insert across all services (64 runs, 215 segments), so each renders as a shaded box. That was correct for the *majority* — but a PDF-fidelity review (per-page verification of all runs) found it **over-boxed short inline inserts** that the print does **not** shade. The correction (`scripts/fix_carveout_pdf_corrections.py`) un-boxed them. The lesson: *conditional ≠ boxed*. The print uses two distinct treatments, and only one maps to `optional: true`.

## Guidance

Before setting `optional: true`, decide which tier the insert is — **by looking at its print page**, not by whether it's "conditional":

**Tier 1 — the print SHADES/boxes it → `optional: true`.**
Substantial added prayers / full conditional inserts: Al HaNissim (Chanukah/Purim), Yaaleh V'Yavo (Rosh Chodesh/Chol Hamoed), the Aseres Yemei Teshuvah additions (Zachreinu, Mi Chamocha, Uchsov, B'Sefer Chaim), Aneinu, the per-festival korbanos selectors, "some add"/"one may insert" tefillos, Avinu Malkeinu verse groups.

**Tier 2 — the print renders it INLINE (parenthetical / compact occasion-label) → leave `optional` unset.**
Short conditional fragments the print keeps in the running text of a bracha: a leap-year parenthetical, the compact occasion labels in a short bracha (Al HaMichyah's `בְּשַׁבָּת: …` / `בר״ח: …` / `ביו״ט: …`), or a single-word substitution (the AYT `הַמֶּלֶךְ הַקָּדוֹשׁ` swap). These are conditional, but the print sets them inline — boxing them adds visual chrome the print doesn't have.

**Decision procedure:** locate the insert via the TOC (`pdf_page = siddur_page + 24`), render the page (`pdftoppm -png -r 300 -f <pg> -l <pg> feigenbaum-siddur-original.pdf out -singlefile`), and check: does the print shade/box this insert, or set it inline? Shade → `optional: true`. Inline → leave it out. **Matching the PDF is primary; shacharit's carve-out style is the template but yields to the PDF for any specific segment.**

**Renderer note (why a stray `optional` matters):** `flattenService` in `ServiceScroll.tsx` merges *contiguous* `optional` segments into one connected shaded box (via `pos: solo|start|mid|end` → `optionalSolo/Start/Mid/End` styles). So an over-flagged inline insert doesn't just get its own box — it visually fuses with adjacent boxed inserts. Any segment that shouldn't be boxed must have `optional` absent/false.

## Why This Matters

PDF fidelity is this project's top-priority content constraint — the print is the sole authority. Over-boxing a Tier-2 insert diverges from the print twice over: it adds a gray box the print lacks, and it visually isolates a word/phrase the print deliberately keeps in the bracha's running flow, misrepresenting how the liturgy is set. A teen davening with the app would see a layout that doesn't match the siddur in their hands.

## When to Apply

Any time you set `optional: true`, write a carve-out `RUNS` entry, add conditional liturgy, or audit existing carve-outs. Verify the insert's treatment against its actual print page first.

## Examples

**Tier 1 — correctly boxed** (from `fix_carveout_optional.py` RUNS, kept `optional: true`):
```python
'src/content/minchah.json': [
  ['min3-avodah-yaaleh-veyavo-rubric', ...,'min3-avodah-yaaleh-veyavo-commentary'],  # Yaaleh V'Yavo
  ['al-hanissim-rubric', ..., 'al-hanissim-purim-c1'],                                # Al HaNissim
  ['min2-rubric-aseres-yemei-avos','min2-prayer-zachreinu','min2-commentary-zachreinu'],  # AYT Zachreinu
]
```

**Tier 2 — over-boxed, then corrected** (`fix_carveout_pdf_corrections.py` removes `optional`, asserting it was set so a stale assumption fails loudly):
```python
UNBOX = {
    'src/content/al-hamichyah.json': [   # print p.129 — inline בְּשַׁבָּת:/בר"ח:/ביו"ט: labels
        's-am-rubric-shabbos','s-am-prayer-shabbos',
        's-am-rubric-roshchodesh','s-am-prayer-roshchodesh',
        's-am-rubric-yomtov','s-am-prayer-yomtov',
    ],
    'src/content/mussaf-rosh-chodesh.json': ['mrc2-s004'],          # print p.217 — leap-year parenthetical
    'src/content/minchah.json': ['min2-prayer-ledor-vador-mhk'],    # print p.141 — AYT המלך הקדוש word-swap, inline
}
for path, ids in UNBOX.items():
    d = json.load(open(path)); loc = {s.get('id'): s for c in conts(d) for s in c['segments']}
    for sid in ids:
        seg = loc[sid]
        assert seg.get('optional') is True, f'{path}: {sid} not optional:true'
        del seg['optional']
```

**One-line test:** if you can picture the print typesetter putting the conditional text in a shaded box on its own line(s), use `optional: true`; if they kept it flowing inside the bracha with an inline `(On Shabbos: …)` label, leave `optional` out.

## Related

- `docs/solutions/documentation-gaps/rubric-rendering-contract-drift-entext-richtext-2026-06-29.md` — adjacent (both invoke PDF-as-authority), but about a different layer (rubric rendering-field/four-surface sync, not boxing granularity).
- `docs/REVIEW_QUEUE.md` → "Code-review + PDF-fidelity pass (2026-06-30)" — the incident this formalizes; also flags documenting the `optional` convention in CONTENT_GUIDE.md.
- `src/components/ServiceScroll.tsx` → `flattenService` + `optionalSolo/Start/Mid/End` — the contiguous-optional-merge rendering behavior.
