#!/usr/bin/env python3
"""WORKAROUND for the RN/iOS render anomaly that clips commentary_shabbos (Shesh
Zechiros) on-device (text renders at intrinsic width, hiding the end of the line).
The JSON content is correct; this inserts explicit line breaks (~30 chars/line, so
each line fits even at the max font step +4 ≈ 1.22x, never needing to wrap → the
bug can't trigger) so the full commentary is VISIBLE — satisfying check 7. English
commentary only (not sacred Hebrew prayer text). REMOVE these breaks once the
renderer is fixed natively (see REVIEW_QUEUE). commentary_har_sinai etc. wrap fine
and are untouched."""
import json, re
ORIG = '**שַׁבָּת**—We must remember that it is the power and sanctity of Shabbos that gives us the “energy” to remain spiritually strong during the week.'
NEW = ('**שַׁבָּת**—We must remember\n'
       'that it is the power and\n'
       'sanctity of Shabbos that gives\n'
       'us the “energy” to remain\n'
       'spiritually strong during\n'
       'the week.')

def skel(s): return re.sub(r'[^A-Za-zא-ת]', '', s or '')

d = json.load(open('src/content/shacharit.json'))
def find(n):
    if isinstance(n, dict):
        if n.get('id') == 'commentary_shabbos': return n
        for v in n.values():
            r = find(v)
            if r: return r
    elif isinstance(n, list):
        for x in n:
            r = find(x)
            if r: return r
s = find(d)
assert s and s['enText'] == ORIG, f'unexpected current text: {s.get("enText")!r}'
# safety: the new text must be identical except for the inserted newlines (no words changed)
assert skel(NEW) == skel(ORIG), 'word content changed — abort'
s['enText'] = NEW
json.dump(d, open('src/content/shacharit.json', 'w'), ensure_ascii=False, indent=2)
print('Applied display line-breaks to commentary_shabbos (content identical, breaks only).')
