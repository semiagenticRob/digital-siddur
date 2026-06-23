#!/usr/bin/env python3
"""
Add rubric labels for Avinu Malkeinu 4a/4b two-column variant section.
Print p. 79 (siddur p. 79) shows column headers:
 "During Aseres Yemei Teshuvah say:" → line 4a (חַדֵּשׁ עָלֵינוּ שָׁנָה טוֹבָה)
 "On fast days say:"                 → line 4b (בָּרֵךְ עָלֵינוּ שָׁנָה טוֹבָה)
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

am = find_prayer(data, 'avinu_malkeinu')
segs = am['segments']

# Find 4a
idx_4a = next(i for i, s in enumerate(segs) if s['id'] == 'avinu_malkeinu_4a')
assert segs[idx_4a]['heText'].startswith('אָבִינוּ מַלְכֵּנוּ חַדֵּשׁ'), segs[idx_4a]['heText'][:40]

idx_4b = next(i for i, s in enumerate(segs) if s['id'] == 'avinu_malkeinu_4b')
assert segs[idx_4b]['heText'].startswith('אָבִינוּ מַלְכֵּנוּ בָּרֵךְ'), segs[idx_4b]['heText'][:40]

print(f'4a at i={idx_4a}, 4b at i={idx_4b}')

# Insert rubric "During Aseres Yemei Teshuvah say:" before 4a
segs.insert(idx_4a, {
    'id': 'avinu_malkeinu_rubric_ayt_4',
    'type': 'rubric',
    'enText': 'During Aseres Yemei Teshuvah say:',
})
print('Inserted AYT rubric before 4a')

# 4b is now at idx_4b + 1 due to the insertion
idx_4b += 1
segs.insert(idx_4b, {
    'id': 'avinu_malkeinu_rubric_fast_4',
    'type': 'rubric',
    'enText': 'On fast days say:',
})
print('Inserted fast-day rubric before 4b')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Done. Run: npm run check')
