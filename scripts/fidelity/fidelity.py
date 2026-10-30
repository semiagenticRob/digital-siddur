"""Letter-for-letter fidelity check: app content vs the print PDF.

Pipeline per unit (a service, the appendices, the book matter, the glossary):
  1. Print side: glyph-exact pieces (pdftext.py) joined into reading sequences
     per page region, normalized, with every char mapped back to its glyph box.
  2. App side: every rendered field, markdown stripped, normalized, with every
     char mapped back to its raw offset in the JSON string.
  3. Each app field is located in the print by anchor voting, then diffed
     character by character (nikud included) against exactly that span.
  4. Coverage: print text not claimed by any app field = missing from the app;
     app text with no print match = not in the print.

Normalization is identical on both sides and limited to encoding differences
that cannot be seen in print (see NORMALIZATION_RULES). Everything visible —
letters, nikud, punctuation, quotes, dashes, case, word spacing — is compared.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import unicodedata
from dataclasses import dataclass, field, asdict

import pdftext

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CONTENT = os.path.join(ROOT, 'src', 'content')

NORMALIZATION_RULES = {
    'nfd': 'Unicode canonical decomposition + canonical mark order (mark storage order is invisible)',
    'invisible': 'drop soft hyphen U+00AD, zero-width/bidi controls U+200B-U+200F, U+202A-U+202E, U+2066-U+2069, U+FEFF',
    'hair-space': 'drop hair/thin spaces U+200A/U+2009 (typesetter kerning around dashes, not word spaces)',
    'latin-ligature': 'decompose Latin ligature glyphs U+FB00-U+FB06 (fi, fl...)',
    'whitespace': 'any run of whitespace = one space; trimmed at field ends',
    'holam-vav': 'holam stored on the letter before a bare vav == holam on the vav (identical in print); U+05BA == U+05B9',
}

DROP = set('­​‌‍‎‏‪‫‬‭‮'
           '⁦⁧⁨⁩﻿  ')

# ---------------------------------------------------------------- units

# (unit id, content source, pdf pages). pdf page = siddur page + 24.
def _pages(a: int, b: int) -> list[int]:
    return list(range(a + 24, b + 24 + 1))

# Each unit's range runs from its first page through the first page of the next
# unit: sections share boundary pages (e.g. Al HaMichyah ends on Borei Nefashos's
# page). Whether print text is "missing from the app" is decided book-wide.
UNITS = {
    'shacharit': ('service:shacharit', _pages(2, 119)),
    'birkas-hamazon': ('service:birkas-hamazon', _pages(118, 129)),
    'al-hamichyah': ('service:al-hamichyah', _pages(128, 130)),
    'borei-nefashos': ('service:borei-nefashos', _pages(129, 131)),
    'tefillas-haderech': ('service:tefillas-haderech', _pages(130, 132)),
    'minchah': ('service:minchah', _pages(131, 164)),
    'maariv': ('service:maariv', _pages(163, 189)),
    'maariv-motzaei-shabbos': ('service:maariv-motzaei-shabbos', _pages(188, 191)),
    'sefiras-haomer': ('service:sefiras-haomer', _pages(190, 195)),
    'krias-shema-al-hamitah': ('service:krias-shema-al-hamitah', _pages(194, 203)),
    'netilas-lulav': ('service:netilas-lulav', _pages(202, 204)),
    'hallel': ('service:hallel', _pages(203, 212)),
    'mussaf-rosh-chodesh': ('service:mussaf-rosh-chodesh', _pages(211, 223)),
    'mussaf-chol-hamoed': ('service:mussaf-chol-hamoed', _pages(222, 239)),
    'book-matter': ('book-matter', [1, 2, 3, 4] + list(range(7, 25)) + _pages(238, 242) + [296]),
    'appendices': ('appendices', _pages(241, 269)),
    'glossary': ('glossary', _pages(268, 272)),
}
ALL_PAGES = sorted({p for _, pages in UNITS.values() for p in pages})
MIN_MATCH_RATIO = 0.5   # an app field must share >=50% of its chars with a print span to count as found

# ---------------------------------------------------------------- normalized text with provenance

@dataclass
class NText:
    """Normalized string; src[i] is the provenance of chars[i]."""
    chars: list = field(default_factory=list)
    src: list = field(default_factory=list)

    @property
    def s(self) -> str:
        return ''.join(self.chars)


def is_mark(ch: str) -> bool:
    return unicodedata.category(ch) == 'Mn'


def _clusters(items: list[tuple[str, object]]):
    """Group (char, src) into base+marks clusters."""
    out: list[list[tuple[str, object]]] = []
    for ch, src in items:
        if is_mark(ch) and out and not out[-1][0][0].isspace():
            out[-1].append((ch, src))
        else:
            out.append([(ch, src)])
    return out


def normalize(items: list[tuple[str, object]]) -> NText:
    """items: raw (char, provenance) pairs in logical order."""
    exp: list[tuple[str, object]] = []
    for ch, src in items:
        if ch in DROP:
            continue
        if 'ﬀ' <= ch <= 'ﬆ':
            for c in unicodedata.normalize('NFKD', ch):
                exp.append((c, src))
            continue
        for c in unicodedata.normalize('NFD', ch):
            exp.append(('ֹ' if c == 'ֺ' else c, src))
    cl = _clusters(exp)
    # canonical mark order inside each cluster
    for k, c in enumerate(cl):
        base, marks = c[0], c[1:]
        marks.sort(key=lambda t: unicodedata.combining(t[0]))
        cl[k] = [base] + marks
    # holam-vav: a holam on the letter before a bare vav sits on the vav
    for k in range(len(cl) - 1):
        nxt = cl[k + 1]
        if len(nxt) == 1 and nxt[0][0] == 'ו':
            hol = [t for t in cl[k][1:] if t[0] == 'ֹ']
            if hol and cl[k][0][0] != 'ו':
                cl[k] = [t for t in cl[k] if t[0] != 'ֹ']
                cl[k + 1] = nxt + hol
    out = NText()
    prev_space = True
    for c in cl:
        for ch, src in c:
            if ch.isspace():
                if prev_space:
                    continue
                out.chars.append(' ')
                out.src.append(src)
                prev_space = True
            else:
                out.chars.append(ch)
                out.src.append(src)
                prev_space = False
    while out.chars and out.chars[-1] == ' ':
        out.chars.pop()
        out.src.pop()
    return out


SKEL_RE = re.compile(r'[A-Za-z0-9א-ת]')


def skeleton(nt: NText) -> tuple[str, list[int]]:
    s, idx = [], []
    for i, ch in enumerate(nt.chars):
        if SKEL_RE.match(ch):
            s.append(ch.lower())
            idx.append(i)
    return ''.join(s), idx

# ---------------------------------------------------------------- print side

@dataclass
class Seq:
    name: str
    nt: NText
    linebreak_hyphens: set = field(default_factory=set)   # normalized idx of a '-' that ended a line
    linebreak_spaces: set = field(default_factory=set)    # join spaces at "/" or dash line breaks


def _reading_order(pcs: list) -> list:
    """Pieces of one flow on one page -> reading order: group into columns by
    horizontal overlap, read each column top-down, columns left-to-right for
    English (right-to-left for Hebrew)."""
    cols: list[list] = []
    for pc in sorted(pcs, key=lambda p: p.y):
        for col in cols:
            cx0 = min(p.x0 for p in col)
            cx1 = max(p.x1 for p in col)
            ov = min(cx1, pc.x1) - max(cx0, pc.x0)
            if ov > 0.3 * min(cx1 - cx0, pc.x1 - pc.x0):
                col.append(pc)
                break
        else:
            cols.append([pc])
    rtl = pcs and pcs[0].stream == 'he'
    cols.sort(key=lambda col: (-max(p.x1 for p in col)) if rtl else min(p.x0 for p in col))
    return [p for col in cols for p in sorted(col, key=lambda p: p.y)]


def print_sequences(pages: list[int]) -> list[Seq]:
    pieces = pdftext.pieces_for_pages(pages)
    flows: dict = {}
    for pc in pieces:
        flows.setdefault(pc.flow, []).append(pc)
    seqs = []
    for key, pcs in sorted(flows.items()):
        stream = key[0]
        ordered = []
        for pg in sorted({p.page for p in pcs}):
            ordered += _reading_order([p for p in pcs if p.page == pg])
        items: list[tuple[str, object]] = []
        hyphen_raw: set = set()
        for pc in ordered:
            if items:
                last = items[-1][0]
                if last == '\u00ad':
                    items.pop()                       # discretionary hyphen: join
                elif last in '-\u2010' and stream == 'en':
                    hyphen_raw.add(len(items) - 1)    # join, remember it was a line-end hyphen
                elif last in '/\u2014\u2013' or (pc.clusters and pc.clusters[0].text[0] in '\u2014\u2013'):
                    # a break after "/" or at a dash: whether a space was meant is
                    # invisible in print, so this join space never counts as a difference
                    items.append((' ', 'LBS'))
                else:
                    items.append((' ', None))
            for c in pc.clusters:
                ref = (pc.page, round(c.x0, 1), round(c.y0, 1), round(c.x1, 1), round(c.y1, 1))
                for ch in c.text:
                    items.append((ch, ref))
        tagged = [(ch, ('LBH', src) if i in hyphen_raw else src) for i, (ch, src) in enumerate(items)]
        nt = normalize(tagged)
        lbh = {i for i, s in enumerate(nt.src) if isinstance(s, tuple) and s and s[0] == 'LBH'}
        lbs = {i for i, s in enumerate(nt.src) if s == 'LBS'}
        nt.src = [None if s == 'LBS' else s for s in nt.src]
        nt.src = [s[1] if isinstance(s, tuple) and s and s[0] == 'LBH' else s for s in nt.src]
        seqs.append(Seq(name='-'.join(map(str, key)), nt=nt, linebreak_hyphens=lbh, linebreak_spaces=lbs))
    return seqs


# ---------------------------------------------------------------- app side

MD_TOKEN = re.compile(r'\[([^\]]+)\]\((?:section|prayer):[^)]+\)|\*\*|\*')


def strip_markdown(raw: str) -> list[tuple[str, int]]:
    """Visible chars of a RichText string with their raw offsets."""
    out: list[tuple[str, int]] = []
    i = 0
    for m in MD_TOKEN.finditer(raw):
        for k in range(i, m.start()):
            out.append((raw[k], k))
        if m.group(1) is not None:                        # link: keep its label
            lab_start = m.start() + 1
            for k in range(lab_start, lab_start + len(m.group(1))):
                out.append((raw[k], k))
        i = m.end()
    for k in range(i, len(raw)):
        out.append((raw[k], k))
    return out


@dataclass
class Field:
    file: str
    path: str              # human/JSON path to the string
    key: str               # field name
    raw: str
    markdown: bool
    nt: NText = None
    claim_text: str = None      # the normalized print text this field matched


RICH_TYPES = {'commentary', 'insight', 'faq', 'section_intro', 'transition', 'rubric'}


def _segment_fields(file: str, base: str, seg: dict) -> list[Field]:
    t = seg.get('type')
    out = []
    he_types = {'prayer', 'header', 'rubric'}
    en_types = {'commentary', 'insight', 'faq', 'section_intro', 'transition', 'rubric', 'header'}
    if t in he_types and seg.get('heText'):
        out.append(Field(file, f'{base}[{seg["id"]}]', 'heText', seg['heText'], False))
    if t == 'prayer' and seg.get('inlineRubric'):
        out.append(Field(file, f'{base}[{seg["id"]}]', 'inlineRubric', seg['inlineRubric'], False))
    if t in en_types and seg.get('enText'):
        out.append(Field(file, f'{base}[{seg["id"]}]', 'enText', seg['enText'], t in RICH_TYPES))
    return out


def app_fields(source: str) -> list[Field]:
    fields: list[Field] = []
    if source.startswith('service:'):
        sid = source.split(':', 1)[1]
        file = f'{sid}.json'
        d = json.load(open(os.path.join(CONTENT, file), encoding='utf-8'))
        for g in d['groups']:
            for p in g['prayers']:
                for seg in p['segments']:
                    fields += _segment_fields(file, p['id'], seg)
    elif source == 'appendices':
        file = 'appendices.json'
        d = json.load(open(os.path.join(CONTENT, file), encoding='utf-8'))
        for a in d['appendices']:
            for seg in a['segments']:
                fields += _segment_fields(file, f'appendix{a["number"]}', seg)
    elif source == 'book-matter':
        file = 'book-matter.json'
        d = json.load(open(os.path.join(CONTENT, file), encoding='utf-8'))
        for pc in d['pieces']:
            for k in ('title', 'subtitle'):
                if pc.get(k):
                    fields.append(Field(file, pc['id'], k, pc[k], False))
            for seg in pc['segments']:
                fields += _segment_fields(file, pc['id'], seg)
    elif source == 'glossary':
        file = 'glossary.json'
        d = json.load(open(os.path.join(CONTENT, file), encoding='utf-8'))
        for i, e in enumerate(d['entries']):
            # printed as "term—definition"; checked as one string, offsets split back below
            fields.append(Field(file, f'entries[{i}]', 'term—definition',
                                e['term'] + '—' + e['definition'], False))
    for f in fields:
        items = strip_markdown(f.raw) if f.markdown else [(ch, i) for i, ch in enumerate(f.raw)]
        f.nt = normalize(items)
    return [f for f in fields if f.nt.chars]

# ---------------------------------------------------------------- matching

K = 10


class Index:
    def __init__(self, seqs: list[Seq]):
        self.seqs = seqs
        self.skel = []
        self.map = {}
        for si, sq in enumerate(seqs):
            s, idx = skeleton(sq.nt)
            self.skel.append((s, idx))
            for j in range(len(s) - K + 1):
                self.map.setdefault(s[j:j + K], []).append((si, j))
        self.claimed = [[False] * len(sq.nt.chars) for sq in seqs]

    def candidates(self, sk: str) -> list[tuple[int, int, int]]:
        """(seq, skeleton start, votes) for an app skeleton."""
        if len(sk) >= 2 * K:
            votes: dict = {}
            step = 1 if len(sk) < 200 else 3
            for i in range(0, len(sk) - K + 1, step):
                for si, j in self.map.get(sk[i:i + K], ())[:400]:
                    d = j - i
                    key = (si, d // 4)
                    votes[key] = votes.get(key, 0) + 1
            if not votes:
                return []
            best = []
            for (si, b), v in votes.items():
                best.append((si, b * 4, v))
            best.sort(key=lambda t: -t[2])
            top = best[0][2]
            return [c for c in best if c[2] >= max(2, top * 0.6)][:30]
        out = []
        for si, (s, _) in enumerate(self.skel):
            start = 0
            while True:
                j = s.find(sk, start)
                if j < 0:
                    break
                out.append((si, j, len(sk)))
                start = j + 1
        return out


@dataclass
class Diff:
    unit: str
    file: str
    path: str
    key: str
    kind: str                # replace | app-only | print-only
    app: str                 # normalized app text of the difference
    print: str               # normalized print text of the difference
    app_raw_span: list       # [start, end) in the raw JSON string (may be None)
    app_context: str
    print_context: str
    pages: list
    boxes: list
    cls: str = ''
    fingerprint: str = ''
    field_ratio: float = 0.0     # share of the field's chars that matched the print span


def _box_union(srcs):
    srcs = [s for s in srcs if s]
    if not srcs:
        return [], []
    pages = sorted({s[0] for s in srcs})
    boxes = []
    for p in pages:
        ss = [s for s in srcs if s[0] == p]
        boxes.append([p, min(s[1] for s in ss), min(s[2] for s in ss), max(s[3] for s in ss), max(s[4] for s in ss)])
    return pages, boxes


def _align(f: Field, sq: Seq, a: int, b: int):
    """Align field f against print span ~[a, b]; returns (ratio, claim0, claim1)."""
    pad = 40
    w0 = max(0, a - pad)
    w1 = min(len(sq.nt.chars), b + 1 + pad)
    win = sq.nt.chars[w0:w1]
    sm = difflib.SequenceMatcher(None, f.nt.chars, win, autojunk=False)
    ops = sm.get_opcodes()
    eq = [o for o in ops if o[0] == 'equal']
    if not eq:
        return 0.0, 0, 0
    first, last = eq[0], eq[-1]
    claim0 = w0 + first[3]
    claim1 = w0 + last[4]
    head = [o for o in ops if o[1] < first[1]]
    tail = [o for o in ops if o[2] > last[2]]
    # An edge substitution may claim print text only within the same word.
    if head and head[-1][0] == 'replace' and ' ' not in ''.join(win[head[-1][3]:head[-1][4]]):
        claim0 = w0 + head[-1][3]
    if tail and tail[0][0] == 'replace' and ' ' not in ''.join(win[tail[0][3]:tail[0][4]]):
        claim1 = w0 + tail[0][4]
    # A match never ends mid-word: if the app's first/last word is cut short
    # (e.g. "ugya" for print "sugya"), the rest of the print word is part of
    # this field's span and shows up as a difference.
    ch = sq.nt.chars
    while claim0 > 0 and ch[claim0 - 1] != ' ' and ch[claim0] != ' ':
        claim0 -= 1
    while claim1 < len(ch) and ch[claim1] != ' ' and ch[claim1 - 1] != ' ':
        claim1 += 1
    matched = sum(o[2] - o[1] for o in eq)
    return matched / max(1, len(f.nt.chars)), claim0, claim1


def match_unit(unit: str, seqs: list[Seq] | None = None, fields: list[Field] | None = None):
    """Diffs for one unit. Returns (diffs, stats, claimed_refs, seqs)."""
    source, pages = UNITS[unit]
    seqs = seqs if seqs is not None else print_sequences(pages)
    fields = fields if fields is not None else app_fields(source)
    idx = Index(seqs)
    diffs: list[Diff] = []
    placements = [None] * len(fields)

    order = sorted(range(len(fields)), key=lambda k: -len(skeleton(fields[k].nt)[0]))
    for k in order:
        f = fields[k]
        sk, skidx = skeleton(f.nt)
        if not sk:
            continue
        cands = idx.candidates(sk)
        if not cands:
            placements[k] = 'unfound'
            continue
        prev = next((placements[j] for j in range(k - 1, -1, -1) if isinstance(placements[j], tuple)), None)
        nxt = next((placements[j] for j in range(k + 1, len(fields)) if isinstance(placements[j], tuple)), None)

        def span_of(c):
            si, j, v = c
            s, sidx = idx.skel[si]
            a = sidx[min(max(j, 0), len(sidx) - 1)]
            b = sidx[min(max(j + len(sk) - 1, 0), len(sidx) - 1)]
            return si, a, b

        def score(c):
            si, a, b = span_of(c)
            v = c[2]
            overlap = sum(idx.claimed[si][a:b + 1]) / max(1, b - a + 1)
            pen = 0
            if prev and prev[0] == si and a < prev[1]:
                pen += 1
            if nxt and nxt[0] == si and a > nxt[1]:
                pen += 1
            dist = abs(a - prev[2]) if prev and prev[0] == si else 0
            # short text (a header, a label) must sit on whole words, not inside one
            ch = seqs[si].nt.chars
            mid = (a > 0 and ch[a - 1] not in ' ([“"\'—' and not is_mark(ch[a - 1]) and ch[a - 1].isalpha()) + \
                  (b + 1 < len(ch) and not is_mark(ch[b + 1]) and ch[b + 1].isalpha())
            return (-v + pen * 1000 + overlap * 5000 + mid * 800, dist)

        best = None
        for c in sorted(cands, key=score)[:5]:
            si, a, b = span_of(c)
            ratio, c0, c1 = _align(f, seqs[si], a, b)
            overlap = sum(idx.claimed[si][c0:c1]) / max(1, c1 - c0)
            key = (ratio - overlap, ratio)
            if best is None or key > best[0]:
                best = (key, si, c0, c1, ratio)
            if ratio > 0.98 and overlap == 0:
                break
        if best is None or best[4] < MIN_MATCH_RATIO:
            placements[k] = 'unfound'
            continue
        _, si, claim0, claim1, ratio = best
        sq = seqs[si]
        for i in range(claim0, claim1):
            idx.claimed[si][i] = True
        placements[k] = (si, claim0, claim1)
        f.claim_text = ''.join(sq.nt.chars[claim0:claim1])
        span = sq.nt.chars[claim0:claim1]
        sm2 = difflib.SequenceMatcher(None, f.nt.chars, span, autojunk=False)
        for tag, i1, i2, j1, j2 in sm2.get_opcodes():
            if tag == 'equal':
                continue
            pj1, pj2 = claim0 + j1, claim0 + j2
            app_txt = ''.join(f.nt.chars[i1:i2])
            pr_txt = ''.join(sq.nt.chars[pj1:pj2])
            # a line-end hyphen in print vs none in the app is typesetting, not text
            if tag == 'insert' and pr_txt == '-' and pj1 in sq.linebreak_hyphens:
                continue
            if tag == 'insert' and pr_txt == ' ' and pj1 in sq.linebreak_spaces:
                continue
            if tag == 'delete' and app_txt == ' ' and any(
                    i in sq.linebreak_spaces for i in range(max(0, pj1 - 1), pj1 + 1)):
                continue
            raw_srcs = [f.nt.src[i] for i in range(i1, i2)]
            if raw_srcs:
                raw_span = [min(raw_srcs), max(raw_srcs) + 1]
            else:
                at = f.nt.src[i1] if i1 < len(f.nt.src) else (f.nt.src[-1] + 1 if f.nt.src else 0)
                raw_span = [at, at]
            pr_srcs = [sq.nt.src[i] for i in range(max(0, pj1 - 1), min(len(sq.nt.src), pj2 + 1))]
            pg, bx = _box_union(pr_srcs)
            diffs.append(Diff(
                unit=unit, file=f.file, path=f.path, key=f.key,
                kind={'replace': 'replace', 'delete': 'app-only', 'insert': 'print-only'}[tag],
                app=app_txt, print=pr_txt, app_raw_span=raw_span,
                app_context=''.join(f.nt.chars[max(0, i1 - 25):i2 + 25]),
                print_context=''.join(sq.nt.chars[max(0, pj1 - 25):pj2 + 25]),
                pages=pg, boxes=bx, field_ratio=round(ratio, 3),
            ))

    unfound = [fields[k] for k in range(len(fields)) if placements[k] in (None, 'unfound')]
    for f in unfound:
        diffs.append(Diff(unit=unit, file=f.file, path=f.path, key=f.key, kind='app-only-field',
                          app=f.nt.s, print='', app_raw_span=[0, len(f.raw)],
                          app_context=f.nt.s[:160], print_context='', pages=[], boxes=[]))
    claimed_refs = set()
    for si, sq in enumerate(seqs):
        for i, c in enumerate(idx.claimed[si]):
            if c and sq.nt.src[i]:
                claimed_refs.add(sq.nt.src[i])
    for d in diffs:
        d.cls = classify(d)
        d.fingerprint = fingerprint(d)
    stats = {
        'fields': len(fields),
        'fields_unfound': len(unfound),
        'app_chars': sum(len(f.nt.chars) for f in fields),
    }
    return diffs, stats, claimed_refs


def coverage(claimed_refs: set) -> list[Diff]:
    """Book-wide: print text (by glyph) that no app field claimed, grouped by line."""
    out = []
    page_units = {}
    for u, (_, pages) in UNITS.items():
        for p in pages:
            page_units.setdefault(p, []).append(u)
    for pc in pdftext.pieces_for_pages(ALL_PAGES):
        run, run_refs = [], []

        def flush():
            txt = ''.join(run).strip()
            if txt and (LAT.search(txt) or HEB.search(txt) or re.search(r'\w', txt)):
                pg, bx = _box_union(run_refs)
                out.append(Diff(unit='|'.join(page_units.get(pc.page, [])), file='', path=f'p{pc.page}',
                                key=pc.stream, kind='print-unclaimed', app='', print=txt,
                                app_raw_span=None, app_context='', print_context=pc.text[:200],
                                pages=pg, boxes=bx))
            run.clear()
            run_refs.clear()

        for c in pc.clusters:
            ref = (pc.page, round(c.x0, 1), round(c.y0, 1), round(c.x1, 1), round(c.y1, 1))
            visible = normalize([(ch, None) for ch in c.text]).chars
            if not visible or visible == [' ']:
                if run:
                    run.append(' ')
                continue
            if ref in claimed_refs:
                flush()
            else:
                run.append(c.text)
                run_refs.append(ref)
        flush()
    for d in out:
        d.cls = classify(d)
        d.fingerprint = fingerprint(d)
    return out


def run_all(units: list[str] | None = None):
    units = units or list(UNITS)
    all_diffs, stats, claimed = [], {}, set()
    for u in units:
        d, st, refs = match_unit(u)
        all_diffs += d
        stats[u] = st
        claimed |= refs
    cov = coverage(claimed) if set(units) == set(UNITS) else []
    return all_diffs + cov, stats


# ---------------------------------------------------------------- classification

DIVINE = re.compile('י[֑-ׇ]*ה[֑-ׇ]*ו[֑-ׇ]*ה')
HEB = re.compile(r'[֑-״]')
LAT = re.compile(r'[A-Za-z]')


def classify(d: Diff) -> str:
    if d.kind == 'print-unclaimed':
        return 'missing-from-app' if (LAT.search(d.print) or HEB.search(d.print)) else 'print-residue'
    if d.kind == 'app-only-field':
        return 'not-in-print'
    both = d.app + d.print
    if both.strip() == '':
        return 'spacing'
    if HEB.search(both):
        ctx = d.print_context + d.app_context
        if set(both) <= {'ֹ'} and DIVINE.search(unicodedata.normalize('NFD', d.print_context)):
            return 'he-divine-name'
        if both.strip() and all('֑' <= c <= '֯' for c in both.replace(' ', '')):
            return 'he-cantillation'
        letters = [c for c in both if 'א' <= c <= 'ת']
        if letters:
            return 'he-letter'
        if '־' in both:
            return 'he-maqaf'
        if 'ֽ' in both and set(both) <= {'ֽ'}:
            return 'he-meteg'
        if all(is_mark(c) for c in both):
            return 'he-nikud'
        return 'he-other'
    if d.app.lower() == d.print.lower() and d.app != d.print:
        return 'en-case'
    if LAT.search(both):
        return 'en-letter'
    if re.search(r'\d', both):
        return 'en-digit'
    if set(both) <= set(' '):
        return 'spacing'
    if re.search('[—–-]', both):
        return 'en-dash'
    if re.search('[\'"‘’“”]', both):
        return 'en-quote'
    return 'en-punct'


def fingerprint(d: Diff) -> str:
    import hashlib
    key = f'{d.unit}|{d.path}|{d.key}|{d.kind}|{d.app}|{d.print}|{d.app_context}'
    return hashlib.sha1(key.encode('utf-8')).hexdigest()[:12]


if __name__ == '__main__':
    import sys
    from collections import Counter
    diffs, stats = run_all(sys.argv[1:] or None)
    for u, st in stats.items():
        c = Counter(d.cls for d in diffs if d.unit == u)
        print(u, st, dict(c))
    cov = [d for d in diffs if d.kind == 'print-unclaimed']
    if cov:
        print('coverage', dict(Counter(d.cls for d in cov)))
