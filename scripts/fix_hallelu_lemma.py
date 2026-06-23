#!/usr/bin/env python3
"""
Fix pz3-148-c1: add ', הַלְלוּהוּ בַּמְּרוֹמִים' to the opening bold lemma.
Print shows: הַלְלוּיָהּ, הַלְלוּ אֶת יְהֹוָה מִן הַשָּׁמַיִם, הַלְלוּהוּ בַּמְּרוֹמִים
Stored has:  הַלְלוּיָהּ, הַלְלוּ אֶת יְהֹוָה מִן הַשָּׁמַיִם  (missing the last clause)
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

# Get the commentary segment
pz3 = find_prayer(data, 'p-pesukei-dzimrah')
segs = pz3['segments']
c1 = next(s for s in segs if s['id'] == 'pz3-148-c1')

old_lemma = '**הַלְלוּיָהּ, הַלְלוּ אֶת יְהֹוָה מִן הַשָּׁמַיִם**'
new_lemma = '**הַלְלוּיָהּ, הַלְלוּ אֶת יְהֹוָה מִן הַשָּׁמַיִם, הַלְלוּהוּ בַּמְּרוֹמִים**'

old_en = c1['enText']
assert old_lemma in old_en, f'Lemma not found in enText:\n{old_en[:120]}'

c1['enText'] = old_en.replace(old_lemma, new_lemma, 1)

# Verify the fix
assert new_lemma in c1['enText'], 'Fix not applied'
assert old_lemma not in c1['enText'], 'Old lemma still present'

print(f'Fixed pz3-148-c1 opening lemma:')
print(f'  was: {old_lemma}')
print(f'  now: {new_lemma}')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
