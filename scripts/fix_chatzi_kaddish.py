import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shema'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-barchu'][0]
segs = p['segments']
by = {s['id']: s for s in segs}

# 1) Merge the four Kaddish Hebrew fragments into one continuous block (as printed).
kad_he = ' '.join(by[i]['heText'] for i in ['kaddish_1', 'kaddish_2', 'kaddish_3', 'kaddish_4'])
by['kaddish_1']['heText'] = kad_he
by['kaddish_1'].pop('condition', None)   # the לְעֵלָּא portion is said all year (AYT variant is inline)

# 2) Merge the three Kaddish glosses into one running commentary, lemmas inline (em-dash).
lemma1 = by['kaddish_1_gloss']['heText']                       # יִתְגַּדַּל וְיִתְקַדַּשׁ שְׁמֵהּ רַבָּא
lemma2 = 'אָמֵן. ' + by['kaddish_2']['heText'].rstrip(':')      # אָמֵן. יְהֵא שְׁמֵהּ רַבָּא מְבָרַךְ...עָלְמַיָּא
lemma3 = by['kaddish_3_gloss']['heText']                       # יִתְבָּרַךְ וְיִשְׁתַּבַּח
en1 = by['kaddish_1_gloss']['enText']
en2 = by['kaddish_2_gloss']['enText']
en3 = by['kaddish_3_gloss']['enText']
by['kaddish_1_gloss']['enText'] = f'{lemma1}—{en1} {lemma2}—{en2} {lemma3}—{en3}'
by['kaddish_1_gloss'].pop('heText', None)

# 3) Barchu glosses: bring lemma inline + italicize the leading parenthetical aside.
def lemma_inline_italic(seg_id):
    s = by[seg_id]
    lemma = s['heText']
    en = s['enText']
    assert en.startswith('('), en
    close = en.index(')')
    en = '*' + en[:close + 1] + '*' + en[close + 1:]   # italicize "(...)" aside
    s['enText'] = f'{lemma}—{en}'
    s.pop('heText', None)

lemma_inline_italic('barchu_gloss_1')
lemma_inline_italic('barchu_gloss_2')

# 4) Rebuild the segment list, dropping the now-merged fragments.
drop = {'kaddish_2', 'kaddish_3', 'kaddish_4', 'kaddish_2_gloss', 'kaddish_3_gloss'}
p['segments'] = [s for s in segs if s['id'] not in drop]

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
for s in p['segments']:
    print(s['type'], s['id'])
print('OK; segs:', len(p['segments']))
