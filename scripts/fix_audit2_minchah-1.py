"""
fix_audit2_minchah-1.py
Batch: minchah-1

All findings in /tmp/fix2/minchah-1.json were confirmed as false positives:
the content was already corrected in a prior pass before this audit run.

This script asserts each target segment exists and that the content already
matches the PDF evidence, then exits cleanly with no changes.
"""
import json
import sys

CONTENT_PATH = "src/content/minchah.json"

def load():
    with open(CONTENT_PATH, encoding="utf-8") as f:
        return json.load(f)

def find_seg(data, seg_id):
    for group in data.get("groups", []):
        for prayer in group.get("prayers", []):
            for seg in prayer.get("segments", []):
                if seg.get("id") == seg_id:
                    return seg
    return None

def find_prayer(data, prayer_id):
    for group in data.get("groups", []):
        for prayer in group.get("prayers", []):
            if prayer.get("id") == prayer_id:
                return prayer
    return None

data = load()

# --- Confirm all findings are already correct ---

# Finding 1: min1-intro-1 check 6 — "there also was one" (already correct)
seg = find_seg(data, "min1-intro-1")
assert seg is not None, "min1-intro-1 not found"
assert "there also was one in the morning" in seg["enText"], \
    "min1-intro-1: expected 'there also was one in the morning'"

# Finding 2: min1-commentary-veezuz check 3 — correct Hebrew lemma (already correct)
seg = find_seg(data, "min1-commentary-veezuz")
assert seg is not None, "min1-commentary-veezuz not found"
assert "וּגְדֻלָּתְךָ" in seg["enText"], \
    "min1-commentary-veezuz: expected וּגְדֻלָּתְךָ (with qubuts, no extra vav)"
assert "וּגְדוּלָּתְךָ" not in seg["enText"], \
    "min1-commentary-veezuz: unexpected extra-vav form still present"

# Finding 3: min1-insight-malchuscha check 3 — "rather He is" and "simply" (already correct)
seg = find_seg(data, "min1-insight-malchuscha")
assert seg is not None, "min1-insight-malchuscha not found"
assert 'rather He is "סוֹמֵךְ"' in seg["enText"], \
    "min1-insight-malchuscha: expected 'rather He is סוֹמֵךְ'"
assert "simply pick us up" in seg["enText"], \
    "min1-insight-malchuscha: expected 'simply pick us up'"

# Findings 4,5,6: p-avinu-malkeinu-minchah header, intro, chatanu (already present)
prayer = find_prayer(data, "p-avinu-malkeinu-minchah")
assert prayer is not None, "p-avinu-malkeinu-minchah not found"
seg_ids = {s["id"] for s in prayer.get("segments", [])}
assert "am-header-en" in seg_ids, "am-header-en missing"
assert "am-header-he" in seg_ids, "am-header-he missing"
assert "am-intro-1" in seg_ids, "am-intro-1 missing"
assert "am-intro-2" in seg_ids, "am-intro-2 missing"
assert "am-chatanu-he" in seg_ids, "am-chatanu-he missing"
assert "am-chatanu-en" in seg_ids, "am-chatanu-en missing"

# Finding 7: am-15-en check 3 — "complete recovery" (already correct)
seg = find_seg(data, "am-15-en")
assert seg is not None, "am-15-en not found"
assert "complete recovery" in seg["enText"], "am-15-en: expected 'complete recovery'"
assert "completely recovery" not in seg["enText"], "am-15-en: erroneous 'completely' still present"

# Findings 8,9,10: tach bold lemmas (already correct)
for sid, lemma in [
    ("tach-2-en", "רַחוּם וְחַנּוּן חָטָאתִי לְפָנֶיךָ"),
    ("tach-4-en", "שׁוֹמֵר גּוֹי אֶחָד"),
    ("tach-6-en", "מִתְרַצֶּה בְּרַחֲמִים"),
]:
    seg = find_seg(data, sid)
    assert seg is not None, f"{sid} not found"
    assert lemma in seg["enText"], f"{sid}: bold lemma '{lemma}' not found"

# Finding 11: tach-kaddish-en1 check 3 — missing phrase (already present)
seg = find_seg(data, "tach-kaddish-en1")
assert seg is not None, "tach-kaddish-en1 not found"
assert "which Hashem created precisely according to His Will" in seg["enText"], \
    "tach-kaddish-en1: missing phrase still absent"

# Finding 12: min6-kaddish-4 check 2 — opening paren (already correct)
seg = find_seg(data, "min6-kaddish-4")
assert seg is not None, "min6-kaddish-4 not found"
assert "(בעש" in seg["heText"], \
    "min6-kaddish-4: opening paren before בעש\"ת missing"

print("All 12 assertions passed. No changes needed — all findings were already corrected.")
print(f"File unchanged: {CONTENT_PATH}")
