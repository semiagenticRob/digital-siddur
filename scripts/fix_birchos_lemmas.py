import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shema'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-birchos-krias-shema'][0]
S = p['segments']

# These First/Second Brachah commentaries stored their opening Hebrew lemma in
# heText, which commentary segments never render — so the Hebrew was invisible
# (and seg 11, whose only Hebrew was that lemma, showed no Hebrew at all).
# Move each lemma inline to the start of enText (em-dash, no surrounding space),
# matching the print and the convention used elsewhere in the file.
# Two of them carry an italic aside before the lemma in the print.
ASIDES = {
    9: '*(Our praise of Hashem:)* ',
    11: "*(The angels' praise of Hashem:)* ",
}
EXPECTED_LEMMA = {
    7:  'בָּרוּךְ אַתָּה יְהוָֹה',
    9:  'הַמֵּאִיר לָאָרֶץ',
    11: 'תִּתְבָּרַךְ צוּרֵנוּ',
    13: 'אֶת שֵׁם הָאֵל הַמֶּלֶךְ',
    19: 'וְהָאוֹפַנִּים',
    21: 'בָּרוּךְ כְּבוֹד יְהוָֹה',
    24: 'לָאֵל בָּרוּךְ נְעִימוֹת יִתֵּנוּ',
    30: 'אַהֲבָה רַבָּה',
    32: 'וַהֲבִיאֵנוּ לְשָׁלוֹם מֵאַרְבַּע כַּנְפוֹת הָאָרֶץ',
}

for idx, expected in EXPECTED_LEMMA.items():
    s = S[idx]
    assert s['type'] == 'commentary', f'idx {idx} is {s["type"]}'
    lemma = s.get('heText', '')
    assert lemma == expected, f'idx {idx}: heText {lemma!r} != expected {expected!r}'
    en = s['enText']
    # guard against double-application (already starts with this lemma or its aside)
    assert not en.startswith(lemma) and not en.startswith(ASIDES.get(idx, '\0')), \
        f'idx {idx}: enText already begins with lemma/aside: {en[:40]!r}'
    s['enText'] = f'{ASIDES.get(idx, "")}{lemma}—{en}'
    s['heText'] = ''

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
for idx in EXPECTED_LEMMA:
    print(idx, '->', repr(S[idx]['enText'][:80]))
print('OK; inlined', len(EXPECTED_LEMMA), 'lemmas')
