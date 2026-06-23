#!/usr/bin/env python3
"""
Move emes_vyatziv_chazan_rubric into the prayer as an inlineRubric field,
and add display:true so the verse is oversized and centered per the print.
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def find_prayer_node(node, pid):
    if isinstance(node, dict):
        if node.get('id') == pid and isinstance(node.get('segments'), list):
            return node
        for v in node.values():
            r = find_prayer_node(v, pid)
            if r: return r
    elif isinstance(node, list):
        for x in node:
            r = find_prayer_node(x, pid)
            if r: return r

# Find the parent prayer container (p-birchos-krias-shema or whichever holds these)
# We search all prayers for the segment IDs
def find_segments_parent(node):
    if isinstance(node, dict):
        segs = node.get('segments')
        if isinstance(segs, list):
            ids = [s['id'] for s in segs]
            if 'emes_vyatziv_chazan_rubric' in ids and 'emes_vyatziv_chazan_line' in ids:
                return segs
        for v in node.values():
            r = find_segments_parent(v)
            if r is not None: return r
    elif isinstance(node, list):
        for x in node:
            r = find_segments_parent(x)
            if r is not None: return r

segs = find_segments_parent(data)
assert segs is not None, 'Could not find segments list containing both IDs'

idx_rubric = next(i for i, s in enumerate(segs) if s['id'] == 'emes_vyatziv_chazan_rubric')
idx_prayer = next(i for i, s in enumerate(segs) if s['id'] == 'emes_vyatziv_chazan_line')

rubric = segs[idx_rubric]
prayer = segs[idx_prayer]

assert rubric['type'] == 'rubric'
assert prayer['type'] == 'prayer'

rubric_he = rubric['heText']
assert rubric_he, 'No heText on rubric'

# Add inlineRubric and display:true to the prayer
prayer['inlineRubric'] = rubric_he
prayer['display'] = True

print(f'Set prayer inlineRubric: {rubric_he}')
print(f'Set prayer display: True')

# Remove the standalone rubric segment
segs.pop(idx_rubric)
print(f'Removed emes_vyatziv_chazan_rubric')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
