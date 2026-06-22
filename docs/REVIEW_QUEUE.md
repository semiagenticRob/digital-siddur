# Review queue — deferred / sign-off items

Items surfaced by the proactive print-vs-app audit that are intentionally NOT
auto-applied. Track them here so they aren't lost.

## Needs rav sign-off

- **Divine Name spelling (siddur-wide).** The print spells the Tetragrammaton
  **יְהוָֹה** (cholam over the vav, U+05B9); many segments dropped it and store
  plain **יְהוָה**. Verified against the print for the Shema (cholam clearly
  present). Bare-`יְהוָה` counts: shacharit 159, hallel 28, birkas-hamazon 15,
  krias-shema-al-hamitah 14, maariv-motzaei-shabbos 12, minchah 6,
  netilas-lulav 6. The brachos before the Shema already use the cholam form.
  → Hold for rav; then mechanical full-token replace `יְהוָה`→`יְהוָֹה`
  (strip-diff verified). Decided 2026-06-18.

## Needs a careful dedicated pass

- **Maqaf in Torah text.** The print uses masoretic maqaf (e.g. אִם־שָׁמֹעַ,
  אֶת־יְהוָה, בְּכָל־לְבַבְכֶם) in the Torah passages (Shema, Ve'ahavta,
  Vehaya, Vayomer); the app uses plain spaces throughout. Verified present in
  the print. Requires per-word transcription of maqaf positions for each
  passage (and is systematic across all Torah quotes in the siddur), so do it
  as its own pass rather than piecemeal.

- **Complete formatting sweep of the Shema glosses.** The audit agents
  under-reported: beyond the fixes already applied, several glosses likely have
  more truncated bold-lemma boundaries (e.g. `אֹתוֹ`→`וּרְאִיתֶם אֹתוֹ`, found
  by hand) and non-italic parenthetical asides. A complete, reliable fix is the
  brachos-style markup pass (render print pages → vision agents mark up the
  existing text → strip-diff verify) over every gloss, not the quick per-page
  audit. Glosses not yet hand-verified: i=37, 51, 66, 68, 74.

## Shemoneh Esrei (Shacharis, g-shemoneh-esrei) — audit 2026-06-22

The verified gloss/nikud fixes from this audit are applied (see
`scripts/fix_se_audit.py`). The following were surfaced by the same audit but
HELD — they are structural, add new liturgy/Hebrew, or are house-style calls.
Segment indices are into `g-shemoneh-esrei` prayer[0].segments.

### Structural (changes segment type/shape — needs author confirm)
- **i=85** — the refuah personal tefillah (יְהִי רָצוֹן… for a specific choleh)
  is stored as a `rubric`; in the print it is davening text, so it should be a
  `prayer` segment (currently renders as plain instructional text, wrong style).
- **i=182** — the יְהִי רָצוֹן before Elokai Netzor is missing its Hebrew title
  line; the print sets a header there.
- **i=130** — possible extra/duplicate Retzei header; verify against print.

### New Hebrew / new liturgy (needs rav sign-off)
- **Missing "Adir bamarom" congregational response** after i=165 (the Kedushah
  area) — not present in the app; print includes the קהל response. New liturgy.
- **i=189** — add optional Aseres Yemei Teshuvah parenthetical
  בעשי"ת הַשָּׁלוֹם as an `optional` insertion.
- **i=152** — Purim וְאַתָּה line: likely a print typo (most siddurim include
  it); confirm before changing.

### Micro nikud / wording (needs hand-verify at high DPI before applying)
- **i=88** — dagesh on תְּבוּאָתָהּ + a comma that should be a colon.
- **i=90** — missing word וְתֵן (nikud-style insertion).
- **i=129** — add bold "all" (adds an English word; parallel to the i=43 fix).

### House-style decisions
- Header/rubric nikud consistency group: i=116, 121, 127, 141.
- קו"ח (kal va-chomer) labels — formatting convention.
- Punctuation review in i=183.

