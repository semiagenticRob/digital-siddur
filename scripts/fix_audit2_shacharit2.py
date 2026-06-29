#!/usr/bin/env python3
"""Fix audit batch shacharit-2 findings against src/content/shacharit.json."""
import json
import sys
import copy

INPUT = "src/content/shacharit.json"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

# ---- helpers ----------------------------------------------------------------

def find_prayer(data, prayer_id):
    """Return the prayer dict (from any group) with id==prayer_id."""
    for group in data.get("groups", []):
        for prayer in group.get("prayers", []):
            if prayer.get("id") == prayer_id:
                return prayer
    raise KeyError(f"Prayer not found: {prayer_id}")


def find_seg_index(prayer, seg_id):
    """Return the 0-based index of segment with id==seg_id."""
    for i, seg in enumerate(prayer.get("segments", [])):
        if seg.get("id") == seg_id:
            return i
    raise KeyError(f"Segment not found: {seg_id} in prayer {prayer.get('id')}")


# ---- Fix 1: check-2 — mah_yakar heText missing vav -------------------------
# pdfEvidence: יִרְוְיוּן  appState: יִרְוְיֻן
prayer = find_prayer(data, "p-atifas-tallis")
idx = find_seg_index(prayer, "mah_yakar")
seg = prayer["segments"][idx]
old_he = seg["heText"]
assert "יִרְוְיֻן" in old_he, f"Expected יִרְוְיֻן in mah_yakar heText, got: {old_he[:60]}"
seg["heText"] = old_he.replace("יִרְוְיֻן", "יִרְוְיוּן", 1)
print("Fix 1 applied: mah_yakar יִרְוְיֻן → יִרְוְיוּן")

# ---- Fix 2: check-4 — add rubric לר"ח before uvroshei_chodsheichem --------
prayer = find_prayer(data, "p-korbanos")
idx = find_seg_index(prayer, "uvroshei_chodsheichem")
# Insert rubric immediately before uvroshei_chodsheichem
new_rubric = {
    "id": "rubric_rosh_chodesh_uvroshei",
    "type": "rubric",
    "condition": "rosh_chodesh",
    "heText": "לר\"ח"
}
prayer["segments"].insert(idx, new_rubric)
print("Fix 2 applied: inserted rubric לר\"ח before uvroshei_chodsheichem")

# ---- Fix 3: check-2 — se3-prayer-modim שֶׁבְּכָליוֹם → שֶׁבְּכָל יוֹם -----
prayer = find_prayer(data, "p-shemoneh-esrei")
idx = find_seg_index(prayer, "se3-prayer-modim")
seg = prayer["segments"][idx]
old_he = seg["heText"]
assert "שֶׁבְּכָליוֹם" in old_he, f"Expected שֶׁבְּכָליוֹם in se3-prayer-modim, got: {old_he[:60]}"
seg["heText"] = old_he.replace("שֶׁבְּכָליוֹם", "שֶׁבְּכָל יוֹם", 1)
print("Fix 3 applied: se3-prayer-modim שֶׁבְּכָליוֹם → שֶׁבְּכָל יוֹם")

# ---- Fix 4: check-5 reconcile — insert סְתֹם פִּיּוֹת after avinu_malkeinu_8
# Hebrew sliced from minchah am-8-he; commentary from am-8-en
# NOTE: pdfEvidence shows מְקַטְרִיגֵינוּ (with extra yod) vs minchah מְקַטְרִיגֵנוּ.
# The PDF evidence is authoritative; however per rules we SLICE from existing JSON.
# minchah has: אָבִינוּ מַלְכֵּנוּ סְתֹם פִּיּוֹת מַשְׂטִינֵינוּ וּמְקַטְרִיגֵנוּ:
# PDF evidence: אָבִינוּ מַלְכֵּנוּ סְתֹם פִּיּוֹת מַשְׂטִינֵינוּ וּמְקַטְרִיגֵינוּ
# We must use the sliced Hebrew from minchah (closest available source).
# Also insert כַּלֵּה דֶּבֶר (am-9-he) between new stom seg and avinu_malkeinu_9.
prayer = find_prayer(data, "avinu_malkeinu")
segs = prayer["segments"]

# Insert after avinu_malkeinu_8 (and its commentary avinu_malkeinu_commentary_8)
# Currently: [...avinu_malkeinu_8, avinu_malkeinu_commentary_8, avinu_malkeinu_9, ...]
# Target:    [...avinu_malkeinu_8, avinu_malkeinu_commentary_8,
#                NEW prayer stom, NEW commentary stom,
#                NEW prayer kalle_dever, NEW commentary kalle_dever,
#                avinu_malkeinu_9, ...]
idx_8_comm = find_seg_index(prayer, "avinu_malkeinu_commentary_8")
insert_at = idx_8_comm + 1  # right after commentary_8

