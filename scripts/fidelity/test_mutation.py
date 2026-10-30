"""Mutation test: proves the checker catches every planted single-character error.

For each sampled unit we take the app fields, plant one random edit in a
random field (substitute / delete / insert a letter, a vowel mark, a
punctuation mark, or a space), re-run the matcher against the same print, and
require a NEW difference that covers the planted position. Mutations are made
in memory only; no content file is touched.

Run: python scripts/fidelity/test_mutation.py [n_per_unit]
"""
import copy
import random
import sys

import fidelity as F

LETTERS = 'abcdefghijklmnopqrstuvwxyz' + 'אבגדהוזחטיכלמנסעפצקרשת'
MARKS = 'ְִֵֶַָֹֻּ'
PUNCT = ',.;:—’“”()!?'
UNITS = ['glossary', 'al-hamichyah', 'hallel', 'appendices', 'sefiras-haomer', 'book-matter', 'minchah']


def key(d):
    return (d.path, d.key, d.kind, d.app, d.print, d.app_context)


def mutate(text: str, rng: random.Random):
    i = rng.randrange(len(text))
    op = rng.choice(['sub', 'del', 'ins'])
    pool = rng.choice([LETTERS, MARKS, PUNCT, ' '])
    ch = rng.choice(pool)
    if op == 'sub':
        if text[i] == ch:
            ch = 'x' if ch != 'x' else 'y'
        return text[:i] + ch + text[i + 1:], i
    if op == 'del':
        return text[:i] + text[i + 1:], i
    return text[:i] + ch + text[i:], i


def main(n: int):
    rng = random.Random(20261029)
    total = caught = 0
    misses = []
    for unit in UNITS:
        source, pages = F.UNITS[unit]
        seqs = F.print_sequences(pages)
        fields = F.app_fields(source)
        base, _, _ = F.match_unit(unit, seqs=seqs, fields=fields)
        base_keys = {key(d) for d in base}
        for _ in range(n):
            fs = copy.deepcopy(fields)
            k = rng.randrange(len(fs))
            f = fs[k]
            raw, pos = mutate(f.raw, rng)
            f.raw = raw
            items = F.strip_markdown(raw) if f.markdown else [(c, i) for i, c in enumerate(raw)]
            f.nt = F.normalize(items)
            def visible(r, md=f.markdown):
                items = F.strip_markdown(r) if md else [(c, i) for i, c in enumerate(r)]
                return F.normalize(items).s
            if visible(raw) == visible(fields[k].raw):
                continue  # invisible edit (doubled space, a markdown marker): not a text error
            total += 1
            diffs, _, _ = F.match_unit(unit, seqs=seqs, fields=fs)
            mine = lambda ds: {key(d): d for d in ds if d.path == f.path and d.key == f.key}
            now, before = mine(diffs), mine(base)
            # detected = the field's differences changed at the planted spot: a new
            # difference appeared, or (if the edit happened to match the print) one vanished
            changed = [now[x] for x in now.keys() - before.keys()] + [before[x] for x in before.keys() - now.keys()]
            hit = any(d.kind == 'app-only-field' or
                      (d.app_raw_span and d.app_raw_span[0] - 2 <= pos <= d.app_raw_span[1] + 2)
                      for d in changed)
            if hit:
                caught += 1
            else:
                misses.append((unit, f.path, f.key, pos, raw[max(0, pos - 15):pos + 15]))
    print(f'mutations planted: {total}, caught: {caught}, missed: {len(misses)}')
    for m in misses[:20]:
        print('  MISSED', m)
    return 0 if not misses else 1


if __name__ == '__main__':
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 60))
