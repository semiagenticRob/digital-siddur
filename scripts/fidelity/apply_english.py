"""Apply English print-fidelity corrections (the print is the authority).

Only differences that are safe to apply mechanically are applied:
  - English only: neither side of the difference contains Hebrew, and the
    field is an English field (enText / title / subtitle / glossary entry).
  - Not a deliberate app adaptation: page references the app rewrote as
    links ("on page 119" -> "here") and anything touching link/markdown
    syntax are left alone and reported as intentional / manual.
  - Strong match: the field matched its print span at >= 85%, and the
    difference is local (<= 60 chars each side).
  - The exact original text must still be at the recorded raw offsets
    (asserted before every edit), so a stale run can't corrupt content.

Every applied change is written to docs/fidelity/english-fixes.json.

Run:  python scripts/fidelity/apply_english.py [--apply]
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

import fidelity as F

EN_KEYS = {'enText', 'title', 'subtitle', 'term—definition'}
HEB = re.compile(r'[֐-׿]')
XREF_PRINT = re.compile(r'\b(on |see )?page \d+|\b(above|below) on \d+|\bon \d+\b', re.I)
LINK = re.compile(r'\[[^\]]+\]\((?:section|prayer):[^)]+\)')
OUT = os.path.join(F.ROOT, 'docs', 'fidelity', 'english-fixes.json')


def load(file):
    path = os.path.join(F.CONTENT, file)
    raw = open(path, encoding='utf-8').read()
    return json.loads(raw), raw.endswith('\n')


def locate(doc, file, path, key):
    """Return (container dict, key name, offset into the shown string)."""
    if file == 'glossary.json':
        i = int(re.match(r'entries\[(\d+)\]', path).group(1))
        return doc['entries'][i], None, 0
    if file == 'book-matter.json' and '[' not in path:
        pc = next(p for p in doc['pieces'] if p['id'] == path)
        return pc, key, 0
    m = re.match(r'(.+)\[(.+)\]$', path)
    parent, seg_id = m.group(1), m.group(2)
    if file == 'appendices.json':
        n = int(parent.replace('appendix', ''))
        segs = next(a for a in doc['appendices'] if a['number'] == n)['segments']
    elif file == 'book-matter.json':
        segs = next(p for p in doc['pieces'] if p['id'] == parent)['segments']
    else:
        segs = next(p for g in doc['groups'] for p in g['prayers'] if p['id'] == parent)['segments']
    hits = [s for s in segs if s['id'] == seg_id]
    assert len(hits) == 1, (file, path)
    return hits[0], key, 0


WORD = re.compile(r"[A-Za-z’']+")


def word_at(text: str, s: int, e: int) -> str:
    a, b = s, e
    while a > 0 and re.match(r"[A-Za-z’']", text[a - 1]):
        a -= 1
    while b < len(text) and re.match(r"[A-Za-z’']", text[b]):
        b += 1
    return text[a:b]


def print_word_counts(diffs) -> Counter:
    """Word frequencies over all English print text (for the typo check)."""
    import pdftext
    c = Counter()
    for pc in pdftext.pieces_for_pages(F.ALL_PAGES):
        if pc.stream == 'en':
            c.update(w.lower() for w in WORD.findall(pc.text))
    return c


DICT = set()
if os.path.exists('/usr/share/dict/words'):
    DICT = {w.strip().lower() for w in open('/usr/share/dict/words', encoding='utf-8')}


def suspicious_words(cluster, words) -> list:
    """Words a group of edits would introduce that look like print typos: not a
    dictionary word and found nowhere else in the book's English."""
    cont, key = cluster[0][0], cluster[0][1]
    glossary = 'definition' in cont and key is None
    raw = cont['term'] + '\u2014' + cont['definition'] if glossary else cont[key]
    after = raw
    for _, _, d, _ in sorted(cluster, key=lambda t: -t[2].app_raw_span[0]):
        s, e = d.app_raw_span
        after = after[:s] + unicodedata.normalize('NFC', d.print) + after[e:]
    # apostrophe style alone (' vs ’) never makes a word suspicious
    flat = lambda t: t.replace('’', "'")
    gained = Counter(WORD.findall(flat(after))) - Counter(WORD.findall(flat(raw)))

    def known(w: str) -> bool:
        base = w.lower().replace('’', "'")
        base = re.sub(r"'(s|t|re|ve|ll|d)$", '', base).strip("'")
        if base.endswith('n') and w.lower().endswith("n’t"):
            base = base[:-1]
        stem = base[:-1] if base.endswith('s') else base
        return (base in DICT or stem in DICT or w.lower() in DICT
                or words[w.lower()] >= 2 or words[base] >= 2)

    return [w for w in gained if not known(w)]


