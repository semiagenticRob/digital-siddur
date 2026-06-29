#!/usr/bin/env python3
"""
Audit fixes for src/content/mussaf-chol-hamoed.json
Findings applied:
  Check 1 (mch1-sec2-comm3): Append missing text continuation (truncated mid-sentence)
  Check 3 (seg-mch2-056):    Merge seg-mch2-056 and seg-2 to fix dangling split
Skipped:
  Check 5 (seg-mch2-001):    False positive — no separate commentary needed;
                               the gap is the same truncation as check 1.
  Check 1 (mch1-header):     Display finding — orchestrator handles.
"""
import json
import re

FILE = 'src/content/mussaf-chol-hamoed.json'

# ── helpers ──────────────────────────────────────────────────────────────────

def strip_md(s):
    """Strip markdown bold/italic markers for strip-diff verification."""
    return re.sub(r'\*+', '', s)

def find_seg(node, seg_id):
    if isinstance(node, dict):
        if node.get('id') == seg_id:
            return node
        for v in node.values():
            r = find_seg(v, seg_id)
            if r:
                return r
    elif isinstance(node, list):
        for x in node:
            r = find_seg(x, seg_id)
            if r:
                return r
    return None

def find_parent_segments(node, seg_id):
    """Return the segments list that contains seg_id, and the index."""
    if isinstance(node, dict):
        if 'segments' in node and isinstance(node['segments'], list):
            for i, s in enumerate(node['segments']):
                if isinstance(s, dict) and s.get('id') == seg_id:
                    return node['segments'], i
        for v in node.values():
            r = find_parent_segments(v, seg_id)
            if r:
                return r
    elif isinstance(node, list):
        for x in node:
            r = find_parent_segments(x, seg_id)
            if r:
                return r
    return None

# ── load ─────────────────────────────────────────────────────────────────────

with open(FILE) as f:
    data = json.load(f)

# ═══════════════════════════════════════════════════════════════════════════
# FIX 1 — mch1-sec2-comm3: append missing continuation text
# PDF p.251-252 (print pp.227-228): commentary ends mid-sentence
# "...reveal to the" — continues with "whole world the glory..."
# ═══════════════════════════════════════════════════════════════════════════

TARGET_1 = 'mch1-sec2-comm3'
seg1 = find_seg(data, TARGET_1)
assert seg1 is not None, f'Segment {TARGET_1} not found'
assert seg1.get('type') == 'commentary', f'{TARGET_1} is not a commentary segment'

EXPECTED_1_TAIL = 'and reveal to the'
CURRENT_EN_1 = seg1['enText']
assert CURRENT_EN_1.endswith(EXPECTED_1_TAIL), (
    f'Unexpected tail of {TARGET_1}: ...{CURRENT_EN_1[-60:]!r}'
)

APPEND_TEXT = (
    ' whole world the glory and power of Your Kingship over us, Bnei Yisrael. '
    'Please gather all Jews from all over the world out of our exile and bring us all '
    'to Yerushalayim and to the rebuilt Beis Hamikdash with songs, joy, and happiness '
    '(*not through pain, war, and suffering*). And once we are there, we will gladly '
    'bring all the appropriate korbanos; and specifically, the ones for today: '
    '(Shabbos/) Pesach/Shavuos/Sukkos/Shemini Atzeres/Simchas Torah, as is written '
    'in Your Torah.'
)

OLD_EN_1 = CURRENT_EN_1
NEW_EN_1 = CURRENT_EN_1 + APPEND_TEXT
seg1['enText'] = NEW_EN_1

# Strip-diff verification: the new text should be strictly longer, same stem
old_plain = strip_md(OLD_EN_1)
new_plain = strip_md(NEW_EN_1)
assert new_plain.startswith(old_plain), 'Strip-diff mismatch on mch1-sec2-comm3'
assert 'whole world the glory and power' in new_plain
assert 'in Your Torah.' in new_plain
print(f'[FIX 1] {TARGET_1}: appended {len(APPEND_TEXT)} chars of continuation text.')

# ═══════════════════════════════════════════════════════════════════════════
# FIX 3 — seg-mch2-056 + seg-2: merge to fix dangling "and for Your"
# PDF p.256 (print p.232): left-column commentary flows uninterrupted;
# the Insight sidebar is at the same level but does NOT interrupt the prose.
# Strategy: append seg-2's enText to seg-mch2-056, then remove seg-2.
# The insight (seg-1) sits between them in the array; after the merge it
# will follow the unified commentary, which matches the PDF sidebar layout.
# ═══════════════════════════════════════════════════════════════════════════

TARGET_3A = 'seg-mch2-056'
TARGET_3B = 'seg-2'

seg3a = find_seg(data, TARGET_3A)
seg3b = find_seg(data, TARGET_3B)
assert seg3a is not None, f'Segment {TARGET_3A} not found'
assert seg3b is not None, f'Segment {TARGET_3B} not found'
assert seg3a.get('type') == 'commentary', f'{TARGET_3A} is not commentary'
assert seg3b.get('type') == 'commentary', f'{TARGET_3B} is not commentary'

EXPECTED_3A_TAIL = 'and for Your'
CURRENT_EN_3A = seg3a['enText']
assert CURRENT_EN_3A.endswith(EXPECTED_3A_TAIL), (
    f'Unexpected tail of {TARGET_3A}: ...{CURRENT_EN_3A[-60:]!r}'
)

EXPECTED_3B_START = '*(hidden)*'
CURRENT_EN_3B = seg3b['enText']
assert CURRENT_EN_3B.startswith(EXPECTED_3B_START), (
    f'Unexpected start of {TARGET_3B}: {CURRENT_EN_3B[:60]!r}'
)

# Merge: append a space + seg-2 text to seg-mch2-056
OLD_EN_3A = CURRENT_EN_3A
NEW_EN_3A = CURRENT_EN_3A + ' ' + CURRENT_EN_3B
seg3a['enText'] = NEW_EN_3A

# Strip-diff: new text must start with the old text (plain)
old3a_plain = strip_md(OLD_EN_3A)
new3a_plain = strip_md(NEW_EN_3A)
assert new3a_plain.startswith(old3a_plain), 'Strip-diff mismatch on seg-mch2-056'
assert 'hidden' in new3a_plain
assert 'placed our hope in You.' in new3a_plain
print(f'[FIX 3a] {TARGET_3A}: appended continuation from {TARGET_3B}.')

# Remove seg-2 from its parent segments list
result = find_parent_segments(data, TARGET_3B)
assert result is not None, f'Could not find parent segments list for {TARGET_3B}'
parent_segs, idx_3b = result
removed = parent_segs.pop(idx_3b)
assert removed.get('id') == TARGET_3B, f'Removed wrong segment: {removed.get("id")}'
print(f'[FIX 3b] Removed segment {TARGET_3B} (now merged into {TARGET_3A}).')

# ═══════════════════════════════════════════════════════════════════════════
# WRITE
# ═══════════════════════════════════════════════════════════════════════════

with open(FILE, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nDone. Wrote {FILE}')
