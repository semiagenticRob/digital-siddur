"""Assemble the 10 additional-section chunk files into individual service JSONs.
Run after the additional-sections workflow completes.
Run: python3 scripts/assemble_additional.py
"""
import json

CHUNK_DIR = "scripts/chunks2"
CONTENT = "src/content"

def load(name):
    with open(f"{CHUNK_DIR}/{name}.json", encoding="utf-8") as f:
        return json.load(f)

def collect(chunk_names, prayer_id):
    segs = []
    for cn in chunk_names:
        for pr in load(cn)["prayers"]:
            if pr["id"] == prayer_id:
                segs.extend(pr["segments"])
    return segs

def title_for(chunk_names, prayer_id):
    for cn in chunk_names:
        for pr in load(cn)["prayers"]:
            if pr["id"] == prayer_id:
                return pr["heTitle"], pr["enTitle"]
    return None, None

def dedup(segments):
    out, seen_headers, seen_ids = [], set(), {}
    for s in segments:
        if s.get("type") == "header":
            key = (s.get("heText",""), s.get("enText",""))
            if key in seen_headers:
                continue
            seen_headers.add(key)
        sid = s.get("id","seg")
        if sid in seen_ids:
            seen_ids[sid] += 1
            s = {**s, "id": f"{sid}_{seen_ids[sid]}"}
        else:
            seen_ids[sid] = 0
        out.append(s)
    return out

def prayer(prayer_id, chunk_names, he=None, en=None):
    h, e = title_for(chunk_names, prayer_id)
    return {"id": prayer_id, "heTitle": he or h, "enTitle": en or e,
            "segments": dedup(collect(chunk_names, prayer_id))}

def service(sid, he, en, group_title, prayers):
    return {"id": sid, "heTitle": he, "enTitle": en,
            "groups": [{"id": f"g-{sid}", "title": group_title, "prayers": prayers}]}

# (service_id, heTitle, enTitle, group_title, [ (prayer_id, [chunks], he, en) ])
SERVICES = [
    ("al-hamichyah", "עַל הַמִּחְיָה", "Al HaMichyah", "Al HaMichyah",
        [("p-al-hamichyah", ["after1"], "עַל הַמִּחְיָה", "Al HaMichyah")]),
    ("borei-nefashos", "בּוֹרֵא נְפָשׁוֹת", "Borei Nefashos", "Borei Nefashos",
        [("p-borei-nefashos", ["after1"], "בּוֹרֵא נְפָשׁוֹת", "Borei Nefashos")]),
    ("tefillas-haderech", "תְּפִלַּת הַדֶּרֶךְ", "Tefillas HaDerech", "Tefillas HaDerech",
        [("p-tefillas-haderech", ["after1"], "תְּפִלַּת הַדֶּרֶךְ", "Tefillas HaDerech")]),
    ("maariv-motzaei-shabbos", "מַעֲרִיב לְמוֹצָאֵי שַׁבָּת", "Maariv for Motzaei Shabbos", "Maariv for Motzaei Shabbos",
        [("p-maariv-motzaei-shabbos", ["mms1"], "מַעֲרִיב לְמוֹצָאֵי שַׁבָּת", "Maariv for Motzaei Shabbos")]),
    ("sefiras-haomer", "סְפִירַת הָעוֹמֶר", "Sefiras HaOmer", "Sefiras HaOmer",
        [("p-sefiras-haomer", ["omer1"], "סְפִירַת הָעוֹמֶר", "Sefiras HaOmer")]),
    ("krias-shema-al-hamitah", "קְרִיאַת שְׁמַע עַל הַמִּטָּה", "Krias Shema al HaMitah", "Krias Shema al HaMitah",
        [("p-krias-shema-al-hamitah", ["ksm1","ksm2"], "קְרִיאַת שְׁמַע עַל הַמִּטָּה", "Krias Shema al HaMitah")]),
    ("netilas-lulav", "נְטִילַת לוּלָב", "Netilas Lulav", "Netilas Lulav",
        [("p-netilas-lulav", ["lulav1"], "נְטִילַת לוּלָב", "Netilas Lulav")]),
    ("hallel", "הַלֵּל", "Hallel", "Hallel",
        [("p-hallel", ["hallel1","hallel2"], "הַלֵּל", "Hallel")]),
    ("mussaf-rosh-chodesh", "מוּסַף לְרֹאשׁ חֹדֶשׁ", "Mussaf for Rosh Chodesh", "Mussaf for Rosh Chodesh",
        [("p-mussaf-rosh-chodesh", ["mrc1","mrc2"], "מוּסַף לְרֹאשׁ חֹדֶשׁ", "Mussaf for Rosh Chodesh")]),
    ("mussaf-chol-hamoed", "מוּסַף לְחוֹל הַמּוֹעֵד", "Mussaf for Chol Hamoed", "Mussaf for Chol Hamoed",
        [("p-mussaf-chol-hamoed", ["mch1","mch2","mch3"], "מוּסַף לְחוֹל הַמּוֹעֵד", "Mussaf for Chol Hamoed")]),
]

for sid, he, en, gtitle, prs in SERVICES:
    prayers = [prayer(pid, chunks, ph, pen) for (pid, chunks, ph, pen) in prs]
    svc = service(sid, he, en, gtitle, prayers)
    with open(f"{CONTENT}/{sid}.json", "w", encoding="utf-8") as f:
        json.dump(svc, f, ensure_ascii=False, indent=2)
    tot = sum(len(p["segments"]) for g in svc["groups"] for p in g["prayers"])
    print(f"{sid}: {tot} segments")