stom_prayer = {
    "id": "avinu_malkeinu_8b",
    "type": "prayer",
    "heText": "אָבִינוּ מַלְכֵּנוּ סְתֹם פִּיּוֹת מַשְׂטִינֵינוּ וּמְקַטְרִיגֵנוּ:"
}
stom_commentary = {
    "id": "avinu_malkeinu_commentary_8b",
    "type": "commentary",
    "enText": "Our Father, our King, close up the mouths of our adversaries and accusers."
}
# כַּלֵּה דֶּבֶר — sliced from minchah am-9-he
kalle_prayer = {
    "id": "avinu_malkeinu_8c",
    "type": "prayer",
    "heText": "אָבִינוּ מַלְכֵּנוּ כַּלֵּה דֶּבֶר וְחֶרֶב וְרָעָב וּשְׁבִי וּמַשְׁחִית וְעָוֹן וּשְׁמַד מִבְּנֵי בְרִיתֶךָ:"
}
kalle_commentary = {
    "id": "avinu_malkeinu_commentary_8c",
    "type": "commentary",
    "enText": "Our Father, our King, get rid of all diseases, wars, hunger, captivity, destruction, evildoing, and negative spiritual influences from Your nation."
}

# Insert in reverse order so indices stay valid
segs.insert(insert_at, kalle_commentary)
segs.insert(insert_at, kalle_prayer)
segs.insert(insert_at, stom_commentary)
segs.insert(insert_at, stom_prayer)

print("Fix 4 applied: inserted avinu_malkeinu_8b (stom piyot) and avinu_malkeinu_8c (kalle dever) after commentary_8")

# ---- Fix 5: check-5 reconcile — rename tach1-s1..s4 → avinu_malkeinu_36..37
prayer = find_prayer(data, "avinu_malkeinu")
renames = {
    "tach1-s1": "avinu_malkeinu_36",
    "tach1-s2": "avinu_malkeinu_commentary_36",
    "tach1-s3": "avinu_malkeinu_37",
    "tach1-s4": "avinu_malkeinu_commentary_37",
}
for old_id, new_id in renames.items():
    idx = find_seg_index(prayer, old_id)
    prayer["segments"][idx]["id"] = new_id
    print(f"Fix 5 applied: renamed {old_id} → {new_id}")

# ---- Fix 6: check-3 — pitum_kdr_comm_4 enText canonical form ---------------
prayer = find_prayer(data, "p-pitum-haketores")
idx = find_seg_index(prayer, "pitum_kdr_comm_4")
seg = prayer["segments"][idx]
# Canonical from kaddish-drab-9 (already verified in shacharit.json)
seg["enText"] = (
    "**עַל יִשְׂרָאֵל וְעַל רַבָּנָן**—(The person saying Kaddish requests:) "
    "May there be abundant peace, mercy, kindness, long life, and material abundance"
    "—from our Father in Heaven—upon all of Bnei Yisrael, and specifically upon our "
    "teachers, their students, and all who study Torah—here and everywhere! "
    "And to that we respond: **אָמֵן**—Absolutely, we agree!"
)
print("Fix 6 applied: pitum_kdr_comm_4 enText → canonical kaddish-drab-9 form")

# ---- Fix 7: check-2 — pitum_kdr_6 heText insert AYT variant ----------------
prayer = find_prayer(data, "p-pitum-haketores")
idx = find_seg_index(prayer, "pitum_kdr_6")
seg = prayer["segments"][idx]
old_he = seg["heText"]
assert "עֹשֶׂה שָׁלוֹם בִּמְרוֹמָיו" in old_he, f"Unexpected heText in pitum_kdr_6: {old_he[:60]}"
# Insert AYT variant: עֹשֶׂה שָׁלוֹם (בעשי"ת הַשָּׁלוֹם) בִּמְרוֹמָיו
seg["heText"] = old_he.replace(
    "עֹשֶׂה שָׁלוֹם בִּמְרוֹמָיו",
    'עֹשֶׂה שָׁלוֹם (בעשי"ת הַשָּׁלוֹם) בִּמְרוֹמָיו',
    1
)
print("Fix 7 applied: pitum_kdr_6 inserted AYT variant")

# ---- Fix 8: check-4 — aleinu_kaddish_comm_3 rubric text 'then says' → 'then points out that'
prayer = find_prayer(data, "p-aleinu")
idx = find_seg_index(prayer, "aleinu_kaddish_comm_3")
seg = prayer["segments"][idx]
old_en = seg["enText"]
assert "then says:" in old_en, f"Expected 'then says:' in aleinu_kaddish_comm_3, got: {old_en[:80]}"
seg["enText"] = old_en.replace("then says:", "then points out that", 1)
print("Fix 8 applied: aleinu_kaddish_comm_3 'then says:' → 'then points out that'")

# ---- Write output -----------------------------------------------------------
with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")

print("\nDone. All fixes applied to", INPUT)
