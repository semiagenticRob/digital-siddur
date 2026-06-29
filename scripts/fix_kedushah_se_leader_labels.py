#!/usr/bin/env python3
"""
Insert small Hebrew rubric segments (חזן:/קר"ח:) before each Kedushah
Shemoneh Esrei verse that has a chazzan/kahal leader label in the print (p.63).
Using separate rubric segments (heText only) rather than inlineRubric so that
the existing display sizes are preserved and long verses aren't forced onto one line.

The ״ character (U+05F4 HEBREW PUNCTUATION GERSHAYIM) is used for the abbreviation
mark in קר״ח (kahal = congregation).

Insertions:
  חזן:  before se1-prayer-leumasam
  קר״ח: before se1-prayer-baruch-kvod
  חזן:  before se1-prayer-uvdivrei
  קר״ח: before se1-prayer-yimloch
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

INSERTIONS = [
    # (new_id, heText, insert_before_id)
    ('se1-rubric-chazan-leumasam',   'חזן:',    'se1-prayer-leumasam'),
    ('se1-rubric-kahal-baruch-kvod', 'קר״ח:', 'se1-prayer-baruch-kvod'),
    ('se1-rubric-chazan-uvdivrei',   'חזן:',    'se1-prayer-uvdivrei'),
    ('se1-rubric-kahal-yimloch',     'קר״ח:', 'se1-prayer-yimloch'),
]

def find_and_patch(node, insertions_remaining):
    if not insertions_remaining:
        return
    if isinstance(node, list):
        i = 0
        while i < len(node):
            item = node[i]
            if isinstance(item, dict):
                # Check if this item matches a target
                for ins_id, ins_he, before_id in list(insertions_remaining):
                    if item.get('id') == before_id:
                        new_seg = {'id': ins_id, 'type': 'rubric', 'heText': ins_he}
                        node.insert(i, new_seg)
                        insertions_remaining.remove((ins_id, ins_he, before_id))
                        print(f'  Inserted {ins_id} ("{ins_he}") before {before_id}')
                        i += 1  # skip the newly inserted item
                        break
                find_and_patch(item, insertions_remaining)
            i += 1
    elif isinstance(node, dict):
        for v in node.values():
            if isinstance(v, (dict, list)):
                find_and_patch(v, insertions_remaining)

remaining = list(INSERTIONS)
find_and_patch(data, remaining)

assert not remaining, f'Could not find insertion targets: {[r[2] for r in remaining]}'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Done. Inserted {len(INSERTIONS)} rubric segments.')
