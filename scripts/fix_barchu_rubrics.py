import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shema'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-barchu'][0]
by = {s['id']: s for s in p['segments']}

# The print keeps the Barchu speaker designations in Hebrew (חזן / קהל / חזן),
# set small to the right of each line. The app had translated them to English.
# Convert each rubric to a Hebrew (heText) rubric so it renders in the print's style.
labels = {
    'Chazzan:': 'חַזָּן:',
    'Congregation:': 'קָהָל:',
    'Chazzan repeats:': 'חַזָּן:',
}

fixed = 0
for s in p['segments']:
    if s['type'] == 'rubric' and s.get('enText') in labels:
        s['heText'] = labels[s['enText']]
        del s['enText']
        fixed += 1

assert fixed == 3, f'expected 3 speaker rubrics, fixed {fixed}'

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
for s in p['segments']:
    print(s['type'], '|', repr(s.get('heText', '')[:40]), '|', repr(s.get('enText', '')[:40]))
print('OK; converted', fixed, 'rubrics to Hebrew')
