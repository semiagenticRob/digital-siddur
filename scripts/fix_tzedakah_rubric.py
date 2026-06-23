#!/usr/bin/env python3
"""
Move (נוֹהֲגִים לִתֵּת צְדָקָה) from a standalone rubric into the
end of the preceding prayer's heText so it renders inline in the
same color as the prayer text, matching the print layout.
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def find_prayer(node, pid):
    if isinstance(node, dict):
        if node.get('id') == pid and isinstance(node.get('segments'), list):
            return node
        for v in node.values():
            r = find_prayer(v, pid)
            if r: return r
    elif isinstance(node, list):
        for x in node:
            r = find_prayer(x, pid)
            if r: return r

p = find_prayer(data, 'p-pesukei-dzimrah')
segs = p['segments']

# Find the prayer and the rubric
idx7  = next(i for i, s in enumerate(segs) if s['id'] == 'azyashir-7')
idx10 = next(i for i, s in enumerate(segs) if s['id'] == 'azyashir-10')

prayer = segs[idx7]
rubric = segs[idx10]

assert prayer['type'] == 'prayer'
assert rubric['type'] == 'rubric'
assert rubric['heText'] == '(נוֹהֲגִים לִתֵּת צְדָקָה)', rubric['heText']

# Append the parenthetical to the prayer heText (space + parenthetical)
prayer['heText'] = prayer['heText'] + ' (נוֹהֲגִים לִתֵּת צְדָקָה)'
print(f'Appended parenthetical to azyashir-7 heText')
print(f'  now ends: ...{prayer["heText"][-45:]}')

# Remove the rubric segment
segs.pop(idx10)
print(f'Removed azyashir-10 rubric segment')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
