# Review queue — deferred items

## Book matter (front/back matter, Task 9, 2026-07-02) — haskamos omitted (images, not text)

pdf pp.9–10 contain two haskamos (rabbinic approbation letters) that are
**deliberately omitted** from `src/content/book-matter.json`. Verified by
rendering both pages at 300 DPI (`pdftoppm -png -r 300 -f 9 -l 10`) and
reading them directly — the task-9 report's original characterization of
these pages as "blank filler pages" was **wrong**; they are handwritten/
facsimile letters:

- **pdf p.9** — a handwritten English approbation letter from **Rabbi
  Yitzchak Shmuel HaLevi Berkovits**, Rosh Reshet HaKollelim L'Inas
  HaTzedek, Sanhedria HaMurchevet 113/27, Jerusalem.
- **pdf p.10** — a handwritten Hebrew approbation letter on Kollel Toronto
  (Institute for Advanced Judaic Studies) letterhead — Rosh HaKollel
  **Rabbi Yaakov Hirschman** and Rosh HaKollel **Rabbi Shlomo Miller** are
  named on the letterhead; the letter itself is signed **Rabbi Shlomo
  Eliyahu Miller**, Rosh HaKollel v'Av Beis Din of Kollel Toronto.

Both are facsimile reproductions of handwritten letters with **no digital
text layer** — `pdftotext` extracts nothing usable from them (they are
image content, not typeset text). Verbatim text digitization is impossible
under the never-retype-Hebrew rule (there is no source string to slice,
and transcribing handwriting from an image is exactly the kind of
retyping the rule exists to prevent — silent errors with no way to
verify against a byte-identical source). They are correctly left out of
`book-matter.json` for this reason, not because the pages are blank.

**Future option:** embed pdf pp.9–10 as images (e.g. on the About screen or
a "haskamos" appendix), scanned/cropped at print quality. This needs an
asset/rendering decision (how images are bundled and displayed elsewhere
in the app, if at all) and author approval before implementing — not
attempted this pass.

## Book matter (front/back matter, Task 9, 2026-07-02) — one omitted Hebrew line

