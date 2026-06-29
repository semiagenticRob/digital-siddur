#!/usr/bin/env python3
"""Parallel-safe segment dump for audit subagents.

Prints a prayer's segments to STDOUT (no temp files, so many auditors can run
concurrently). Each line: index | type | id | flags | heText | enText.

Usage:
  python3 scripts/dump_segments.py <content-file> <prayer-id>
  python3 scripts/dump_segments.py appendices.json <appendix-number>

PDF page = siddur page + 24. Hebrew is shown verbatim (with nikud) so the
auditor can compare consonant skeletons against the print.
"""
import json, sys, os

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
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    cfile, pid = sys.argv[1], sys.argv[2]
    path = cfile if os.path.exists(cfile) else os.path.join('src/content', cfile)
    data = json.load(open(path))

    prayer = None
    # appendices.json: list of {number, title, segments} or {appendices:[...]}
    if os.path.basename(path) == 'appendices.json':
        apps = data if isinstance(data, list) else data.get('appendices', [])
        for a in apps:
            if str(a.get('number')) == str(pid):
                prayer = {'id': f'appendix-{pid}', 'enTitle': a.get('title', ''),
                          'heTitle': '', 'segments': a.get('segments', [])}
                break
    else:
        prayer = find_prayer(data, pid)

    if not prayer:
        print(f'prayer/appendix {pid!r} not found in {path}'); sys.exit(1)

    print(f'FILE: {path}')
    print(f'PRAYER: {prayer.get("id")}  heTitle={prayer.get("heTitle","")!r}  enTitle={prayer.get("enTitle","")!r}')
    print(f'SEGMENTS: {len(prayer["segments"])}')
    print('=' * 80)
    for i, s in enumerate(prayer['segments']):
        flags = [k for k in ('optional','display','center','enTop','enPrimary','plain')
                 if s.get(k)]
        flagstr = (' [' + ','.join(flags) + ']') if flags else ''
        cond = f' cond={s["condition"]!r}' if s.get('condition') else ''
        print(f'\n[{i}] type={s["type"]} id={s.get("id")}{flagstr}{cond}')
        if s.get('heText'):
            print(f'    HE: {s["heText"]}')
        if s.get('enText'):
            print(f'    EN: {s["enText"]}')
        if s.get('inlineRubric'):
            print(f'    inlineRubric: {s["inlineRubric"]}')

if __name__ == '__main__':
    main()
