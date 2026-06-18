#!/usr/bin/env python3
"""Read-only content linter for the siddur JSON.

Encodes the app's *rendering contract* (what each segment type actually draws)
and flags data that can't render or won't match the print. Grew out of the
recurring bugs found during the Shacharis proofing pass:
  - Hebrew lemmas stranded in commentary.heText (commentary draws enText only)
  - bridge lines typed as commentary (boxed) instead of section_intro (centered)
  - literal '*' in rubrics (rubrics draw as plain text, not markdown)
  - garbled / wrong lemmas (lemma not present in the prayer it explains)
  - unbalanced **bold** / *italic* markers

Usage:
  python3 scripts/lint_content.py            # report everything
  python3 scripts/lint_content.py --strict   # exit 1 if any ERROR-severity finding
  python3 scripts/lint_content.py --errors   # only show ERROR-severity findings
"""
import json, re, glob, sys, os
from collections import defaultdict

HE_RUN = re.compile(r'[֐-׿‏‎]')          # Hebrew block + nikud + RTL/LTR marks
CONSONANT = re.compile(r'[א-ת]')          # base letters only (skeleton for matching)
RICHTEXT_TYPES = {'commentary', 'insight', 'faq', 'section_intro', 'transition'}

# check-id -> severity. ERROR = renders wrong / data invisible. WARN = advisory.
SEVERITY = {
    'commentary.heText (stranded — never renders)':       'error',
    "rubric contains '*' (renders literally)":            'error',
    'unbalanced markdown markers':                        'error',
    'prayer.heText empty':                                'error',
    'lemma not bolded (**…**)':                           'warn',
    'lemma not found in any prayer (garble/wrong?)':      'warn',
    'commentary looks like a bridge (→ section_intro?)':  'warn',
    'prayer.enText (never renders)':                      'warn',
    'heText in a render-enText type (never renders)':     'warn',
}

findings = defaultdict(list)

def strip_md(s):
    return s.replace('**', '').replace('*', '')

def he_norm(s):
    return ''.join(CONSONANT.findall(s))

def leading_lemma(en):
    """The opening Hebrew lemma of a gloss (Hebrew before the first em-dash)."""
    s = re.sub(r'^\*\([^)]*\)\*\s*', '', en)      # drop a leading italic aside
    if '—' not in s:
        return None
    head = strip_md(s.split('—', 1)[0])
    he = ''.join(ch for ch in head if HE_RUN.match(ch) or ch in ' ,.׳״').strip(' ,.')
    return he if len(HE_RUN.findall(he)) >= 2 else None

def lint_segments(segs, where):
    prayer_he = he_norm(' '.join(s.get('heText', '') for s in segs if s['type'] == 'prayer'))
    for i, s in enumerate(segs):
        t, he, en = s['type'], s.get('heText') or '', s.get('enText') or ''
        loc = f'{where}[{i}] {s.get("id","?")}'

        if t == 'commentary' and he.strip():
            findings['commentary.heText (stranded — never renders)'].append(loc)
        elif t in ('insight', 'faq', 'section_intro', 'transition') and he.strip():
            findings['heText in a render-enText type (never renders)'].append(f'{loc} ({t})')

        if t == 'prayer':
            if en.strip():
                findings['prayer.enText (never renders)'].append(loc)
            if not he.strip():
                findings['prayer.heText empty'].append(loc)

        if t == 'rubric' and ('*' in he or '*' in en):
            findings["rubric contains '*' (renders literally)"].append(loc)

        if t in RICHTEXT_TYPES and en:
            if en.count('**') % 2 or en.replace('**', '').count('*') % 2:
                findings['unbalanced markdown markers'].append(loc)

        if t in ('commentary', 'insight'):
            lem = leading_lemma(en)
            if lem:
                body = re.sub(r'^\*\([^)]*\)\*\s*', '', en)
                if not body.lstrip().startswith('**'):
                    findings['lemma not bolded (**…**)'].append(loc)
                if prayer_he and he_norm(lem) not in prayer_he:
                    findings['lemma not found in any prayer (garble/wrong?)'].append(f'{loc}  «{lem}»')

        if t == 'commentary' and not HE_RUN.search(en) and en.strip().endswith(':'):
            findings['commentary looks like a bridge (→ section_intro?)'].append(loc)

def walk(node, path):
    if isinstance(node, dict):
        if isinstance(node.get('segments'), list) and all(isinstance(x, dict) for x in node['segments']):
            label = node.get('id') or node.get('title') or node.get('number')
            lint_segments(node['segments'], f'{path}/{label}')
        for k, v in node.items():
            walk(v, f'{path}/{k}')
    elif isinstance(node, list):
        for x in node:
            walk(x, path)

def main():
    errors_only = '--errors' in sys.argv
    strict = '--strict' in sys.argv
    for f in sorted(glob.glob('src/content/*.json')):
        walk(json.load(open(f)), os.path.basename(f))

    n_err = sum(len(v) for k, v in findings.items() if SEVERITY.get(k) == 'error')
    n_warn = sum(len(v) for k, v in findings.items() if SEVERITY.get(k) != 'error')
    print(f'{n_err} errors, {n_warn} warnings across {len(findings)} checks.\n')
    for k in sorted(findings, key=lambda k: (SEVERITY.get(k) != 'error', -len(findings[k]))):
        sev = SEVERITY.get(k, 'warn')
        if errors_only and sev != 'error':
            continue
        print(f'### [{sev.upper()}] {k}: {len(findings[k])}')
        for loc in findings[k][:6]:
            print(f'   - {loc}')
        if len(findings[k]) > 6:
            print(f'   … and {len(findings[k])-6} more')
        print()

    if strict and n_err:
        print(f'FAIL: {n_err} error-severity findings.')
        sys.exit(1)

if __name__ == '__main__':
    main()