## Shemoneh Esrei (Shacharis) — formatting scan 2026-06-22

Full 16-page print-vs-app formatting audit. Safe fixes applied in
`scripts/fix_se_formatting_scan.py` (display on whole-segment framework
chasimos i=16/35/175, heTop on transliteration headers, lemma spellings,
refuah-insert italics, epilogue bridge). Held items below.

### Framework chasimah enlargement — DONE except Kedushas Hashem
The print sets the chasimah (בָּרוּךְ אַתָּה ה׳…) of the **six framework
brachos** oversized + centered; the 13 middle requests stay normal.
APPLIED: `display` on i=16 (Avos), i=35 (Gevuros), i=131 (Retzei),
i=175 (Sim Shalom); Modim split — i=159 keeps the normal opening,
`se3-prayer-modim-chasimah` carries the enlarged chasimah.
HELD — **i=53 / i=57 (Kedushas Hashem)**: the chasimah is enlarged but
carries the small AYT parenthetical `(בעשי״ת הַמֶּלֶךְ הַקָּדוֹשׁ)`, which the
print keeps small *inside* the enlarged line. A whole-segment `display`
would enlarge the parenthetical too, so this can't match the print without
a **renderer change** (small-label/parenthetical span inside a display
verse). Also note an app-vs-print content diff: app has `הָאֵל הַקָּדוֹשׁ
(בעשי״ת …)` but the print sets `הָאֵל (בעשי״ת הַמֶּלֶךְ) הַקָּדוֹשׁ` — rav/content call.

### Header order — re-architected to be PDF-deterministic (commit 32bc4f1)
No global default may contradict the PDF. Default is now **Hebrew-on-top**
(the print's majority — every transliteration/description sub-header);
**`enTop`** explicitly marks English-on-top headers. `heTop` removed.
Verified at the PDF: catchy English **title/sentence** = English-on-top
(My Body Works!, OUR REQUESTS, food-brachos, bentching brachah titles,
Travel Safe!, etc.); transliteration ("Ashrei", "Korbanos") / bracha-
description ("Give me healing") = Hebrew-on-top. 30 title-headers tagged
`enTop` app-wide by this rule.

CONFIDENCE: SE (verified at 300 DPI per header) + My Body Works are
directly PDF-verified. The other-service title-headers (bentching, food
brachos, bedtime, sefiras, tefillas-haderech, Aleinu sentence-headers,
mussaf korbanos) were tagged by the **verified rule**, not each visually
confirmed — worth a spot-check pass.

FLAGGED — left on the Hebrew-on-top default, NOT guessed (need a visual
check; they're spelled-out service titles / labels, ambiguous under the
rule): `mch1-header` "Mussaf for Chol Hamoed", `s-header` "Mussaf for
Rosh Chodesh", shacharit `header_aleinu` "Shacharis • Aleinu", shacharit
`header_sunday/monday/tuesday/wednesday` day-of-week labels. Also the main
service transliteration headers (Maariv, Minchah, Hallel, Tachanun, the
Kaddish variants) default Hebrew-on-top by rule — confirm if any are set
English-first in the print.

### Blocked on a clean Hebrew source + renderer support
- **Inline Kedushah speaker tags** (חזן / קו״ח / קו״ש before לְעֻמָּתָם i=44,
  בָּרוּךְ כְּבוֹד i=46, וּבְדִבְרֵי i=48, יִמְלֹךְ i=50). Same renderer limit as
  i=53/57: the labels on i=46/i=50 sit on `display` verses, so adding them
  inline would enlarge the label. Needs a small-label-prefix renderer span.
- **Adir Bamarom** congregational response after i=165 — new liturgy, rav
  sign-off. pdftotext extraction fragments the nikud (אַדִּ יר), so it can't
  be added accurately without a clean digital source or rav-verified text.
