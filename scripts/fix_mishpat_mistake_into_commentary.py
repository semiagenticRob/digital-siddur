#!/usr/bin/env python3
"""
Move 'If you made a mistake, see Appendix 12:5' from a standalone rubric into
the end of the mishpat commentary's enText as an italic line.
RichText already linkifies 'Appendix N:N' and renders *...* as italic.
"""
import json

COMMENTARY_ID = 'se2-mishpat-commentary'
RUBRIC_ID     = 'se2-mishpat-mistake-rubric'
APPEND        = '\n*(If you made a mistake, see Appendix 12:5)*'

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def patch(node):
    if isinstance(node, list):
        for x in node: patch(x)
    elif isinstance(node, dict):
        segs = node.get('segments')
        if isinstance(segs, list):
            cmt_idx = next((i for i, s in enumerate(segs) if s.get('id') == COMMENTARY_ID), None)
            rub_idx = next((i for i, s in enumerate(segs) if s.get('id') == RUBRIC_ID), None)
            if cmt_idx is not None and rub_idx is not None:
                assert rub_idx == cmt_idx + 1, 'Not consecutive'
                segs[cmt_idx]['enText'] += APPEND
                print(f'  Appended italic mistake note to {COMMENTARY_ID}')
                segs.pop(rub_idx)
                print(f'  Removed {RUBRIC_ID}')
                return
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
