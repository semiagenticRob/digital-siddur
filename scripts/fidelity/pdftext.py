"""Exact text extraction from the print PDF, rebuilt from glyph geometry.

Why not plain `get_text()`: the print's text layer has two defects that would
produce false differences (and could hide real ones):

1. Word order. Some Hebrew lines come out in visual (left-to-right) word order.
   We ignore stream order between glyphs and read every line by position:
   right-to-left for Hebrew lines, left-to-right for English lines with each
   embedded Hebrew run reversed (Unicode bidi rules for neutrals).
2. Nikud order. MuPDF's logical reversal of RTL spans also reverses the inside
   of letter+mark ligature glyphs (e.g. bet-with-dagesh -> "ּב"). We build
   glyph clusters from the raw drawing trace instead, where the rule is
   consistent in both Hebrew fonts: a ligature continuation (glyph id -1)
   belongs to the glyph before it, and a standalone mark glyph belongs to the
   NEXT base glyph in drawing order.

Every output character keeps a reference to the glyph box it came from, so a
difference can be shown as a crop of the exact print glyphs.
"""
from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field

import pymupdf

PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'feigenbaum-siddur-original.pdf')
TOP_BAND = 34.0          # running heads + folios live above this (verified on all 296 pages)
COLUMN_SPLIT_EM = 3.0    # same-baseline gap (in em) that separates two columns
GAP_SPACE_EM = 0.125     # a visible word space = ink gap above this (in em). Measured over the
                         # whole book: glyphs with no space between gap <=0.05em (max 0.10);
                         # real word spaces gap >=0.15em. Space glyphs themselves are ignored:
                         # ~1,600 are kerned to nothing (e.g. 'term—definition' in the glossary).
SPACE_GLYPH_GAP_EM = 0.075  # ...unless a space glyph IS drawn there and the gap is at least this:
                         # tightly-set lines have real word spaces of ~0.10em, while kerned-away
                         # spaces sit at <=0.05em.
REGION_SPLIT_X = 167.0
MARK_LINE_EM = 0.8        # marks may sit up to ~0.4em off their letter's baseline; lines are >=1.2em apart   # commentary column ends / main column starts (page is 368pt wide)

HEB_LETTER = re.compile(r'[א-תיִ-ﭏ]')


def is_mark(ch: str) -> bool:
    return unicodedata.category(ch) == 'Mn'


def is_hebrew_mark(ch: str) -> bool:
    return '֑' <= ch <= 'ׇ' and is_mark(ch)


def bidi_class(text: str) -> str:
    """'R' Hebrew, 'L' Latin/digit, 'N' neutral, 'S' space — of a cluster's base."""
    base = text[0]
    if base.isspace():
        return 'S'
    if HEB_LETTER.match(base) or base in '־׀׃׆׳״':
        return 'R'
    cat = unicodedata.category(base)
    if cat.startswith('L') or cat == 'Nd':
        return 'L'
    return 'N'


def font_name(raw: str) -> str:
    return raw.split('+')[-1]


def stream_of(font: str, size: float, text: str) -> str:
    """'he' = Hebrew liturgical/heading text, 'en' = English (incl. inline Hebrew citations)."""
    if 'Livorna' in font or 'AdobeHebrew' in font:
        return 'he'
    if 'RmzHadas' in font:
        return 'he' if size >= 10.5 else 'en'
    return 'en'


@dataclass
class Cluster:
    text: str                      # base + its marks/continuations, drawing order fixed
    x0: float
    x1: float
    y0: float
    y1: float
    base_y: float                  # baseline of the base glyph
    size: float
    font: str
    stream: str
    page: int
    synthetic: bool = False        # a space we inferred from a gap (no glyph drawn)
    flow: tuple = None             # set for inline Hebrew citations: the flow of their sentence

    @property
    def cls(self) -> str:
        return bidi_class(self.text)


@dataclass
class Piece:
    """One line of one column on one page, in logical (reading) order."""
    page: int
    stream: str
    region: str                    # 'L' commentary column, 'R' main column, 'W' wide
    y: float
    x0: float
    x1: float
    clusters: list = field(default_factory=list)
    flow: tuple = ()

    @property
    def text(self) -> str:
        return ''.join(c.text for c in self.clusters)


ORPHAN_STATS = {'attached': 0, 'unplaced': 0}


