#!/usr/bin/env python3
"""
Convert bare page-number references to tappable prayer links (or plain text).

se4-end-rubric: "On Rosh Chodesh, Chanukah, and Chol Hamoed, Say Hallel—page 204."
  → "On Rosh Chodesh, Chanukah, and Chol Hamoed, Say Hallel."
  (Hallel is a separate service; no cross-service link per design decision)

se4-tachanun-xref-rubric: "Tachanun—page 83; Avinu Malkeinu—page 78."
  → "[Tachanun](prayer:shacharit/p-tachanun); [Avinu Malkeinu](prayer:shacharit/avinu_malkeinu)"
  (Both prayers live in shacharit.json; tapping navigates to that prayer)
"""
import json

CHANGES = {
    'se4-end-rubric': (
        'On Rosh Chodesh, Chanukah, and Chol Hamoed, Say Hallel—page 204.',
        'On Rosh Chodesh, Chanukah, and Chol Hamoed, Say Hallel.',
    ),
    'se4-tachanun-xref-rubric': (
        'Tachanun—page 83; Avinu Malkeinu—page 78.',
        '[Tachanun](prayer:shacharit/p-tachanun); [Avinu Malkeinu](prayer:shacharit/avinu_malkeinu)',
    ),
}

with open('src/content/shacharit.json') as f:
    data = json.load(f)

fixed = set()

def patch(node):
    if isinstance(node, dict):
        seg_id = node.get('id')
        if seg_id in CHANGES:
            old, new = CHANGES[seg_id]
            assert node.get('enText') == old, f'{seg_id}: expected {old!r}, got {node.get("enText")!r}'
            node['enText'] = new
            fixed.add(seg_id)
            print(f'  Updated {seg_id}')
        for v in node.values():
            if isinstance(v, (dict, list)):
                patch(v)
    elif isinstance(node, list):
        for x in node:
            patch(x)

patch(data)
assert fixed == set(CHANGES), f'Missing: {set(CHANGES) - fixed}'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
