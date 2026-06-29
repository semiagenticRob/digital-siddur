#!/usr/bin/env python3
"""Add the missing 'Appendix N' label header to appendices 4, 6, 7 and split
appendix 8's combined header — matching the two-level header pattern used by
appendices 1-3, 5, 9-12 (verified APPENDIX N + TITLE in the print). Headers
render textTransform:uppercase, so 'Appendix N' displays as 'APPENDIX N'."""
import json

d = json.load(open('src/content/appendices.json'))
apps = d if isinstance(d, list) else d['appendices']
def get(n):
    for a in apps:
        if a.get('number') == n: return a

# Apps 4,6,7: prepend an 'Appendix N' header before the existing title header.
for n, hid in [(4, 'a4-header'), (6, 'a6-header'), (7, 'a7-header')]:
    a = get(n); segs = a['segments']
    assert segs[0].get('id') == hid, f'app {n}: expected {hid} first, got {segs[0].get("id")}'
    assert not any(s.get('id') == f'a{n}-header-appendix' for s in segs), f'app {n} label already present'
    segs.insert(0, {'id': f'a{n}-header-appendix', 'type': 'header', 'enText': f'Appendix {n}'})
    print(f'App {n}: inserted "Appendix {n}" label header')

# App 8: split 'Appendix 8: Our Material World' into two headers.
a8 = get(8); segs = a8['segments']
h = segs[0]
assert h.get('id') == 'a8-header' and 'Our Material World' in h.get('enText', ''), 'app 8 header unexpected'
h['enText'] = 'Our Material World'
segs.insert(0, {'id': 'a8-header-appendix', 'type': 'header', 'enText': 'Appendix 8'})
print('App 8: split into "Appendix 8" + "Our Material World"')

json.dump(d, open('src/content/appendices.json', 'w'), ensure_ascii=False, indent=2)
print('Done.')