def page_clusters(page: pymupdf.Page, pno: int) -> list[Cluster]:
    out: list[Cluster] = []
    orphans: list[tuple] = []              # lists of (mark, origin) placed by position
    pending: list[tuple] = []              # standalone marks waiting for their base;
                                           # may continue into the next drawing run
    pending_font = None
    for tr in page.get_texttrace():
        font = font_name(tr['font'])
        size = round(tr['size'], 2)
        for u, gid, origin, bbox in tr['chars']:
            ch = chr(u)
            if gid == -1 and out and out[-1].page == pno and ch != ' ':
                # ligature continuation: belongs to the glyph just drawn
                prev = out[-1]
                prev.text += ch
                continue
            if is_hebrew_mark(ch):
                if pending and (pending_font != font or abs(pending[0][1][1] - origin[1]) > MARK_LINE_EM * size):
                    orphans.append(pending)
                    pending = []
                pending.append((ch, origin))
                pending_font = font
                continue
            if pending and (ch.isspace() or pending_font != font
                            or abs(pending[0][1][1] - origin[1]) > MARK_LINE_EM * size):
                # a mark drawn after its letter with no letter following it on the
                # same line in the same font (e.g. a line-final shuruk dagesh):
                # place it by position below
                orphans.append(pending)
                pending = []
            text = ch + ''.join(m for m, _ in pending)
            pending = []
            out.append(Cluster(
                text=text, x0=bbox[0], x1=bbox[2], y0=bbox[1], y1=bbox[3],
                base_y=round(origin[1], 1), size=size, font=font,
                stream=stream_of(font, size, ch), page=pno,
            ))
    if pending:
        orphans.append(pending)
    # Attach orphaned marks to the Hebrew letter whose box they sit over.
    for marks in orphans:
        mx, my = marks[0][1]
        cands = [c for c in out if bidi_class(c.text) == 'R'
                 and abs(c.base_y - my) <= MARK_LINE_EM * c.size]
        if not cands:
            ORPHAN_STATS['unplaced'] += len(marks)
            continue
        best = min(cands, key=lambda c: 0 if c.x0 - 0.5 <= mx <= c.x1 + 0.5
                   else min(abs(mx - c.x0), abs(mx - c.x1)))
        best.text += ''.join(m for m, _ in marks)
        ORPHAN_STATS['attached'] += len(marks)
    return [c for c in out if c.y1 >= TOP_BAND]


def _bidi_order(clusters: list[Cluster], rtl: bool) -> list[Cluster]:
    """Visual (left-to-right sorted) clusters -> logical order."""
    vis = sorted(clusters, key=lambda c: (c.x0 + c.x1) / 2)
    if rtl:
        seq = vis[::-1]
        strong, weak = 'L', 'R'
    else:
        seq = vis
        strong, weak = 'R', 'L'
    # Reverse each maximal run of the "foreign" direction, including neutrals and
    # spaces that sit strictly between two foreign clusters (UBA rules N1/N2).
    out = list(seq)
    i = 0
    n = len(out)
    while i < n:
        if out[i].cls != strong:
            i += 1
            continue
        j = i
        k = i
        while k + 1 < n:
            nxt = out[k + 1]
            if nxt.cls == strong:
                k += 1
                j = k
            elif nxt.cls in ('N', 'S'):
                k += 1
            else:
                break
        out[i:j + 1] = out[i:j + 1][::-1]
        i = j + 1
    return out


def _with_gap_spaces(vis: list[Cluster], spaces: list[Cluster]) -> list[Cluster]:
    """Word spaces from geometry: a space wherever the ink gap is word-sized.

    `vis` holds ink clusters only, left to right; `spaces` the space glyphs."""
    centers = sorted((sp.x0 + sp.x1) / 2 for sp in spaces)
    out: list[Cluster] = []
    import bisect
    for c in vis:
        if out:
            p = out[-1]
            gap = c.x0 - p.x1
            em = max(c.size, p.size)
            k = bisect.bisect_left(centers, p.x1 - 0.5 * em)
            glyph_between = k < len(centers) and centers[k] <= c.x0 + 0.5 * em
            # Spaces kerned up against an em/en dash are typesetting, not word
            # spaces: next to a dash only a clearly visible gap counts.
            by_dash = p.text[0] in '\u2014\u2013' or c.text[0] in '\u2014\u2013'
            if gap > GAP_SPACE_EM * em or (glyph_between and not by_dash
                                           and gap >= SPACE_GLYPH_GAP_EM * em):
                out.append(Cluster(' ', p.x1, c.x0, min(p.y0, c.y0), max(p.y1, c.y1),
                                   c.base_y, c.size, c.font, c.stream, c.page, synthetic=True))
        out.append(c)
    return out


def region_of(x0: float, x1: float) -> str:
    if x1 <= REGION_SPLIT_X + 3:
        return 'L'
    if x0 >= REGION_SPLIT_X - 2:
        return 'R'
    return 'W'


SANS = ('Gotham', 'Quiche')


def flow_key(c: Cluster) -> tuple:
    """Which text flow a glyph belongs to. Side-by-side blocks on one page (an
    'Instant Insight' sidebar, an intro, the commentary column) are told apart by
    typeface class and size; Hebrew liturgy is one flow (small inline speaker
    tags must stay inside their line)."""
    if c.stream == 'he':
        return ('he',)
    if c.flow is not None:
        return c.flow
    family = 'sans' if any(f in c.font for f in SANS) else 'serif'
    return ('en', family, round(c.size))


