"""Deterministically assemble extracted chunk files into service JSON.
Run: python3 scripts/assemble_chunks.py
"""
import json, os

CHUNK_DIR = "scripts/chunks"
CONTENT = "src/content"

def load(name):
    with open(f"{CHUNK_DIR}/{name}.json", encoding="utf-8") as f:
        return json.load(f)

def collect(chunk_names, prayer_id):
    """Concatenate, in order, all segments from prayer objects matching prayer_id
    across the given chunks (and repeated prayer objects within a chunk)."""
    segs = []
    for cn in chunk_names:
        d = load(cn)
        for pr in d["prayers"]:
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
    """Drop duplicate header segments (same type+text) and ensure unique ids."""
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
    return {
        "id": prayer_id,
        "heTitle": he or h,
        "enTitle": en or e,
        "segments": dedup(collect(chunk_names, prayer_id)),
    }

# ---- SHACHARIS: surgically update existing file ----
with open(f"{CONTENT}/shacharit.json", encoding="utf-8") as f:
    sh = json.load(f)

def find_group(d, gid):
    return next(g for g in d["groups"] if g["id"] == gid)

# Pesukei D'Zimrah
g = find_group(sh, "g-pesukei-dzimrah")
g["prayers"] = [prayer("p-pesukei-dzimrah", ["pz1","pz2","pz3","pz4"],
                       he="פְּסוּקֵי דְּזִמְרָה", en="Pesukei D'Zimrah")]

# Shemoneh Esrei
g = find_group(sh, "g-shemoneh-esrei")
g["prayers"] = [prayer("p-shemoneh-esrei", ["se1","se2","se3","se4"],
                       he="שְׁמֹנֶה עֶשְׂרֵה", en="Shemoneh Esrei")]

# Tachanun group: keep existing Avinu Malkeinu, rebuild Tachanun from chunks
g = find_group(sh, "g-tachanun")
avinu = next((p for p in g["prayers"] if "avinu" in p["id"]), None)
tach = prayer("p-tachanun", ["tach1","tach2"], he="תַּחֲנוּן", en="Tachanun")
g["prayers"] = ([avinu] if avinu else []) + [tach]

# Krias HaTorah: keep existing Chatzi Kaddish first, replace Seder Krias HaTorah
g = find_group(sh, "g-krias-hatorah")
kaddish = next((p for p in g["prayers"] if "kaddish" in p["id"].lower()), None)
seder = prayer("p-seder-krias-hatorah", ["kt1","kt2","kt3"],
               he="סֵדֶר קְרִיאַת הַתּוֹרָה", en="Seder Krias HaTorah")
g["prayers"] = ([kaddish] if kaddish else []) + [seder]

with open(f"{CONTENT}/shacharit.json", "w", encoding="utf-8") as f:
    json.dump(sh, f, ensure_ascii=False, indent=2)

# ---- MINCHAH: rebuild ----
minchah = {
    "id": "minchah", "heTitle": "מִנְחָה", "enTitle": "Minchah",
    "groups": [
        {"id": "g-minchah-main", "title": "Minchah", "prayers": [
            prayer("p-ashrei-minchah", ["min1"], he="אַשְׁרֵי", en="Ashrei"),
            prayer("p-shemoneh-esrei-minchah", ["min2","min3","min4"], he="שְׁמֹנֶה עֶשְׂרֵה", en="Shemoneh Esrei"),
        ]},
        {"id": "g-minchah-concluding", "title": "Minchah — concluding", "prayers": [
            prayer("p-avinu-malkeinu-minchah", ["min5"], he="אָבִינוּ מַלְכֵּנוּ", en="Avinu Malkeinu"),
            prayer("p-tachanun-minchah", ["min5"], he="תַּחֲנוּן", en="Tachanun"),
            prayer("p-aleinu-minchah", ["min6"], he="עָלֵינוּ", en="Aleinu"),
        ]},
    ],
}
with open(f"{CONTENT}/minchah.json", "w", encoding="utf-8") as f:
    json.dump(minchah, f, ensure_ascii=False, indent=2)

# ---- MAARIV: rebuild ----
maariv = {
    "id": "maariv", "heTitle": "מַעֲרִיב", "enTitle": "Maariv",
    "groups": [
        {"id": "g-maariv-main", "title": "Maariv", "prayers": [
            prayer("p-maariv-shema", ["mv1","mv2"], he="קְרִיאַת שְׁמַע וּבִרְכוֹתֶיהָ", en="Krias Shema and its Brachos"),
            prayer("p-shemoneh-esrei-maariv", ["mv2","mv3","mv4"], he="שְׁמֹנֶה עֶשְׂרֵה", en="Shemoneh Esrei"),
        ]},
        {"id": "g-maariv-concluding", "title": "Maariv — concluding", "prayers": [
            prayer("p-aleinu-maariv", ["mv4"], he="עָלֵינוּ", en="Aleinu"),
        ]},
    ],
}
with open(f"{CONTENT}/maariv.json", "w", encoding="utf-8") as f:
    json.dump(maariv, f, ensure_ascii=False, indent=2)

# ---- report ----
for sid in ["shacharit","minchah","maariv"]:
    with open(f"{CONTENT}/{sid}.json", encoding="utf-8") as f:
        d = json.load(f)
    tot = sum(len(p["segments"]) for g in d["groups"] for p in g["prayers"])
    print(f"{sid}: {len(d['groups'])} groups, "
          f"{sum(len(g['prayers']) for g in d['groups'])} prayers, {tot} segments")
    for g in d["groups"]:
        print("   " + g["id"] + ": " + ", ".join(f"{p['enTitle']}({len(p['segments'])})" for p in g["prayers"]))