def decide(d, raw, words=None):
    """'apply' | reason string."""
    if d.key not in EN_KEYS or d.kind not in ('replace', 'app-only', 'print-only'):
        return 'not-english-field'
    if HEB.search(d.app) or HEB.search(d.print):
        return 'hebrew'
    if re.search(r'[*\[\]]', d.print):
        return 'markdown-char-in-print'   # e.g. a printed footnote asterisk: '*' is italic syntax here
    if d.field_ratio < 0.85:
        return 'weak-field-match'
    if len(d.app) > 60 or len(d.print) > 60:
        return 'large'
    # Multi-word edits are where reading order fails (side-by-side columns,
    # labels and sidebars beside the text): a visual check found about a third
    # of them wrong, so a person decides each one.
    if len(re.findall(r'[A-Za-z]+', d.app)) >= 2 or len(re.findall(r'[A-Za-z]+', d.print)) >= 2:
        return 'multi-word'
    # A space dropped after punctuation ("rescue,for") is an extraction gap, not print.
    if d.kind == 'app-only' and not d.app.strip():
        i = d.app_context.find(d.app)
        if i > 0 and d.app_context[i - 1] in ',;:.!?':
            return 'space-after-punct'
    s, e = d.app_raw_span
    if XREF_PRINT.search(d.print) or XREF_PRINT.search(d.print_context[20:-20] if len(d.print_context) > 40 else d.print_context):
        if re.search(r'\bhere\b|\bpage\b|\d', d.app + d.print):
            return 'intentional-xref'
    for m in LINK.finditer(raw):
        if s < m.end() and e > m.start() or (s == e and m.start() < s <= m.end()):
            return 'touches-link'
    if '*' in raw[max(0, s - 1):e + 1] and d.kind != 'print-only':
        return 'touches-markdown'
    if unicodedata.normalize('NFD', raw[s:e]) != d.app:
        return 'raw-mismatch'
    # punctuation/spacing at a Hebrew-English boundary is where print reading
    # order is least certain: hold for a human look instead of applying
    if not re.search('[A-Za-z]', d.app + d.print):
        for ctx, mid in ((d.app_context, d.app), (d.print_context, d.print)):
            i = ctx.find(mid) if mid else 25
            i = 25 if i < 0 else i
            around = ctx[max(0, i - 2):i] + ctx[i + len(mid):i + len(mid) + 2]
            if HEB.search(around):
                return 'near-hebrew'
    return 'apply'


LEDGER = os.path.join(F.ROOT, 'docs', 'fidelity', 'ledger.json')


def human_decisions() -> dict:
    """Fingerprint -> decision for every finding a person has ruled on."""
    if not os.path.exists(LEDGER):
        return {}
    return {k: v['decision'] for k, v in json.load(open(LEDGER, encoding='utf-8')).items()
            if v.get('by') == 'human'}


