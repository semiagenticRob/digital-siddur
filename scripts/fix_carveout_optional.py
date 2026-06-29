#!/usr/bin/env python3
"""Apply shacharit's carve-out visual convention (optional:true -> shaded box) to
every conditional/seasonal insert across the other services. Runs identified by
per-file analysis, modeled on shacharit. EXCLUDES the daily winter/summer
Mashiv-HaRuach/Morid-HaTal/Tal toggle, because shacharit itself does NOT box that
(se1-rubric-winter/summer are optional:false) — matching the reference style.

Each run is a contiguous block of segment ids within one container; the script
asserts every id exists, that the ids are contiguous and in array order within a
single container, then sets optional:true on each. Idempotent.
"""
import json

RUNS = {
 'src/content/al-hamichyah.json': [
   ['s-am-rubric-shabbos','s-am-prayer-shabbos'],
   ['s-am-rubric-roshchodesh','s-am-prayer-roshchodesh'],
   ['s-am-rubric-yomtov','s-am-prayer-yomtov'],
 ],
 'src/content/birkas-hamazon.json': [
   ['zimun-137-rubric','zimun-137-header','zimun-137-prayer'],
   ['al_hanissim_rubric','al_hanissim_prayer','al_hanissim_commentary',
    'al_hanissim_chanukah_prayer','al_hanissim_chanukah_commentary',
    'al_hanissim_purim_prayer','al_hanissim_purim_commentary'],
   ['shabbos_rubric','retzeh_he','retzeh_en'],
   ['yaaleh_rubric','yaaleh_he','yaaleh_occasion_rubric','yaaleh_he_2','yaaleh_en'],
   ['harachaman_shabbos_rubric','harachaman_shabbos_he','harachaman_shabbos_en'],
   ['harachaman_rc_rubric','harachaman_rc_he','harachaman_rc_en'],
   ['harachaman_yt_rubric','harachaman_yt_he','harachaman_yt_en'],
   ['harachaman_sukkos_rubric','harachaman_sukkos_he','harachaman_sukkos_en'],
 ],
 'src/content/hallel.json': [
   ['tehillim-115-omit-rubric','tehillim-115a-header','tehillim-115a-focus','tehillim-115a-gloss','tehillim-115a-text'],
   ['tehillim-116-omit-rubric','tehillim-116-header','tehillim-116-focus','tehillim-116-text'],
   ['hallel2-veyikrosem-rubric','hallel2-veyikrosem-prayer'],
   ['hallel2-kaddish-rubric'],
 ],
 'src/content/maariv.json': [
   ['mv1-s034','mv1-s035','mv1-s036'],
   ['mv2-extra-brachah-rubric','mv2-extra-brachah-subheader','mv2-baruch-label','mv2-baruch-text','mv2-baruch-comm-1'],
   ['mv2-avos-zochreinu-rubric','mv2-avos-zochreinu-text','mv2-avos-zochreinu-comm'],
   ['mv2-gevuros-mikamocha-rubric','mv2-gevuros-mikamocha-text','mv2-gevuros-mikamocha-comm'],
   ['mv2-binah-atah-chonantanu-rubric','mv2-binah-atah-chonantanu-text','mv2-binah-atah-chonantanu-comm','mv2-binah-atah-chonantanu-continue'],
   ['mv3-r-refua-cholim','mv3-c-refua-cholim'],
   ['mv3-r-shema-koleinu-tefillah','mv3-p-shema-koleinu-tefillah','mv3-c-private-requests'],
   ['mv3-r-yaaleh-veyavo','mv3-p-yaaleh-veyavo','mv3-c-yaaleh-veyavo'],
   ['mv4-seg-001','mv4-seg-002','mv4-seg-003','mv4-seg-004','mv4-seg-005','mv4-seg-006','mv4-seg-007','mv4-seg-008','mv4-seg-009'],
   ['mv4-seg-012','mv4-seg-013','mv4-seg-014'],
   ['mv4-seg-020','mv4-seg-021','mv4-seg-022'],
   ['mv4-seg-030','mv4-seg-031','mv4-seg-032'],
   ['mv4-seg-054'],
 ],
 'src/content/minchah.json': [
   ['min2-rubric-aseres-yemei-avos','min2-prayer-zachreinu','min2-commentary-zachreinu'],
   ['min2-rubric-aseres-yemei-mi-chamocha','min2-prayer-mi-chamocha','min2-commentary-mi-chamocha'],
   ['min2-prayer-ledor-vador-mhk'],
   ['min2-rubric-aneinu','min2-prayer-aneinu','min2-commentary-aneinu'],
   ['min2-rubric-refuah-insert','min2-prayer-refuah-insert','min2-commentary-refuah-insert'],
   ['min3-yerushalayim-nachem-rubric','min3-yerushalayim-nachem-prayer','min3-yerushalayim-nachem-commentary'],
   ['min3-shema-koleinu-aneinu-rubric','min3-shema-koleinu-aneinu-prayer','min3-shema-koleinu-aneinu-commentary'],
   ['min3-shema-koleinu-yom-kippur-rubric','min3-shema-koleinu-yom-kippur-prayer'],
   ['min3-avodah-yaaleh-veyavo-rubric','min3-avodah-yaaleh-veyavo-prayer','min3-avodah-yaaleh-veyavo-occasion','min3-avodah-yaaleh-veyavo-prayer-2','min3-avodah-yaaleh-veyavo-commentary'],
   ['al-hanissim-rubric','al-hanissim-prayer','al-hanissim-c1','al-hanissim-chanukah-rubric','al-hanissim-chanukah-prayer','al-hanissim-chanukah-c1','al-hanissim-purim-rubric','al-hanissim-purim-prayer','al-hanissim-purim-c1'],
   ['modim-uchsov-rubric','modim-uchsov-prayer','modim-uchsov-c1'],
   ['birkas-kohanim-rubric','birkas-kohanim-prayer','birkas-kohanim-c1','birkas-kohanim-insight'],
   ['sim-shalom-rubric','sim-shalom-prayer','sim-shalom-c1'],
   ['sim-shalom-besefer-rubric','sim-shalom-besefer-prayer','sim-shalom-besefer-c1'],
   ['yihyu-tefillah-rubric','yihyu-tefillah-prayer','yihyu-tefillah-c1'],
   ['am-2-rubric','am-2-he','am-2-en'],
   ['am-3-rubric','am-3-he','am-3-en'],
   ['am-18-rubric','am-18-he','am-18-en','am-19-he','am-19-en','am-20-he','am-20-en','am-21-he','am-21-en','am-22-he','am-22-en'],
   ['am-23-rubric','am-23-he','am-23-en','am-24-he','am-24-en','am-25-he','am-25-en','am-26-he','am-26-en','am-27-he','am-27-en'],
 ],
 'src/content/mussaf-rosh-chodesh.json': [
   ['mrc2-s004'],
   ['mrc2-s022','mrc2-s023','mrc2-s024','mrc2-s025','mrc2-s026'],
   ['mrc2-s047','mrc2-s048','mrc2-s049'],
 ],
 'src/content/mussaf-chol-hamoed.json': [
   ['seg-mch2-005','seg-mch2-006'],
   ['seg-mch2-010','seg-mch2-011','seg-mch2-012'],
   ['seg-mch2-013','seg-mch2-014','seg-mch2-015'],
   ['seg-mch2-016','seg-mch2-017','seg-mch2-018'],
   ['seg-mch2-019','seg-mch2-020','seg-mch2-021'],
   ['seg-mch2-022','seg-mch2-023'],
   ['seg-mch2-024','seg-mch2-025'],
   ['seg-mch2-026','seg-mch2-027'],
   ['seg-mch2-028','seg-mch2-029'],
   ['seg-mch2-030','seg-mch2-031'],
   ['seg-mch2-032','seg-mch2-033'],
   ['seg-mch2-034','seg-mch2-035'],
   ['seg-mch2-037','seg-mch2-038','seg-mch2-039'],
   ['seg-31','seg-32','seg-33'],
 ],
}

