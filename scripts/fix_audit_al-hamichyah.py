#!/usr/bin/env python3
"""
Fix audit findings for al-hamichyah.json.

Check 6 (s-am-intro, section_intro enText):
  PDF p.153 says: "Yes, even cake is a miracle! See Introduction to Birkas Ha'mazon above on 119."
  App has:        "Yes, even cake is a miracle! See the Introduction to Birkas Ha'mazon [here](section:bm-intro)."
  Fix:
    - Remove spurious "the" before "Introduction" (not in print)
    - Replace bare "[here]" link text with "[above on 119]" to match print wording
    - Keep the digital hyperlink target (section:bm-intro) — acceptable digital adaptation
"""
import json
import re

FILE = 'src/content/al-hamichyah.json'
TARGET_ID = 's-am-intro'

OLD_TEXT = "Yes, even cake is a miracle! See the Introduction to Birkas Ha'mazon [here](section:bm-intro)."
NEW_TEXT = "Yes, even cake is a miracle! See Introduction to Birkas Ha'mazon [above on 119](section:bm-intro)."

with open(FILE, encoding='utf-8') as f:
    data = json.load(f)

# Locate the segment and apply fix
found = False
for group in data['groups']:
    for prayer in group['prayers']:
        for seg in prayer['segments']:
            if seg.get('id') == TARGET_ID:
                assert seg.get('type') == 'section_intro', \
                    f"Expected type section_intro, got {seg.get('type')}"
                current = seg.get('enText', '')
                assert current == OLD_TEXT, \
                    f"Text mismatch on {TARGET_ID}!\n  EXPECTED: {OLD_TEXT!r}\n  FOUND:    {current!r}"
                seg['enText'] = NEW_TEXT
                found = True
                print(f"  Patched {TARGET_ID}")
                print(f"    OLD: {OLD_TEXT}")
                print(f"    NEW: {NEW_TEXT}")

assert found, f"Segment {TARGET_ID!r} not found in {FILE}"

# Strip-diff verification (strip markdown and check the change is intentional)
def strip_md(s):
    s = re.sub(r'\*\*.*?\*\*', '', s)
    s = re.sub(r'\*.*?\*', '', s)
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)
    return s.strip()

old_stripped = strip_md(OLD_TEXT)
new_stripped = strip_md(NEW_TEXT)
print(f"\n  Strip-diff (markdown/links removed):")
print(f"    OLD: {old_stripped}")
print(f"    NEW: {new_stripped}")
assert old_stripped != new_stripped, "Strip-diff: no change detected (bug in script)"
assert "Introduction to Birkas Ha'mazon" in new_stripped, "Core text preserved"
assert "above on 119" in new_stripped, "Link text updated to match print"
assert "the Introduction" not in new_stripped, "Spurious 'the' removed"
print("  Strip-diff OK: wording change is intentional and correct.")

with open(FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print('\nDone.')
