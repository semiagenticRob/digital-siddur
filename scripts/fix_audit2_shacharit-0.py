#!/usr/bin/env python3
"""
fix_audit2_shacharit-0.py
Apply audit2 findings for shacharit-0 batch to src/content/shacharit.json.
Findings: checks 1,2,3,4,5,6 across multiple prayers.
"""
import json
import sys
import re

FILE = "src/content/shacharit.json"

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


def find_prayer(prayer_id):
    for group in data.get("groups", []):
        for prayer in group.get("prayers", []):
            if prayer.get("id") == prayer_id:
                return prayer
    return None


def find_segment(segments, seg_id):
    for seg in segments:
        if seg.get("id") == seg_id:
            return seg
    return None


def segment_index(segments, seg_id):
    for i, seg in enumerate(segments):
        if seg.get("id") == seg_id:
            return i
    return -1


# ── CHECK 2: p-netilas-yadayim / asher-yatzar-bracha ─────────────────────────
# Fix: לְהִתְקַיֵּם → לְהִתְקַיֵּים  and  [אֲפִלּוּ → [אֲפִילּוּ
prayer = find_prayer("p-netilas-yadayim")
assert prayer is not None, "p-netilas-yadayim not found"
segs = prayer["segments"]
seg = find_segment(segs, "asher-yatzar-bracha")
assert seg is not None, "asher-yatzar-bracha not found"

old_he = seg["heText"]
# Fix לְהִתְקַיֵּם (missing yod) → לְהִתְקַיֵּים
# and [אֲפִלּוּ (missing yod) → [אֲפִילּוּ
new_he = old_he.replace("לְהִתְקַיֵּם", "לְהִתְקַיֵּים")
new_he = new_he.replace("[אֲפִלּוּ", "[אֲפִילּוּ")
assert new_he != old_he, "CHECK 2: no change made to asher-yatzar-bracha"
assert "לְהִתְקַיֵּים" in new_he, "CHECK 2: יים not present after fix"
assert "[אֲפִילּוּ" in new_he, "CHECK 2: אפילו fix not present"
seg["heText"] = new_he
print("✓ CHECK 2: asher-yatzar-bracha heText fixed (להתקיים + אפילו)")


# ── CHECK 3a: p-birchos-hashachar / bracha-matir-asurim-commentary ────────────
# Fix: 'by waking us up' → 'by You waking us up'
prayer = find_prayer("p-birchos-hashachar")
assert prayer is not None, "p-birchos-hashachar not found"
segs = prayer["segments"]
seg = find_segment(segs, "bracha-matir-asurim-commentary")
assert seg is not None, "bracha-matir-asurim-commentary not found"

old_en = seg["enText"]
assert "by waking us up" in old_en, "CHECK 3a: 'by waking us up' not found"
new_en = old_en.replace("by waking us up", "by You waking us up", 1)
assert new_en != old_en, "CHECK 3a: no change made"
seg["enText"] = new_en
print("✓ CHECK 3a: bracha-matir-asurim-commentary enText fixed ('by You waking us up')")


# ── CHECK 1: p-pesukei-dzimrah / pz1-header-1 ────────────────────────────────
# Fix EN: 'Pesukei DZimrah' → "Pesukei D'Zimrah"
prayer = find_prayer("p-pesukei-dzimrah")
assert prayer is not None, "p-pesukei-dzimrah not found"
segs = prayer["segments"]
seg = find_segment(segs, "pz1-header-1")
assert seg is not None, "pz1-header-1 not found"

old_en = seg["enText"]
assert "Pesukei DZimrah" in old_en, "CHECK 1: 'Pesukei DZimrah' not found in pz1-header-1"
new_en = old_en.replace("Pesukei DZimrah", "Pesukei D'Zimrah", 1)
assert new_en != old_en, "CHECK 1: no change made"
seg["enText"] = new_en
print("✓ CHECK 1: pz1-header-1 EN fixed (Pesukei D'Zimrah)")


# ── CHECK 3b: p-vidui / vidui-9 ──────────────────────────────────────────────
# Replace commentary enText with PDF-faithful version
prayer = find_prayer("p-vidui")
assert prayer is not None, "p-vidui not found"
segs = prayer["segments"]
seg = find_segment(segs, "vidui-9")
assert seg is not None, "vidui-9 not found"

