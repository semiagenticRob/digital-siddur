#!/usr/bin/env python3
"""
Fix script for shacharit-1 audit batch.
Applies findings from /tmp/fix2/shacharit-1.json to src/content/shacharit.json.
"""
import json
import sys
import copy

SHACHARIT_PATH = "src/content/shacharit.json"


def find_prayer(data, prayer_id):
    """Find a prayer by id anywhere in the nested structure."""
    for group in data.get("groups", []):
        for prayer in group.get("prayers", []):
            if prayer.get("id") == prayer_id:
                return prayer
    return None


def find_segment(prayer, segment_id):
    """Find a segment by id within a prayer."""
    for seg in prayer.get("segments", []):
        if seg.get("id") == segment_id:
            return seg
    return None


def find_segment_index(prayer, segment_id):
    """Return index of segment with given id, or -1."""
    for i, seg in enumerate(prayer.get("segments", [])):
        if seg.get("id") == segment_id:
            return i
    return -1


def load():
    with open(SHACHARIT_PATH, encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(SHACHARIT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    data = load()
    errors = []

    # ─── Fix 1: insight-bedrock-emunah (check 3) ───────────────────────────
    # Replace **שׁעֵרֵי** with **שֵׂכֶל** in p-birchos-hatorah / insight-bedrock-emunah
    prayer = find_prayer(data, "p-birchos-hatorah")
    assert prayer is not None, "p-birchos-hatorah not found"
    seg = find_segment(prayer, "insight-bedrock-emunah")
    assert seg is not None, "insight-bedrock-emunah not found"
    old_text = seg["enText"]
    assert "**שׁעֵרֵי**" in old_text, f"Expected **שׁעֵרֵי** not found in insight-bedrock-emunah. Got: {old_text[:100]}"
    seg["enText"] = old_text.replace("**שׁעֵרֵי**", "**שֵׂכֶל**", 1)
    print("FIX 1 applied: insight-bedrock-emunah — replaced שׁעֵרֵי with שֵׂכֶל")

    # ─── Fix 2: korb1-007 (check 6) ────────────────────────────────────────
    # Fix broken sentence fragment in enText of korb1-007
    prayer = find_prayer(data, "p-korbanos")
    assert prayer is not None, "p-korbanos not found"
    seg = find_segment(prayer, "korb1-007")
    assert seg is not None, "korb1-007 not found"
    old_text = seg["enText"]
    assert "which in the Beis Hamikdash with korbanos" in old_text, \
        f"Expected broken fragment not found in korb1-007. Got: {old_text}"
    seg["enText"] = old_text.replace(
        "which in the Beis Hamikdash with korbanos",
        "which was done in the Beis Hamikdash through korbanos"
    )
    print("FIX 2 applied: korb1-007 — fixed broken sentence fragment")

    # ─── Fix 3: pz1 pause rubric (check 4) ─────────────────────────────────
    # Add a standalone rubric segment between pz1-prayer-4 and pz1-commentary-4
    prayer = find_prayer(data, "p-pesukei-dzimrah")
    assert prayer is not None, "p-pesukei-dzimrah not found"
    idx_prayer4 = find_segment_index(prayer, "pz1-prayer-4")
    assert idx_prayer4 >= 0, "pz1-prayer-4 not found"
    # Check if rubric already exists
    existing_rubric = find_segment(prayer, "pz1-rubric-pause")
    if existing_rubric is None:
        rubric_seg = {
            "id": "pz1-rubric-pause",
            "type": "rubric",
            "heText": "(כאן צריך להפסיק מעט)",
            "enText": "Pause slightly here"
        }
        # Insert AFTER pz1-prayer-4
        prayer["segments"].insert(idx_prayer4 + 1, rubric_seg)
        print("FIX 3 applied: inserted pz1-rubric-pause rubric after pz1-prayer-4")
    else:
        print("FIX 3 skipped: pz1-rubric-pause already exists")

    # ─── Fix 4: avinu_malkeinu_commentary_2 (check 3) ──────────────────────
    prayer = find_prayer(data, "avinu_malkeinu")
    assert prayer is not None, "avinu_malkeinu not found"
    seg = find_segment(prayer, "avinu_malkeinu_commentary_2")
    assert seg is not None, "avinu_malkeinu_commentary_2 not found"
    old_text = seg["enText"]
    assert "(even though we may not be personally deserving, but please)" in old_text, \
        f"Expected parenthetical not found in avinu_malkeinu_commentary_2. Got: {old_text}"
    seg["enText"] = old_text.replace(
        "(even though we may not be personally deserving, but please)",
        "(even though we may have messed up, still we accept and publicly proclaim that)"
    )
    print("FIX 4 applied: avinu_malkeinu_commentary_2 — replaced parenthetical")

    # ─── Fix 5: avinu_malkeinu_commentary_30 (check 3) ─────────────────────
    seg = find_segment(prayer, "avinu_malkeinu_commentary_30")
    assert seg is not None, "avinu_malkeinu_commentary_30 not found"
    old_text = seg["enText"]
    expected_end = "for proclaiming the Oneness of Hashem."
    assert old_text.endswith(expected_end), \
        f"avinu_malkeinu_commentary_30 does not end as expected. Got: {old_text[-80:]}"
    seg["enText"] = old_text[:-len(expected_end)] + \
        "for proclaiming the Oneness of Hashem *(as expressed in the Shema)*."
    print("FIX 5 applied: avinu_malkeinu_commentary_30 — appended Shema parenthetical")

    # ─── Fix 6: tach2-s12 (check 3) ────────────────────────────────────────
    prayer = find_prayer(data, "p-tachanun")
    assert prayer is not None, "p-tachanun not found"
    seg = find_segment(prayer, "tach2-s12")
    assert seg is not None, "tach2-s12 not found"
    old_text = seg["enText"]
    assert "Bnei Yisrael) Hashem" in old_text, \
        f"Expected stray ')' not found in tach2-s12. Got: {old_text}"
    seg["enText"] = old_text.replace(
        "Bnei Yisrael) Hashem",
        "Bnei Yisrael, Hashem"
    )
    print("FIX 6 applied: tach2-s12 — removed stray closing parenthesis")

    # ─── Fix 7: pitum_kdr_comm_6 (check 3) ─────────────────────────────────
    # Prepend bold lemma and fix "Absolutely correct!" -> "Absolutely, we agree!"
    # The lemma to prepend: **עֹשֶׂה שָׁלוֹם (בעשי"ת הַשָּׁלוֹם) בִּמְרוֹמָיו**—
    # Slice Hebrew from pitum_kdr_6 heText: "עֹשֶׂה שָׁלוֹם (בעשי\"ת הַשָּׁלוֹם) בִּמְרוֹמָיו"
    prayer = find_prayer(data, "p-pitum-haketores")
    assert prayer is not None, "p-pitum-haketores not found"
    seg = find_segment(prayer, "pitum_kdr_comm_6")
    assert seg is not None, "pitum_kdr_comm_6 not found"

    # Get the Hebrew from the adjacent prayer segment for the lemma
    pitum_kdr_6 = find_segment(prayer, "pitum_kdr_6")
    assert pitum_kdr_6 is not None, "pitum_kdr_6 not found"
    he_prayer = pitum_kdr_6["heText"]
    # Slice the opening phrase: "עֹשֶׂה שָׁלוֹם (בעשי\"ת הַשָּׁלוֹם) בִּמְרוֹמָיו"
    # It appears before the comma in the prayer text
    comma_idx = he_prayer.index(",")
    he_lemma = he_prayer[:comma_idx]  # "עֹשֶׂה שָׁלוֹם (בעשי\"ת הַשָּׁלוֹם) בִּמְרוֹמָיו"

    old_text = seg["enText"]
    assert old_text.startswith("*(The person saying Kaddish requests:)*"), \
        f"pitum_kdr_comm_6 does not start as expected. Got: {old_text[:80]}"
    assert "Absolutely correct!" in old_text, \
        f"Expected 'Absolutely correct!' in pitum_kdr_comm_6. Got: {old_text}"

    # Build new text: prepend bold lemma, fix "correct!" -> ", we agree!"
    new_text = f"**{he_lemma}**—" + old_text.replace("Absolutely correct!", "Absolutely, we agree!")
    seg["enText"] = new_text
    print(f"FIX 7 applied: pitum_kdr_comm_6 — prepended lemma '{he_lemma}', fixed 'Absolutely correct!'")

    # ─── Fix 8: commentary_aleinu_1 (check 3) ──────────────────────────────
    # Rewrite the malformed double-lemma passage
    prayer = find_prayer(data, "p-aleinu")
    assert prayer is not None, "p-aleinu not found"
    seg = find_segment(prayer, "commentary_aleinu_1")
    assert seg is not None, "commentary_aleinu_1 not found"
    old_text = seg["enText"]
    # The broken section: from "**הַקָּדוֹשׁ בָּרוּךְ הוּא**—Who is both our understanding"
    # to "...here on earth (בָּרוּךְ הוּא)!"
    old_fragment = ("**הַקָּדוֹשׁ בָּרוּךְ הוּא**—Who is both our understanding; "
                    "**הַקָּדוֹשׁ בָּרוּךְ הוּא**—His Presence in the Heavens) and at the same time, "
                    "He is also the Source of everything here on earth (בָּרוּךְ הוּא)!")
    assert old_fragment in old_text, \
        f"Expected broken aleinu fragment not found. Got portion: {old_text[200:400]}"
    new_fragment = ("**הַקָּדוֹשׁ**—(Who is both our understanding of the transcendence of Hashem "
                    "beyond this world — His Presence in the Heavens) and at the same time, "
                    "He is also the Source of everything here on earth (**בָּרוּךְ הוּא**)!")
    seg["enText"] = old_text.replace(old_fragment, new_fragment)
    print("FIX 8 applied: commentary_aleinu_1 — corrected double-lemma passage")

    # ─── Fix 9: barchi_nafshi_commentary (check 3) ─────────────────────────
    # Insert missing paragraph after "grow bright and strong."
    prayer = find_prayer(data, "p-barchi-nafshi")
    assert prayer is not None, "p-barchi-nafshi not found"
    seg = find_segment(prayer, "barchi_nafshi_commentary")
    assert seg is not None, "barchi_nafshi_commentary not found"
    old_text = seg["enText"]
    anchor = "grow bright and strong. Every month"
    assert anchor in old_text, \
        f"Expected anchor text not found in barchi_nafshi_commentary. Got: {old_text[-200:]}"
    missing_paragraph = (
        'The same is true with each of us. We\'ve all had times when we feel we\'re not growing; '
        'we\'ve become insignificant and are losing our "light." But we always have the ability to '
        'pop back, just like the moon does every month. And why is that? Because the "laws of nature" '
        'and "rules of politics and sociology" are controlled by the Master Creator! '
        'But sometimes that\'s hard to see. So every month'
    )
    seg["enText"] = old_text.replace(
        anchor,
        "grow bright and strong. " + missing_paragraph + ", when that moon"
    ).replace(
        'grow bright and strong. The same is true with each of us.',
        'grow bright and strong. The same is true with each of us.'
    )
    # More careful replacement: replace the anchor specifically
    seg["enText"] = old_text.replace(
        "grow bright and strong. Every month, when that moon",
        ('grow bright and strong. The same is true with each of us. We\'ve all had times when we '
         'feel we\'re not growing; we\'ve become insignificant and are losing our "light." But we '
         'always have the ability to pop back, just like the moon does every month. And why is that? '
         'Because the "laws of nature" and "rules of politics and sociology" are controlled by the '
         'Master Creator! But sometimes that\'s hard to see. So every month, when that moon')
    )
    assert "The same is true with each of us." in seg["enText"], "Missing paragraph insertion failed"
    print("FIX 9 applied: barchi_nafshi_commentary — inserted missing personal-application paragraph")

    # ─── Fix 10: insight_lishuosecha (check 3) ──────────────────────────────
    # Fix lemma word order: קִוִּיתִי יְהֹוָה לִישׁוּעָתְךָ -> לִישׁוּעָתְךָ קִוִּיתִי יְהֹוָה
    # Derive from hebrew_lishuosecha heText (first three words)
    prayer = find_prayer(data, "p-shloshah-asar-ikarim")
    assert prayer is not None, "p-shloshah-asar-ikarim not found"
    # Get the correct Hebrew from hebrew_lishuosecha
    heb_seg = find_segment(prayer, "hebrew_lishuosecha")
    assert heb_seg is not None, "hebrew_lishuosecha not found"
    he_text = heb_seg["heText"]
    # First three words before the first colon: "לִישׁוּעָתְךָ קִוִּיתִי יְהֹוָה"
    colon_idx = he_text.index(":")
    first_phrase = he_text[:colon_idx]  # "לִישׁוּעָתְךָ קִוִּיתִי יְהֹוָה"

    seg = find_segment(prayer, "insight_lishuosecha")
    assert seg is not None, "insight_lishuosecha not found"
    old_text = seg["enText"]
    assert "**קִוִּיתִי יְהֹוָה לִישׁוּעָתְךָ**" in old_text, \
        f"Expected wrong-order lemma not found in insight_lishuosecha. Got: {old_text[:150]}"
    seg["enText"] = old_text.replace(
        "**קִוִּיתִי יְהֹוָה לִישׁוּעָתְךָ**",
        f"**{first_phrase}**"
    )
    print(f"FIX 10 applied: insight_lishuosecha — corrected lemma word order to '{first_phrase}'")

    # ─── Save ────────────────────────────────────────────────────────────────
    save(data)
    print("\nAll fixes applied and saved.")


if __name__ == "__main__":
    main()
