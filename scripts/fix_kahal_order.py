#!/usr/bin/env python3
"""
Move the הקהל prayer segments to appear BEFORE the commentary (EXPLANATION box),
not after. Correct order per PDF p.97:
  se3-prayer-birkas-kohanim   (three blessings)
  se3-rubric-kahal            (הַקָּהָל: rubric)
  se3-prayer-adir-bamarom     (congregation prayer)
  se3-commentary-birkas-kohanim  (EXPLANATION box)
  se3-insight-shalom
"""
import json

TARGET_ORDER = [
    'se3-prayer-birkas-kohanim',
    'se3-rubric-kahal',
    'se3-prayer-adir-bamarom',
    'se3-commentary-birkas-kohanim',
    'se3-insight-shalom',
]

with open('src/content/shacharit.json') as f:
    data = json.load(f)

fixed = False

def patch(node):
    global fixed
    if isinstance(node, dict):
        if 'segments' in node and isinstance(node['segments'], list):
            segs = node['segments']
            ids = [s.get('id') for s in segs]
            if all(t in ids for t in TARGET_ORDER):
                # Pull out the five segments, reorder them, splice back
                positions = {t: ids.index(t) for t in TARGET_ORDER}
                # Remove all five from their current positions (high→low to preserve indices)
                removed = {}
                for t in sorted(TARGET_ORDER, key=lambda t: positions[t], reverse=True):
                    removed[t] = segs.pop(positions[t])
                # Insert them back in correct order at the earliest position
                insert_at = min(positions.values())
                for i, t in enumerate(TARGET_ORDER):
                    segs.insert(insert_at + i, removed[t])
                fixed = True
                print('  Reordered: ' + ' → '.join(TARGET_ORDER))
                return
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)
    elif isinstance(node, list):
        for x in node: patch(x)

patch(data)
assert fixed, 'Target segment sequence not found'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