new_vidui_en = (
    "**אֵל אֶרֶךְ אַפַּיִם**—You are slow to anger and full of compassion "
    "*(and thus we ask for time to get back on track)*. "
    "Please show us compassion and listen to our requests "
    "*(for help in returning to You and living up to our true potential)*. "
    "You Yourself taught Moshe that we should proclaim Your thirteen attributes of mercy "
    "*(יג מדות הרחמים)*, "
    "and You will listen to our requests, forgive our mistakes, and give us another chance, "
    "as it says in the Torah."
)
old_en = seg["enText"]
assert old_en != new_vidui_en, "CHECK 3b: vidui-9 already matches — nothing to do"
seg["enText"] = new_vidui_en
print("✓ CHECK 3b: vidui-9 commentary replaced with full PDF text")


# ── CHECK 5: avinu_malkeinu — insert 2 missing lines after avinu_malkeinu_8 ───
# PDF order: avinu_malkeinu_8 → [stom] → [kaleh dever] → avinu_malkeinu_9 (מנע מגפה)
# Hebrew sliced from minchah.json (am-8-he and am-9-he)
prayer = find_prayer("avinu_malkeinu")
assert prayer is not None, "avinu_malkeinu not found"
segs = prayer["segments"]

# Confirm targets exist
assert segment_index(segs, "avinu_malkeinu_8") >= 0, "avinu_malkeinu_8 not found"
assert segment_index(segs, "avinu_malkeinu_commentary_8") >= 0, "avinu_malkeinu_commentary_8 not found"
assert segment_index(segs, "avinu_malkeinu_9") >= 0, "avinu_malkeinu_9 not found"

# Confirm the missing lines are NOT already present
assert segment_index(segs, "avinu_malkeinu_stom") < 0, "avinu_malkeinu_stom already exists"
assert segment_index(segs, "avinu_malkeinu_commentary_stom") < 0, "avinu_malkeinu_commentary_stom already exists"
assert segment_index(segs, "avinu_malkeinu_kaleh_dever") < 0, "avinu_malkeinu_kaleh_dever already exists"
assert segment_index(segs, "avinu_malkeinu_commentary_kaleh_dever") < 0, "avinu_malkeinu_commentary_kaleh_dever already exists"

# Insert after avinu_malkeinu_commentary_8 (which follows avinu_malkeinu_8)
insert_after_idx = segment_index(segs, "avinu_malkeinu_commentary_8")
assert insert_after_idx >= 0

# Two new prayer+commentary pairs to insert, in order:
# 1. סְתֹם פִּיּוֹת (sliced from minchah am-8-he)
# 2. כַּלֵּה דֶּבֶר (sliced from minchah am-9-he)
new_segments = [
    {
        "id": "avinu_malkeinu_stom",
        "type": "prayer",
        "heText": "אָבִינוּ מַלְכֵּנוּ סְתֹם פִּיּוֹת מַשְׂטִינֵינוּ וּמְקַטְרִיגֵנוּ:"
    },
    {
        "id": "avinu_malkeinu_commentary_stom",
        "type": "commentary",
        "enText": "Our Father, our King, close up the mouths of our adversaries and accusers."
    },
    {
        "id": "avinu_malkeinu_kaleh_dever",
        "type": "prayer",
        "heText": "אָבִינוּ מַלְכֵּנוּ כַּלֵּה דֶּבֶר וְחֶרֶב וְרָעָב וּשְׁבִי וּמַשְׁחִית וְעָוֹן וּשְׁמַד מִבְּנֵי בְרִיתֶךָ:"
    },
    {
        "id": "avinu_malkeinu_commentary_kaleh_dever",
        "type": "commentary",
        "enText": "Our Father, our King, get rid of all diseases, wars, hunger, captivity, destruction, evildoing, and negative spiritual influences from Your nation."
    }
]

# Splice in after insert_after_idx
segs[insert_after_idx + 1:insert_after_idx + 1] = new_segments
print("✓ CHECK 5: inserted avinu_malkeinu_stom + avinu_malkeinu_kaleh_dever (+ commentaries) after avinu_malkeinu_commentary_8")


