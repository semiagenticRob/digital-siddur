#!/usr/bin/env python3
"""Relocate the Uva Letzion tail (end of Maariv for Motzaei Shabbos) from
sefiras-haomer.json, where it was mis-filed because it shares print p.191 with
the Sefiras HaOmer header, back to the end of maariv-motzaei-shabbos.json.

The Hebrew prayer paragraph these commentaries annotate was dropped entirely in
digitization; restore it by slicing Shacharit's identical Uva Letzion segment
(kt3-uva-6), which carries the print-faithful cholam Divine Name. Verified
against print siddur p.191 (pdf p.215).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "src" / "content"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def dump(name, data):
    (ROOT / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def find_segment(obj, seg_id):
    if isinstance(obj, dict):
        if obj.get("id") == seg_id and "type" in obj:
            return obj
        for v in obj.values():
            r = find_segment(v, seg_id)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_segment(v, seg_id)
            if r:
                return r
    return None


sh = load("shacharit.json")
sef = load("sefiras-haomer.json")
ms = load("maariv-motzaei-shabbos.json")

# 1. Source the missing Hebrew by slicing Shacharit's Uva Letzion tail.
uva = find_segment(sh, "kt3-uva-6")
assert uva is not None, "kt3-uva-6 not found in shacharit.json"
he = uva["heText"]
assert he.startswith("בָּרוּךְ הוּא אֱלֹהֵינוּ שֶׁבְּרָאָנוּ"), "unexpected Uva tail head"
assert he.rstrip().endswith("יַגְדִּיל תּוֹרָה וְיַאְדִּיר:"), "unexpected Uva tail end"

# 2. Grab the three orphaned segments off the front of Sefiras HaOmer.
sef_segs = sef["groups"][0]["prayers"][0]["segments"]
assert [s["id"] for s in sef_segs[:3]] == ["seg-001", "seg-002", "seg-003"], \
    "sefiras front segments are not the expected orphaned trio"
comm_shebranu, comm_hagever, rubric = sef_segs[0], sef_segs[1], sef_segs[2]
assert comm_shebranu["enText"].startswith("**שֶׁבְּרָאָנוּ לִכְבוֹדוֹ**")
assert comm_hagever["enText"].startswith("**בָּרוּךְ הַגֶּבֶר**")
assert rubric["type"] == "rubric" and "Full-Kaddish and Aleinu" in rubric["enText"]

# 3. Build the relocated segments in print order (prayer -> 2 comms -> rubric),
#    matching this file's convention: comment/rubric carry only enText.
new_segments = [
    {"id": "seg-shebranu", "type": "prayer", "heText": he},
    {"id": "seg-shebranu-comm", "type": "commentary", "enText": comm_shebranu["enText"]},
    {"id": "seg-hagever-comm", "type": "commentary", "enText": comm_hagever["enText"]},
    {"id": "seg-full-kaddish-aleinu", "type": "rubric", "enText": rubric["enText"]},
]

ms_segs = ms["groups"][0]["prayers"][0]["segments"]
assert ms_segs[-1]["id"] == "seg-vatah-kadosh-comm3", "maariv-ms does not end where expected"
existing_ids = {s["id"] for s in ms_segs}
for s in new_segments:
    assert s["id"] not in existing_ids, f"id collision: {s['id']}"
ms_segs.extend(new_segments)

# 4. Drop the orphaned trio from Sefiras HaOmer.
del sef_segs[:3]
assert sef_segs[0]["id"] == "seg-004", "unexpected new head of sefiras segments"

dump("maariv-motzaei-shabbos.json", ms)
dump("sefiras-haomer.json", sef)
print("moved Uva Letzion tail; restored Hebrew paragraph (%d chars)" % len(he))
