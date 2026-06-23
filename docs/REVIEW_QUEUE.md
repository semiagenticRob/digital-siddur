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

## Shacharis post-SE sections — audit 2026-06-23

Parallel vision audit of print pages 84-142 (siddur 60-118). Confirmed fixes applied in
`scripts/fix_post_se_audit.py` (21 fixes: parenthetical format, header enTop, nikud,
segment type, text accuracy, Ikarim ordering, L'Dovid artifact removal, Pitum rubric).
The following were surfaced but HELD — they require new Hebrew content, content additions,
or PDF verification.

### Missing content — RESOLVED in session 2026-06-23

- ✅ **Avinu Malkeinu: ~30 missing lines added** (`scripts/add_shacharis_missing_content.py`).
  Lines 9-35, AYT/fast two-column variants, Insight box, responsive rubric. Now 116 segs.
- ✅ **Shir shel Yom: Thursday + Friday added** (Psalm 81, Psalm 93; now 34 segs).
- ✅ **Kaddish Shalem: 3 closing paragraphs added** (תִּתְקַבֵּל, יְהֵא שְׁלָמָא, עֹשֶׂה שָׁלוֹם).
- ✅ **Kaddish Yasom after Aleinu: added** (11 segs, full prayer+commentary structure).
- ✅ **Avinu Malkeinu 4a/4b variant rubrics added** (prints p. 79: AYT / fast-day labels).

### All items resolved — 2026-06-23

- ✅ **Pitum + Kaddish D'Rabbanan**: full D'Rabbanan added (16 segs); In-Israel Barchu included.
- ✅ **avinu_malkeinu_title display: true** → CLEAN (verified NO at 300 DPI; header treatment only).
- ✅ **kt3-uva-comm-5 ordering**: swapped with kt3-uva-6 (commentary now follows its prayer).
- ✅ **L'Dovid rubric_kaddish**: removed enText; standardized with Shir shel Yom pattern.

### v2 / deferred (not textual errors)

- **Barchi Nafshi: Rosh Chodesh conditional display.** The prayer (Tehillim 104) is
  a Rosh Chodesh addition; the app always shows it. The rubric says "On Rosh Chodesh,
  add Tehillim Chapter 104:" — informing the user. Hiding it conditionally requires a
  v2 conditional-display system (the v1 `optional: true` only adds a shaded box,
  doesn't hide). Text is correct; this is a feature-completeness item, not a content
  error. Hold for v2 conditional display.

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

RULE TURNED OUT UNRELIABLE — now verified-only. TOC-based per-header
checks (pdf = siddur + 24) showed the "catchy English title = English-on-
top" rule is wrong ~40% of the time: sections with a prominent **formal
Hebrew name** put the Hebrew on top with the English as a *subtitle*
(מַעֲרִיב לְמוֹצָאֵי שַׁבָּת, שְׁלֹשָׁה עָשָׂר עִיקָרִים, שֵׁשׁ זְכִירוֹת, לְדָוִד ה׳ אוֹרִי,
מוּסָף), while only some re-titled sections are English-on-top. There is NO
derivable rule — each header must be checked at its TOC page.

`enTop` is now set ONLY on the 6 directly PDF-verified English-on-top
headers: My Body Works! (siddur 3), OUR REQUESTS (shacharit 60 + minchah
138), Al Ha'michyah "You Ate a Piece of Cake" (129), Borei Nefashos "You
Had a Glass of Water" (130), Travel Safe! / Tefillas Ha'derech (131).
Already-fixed Hebrew-on-top (enTop removed): Maariv Motzaei (189), 13
Ikarim (117), Shesh Zechiros (116), L'Dovid (111).

RESOLVED (2026-06-23). Each remaining header checked at its TOC page.
The refined "formal Hebrew name = Hebrew-on-top" pattern is ALSO not
reliable — Yishtabach (formal name יִשְׁתַּבַּח) and Shiras Ha'yam are
English-on-top. Confirmed: there is no rule; verify each.

PDF-VERIFIED English-on-top (enTop), this round:
- And I Have a Soul! (siddur 3), I Have a Torah! (4) — above אֱלֹהַי נְשָׁמָה /
  בִּרְכוֹת הַתּוֹרָה.
- Concluding Brachah of Pesukei D'Zimrah / Yishtabach (48), Shiras Ha'yam—
  Conclusion (46) — English title above ישתבח / ויושע.

APPLIED BY THE VERIFIED PATTERN (English title-on-top; Robert approved
applying the pattern to clear cases — teaching/descriptive English titles —
NOT each pixel-verified, worth a later spot-check): And I Am Committed,
Now I'm Ready to Daven, Hashem as Master of Nature, Last Six Chapters,
And to Sum Up, Introduction to Shiras Ha'yam, Returning the Torah, LET'S
TAKE ALL THIS HOME!, the 4 bentching brachah titles, You Control Our
Sleep, The Korbanos of the Festival.

PDF-VERIFIED Hebrew-on-top (stay on default, no enTop):
- Aleinu "We Have a Unique Relationship" (×3: shacharit 105, minchah,
  maariv) — עָלֵינוּ on top.
- Counting Up to Kabbalas HaTorah / Sefiras (191) — סְפִירַת הָעוֹמֶר on top.

UNRESOLVED — `kt1-header` "Now Let's Learn Some Torah!" / Krias HaTorah
(siddur 91): the section opens with חֲצִי קַדִּישׁ; no distinct printed
header found for this enText on siddur 90–91 (text layer also can't find
it). Left on the Hebrew-on-top default; confirm against the physical book
whether this header exists in print as English-on-top.

FLAGGED ITEMS — VERIFIED at the PDF (all Hebrew-on-top → correctly on the
default, no change needed):
- `s-header` "Mussaf for Rosh Chodesh" — print title is מוסף לראש חודש
  (Hebrew on top); the catchy "Another Month—Another Chance!" is a separate
  subtitle segment, and "Mussaf for Rosh Chodesh" is an app-added
  transliteration. He-top. ✓ (pdf-verified)
- `mch1-header` "Mussaf for Chol Hamoed" — same structure. He-top. ✓
- `header_sunday/monday/tuesday/...` — Hebrew day-name (שיר של יום …) on
  top, "(Tuesday, Chapter 82)" label below. He-top. ✓ (pdf-verified)
- `header_aleinu` "Shacharis • Aleinu" — that enText is the running-page-
  header text; the section title in print is Hebrew עָלֵינוּ. He-top. ✓

CONFIRMED RULE LOGIC: the Mussaf case validated it — a transliteration
header is He-top even when a catchy English subtitle sits nearby (the
subtitle is a separate segment, not the header's enText).

STILL RULE-BASED (not each visually confirmed; PDF page-location in this
environment is unreliable): the catchy-title enTop tags in the food-
brachos, bentching, bedtime, sefiras, tefillas-haderech, Aleinu-sentence,
and pesukei-dzimrah/kt title headers. The rule is verified on diverse
samples (My Body Works, OUR REQUESTS at 300 DPI) and consistent; for
absolute per-instance certainty, eyeball the rendered sections.

### Blocked on a clean Hebrew source + renderer support
- **Inline Kedushah speaker tags** (חזן / קו״ח / קו״ש before לְעֻמָּתָם i=44,
  בָּרוּךְ כְּבוֹד i=46, וּבְדִבְרֵי i=48, יִמְלֹךְ i=50). Same renderer limit as
  i=53/57: the labels on i=46/i=50 sit on `display` verses, so adding them
  inline would enlarge the label. Needs a small-label-prefix renderer span.
- **Adir Bamarom** congregational response after i=165 — new liturgy, rav
  sign-off. pdftotext extraction fragments the nikud (אַדִּ יר), so it can't
  be added accurately without a clean digital source or rav-verified text.
