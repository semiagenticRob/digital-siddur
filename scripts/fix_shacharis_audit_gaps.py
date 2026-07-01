#!/usr/bin/env python3
"""Two print-verified Shacharis audit gaps (Feigenbaum siddur):

1. Barchi Nafshi (Tehillim 104) is missing its closing `קדיש יתום` rubric. The
   print (siddur p.110) prints it after the psalm's final הַלְלוּיָהּ, and every
   sibling daily-psalm (all six Shir shel Yom days) plus the adjacent L'Dovid
   carries one. Add a rubric, Hebrew SLICED from L'Dovid's rubric_kaddish.

2. Hashkamas HaBoker header omits the name-list subtitle the print prints under
   "I Woke Up!" (siddur p.2): מוֹדֶה אֲנִי / רֵאשִׁית חָכְמָה / תּוֹרָה צִוָּה — the three
   sub-passages of the section. Parallel sections store this (birchos-hatorah
   `header-torah-learning-hebrew`, tefillin `header_kadeish_li`). Add a header,
   each name SLICED from its own prayer segment (never retyped).
"""
import json, pathlib

PATH = pathlib.Path("src/content/shacharit.json")
data = json.loads(PATH.read_text(encoding="utf-8"))
prayers = {p["id"]: p for g in data["groups"] for p in g["prayers"]}


def seg(prayer_id, seg_id):
    for s in prayers[prayer_id]["segments"]:
        if s.get("id") == seg_id:
            return s
    raise AssertionError(f"{seg_id} not found in {prayer_id}")


def first_words(text, n):
    return " ".join(text.split()[:n])


# --- Fix 1: Barchi Nafshi closing Kaddish Yasom rubric ---
bn = prayers["p-barchi-nafshi"]["segments"]
assert bn[-1]["id"] == "barchi_nafshi_v33_35", "Barchi Nafshi tail moved"
assert bn[-1]["heText"].rstrip().endswith("הַֽלְלוּ־יָֽהּ׃"), "psalm end changed"
assert not any(s.get("id") == "barchi_nafshi_kaddish" for s in bn), "rubric already present"
kaddish_he = seg("p-ldovid-hashem-ori", "rubric_kaddish")["heText"]  # 'קדיש יתום'
bn.append({"id": "barchi_nafshi_kaddish", "type": "rubric", "heText": kaddish_he})

# --- Fix 2: Hashkamas HaBoker name-list subtitle header ---
ma = prayers["modeh_ani"]["segments"]
assert ma[0]["id"] == "modeh_ani_header_en", "modeh_ani header moved"
assert not any(s.get("id") == "modeh_ani_header_names" for s in ma), "names header present"
name1 = first_words(seg("modeh_ani", "modeh_ani_1")["heText"], 2)   # מוֹדֶה אֲנִי
name2 = first_words(seg("modeh_ani", "modeh_ani_2")["heText"], 2)   # רֵאשִׁית חָכְמָה
name3 = first_words(seg("modeh_ani", "modeh_ani_3")["heText"], 2)   # תּוֹרָה צִוָּה
assert name1 == "מוֹדֶה אֲנִי" and name2 == "רֵאשִׁית חָכְמָה" and name3 == "תּוֹרָה צִוָּה", \
    f"unexpected slices: {name1!r} {name2!r} {name3!r}"
names_he = f"{name1} / {name2} / {name3}"
ma.insert(1, {"id": "modeh_ani_header_names", "type": "header", "heText": names_he})

PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2).rstrip("\n"), encoding="utf-8")
print("Fix 1: added barchi_nafshi_kaddish rubric ->", repr(kaddish_he))
print("Fix 2: added modeh_ani_header_names header ->", repr(names_he))
