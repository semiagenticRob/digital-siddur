#!/usr/bin/env python3
"""
Fix all commentary formatting errors found during the /goal audit:

1. bh2-comm-yehiratzon-lamakom: lemma starts "וִיהִי" but prayer starts "יְהִי" — remove vav
2. commentary_monday: enText truncated mid-sentence; append missing text from PDF p.132
3. pz1-commentary-1: lemma is italic (*...*) with leading em-dash; convert to bold (**...**—)
4. pz1-commentary-2: all Hebrew lemmas are italic; convert to bold. Multiple Kaddish phrases.
5. pz2-yehi-khvod-1-commentary: Hebrew lemmas are italic; convert to bold
6. pz2-yehi-khvod-2-commentary: Hebrew lemmas are italic (two spans merged); convert to bold
7. tach1-s18, s20, s22, s24, s26, s28: broken *word **lemma**—* format; merge to **word lemma**—
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

# ── helpers ──────────────────────────────────────────────────────────────────
def exact(node, seg_id, old_en, new_en):
    """Find seg_id, assert enText == old_en, replace with new_en."""
    return _patch(node, seg_id, old_en, new_en, [False])

def _patch(node, seg_id, old, new, flag):
    if isinstance(node, dict):
        if node.get('id') == seg_id and node.get('type') == 'commentary':
            assert node.get('enText') == old, (
                f'{seg_id}: expected\n  {old[:80]!r}\ngot\n  {node.get("enText","")[:80]!r}'
            )
            node['enText'] = new
            flag[0] = True
            print(f'  Fixed {seg_id}')
            return
        for v in node.values():
            if isinstance(v, (dict, list)):
                _patch(v, seg_id, old, new, flag)
    elif isinstance(node, list):
        for x in node:
            _patch(x, seg_id, old, new, flag)
    if not flag[0]:
        pass  # will be asserted after call

# ── Fix 1: bh2-comm-yehiratzon-lamakom ──────────────────────────────────────
# Prayer heText: "יְהִי רָצוֹן מִלְּפָנֶיךָ..." — lemma should NOT have the leading וִ
OLD_BH2 = ('**וִיהִי רָצוֹן מִלְּפָנֶיךָ** — May it be Your will, Hashem — Who controls everything '
           'and has taken care of Bnei Yisrael throughout history — that You make Torah study something '
           'comfortable and familiar to us; and make us feel a closeness and attachment to Your mitzvos. '
           'Do not bring us into situations and challenges that could lead us to sin or to be disappointed '
           'with ourselves; and do not allow the yetzer hara to get the better of us. Keep us far away '
           'from evil people and bad friends; and help us attach ourselves to our yetzer tov and to good '
           'friends. **וְכֹף אֶת יִצְרֵנוּ** — Compel our creative powers to be used to serve You. '
           'And may we always find favor in Your eyes, and in the eyes of everyone we meet. And do for us '
           'good acts of kindness. **הַגּוֹמֵל** — You, Hashem, are the Source of everything; '
           '**בָּרוּךְ אַתָּה יהוה** — **חֲסָדִים טוֹבִים לְעַמּוֹ יִשְׂרָאֵל** — Who does good acts '
           'of kindness to His nation, Bnei Yisrael.')
NEW_BH2 = OLD_BH2.replace('**וִיהִי רָצוֹן מִלְּפָנֶיךָ**', '**יְהִי רָצוֹן מִלְּפָנֶיךָ**', 1)
assert NEW_BH2 != OLD_BH2
f1 = [False]
_patch(data, 'bh2-comm-yehiratzon-lamakom', OLD_BH2, NEW_BH2, f1)
assert f1[0], 'bh2-comm-yehiratzon-lamakom not found or text mismatch'

# ── Fix 2: commentary_monday ─────────────────────────────────────────────────
# Text ends mid-sentence; PDF p.132 provides the completion.
OLD_MON = ('**שִׁיר מִזְמוֹר לִבְנֵי קֹרַח**—The city of Yerushalayim was chosen by Hashem as His '
           'special place where He will reveal His greatness to the nations of the world. And just as '
           'Yerushalayim (with its unique kedushah and beauty) is to be an example to us of how to '
           'conduct our lives, so, too, we are to be a model for others to emulate. And as the unique '
           'status of')
NEW_MON = OLD_MON + (' Yerushalayim is eternal, so, too, our unique relationship with Hashem '
                     'is eternal.')
f2 = [False]
_patch(data, 'commentary_monday', OLD_MON, NEW_MON, f2)
assert f2[0], 'commentary_monday not found or text mismatch'

# ── Fix 3: pz1-commentary-1 ─────────────────────────────────────────────────
# Leading em-dash + italic lemma → standard bold lemma + em-dash
OLD_PZ1_1 = ('—*מִזְמוֹר שִׁיר חֲנֻכַּת הַבַּיִת* A song composed by David HaMelech to be used in '
             'the eventual dedication of the Beis Hamikdash—I praise You because You have raised me up '
             'from the depths of all my difficulties—and You did not let my enemies (*real or imagined*) '
             'triumph over me. I called out to You and You healed me; You brought me back up when I was '
             'down. I should always be singing Your praises because Your "anger" is only for a '
             'moment—and its purpose is really to improve our lives! Though **בְּרֶגַע**—in "dark times" '
             '(*when we are in pain*) we do not understand the purpose of our pain, we are confident '
             'that **לַבֹּקֶר**—"in the morning" (*when all is clear*), we will be joyful. '
             '**וַאֲנִי אָמַרְתִּי בְשַׁלְוִי**—When all is calm and my body healthy, I think '
             '**בַּל אֶמּוֹט לְעוֹלָם**—that state is natural and will last forever. But I know that it '
             'is You, Hashem, Who keeps me strong. If You would chas v\'shalom "turn away from me"—all '
             'would fall apart. Therefore, I turn to You for help; it is to You I call out and proclaim: '
             '"My goal is to accomplish the mission You gave me." Therefore, I need Your (*material and '
             'emotional*) support to allow me to do that! **הָפַכְתָּ מִסְפְּדִי לְמָחוֹל לִי**—So '
             'many times You turn my difficulties into growth opportunities (*even though I do not always '
             'realize that at the moment*)—all in order for me to accomplish my mission. Hashem Who '
             'takes care of me—in all circumstances I will praise You!')
NEW_PZ1_1 = OLD_PZ1_1.replace(
    '—*מִזְמוֹר שִׁיר חֲנֻכַּת הַבַּיִת* A song',
    '**מִזְמוֹר שִׁיר חֲנֻכַּת הַבַּיִת**—A song', 1)
assert NEW_PZ1_1 != OLD_PZ1_1
f3 = [False]
_patch(data, 'pz1-commentary-1', OLD_PZ1_1, NEW_PZ1_1, f3)
assert f3[0], 'pz1-commentary-1 not found or text mismatch'

# ── Fix 4: pz1-commentary-2 ─────────────────────────────────────────────────
# All Hebrew Kaddish phrases in italic (*...*); convert to bold (**...**)
OLD_PZ1_2 = ('יִתְגַּדַּל וְיִתְקַדַּשׁ שְׁמֵהּ רַבָּא (*The person saying Kaddish proclaims our '
             'hope that*) soon, in our lifetime, the entire world, which Hashem created precisely '
             'according to His Will, will recognize Hashem as the Source of all and will see the '
             'sanctity, perfection, and purpose of all He has done. '
             '*אָמֵן. יְהֵא שְׁמֵהּ רַבָּא מְבָרַךְ לְעָלַם וּלְעָלְמֵי עָלְמַיָּא* '
             '(*We all enthusiastically respond:*) Absolutely correct! May everyone (*including me!*), '
             'everywhere, and forever, see that all His actions are great and deserving of praise! '
             '*יִתְבָּרַךְ וְיִשְׁתַּבַּח* (*The person saying Kaddish then points out that*) in '
             'reality, the true greatness and power of Hashem far exceeds any praises that we mere '
             'humans could say. And to that we respond: **אָמֵן**—Absolutely correct! '
             '*יְהֵא שְׁלָמָא רַבָּא* (*The person saying Kaddish requests:*) May there be abundant '
             'peace, that comes from Heaven, and life, upon us and upon all of Bnei Yisrael. And to '
             'that we respond: **אָמֵן**—Absolutely, we agree! '
             '*עֹשֶׂה שָׁלוֹם בִּמְרוֹמָיו* (*The person saying Kaddish requests:*) May He Who makes '
             'peace in the Heavens bring about peace upon us and upon all of Bnei Yisrael! And to that '
             'we respond: **אָמֵן**—Absolutely, we agree!')
NEW_PZ1_2 = (OLD_PZ1_2
    .replace('יִתְגַּדַּל וְיִתְקַדַּשׁ שְׁמֵהּ רַבָּא (*The person',
             '**יִתְגַּדַּל וְיִתְקַדַּשׁ שְׁמֵהּ רַבָּא** (*The person', 1)
    .replace('*אָמֵן. יְהֵא שְׁמֵהּ רַבָּא מְבָרַךְ לְעָלַם וּלְעָלְמֵי עָלְמַיָּא*',
             '**אָמֵן. יְהֵא שְׁמֵהּ רַבָּא מְבָרַךְ לְעָלַם וּלְעָלְמֵי עָלְמַיָּא**', 1)
    .replace('*יִתְבָּרַךְ וְיִשְׁתַּבַּח*',
             '**יִתְבָּרַךְ וְיִשְׁתַּבַּח**', 1)
    .replace('*יְהֵא שְׁלָמָא רַבָּא*',
             '**יְהֵא שְׁלָמָא רַבָּא**', 1)
    .replace('*עֹשֶׂה שָׁלוֹם בִּמְרוֹמָיו*',
             '**עֹשֶׂה שָׁלוֹם בִּמְרוֹמָיו**', 1)
)
assert NEW_PZ1_2 != OLD_PZ1_2
f4 = [False]
_patch(data, 'pz1-commentary-2', OLD_PZ1_2, NEW_PZ1_2, f4)
assert f4[0], 'pz1-commentary-2 not found or text mismatch'

# ── Fix 5: pz2-yehi-khvod-1-commentary ──────────────────────────────────────
OLD_PZ2_1 = ('*יְהִי כְבוֹד יְהֹוָה*—May the Presence of Hashem be felt and seen clearly in the '
             'world; *(that way it will be easier for us to act appropriately)* and thus Hashem will '
             'be pleased with us—His creations. From the East to the West—the entire world, the Heavens '
             'and the earth and all the nations proclaim the glory of Hashem and His absolute and '
             'eternal rulership over "nature" and the course of world history—from the beginning of '
             'time till the end of days. *רַבּוֹת מַחֲשָׁבוֹת בְּלֶב אִישׁ*—Humans have many plans, '
             'thoughts and intentions; *וַעֲצַת יְהֹוָה הִיא תָקוּם*—but in the end, only the plan '
             'of Hashem will prevail. The "plan" Hashem has for history is eternal and spans all '
             'generations *(which is why we have difficulty grasping its entirety).*')
NEW_PZ2_1 = (OLD_PZ2_1
    .replace('*יְהִי כְבוֹד יְהֹוָה*—', '**יְהִי כְבוֹד יְהֹוָה**—', 1)
    .replace('*רַבּוֹת מַחֲשָׁבוֹת בְּלֶב אִישׁ*—', '**רַבּוֹת מַחֲשָׁבוֹת בְּלֶב אִישׁ**—', 1)
    .replace('*וַעֲצַת יְהֹוָה הִיא תָקוּם*—', '**וַעֲצַת יְהֹוָה הִיא תָקוּם**—', 1)
)
assert NEW_PZ2_1 != OLD_PZ2_1
f5 = [False]
_patch(data, 'pz2-yehi-khvod-1-commentary', OLD_PZ2_1, NEW_PZ2_1, f5)
assert f5[0], 'pz2-yehi-khvod-1-commentary not found or text mismatch'

# ── Fix 6: pz2-yehi-khvod-2-commentary ──────────────────────────────────────
OLD_PZ2_2 = ('*כִּי בָחַר יְהֹוָה בְּצִיּוֹן*—Hashem has chosen Eretz Yisrael as His special land, '
             'and us, Bnei Yisrael, as His *(סְגֻלָּה)* special treasure. '
             '*כִּי לֹא יִטֹּשׁ יְהֹוָה עַמּוֹ*—and He will never destroy Bnei Yisrael or abandon '
             'His land. *וְהוּא רַחוּם יְכַפֵּר עָוֹן וְלֹא יַשְׁחִית* (Even if we mess up,) He will '
             'forgive our sins, give us another chance; '
             '*הַמֶּלֶךְ יַעֲנֵנוּ בְיוֹם* *קָרְאֵנוּ*—Hashem, please *(continue)* to save us and '
             'answer our tefillos whenever we call out to You.')
NEW_PZ2_2 = (OLD_PZ2_2
    .replace('*כִּי בָחַר יְהֹוָה בְּצִיּוֹן*—', '**כִּי בָחַר יְהֹוָה בְּצִיּוֹן**—', 1)
    .replace('*כִּי לֹא יִטֹּשׁ יְהֹוָה עַמּוֹ*—', '**כִּי לֹא יִטֹּשׁ יְהֹוָה עַמּוֹ**—', 1)
    .replace('*וְהוּא רַחוּם יְכַפֵּר עָוֹן וְלֹא יַשְׁחִית*',
             '**וְהוּא רַחוּם יְכַפֵּר עָוֹן וְלֹא יַשְׁחִית**', 1)
    # Merge the two split italic spans into one bold lemma
    .replace('*הַמֶּלֶךְ יַעֲנֵנוּ בְיוֹם* *קָרְאֵנוּ*—',
             '**הַמֶּלֶךְ יַעֲנֵנוּ בְיוֹם קָרְאֵנוּ**—', 1)
)
assert NEW_PZ2_2 != OLD_PZ2_2
f6 = [False]
_patch(data, 'pz2-yehi-khvod-2-commentary', OLD_PZ2_2, NEW_PZ2_2, f6)
assert f6[0], 'pz2-yehi-khvod-2-commentary not found or text mismatch'

# ── Fix 7: tach1-s18, s20, s22, s24, s26, s28 ───────────────────────────────
# Pattern: *prefix **lemma**—*rest  →  **prefix lemma**—rest
TACH1_FIXES = {
    'tach1-s18': (
        '*וְהוּא **רַחוּם יְכַפֵּר עָוֹן**—*',
        '**וְהוּא רַחוּם יְכַפֵּר עָוֹן**—',
    ),
    'tach1-s20': (
        '*הַטֵּה **אֱלֹהַי אָזְנְךָ וּשְׁמָע**—*',
        '**הַטֵּה אֱלֹהַי אָזְנְךָ וּשְׁמָע**—',
    ),
    'tach1-s22': (
        '*הַבֶּט **נָא רַחֶם נָא**—*',
        '**הַבֶּט נָא רַחֶם נָא**—',
    ),
    'tach1-s24': (
        '*אָנָּא **מֶלֶךְ חַנּוּן וְרַחוּם**—*',
        '**אָנָּא מֶלֶךְ חַנּוּן וְרַחוּם**—',
    ),
    'tach1-s26': (
        '*אַל **רַחוּם וְחַנּוּן**—*',
        '**אַל רַחוּם וְחַנּוּן**—',
    ),
    'tach1-s28': (
        '*אֵין **כָּמוֹךָ חַנּוּן וְרַחוּם**—*',
        '**אֵין כָּמוֹךָ חַנּוּן וְרַחוּם**—',
    ),
}

def find_full_en(node, seg_id):
    if isinstance(node, dict):
        if node.get('id') == seg_id:
            return node.get('enText', '')
        for v in node.values():
            r = find_full_en(v, seg_id)
            if r is not None: return r
    elif isinstance(node, list):
        for x in node:
            r = find_full_en(x, seg_id)
            if r is not None: return r
    return None

for seg_id, (old_prefix, new_prefix) in TACH1_FIXES.items():
    full = find_full_en(data, seg_id)
    assert full is not None, f'{seg_id} not found'
    assert full.startswith(old_prefix), (
        f'{seg_id}: expected prefix {old_prefix!r}, got {full[:80]!r}')
    new_full = new_prefix + full[len(old_prefix):]
    flag = [False]
    _patch(data, seg_id, full, new_full, flag)
    assert flag[0]

# ── write ─────────────────────────────────────────────────────────────────────
with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('All fixes applied.')
