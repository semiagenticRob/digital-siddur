import json

PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shemoneh-esrei'][0]
segs = g['prayers'][0]['segments']
by = {s['id']: s for s in segs}

def repl(seg_id, old, new, field='enText'):
    s = by[seg_id]
    assert old in s[field], f'{seg_id}: {old!r} not found'
    s[field] = s[field].replace(old, new)

# ---- Text corrections ----
# 1) Kedushah section intro: essence word אוֹתוֹ, action word שֵׁם (both were אַתָּה)
repl('se1-section-intro-kedushah', 'represented by the word "אַתָּה"',
     'represented by the word "אוֹתוֹ"')
repl('se1-section-intro-kedushah', 'referred to as "אַתָּה"', 'referred to as "שֵׁם"')
# 2) Nekadeish commentary: essence term אוֹתוֹ (was אַתָּה); שֵׁם already correct
repl('se1-commentary-nekadeish', 'kedushah of "אַתָּה"—the essence', 'kedushah of "אוֹתוֹ"—the essence')
# 3) Refuah insert rubric: garbled בָּעֵר זֶה -> כָּאן
repl('se2-refuah-insert-rubric', 'יֹאמַר בָּעֵר זֶה תְּחִנָּה', 'יֹאמַר כָּאן תְּחִנָּה', field='heText')
# 4) Parnasah insert: הַשִּׂיבֵנִי -> הַטְרִיפֵנִי, and drop extra vav on second מִשֶּׁפַע
repl('se2-shema-koleinu-insert-prayer', 'הַשִּׂיבֵנִי לֶחֶם', 'הַטְרִיפֵנִי לֶחֶם', field='heText')
repl('se2-shema-koleinu-insert-prayer', 'וּמִשֶּׁפַע בְּרָכָה עֶלְיוֹנָה', 'מִשֶּׁפַע בְּרָכָה עֶלְיוֹנָה', field='heText')
# 5/6) Missing appendix cross-refs on two rubrics
repl('se3-rubric-al-hanissim', 'special "Thanks":', 'special "Thanks": (If you forgot, see Appendix 12:7)')
repl('se3-rubric-uchsov', 'During Aseres Yemei Teshuvah add:',
     'During Aseres Yemei Teshuvah add: (If you forgot, see Appendix 12:2)')

# ---- Reorderings (operate by id so indices don't matter) ----
def reorder(current_ids, desired_ids):
    assert sorted(current_ids) == sorted(desired_ids)
    start = next(i for i, s in enumerate(segs) if s['id'] == current_ids[0])
    assert [s['id'] for s in segs[start:start + len(current_ids)]] == current_ids, \
        [s['id'] for s in segs[start:start + len(current_ids)]]
    segs[start:start + len(current_ids)] = [by[i] for i in desired_ids]

# Retzei: prayer before its commentary
reorder(['se3-commentary-vsechezenah', 'se3-prayer-vsechezenah'],
        ['se3-prayer-vsechezenah', 'se3-commentary-vsechezenah'])
# Modim (two halves): prayer1, comm1, prayer2, comm2
reorder(['se3-commentary-modim', 'se3-prayer-modim', 'se3-commentary-modim-cont', 'se3-prayer-modim-cont'],
        ['se3-prayer-modim', 'se3-commentary-modim', 'se3-prayer-modim-cont', 'se3-commentary-modim-cont'])
# Sim Shalom AYT insert: rubric before the prayer it introduces
reorder(['se4-sim-shalom-teshuvah-insert', 'se4-sim-shalom-teshuvah-rubric'],
        ['se4-sim-shalom-teshuvah-rubric', 'se4-sim-shalom-teshuvah-insert'])
# Elokai Netzor optional tefillah: rubric before the prayer it introduces
reorder(['se4-elokai-netzor-tefillah-insert', 'se4-elokai-netzor-tefillah-rubric'],
        ['se4-elokai-netzor-tefillah-rubric', 'se4-elokai-netzor-tefillah-insert'])

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('applied all SE Step 2 fixes; segment count:', len(segs))
