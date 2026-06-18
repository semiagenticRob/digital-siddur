import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-pesukei-dzimrah'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-pesukei-dzimrah'][0]
segs = p['segments']
by = {s['id']: s for s in segs}

YMLOCH = 'יְהוָה יִמְלֹךְ לְעֹלָם וָעֶד:'
TARGUM = 'יְהוָה מַלְכוּתֵהּ קָאֵם לְעָלַם וּלְעָלְמֵי עָלְמַיָּא:'

# ---- Block B Hebrew: מי כמכה → מקדש אדני כוננו ידיך (strip the trailing ה' ימלך) ----
b32 = by['azyashir-32']['heText'].strip()
assert b32.endswith(YMLOCH), b32[-40:]
b32_head = b32[:-len(YMLOCH)].rstrip()          # ends at "...כּוֹנְנוּ יָדֶיךָ:"
block_b_he = ' '.join([by['azyashir-28']['heText'].strip(),
                       by['azyashir-30']['heText'].strip(),
                       by['azyashir-31']['heText'].strip(),
                       b32_head])
assert block_b_he.endswith('יָדֶיךָ:'), block_b_he[-20:]

# ---- Block C Hebrew: ה' ימלך (×2) + (targum) + כי בא → ביום ההוא ----
a34 = by['azyashir-34']['heText'].strip()
assert TARGUM in a34
a34_paren = a34.replace(TARGUM, '(' + TARGUM + ')')      # parenthesize the Targum
block_c_he = ' '.join([YMLOCH, a34_paren, by['azyashir-36']['heText'].strip()])
assert block_c_he.endswith('וּשְׁמוֹ אֶחָד:'), block_c_he[-20:]

# ---- Commentary B (match print exactly: plain lemmas, "You", asides parenthesized) ----
block_b_en = (
    "מִי כָמֹכָה בָּאֵלִם יְהוָה—Among all the powers (*powers of nature, powers of "
    "humans*), who is equal to You, Hashem?; מִי כָּמֹכָה נֶאְדָּר בַּקֹּדֶשׁ—Who is like "
    "You, powerful but with purity of purpose?; נוֹרָא תְהִלֹּת עֹשֵׂה פֶלֶא—Our songs "
    "praising You instill in us awe of Your wondrous deeds, which are in truth beyond "
    "our comprehension. All the nations of the world shuddered with fear (*when they "
    "heard of this great miracle*). May dread and fear fall upon them until Your nation "
    "crosses over (*into Eretz Yisrael*), the place Your Presence is most felt."
)

# ---- Commentary C (two lemmas, asides parenthesized, per print) ----
block_c_en = (
    "יְהוָה יִמְלֹךְ לְעֹלָם וָעֶד—(*Just as we have seen the rulership of Hashem here at "
    "the sea, so too for all future times*) Hashem will reign forever and ever! "
    "כִּי לַיהוָה הַמְּלוּכָה וּמֹשֵׁל בַּגּוֹיִם—(*Once Mashiach comes*) the entire world "
    "will recognize Hashem as the King of His nation, Bnei Yisrael, and the ruler over "
    "all nations. On that day, Hashem will be recognized as the sole power, and His "
    "Presence will be felt by all."
)

new_block = [
    {'id': 'azyashir-28', 'type': 'prayer', 'heText': block_b_he},
    {'id': 'azyashir-29', 'type': 'commentary', 'heText': '', 'enText': block_b_en},
    {'id': 'azyashir-34', 'type': 'prayer', 'heText': block_c_he},
    {'id': 'azyashir-33', 'type': 'commentary', 'heText': '', 'enText': block_c_en},
]

# replace the run azyashir-28 .. azyashir-35 (currently 9 segments) in place
start = next(i for i, s in enumerate(segs) if s['id'] == 'azyashir-28')
old = ['azyashir-28','azyashir-29','azyashir-30','azyashir-31','azyashir-32',
       'azyashir-34','azyashir-33','azyashir-36','azyashir-35']
assert [s['id'] for s in segs[start:start+9]] == old, [s['id'] for s in segs[start:start+9]]
segs[start:start+9] = new_block

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
for s in segs[start-1:start+4]:
    print(s['type'], s['id'], '|', (s.get('heText') or s.get('enText') or '')[:48])
print('OK')
