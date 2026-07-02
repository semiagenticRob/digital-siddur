#!/usr/bin/env python3
"""Build src/content/book-matter.json from the print's front/back matter
(introductions, dedications, acknowledgments, personal notes).

All body text is taken verbatim from `pdftotext` output — Hebrew included,
never retyped (retyping drops nikud/letters). Two structural quirks of this
particular extraction are corrected mechanically (never by retyping Hebrew):

1. Page-break running heads/folios. The print sets these essays as
   first-line-indent paragraphs with NO blank-line gap between paragraphs,
   so pdftotext gives one continuous run of text per page — paragraph
   breaks are therefore NOT recoverable from blank lines. `strip_running_head`
   removes each page's leading/trailing running-head or folio-number line(s);
   pages are then flattened to one continuous string per piece and paragraph
   boundaries are located with an explicit, ordered list of marker
   substrings (each asserted present via str.index, which raises loudly if
   the source text ever shifts). Markers were determined by reading the
   300 DPI page renders alongside the text (see task-9-report.md).

2. Inline Hebrew-citation embeds. pdftotext wraps each embedded RTL run in
   RLE/PDF bidi-control characters (U+202B/U+202C) and, for short citations
   of the form "HEBREW—English gloss", sometimes (a) emits the run's leading
   neutral punctuation (an em dash or a closing paren) at the *start* of the
   embed instead of the end, and (b) omits the space at the script boundary
   where the embed abuts English/Hebrew text. `fix_leading_punct` and
   `fix_script_boundary_spacing` correct these mechanically (they move
   punctuation/insert spacing; no Hebrew letter or nikud mark is ever
   retyped). A third, unrelated case (`fix_ze_eli`) swaps two whole RTL runs
   that pdftotext emitted in physical left-to-right order instead of logical
   (Hebrew reading) order — again a whole-substring swap, not retyping.

One inline citation (the Ashrei lemma quoted in translation-note, "Happy are
those who are living in the house of Hashem") is vocalized, and pdftotext
mangles vocalized Hebrew badly (spurious spaces inside words, sometimes
reordering a base letter and its point). Rather than attempt to un-mangle
it, that citation is sliced from the *already-digitized-and-proofed* Ashrei
prayer commentary in shacharit.json (same lemma, same gloss — verified) —
still "derive by slicing an existing string," per CLAUDE.md, just from
within the corpus instead of from this page's own (corrupted) extraction.

One further Hebrew line — the dedications' Isaiah 56:5 epigraph (pdf p.8,
"I will give them... a monument and a name") — is *also* vocalized-and-
mangled, and unlike the Ashrei lemma it does not already exist anywhere else
in the corpus to slice from. Per the task's explicit fallback ("document
anything you cannot resolve rather than retype"), it is OMITTED from
book-matter.json; see docs/REVIEW_QUEUE.md and task-9-report.md.
"""
import json
import re
import subprocess

PDF = "feigenbaum-siddur-original.pdf"
_PAGE_CACHE = {}

NUMERAL = r"[IVXLC]+|\d+"
BIDI_CONTROL = re.compile(r"[‪-‮⁦-⁩]")
HEBREW_RANGE = re.compile(r"[֐-׿]")


