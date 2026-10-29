#!/usr/bin/env python3
"""Make every service segment id unique across src/content/*.json.

Highlights and notes are keyed by segment id alone, and segmentIndex maps an id
back to one location. Duplicate ids meant highlighting one copy highlighted the
other, and a note jumped back to whichever copy the index found first.

Each rename names the exact (file, prayer, old id) it expects, asserts that
target exists exactly once, and fails loudly otherwise. The first occurrence of
each id keeps its name; later copies get a prayer-scoped name.
"""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'content')

# (file, prayer id, old segment id, new segment id)
RENAMES = [
    ('minchah.json', 'p-shemoneh-esrei-minchah', 'birkas-kohanim-prayer', 'minchah-birkas-kohanim-prayer'),
    ('shacharit.json', 'p-hanachas-tefillin', 'baruch_shem', 'tefillin-baruch-shem'),
    ('netilas-lulav.json', 'p-netilas-lulav', 'seg-header', 'netilas-lulav-header'),
    ('shacharit.json', 'p-birchos-hashachar', 'faq-chosen-people', 'birchos-hashachar-faq-chosen-people'),
    ('shacharit.json', 'p-shesh-zechiros', 'header', 'shesh-zechiros-header'),
    ('shacharit.json', 'p-shloshah-asar-ikarim', 'header', 'shloshah-asar-ikarim-header'),
    ('shacharit.json', 'p-birchos-krias-shema', 'section_intro', 'birchos-krias-shema-section-intro'),
    ('shacharit.json', 'p-pitum-haketores', 'section_intro', 'pitum-haketores-section-intro'),
    ('shacharit.json', 'p-shesh-zechiros', 'section_intro', 'shesh-zechiros-section-intro'),
    ('shacharit.json', 'p-shloshah-asar-ikarim', 'section_intro', 'shloshah-asar-ikarim-section-intro'),
    ('shacharit.json', 'p-shir-shel-yom', 'commentary_intro', 'shir-shel-yom-commentary-intro'),
    ('shacharit.json', 'p-barchi-nafshi', 'barchi_nafshi_commentary', 'barchi-nafshi-commentary'),
]


def main():
    docs = {}
    trailing_nl = {}  # keep each file's original EOF to avoid churn
    for fname, prayer_id, old, new in RENAMES:
        if fname not in docs:
            with open(os.path.join(ROOT, fname), encoding='utf-8') as f:
                raw = f.read()
            docs[fname] = json.loads(raw)
            trailing_nl[fname] = raw.endswith('\n')
        prayers = [p for g in docs[fname]['groups'] for p in g['prayers'] if p['id'] == prayer_id]
        assert len(prayers) == 1, f'{fname}: expected one prayer {prayer_id}, found {len(prayers)}'
        hits = [s for s in prayers[0]['segments'] if s['id'] == old]
        assert len(hits) == 1, f'{fname}/{prayer_id}: expected one segment {old}, found {len(hits)}'
        hits[0]['id'] = new
        print(f'{fname}/{prayer_id}: {old} -> {new}')

    for fname, doc in docs.items():
        path = os.path.join(ROOT, fname)
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
            if trailing_nl[fname]:
                f.write('\n')
        os.replace(tmp, path)


if __name__ == '__main__':
    main()
