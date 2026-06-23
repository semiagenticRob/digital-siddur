#!/usr/bin/env python3
"""
Batch fix script: post-SE Shacharis audit 2026-06-23
Covers SE brachos, Tachanun, Krias HaTorah, Avinu Malkeinu, and concluding sections.

Changes applied (all PDF-verified by vision agents):
  SE:          parenthetical asterisk format (i=78,83,88,92,108); avodah header (i=120)
  Tachanun:    garbled text (i=1); tach1-s7 type+spelling (i=6)
  KT:          kt1-header enTop; kt1-chatzi-kaddish-header nikud
  Avinu Malk.: header enTop
  Shesh Zech.: header enTop; section_intro "list just four"
  Shloshah AI: header enTop; swap commentary/prayer order for all 13 principles
  L'Dovid:     header_title "Teshuva"; remove running_header
  Barchi Naf.: strip trailing {פ}
  Pitum HaK.:  remove misplaced rubric_in_israel (belongs to Kaddish D'Rabbanan)
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def find_prayer(node, pid):
    if isinstance(node, dict):
        if node.get('id') == pid and isinstance(node.get('segments'), list):
            return node
        for v in node.values():
            r = find_prayer(v, pid)
            if r: return r
    elif isinstance(node, list):
        for x in node:
            r = find_prayer(x, pid)
            if r: return r

# ─── Shemoneh Esrei ────────────────────────────────────────────────────────────
se = find_prayer(data, 'p-shemoneh-esrei')
segs = se['segments']

# i=78: parenthetical asides use (*text*) instead of *(text)*
s = segs[78]
assert s['id'] == 'se2-aneinu-commentary', s['id']
en = s['enText']
en = en.replace('(*when describing the end of days*)', '*(when describing the end of days)*')
en = en.replace('(*Hashem*)', '*(Hashem)*')
en = en.replace('(*that are in their hearts*)', '*(that are in their hearts)*')
assert en != s['enText']
s['enText'] = en
print('i=78 aneinu: fixed parenthetical format')

# i=83
s = segs[83]
assert s['id'] == 'se2-refuah-commentary', s['id']
en = s['enText']
en = en.replace('(*physical and emotional*)', '*(physical and emotional)*')
assert en != s['enText']
s['enText'] = en
print('i=83 refuah: fixed parenthetical format')

# i=88
s = segs[88]
assert s['id'] == 'se2-shanim-commentary', s['id']
en = s['enText']
en = en.replace('(*in the summer say: a blessing*)', '*(in the summer say: a blessing)*')
en = en.replace('(*in the winter say: rain and dew for a blessing*)', '*(in the winter say: rain and dew for a blessing)*')
assert en != s['enText']
s['enText'] = en
print('i=88 shanim: fixed parenthetical format')

# i=92
s = segs[92]
assert s['id'] == 'se2-kibbutz-commentary', s['id']
en = s['enText']
en = en.replace('(*make a public demonstration of Your Divine Presence*)',
                '*(make a public demonstration of Your Divine Presence)*')
en = en.replace('(*to our Land*)', '*(to our Land)*')
assert en != s['enText']
s['enText'] = en
print('i=92 kibbutz: fixed parenthetical format')

# i=108: missing ! in parenthetical
s = segs[108]
assert s['id'] == 'se2-david-commentary', s['id']
en = s['enText']
en = en.replace('(*present tense—just like the previous brachah*)',
                '*(present tense—just like the previous brachah!)*')
assert en != s['enText']
s['enText'] = en
print('i=108 david: fixed parenthetical (added !)')

# i=120: avodah header "to" → "in"
s = segs[120]
assert s['id'] == 'se2-avodah-header', s['id']
en = s['enText']
en = en.replace('Return the avodah to the Beis Hamikdash',
                'Return the avodah in the Beis Hamikdash')
assert en != s['enText']
s['enText'] = en
print('i=120 avodah: "to" → "in" the Beis Hamikdash')

# ─── Tachanun ──────────────────────────────────────────────────────────────────
tach = find_prayer(data, 'p-tachanun')
ts = tach['segments']

# i=1: garbled "they mind" → "the world"
s = ts[1]
assert s['id'] == 'tach1-s2', s['id']
en = s['enText']
en = en.replace('that they mind intuitively knows', 'that the world intuitively knows')
assert en != s['enText']
s['enText'] = en
print('Tachanun i=1: "they mind" → "the world"')

# i=6: type prayer→rubric + spelling וְיֹאמֶר → וַיֹּאמֶר
s = ts[6]
assert s['id'] == 'tach1-s7', s['id']
assert s['type'] == 'prayer', f'Expected prayer, got {s["type"]}'
s['type'] = 'rubric'
he = s['heText']
he = he.replace('וְיֹאמֶר דָּוִד', 'וַיֹּאמֶר דָּוִד')
assert he != s['heText']
s['heText'] = he
print('Tachanun i=6: type→rubric + וַיֹּאמֶר spelling')

# ─── Krias HaTorah ─────────────────────────────────────────────────────────────
kt = find_prayer(data, 'p-seder-krias-hatorah')
ks = kt['segments']

# i=0: kt1-header enTop: true
s = ks[0]
assert s['id'] == 'kt1-header', s['id']
s['enTop'] = True
print('kt1-header: enTop → true')

# i=56: nikud fix
s = ks[56]
assert s['id'] == 'kt1-chatzi-kaddish-header', s['id']
assert s.get('heText') == 'חצי קדיש', f'Unexpected: {s.get("heText")}'
s['heText'] = 'חֲצִי קַדִּישׁ'
print('kt1-chatzi-kaddish-header: added nikud')

# ─── Avinu Malkeinu ────────────────────────────────────────────────────────────
am = find_prayer(data, 'avinu_malkeinu')
as_ = am['segments']
s = as_[12]
assert s['id'] == 'avinu_malkeinu_header', s['id']
s['enTop'] = True
print('avinu_malkeinu_header: enTop → true')

# ─── Shesh Zechiros ────────────────────────────────────────────────────────────
sz = find_prayer(data, 'p-shesh-zechiros')
ss = sz['segments']

s = ss[0]
assert s['id'] == 'header', s['id']
assert s.get('heText') == 'שֵׁשׁ זְכִירוֹת'
s['enTop'] = True
print('Shesh Zechiros header: enTop → true')

s = ss[1]
en = s['enText']
en = en.replace('list four,', 'list just four,', 1)
assert en != s['enText']
s['enText'] = en
print('Shesh Zechiros section_intro: "list just four"')

# ─── Shloshah Asar Ikarim ──────────────────────────────────────────────────────
sai = find_prayer(data, 'p-shloshah-asar-ikarim')
sis = sai['segments']

s = sis[0]
assert s['id'] == 'header', s['id']
s['enTop'] = True
print('Shloshah Asar Ikarim header: enTop → true')

# Swap commentary/prayer pairs for all 13 principles so Hebrew comes first
# Currently: commentary_ani_N at even indices, hebrew_ani_N at odd indices (i=2..27)
for n in range(1, 14):
    ci = 2 + (n-1)*2      # commentary
    pi = ci + 1            # prayer (hebrew)
    c_seg = sis[ci]
    p_seg = sis[pi]
    assert 'commentary' in c_seg['id'], f'Expected commentary at i={ci}: {c_seg["id"]}'
    assert 'hebrew' in p_seg['id'], f'Expected hebrew at i={pi}: {p_seg["id"]}'
    sis[ci], sis[pi] = sis[pi], sis[ci]
print('Shloshah Asar Ikarim: swapped all 13 principle pairs (Hebrew now first)')

# ─── L'Dovid ───────────────────────────────────────────────────────────────────
ldovid = find_prayer(data, 'p-ldovid-hashem-ori')
ls = ldovid['segments']

# Fix header_title BEFORE removing i=0 (indices still original)
s = ls[2]
assert s['id'] == 'header_title', s['id']
en = s['enText']
en = en.replace('Teshuvah Process', 'Teshuva Process')
assert en != s['enText']
s['enText'] = en
print('L\'Dovid header_title: "Teshuvah" → "Teshuva"')

# Remove running_header (i=0) — print artifact, not prayer content
s = ls[0]
assert s['id'] == 'running_header', s['id']
ls.pop(0)
print('L\'Dovid: removed running_header segment (print artifact)')

# ─── Barchi Nafshi ─────────────────────────────────────────────────────────────
bn = find_prayer(data, 'p-barchi-nafshi')
bs = bn['segments']
s = bs[12]
assert s['id'] == 'barchi_nafshi_v33_35', s['id']
he = s['heText']
he = he.replace(' {פ}', '')
assert he != s['heText']
s['heText'] = he
print('Barchi Nafshi i=12: stripped {פ} paragraph marker')

# ─── Pitum HaKetores ───────────────────────────────────────────────────────────
pitum = find_prayer(data, 'p-pitum-haketores')
ps = pitum['segments']
s = ps[0]
assert s['id'] == 'rubric_in_israel', s['id']
assert s.get('enText') == 'In Israel, the following is added:', s.get('enText')
ps.pop(0)
print('Pitum HaKetores: removed misplaced rubric_in_israel (belongs to Kaddish D\'Rabbanan section)')

# ─── Write ─────────────────────────────────────────────────────────────────────
with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('\nAll fixes applied. Run: npm run check')
