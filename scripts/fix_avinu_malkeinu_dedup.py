#!/usr/bin/env python3
"""
The avinu_malkeinu prayer begins with 12 segments that duplicate the tail of the
13 middos (נֹצֵר חֶסֶד … וְסָלַחְתָּ). These already exist — correctly, with bold
lemmas — as vidui-29..40. The print (siddur p.77→78) shows this content ONCE,
flowing continuously into "A SPECIAL TIME, SPECIAL REQUESTS" / Avinu Malkeinu;
the page break duplicated it into the avinu_malkeinu prayer.

Remove ONLY the 12 duplicate segments so the avinu_malkeinu prayer starts at its
"A SPECIAL TIME, SPECIAL REQUESTS" header — which puts the auto-rendered
AVINU MALKEINU divider directly above that header.

PRESERVED: avinu_malkeinu_header and avinu_malkeinu_title (the section headers).
Content-only change; no rendering code touched.
"""
import json, re

DUP_IDS = [
    'avinu_malkeinu_intro_continued_1', 'avinu_malkeinu_intro_commentary_1',
    'avinu_malkeinu_intro_continued_2', 'avinu_malkeinu_intro_commentary_2',
    'avinu_malkeinu_intro_continued_3', 'avinu_malkeinu_intro_commentary_3',
    'avinu_malkeinu_intro_continued_4', 'avinu_malkeinu_intro_commentary_4',
    'avinu_malkeinu_intro_continued_5', 'avinu_malkeinu_intro_commentary_5',
    'avinu_malkeinu_intro_continued_6', 'avinu_malkeinu_intro_commentary_6',
]
# Headers that MUST remain immediately after the removed run
KEEP_AFTER = ['avinu_malkeinu_header', 'avinu_malkeinu_title']

def strip_nikud(s):
    return re.sub(r'[֑-ׇ]', '', s or '')
def skel(s):
    return re.sub(r'[^א-ת]', '', strip_nikud(s))

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def find_prayer(node, pid):
    if isinstance(node, dict):
        if node.get('id') == pid and 'segments' in node:
            return node
        for v in node.values():
            r = find_prayer(v, pid)
            if r is not None: return r
    elif isinstance(node, list):
        for x in node:
            r = find_prayer(x, pid)
            if r is not None: return r

am = find_prayer(data, 'avinu_malkeinu')
assert am, 'avinu_malkeinu prayer not found'
segs = am['segments']
ids = [s.get('id') for s in segs]

# Safety: the first 12 segments must be exactly the duplicate run, in order
assert ids[:12] == DUP_IDS, f'Unexpected leading segments: {ids[:12]}'
# Safety: segments 12,13 must be the section headers we are preserving
assert ids[12:14] == KEEP_AFTER, f'Headers not where expected: {ids[12:14]}'

# Safety: every duplicate prayer-text must skeleton-match its vidui original
PAIRS = [
    ('avinu_malkeinu_intro_continued_1', 'vidui-29'),
    ('avinu_malkeinu_intro_continued_2', 'vidui-31'),
    ('avinu_malkeinu_intro_continued_3', 'vidui-33'),
    ('avinu_malkeinu_intro_continued_4', 'vidui-35'),
    ('avinu_malkeinu_intro_continued_5', 'vidui-37'),
    ('avinu_malkeinu_intro_continued_6', 'vidui-39'),
]
def find_seg(node, sid):
    if isinstance(node, dict):
        if node.get('id') == sid: return node
        for v in node.values():
            r = find_seg(v, sid)
            if r is not None: return r
    elif isinstance(node, list):
        for x in node:
            r = find_seg(x, sid)
            if r is not None: return r
for dup, orig in PAIRS:
    d = find_seg(data, dup); o = find_seg(data, orig)
    assert skel(d.get('heText')) == skel(o.get('heText')), \
        f'{dup} does not match {orig}; aborting to avoid deleting non-duplicate text'

# Remove exactly the 12 duplicate segments (keep everything from index 12 on)
am['segments'] = segs[12:]

# Verify headers survived and are now first
new_ids = [s.get('id') for s in am['segments']]
assert new_ids[:2] == KEEP_AFTER, f'Post-delete order wrong: {new_ids[:2]}'
print(f'Removed {len(DUP_IDS)} duplicate segments.')
print(f'avinu_malkeinu now starts with: {new_ids[:3]}')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
