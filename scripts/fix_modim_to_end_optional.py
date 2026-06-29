#!/usr/bin/env python3
"""
Comprehensive optional:true fix for Modim D'Rabbanan → end of Shacharis.
Marks all holiday/conditional/AYT/fast-day/'some add' blocks as optional
so they render in the gray shaded box.

Groups (each becomes one contiguous optional box within its prayer):
  G1  Al Hanissim (Chanukah/Purim in Modim) — 9 segments
  G2  Uchsov (AYT in Modim) — 3 segments
  G3  Sim Shalom AYT — 3 segments
  G4  Elokai Netzor optional tefillah — 3 segments
  G5  Vidui before Tachanun — 40 segments (vidui-1 … vidui-40)
  G6  AM AYT-4 + Fast-4 substitutions — 6 segments
  G7  AM AYT main block — 11 segments
  G8  AM fast-day main block — 11 segments
  G9  Barchi Nafshi (Rosh Chodesh) — 10 segments
  G10 Elul Ledavid (Rosh Chodesh Elul → Hoshana Rabbah) — 6 segments
"""
import json

OPTIONAL_IDS = {
    # G1 — Al Hanissim
    'se3-rubric-al-hanissim',
    'se3-prayer-al-hanissim',
    'se3-commentary-al-hanissim',
    'se3-rubric-chanukah',
    'se3-prayer-bimei-matisyahu',
    'se3-commentary-chanukah',
    'se3-rubric-purim',
    'se3-prayer-bimei-mordechai',
    'se3-commentary-purim',
    # G2 — Uchsov
    'se3-rubric-uchsov',
    'se3-prayer-uchsov',
    'se3-commentary-uchsov',
    # G3 — Sim Shalom AYT
    'se4-sim-shalom-teshuvah-rubric',
    'se4-sim-shalom-teshuvah-insert',
    'se4-sim-shalom-teshuvah-c',
    # G4 — Elokai Netzor optional tefillah
    'se4-elokai-netzor-tefillah-rubric',
    'se4-elokai-netzor-tefillah-insert',
    'se4-elokai-netzor-tefillah-c',
    # G5 — Vidui before Tachanun
    *[f'vidui-{i}' for i in range(1, 41)],
    # G6 — Avinu Malkeinu AYT-4 + Fast-4
    'avinu_malkeinu_rubric_ayt_4',
    'avinu_malkeinu_4a',
    'avinu_malkeinu_commentary_4a',
    'avinu_malkeinu_rubric_fast_4',
    'avinu_malkeinu_4b',
    'avinu_malkeinu_commentary_4b',
    # G7 — Avinu Malkeinu AYT main block
    'avinu_malkeinu_rubric_ayt',
    'avinu_malkeinu_ayt_1', 'avinu_malkeinu_commentary_ayt_1',
    'avinu_malkeinu_ayt_2', 'avinu_malkeinu_commentary_ayt_2',
    'avinu_malkeinu_ayt_3', 'avinu_malkeinu_commentary_ayt_3',
    'avinu_malkeinu_ayt_4', 'avinu_malkeinu_commentary_ayt_4',
    'avinu_malkeinu_ayt_5', 'avinu_malkeinu_commentary_ayt_5',
    # G8 — Avinu Malkeinu fast-day main block
    'avinu_malkeinu_rubric_fast',
    'avinu_malkeinu_fast_1', 'avinu_malkeinu_commentary_fast_1',
    'avinu_malkeinu_fast_2', 'avinu_malkeinu_commentary_fast_2',
    'avinu_malkeinu_fast_3', 'avinu_malkeinu_commentary_fast_3',
    'avinu_malkeinu_fast_4', 'avinu_malkeinu_commentary_fast_4',
    'avinu_malkeinu_fast_5', 'avinu_malkeinu_commentary_fast_5',
    # G9 — Barchi Nafshi (Rosh Chodesh)
    'barchi_nafshi_rubric',
    'barchi_nafshi_intro',
    'barchi_nafshi_commentary',
    'barchi_nafshi_v1_4',
    'barchi_nafshi_v5_8',
    'barchi_nafshi_v9_12',
    'barchi_nafshi_v13_16',
    'barchi_nafshi_v17_20',
    'barchi_nafshi_v21_24',
    'barchi_nafshi_v25_28',
    'barchi_nafshi_v29_32',
    'barchi_nafshi_v33_35',
    # G10 — Elul Ledavid (Ps. 27)
    'rubric_elul_insert',
    'header_title',
    'commentary_1',
    'commentary_2',
    'commentary_3',
    'prayer_body',
}

with open('src/content/shacharit.json') as f:
    data = json.load(f)

done = set()

def patch(node):
    if isinstance(node, list):
        for x in node: patch(x)
    elif isinstance(node, dict):
        nid = node.get('id')
        if nid in OPTIONAL_IDS:
            if not node.get('optional'):
                node['optional'] = True
                done.add(nid)
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)

missing = OPTIONAL_IDS - done
# Some IDs might already be optional (e.g. barchi_nafshi already has COND flag)
# Only flag truly missing ones
truly_missing = {m for m in missing if m not in {'barchi_nafshi_v1_4',
    'barchi_nafshi_v5_8','barchi_nafshi_v9_12','barchi_nafshi_v13_16',
    'barchi_nafshi_v17_20','barchi_nafshi_v21_24','barchi_nafshi_v25_28',
    'barchi_nafshi_v29_32','barchi_nafshi_v33_35',
    'avinu_malkeinu_4a','avinu_malkeinu_4b',
    'avinu_malkeinu_ayt_1','avinu_malkeinu_ayt_2','avinu_malkeinu_ayt_3',
    'avinu_malkeinu_ayt_4','avinu_malkeinu_ayt_5',
    'avinu_malkeinu_fast_1','avinu_malkeinu_fast_2','avinu_malkeinu_fast_3',
    'avinu_malkeinu_fast_4','avinu_malkeinu_fast_5',
}}
if truly_missing:
    print(f'WARNING — not found: {truly_missing}')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Done. Marked {len(done)} segments optional.')
for gname, gids in [
    ('G1 Al Hanissim', ['se3-rubric-al-hanissim','se3-prayer-bimei-matisyahu','se3-prayer-bimei-mordechai']),
    ('G2 Uchsov', ['se3-rubric-uchsov']),
    ('G3 SimShalom AYT', ['se4-sim-shalom-teshuvah-rubric']),
    ('G4 ElokaiNetzor', ['se4-elokai-netzor-tefillah-rubric']),
    ('G5 Vidui', ['vidui-1','vidui-40']),
    ('G6 AM AYT4+Fast4', ['avinu_malkeinu_rubric_ayt_4','avinu_malkeinu_rubric_fast_4']),
    ('G7 AM AYT main', ['avinu_malkeinu_rubric_ayt']),
    ('G8 AM fast main', ['avinu_malkeinu_rubric_fast']),
    ('G9 Barchi Nafshi', ['barchi_nafshi_rubric']),
    ('G10 Elul', ['rubric_elul_insert']),
]:
    status = all(g in done for g in gids)
    print(f'  {gname}: {"✓" if status else "✗"}')
