import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-pesukei-dzimrah'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-pesukei-dzimrah'][0]
segs = p['segments']
by = {s['id']: s for s in segs}

# 1) Split the combined explanation at the בָּרוּךְ אַתָּה brachah gloss.
cmt = by['pz4-cmt-yishtabach']
SPLIT = 'בָּרוּךְ אַתָּה יְהֹוָה—'
assert SPLIT in cmt['enText']
part1, part2 = cmt['enText'].split(SPLIT, 1)
part1 = part1.strip().replace('*(שֶׁבַר)*', '*(שִׁמְךָ)*')   # fix garbled gloss
cmt['enText'] = part1
baruch_cmt = {'id': 'pz4-cmt-baruch-atah', 'type': 'commentary',
              'heText': '', 'enText': SPLIT + part2.strip()}

# 2) Clean the FAQ to match the print, and relocate it after the brachah's gloss,
#    immediately before the "During Aseres Yemei Teshuvah" rubric.
faq = by['pz4-faq-yishtabach']
faq['enText'] = (
    'FAQ: What does it mean that Hashem הַבּוֹחֵר בְּשִׁירֵי זִמְרָה—takes pleasure in '
    'songs of praise? Hashem is not human; what does it mean that He takes pleasure? '
    'ANSWER: Good question! See Appendix 10.'
)

# remove the FAQ from its current spot, then splice [brachah-gloss, faq] after the brachah
segs.remove(faq)
ins = next(i for i, s in enumerate(segs) if s['id'] == 'pz4-pry-baruch-atah') + 1
segs[ins:ins] = [baruch_cmt, faq]

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
start = next(i for i, s in enumerate(segs) if s['id'] == 'pz4-pry-yishtabach-1')
for s in segs[start:start+6]:
    print(s['type'], s['id'], '|', (s.get('heText') or s.get('enText') or '')[:46])
print('OK')
