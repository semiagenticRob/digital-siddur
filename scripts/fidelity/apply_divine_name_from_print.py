"""Divine Name, second pass: tokens the app left unvocalized or partly
vocalized (יהוה, יְהוה) inside vocalized text take the print's spelling.

Evidence-based and token-for-token: for each app field, its Divine Name
tokens are paired in order with the Divine Name tokens of the print text that
field matched. A token is replaced only when the counts agree, the consonants
(with any prefix) are identical, and the print token carries the cholam.
Run:  python scripts/fidelity/apply_divine_name_from_print.py [--apply]
"""
import json
import os
import re
import sys
import unicodedata

import fidelity as F

M = '[֑-ׇ]*'
TOK = re.compile(r'(?<![א-ת֑-ׇ])(?:[א-ת]' + M + '){0,2}?י' + M + 'ה' + M + 'ו' + M + 'ה' + M + r'(?![א-ת])')
CONS = lambda t: re.sub('[֑-ׇ]', '', t)
LOG = os.path.join(F.ROOT, 'docs', 'fidelity', 'divine-name-fixes.json')


def main(apply):
    changes = []
    edits = {}                      # (file, path, key) -> list of (old, new) by order
    for unit, (source, pages) in F.UNITS.items():
        fields = F.app_fields(source)
        F.match_unit(unit, fields=fields)
        for f in fields:
            if not f.claim_text or f.file == 'glossary.json':
                continue
            app_toks = list(TOK.finditer(f.raw))
            pr_toks = TOK.findall(f.claim_text)
            if not app_toks or len(app_toks) != len(pr_toks):
                continue
            plan = []
            for m, pt in zip(app_toks, pr_toks):
                at = m.group()
                if CONS(at) != CONS(pt) or '\u05b9' not in pt:
                    continue
                # the print's vowels, never its cantillation (the app omits trope)
                new = unicodedata.normalize('NFC', re.sub('[\u0591-\u05af]', '', pt))
                if '\u05b9' in at and len(re.findall('[\u0591-\u05c7]', at)) >= 3:
                    # already vocalized with the cholam: only add the sheva the print
                    # sets under the yod after a prefix (וַיְהֹוָה, בַּיְהֹוָה)
                    a, b = unicodedata.normalize('NFD', at), unicodedata.normalize('NFD', new)
                    if b.count('\u05b0') != a.count('\u05b0') + 1 or CONS(a) != CONS(b) or \
                            sorted(b.replace('\u05b0', '', 1)) != sorted(a):
                        continue
                if new != at:
                    plan.append((m.start(), m.end(), at, new))
            if plan:
                edits[(f.file, f.path, f.key)] = plan
    files = {}
    for (file, path, key), plan in edits.items():
        if file not in files:
            raw = open(os.path.join(F.CONTENT, file), encoding='utf-8').read()
            files[file] = (json.loads(raw), raw.endswith('\n'))
        doc = files[file][0]
        m = re.match(r'(.+)\[(.+)\]$', path)
        parent, sid = m.group(1), m.group(2)
        if file == 'appendices.json':
            segs = next(a for a in doc['appendices'] if a['number'] == int(parent.replace('appendix', '')))['segments']
        elif file == 'book-matter.json':
            segs = next(p for p in doc['pieces'] if p['id'] == parent)['segments']
        else:
            segs = next(p for g in doc['groups'] for p in g['prayers'] if p['id'] == parent)['segments']
        seg = next(s for s in segs if s['id'] == sid)
        text = seg[key]
        for s, e, at, new in sorted(plan, reverse=True):
            assert text[s:e] == at, (file, sid, text[s:e], at)
            text = text[:s] + new + text[e:]
            changes.append({'file': file, 'segment': sid, 'field': key, 'old': at, 'new': new})
        if 'heParts' in seg and key == 'heText':
            continue                        # never touch heParts-bearing segments automatically
        seg[key] = text
    print('second-pass divine name edits:', len(changes))
    from collections import Counter
    for (a, b), n in Counter((c['old'], c['new']) for c in changes).most_common(12):
        print(f'  {n:4}  {a} -> {b}')
    if apply:
        for file, (doc, nl) in files.items():
            path = os.path.join(F.CONTENT, file)
            with open(path + '.tmp', 'w', encoding='utf-8') as fh:
                json.dump(doc, fh, ensure_ascii=False, indent=2)
                if nl:
                    fh.write('\n')
            os.replace(path + '.tmp', path)
        with open(LOG.replace('.json', '-pass2.json'), 'w', encoding='utf-8') as fh:
            json.dump(changes, fh, ensure_ascii=False, indent=1)
            fh.write('\n')


if __name__ == '__main__':
    main('--apply' in sys.argv)