def main(apply: bool):
    diffs, _ = F.run_all()
    ruled = human_decisions()
    words = print_word_counts(diffs)
    plan = defaultdict(list)          # file -> [(container, key, d)]
    reasons = Counter()
    docs = {}
    held = []
    for d in diffs:
        if d.kind not in ('replace', 'app-only', 'print-only') or not d.file:
            continue
        if d.file not in docs:
            docs[d.file] = load(d.file)
        doc, _ = docs[d.file]
        cont, key, _ = locate(doc, d.file, d.path, d.key)
        if d.file == 'glossary.json':
            raw = cont['term'] + '—' + cont['definition']
        else:
            raw = cont[key]
        r = decide(d, raw, words)
        fp = F.fingerprint(d)
        if r == 'apply' and fp in ruled and ruled[fp] != 'fix':
            r = f'human:{ruled[fp]}'   # a person ruled on this one; only "fix" applies
        plan[d.file].append((cont, key, d, r))

    # Edits within a few characters of each other are one change: apply the
    # group only if every edit in it is safe, never half a word.
    for file in list(plan):
        by_field = defaultdict(list)
        for cont, key, d, r in plan[file]:
            by_field[(id(cont), key)].append((cont, key, d, r))
        keep = []
        for group in by_field.values():
            group.sort(key=lambda t: t[2].app_raw_span[0])
            clusters, cur = [], [group[0]]
            for item in group[1:]:
                if item[2].app_raw_span[0] - cur[-1][2].app_raw_span[1] <= 3:
                    cur.append(item)
                else:
                    clusters.append(cur)
                    cur = [item]
            clusters.append(cur)
            for cl in clusters:
                ok = all(t[3] == 'apply' for t in cl)
                typo = ok and suspicious_words(cl, words)
                for cont, key, d, r in cl:
                    outcome = r if r != 'apply' or ok else 'held-with-neighbour'
                    if outcome == 'apply' and typo:
                        outcome = 'possible-print-typo'
                    reasons[(d.cls, outcome)] += 1
                    if outcome == 'apply':
                        keep.append((cont, key, d))
                    elif d.key in EN_KEYS and not (HEB.search(d.app) or HEB.search(d.print)) \
                            and outcome not in ('not-english-field',):
                        held.append({'file': file, 'path': d.path, 'key': d.key, 'class': d.cls,
                                     'reason': outcome, 'app': d.app, 'print': d.print,
                                     'pages': d.pages, 'app_context': d.app_context,
                                     'print_context': d.print_context})
        plan[file] = keep

    changes = []
    for file, items in plan.items():
        doc, nl = docs[file]
        # apply right-to-left inside each string so earlier offsets stay valid
        by_field = defaultdict(list)
        for cont, key, d in items:
            by_field[(id(cont), key)].append((cont, key, d))
        for (_, key), group in by_field.items():
            cont = group[0][0]
            glossary = file == 'glossary.json'
            raw = cont['term'] + '—' + cont['definition'] if glossary else cont[key]
            before = raw
            for _, _, d in sorted(group, key=lambda t: -t[2].app_raw_span[0]):
                s, e = d.app_raw_span
                assert unicodedata.normalize('NFD', raw[s:e]) == d.app, (file, d.path, raw[s:e], d.app)
                new = unicodedata.normalize('NFC', d.print)
                raw = raw[:s] + new + raw[e:]
                changes.append({'file': file, 'path': d.path, 'key': d.key, 'class': d.cls,
                                'app': d.app, 'print': new, 'pages': d.pages,
                                'app_context': d.app_context, 'print_context': d.print_context})
            if glossary:
                term_len = len(cont['term'])
                assert raw.count('—') >= 1
                t, df = raw[:term_len], raw[term_len + 1:]
                assert raw[term_len] == '—', (file, d.path)
                cont['term'], cont['definition'] = t, df
            else:
                cont[key] = raw
            assert before != raw
    applied = len(changes)
    print('decisions (class, outcome):')
    for (cls, r), n in sorted(reasons.items(), key=lambda t: (t[0][1] != 'apply', -t[1])):
        print(f'  {n:5}  {cls:12} {r}')
    print(f'english fixes to apply: {applied}; english held for review: {len(held)}')
    if apply and applied:
        for file, (doc, nl) in docs.items():
            if file not in plan:
                continue
            path = os.path.join(F.CONTENT, file)
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump(doc, fh, ensure_ascii=False, indent=2)
                if nl:
                    fh.write('\n')
            os.replace(tmp, path)
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(changes, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        with open(OUT.replace('english-fixes', 'english-held'), 'w', encoding='utf-8') as fh:
            json.dump(held, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        print('written:', OUT)


if __name__ == '__main__':
    main('--apply' in sys.argv)
