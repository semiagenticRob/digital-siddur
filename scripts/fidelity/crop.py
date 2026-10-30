"""Render the print glyphs behind a finding, for review.

Run:  python scripts/fidelity/crop.py <finding id> [out.png]
Looks the id up in docs/fidelity/findings/*.json and renders its print box(es)
at 400 DPI with a margin, so a reviewer sees exactly what the print shows.
"""
import glob
import json
import os
import sys

import pymupdf

import pdftext

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def find(fid):
    for f in glob.glob(os.path.join(ROOT, 'docs', 'fidelity', 'findings', '*.json')):
        for item in json.load(open(f, encoding='utf-8')):
            if item['id'] == fid:
                return item
    raise SystemExit(f'no finding {fid}')


def main(fid, out):
    item = find(fid)
    if not item['boxes']:
        raise SystemExit('finding has no print location (app-only)')
    doc = pdftext.doc()
    pg, x0, y0, x1, y1 = item['boxes'][0]
    page = doc[pg - 1]
    clip = pymupdf.Rect(max(0, x0 - 60), max(0, y0 - 14), min(page.rect.x1, x1 + 60), min(page.rect.y1, y1 + 14))
    pix = page.get_pixmap(dpi=400, clip=clip)
    pix.save(out)
    print(f'p{pg} {item["class"]}: app {item["app"]!r} / print {item["print"]!r} -> {out}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else f'{sys.argv[1]}.png')