`scripts/extract_book_matter.py` builds `src/content/book-matter.json` from
`pdftotext` output of the print's front/back matter. One Hebrew line is
**omitted** rather than included: the dedications piece's Isaiah 56:5
epigraph ("I will give them, in My house and within My walls, a monument
and a name"), printed at the top of pdf p.8 above the Sara Goldman
dedication. It is vocalized (nikud-bearing) and pdftotext extracts it badly
mangled — spurious spaces inside nearly every word, from the same class of
RTL/nikud extraction defect documented elsewhere in this file (see
"PDF-extraction attempt results" above). Unlike the Ashrei lemma quoted in
translation-note (also vocalized-and-mangled, but resolved by slicing the
already-proofed lemma out of `shacharit.json`), this exact pasuk does not
appear anywhere else in the digitized corpus to slice from. Per the task's
explicit fallback, it was left out rather than retyped (retyping a nikud-
bearing pasuk risks silent nikud errors). Add it when a clean vocalized
source (e.g. a PyMuPDF geometry-based re-extraction, or Sefaria) is
available — see `scripts/extract_pdf_hebrew.py` for the extraction
approach used elsewhere in this project for the same class of defect.

## Book matter (front/back matter, Task 9) — judgment calls (minor, disclosed only in task report)

- **Dropped cross-reference line.** The personal-notes piece's "Teens—see
  page 240 for YOUR personal note!" cross-reference (pdf pp.263–265) was
  dropped from `book-matter.json`, following the same convention already
  applied to the intro-parents piece's "Introduction for Teens on page
  XVIII" cross-reference (which *was* specified in the task brief). This
  extension to personal-notes was a judgment call, not explicit brief text.
- **Dedication-page bolding extended to all name lines.** The task brief's
  bold-markdown example covered the two memorial names (Cohen, Goldman)
  explicitly; bolding was also applied to the Feigenbaum reference, the
  Tobias tribute signature, and both donor names in the ואלו יעמדו על הברכה
  line, matching their visual prominence in print. Judgment call extending
  the brief's stated rule, not itself specified.

Items surfaced by the proactive print-vs-app audit that are intentionally NOT
auto-applied. Track them here so they aren't lost.

## Book matter — digitization record + glossary typo call (Task 11, 2026-07-02)

Front/back matter + glossary digitized (`scripts/extract_book_matter.py`,
`scripts/extract_glossary.py`) — human spot-check of the six About pieces
against the print recommended before release, in addition to the omissions
and judgment calls already logged above.

- **Glossary `sandek` entry preserves the print's typo "cirucumcision"
  verbatim.** Per the fidelity rule (derive-don't-retype extends to not
  silently "fixing" the print's own errors), `glossary.json` keeps the
  misspelling as printed. Author call needed: correct it with an inline
  `[sic]`, or leave it exactly as the print has it.

## Future round — Zmanim source decision — SHIPPED 2026-07-02

Hebcal hosted Zmanim REST API is now live (`src/store/zmanim.ts`, batch fetch
+ offline-first AsyncStorage cache; `src/lib/location.ts` for device location
and city search; Settings "Zmanim" section for location management). The
Hebcal.com attribution line (CC BY 4.0) ships in Settings. Sof zman Krias
Shema displays as GRA (user decision 2026-07-02, recorded in
`src/store/zmanim.ts`).

Open items from this round, deferred to a future author decision/pass:

- **Israel-mode calendar rules are out of scope.** The badges/chol-hamoed
  spans and special-day promotion logic (`src/lib/specialDays.ts`) assume
  diaspora practice only; an Israel toggle (different Yom Tov lengths, no
  second-day observances) is a future author decision.
- **Device-tz == location-tz assumption.** Wall-clock comparisons against
  cached zmanim assume the device's timezone matches the selected zmanim
  location's `tzid`. This breaks mid-travel (e.g. device still on home tz
  while the user has set a zmanim location abroad) — no cross-check or
  warning is implemented yet.
- **Suggested-service fallback boundaries are v1 heuristics.** When no
  zmanim are cached (offline, no location set, or stale beyond the batch
  window), `src/lib/suggestService.ts` falls back to fixed wall-clock
  boundaries (13:00 for Minchah, 19:30 for Maariv) rather than
  computed/cached zmanim. These times are placeholders, not derived from any
  halachic source, and should be revisited once real-world usage data or
  author guidance is available.

## Full print-vs-app audit (2026-07-01) — Shacharis + meal brachos

Systematic per-page audit (vision agents, 300 DPI) of Shacharis (pp.2-118) and
the meal-brachos block (pp.119-131). **Fixed this pass** (see scripts/):
Barchi Nafshi closing קדיש יתום; Hashkamas HaBoker name-list subtitle; Birkas
HaZan dropped אֵל (כִּי הוּא אֵל זָן); Al HaMichyah opening+closing variant scaffold
(restored the wine chasimah + עַל הָעֵץ, removed the duplicate grain chasimah).

**Still deferred (needs a clean vocalized source — unsliceable tokens):**
- **Al HaMichyah — Eretz-Yisrael closing parentheticals**, print p.154: the wine
  chasimah's `(בא״י וְעַל פְּרִי גַפְנָהּ)` and the fruit chasimah's `(בא״י וְעַל פֵּרוֹתֶיהָ)`.
  The tokens גַפְנָהּ / פֵּרוֹתֶיהָ appear nowhere in the corpus to slice; retyping
  their nikud is unsafe. Add both when a clean vocalized source is available.
- **Birkas HaMazon — Zimun Tehillim 137 focus-commentary** and **Nodeh V'al Hakol
  commentary** (print pp.143-144, 148). Both English glosses are printed but absent
  — same class as the deferred Hallel 116/117 per-verse glosses below.
  (Shir HaMaalos Ps 126 + Hodu Shabbos/YT block already tracked under MISSING
  CONTENT, print p.120.)

## Nikud / spelling decisions (build TODOs)

- **Divine Name spelling (siddur-wide).** The print spells the Tetragrammaton
  **יְהוָֹה** (cholam over the vav, U+05B9); many segments dropped it and store
  plain **יְהוָה**. Verified against the print for the Shema (cholam clearly
  present). Bare-`יְהוָה` counts: shacharit 159, hallel 28, birkas-hamazon 15,
  krias-shema-al-hamitah 14, maariv-motzaei-shabbos 12, minchah 6,
  netilas-lulav 6. The brachos before the Shema already use the cholam form.
  → Pending decision; then mechanical full-token replace `יְהוָה`→`יְהוָֹה`
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

### New Hebrew / new liturgy
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
~~HELD — **i=53 / i=57 (Kedushas Hashem)**~~ **RESOLVED 2026-07-01** via the
`heParts` small-span renderer field (`scripts/fix_kedushah_tags.py`): Atah
Kadosh is now whole-segment `display` with the AYT parenthetical small inside
the line, in the print's position `הָאֵל (בעשי״ת הַמֶּלֶךְ) הַקָּדוֹשׁ`. The
chazan's ledor-vador chasimah measured NOT-enlarged in print (1.00x) so it
stays normal size with the same small parenthetical. See the Kedushah entry
under "Blocked on a clean Hebrew source" for the measurements.

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
- ✅ **Inline Kedushah speaker tags — RESOLVED 2026-07-01** via the new
  `heParts` small-span renderer field (`scripts/fix_kedushah_tags.py`).
  Print-verified at 300 DPI (pdf 86-87): tags are חזן: / **קו"ח:** (the app's
  standalone rubrics said קר״ח — misreading, fixed), inlined small on קָדוֹשׁ
  (tag was missing entirely), לְעֻמָּתָם, בָּרוּךְ כְּבוֹד, וּבְדִבְרֵי, יִמְלֹךְ,
  and לְדוֹר וָדוֹר; the four standalone tag rubrics removed.
