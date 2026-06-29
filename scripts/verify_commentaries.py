#!/usr/bin/env python3
"""
Comprehensive post-fix verification of all commentary segments in shacharit.json.

Key checks — each written to avoid firing on **bold** spans:
  1. ITALIC_LEAD: commentary starts with a SINGLE *Hebrew* (should be **bold**)
  2. BROKEN_MIX: *word **lemma**—* malformed hybrid
  3. BARE_HE: bare Hebrew letters at start (not inside **)
  4. ITALIC_HE_INLINE: *Hebrew* in body, NOT inside (*parens*) or (**bold**)
  5. TRUNCATION: English ends without terminal punctuation or a recognized suffix

Rules for single-* vs double-**:
  - \*(?!\*)  matches a lone * not followed by *  → italic marker
  - \*\*      matches double **                    → bold marker
"""
import json, re

with open('src/content/shacharit.json') as f:
    data = json.load(f)

# ── regex helpers ─────────────────────────────────────────────────────────────
# Single italic marker (not part of bold **): *text* where * is NOT doubled
SINGLE_STAR = r'(?<!\*)\*(?!\*)'  # a * not preceded and not followed by *

# Italic Hebrew span (single stars, Hebrew content, not inside parens)
ITALIC_HE_RE = re.compile(
    r'(?<!\()' + SINGLE_STAR + r'([^*()\n]*[א-ת][^*()\n]*)' + SINGLE_STAR + r'(?!\))',
)

# Bold span: **content** — used to strip bold spans before italic scan
BOLD_RE = re.compile(r'\*\*[^*]+\*\*')

CLOSE_PUNCT = set('.!?:')
CLOSE_QUOTE = set(['”', '’', '“', '‘', '"', "'"])

def ends_well(en):
    """True if commentary ends with recognized terminal punctuation."""
    s = re.sub(r'\*+$', '', en.strip())
    s = s.rstrip(')*').rstrip()
    if not s:
        return True
    last = s[-1]
    if last in CLOSE_PUNCT or last in CLOSE_QUOTE:
        return True
    if last.isdigit():          # Appendix N reference
        return True
    if re.search(r'[א-ת]$', s): # ends in Hebrew
        return True
    return False

# ── known legitimate patterns ─────────────────────────────────────────────────
# These are flagged by our heuristics but confirmed not to be errors.
KNOWN_LEGIT = {
    # "אָמֵן. **bold**" prefix — congregation's Amen response before bold lemma
    'kaddish-drab-4',
    'chatzi_kaddish_torah_commentary_2',
    # Inline word-gloss *בָּרוּךְ* immediately after the bold lemma
    'pz1-commentary-3',
    # *כָּל הָאָרֶץ* — intentional verse-continuation notation after bold lemma
    'pz1-commentary-6',
    # Commentary ends with colon — the proclamation IS the prayer verse that follows
    'pz1-commentary-4',
    # Appendix reference endings (digit = Appendix N)
    'se1-commentary-ledor-vador',
    'se1-commentary-kedushas-hashem',
    'se2-mishpat-commentary',
    # (*אֶחָד*)/ (*קָדוֹשׁ*) parenthetical word-glosses; trailing ** already fixed
    'tach2-s29',
    'tach2-s31',
    # *(English description:)* italic intro notes before a bold Hebrew lemma —
    # the * at start is English rubric/context, not a Hebrew lemma. Correct format.
    'yotzer_2_gloss_a',     # *(Our praise of Hashem:)* **bold lemma**—
    'yotzer_3_gloss',       # *(The angels' praise of Hashem:)* **bold lemma**—
    'se4-sim-shalom-c1',    # *(Peace of mind, inner peace:)* **bold lemma**—
    'se4-sim-shalom-c2',    # *(Peace between one another:)* **bold lemma**—
    'se4-sim-shalom-c3',    # *(Peace from war and danger:)* **bold lemma**—
    'kt3-ashrei-comm-9',    # *(And to sum up...:)* **bold lemma**—
    'aleinu_kaddish_comm_3',  # *(The person saying Kaddish then says:)* ... **אָמֵן**—
    'aleinu_kaddish_comm_4',  # *(The person saying Kaddish requests:)* ... **אָמֵן**—
    'aleinu_kaddish_comm_5',  # *(The person saying Kaddish requests:)* ... **אָמֵן**—
    'pitum_kdr_comm_3',     # *(The person saying Kaddish then says:)* ... **אָמֵן**—
    'pitum_kdr_comm_4',     # *(The person saying Kaddish requests:)* ... **אָמֵן**—
    'pitum_kdr_comm_5',     # *(The person saying Kaddish requests:)* ... **אָמֵן**—
    'pitum_kdr_comm_6',     # *(The person saying Kaddish requests:)* ... **אָמֵן**—
}

