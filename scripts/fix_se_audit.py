#!/usr/bin/env python3
"""Apply the VERIFIED Shemoneh Esrei audit fixes (print pages 60-75).
Every Hebrew lemma is DERIVED from the prayer text, never retyped."""
import json
import os

PATH = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'shacharit.json')
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shemoneh-esrei'][0]
S = g['prayers'][0]['segments']

def field(i):
    return 'heText' if S[i]['type'] == 'prayer' else 'enText'

def repl(i, old, new):
    f = field(i)
    s = S[i]
    assert old in s[f], f'seg {i}: not found: {old!r}'
    s[f] = s[f].replace(old, new, 1)

# Derive Hebrew phrases from prayer segments (assert presence first)
kakatuv = 'כַּכָּתוּב עַל יַד נְבִיאֶךָ'
assert kakatuv in S[40]['heText']
kibcha = 'כִּי בְךָ בָּטָחְנוּ'
assert kibcha in S[102]['heText']
yeru_ext = 'עִירְךָ בְּרַחֲמִים תָּשׁוּב'
assert yeru_ext in S[105]['heText']
bashalom = 'בַּשָּׁלוֹם'
assert bashalom in S[175]['heText']

# i=15 zachreinu: re-pair lemmas with prayer phrases, English unchanged
phrases = S[14]['heText'].rstrip(':').split(', ')
assert len(phrases) == 4
parts = S[15]['enText'].split('; ')
assert len(parts) == 4
glosses = [p.split('—', 1)[1] for p in parts]
S[15]['enText'] = '; '.join(f'**{phrases[k]}**—{glosses[k]}' for k in range(4))

# i=34 mi-chamocha split
repl(34, 'Father; Who remembers us, His creations, for life; **לְחַיִּים בְּרַחֲמִים**—with mercy.',
        'Father; **לְחַיִּים**—Who remembers us, His creations, for life; **בְּרַחֲמִים**—with mercy.')

# i=41 nekadeish: insert kakatuv lemma + fix וְקָרָא gloss
repl(41, 'the essence of Hashem. **וְקָרָא זֶה אֶל זֶה וְאָמַר**—As the Navi tells us; *(so that they all praise Hashem in unison)* and say:',
        f'the essence of Hashem. **{kakatuv}**—As the Navi tells us; **וְקָרָא זֶה אֶל זֶה וְאָמַר**—that one angel calls to the other *(so that they all praise Hashem in unison)* and say:')

# i=43 bold "all"
repl(43, 'can be felt in all worlds', 'can be felt in **all** worlds')

# i=103 extend lemma
repl(103, '**וְלֹא נֵבוֹשׁ**—and may we never feel embarrassed', f'**וְלֹא נֵבוֹשׁ {kibcha}**—and may we never feel embarrassed')

# i=106 extend lemma
repl(106, '**וְלִירוּשָׁלַיִם**—Hashem, even if', f'**וְלִירוּשָׁלַיִם {yeru_ext}**—Hashem, even if')

# i=176 בְּשָׁלוֹם -> בַּשָּׁלוֹם
repl(176, 'יִשְׂרָאֵל בְּשָׁלוֹם**', f'יִשְׂרָאֵל {bashalom}**')

# i=180/181 נְצוֹר -> נְצֹר (remove vav, derive target)
nezor_t = 'נְצוֹר'.replace('ו', '')
repl(180, 'נְצוֹר', nezor_t)
repl(181, 'נְצוֹר', nezor_t)

# English corrections
repl(1, 'I just daven here because', 'I just daven because')
repl(7, 'for all kinds of stuff', 'for stuff')
repl(7, 'Bas Yisrael!!', 'Bas Yisrael!')
repl(26, 'In Israel the summer add:', 'In Israel in the summer add:')
repl(124, "add Yaaleh V'Yavo:", "add Yaaleh V'Yavo: (If you forgot, see Appendix 12:6)")
repl(186, 'therefore give me strength and power save me', 'therefore with strength and power save me')

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('applied. nezor target codepoints:', [hex(ord(c)) for c in nezor_t])
