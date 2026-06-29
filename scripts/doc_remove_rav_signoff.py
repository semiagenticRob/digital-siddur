#!/usr/bin/env python3
"""Remove the rav nikud sign-off as a tracked project gate/policy from
docs/REVIEW_QUEUE.md. The underlying TECHNICAL content gaps (unvocalized Sivan,
Hallel 116:9 dagesh, Divine Name spelling decision, Torah maqaf, malei/chaser)
are KEPT — only reworded from "rav sign-off / rav must verify" framing into
plain build TODOs. Rabbi outreach is managed separately, outside the repo.

Each replacement asserts its target appears exactly once, so a stale assumption
fails loudly instead of silently no-op'ing.
"""
PATH = 'docs/REVIEW_QUEUE.md'

REPLACEMENTS = [
    ("# Review queue — deferred / sign-off items",
     "# Review queue — deferred items"),

    ("## Needs rav sign-off",
     "## Nikud / spelling decisions (build TODOs)"),

    ("  → Hold for rav; then mechanical full-token replace",
     "  → Pending decision; then mechanical full-token replace"),

    ("### New Hebrew / new liturgy (needs rav sign-off)",
     "### New Hebrew / new liturgy"),

    (" — rav/content call.",
     " — content/house-style call."),

    ("- **Adir Bamarom** congregational response after i=165 — new liturgy, rav\n"
     "  sign-off. pdftotext extraction fragments the nikud (אַדִּ יר), so it can't\n"
     "  be added accurately without a clean digital source or rav-verified text.",
     "- **Adir Bamarom** congregational response after i=165 — new liturgy.\n"
     "  pdftotext extraction fragments the nikud (אַדִּ יר), so it can't\n"
     "  be added accurately without a clean vocalized source."),

    ("trusted vocalized source (e.g. Sefaria) + rav sign-off before insertion.",
     "trusted vocalized source (e.g. Sefaria) before insertion."),

    (" — a normalization the rav must settle.",
     " — a normalization still to settle."),

    ("*** RAV MUST VERIFY NIKUD before shipping. ***",
     "*** NIKUD TODO — verify/complete the vocalization. ***"),

    ("consonant-skeleton verified. *** ALL\nrequire rav nikud verification before shipping. *** Scripts:",
     "consonant-skeleton verified. *** ALL\nstill need nikud verification/completion (build TODO). *** Scripts:"),

    ("(Sivan inserted UNVOCALIZED — rav to add nikud)",
     "(Sivan inserted UNVOCALIZED — TODO: add nikud)"),

    ("RAV-VERIFY checklist (known/likely nikud spots):",
     "NIKUD TODO checklist (known/likely spots to verify/complete):"),

    ("## REMAINING STANDING ITEM: rav sign-off (universal policy)\n"
     "Not an audit discrepancy — the project ships no liturgical text without rav sign-off. The\n"
     "PDF-extracted insertions (Hallel 116/117/118:1, Omer 45-49, Zimun/Tehillim 137, Ve-al-hakol)\n"
     "are consonant-verified vs the print + nikud spot-checked; specific nikud spots for the rav's\n"
     "confirmation are listed above (e.g. Hallel 116:9 dagesh, Omer month-name vocalization).",
     "## Nikud status — PDF-extracted insertions\n"
     "The PDF-extracted insertions (Hallel 116/117/118:1, Omer 45-49, Zimun/Tehillim 137, Ve-al-hakol)\n"
     "are consonant-verified vs the print and nikud spot-checked; the specific nikud spots still to\n"
     "verify/complete are in the NIKUD TODO checklist above (e.g. Hallel 116:9 dagesh, Omer\n"
     "month-name vocalization)."),
]

text = open(PATH, encoding='utf-8').read()
for old, new in REPLACEMENTS:
    n = text.count(old)
    assert n == 1, f'expected exactly 1 occurrence, found {n}:\n---\n{old[:80]}...\n---'
    text = text.replace(old, new)

# Safety net: no rav/sign-off gating language should remain.
import re
leftover = [m.group(0) for m in re.finditer(r'(?i)rav[- ]?(sign|verify|to add|must)', text)]
assert not leftover, f'rav-gating language still present: {leftover}'
assert 'sign-off' not in text.lower(), 'sign-off still present'

open(PATH, 'w', encoding='utf-8').write(text)
print(f'OK — applied {len(REPLACEMENTS)} rewrites; no rav/sign-off gating language remains.')