- ✅ **Kedushas Hashem AYT parenthetical — RESOLVED 2026-07-01** (same script).
  Both chasimos now read the print's form `… הָאֵל (בעשי״ת הַמֶּלֶךְ) הַקָּדוֹשׁ:`
  with the parenthetical as a small `heParts` span (was trailing, with הַקָּדוֹשׁ
  duplicated inside). Pixel-verified: ledor-vador has NO comma after the Name
  (removed); Atah Kadosh keeps its comma. `se1-prayer-kedushas-hashem` is now
  `display: true` (print sets the whole short bracha ~1.18x, like the other
  framework chasimos).
- **NEW HOUSE-STYLE FINDING (held) — Kedushah response verses are NOT enlarged
  in the print.** Same-word width measurement at 300 DPI (validated against the
  Gevuros chasimah, which measures the expected ~1.18x): קָדוֹשׁ / בָּרוּךְ כְּבוֹד /
  יִמְלֹךְ measure 1.00x (e.g. יְהֹוָה = 90px in all three, same as normal brachos;
  בָּרוּךְ = 97px), right-aligned with inline tags — and the chazan's לְדוֹר וָדוֹר
  chasimah is also 1.00x. The app's `display: true` (1.5x centered) on
  se1-prayer-kadosh / baruch-kvod / yimloch therefore OVERSTATES the print.
  Kept as-is for davening prominence pending an author call; if changed, also
  revisit commit 8fd5527's premise. Note also the app's display scale (1.5x) vs
  the print's measured ~1.18x for true framework chasimos — a global style knob.
- **Follow-up:** mussaf-chol-hamoed has two standalone `חזן:` rubrics
  (mch1-kedushah-chazzan1/2-rubric) that likely print inline the same way —
  verify at their TOC pages and apply the heParts treatment there too.
- **Adir Bamarom** congregational response after i=165 — new liturgy.
  pdftotext extraction fragments the nikud (אַדִּ יר), so it can't
  be added accurately without a clean vocalized source.

## Display residual — short Hebrew-lemma commentary clipping (audit 2026-06-25)

