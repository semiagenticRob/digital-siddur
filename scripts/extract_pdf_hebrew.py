#!/usr/bin/env python3
"""Extract vocalized Hebrew PRAYER TEXT from the print PDF, cleaned of the text
layer's spurious intra-word spaces via glyph geometry.

The PDF's Hebrew text layer has correctly-ORDERED nikud (via PyMuPDF) but inserts
spurious spaces between letters. This re-inserts word breaks purely from glyph
geometry (gaps between consonant clusters wider than ~0.35x avg char width), and
filters to the large prayer-text font so commentary-citation fonts (which have a
worse dagesh-order problem) are excluded.

REQUIRES the venv: /tmp/pdfvenv/bin/python scripts/extract_pdf_hebrew.py <pdfpage> [minsize]
Output is BEST-EFFORT and MUST be rav-verified before shipping (per REVIEW_QUEUE).
"""
import sys, re, unicodedata
import fitz  # PyMuPDF (venv)

PDF = 'feigenbaum-siddur-original.pdf'
MARK = lambda c: unicodedata.category(c) == 'Mn'
HE = lambda c: bool(re.match(r'[֐-׿]', c))

def clean(chars):
    glyphs = [c for c in chars if c['c'] not in (' ', '\xa0')]
    widths = [c['bbox'][2]-c['bbox'][0] for c in glyphs if not MARK(c['c']) and HE(c['c'])]
    avgw = sum(widths)/len(widths) if widths else 10
    out, prev = [], None
    for c in glyphs:
        ch = c['c']
        if prev is not None and not MARK(ch):
            if prev['bbox'][0] - c['bbox'][2] > 0.35*avgw:
                out.append(' ')
        out.append(ch)
        if not MARK(ch):
            prev = c
    return ''.join(out).strip()

def main():
    pg = int(sys.argv[1])
    minsize = float(sys.argv[2]) if len(sys.argv) > 2 else 15.5
    d = fitz.open(PDF)
    p = d[pg-1]
    for b in p.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            chars = [c for s in l['spans'] if s['size'] >= minsize for c in s['chars']]
            if any(HE(c['c']) for c in chars):
                line = clean(chars)
                if re.search(r'[֐-׿]', line):
                    print(line)

if __name__ == '__main__':
    main()
