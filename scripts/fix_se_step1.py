import json, re

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))

# ---- 1) Strip literal markdown asterisks from rubrics (rendered plain, already italic) ----
stripped = 0
for g in d['groups']:
    for p in g['prayers']:
        for s in p['segments']:
            if s['type'] == 'rubric':
                for k in ('heText', 'enText'):
                    if s.get(k) and '*' in s[k]:
                        s[k] = s[k].replace('*', '')
                        stripped += 1

# ---- Shemoneh Esrei specific fixes ----
g = [g for g in d['groups'] if g['id'] == 'g-shemoneh-esrei'][0]
segs = g['prayers'][0]['segments']
by = {s['id']: s for s in segs}

# 2) Merge the geulah commentary that was split mid-italic across a chunk boundary,
#    and repair the broken italic span "(because ... it" + "is a chillul Hashem)".
a76 = by['se1-commentary-geulah']['enText']
a77 = by['se2-geulah-commentary-end']['enText']
head76 = a76.rsplit('*(', 1)[0]                       # "...for the glory of Your Name "
paren1 = a76.rsplit('*(', 1)[1].rstrip('*').strip()   # "because ... it"
m = re.match(r'\*(.*?)\*\)(.*)', a77, re.S)
paren2, rest77 = m.group(1).strip(), m.group(2)       # "is a chillul Hashem", ", for You..."
by['se1-commentary-geulah']['enText'] = (
    f"{head76}*({paren1} {paren2})*{rest77}"
)
segs.remove(by['se2-geulah-commentary-end'])

# 3) Remove the stray asterisk in the refuah commentary: "...emotional*).* For" -> "*). For"
r = by['se2-refuah-commentary']
assert '*).* For You' in r['enText'], r['enText'][-120:]
r['enText'] = r['enText'].replace('*).* For You', '*). For You')

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('rubric fields stripped of asterisks:', stripped)
print('merged geulah commentary:', by['se1-commentary-geulah']['enText'][:90], '...')
print('refuah odd-asterisk fixed:', '*).* ' not in r['enText'])