def _adopt_inline_hebrew(clusters: list[Cluster]) -> None:
    """Prayer-font Hebrew set inside an English sentence (e.g. He is "סוֹמֵךְ")
    belongs to that English line: move it to the English flow when English
    ink sits on the same baseline on both sides of it, close by."""
    en_rows: dict = {}
    for c in clusters:
        if c.stream == 'en' and not c.text.isspace():
            en_rows.setdefault(round(c.base_y), []).append(c)
    for c in clusters:
        if c.stream != 'he' or c.text.isspace():
            continue
        row = []
        for dy in (-1, 0, 1):
            row += en_rows.get(round(c.base_y) + dy, [])
        if not row:
            continue
        reach = 2.5 * c.size
        left = any(e.x1 <= c.x0 + 0.5 and c.x0 - e.x1 <= reach for e in row)
        right = any(e.x0 >= c.x1 - 0.5 and e.x0 - c.x1 <= reach for e in row)
        if left and right:
            near = min(row, key=lambda e: min(abs(e.x0 - c.x1), abs(c.x0 - e.x1)))
            c.stream = 'en'
            c.size = near.size
            c.font = near.font


def page_pieces(page: pymupdf.Page, pno: int) -> list[Piece]:
    clusters = page_clusters(page, pno)
    # run twice so a multi-word Hebrew phrase is adopted from both ends inward
    _adopt_inline_hebrew(clusters)
    _adopt_inline_hebrew(clusters)
    pieces: list[Piece] = []
    # Inline Hebrew citations take the flow of the English sentence around them.
    latin = [c for c in clusters if c.stream == 'en' and not c.text.isspace()
             and HEB_LETTER.match(c.text[0]) is None]
    for c in clusters:
        if c.stream == 'en' and HEB_LETTER.match(c.text[0]):
            row = [e for e in latin if abs(e.base_y - c.base_y) <= 0.35 * max(e.size, c.size)]
            if row:
                near = min(row, key=lambda e: min(abs(e.x0 - c.x1), abs(c.x0 - e.x1)))
                if min(abs(near.x0 - c.x1), abs(c.x0 - near.x1)) <= 6 * c.size:
                    c.flow = flow_key(near)
    keys = sorted({flow_key(c) for c in clusters if not c.text.isspace()})
    for key in keys:
        stream = key[0]
        # space glyphs join the flow of the nearest ink on their line
        cs = [c for c in clusters if (not c.text.isspace() and flow_key(c) == key)
              or (c.text.isspace() and c.stream == stream)]
        # group by baseline
        cs.sort(key=lambda c: c.base_y)
        rows: list[list[Cluster]] = []
        for c in cs:
            if rows and abs(rows[-1][0].base_y - c.base_y) <= 0.35 * max(c.size, rows[-1][0].size):
                rows[-1].append(c)
            else:
                rows.append([c])
        for row in rows:
            row.sort(key=lambda c: c.x0)
            # split into columns at big gaps
            groups: list[list[Cluster]] = [[]]
            for c in row:
                g = groups[-1]
                last = next((x for x in reversed(g) if not x.text.isspace()), None)
                if last and not c.text.isspace() and c.x0 - last.x1 > COLUMN_SPLIT_EM * max(c.size, last.size):
                    groups.append([])
                groups[-1].append(c)
            for g in groups:
                ink = [c for c in g if not c.text.isspace()]
                if not ink:
                    continue
                vis = _with_gap_spaces(sorted(ink, key=lambda c: c.x0),
                                       [c for c in g if c.text.isspace()])
                # A line with no Latin letters is a right-to-left line (e.g. small
                # Hebrew labels set in the commentary font), whatever its stream.
                has_latin = any(c.cls == 'L' and not c.text[0].isdigit() for c in vis)
                logical = _bidi_order(vis, rtl=(stream == 'he' or not has_latin))
                # trim leading/trailing spaces
                while logical and logical[0].text.isspace():
                    logical.pop(0)
                while logical and logical[-1].text.isspace():
                    logical.pop()
                x0 = min(c.x0 for c in ink)
                x1 = max(c.x1 for c in ink)
                pieces.append(Piece(page=pno, stream=stream, region=region_of(x0, x1),
                                    y=min(c.y0 for c in ink), x0=x0, x1=x1, clusters=logical,
                                    flow=key))
    return pieces


_DOC = None


def doc() -> pymupdf.Document:
    global _DOC
    if _DOC is None:
        _DOC = pymupdf.open(PDF_PATH)
    return _DOC


def pieces_for_pages(pages: list[int]) -> list[Piece]:
    d = doc()
    out: list[Piece] = []
    for pno in pages:
        out.extend(page_pieces(d[pno - 1], pno))
    return out


if __name__ == '__main__':
    import sys
    for pc in pieces_for_pages([int(a) for a in sys.argv[1:]]):
        print(f'p{pc.page} {pc.stream} {pc.region} y{pc.y:5.0f} | {pc.text}')
