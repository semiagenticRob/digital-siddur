import json, copy

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shema'][0]
P = {p['id']: p for p in g['prayers']}

def seg(t, **kw):
    s = {'id': kw.pop('id'), 'type': t}
    if 'heText' in kw: s['heText'] = kw.pop('heText')
    if 'enText' in kw: s['enText'] = kw.pop('enText')
    for k, v in kw.items(): s[k] = v
    return s

# ---------------- BARCHU ----------------
b = P['p-barchu']['segments']

# Fix 1: italicize the leading speaker-cue parentheticals (i=3,5,7)
def italic_lead_paren(text):
    assert text.startswith('('), text
    close = text.index(')')
    return '*' + text[:close+1] + '*' + text[close+1:]

for i in (3, 5, 7):
    b[i]['enText'] = italic_lead_paren(b[i]['enText'])

# Fix 2: surface the chazzan/congregation speaker labels as rubrics
#        (they were stranded in the prayer enText, which never renders).
labels = {
    'barchu_chazzan':        'Chazzan:',
    'barchu_kahal':          'Congregation:',
    'barchu_chazzan_repeat': 'Chazzan repeats:',
}
new_b = []
for s in b:
    if s['id'] in labels:
        new_b.append(seg('rubric', id=s['id'] + '_label', enText=labels[s['id']]))
        s = copy.deepcopy(s); s.pop('enText', None)  # drop the dead label
    new_b.append(s)
P['p-barchu']['segments'] = new_b

# ---------------- BIRCHOS KRIAS SHEMA ----------------
k = P['p-birchos-krias-shema']['segments']

# Fix 3: Shema title — add the third running-title line of the five sub-passages
#        (matches the "/"-separated name-list style used in i=5 and i=58).
h33 = next(s for s in k if s['id'] == k[33]['id']) if False else k[33]
assert k[33]['type'] == 'header' and 'קְרִיאַת שְׁמַע' in k[33]['heText']
k[33]['heText'] = ('קְרִיאַת שְׁמַע / עַל מַלְכוּת שָׁמַיִם\n'
                   'שְׁמַע / בָּרוּךְ שֵׁם / וְאָהַבְתָּ / וְהָיָה / וַיֹּאמֶר')

# Fix 4: chazzan repetition — clean the conflated header, fix rubric, add prayer text.
assert k[55]['id'] == 'emes_vyatziv_header'
k[55].pop('heText', None)                       # header now carries only the English title
assert k[56]['id'] == 'emes_vyatziv_chazan_rubric'
k[56]['heText'] = 'הַשַּׁ"ץ חוֹזֵר וְאוֹמֵר:'
k[56]['enText'] = 'The chazzan repeats and says:'
prayer_line = seg('prayer', id='emes_vyatziv_chazan_line', heText='יְהוָה אֱלֹהֵיכֶם אֱמֶת:')
# insert immediately after the rubric (index 57)
ins = next(i for i, s in enumerate(k) if s['id'] == 'emes_vyatziv_chazan_rubric') + 1
k.insert(ins, prayer_line)

# Fix 5: move the three Shema insights from the very end to beside the Shema
#        (after the Baruch Shem "Quietly" commentary, before the Va'ahavta intro).
insight_ids = [s['id'] for s in k if s['type'] == 'insight'][-3:]
moved = [s for s in k if s['id'] in insight_ids]
k = [s for s in k if s['id'] not in insight_ids]
anchor = next(i for i, s in enumerate(k)
              if s['type'] == 'commentary' and s.get('enText', '').startswith('בָּרוּךְ שֵׁם'))
for off, s in enumerate(moved):
    k.insert(anchor + 1 + off, s)
P['p-birchos-krias-shema']['segments'] = k

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('p-barchu segs:', len(P['p-barchu']['segments']))
print('p-birchos-krias-shema segs:', len(P['p-birchos-krias-shema']['segments']))
print('OK')
