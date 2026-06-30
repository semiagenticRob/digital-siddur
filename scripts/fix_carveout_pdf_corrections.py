#!/usr/bin/env python3
"""PDF-fidelity correction to the carve-out pass. The print (sole content authority)
renders SHORT inline conditional inserts as inline parentheticals / rubric labels —
NOT shaded boxes. The earlier carve-out pass wrongly set optional:true on several of
these. Per-page PDF verification (this review) found these specific over-boxings:

- al-hamichyah  : Shabbos / Rosh Chodesh / Yom Tov inserts (print p.129 — inline labels)
- mussaf-rosh-chodesh : mrc2-s004 leap-year insert (print p.217 — inline parenthetical)
- minchah       : min2-prayer-ledor-vador-mhk AYT המלך הקדוש substitute (print p.141 — inline)

Substantial boxed inserts (Al HaNissim, Yaaleh V'Yavo, AYT Zachreinu, korbanos selectors,
"some add"/"one may insert" tefillos, Avinu Malkeinu verse groups) are LEFT boxed — the
print shades those, matching shacharit. This only removes the box from print-inline inserts.

Removes the `optional` key (returns the segment to its pre-carve-out rendering). Asserts
each target currently has optional:true so a stale assumption fails loudly.
"""
import json

UNBOX = {
    'src/content/al-hamichyah.json': [
        's-am-rubric-shabbos','s-am-prayer-shabbos',
        's-am-rubric-roshchodesh','s-am-prayer-roshchodesh',
        's-am-rubric-yomtov','s-am-prayer-yomtov',
    ],
    'src/content/mussaf-rosh-chodesh.json': ['mrc2-s004'],
    'src/content/minchah.json': ['min2-prayer-ledor-vador-mhk'],
}

def conts(n):
    o=[]
    if isinstance(n,dict):
        if isinstance(n.get('segments'),list): o.append(n)
        for v in n.values(): o+=conts(v)
    elif isinstance(n,list):
        for x in n: o+=conts(x)
    return o

for path, ids in UNBOX.items():
    d=json.load(open(path))
    loc={s.get('id'):s for c in conts(d) for s in c['segments']}
    for sid in ids:
        assert sid in loc, f'{path}: id not found: {sid}'
        seg=loc[sid]
        assert seg.get('optional') is True, f'{path}: {sid} not optional:true (got {seg.get("optional")})'
        del seg['optional']
    json.dump(d, open(path,'w'), ensure_ascii=False, indent=2)
    print(f"{path.split('/')[-1]:28} un-boxed {len(ids)} segment(s): {ids}")
print("Done.")
