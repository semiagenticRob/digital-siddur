#!/usr/bin/env python3
"""
Fix two errors in se1-prayer-kedushas-hashem heText (PDF p.63):
  1. The sof-pasuk (:) is after the parenthetical — PDF shows it before.
  2. The ASCII " (U+0022) in בעשי"ת is bidi-neutral, so the bidi algorithm
     visually separates it from the ת, making an apparent extra letter.
     Replace with Hebrew gershayim ״ (U+05F4) which is RTL-classified.

Current tail: ...הָאֵל הַקָּדוֹשׁ (בעשי"ת הַמֶּלֶךְ הַקָּדוֹשׁ):
Correct tail: ...הָאֵל הַקָּדוֹשׁ: (בעשי״ת הַמֶּלֶךְ הַקָּדוֹשׁ)
"""
import json

TARGET_ID = 'se1-prayer-kedushas-hashem'

WRONG_TAIL  = ' (בעשי"ת הַמֶּלֶךְ הַקָּדוֹשׁ):'
FIXED_TAIL  = ': (בעשי״ת הַמֶּלֶךְ הַקָּדוֹשׁ)'

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def patch(node):
    if isinstance(node, list):
        for x in node: patch(x)
    elif isinstance(node, dict):
        if node.get('id') == TARGET_ID:
            he = node.get('heText', '')
            assert he.endswith(WRONG_TAIL), \
                f'Unexpected tail: {repr(he[-60:])}'
            node['heText'] = he[:-len(WRONG_TAIL)] + FIXED_TAIL
            print(f'  Fixed {TARGET_ID}')
            print(f'  New tail: {repr(node["heText"][-50:])}')
            return
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
