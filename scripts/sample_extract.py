"""
Sample extraction: Birchos Hashachar (siddur pp. 11–18 = PDF pp. 35–42)
Renders pages to PNG, sends to Claude, outputs annotated JSON.
Run: python3 scripts/sample_extract.py
"""

import os, json, base64
from pdf2image import convert_from_path
import anthropic

PDF_PATH = "feigenbaum-siddur-original.pdf"
OUT_DIR = "scripts/sample_output"
# PDF pages 35-42 = siddur pages 11-18 (Birchos Hashachar)
# Adjust if offset differs — we'll see from filenames
FIRST_PDF_PAGE = 35
LAST_PDF_PAGE  = 42

PROMPT = """You are digitizing the Feigenbaum Weekday Teen Siddur for a mobile app.
Your job: read this siddur page image and extract every distinct content block into a structured JSON array.

## Segment types
Classify each block as ONE of these types:

- "prayer"        Hebrew liturgical text (with or without nikkud). Large Hebrew font, RTL.
                  ALWAYS copy the Hebrew exactly, including nikkud and all vowel marks.

- "commentary"    English explanation — either (a) the left-column word-by-word gloss
                  that runs alongside a prayer, or (b) a paragraph of English explanation
                  below or near a Hebrew block. Copy verbatim.

- "rubric"        Instructional label — typically italic centered text like
                  "Brachah before putting on tallis:", "For women:", "After putting on the tallis:",
                  "Some say all, some say some, some say none", etc.
                  Copy verbatim.

- "insight"       "Instant Insight" callouts — a pill label followed by indented text.
                  Copy verbatim including the insight text, NOT the "Instant Insight" label itself.

- "faq"           Right- or left-margin FAQ/ANSWER boxes.
                  Format as: "FAQ: [question text] ANSWER: [answer text]"

- "summary"       "TO SUMMARIZE" blocks — brief bulleted or paragraph summaries.
                  Copy verbatim.

- "section_intro" Bold introductory English paragraphs that appear BEFORE a prayer group
                  (not a rubric, not a commentary — standalone preamble). Copy verbatim.

- "header"        Section title/heading text (e.g. "But First—Fifteen Thank-Yous!",
                  "ברכות השחר", "Now I'm Ready to Daven"). Both Hebrew and English.

## Rules
1. Preserve order top-to-bottom as they appear on the page.
2. For "prayer" segments: put the Hebrew in "heText". Never translate or paraphrase it.
3. For all other segments: put the text in "enText". If the segment contains Hebrew words
   mixed into English (like transliterated terms or inline Hebrew), include them as-is.
4. Skip page headers/footers (running headers like "Shacharis • Birchos Ha'shachar",
   page numbers).
5. If a prayer block and its left-column word-by-word gloss appear side-by-side,
   output them as TWO separate segments in order: prayer first, then commentary.
6. For "For men:" / "For women:" variants on the same page, output each as its own
   prayer segment preceded by a rubric segment.
7. Assign a short, stable, snake_case id to each segment based on content
   (e.g. "bracha_bikurim_1", "bracha_bikurim_commentary", "rubric_for_women").

## Output format
Return ONLY a valid JSON array — no markdown fences, no explanation:
[
  {
    "id": "string",
    "type": "prayer|commentary|rubric|insight|faq|summary|section_intro|header",
    "heText": "Hebrew text if type is prayer (omit otherwise)",
    "enText": "English/mixed text for all other types (omit for prayer)"
  },
  ...
]
"""

def image_to_b64(img):
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode()

def extract_page(client, img, page_num):
    b64 = image_to_b64(img)
    resp = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": b64,
                    }
                },
                {
                    "type": "text",
                    "text": PROMPT
                }
            ]
        }]
    )
    raw = resp.content[0].text.strip()
    # Strip any accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    try:
        segments = json.loads(raw)
        return segments
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON parse error on page {page_num}: {e}")
        print(f"  Raw: {raw[:200]}")
        return []

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY environment variable")

    client = anthropic.Anthropic(api_key=api_key)

    print(f"Rendering PDF pages {FIRST_PDF_PAGE}–{LAST_PDF_PAGE} at 200 DPI…")
    images = convert_from_path(
        PDF_PATH,
        dpi=200,
        first_page=FIRST_PDF_PAGE,
        last_page=LAST_PDF_PAGE,
    )
    print(f"  Got {len(images)} pages.")

    all_results = {}
    for i, img in enumerate(images):
        pdf_page = FIRST_PDF_PAGE + i
        print(f"Extracting PDF page {pdf_page}…")
        segments = extract_page(client, img, pdf_page)
        print(f"  → {len(segments)} segments")
        all_results[f"pdf_page_{pdf_page}"] = segments

        # Save per-page PNG for inspection
        img.save(f"{OUT_DIR}/page_{pdf_page:03d}.png")
        # Save per-page JSON
        with open(f"{OUT_DIR}/page_{pdf_page:03d}.json", "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

    # Save combined output
    combined_path = f"{OUT_DIR}/sample_combined.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Output in {OUT_DIR}/")
    print(f"Combined: {combined_path}")
    total = sum(len(v) for v in all_results.values())
    print(f"Total segments extracted: {total}")

if __name__ == "__main__":
    main()
