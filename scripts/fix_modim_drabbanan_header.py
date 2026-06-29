#!/usr/bin/env python3
"""
Modim D'Rabbanan header fix.

PDF page 71 shows the subtitle "When thanking Hashem, an 'Amen' is not sufficient!"
is the header's English subtitle — same pattern as Binah ("Help me understand"),
Hodaah ("Thank You for everything—large and small!"), etc.

Current (wrong):
  header   enText = "Modim D'Rabbanan"   ← redundant transliteration
  transition enText = "When thanking Hashem, an \"Amen\" is not sufficient!"

After fix:
  header   enText = "When thanking Hashem, an \"Amen\" is not sufficient!"
  transition → DELETED
"""
import json

HEADER_ID     = 'se3-header-modim-drabbanan'
TRANSITION_ID = 'se3-transition-modim-drabbanan'
NEW_EN        = 'When thanking Hashem, an “Amen” is not sufficient!'

with open('src/content/shacharit.json') as f:
    data = json.load(f)

fixed_header = False
removed_transition = False

def patch(node):
    global fixed_header, removed_transition
    if isinstance(node, list):
        i = 0
        while i < len(node):
            item = node[i]
            if isinstance(item, dict):
                if item.get('id') == TRANSITION_ID:
                    node.pop(i)
                    removed_transition = True
                    print(f'  Deleted {TRANSITION_ID}')
                    continue
                patch(item)
            i += 1
    elif isinstance(node, dict):
        if node.get('id') == HEADER_ID:
            old = node.get('enText')
            node['enText'] = NEW_EN
            fixed_header = True
            print(f'  Header enText: {repr(old)} → {repr(NEW_EN)}')
        for v in node.values():
            if isinstance(v, (dict, list)):
                patch(v)

patch(data)
assert fixed_header, 'Header not found'
assert removed_transition, 'Transition not found'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