# ── CHECK 3c: p-tachanun / tach2-s2 ──────────────────────────────────────────
# Fix: 'on Your nation' → 'on Your children'
prayer = find_prayer("p-tachanun")
assert prayer is not None, "p-tachanun not found"
segs = prayer["segments"]
seg = find_segment(segs, "tach2-s2")
assert seg is not None, "tach2-s2 not found"

old_en = seg["enText"]
assert "on Your nation" in old_en, "CHECK 3c: 'on Your nation' not found in tach2-s2"
new_en = old_en.replace("on Your nation", "on Your children", 1)
assert new_en != old_en, "CHECK 3c: no change made"
seg["enText"] = new_en
print("✓ CHECK 3c: tach2-s2 enText fixed ('on Your children')")


# ── CHECK 3d: p-pitum-haketores / pitum_kdr_comm_5 ───────────────────────────
# Fix: prepend bold lemma + fix 'a good life' → 'life' + fix 'Absolutely correct!' → 'Absolutely, we agree!'
prayer = find_prayer("p-pitum-haketores")
assert prayer is not None, "p-pitum-haketores not found"
segs = prayer["segments"]
seg = find_segment(segs, "pitum_kdr_comm_5")
assert seg is not None, "pitum_kdr_comm_5 not found"

new_kdr_en = (
    "**יְהֵא שְׁלָמָא רַבָּא**—*(The person saying Kaddish requests:)* "
    "May there be abundant peace, that comes from Heaven, and life, "
    "upon us and upon all of Bnei Yisrael! "
    "And to that we respond: **אָמֵן**—Absolutely, we agree!"
)
old_en = seg["enText"]
assert old_en != new_kdr_en, "CHECK 3d: pitum_kdr_comm_5 already matches"
seg["enText"] = new_kdr_en
print("✓ CHECK 3d: pitum_kdr_comm_5 enText fixed (added lemma, fixed 'life', fixed amen phrase)")


# ── CHECK 4: p-pitum-haketores / pitum_kdr_barchu_response ───────────────────
# Add a rubric segment with heText 'קהל וחזן' immediately before pitum_kdr_barchu_response
prayer = find_prayer("p-pitum-haketores")
segs = prayer["segments"]

barchu_resp_idx = segment_index(segs, "pitum_kdr_barchu_response")
assert barchu_resp_idx >= 0, "pitum_kdr_barchu_response not found"

# Check rubric not already there
rubric_id = "pitum_kdr_barchu_rubric"
assert segment_index(segs, rubric_id) < 0, f"{rubric_id} already exists"

new_rubric = {
    "id": rubric_id,
    "type": "rubric",
    "heText": "קהל וחזן:"
}
segs.insert(barchu_resp_idx, new_rubric)
print("✓ CHECK 4: inserted pitum_kdr_barchu_rubric (קהל וחזן) before pitum_kdr_barchu_response")


# ── CHECK 3e: p-shir-shel-yom / commentary_monday_cont ───────────────────────
# Delete commentary_monday_cont entirely (duplicate sentence)
prayer = find_prayer("p-shir-shel-yom")
assert prayer is not None, "p-shir-shel-yom not found"
segs = prayer["segments"]

cont_idx = segment_index(segs, "commentary_monday_cont")
assert cont_idx >= 0, "commentary_monday_cont not found"
removed = segs.pop(cont_idx)
assert removed.get("id") == "commentary_monday_cont"
print("✓ CHECK 3e: deleted commentary_monday_cont (duplicate closing sentence)")


# ── CHECK 6: p-shesh-zechiros / section_intro ────────────────────────────────
# The audit appState said the text reads "...Hashem spoke directly to us at Har Sinai, and gave us
# His Torah..." but the actual text in the JSON already reads "...Hashem spoke directly to us at
# Har Sinai, and Shabbos, which reminds us of Creation (and thus His providence)."
# The appState was incorrect — the section_intro does NOT contain "and gave us His Torah".
# That phrase lives in commentary_har_sinai (a different segment), which is fine as-is.
# The section_intro is already PDF-faithful for the Har Sinai clause.
# Therefore CHECK 6 is a FALSE POSITIVE — SKIPPED.
print("~ CHECK 6: SKIP — section_intro already correct; 'and gave us His Torah' is in commentary_har_sinai (correct), not section_intro (false positive appState in audit)")


# ── WRITE OUTPUT ──────────────────────────────────────────────────────────────
with open(FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"\n✓ Written: {FILE}")