def page_text(n):
    if n not in _PAGE_CACHE:
        raw = subprocess.run(
            ["pdftotext", "-f", str(n), "-l", str(n), PDF, "-"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        # The print's discretionary soft-hyphen marks (U+00AD) sit at
        # hyphenation points inside compound words (e.g. "self-\xadunderstood").
        # Where one falls right at a pdftotext line-wrap ("heart-\xad\nto-\xad-
        # heart"), collapse the soft-hyphen *and* the following newline
        # together (no space — the word continues), rather than letting the
        # later whitespace-collapse turn that newline into a stray space.
        # A bare mid-line soft hyphen is dropped in the final cleanup pass.
        raw = re.sub(r"\xad\s*\n\s*", "", raw)
        # Same story for a line-wrap that falls right after a slash in a
        # compound term ("ben Torah/\nbas Yisrael") — no soft hyphen marks
        # it (the slash is itself already a break point), but the following
        # newline must still collapse to nothing, not a stray space.
        raw = re.sub(r"/\s*\n\s*", "/", raw)
        _PAGE_CACHE[n] = raw
    return _PAGE_CACHE[n]


# ---------------------------------------------------------------------------
# Hebrew-embed mechanical fixes (never retype a Hebrew letter or nikud mark)
# ---------------------------------------------------------------------------

def fix_ze_eli(text):
    """pdftotext emits the two RTL runs of a hyphenated two-word citation
    (Az Yashir's 'this is my God', hyphenated across the two Divine-Name
    letters) in physical left-to-right order instead of logical (Hebrew
    reading) order. Swap the two whole embedded runs — the Hebrew letters
    inside each run are untouched, only their order relative to each other
    changes. Verified against the 300 DPI render of pdf p.18/19."""
    pat = re.compile(r"‫([^‬]*)‬-‫([^‬]*)‬")
    matches = list(pat.finditer(text))
    assert len(matches) == 1, f"expected exactly one hyphen-joined RTL pair, found {len(matches)}"
    m = matches[0]
    swapped = f"‫{m.group(2)}‬-‫{m.group(1)}‬"
    return text[: m.start()] + swapped + text[m.end() :]


def fix_leading_punct(text):
    """Move a neutral punctuation mark (em dash or closing paren) that
    pdftotext placed at the START of an RTL embed to the END instead,
    dropping the embed markers. E.g. an embed of the form ' — HEBREW' (dash
    first) becomes 'HEBREW—' (dash last), matching where it visually sits in
    the print (immediately before the following English gloss)."""
    pat = re.compile(r"‫\s*([—)])\s*([^‬]+)‬")

    def repl(m):
        punct, heb = m.group(1), m.group(2)
        return heb.strip() + punct

    return pat.sub(repl, text)


def strip_bidi_controls(text):
    return BIDI_CONTROL.sub("", text)


def fix_script_boundary_spacing(text):
    """Insert a space wherever pdftotext glued a Hebrew run directly against
    an adjacent Latin letter with no space (a cosmetic extraction artifact —
    the closing bidi-embed marker directly abuts the next English word with
    no space in the source). Never removes or reorders a letter."""
    text = re.sub(r"([֐-׿])([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"([A-Za-z])([֐-׿])", r"\1 \2", text)
    text = re.sub(r"([֐-׿]\))([A-Za-z])", r"\1 \2", text)
    return text


def clean_hebrew_embeds(text):
    text = fix_leading_punct(text)
    text = strip_bidi_controls(text)
    text = fix_script_boundary_spacing(text)
    return text


def sliced_lemma(json_path, english_anchor):
    """Extract an already-digitized, already-proofed bold Hebrew lemma from
    an existing content JSON file by its English gloss anchor (ASCII-only
    pattern — the Hebrew itself is captured, never typed, into the regex)."""
    raw = open(json_path, encoding="utf-8").read()
    pat = re.compile(r"\*\*([^*]+)\*\*—" + re.escape(english_anchor))
    m = pat.search(raw)
    assert m, f"lemma anchored by {english_anchor!r} not found in {json_path}"
    return m.group(1)


ASHREI_LEMMA = sliced_lemma(
    "src/content/shacharit.json",
    "Happy are those who (wherever they are) are living in the house of Hashem",
)


def fix_ashrei_quote(text):
    """Replace the whole vocalized-and-mangled Ashrei citation span (pdf
    p.16) with the clean lemma sliced from shacharit.json above. The span is
    located purely by its ASCII anchors on both sides, so the corrupted
    Hebrew itself is never inspected or retyped — just cut out wholesale."""
    start_anchor = "they will be in italics: e.g., “"
    end_anchor = "Happy are those who (wherever they are) are living"
    i = text.index(start_anchor) + len(start_anchor)
    j = text.index(end_anchor, i)
    assert HEBREW_RANGE.search(text[i:j]), "expected corrupted Hebrew between anchors"
    return text[:i] + ASHREI_LEMMA + "—" + text[j:]


# ---------------------------------------------------------------------------
# Page-break cleanup + paragraph assembly
# ---------------------------------------------------------------------------

def strip_running_head(n, heads, required=True):
    """Return page n's body with a leading/trailing running-head and/or
    folio-number block removed. `heads` lists the exact running-head
    string(s) (without the numeral) that may legitimately appear on this
    page (a page can carry a 1- or 2-line header/footer combination)."""
    text = page_text(n)
    lines = text.split("\n")
    head_alt = "|".join(re.escape(h) for h in heads) if heads else r"(?!x)x"
    noise_re = re.compile(
        rf"^(?:(?:{NUMERAL})\s+(?:{head_alt})|(?:{head_alt})\s+(?:{NUMERAL})"
        rf"|(?:{head_alt})|(?:{NUMERAL}))$"
    )
    i, hit = 0, False
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if noise_re.match(s):
            hit = True
            i += 1
            continue
        break
    lines = lines[i:]
    j = len(lines)
    while j > 0:
        s = lines[j - 1].strip()
        if not s:
            j -= 1
            continue
        if noise_re.match(s):
            hit = True
            j -= 1
            continue
        break
    lines = lines[:j]
    if required:
        assert hit, f"page {n}: expected a running head/folio (heads={heads!r})"
    return "\n".join(lines).strip("\n")


def flatten(page_specs):
    """page_specs: list of (page_number, heads, required). Returns one
    continuous whitespace-normalized string spanning all the given pages,
    with the Hebrew-embed fixes applied first (page-local, so page-break
    splicing below never has to reason about embed internals)."""
    parts = []
    for n, heads, required in page_specs:
        body = strip_running_head(n, heads, required=required)
        parts.append(body)
    text = "\n\n".join(parts)
    return text


def split_at_markers(text, markers):
    """Split `text` into paragraphs at each marker substring (in order).
    Every marker must occur — str.index raises loudly if the source text
    ever shifts — and nothing before the first marker may be left over."""
    positions = []
    cursor = 0
    for m in markers:
        idx = text.index(m, cursor)
        positions.append(idx)
        cursor = idx + 1
    leading = text[: positions[0]].strip()
    assert leading == "", f"unclaimed text before first marker: {leading!r}"
    positions.append(len(text))
    paras = []
    for k in range(len(markers)):
        chunk = text[positions[k] : positions[k + 1]]
        chunk = re.sub(r"\s+", " ", chunk).strip()
        paras.append(chunk)
    return paras


def take_trailing_hebrew(text, after_marker):
    """Split off a single Hebrew-only line that immediately follows
    `after_marker` (an ASCII substring). Returns (english_part, hebrew_line,
    leftover) — leftover is whatever text (if any) follows that line, for
    callers where the Hebrew line isn't literally the end of the source
    text. The Hebrew is sliced, never typed, and only verified (contains
    Hebrew, no Latin letters), never transcribed."""
    idx = text.index(after_marker)
    end = idx + len(after_marker)
    remainder = text[end:].lstrip("\n \t")
    nl = remainder.find("\n")
    tail = (remainder if nl == -1 else remainder[:nl]).strip()
    leftover = "" if nl == -1 else remainder[nl:]
    assert tail, "expected a trailing Hebrew line"
    assert HEBREW_RANGE.search(tail), f"trailing text has no Hebrew: {tail!r}"
    assert not re.search(r"[A-Za-z]", tail), f"trailing text has Latin letters: {tail!r}"
    return text[:end].strip(), tail, leftover


def commentary(seg_id, en_text):
    return {"id": seg_id, "type": "commentary", "enText": en_text}


def prayer(seg_id, he_text):
    return {"id": seg_id, "type": "prayer", "heText": he_text}


def rubric(seg_id, en_text):
    return {"id": seg_id, "type": "rubric", "enText": en_text}


def header(seg_id, en_text=None, he_text=None):
    seg = {"id": seg_id, "type": "header"}
    if he_text is not None:
        seg["heText"] = he_text
    if en_text is not None:
        seg["enText"] = en_text
    return seg


def clean_he_line(s):
    return strip_bidi_controls(s).strip()


# ---------------------------------------------------------------------------
# intro-teens  ("But I Don't Do Davening!" — pdf pp.18-23)
# ---------------------------------------------------------------------------

def build_intro_teens():
    specs = [(n, ["Introduction for Teens"], n != 18) for n in range(18, 24)]
    raw = flatten(specs)
    heading = "INTRODUCTION FOR TEENS\n“But I Don’t Do Davening!”\n\n(“OK, I do davening, but I don’t enjoy it!”)"
    assert raw.startswith(heading)
    raw = raw[len(heading) :]
    raw = fix_ze_eli(raw)
    text = clean_hebrew_embeds(raw)

    markers = [
        "OK, I get that. That is actually the most common comment",
        "So we need to figure out",
        "But maybe",
        "Perhaps there are other possible reasons you",
        "OK — I hear that. So don’t",
        "I once walked into my ninth",
        "But I would like to suggest one last possible reason",
        "It is self-",
        "One brachah! All growth is in stages.",
        "Be wary of what the mussar sefarim call",
        "Will this be a steady climb up?",
        "The Satmar Rebbe, zy”a, used to say the following:",
        "So don’t be afraid to join the club",
        "How will this siddur help? This is",
        "Of course, whenever possible, you should say the tefillos",
        "Of all the “Instant Insights” in this siddur",
        "If used properly, honestly, and diligently, this siddur will",
    ]
    paras = split_at_markers(text, markers)

    segs = [
        rubric("intro-teens-parenthetical", "(“OK, I do davening, but I don’t enjoy it!”)")
    ]
    for i, p in enumerate(paras, 1):
        segs.append(commentary(f"intro-teens-p{i}", p))
    return {
        "id": "intro-teens",
        "title": "“But I Don’t Do Davening!”",
        "subtitle": "Introduction for Teens",
        "segments": segs,
    }


# ---------------------------------------------------------------------------
# translation-note ("How to Read the Translation" — pdf pp.16-18)
# ---------------------------------------------------------------------------

def build_translation_note():
    p16 = strip_running_head(16, ["Introduction for Parents, Mechanchim, and Mechanchos"])
    p16 = fix_ashrei_quote(p16)
    p17 = strip_running_head(17, ["Introduction for Parents, Mechanchim, and Mechanchos"])
    p18 = strip_running_head(18, [], required=False)

    heading = "Note Regarding This “Translation”"
    end_marker = "INTRODUCTION FOR TEENS"
    i = p16.index(heading) + len(heading)
    j = p18.index(end_marker)
    text = "\n\n".join([p16[i:], p17, p18[:j]])
    text = clean_hebrew_embeds(text)

    # The three bullets aren't ASCII-anchorable before cleaning (they start
    # with a Hebrew word), so split on the final paragraph first, then peel
    # the bullets off the remainder using the bullet glyph itself.
    markers = [
        "First of all, this is",
        "Thus at times, long paragraphs",
        "Tefillos that I felt are most central",
        "In addition, commentaries like the Malbim",
    ]
    head_paras = split_at_markers(text[: text.index("Throughout this siddur")], markers)
    tail = text[text.index("Throughout this siddur") :]
    tail = re.sub(r"\s+", " ", tail).strip()

    # `head_paras[3]` ends with "...do not fit the norm:" immediately
    # followed by the three bullets (each starts with "• "). Split those
    # off into their own segments.
    lead, _, bullets_blob = head_paras[3].partition("• ")
    bullets_blob = "• " + bullets_blob
    bullet_paras = [b.strip() for b in re.split(r"(?=• )", bullets_blob) if b.strip()]
    assert len(bullet_paras) == 3, f"expected 3 bullets, got {len(bullet_paras)}"

    segs = [commentary("translation-note-p1", head_paras[0])]
    segs.append(commentary("translation-note-p2", head_paras[1]))
    segs.append(commentary("translation-note-p3", head_paras[2]))
    segs.append(commentary("translation-note-p4", lead.strip()))
    for i, b in enumerate(bullet_paras, 1):
        segs.append(commentary(f"translation-note-bullet{i}", b))
    segs.append(commentary("translation-note-p5", tail))

    return {
        "id": "translation-note",
        "title": "How to Read the Translation",
        "subtitle": "Note Regarding This “Translation”",
        "segments": segs,
    }


# ---------------------------------------------------------------------------
# intro-parents (pdf pp.14-16)
# ---------------------------------------------------------------------------

def build_intro_parents():
    heads = ["Introduction for Parents, Mechanchim, and Mechanchos"]
    specs = [(14, heads, False), (15, heads, True), (16, heads, True)]
    text = flatten(specs)
    heading = "INTRODUCTION FOR PARENTS,\nMECHANCHIM, AND MECHANCHOS"
    assert text.startswith(heading)
    text = text[len(heading) :]

    cross_ref = "Introduction for Teens on page XVIII"
    text = text.replace(cross_ref, "", 1)

    body, amen, _leftover = take_trailing_hebrew(text, "And you will learn much in the process!")

    text = clean_hebrew_embeds(body)
    markers = [
        "It was Friday morning at a Torah Umesorah convention.",
        "Tefillah is the Achilles’ heel of chinuch",
        "Tefillah is “avodah she’ba’lev,”",
        "So how will this siddur help?",
        "Will this solve all",
    ]
    paras = split_at_markers(text, markers)
    segs = [commentary(f"intro-parents-p{i}", p) for i, p in enumerate(paras, 1)]
    segs.append(prayer("intro-parents-amen", clean_he_line(amen)))
    return {
        "id": "intro-parents",
        "title": "Introduction for Parents, Mechanchim, and Mechanchos",
        "segments": segs,
    }


# ---------------------------------------------------------------------------
# acknowledgments (pdf pp.11-13)
# ---------------------------------------------------------------------------

def build_acknowledgments():
    heads = ["Acknowledgments"]
    specs = [(11, heads, False), (12, heads, True), (13, heads, True)]
    text = flatten(specs)
    heading = "ACKNOWLEDGMENTS"
    assert text.startswith(heading)
    text = text[len(heading) :]
    body, amen, _leftover = take_trailing_hebrew(text, "even if the best thing for us right\nnow is a no.")
    body = re.sub(r"\s+", " ", body).strip()

    markers = [
        "If ever there were a situation",
        "Yet, to be honest, I struggle with that.",
        "Clearly, without the support, understanding, and binah",
        "“U’mi’talmidai yoser mi’kulam.”",
        "“Acharon acharon chaviv.”",
        "To all those who had a hand in taking this siddur",
    ]
    paras = split_at_markers(body, markers)
    segs = [commentary(f"acknowledgments-p{i}", p) for i, p in enumerate(paras, 1)]
    segs.append(prayer("acknowledgments-amen", clean_he_line(amen)))
    return {"id": "acknowledgments", "title": "Acknowledgments", "segments": segs}


# ---------------------------------------------------------------------------
# personal-notes (pdf pp.263-265, siddur pp.239-241 — corrects the brief's
# pp.263-264: the "For Teens" note continues onto pdf p.265 / siddur p.241)
# ---------------------------------------------------------------------------

def build_personal_notes():
    heads = ["A Personal Note"]
    p263 = strip_running_head(263, heads)  # leading "239 A Personal Note"
    p264 = strip_running_head(264, heads)  # leading "A Personal Note" + trailing folio "240"
    p265 = strip_running_head(265, heads)  # leading "241 A Personal Note", no trailing folio

    heading1 = "A PERSONAL NOTE\nFROM RABBI FEIGENBAUM FOR\nPARENTS, MECHANCHIM, AND\nMECHANCHOS"
    cross_ref = "Teens—see page 240 for YOUR personal note!"
    i = p263.index(heading1) + len(heading1)
    j = p263.index(cross_ref) + len(cross_ref)
    part1 = p263[j:]

    # The "For Parents" note continues from p263 onto the top of p264 before
    # the "For Teens" heading starts partway down that page.
    heading2 = "A PERSONAL NOTE FROM\nRABBI FEIGENBAUM FOR TEENS"
    k = p264.index(heading2)
    part2_before_h2 = p264[:k]
    part2_after_h2 = p264[k + len(heading2) :]

    full1 = re.sub(r"\s+", " ", "\n\n".join([part1, part2_before_h2])).strip()
    # The "For Teens" note continues past p264's end onto p265 in full — the
    # brief's pp.263-264 range is incomplete; see task-9-report.md.
    full2 = re.sub(r"\s+", " ", "\n\n".join([part2_after_h2, p265])).strip()

    markers1 = [
        "“Are you sure my kid/student should be reading this?",
        "Me too! I went to school in the",
        "I am basing myself on my unique area of expertise",
        "As Harav Wolbe, zt”l, would say",
        "Harav Aharon Feldman, shlita",
        "The opening essay",
        "Much hatzlachah!",
    ]
    paras1 = split_at_markers(full1, markers1)

    markers2 = [
        "I assume you read the introduction for the adults!",
        "1. As much as we all wish our daily experience",
        "2. Your questions must be honest questions",
        "3. These are all complex topics.",
        "Thanks for listening, and may you have much success",
    ]
    paras2 = split_at_markers(full2, markers2)

    segs = [header("personal-notes-h1", en_text="For Parents, Mechanchim, and Mechanchos")]
    for i, p in enumerate(paras1, 1):
        segs.append(commentary(f"personal-notes-parents-p{i}", p))
    segs.append(header("personal-notes-h2", en_text="For Teens"))
    for i, p in enumerate(paras2, 1):
        segs.append(commentary(f"personal-notes-teens-p{i}", p))

    return {
        "id": "personal-notes",
        "title": "A Personal Note from Rabbi Feigenbaum",
        "segments": segs,
    }


# ---------------------------------------------------------------------------
# dedications (pdf pp.7-8; pp.9-10 are blank filler in the print)
# ---------------------------------------------------------------------------

def build_dedications():
    p7 = strip_running_head(7, [], required=False)
    p8 = strip_running_head(8, [], required=False)

    def lines(page):
        return [l for l in page.split("\n")]

    l7 = lines(p7)

    def idx(hay, needle, start=0):
        return hay.index(needle, start)

    segs = []

    # -- title (Cohen Family Edition front page) -----------------------
    assert l7[0] == "The Cohen Family Edition"
    segs.append(prayer("dedications-title-he1", clean_he_line(l7[1])))
    segs.append(prayer("dedications-title-he2", clean_he_line(l7[2])))

    # -- Mrs. Gloria Cohen, may she rest in peace -------------------------
    i = idx(p7, "In loving memory of")
    j = idx(p7, "Mrs. Gloria Cohen")
    segs.append(rubric("dedications-cohen-caption", "In loving memory of"))
    he_name = clean_he_line(p7[i + len("In loving memory of") : j].strip())
    segs.append(prayer("dedications-cohen-name-he", he_name))

    # "Mrs. Gloria Cohen <trailing Hebrew honorific>" through the death-date line
    after_name = p7[j:]
    nl1 = after_name.index("\n")
    cohen_title_line = after_name[:nl1]
    cohen_title_en, cohen_title_he = cohen_title_line.split(" ‫", 1)
    cohen_title_he = clean_he_line(cohen_title_he)
    segs.append(commentary("dedications-cohen-name", f"**{cohen_title_en.strip()} {cohen_title_he}**"))

    rest = after_name[nl1 + 1 :]
    death_date_line, rest = rest.split("\n", 1)
    segs.append(prayer("dedications-cohen-date-he", clean_he_line(death_date_line)))
    place_line, rest = rest.split("\n", 1)
    assert place_line.strip() == "Thornhill, Canada"
    segs.append(commentary("dedications-cohen-place", "Thornhill, Canada"))

    bio_anchor = "dearly missed by all."
    bio_end = rest.index(bio_anchor) + len(bio_anchor)
    bio_block = rest[:bio_end].strip()
    bio_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", re.sub(r"\s+", " ", bio_block).strip())
    assert len(bio_sentences) == 5, f"expected 5 Cohen bio sentences, got {len(bio_sentences)}"
    for i, s in enumerate(bio_sentences, 1):
        segs.append(commentary(f"dedications-cohen-bio-{i}", s))

    # NOTE: the Isaiah 56:5 epigraph ("I will give them... a monument and a
    # name") that follows here in the print (the rest of `rest`, unused) is
    # a vocalized Hebrew line that pdftotext extracts corrupted (spurious
    # intra-word spaces) with no clean copy elsewhere in the corpus to slice
    # from. Per the task's documented fallback, it is OMITTED rather than
    # retyped — see docs/REVIEW_QUEUE.md.

    # -- Sara Goldman, may she rest in peace -------------------------------
    i = idx(p8, "In loving memory of")
    j = idx(p8, "Sara Goldman")
    segs.append(rubric("dedications-goldman-caption", "In loving memory of"))
    he_name = clean_he_line(p8[i + len("In loving memory of") : j].strip())
    segs.append(prayer("dedications-goldman-name-he", he_name))

    after_name = p8[j:]
    nl1 = after_name.index("\n")
    goldman_title_line = after_name[:nl1]
    goldman_title_en, goldman_title_he = goldman_title_line.split(" ‫", 1)
    goldman_title_he = clean_he_line(goldman_title_he)
    segs.append(commentary("dedications-goldman-name", f"**{goldman_title_en.strip()} {goldman_title_he}**"))

    rest = after_name[nl1 + 1 :]
    bio_end = rest.index("\n\n‫")
    bio_block = rest[:bio_end]
    segs.append(commentary("dedications-goldman-bio", re.sub(r"\s+", " ", bio_block).strip()))
    rest2 = rest[bio_end:].lstrip("\n")
    date_line = rest2.split("\n", 1)[0]
    segs.append(prayer("dedications-goldman-date-he", clean_he_line(date_line)))

    # -- Tobias tribute to HaRav Yitzchak Feigenbaum -----------------------
    i = idx(p8, "Li’chvod my Rosh Yeshiva")
    j = idx(p8, "HaRav Yitzchak Feigenbaum")
    segs.append(rubric("dedications-tobias-caption", "Li’chvod my Rosh Yeshiva"))
    rest = p8[j:]
    name_line, rest = rest.split("\n", 1)
    segs.append(commentary("dedications-tobias-name", f"**{name_line.strip()}**"))
    sign_i = rest.index("With much love and gratitude,")
    body_block = rest[:sign_i]
    segs.append(commentary("dedications-tobias-body", re.sub(r"\s+", " ", body_block).strip()))
    sign_block = rest[sign_i:]
    sign_line, sig_name = sign_block.split("\n", 1)
    assert sign_line.strip() == "With much love and gratitude,"
    segs.append(commentary("dedications-tobias-signoff", "With much love and gratitude,"))
    sig_name = sig_name.strip().split("\n")[0]
    segs.append(commentary("dedications-tobias-signature", f"**{sig_name}**"))

    # -- "and these shall stand for the blessing" (Hebrew dedication-page
    #    convention line) + the two-donor pair that follows it -------------
    i = idx(p8, "AVI AND ILANA TOBIAS") + len("AVI AND ILANA TOBIAS")
    j = idx(p8, "Mr. Mayer Rosenzweig")
    ve_eilu_block = p8[i:j]
    segs.append(prayer("dedications-veeilu-he", clean_he_line(ve_eilu_block)))
    rest = p8[j:]
    donor_lines = [l.strip() for l in rest.strip().split("\n") if l.strip()]
    assert donor_lines == ["Mr. Mayer Rosenzweig", "Mr. Josh Salmon"]
    for i, d in enumerate(donor_lines, 1):
        segs.append(commentary(f"dedications-donor-{i}", f"**{d}**"))

    return {"id": "dedications", "title": "Dedications", "subtitle": "The Cohen Family Edition", "segments": segs}


# ---------------------------------------------------------------------------

def main():
    pieces = [
        build_intro_teens(),
        build_translation_note(),
        build_intro_parents(),
        build_personal_notes(),
        build_dedications(),
        build_acknowledgments(),
    ]
    assert [p["id"] for p in pieces] == [
        "intro-teens",
        "translation-note",
        "intro-parents",
        "personal-notes",
        "dedications",
        "acknowledgments",
    ]
    # pdftotext leaves the print's discretionary soft-hyphen marks
    # (U+00AD, at hyphenation points like "ninth-\xadgrade") in hyphenated
    # words; strip them everywhere as a final formatting-artifact cleanup
    # (removes an invisible character, never a real letter).
    for p in pieces:
        assert p["segments"], f"empty piece {p['id']}"
        for s in p["segments"]:
            for field in ("enText", "heText"):
                if s.get(field):
                    s[field] = s[field].replace("\xad", "")
            assert s.get("enText") or s.get("heText"), f"empty segment {p['id']}/{s['id']}"

    with open("src/content/book-matter.json", "w", encoding="utf-8") as f:
        json.dump({"pieces": pieces}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    total = sum(len(p["segments"]) for p in pieces)
    print(f"wrote {len(pieces)} pieces, {total} segments")


if __name__ == "__main__":
    main()