A commentary/insight that **leads with a short Hebrew lemma** and whose total
text is short (~1–2 lines) still clips on the right edge in the reader (e.g.
Shesh Zechiros `commentary_shabbos`: "**שַׁבָּת**—…to remain spiritually strong
during the week." renders "…to rem" off-screen). Long Hebrew-lemma commentaries
(e.g. `מרים`, `מעשה עמלק`) and all pure-English commentaries wrap correctly.

Root cause: RN/iOS measures a `<Text>` whose content begins with an RTL run at
its intrinsic single-line width when the content is short, overflowing the
container. **Four fixes tried and ruled out** (verified on device): concrete
`itemRoot` width (ServiceScroll), `width:'100%'`+`alignSelf:'stretch'` on the
commentary containers, concrete `maxWidth` on the text style, and a leading LRM
(U+200E) prefix in RichText. None re-wrap the short RTL-leading line.

NOTE: the user's originally-reported clipping (the pure-English Shloshah Asar
Ikarim *principle* boxes) **is fixed** by the `itemRoot` concrete-width change —
confirmed wrapping on device after a clean reload. Only the short-Hebrew-lemma
case remains.

→ Needs a deeper structural fix, e.g. render the leading lemma as its own
element so the paragraph Text does not start with an RTL isolate, or replace the
FlashList cell measurement path. Candidate, not yet attempted: split the lemma
out of RichText's first span. Hold as its own focused task.

## Missing liturgy needing a clean nikud source — full-siddur audit 2026-06-25

These passages are printed in the siddur but ABSENT from the app, and the Hebrew
exists nowhere in src/content/ to slice from. Retyping is forbidden (drops nikud)
and the PDF text layer is corrupted (spurious intra-word spaces), so they need a
trusted vocalized source (e.g. Sefaria) before insertion.

- **Hallel — Tehillim 116 (אָהַבְתִּי) and 117 (הַלְלוּ אֶת ה׳ כָּל גּוֹיִם), and 118:1
  (הוֹדוּ … כִּי טוֹב).** The app jumps 115→118:2; verified against print pp.206–207.
  Also the second "Omit the following on Rosh Chodesh…" rubric before 116. This is
  a major Hallel gap — full chapters of liturgy missing.
- **Sefiras HaOmer — days 45–49 (1–5 Sivan).** App now has days 1–44 (Day 44 was
  added by fragment-assembly and hand-verified against print p.195). Days 45–49
  need only the month name **סִיוָן** with nikud (the rest is composable from
  existing day entries); that token is absent from the app. Verified print p.195.
- **Birkas Ha'mazon — the Zimun** (weekday intro + Tehillim 137 על נהרות בבל + the
  invitation), print pp.119–121; and the **Ve-al-hakol closing** of Birkas
  Ha'aretz (וְעַל הַכֹּל … בָּרוּךְ אַתָּה ה׳, עַל הָאָרֶץ וְעַל הַמָּזוֹן), print p.124.
- **Krias Shema al Ha'mitah — the ג״פ (×3) recitation rubric** Hebrew label to
  precede ksm2-prayer-8/9/11, print p.225 (small, but needs correct nikud form).

(English fixes, markdown, dedups, and reconcile items sliceable from existing app
text were auto-applied in this audit — see scripts/fix_audit*.py.)

  UPDATE 2026-06-26: 7th fix attempt (concrete `width` on the text instead of
  maxWidth) also failed — short Hebrew-lemma commentary still clips when centered.
  Confirmed intractable via style/layout props; needs a rendering-architecture
  change (e.g. render leading lemma outside the paragraph, or replace FlashList
  cell measurement). Left as documented residual.

## PDF-extraction attempt results (2026-06-26) — partial

Built a working extractor (`scripts/extract_pdf_hebrew.py`, needs PyMuPDF venv):
filters to the prayer-text column and re-inserts word breaks from glyph geometry,
removing the text layer's spurious intra-word spaces. Outcome is MIXED:

