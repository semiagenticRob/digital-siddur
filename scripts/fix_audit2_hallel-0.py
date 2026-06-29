#!/usr/bin/env python3
"""
fix_audit2_hallel-0.py

Apply audit2 batch hallel-0 content fixes to src/content/hallel.json.

Fix applied:
  - check 3: tehillim-114-gloss — replace bold lemma **אֲרֹן חוּלִי אָרֶץ**
    with **אָדוֹן חוּלִי אָרֶץ** (sliced from tehillim-114-text which already
    contains the correct nikud).
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
CONTENT_FILE = REPO / "src" / "content" / "hallel.json"

def main():
    data = json.loads(CONTENT_FILE.read_text(encoding="utf-8"))

    # Locate the prayer (structure: data -> groups[] -> prayers[])
    prayer = None
    for group in data.get("groups", []):
        for p in group.get("prayers", []):
            if p.get("id") == "p-hallel":
                prayer = p
                break
        if prayer is not None:
            break
    assert prayer is not None, "Prayer p-hallel not found"

    segments = prayer.get("segments", [])

    # --- Fix check 3: tehillim-114-gloss bold lemma ---
    gloss = next((s for s in segments if s.get("id") == "tehillim-114-gloss"), None)
    assert gloss is not None, "Segment tehillim-114-gloss not found"

    old_lemma = "**אֲרֹן חוּלִי אָרֶץ**"
    new_lemma = "**אָדוֹן חוּלִי אָרֶץ**"

    en_text = gloss.get("enText", "")
    assert old_lemma in en_text, f"Expected lemma not found in tehillim-114-gloss enText.\nActual: {en_text!r}"

    gloss["enText"] = en_text.replace(old_lemma, new_lemma, 1)

    # Verify the fix
    assert new_lemma in gloss["enText"], "Fix was not applied correctly"
    assert old_lemma not in gloss["enText"], "Old lemma still present after fix"

    # Write output
    CONTENT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print("Done. Fixed tehillim-114-gloss bold lemma: אֲרֹן → אָדוֹן")

if __name__ == "__main__":
    main()
