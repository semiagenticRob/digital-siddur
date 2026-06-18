import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-pesukei-dzimrah'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-pesukei-dzimrah'][0]
segs = p['segments']
by = {s['id']: s for s in segs}

# The print sets the Shirah (אָז יָשִׁיר → צָלֲלוּ כַּעוֹפֶרֶת, "sank like lead") as one
# continuous Hebrew block with a single running commentary. We had split it into six
# prayer segments interleaved with four commentary boxes. Recombine.
prayer_ids = ['azyashir-18', 'azyashir-20', 'azyashir-22', 'azyashir-24', 'azyashir-25', 'azyashir-27']
cmt_ids    = ['azyashir-19', 'azyashir-21', 'azyashir-23', 'azyashir-26']

merged_he = ' '.join(by[i]['heText'] for i in prayer_ids)
merged_en = ' '.join(by[i]['enText'] for i in cmt_ids)

# sanity: block must end at "sank like lead"
assert merged_he.rstrip().endswith('בְּמַיִם אַדִּירִים:'), merged_he[-30:]
assert merged_en.rstrip().endswith('sank like lead!'), merged_en[-30:]

# verify the ten segments are contiguous and in the expected order
block = ['azyashir-18','azyashir-19','azyashir-20','azyashir-21','azyashir-22',
         'azyashir-23','azyashir-24','azyashir-25','azyashir-26','azyashir-27']
start = next(i for i, s in enumerate(segs) if s['id'] == 'azyashir-18')
assert [s['id'] for s in segs[start:start+10]] == block, [s['id'] for s in segs[start:start+10]]

song_prayer = {'id': 'azyashir-18', 'type': 'prayer', 'heText': merged_he}
song_cmt    = {'id': 'azyashir-19', 'type': 'commentary', 'heText': '', 'enText': merged_en}
segs[start:start+10] = [song_prayer, song_cmt]

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
for s in segs[start-1:start+3]:
    print(s['type'], s['id'], '|', (s.get('heText') or s.get('enText') or '')[:55])
print('OK; prayer segs now:', len(segs))