- **Tehillim 117 — extracts PERFECTLY** (verified vs print p.207):
  `הַלְלוּ אֶת יְהֹוָה כָּל גּוֹיִם, שַׁבְּחוּהוּ כָּל הָאֻמִּים: כִּי גָבַר עָלֵינוּ חַסְדּוֹ, וֶאֱמֶת יְהֹוָה לְעוֹלָם, הַלְלוּיָהּ:`
  (Can't insert alone — Tehillim 116 must precede it.)
- **Tehillim 116 — extractable but with sporadic per-line defects** (one line lost
  all word-spaces, a line-break cut a word, RTL colon misplacement, block-order
  jumbling across the 2 pages). Needs careful per-line assembly + image verify.
- **Sefiras Omer 45–49 — count phrases extract clean** (e.g. `הַיּוֹם חֲמִשָּׁה וְאַרְבָּעִים יוֹם, שֶׁהֵם שִׁשָּׁה שָׁבוּעוֹת וּשְׁלֹשָׁה יָמִים בָּעֹמֶר:`) BUT the **month name סיון comes out bare/nikud-dropped** — the one genuinely-blocked token is STILL not cleanly recoverable. Also `בָּעֹמֶר` (chaser) vs the app's `בָּעוֹמֶר` (malei) — a normalization still to settle.

CONCLUSION: PDF extraction partially works but cannot reliably produce all the
missing nikud (Sivan, and 116's defect lines). A clean vocalized source (Sefaria)
remains the safe path for the Hallel psalms, the Omer Sivan days, and the Zimun.
Extractor + clean 117 text are preserved here for whoever completes it.

## UPDATE 2026-06-26 — Hallel 116/117/118:1 INSERTED (PDF-extracted)

Tehillim 116, 117, and 118:1 (הוֹדוּ) are now in hallel.json (after 115b) via
scripts/fix_hallel_116_117_118.py — Hebrew PDF-extracted (PyMuPDF + geometry
de-spacing, scripts/extract_pdf_hebrew.py), consonant-skeleton verified verse by
verse. *** NIKUD TODO — verify/complete the vocalization. *** Known open spots:
116:9 אֶתְהַלֵךְ (Masoretic has dagesh: אֶתְהַלֵּךְ); 118 header now appears before
הוֹדוּ while a second 118 sub-header (hallel2-118a-header) remains later in the
section — confirm the 118 header structure. Focus-commentaries / per-verse glosses
for 116 & 117 are NOT yet added (English enhancement, follow-up).

STILL needing a clean source (PDF extraction insufficient): Omer 45-49 (Sivan
month nikud), Birkas Hamazon Zimun (Tehillim 137) + Ve-al-hakol closing, ג״פ rubric.

## UPDATE 2026-06-26 (2) — ALL missing-liturgy gaps now INSERTED (PDF-extracted)

Every source-needed passage has been extracted from the print PDF (pipeline:
scripts/extract_pdf_hebrew.py) and inserted, consonant-skeleton verified. *** ALL
still need nikud verification/completion (build TODO). *** Scripts:
- Hallel Tehillim 116, 117, 118:1 — scripts/fix_hallel_116_117_118.py
- Sefiras Omer days 45-49 — scripts/fix_omer_45_49.py (Sivan inserted UNVOCALIZED — TODO: add nikud)
- Birkas HaMazon Zimun (Tehillim 137 + call-response invitation) — scripts/fix_zimun.py
- Birkas HaMazon Ve-al-hakol closing — scripts/fix_velahakol_and_gimelpe.py
- Krias Shema al Ha'mitah ג״פ rubrics (verses 8-11) — scripts/fix_velahakol_and_gimelpe.py

NIKUD TODO checklist (known/likely spots to verify/complete):
- Hallel 116:9 אֶתְהַלֵךְ (Masoretic אֶתְהַלֵּךְ)
- Omer 45-49 month name סיון (bare — standard סִיוָן)
- Zimun role labels (הַמְזַמֵּן אוֹמֵר etc.) and the בעשרה inline conditional; nikud throughout Tehillim 137

REMAINING (enhancements / not blocking liturgy):
- Focus-commentaries + per-verse glosses (English) for Hallel 116 & 117
- Zimun Shabbos alternative (Tehillim 126) — not yet added
- 118 header structure (a second 118 sub-header remains mid-section)
- DISPLAY residual: short Hebrew-lemma commentary clip (7 fixes failed; needs renderer-architecture change)

## DISPLAY RESIDUAL — FINAL determination (2026-06-26)
9 distinct fixes attempted & ruled out on device for the short-Hebrew-lemma commentary
clip: (1) itemRoot concrete width, (2) container width:'100%'+alignSelf:stretch,
(3) text maxWidth, (4) text concrete width, (5) container concrete width, (6) LRM
(U+200E) prefix, (7) remove writingDirection:'ltr', (8) alignSelf:flex-start,
(9) remove the RLI/PDI directional isolate. The Text renders at its intrinsic
single-line width and overflows its (correctly-sized) container regardless — an
RN/iOS Text-layout limitation for short content beginning with an RTL run.
A React-level cure requires either a native measurement fix / RN upgrade, or a
flex-wrapped word-layout rewrite of RichText (which would break inline bidi ordering
for multi-word inline Hebrew — a regression across the whole siddur). NOT fixable by
a safe, parsimonious agent edit. Scoped as a dedicated renderer task.

## DISPLAY RESIDUAL — RESOLVED via workaround (2026-06-26 final)
commentary_shabbos (the one confirmed render-clip) now displays fully: applied explicit
display line-breaks (~30 chars/line, robust across font steps -2…+4) via
scripts/fix_shabbos_display_breaks.py — word content identical to print, breaks only.
Verified on-device: all 6 lines visible, no clip. Display verifiers found no other real
clips across 133 screens (all 14 services). Check 7 now passes for all 60 prayers.
→ CLEANUP TASK (not blocking): when the underlying RN/iOS FlashList Text-measurement bug is
  fixed natively, REMOVE the manual breaks from commentary_shabbos so it reflows naturally.

## Nikud status — PDF-extracted insertions
The PDF-extracted insertions (Hallel 116/117/118:1, Omer 45-49, Zimun/Tehillim 137, Ve-al-hakol)
are consonant-verified vs the print and nikud spot-checked; the specific nikud spots still to
verify/complete are in the NIKUD TODO checklist above (e.g. Hallel 116:9 dagesh, Omer
month-name vocalization).

## DISPLAY RESIDUAL — RESOLVED & root cause corrected (2026-06-26 final)
The commentary_shabbos "clip" was NOT a persistent content/renderer bug — it was a FlashList
measurement-SETTLE delay: every "clip" screenshot this session was taken ~1s after a swipe,
catching the cell mid-measurement. With the NATURAL text (no manual breaks) and a proper
settle (~5s, no swipe immediately before capture), the box wraps EDGE-TO-EDGE correctly,
identical to the other EXPLANATION boxes (verified on-device). The earlier manual-line-break
workaround was the WRONG fix (made it wrap early / inconsistent) and has been REVERTED to the
natural print-faithful sentence. NO renderer change or content workaround is needed.
(Minor: a fast scroller may briefly see the transient mid-measure state before it settles —
standard FlashList behavior, self-correcting, not a content defect.)

## Mid-scroll Hebrew word-break artifact — FIXED siddur-wide (2026-06-26)
User reported a prayer line rendering with an orphaned final letter (e.g. modeh_ani_3:
"…אֱלֹהֵיכֶם" briefly showing "ם," alone on the next line). Audited ALL shacharit Hebrew DATA:
clean — no hidden/directional chars, no genuine word-splits, no internal-space defects (the
only scan hits were legitimate masoretic maqaf in Barchi Nafshi + intentional rubric/bullet
spacing). Root cause was a transient FlashList async-measurement state during scroll (the same
class as the earlier commentary_shabbos "clip"). FIX: set drawDistance={1000} on the
ServiceScroll FlashList so cells finish measuring/settle off-screen before they scroll into
view. Verified: the reported line now renders correctly even on a quick scroll-capture.
This supersedes/closes the commentary_shabbos render-clip too (natural text + drawDistance).

## Code-review deferred items (2026-06-29, ce-code-review after /simplify)
The /simplify refactor reviewed clean. Two P0 contract-sync gaps were FIXED this pass (rubric
`enText` renders via RichText — CLAUDE.md + CONTENT_GUIDE.md + lint_content.py now document/enforce
it; the `prayer:`/`section:`/`Appendix N:M` link schemes are documented in CONTENT_GUIDE convention 8).
Also applied: typed-href in RichText (dropped `as never`), an `initialPrayer` re-fire guard, the
`useImperativeHandle([items])` dep, and an a11y label on the selection ✕. Three items DEFERRED — all
pre-existing, none blocking:

1. **Deep-link / ToC scroll readiness (P1).** `app/daven/[service].tsx` still uses a fixed 350ms
   `setTimeout` before `scrollToPrayer`; it races FlashList initial layout on slow/cold loads and can
   silently no-op (FlashList 2.x `scrollToIndex` has no FlatList-style failure callback to bolt on
   safely). Proper fix: expose an `onLoad`/ready signal from `ServiceScroll` and gate the scroll on it
   instead of a magic delay. `drawDistance={1000}` already mitigates in practice.
2. **Same-service `prayer:` link stacks a duplicate screen (P2).** `RichText` `prayer:` links always
   `router.push`, so a link whose target service == the current screen pushes a second reader instance
   instead of scrolling in place. Fix needs a `scrollToPrayer` handle threaded to RichText (context or
   prop): same-service → scroll; cross-service → push.
3. **No unit tests for pure render-logic (P1).** `flattenService` pos classification (solo/start/mid/end),
   the `prayer:` link regex in `renderLeaf`, and the bilingual-rubric display-mode branch are untested.
   Blocked on harness setup: these live inside components, and importing them pulls FlashList/expo-router;
   `CONTENT_WIDTH` also resolves to -32 under Jest's node env. Cleanest path is to extract the pure helpers
   (flattenService, renderLeaf parsing) into standalone modules, then unit-test those.

## Code-review + PDF-fidelity pass (2026-06-30)
PDF-first verification of the corpus-wide carve-out/style work. Per-page print verification
of all ~64 carve-out runs: boundaries confirmed exact. Corrections applied this pass:
- **Un-boxed short inline inserts** the print renders inline (not shaded), per PDF-primary:
  al-hamichyah Shabbos/RC/YT inserts, mussaf-rosh-chodesh leap-year (mrc2-s004), minchah AYT
  המלך הקדוש substitute (min2-prayer-ledor-vador-mhk). Script: fix_carveout_pdf_corrections.py.
- **Lint guard:** promoted `prayer.enText (never renders)` warn→error (corpus is clean of it
  after the krias-shema relocation), so re-introduction blocks the commit gate.

MISSING CONTENT (build TODO — needs a clean vocalized source, not yet digitized):
- **Birkas Hamazon — Tehillim 122 (שִׁיר הַמַּעֲלוֹת לְדָוִד) Shabbos/Yom Tov pre-bentching insert**,
  print p.120: rubric "On Shabbos and Yom Tov start with the following" + Psalm 122 + a "Some add"
  addition. Entirely absent from birkas-hamazon.json (no segments). Add when a clean source is available.

DEFERRED code-review findings (low priority; not PDF-fidelity — see ce-code-review run
.context/compound-engineering/ce-code-review/20260630-083247-23c048f0/):
- fix_ksm_dead_glosses.py: latent guard-soundness defects (`global ok` inert; slice_voc
  first-match/nikud-blind/word-boundary-blind/empty-skeleton). SHIPPED OUTPUT VERIFIED CLEAN —
  harden only if the slice-re-vocalize helper is reused.
- Script duplication: `containers()`/`strip_md`/`skel`/`balanced` copy-pasted across scripts;
  extract scripts/_content_utils.py (one skel variant includes Latin chars — reconcile first).
- Linter hardening (style guards): add a malformed split-lemma (`*word **rest**`) error check and
  a carve-out contiguity check to lint_content.py to prevent regression.
- CONTENT_GUIDE.md: document the `optional`→shaded-box carve-out convention (style-doc sync).
