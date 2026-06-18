#!/usr/bin/env python3
"""Prep a section for a proactive print-vs-app audit.

Renders the print pages and dumps the app segments so vision subagents can diff
them. Usage:

  python3 scripts/audit_prep.py <content-file> <prayer-id> <siddur-start> <siddur-end>

e.g. python3 scripts/audit_prep.py shacharit.json p-birchos-krias-shema 51 54

Outputs to /tmp/audit/: page-<pdf>.png per page, and segments.json (the prayer's
segments). PDF page = siddur page + 24. Then dispatch one vision agent per page
to mark up segments.json against the rendered page (see docs/CONTENT_GUIDE.md).
"""
import json, sys, os, subprocess, glob

PDF = 'feigenbaum-siddur-original.pdf'
OFFSET = 24
OUT = '/tmp/audit'

def find_prayer(node, pid):
    if isinstance(node, dict):
        if node.get('id') == pid and isinstance(node.get('segments'), list):
            return node
        for v in node.values():
            r = find_prayer(v, pid)
            if r: return r
    elif isinstance(node, list):
        for x in node:
            r = find_prayer(x, pid)
            if r: return r
    return None

def main():
    if len(sys.argv) != 5:
        print(__doc__); sys.exit(1)
    cfile, pid, s_start, s_end = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    path = cfile if os.path.exists(cfile) else os.path.join('src/content', cfile)
    prayer = find_prayer(json.load(open(path)), pid)
    if not prayer:
        print(f'prayer id {pid!r} not found in {path}'); sys.exit(1)

    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(f'{OUT}/*'):
        os.remove(f)

    dump = [{'i': i, 'type': s['type'], 'id': s.get('id'),
             'heText': s.get('heText', ''), 'enText': s.get('enText', '')}
            for i, s in enumerate(prayer['segments'])]
    json.dump({'file': path, 'prayer': pid, 'segments': dump},
              open(f'{OUT}/segments.json', 'w'), ensure_ascii=False, indent=2)

    for sp in range(s_start, s_end + 1):
        pdf_pg = sp + OFFSET
        subprocess.run(['pdftoppm', '-png', '-r', '300', '-f', str(pdf_pg), '-l', str(pdf_pg),
                        PDF, f'{OUT}/page-{pdf_pg}', '-singlefile'], check=True)

    pages = sorted(glob.glob(f'{OUT}/page-*.png'))
    print(f'Prepped {pid}: {len(dump)} segments, {len(pages)} print pages -> {OUT}/')
    print(f'  segments: {OUT}/segments.json')
    for p in pages:
        print(f'  page:     {p}')
    print('\nNext: dispatch one vision agent per page to mark up segments.json'
          ' against the page (see docs/CONTENT_GUIDE.md). Verify edits with strip-diff.')

if __name__ == '__main__':
    main()
