#!/usr/bin/env python3
"""Add English focus-commentary to the newly-inserted Hallel Tehillim 116 & 117,
matching the app's existing psalm pattern (header → focus → prayer). Text is from
the PDF English column (p.206-207)."""
import json
F116 = "The focus of the first half of this chapter is that we have complete trust in Hashem that He will always protect us."
F116b = "The focus of the second half of this chapter is that we know that in truth, the providence of Hashem is everywhere."
F117 = "The focus of this chapter is our call to the nations (in the end of days) to recognize Hashem."

d = json.load(open('src/content/hallel.json'))
prayer = d['groups'][0]['prayers'][0]
segs = prayer['segments']
def idx(i): return next(k for k, s in enumerate(segs) if s.get('id') == i)

assert not any(s.get('id') == 'tehillim-116-focus' for s in segs), 'already added'
# 116 focus before the 116 prayer text
i = idx('tehillim-116-text')
segs[i:i] = [{'id': 'tehillim-116-focus', 'type': 'commentary', 'enText': F116 + ' ' + F116b}]
# 117 focus before 117 prayer text
i = idx('tehillim-117-text')
segs[i:i] = [{'id': 'tehillim-117-focus', 'type': 'commentary', 'enText': F117}]

json.dump(d, open('src/content/hallel.json', 'w'), ensure_ascii=False, indent=2)
print('Added focus commentary to Hallel 116 and 117.')
