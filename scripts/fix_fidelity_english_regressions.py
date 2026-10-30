"""Undo the English print-fidelity fixes (commit 82cf20c) that a visual check of the
print showed to be wrong.

The fixer read some side-by-side print columns (Avinu Malkeinu, Shemoneh Esrei
blessing pairs, Al HaNissim) straight across, and picked up neighbouring labels
and sidebars, so a few edits wrote mixed-up text into the app. Every multi-word
edit in that commit was compared with the print by eye (2026-10-30); this script
reverts the wrong ones and keeps the rest, including the punctuation and quote
fixes in the same strings.

Each target must still hold exactly the text 82cf20c wrote, or the script stops.
Run from the repo root:  python3 scripts/fix_fidelity_english_regressions.py
"""
import difflib
import json
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
COMMIT = '82cf20c'

# (file, JSON pointer) -> which content edits to revert:
#   'all'          every edit that changes words (punctuation/quote edits stay)
#   [substr, ...]  only edits whose before- or after-text contains one of these
TARGETS = {
    # side-by-side columns read across
    ('shacharit.json', '/groups/4/prayers/1/segments/14/enText'): 'all',
    ('shacharit.json', '/groups/4/prayers/1/segments/17/enText'): 'all',
    ('shacharit.json', '/groups/4/prayers/1/segments/49/enText'): 'all',
    ('shacharit.json', '/groups/4/prayers/1/segments/51/enText'): 'all',
    ('shacharit.json', '/groups/4/prayers/1/segments/60/enText'): 'all',
    ('minchah.json', '/groups/1/prayers/0/segments/14/enText'): 'all',
    ('minchah.json', '/groups/1/prayers/0/segments/17/enText'): 'all',
    ('minchah.json', '/groups/1/prayers/0/segments/49/enText'): 'all',
    ('minchah.json', '/groups/1/prayers/0/segments/51/enText'): 'all',
    ('minchah.json', '/groups/1/prayers/0/segments/60/enText'): 'all',
    ('minchah.json', '/groups/1/prayers/0/segments/64/enText'): 'all',
    ('shacharit.json', '/groups/0/prayers/6/segments/22/enText'): 'all',
    # text dropped that the print has
    ('al-hamichyah.json', '/groups/0/prayers/0/segments/3/enText'): 'all',
    ('birkas-hamazon.json', '/groups/0/prayers/4/segments/34/enText'): 'all',
    ('minchah.json', '/groups/0/prayers/1/segments/138/enText'): 'all',
    ('shacharit.json', '/groups/2/prayers/1/segments/30/enText'): 'all',
    ('minchah.json', '/groups/0/prayers/1/segments/123/enText'): 'all',
    ('minchah.json', '/groups/0/prayers/1/segments/42/enText'): 'all',
    # labels lost or neighbouring text pulled in
    ('appendices.json', '/appendices/8/segments/1/enText'): 'all',
    ('birkas-hamazon.json', '/groups/0/prayers/2/segments/9/enText'): 'all',
    ('minchah.json', '/groups/0/prayers/1/segments/60/enText'): ['During Aseres'],
    ('mussaf-chol-hamoed.json', '/groups/0/prayers/0/segments/61/enText'): ['On Sukkos', 'On Shemini'],
    ('mussaf-chol-hamoed.json', '/groups/0/prayers/0/segments/16/enText'): [' level'],
    ('maariv.json', '/groups/0/prayers/1/segments/95/enText'): ['Instant Insight'],
    ('shacharit.json', '/groups/5/prayers/1/segments/122/enText'): ['Crucial', 'up!'],
    ('shacharit.json', '/groups/6/prayers/6/segments/1/enText'): ['We Believe'],
    ('borei-nefashos.json', '/groups/0/prayers/0/segments/1/enText'): ['cite', 'the '],
    # space after a comma deleted
    ('maariv.json', '/groups/0/prayers/1/segments/116/enText'): [','],
    ('shacharit.json', '/groups/1/prayers/0/segments/105/enText'): [','],
}

# Curly quotes the print has, lost where a reverted edit shared a word with them.
FOLLOW_UP = {
    ('shacharit.json', '/groups/6/prayers/6/segments/1/enText'): [("What's popular", 'What’s popular')],
    ('shacharit.json', '/groups/1/prayers/0/segments/105/enText'): [('as, "Hashem', 'as, “Hashem')],
    ('shacharit.json', '/groups/2/prayers/1/segments/30/enText'): [('we can — we will', 'we can—we will')],
    # print (pdf p.62 sidebar): "fallings—סומך יהוה לכל־הנפלים—He helps us get back up!"
    ('shacharit.json', '/groups/5/prayers/1/segments/122/enText'): [
        ('our fallings **סוֹמֵךְ', 'our fallings—**סוֹמֵךְ'),
        ('** — He will get back us up!', '**—He helps us get back up!')],
}

TOKEN = re.compile(r'\s+|[^\s]+')
WORDS = lambda s: re.findall(r'[A-Za-zא-ת]+', s)


def get(doc, ptr):
    o = doc
    for p in ptr.strip('/').split('/'):
        o = o[int(p)] if isinstance(o, list) else o[p]
    return o


def put(doc, ptr, value):
    parts = ptr.strip('/').split('/')
    o = get(doc, '/' + '/'.join(parts[:-1]))
    o[parts[-1]] = value


def repair(old: str, new: str, rule) -> str:
    a, b = TOKEN.findall(old), TOKEN.findall(new)
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        before, after = ''.join(a[i1:i2]), ''.join(b[j1:j2])
        if tag == 'equal':
            out.append(after)
        elif rule == 'all':
            out.append(before if WORDS(before) != WORDS(after) else after)
        else:
            out.append(before if any(k in before or k in after for k in rule) else after)
    return ''.join(out)


def main():
    changed = 0
    for file in sorted({f for f, _ in TARGETS}):
        path = os.path.join(ROOT, 'src', 'content', file)
        raw = open(path, encoding='utf-8').read()
        doc = json.loads(raw)
        prior = json.loads(subprocess.check_output(
            ['git', 'show', f'{COMMIT}~1:src/content/{file}'], cwd=ROOT, text=True))
        fixed = json.loads(subprocess.check_output(
            ['git', 'show', f'{COMMIT}:src/content/{file}'], cwd=ROOT, text=True))
        for (f, ptr), rule in TARGETS.items():
            if f != file:
                continue
            cur, old, new = get(doc, ptr), get(prior, ptr), get(fixed, ptr)
            assert cur == new, f'{file}{ptr} changed since {COMMIT}; re-check by hand'
            assert old != new
            out = repair(old, new, rule)
            for a, b in FOLLOW_UP.get((file, ptr), []):
                assert out.count(a) == 1, (file, ptr, a)
                out = out.replace(a, b)
            assert out != new, f'{file}{ptr}: nothing reverted'
            put(doc, ptr, out)
            changed += 1
            print(f'{file}{ptr}\n   was: {new[:150]}\n   now: {out[:150]}')
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)
            if raw.endswith('\n'):
                fh.write('\n')
    print(f'{changed} strings repaired')


if __name__ == '__main__':
    main()
