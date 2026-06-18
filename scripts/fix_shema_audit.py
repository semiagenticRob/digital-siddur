#!/usr/bin/env python3
"""Apply the verified Krias Shema audit fixes (print pages 55-59).
Does NOT touch the Divine Name spelling (held for rav sign-off) or maqaf.
Every edit asserts its target exists; added Hebrew is derived from the prayer
text, not retyped.
"""
import json, re

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shema'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-birchos-krias-shema'][0]
S = p['segments']

def repl(i, old, new):
    s = S[i]
    field = 'heText' if s['type'] == 'prayer' else 'enText'
    assert old in s[field], f'seg {i}: not found: {old!r}'
    s[field] = s[field].replace(old, new, 1)

def ital(i, inner):
    repl(i, f'({inner})', f'*({inner})*')

# --- derive added Hebrew from the prayer text (don't retype) ---
vhaya = S[53]['heText']; vayomer = S[56]['heText']
et_hashamayim = re.search(r'וְעָצַר (אֶת הַשָּׁמַיִם)', vhaya).group(1)
ureitem = re.search(r'(וּרְאִיתֶם) אֹתוֹ', vayomer).group(1)
lo_tasuru_full = re.search(r'(וְלֹא תָתוּרוּ אַחֲרֵי לְבַבְכֶם וְאַחֲרֵי עֵינֵיכֶם)', vayomer).group(1)

# --- i=41,43,45: italicize parenthetical asides (Shema kavanos / Baruch Shem) ---
ital(41, 'with all the responsibilities that come with that!')
ital(43, 'just that sometimes the "medicine" is bitter')
ital(45, 'so all humans will recognize His existence and power')

# --- i=54 (Vehaya gloss): extend בָּכֶם וְעָצַר lemma; italicize two asides ---
repl(54, '**בָּכֶם וְעָצַר**—', f'**בָּכֶם וְעָצַר {et_hashamayim}**—')
ital(54, 'Then, in order to help you return to clarity')
ital(54, 'But even in exile')

# --- i=57 (Vayomer gloss): extend two truncated lemmas; italicize techeiles aside ---
repl(57, '**אֹתוֹ**—', f'**{ureitem} אֹתוֹ**—')
repl(57, '**וְלֹא תָתוּרוּ**—', f'**{lo_tasuru_full}**—')
ital(57, 'techeiles is the color of the sea, which is similar to the sky, which looks like a sapphire, which will remind you of the throne of Hashem—a lesson that spiritual growth is a slow, step-by-step process!')

# --- i=63 (Emes prayer): tzitzis-kiss rubric יִשַּׁק -> יִנְשַׁק (missing נ) ---
repl(63, '(יִשַּׁק הַצִּיצִיּוֹת', '(יִנְשַׁק הַצִּיצִיּוֹת')

# --- i=64 (gloss): abbreviated Name ה -> ה׳ (add geresh) ---
repl(64, '**ה אֱלֹקֵיכֶם אֱמֶת**', '**ה׳ אֱלֹקֵיכֶם אֱמֶת**')

# --- i=70 (Geulah gloss): remove duplicated leading clause; italicize aside ---
repl(70, '**מִמִּצְרַיִם גְּאַלְתָּנוּ יְהוָה**—And at that time we sang Shirah to You. '
        'And You consistently answer our nation whenever they cry out to You for help. '
        '**תְּהִלּוֹת לְאֵל עֶלְיוֹן**—',
        '**תְּהִלּוֹת לְאֵל עֶלְיוֹן**—')
ital(70, 'When You split the sea and saved us from the Egyptians')

# --- i=72,76,78: italicize parenthetical asides (Geulah glosses) ---
ital(72, 'powers of nature, powers of humans')
ital(76, 'Just as we have seen the rulership of Hashem here at the sea, so too for all future times')
ital(78, 'And therefore we ask that just like You miraculously saved us then from the Egyptians and we sang Shirah, so too now')
ital(78, 'from Egypt, and will redeem us in the future')

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('applied Shema audit fixes; derived:', repr(et_hashamayim), repr(ureitem), repr(lo_tasuru_full[:20]+'...'))
