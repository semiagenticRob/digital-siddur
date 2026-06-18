import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-pesukei-dzimrah'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-pesukei-dzimrah'][0]
segs = p['segments']
by = {s['id']: s for s in segs}

# azyashir-12 currently bundles both lemmas. Split into two boxes that match the
# two Hebrew segments: azyashir-13 (אַתָּה הוּא) and azyashir-14 (וְכָרוֹת עִמּוֹ הַבְּרִית).
by['azyashir-12']['enText'] = (
    "אַתָּה הוּא—The Navi Nechemiah proclaims: You, Hashem, alone, created the "
    "entire universe, and You chose Avraham! You saved him from Ur Kasdim."
)
part_b = {
    'id': 'azyashir-12b',
    'type': 'commentary',
    'heText': '',
    'enText': (
        "כְּרוֹת עִמּוֹ הַבְּרִית—and You established an everlasting covenant with his "
        "descendants (*that's us!*). You saw the suffering of Bnei Yisrael in Egypt, "
        "and You performed great public miracles—culminating with splitting the sea "
        "in order to save us, Your nation (*for a great mission to the world*)."
    ),
}

# insert part B immediately after the second prayer segment (azyashir-14)
ins = next(i for i, s in enumerate(segs) if s['id'] == 'azyashir-14') + 1
segs.insert(ins, part_b)

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
i = next(i for i, s in enumerate(segs) if s['id'] == 'azyashir-13')
for s in segs[i:i+4]:
    print(s['type'], s['id'], '|', (s.get('heText') or s.get('enText') or '')[:50])
print('OK')
