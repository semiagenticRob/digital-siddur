#!/usr/bin/env python3
"""
Fix script for appendices-0 audit batch.
Applies findings from /tmp/fix2/appendices-0.json to src/content/appendices.json.

The appendices.json structure is:
  { "appendices": [ { "number": N, "title": "...", "segments": [...] }, ... ] }

Segment IDs like "a3-prayer-1" correspond to appendix number 3.
"""
import json
import sys
import copy

CONTENT_FILE = "src/content/appendices.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def find_appendix(data, number):
    """Find appendix by number (int)."""
    for ap in data["appendices"]:
        if ap.get("number") == number:
            return ap
    raise KeyError(f"Appendix number not found: {number}")

def find_segment(appendix, segment_id):
    for seg in appendix.get("segments", []):
        if seg.get("id") == segment_id:
            return seg
    raise KeyError(f"Segment not found: {segment_id} in appendix {appendix.get('number')}")

def find_segment_index(appendix, segment_id):
    for i, seg in enumerate(appendix.get("segments", [])):
        if seg.get("id") == segment_id:
            return i
    raise KeyError(f"Segment not found: {segment_id} in appendix {appendix.get('number')}")

def main():
    data = load_json(CONTENT_FILE)

    # -------------------------------------------------------------------------
    # Finding 1 (check=3): appendix-3 / a3-prayer-1
    # Convert type=prayer to type=commentary, remove heText, fix enText with
    # bold Hebrew lemmas per rendering contract.
    # -------------------------------------------------------------------------
    ap3 = find_appendix(data, 3)
    seg = find_segment(ap3, "a3-prayer-1")
    assert seg["type"] == "prayer", f"Expected prayer, got {seg['type']}"
    seg["type"] = "commentary"
    seg["heText"] = ""
    seg["enText"] = (
        "**מודה אני**—*Thank You, Hashem, for giving my neshamah back to me* "
        "(which was a merciful thing to do, since I have not yet lived up to my "
        "full potential, and therefore may not really deserve that); "
        "**רבה אמונתך**—*Your belief in me is very great!* "
        "(You believe I am important; my struggles are important; and You believe "
        "I can climb up to the next rung—that is why You woke me up. Thank You!)"
    )
    print("APPLIED: a3-prayer-1 — converted prayer→commentary, removed heText, added bold lemmas to enText")

    # -------------------------------------------------------------------------
    # Finding 2 (check=1): appendix-3 / a3-header-1
    # Add a preceding header segment a3-header-0 with enText='APPENDIX 3'
    # -------------------------------------------------------------------------
    ap3 = find_appendix(data, 3)
    idx_header1 = find_segment_index(ap3, "a3-header-1")
    # Only insert if a3-header-0 doesn't already exist
    existing_ids = [s["id"] for s in ap3["segments"]]
    if "a3-header-0" not in existing_ids:
        new_header = {
            "id": "a3-header-0",
            "type": "header",
            "heText": "",
            "enText": "APPENDIX 3"
        }
        ap3["segments"].insert(idx_header1, new_header)
        print("APPLIED: a3-header-0 — inserted new APPENDIX 3 header before a3-header-1")
    else:
        print("SKIP (already exists): a3-header-0")

    # -------------------------------------------------------------------------
    # Finding 3 (check=3): appendix-4 / a4-p1
    # Change 'three million people' to 'three million Jews'
    # -------------------------------------------------------------------------
    ap4 = find_appendix(data, 4)
    seg = find_segment(ap4, "a4-p1")
    assert "three million people" in seg["enText"], "Expected 'three million people' in a4-p1"
    seg["enText"] = seg["enText"].replace("three million people", "three million Jews", 1)
    print("APPLIED: a4-p1 — 'three million people' → 'three million Jews'")

    # -------------------------------------------------------------------------
    # Finding 4 (check=3): appendix-8 / a8-p1
    # Replace the Mishnah gloss with PDF text: 'Everything you do should be for
    # the sake of Heaven.'
    # -------------------------------------------------------------------------
    ap8 = find_appendix(data, 8)
    seg = find_segment(ap8, "a8-p1")
    old_gloss = (
        "—Everything you do or say, everything we buy, and how we spend every "
        "minute of the day should all be based on what will maximize our "
        "*avodas Hashem*."
    )
    new_gloss = "—Everything you do should be for the sake of Heaven."
    assert old_gloss in seg["enText"], f"Expected old gloss in a8-p1 enText. Got:\n{seg['enText']}"
    seg["enText"] = seg["enText"].replace(old_gloss, new_gloss, 1)
    print("APPLIED: a8-p1 — replaced expanded Mishnah gloss with PDF text")

    # -------------------------------------------------------------------------
    # Finding 5 (check=2): appendix-12 / a12-c3
    # Correct Hebrew phrase: 'הקדוש הא-ל' → 'הא-ל הקדוש'
    # This is inline Hebrew within English enText — no nikud so direct replacement.
    # -------------------------------------------------------------------------
    ap12 = find_appendix(data, 12)
    seg = find_segment(ap12, "a12-c3")
    assert "הקדוש הא-ל" in seg["enText"], "Expected 'הקדוש הא-ל' in a12-c3"
    seg["enText"] = seg["enText"].replace("הקדוש הא-ל", "הא-ל הקדוש", 1)
    print("APPLIED: a12-c3 — corrected Hebrew word order 'הקדוש הא-ל' → 'הא-ל הקדוש'")

    # -------------------------------------------------------------------------
    # Finding 6 (check=2): appendix-12 / a12-rubric-7
    # Fix first line of heText: 'וְתֵן טַל וּמָטָר/' → 'וְתֵן בְּרָכָה/'
    # Hebrew source: extract וְתֵן and בְּרָכָה from shacharit brachah text.
    # -------------------------------------------------------------------------
    ap12 = find_appendix(data, 12)
    seg = find_segment(ap12, "a12-rubric-7")
    current_he = seg.get("heText", "")
    assert current_he.startswith("וְתֵן טַל וּמָטָר/"), (
        f"Expected first line 'וְתֵן טַל וּמָטָר/' in a12-rubric-7, got: {current_he[:50]}"
    )
    # Verify source exists in maariv.json for the nikud of בְּרָכָה and וְתֵן
    # Both appear in maariv brachah text: "וְתֵן (בקיץ: בְּרָכָה)"
    with open("src/content/maariv.json", "r", encoding="utf-8") as _f:
        maariv_raw = _f.read()
    assert "בְּרָכָה" in maariv_raw, "Could not find source for בְּרָכָה nikud in maariv.json"
    assert "וְתֵן" in maariv_raw, "Could not find source for וְתֵן nikud in maariv.json"
    # compose the corrected first line
    corrected_he = current_he.replace("וְתֵן טַל וּמָטָר/", "וְתֵן בְּרָכָה/", 1)
    seg["heText"] = corrected_he
    print("APPLIED: a12-rubric-7 — corrected first line from 'וְתֵן טַל וּמָטָר/' to 'וְתֵן בְּרָכָה/'")

    # -------------------------------------------------------------------------
    # Finding 7 (check=3): appendix-12 / a12-c11
    # Fix inline Hebrew: 'ומטר instead of טל ברכה' → 'ותן טל ומטר instead of ותן ברכה'
    # -------------------------------------------------------------------------
    ap12 = find_appendix(data, 12)
    seg = find_segment(ap12, "a12-c11")
    en = seg["enText"]
    assert "ומטר instead of טל ברכה" in en, (
        f"Expected pattern 'ומטר instead of טל ברכה' in a12-c11. Got:\n{en}"
    )
    en = en.replace("ומטר instead of טל ברכה", "ותן טל ומטר instead of ותן ברכה", 1)
    seg["enText"] = en
    print("APPLIED: a12-c11 — corrected truncated Hebrew phrases")

    # -------------------------------------------------------------------------
    # Finding 8 (check=5): appendix-12 / a12-c24
    # Move a12-c24 to before a12-rubric-14 (currently placed after it at index [40])
    # -------------------------------------------------------------------------
    ap12 = find_appendix(data, 12)
    segs = ap12["segments"]
    idx_c24 = find_segment_index(ap12, "a12-c24")
    idx_rubric14 = find_segment_index(ap12, "a12-rubric-14")
    assert idx_c24 > idx_rubric14, (
        f"a12-c24 (idx={idx_c24}) should be after a12-rubric-14 (idx={idx_rubric14})"
    )
    # Remove a12-c24 from current position and insert before a12-rubric-14
    seg_c24 = segs.pop(idx_c24)
    # After pop, rubric-14 index is unchanged (c24 was after it)
    idx_rubric14_after = find_segment_index(ap12, "a12-rubric-14")
    segs.insert(idx_rubric14_after, seg_c24)
    print("APPLIED: a12-c24 — moved before a12-rubric-14 to match PDF section order")

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------
    save_json(CONTENT_FILE, data)
    print(f"\nSaved {CONTENT_FILE}")

    # Strip-diff verify: confirm key changes are present
    verify_data = load_json(CONTENT_FILE)

    ap3v = find_appendix(verify_data, 3)
    seg_prayer1 = find_segment(ap3v, "a3-prayer-1")
    assert seg_prayer1["type"] == "commentary", "VERIFY FAIL: a3-prayer-1 type"
    assert "**מודה אני**" in seg_prayer1["enText"], "VERIFY FAIL: a3-prayer-1 enText lemma"
    assert find_segment_index(ap3v, "a3-header-0") < find_segment_index(ap3v, "a3-header-1"), \
        "VERIFY FAIL: a3-header-0 position"

    ap4v = find_appendix(verify_data, 4)
    seg_a4p1 = find_segment(ap4v, "a4-p1")
    assert "three million Jews" in seg_a4p1["enText"], "VERIFY FAIL: a4-p1"
    assert "three million people" not in seg_a4p1["enText"], "VERIFY FAIL: a4-p1 old text remains"

    ap8v = find_appendix(verify_data, 8)
    seg_a8p1 = find_segment(ap8v, "a8-p1")
    assert "Everything you do should be for the sake of Heaven." in seg_a8p1["enText"], "VERIFY FAIL: a8-p1"
    assert "everything we buy" not in seg_a8p1["enText"], "VERIFY FAIL: a8-p1 old text remains"

    ap12v = find_appendix(verify_data, 12)
    seg_c3 = find_segment(ap12v, "a12-c3")
    assert "הא-ל הקדוש" in seg_c3["enText"], "VERIFY FAIL: a12-c3"
    assert "הקדוש הא-ל" not in seg_c3["enText"], "VERIFY FAIL: a12-c3 old order remains"

    seg_r7 = find_segment(ap12v, "a12-rubric-7")
    assert seg_r7["heText"].startswith("וְתֵן בְּרָכָה/"), "VERIFY FAIL: a12-rubric-7 first line"

    seg_c11 = find_segment(ap12v, "a12-c11")
    assert "ותן טל ומטר" in seg_c11["enText"], "VERIFY FAIL: a12-c11 ותן טל ומטר"
    assert "ותן ברכה" in seg_c11["enText"], "VERIFY FAIL: a12-c11 ותן ברכה"

    # a12-c24 should now be before a12-rubric-14
    idx_c24_final = find_segment_index(ap12v, "a12-c24")
    idx_r14_final = find_segment_index(ap12v, "a12-rubric-14")
    assert idx_c24_final < idx_r14_final, "VERIFY FAIL: a12-c24 not before a12-rubric-14"

    print("\nAll verifications passed.")

if __name__ == "__main__":
    main()
