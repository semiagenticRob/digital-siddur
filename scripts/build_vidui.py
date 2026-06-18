import json

OUT = '/private/tmp/claude-501/-Users-robertwarren/d6a0926a-9f8b-467d-b655-0d748c9d2c46/tasks/wtrj6p1dd.output'
PATH = 'src/content/shacharit.json'

vid = json.load(open(OUT))['result']['segments']

segments = []
for i, s in enumerate(vid, 1):
    seg = {'id': f'vidui-{i}', 'type': s['type']}
    he = s.get('heText', '')
    en = s.get('enText', '').replace(' — ', '—')   # normalize to the siddur's em-dash style
    if he:
        seg['heText'] = he
    if en:
        seg['enText'] = en
    segments.append(seg)

prayer = {
    'id': 'p-vidui',
    'heTitle': 'וִדּוּי',
    'enTitle': 'Vidui',
    'segments': segments,
}

d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-tachanun'][0]
# insert before Avinu Malkeinu (the Vidui precedes it in the print, siddur 76-78)
idx = next(i for i, p in enumerate(g['prayers']) if p['id'] == 'avinu_malkeinu')
g['prayers'].insert(idx, prayer)

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('inserted p-vidui with', len(segments), 'segments at position', idx)
print('g-tachanun prayers:', [p['id'] for p in g['prayers']])
# sanity: 13 middos present
middos = [s for s in segments if s['type'] == 'prayer' and s.get('heText', '').endswith('.') and len(s['heText']) < 25]
print('13 attributes captured:', len(middos))
