#!/usr/bin/env python3
"""Extract the Glossary (siddur p.269 ff -> pdf p.293 ff) into glossary.json.

Deterministic: asserts the GLOSSARY heading is present and that entry count
lands in the expected range, so a bad pdftotext run fails loudly.

Entry format in the print: "term—definition." (em dash, U+2014, usually with
no visible space either side; pdftotext sometimes inserts a space before the
dash depending on kerning, so the regex tolerates optional whitespace on
either side). A few definitions wrap to a second physical line (e.g.
"sandek"); those continuation lines carry no dash and are appended to the
current entry.
"""
import json
import re
import subprocess

PDF = 'feigenbaum-siddur-original.pdf'
raw = subprocess.run(
    ['pdftotext', '-f', '293', '-l', '294', PDF, '-'],
    capture_output=True, text=True, check=True,
).stdout

assert 'GLOSSARY' in raw, 'GLOSSARY heading not found on pdf p.293+'

entries = []
current = None
for line in raw.splitlines():
    line = line.strip()
    # skip blanks, headings, running heads, page numbers, form feeds
    if not line or line in ('GLOSSARY', 'Glossary') or re.fullmatch(r'[0-9]+', line):
        continue
    m = re.match(r'^(.{1,60}?)\s*—\s*(.+)$', line)
    if m:
        if current:
            entries.append(current)
        current = {'term': m.group(1).strip(), 'definition': m.group(2).strip()}
    elif current:
        # wrapped definition line (e.g. "sandek" continues onto a 2nd line)
        current['definition'] += ' ' + line
if current:
    entries.append(current)

assert 60 <= len(entries) <= 90, f'unexpected entry count: {len(entries)}'
assert all(e['term'] and e['definition'] for e in entries)

with open('src/content/glossary.json', 'w', encoding='utf-8') as f:
    json.dump({'entries': entries}, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'wrote {len(entries)} entries')
