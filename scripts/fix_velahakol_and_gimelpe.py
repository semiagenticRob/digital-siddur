#!/usr/bin/env python3
"""Two reconcile fixes (PDF-extracted, rav-verify nikud):
1. Birkas HaMazon p-nodeh missing its closing bracha (וְעַל הַכֹּל … בָּרוּךְ … עַל
   הָאָרֶץ וְעַל הַמָּזוֹן) — print p.124. Append as a prayer at end of p-nodeh.
2. Krias Shema al Ha'mitah: add the ג״פ (×3) rubric before the four verses the
   print marks for triple recitation — ksm2-prayer-8/9/10/11 (print p.225).
"""
import json, re

VEAL = ("וְעַל הַכֹּל יְהֹוָה אֱלֹהֵינוּ אֲנַחְנוּ מוֹדִים לָךְ, וּמְבָרְכִים אוֹתָךְ, "
        "יִתְבָּרַךְ שִׁמְךָ בְּפִי כָּל חַי תָּמִיד לְעוֹלָם וָעֶד, כַּכָּתוּב, וְאָכַלְתָּ וְשָׂבָעְתָּ "
        "וּבֵרַכְתָּ אֶת יְהֹוָה אֱלֹהֶיךָ עַל הָאָרֶץ הַטֹּבָה אֲשֶׁר נָתַן לָךְ: "
        "בָּרוּךְ אַתָּה יְהֹוָה, עַל הָאָרֶץ וְעַל הַמָּזוֹן:")

def skel(s): return re.sub(r'[^א-ת]', '', s or '')

# ---- 1. Ve-al-hakol into birkas-hamazon.json ----
bh = json.load(open('src/content/birkas-hamazon.json'))
def find(n, pid):
    if isinstance(n, dict):
        if n.get('id') == pid: return n
        for v in n.values():
            r = find(v, pid)
            if r: return r
    elif isinstance(n, list):
        for x in n:
            r = find(x, pid)
            if r: return r
nodeh = find(bh, 'p-nodeh')
assert nodeh, 'p-nodeh not found'
assert not any(s.get('id') == 'nodeh_veal_hakol_prayer' for s in nodeh['segments']), 'already present'
assert skel(VEAL).startswith('ועלהכל') and skel(VEAL).endswith('ועלהמזון')
nodeh['segments'].append({'id': 'nodeh_veal_hakol_prayer', 'type': 'prayer', 'heText': VEAL})
json.dump(bh, open('src/content/birkas-hamazon.json', 'w'), ensure_ascii=False, indent=2)
print('Appended Ve-al-hakol closing to p-nodeh.')

# ---- 2. ג״פ rubrics into krias-shema-al-hamitah.json ----
ks = json.load(open('src/content/krias-shema-al-hamitah.json'))
prayer = None
def find_prayer(n):
    global prayer
    if isinstance(n, dict):
        if isinstance(n.get('segments'), list) and any(s.get('id')=='ksm2-prayer-8' for s in n['segments']):
            prayer = n
        for v in n.values(): find_prayer(v)
    elif isinstance(n, list):
        for x in n: find_prayer(x)
find_prayer(ks)
assert prayer, 'ksm2 prayer container not found'
segs = prayer['segments']
TARGETS = ['ksm2-prayer-8', 'ksm2-prayer-9', 'ksm2-prayer-10', 'ksm2-prayer-11']
for tid in TARGETS:
    rid = f'{tid}-gimelpe-rubric'
    if any(s.get('id') == rid for s in segs):
        continue
    idx = next(i for i, s in enumerate(segs) if s.get('id') == tid)
    segs.insert(idx, {'id': rid, 'type': 'rubric', 'heText': 'ג״פ'})
json.dump(ks, open('src/content/krias-shema-al-hamitah.json', 'w'), ensure_ascii=False, indent=2)
print(f'Inserted ג״פ rubric before {len(TARGETS)} verses (8,9,10,11).')
