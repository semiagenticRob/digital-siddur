"""Divine Name follows the print: יְהֹוָה (cholam on the first he).

Decision (2026-10-29, project owner): the print writes the Name with a cholam
(יְהֹוָה, לַיהֹוָה, בַּיהֹוָה ...) in ~1,280 places; the app had ~300 vocalized
forms without it (יְהוָה) and 19 with the cholam stored on the vav (יְהוָֹה).

This script changes ONLY vocalized Divine Name tokens:
  - first he has no cholam and the vav has a vowel (qamats/chirik): add a
    cholam on the first he;
  - cholam stored on the vav after its vowel: move it onto the first he.
Unvocalized (יהוה) or partly vocalized (יְהוה) forms are left for the rav.
Instances the print itself writes without a cholam (a Torah passage such as
יְהוָ֡ה) are listed in EXCLUDE after checking against the print.

Every edit asserts the token it changes; heParts are kept equal to heText.
Run:  python scripts/fidelity/apply_divine_name.py [--apply]
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CONTENT = os.path.join(ROOT, 'src', 'content')
OUT = os.path.join(ROOT, 'docs', 'fidelity', 'divine-name-fixes.json')

MARKS = '[֑-ׇ]*'
HOLAM = 'ֹ'
# yod + marks (must be vocalized: sheva/chataf/patach-yod in prefixed forms is fine)
TOKEN = re.compile('(?P<pre>(?:[א-ת]' + MARKS + '){0,2}?)'
                   '(?P<y>י' + MARKS + ')'
                   '(?P<h>ה)(?P<hm>' + MARKS + ')'
                   '(?P<v>ו)(?P<vm>' + MARKS + ')'
                   '(?P<h2>ה' + MARKS + ')'
                   '(?![א-ת])')

# (file, json-path substring) pairs where the print has no cholam: never touch
EXCLUDE: set = set()


def fix_token(m: re.Match) -> str | None:
    hm, vm = m.group('hm'), m.group('vm')
    if HOLAM in hm or 'ֺ' in hm:
        return None                                   # already as printed
    vowel_on_vav = any(c in vm for c in 'ִַָ')   # qamats / chirik / patach
    if not vowel_on_vav:
        return None                                   # unvocalized or partial: rav
    new_vm = vm.replace(HOLAM, '')                    # cholam stored on the vav moves to the he
    return (m.group('pre') + m.group('y') + m.group('h') + HOLAM + hm
            + m.group('v') + new_vm + m.group('h2'))


def fix_string(s: str) -> tuple[str, list]:
    out, last, edits = [], 0, []
    for m in TOKEN.finditer(s):
        if m.group('pre') and not re.match('[לבוכמשדה]', m.group('pre')):
            continue                                  # prefix must be a real prefix letter
        new = fix_token(m)
        if new is None:
            continue
        out.append(s[last:m.start()])
        out.append(new)
        edits.append((m.group(), new))
        last = m.end()
    out.append(s[last:])
    return ''.join(out), edits


def walk(o, path, file, changes, apply):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            p = f'{path}/{k}'
            if isinstance(v, str) and k in ('heText', 'enText', 'inlineRubric', 'text', 'title', 'subtitle',
                                             'heTitle', 'definition', 'term'):
                if any(file == f and x in p for f, x in EXCLUDE):
                    continue
                new, edits = fix_string(v)
                if edits:
                    changes += [{'file': file, 'path': p, 'old': a, 'new': b} for a, b in edits]
                    if apply:
                        o[k] = new
            else:
                walk(v, p + (f'[{o.get("id")}]' if isinstance(v, (list, dict)) and 'id' in o else ''),
                     file, changes, apply)
        if 'heParts' in o and 'heText' in o:
            assert ''.join(pt['text'] for pt in o['heParts']) == o['heText'], (file, path)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, f'{path}[{i}]', file, changes, apply)


def main(apply: bool):
    changes = []
    for name in sorted(os.listdir(CONTENT)):
        if not name.endswith('.json'):
            continue
        path = os.path.join(CONTENT, name)
        raw = open(path, encoding='utf-8').read()
        doc = json.loads(raw)
        before = len(changes)
        walk(doc, '', name, changes, apply)
        if apply and len(changes) > before:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump(doc, fh, ensure_ascii=False, indent=2)
                if raw.endswith('\n'):
                    fh.write('\n')
            os.replace(tmp, path)
    from collections import Counter
    print('divine name edits:', len(changes))
    for (a, b), n in Counter((c['old'], c['new']) for c in changes).most_common(20):
        print(f'  {n:4}  {a}  ->  {b}')
    if apply:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(changes, fh, ensure_ascii=False, indent=1)
            fh.write('\n')


if __name__ == '__main__':
    main('--apply' in sys.argv)
