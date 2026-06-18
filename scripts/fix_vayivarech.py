import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-pesukei-dzimrah'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-pesukei-dzimrah'][0]
segs = p['segments']
by = {s['id']: s for s in segs}

# Fix 1: repair the scrambled Instant Insight Hebrew + wording.
by['azyashir-9']['enText'] = (
    "The first letters of the opening four words—ויברך דוד את ה'—spell ודאי, "
    "one of the Names of Hashem, which represents His attribute of certainty and "
    "reliability. Notwithstanding all the difficulties in his life, David HaMelech "
    "always lived with the belief that Hashem can be relied on to take care of him."
)

# Fix 2: keep Vayivarech David contiguous. Current order:
#   azyashir-7 (prayer 1) , -8 (commentary) , -9 (insight) , -10 (rubric) , -11 (prayer 2)
# Desired: prayer1, rubric, prayer2, commentary, insight
order_ids = ['azyashir-7', 'azyashir-8', 'azyashir-9', 'azyashir-10', 'azyashir-11']
start = next(i for i, s in enumerate(segs) if s['id'] == order_ids[0])
# confirm the block is exactly these five in this position
assert [s['id'] for s in segs[start:start+5]] == order_ids, [s['id'] for s in segs[start:start+5]]
new_block = [by['azyashir-7'], by['azyashir-10'], by['azyashir-11'],
             by['azyashir-8'], by['azyashir-9']]
segs[start:start+5] = new_block

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('reordered Vayivarech David block; new order:',
      [s['id'] for s in segs[start:start+5]])
print('OK')
