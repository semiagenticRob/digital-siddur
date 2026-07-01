#!/usr/bin/env python3
"""Two print-verified meal-brachos fixes (audit 2026-07-01):

1. Birkas HaZan dropped the word אֵל. Print p.146: כִּי הוּא אֵל זָן וּמְפַרְנֵס לַכֹּל;
   app stored כִּי הוּא זָן. Restore, slicing אֵל from existing corpus text.

2. Al HaMichyah's opening + closing variant scaffold was wrong (print pp.153-154):
   - Opening merged four labeled options into an unlabeled run-on that dropped
     עַל הָעֵץ. Rebuild the four labeled options (על היין / על פירות / על מזונות /
     combined) — all vocalized fragments SLICED from existing app strings.
   - Closing variant #1 was a duplicate GRAIN chasimah; the WINE chasimah
     (…וְעַל פְּרִי הַגֶּפֶן) was absent. Restore it and relabel all four to the print's
     (unvocalized) labels. Vocalized bodies sliced from existing app text.
   The two Eretz-Yisrael parentheticals — (בא״י ועל פרי גפנה) / (בא״י ועל פירותיה) —
   need vocalized גַפְנָהּ / פֵּרוֹתֶיהָ, which appear nowhere in the corpus; NOT added
   here (would require retyping nikud). Logged to REVIEW_QUEUE.
"""
import json, re, glob, pathlib

NIKUD = re.compile(r"[֑-ׇ]")
def skel(s): return NIKUD.sub("", s).replace(" ", "").replace(":", "").replace(".", "")

# ---------- Fix 1: Birkas HaZan אֵל ----------
bm_path = pathlib.Path("src/content/birkas-hamazon.json")
bm = json.loads(bm_path.read_text(encoding="utf-8"))
prayers = {p["id"]: p for g in bm["groups"] for p in g["prayers"]}

# source אֵל by slicing a standalone occurrence from the corpus
pool = []
for f in glob.glob("src/content/*.json"):
    pool.append(pathlib.Path(f).read_text(encoding="utf-8"))
m = re.search(r"(?<![֑-ׇא-ת])אֵל(?![֑-ׇא-ת])", "\n".join(pool))
assert m, "could not find a standalone אֵל to slice"
EL = m.group(0)
assert skel(EL) == "אל"

hazan = prayers["p-hazan"]["segments"][1]
assert hazan["id"] == "hazan_prayer"
assert "כִּי הוּא זָן וּמְפַרְנֵס" in hazan["heText"], "hazan text not in expected state"
hazan["heText"] = hazan["heText"].replace("כִּי הוּא זָן", "כִּי הוּא " + EL + " זָן", 1)
assert "כִּי הוּא אֵל זָן וּמְפַרְנֵס" in hazan["heText"]
bm_path.write_text(json.dumps(bm, ensure_ascii=False, indent=2).rstrip("\n"), encoding="utf-8")
print("Fix 1: Birkas HaZan — restored", repr(EL), "-> כִּי הוּא אֵל זָן")

# ---------- Fix 2: Al HaMichyah opening + closing ----------
am_path = pathlib.Path("src/content/al-hamichyah.json")
am = json.loads(am_path.read_text(encoding="utf-8"))
segs = am["groups"][0]["prayers"][0]["segments"]
S = {s["id"]: s for s in segs}

p1 = S["s-am-prayer-1"]["heText"].split("\n")
p4 = S["s-am-prayer-4"]["heText"].split("\n")
# sanity on current (garbled) state
assert p1[0].startswith("בָּרוּךְ אַתָּה יְהֹוָה אֱלֹהֵינוּ מֶלֶךְ הָעוֹלָם")
assert "וְעַל פְּרִי הָעֵץ" in p1[1] and "עַל הַמִּחְיָה וְעַל הַכַּלְכָּלָה" in p1[1]
assert p1[3].startswith("עַל הַגֶּפֶן וְעַל פְּרִי הַגֶּפֶן")

# --- sliced vocalized fragments (never retyped) ---
BRACHA   = p1[0]                                             # בָּרוּךְ … מֶלֶךְ הָעוֹלָם
GEFEN    = p1[3].rstrip(".")                                 # עַל הַגֶּפֶן וְעַל פְּרִי הַגֶּפֶן
MECHYA   = p1[1].split(" וְעַל פְּרִי הָעֵץ")[0]                # עַל הַמִּחְיָה וְעַל הַכַּלְכָּלָה
PRI_ETZ  = "וְעַל פְּרִי הָעֵץ"                                 # tail of p1[1]
assert PRI_ETZ in p1[1]
AL   = MECHYA.split()[0]                                     # עַל
HAETZ = PRI_ETZ.split()[-1]                                  # הָעֵץ
ETZ_FULL = f"{AL} {HAETZ} {PRI_ETZ}"                         # עַל הָעֵץ וְעַל פְּרִי הָעֵץ
PRI_GEFEN = " ".join(GEFEN.split()[-2:])                     # פְּרִי הַגֶּפֶן

# closing bodies sliced from current p4
body_fruit = p4[1].split(": ", 1)[1]                         # בָּרוּךְ … עַל הָאָרֶץ וְעַל הַפֵּרוֹת:
body_grain = p4[2].split(": ", 1)[1]                         # בָּרוּךְ … וְעַל הַמִּחְיָה וְעַל הַכַּלְכָּלָה:
body_combo = p4[3].split(": ", 1)[1]                         # בָּרוּךְ … וְעַל (בא״י וְעַל) פְּרִי הַגֶּפֶן:
assert skel(body_fruit).endswith("ועלהפרות")
assert skel(body_grain).endswith("ועלהמחיהועלהכלכלה")
chasima_prefix = body_grain.split("וְעַל", 1)[0] + "וְעַל "   # בָּרוּךְ … עַל הָאָרֶץ וְעַל
body_wine = chasima_prefix + PRI_GEFEN + ":"                 # … וְעַל פְּרִי הַגֶּפֶן:
assert skel(body_wine) == "ברוךאתהיהוהעלהארץועלפריהגפן", skel(body_wine)

# --- rebuild opening (labels are PLAIN/unvocalized in the print) ---
new_p1 = "\n".join([
    BRACHA,
    "על היין: " + GEFEN,
    "על פירות משבעת המינים: " + ETZ_FULL,
    "על מזונות: " + MECHYA,
    "על מזונות ויין ביחד: " + f"{MECHYA} {GEFEN}",
])
# --- rebuild closing: wine first, then fruit/grain/combined ---
new_p4 = "\n".join([
    "על היין: " + body_wine,
    "על הפירות: " + body_fruit,
    "על מזונות: " + body_grain,
    "על מזונות ויין ביחד: " + body_combo,
])

# skeleton guards on the rebuilt vocalized content
assert skel(new_p1).startswith("ברוךאתהיהוהאלהינומלךהעולם")
assert "עלהעץועלפריהעץ" in skel(new_p1), "עַל הָעֵץ not restored in opening"
assert skel(new_p4).count("ברוךאתהיהוה") == 4
assert "ועלפריהגפן" in skel(new_p4) and skel(new_p4).count("ועלהמחיה") >= 2

S["s-am-prayer-1"]["heText"] = new_p1
S["s-am-prayer-4"]["heText"] = new_p4
am_path.write_text(json.dumps(am, ensure_ascii=False, indent=2).rstrip("\n"), encoding="utf-8")
print("Fix 2: Al HaMichyah — rebuilt opening (4 labeled options, עַל הָעֵץ restored)")
print("        and closing (wine chasimah restored, duplicate grain removed)")