def containers(n):
    out=[]
    if isinstance(n,dict):
        if isinstance(n.get('segments'),list): out.append(n)
        for v in n.values(): out+=containers(v)
    elif isinstance(n,list):
        for x in n: out+=containers(x)
    return out

grand=0
for path, runs in RUNS.items():
    d=json.load(open(path))
    # map id -> (container_index, seg_index)
    loc={}
    for ci,c in enumerate(containers(d)):
        for si,s in enumerate(c['segments']):
            sid=s.get('id')
            if sid is not None:
                assert sid not in loc, f'{path}: duplicate id {sid}'
                loc[sid]=(ci,si)
    conts=containers(d)
    flagged=0; already=0
    for run in runs:
        idxs=[]
        for sid in run:
            assert sid in loc, f'{path}: id not found: {sid}'
            idxs.append(loc[sid])
        cis={c for c,_ in idxs}
        assert len(cis)==1, f'{path}: run spans multiple containers: {run}'
        sidx=[s for _,s in idxs]
        assert sidx==list(range(sidx[0], sidx[0]+len(sidx))), \
            f'{path}: run NOT contiguous/in-order: {run} -> indices {sidx}'
        ci=idxs[0][0]
        for _,si in idxs:
            seg=conts[ci]['segments'][si]
            if seg.get('optional'): already+=1
            else: seg['optional']=True; flagged+=1
    json.dump(d, open(path,'w'), ensure_ascii=False, indent=2)
    grand+=flagged
    print(f"{path.split('/')[-1]:32} runs={len(runs):2}  newly-flagged={flagged:3}  already-optional={already}")
print(f"\nTOTAL newly-flagged optional segments: {grand}")
