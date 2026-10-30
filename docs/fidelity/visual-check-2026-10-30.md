# Visual check of the print fidelity audit — 2026-10-30

A person-by-eye check of the automated audit, against `feigenbaum-siddur-original.pdf`.

## 1. Spot test: 50 passages across the book

50 app fields sampled evenly from every unit (PDF p.37–294: services, book matter,
appendices, glossary). Each print crop was read against the app text at 300 DPI. Every
Hebrew line was then re-read at 600 DPI.

**39 match the print exactly.** 11 differ:

| # | Where | Difference | Status |
|---|---|---|---|
| 4 | Avinu Malkeinu (AYT) | English translation interleaved from two print columns | **Caused by the audit's English fixer; repaired** (see 2) |
| 23 | Tefillas HaDerech, p.155 | App נ"פ, print ג"פ ("three times"), both instances; app also vocalizes ואומר | For the rav (`REVIEW_QUEUE.md`) |
| 16 | Avinu Malkeinu | App נְקֹם, print נְקוֹם | Already in the ledger (rav) |
| 20, 21, 36 | Commentary lemmas | App lemma shorter or longer than the print's | Already in the ledger (rav) |
| 3 | Pesukei D'Zimrah header | Print unvocalized ברוך יהוה לעולם; app vocalized | Not in the ledger: matched to a commentary lemma instead |
| 37–39 | Sefiras HaOmer | Date labels vocalized with a period in the app; small, unvocalized, colon in print. Also בָּעוֹמֶר vs print בָּעֹמֶר (×49) | Labels for the rav (`missing.py` wrongly calls them missing); בעמר already in the ledger |
| 49 | Appendix 3 | Straight opening quote, print curly | Already held (`english-held.json`) |

Where the tool, not the app, was wrong:
- **Near-identical lines get paired wrongly.** Examples: מתיר אסורים compared against
  זוקף כפופים (test 18), and neighbouring Omer lines. The ledger shows made-up Hebrew
  differences there; the app text is correct.
- **English rubrics the app adds** can match a nearby print line (test 34).

## 2. Every multi-word English fix, checked against the print

The fixer reads print columns side by side as one line where two translations sit next
to each other (Avinu Malkeinu, the Shelo Asani pair, Al HaNissim). It also picks up
neighbouring labels and sidebars. All 82 strings where commit `82cf20c` changed two or
more words were compared with the print. Method: each phrase was looked up in the
PDF's English text layer, then the crop was read by eye.

- **Correct, kept:** most of them, e.g. "cheer up other patients", "the Chashmonai",
  "(The person saying Kaddish requests:)", "we agree".
- **Wrong, undone:** 29 strings, restored by
  `scripts/fix_fidelity_english_regressions.py`. The fixer had:
  - interleaved Avinu Malkeinu translations (Shacharis and Minchah)
  - dropped printed text: "the fruit of the tree;", "Give thanks to", "and You are a
    compassionate and merciful King.", "best we can—we will merit Olam Haba."
  - dropped labels: "On Purim:", "On Sukkos:", "On Shemini Atzeres/Simchas Torah:",
    "(During Aseres Yemei Teshuvah say instead:", "level"
  - pulled in neighbouring text: a glossary line over the "Korbanos" header, a
    sidebar into the Ashrei insight, "What We Believe!" from a title
  - deleted spaces after commas ("rescue,for", "as,“Hashem")
  - added "cite" after a link
- **Same strings, corrected to the print:** the Ashrei insight now reads
  "fallings—סוֹמֵךְ…—He helps us get back up!" (pdf p.62).

Each of the 11 audit findings that would have redone one of these edits is now
`by: human, decision: app-correct` in `ledger.json`, and `apply_english.py` skips any
finding a person has ruled on. The fixer also now holds back for a person:
- any edit of two or more words
- a space deleted after punctuation
- an edit at the end of a link

Single-character fixes (quotes, apostrophes, dashes) were not re-checked one by one.
None of the 50 spot-test passages showed a wrong one.

## 3. Limits

- The sample covers only text the tool could locate in the print, so content it
  cannot place is under-represented.
- Read by eye at 600 DPI, letters, words and most vowels are reliable. A dropped
  vav (בָּעֹמֶר) was missed at 300 DPI and caught only by the tool and at 600 DPI.
  The glyph-level ledger stays the authority for nikud.
- Minchah's נְקַדֵּשׁ commentary is missing the print's כַּכָּתוּב עַל יַד נְבִיאֶךָ
  lemma ("As the Navi tells us" sits after the wrong lemma). This was true both
  before and after the fixer and needs a hand edit.
