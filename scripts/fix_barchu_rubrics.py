import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shema'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-barchu'][0]
segs = p['segments']

# In the print the speaker designation sits INLINE at the right edge of each
# Barchu line — plain consonants, with a colon (חזן: / קהל: / חזן:), no nikud.
# That matches the app's own Hallel convention of embedding the label in the
# prayer's heText. Replace the stacked rubric segments with inline labels.

# Locate the three prayer lines of Barchu (they follow the בָּרְכוּ header).
hdr = next(i for i, s in enumerate(segs) if s['type'] == 'header' and s.get('heText') == 'בָּרְכוּ')
prayers = [s for s in segs[hdr:] if s['type'] == 'prayer'][:3]
assert prayers[0]['heText'].startswith('בָּרְכוּ אֶת'), prayers[0]['heText']
assert prayers[1]['heText'].startswith('בָּרוּךְ'), prayers[1]['heText']
assert prayers[2]['heText'].startswith('בָּרוּךְ'), prayers[2]['heText']

labels = ['חזן: ', 'קהל: ', 'חזן: ']
for prayer, label in zip(prayers, labels):
    if not prayer['heText'].startswith(('חזן', 'קהל')):   # idempotent
        prayer['heText'] = label + prayer['heText']

# Drop the now-redundant speaker rubrics (whether English or the Hebrew ones
# this script previously created).
speaker_rubric_text = {'Chazzan:', 'Congregation:', 'Chazzan repeats:',
                       'חַזָּן:', 'קָהָל:', 'חזן:', 'קהל:'}
p['segments'] = [
    s for s in segs
    if not (s['type'] == 'rubric'
            and (s.get('enText') in speaker_rubric_text
                 or s.get('heText') in speaker_rubric_text))
]

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
for s in p['segments']:
    print(s['type'], '|', repr(s.get('heText', '')[:48]), '|', repr(s.get('enText', '')[:36]))