# ── audit ─────────────────────────────────────────────────────────────────────
total = clean = 0
unresolved = []
legitimate = []

for group in data.get('groups', []):
    for prayer in group.get('prayers', []):
        for seg in prayer.get('segments', []):
            if seg.get('type') != 'commentary':
                continue
            total += 1
            en = seg.get('enText', '')
            sid = seg.get('id', '')
            flags = []

            # 1. Italic leading lemma: starts with *Hebrew (single *, not **)
            if re.match(r'^\*(?!\*)[^\n]*[א-ת]', en):
                flags.append('ITALIC_LEAD_LEMMA')

            # 2. Broken mixed: *word **lemma**—*
            if re.search(r'^\*(?!\*)[^\n]+ \*\*[^*]+\*\*—\*(?!\*)', en):
                flags.append('BROKEN_MIX')

            # 3. Bare Hebrew at start (not **bold**, not אָמֵן. prefix)
            if re.match(r'^[א-ת]', en):
                # Allow "אָמֵן." plain prefix before **bold**
                if not re.match(r'^אָמֵן\. \*\*', en):
                    flags.append('BARE_HE_START')

            # 4. Italic Hebrew in body (scan after stripping bold spans and (*parens*))
            en_stripped = BOLD_RE.sub('', en)       # remove **bold** spans
            en_stripped = re.sub(r'\(\*[^)]+\*\)', '', en_stripped)  # remove (*...*) parens
            italic_hits = ITALIC_HE_RE.findall(en_stripped)
            # Filter: must contain Hebrew, and must not be pure English
            italic_he = [h for h in italic_hits if re.search(r'[א-ת]', h)
                         and not re.match(r'^[a-zA-Z]', h.strip())]
            if italic_he:
                flags.append(f'ITALIC_HE_INLINE:{italic_he[0][:50]}')

            # 5. Truncation check
            if not ends_well(en):
                flags.append(f'TRUNCATION')

            if not flags:
                clean += 1
            elif sid in KNOWN_LEGIT:
                legitimate.append((sid, flags))
            else:
                unresolved.append((sid, flags))

# ── report ────────────────────────────────────────────────────────────────────
print(f'=== POST-FIX VERIFICATION: shacharit.json commentaries ===')
print(f'Total:       {total}')
print(f'Clean:       {clean}')
print(f'Legitimate:  {len(legitimate)} (confirmed not errors)')
print(f'Unresolved:  {len(unresolved)}')
print()

if unresolved:
    print('=== UNRESOLVED FLAGS ===')
    for sid, flags in unresolved:
        print(f'  [{", ".join(flags)}] {sid}')
    print()
else:
    pct = (clean + len(legitimate)) / total * 100
    print(f'ALL {total} commentaries accounted for.')
    print(f'Confidence: {pct:.1f}% ({clean} clean + {len(legitimate)} confirmed-legitimate'
          f' out of {total})')

if legitimate:
    print()
    print('=== CONFIRMED LEGITIMATE ===')
    for sid, flags in legitimate:
        print(f'  {sid}: {flags}')
