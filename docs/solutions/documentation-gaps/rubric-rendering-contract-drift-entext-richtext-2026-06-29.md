---
title: "Rubric rendering-contract drift: enText became RichText but docs and linter still said plain text"
date: 2026-06-29
category: documentation-gaps
module: segment-rendering-contract
problem_type: documentation_gap
component: documentation
severity: high
applies_when:
  - "Changing what any segment type renders in src/components/SegmentRenderer.tsx"
  - "Adding a new segment type or changing which field of a type renders"
  - "Adding inline-link or markdown capability to a RichText-rendered field"
  - "Editing the CLAUDE.md segment-type table or docs/CONTENT_GUIDE.md"
tags:
  - segment-renderer
  - rendering-contract
  - rubric
  - richtext
  - content-linter
  - documentation-drift
  - contract-sync
  - digital-siddur
---

# Rubric rendering-contract drift: enText became RichText but docs and linter still said plain text

## Context

This app's rendering contract — which field each segment `type` actually draws — is **duplicated across four surfaces** that have no automatic cross-check:

1. `src/components/SegmentRenderer.tsx` — the implementation (the running truth)
2. the `CLAUDE.md` segment-type table — the summary agents read
3. `docs/CONTENT_GUIDE.md` — the source of truth for human editors
4. `scripts/lint_content.py` — the machine-enforced encoding (runs in the pre-commit gate)

`CLAUDE.md` carries an explicit mandate: *"If you change a rendering rule in `SegmentRenderer.tsx`, update the guide and the linter together."*

The `rubric` type silently drifted out of sync. Timeline (reconstructed from git, since no prior sessions exist) *(session history)*:

- **Jun 18** (`f662b67`) — `lint_content.py` introduced. At that point rubric `enText` rendered as plain `<Text>`, so `RICHTEXT_TYPES = {'commentary','insight','faq','section_intro','transition'}` (no `rubric`) and a "rubric contains `*`" error were both *accurate*.
- **Jun 23** (`b5d0a82`) — RichText gained `[label](section:key)` inline links, and rubric `enText` started rendering through `RichText` to carry `Appendix N` / `section:` references. **The contract changed here; the docs and linter were not co-updated.** Drift began.
- **Jun 29** (`536c243`) — a code review caught it as two P0 "contract drift" findings. By then 32 instructional rubrics depended on RichText (e.g. `"On Shabbos add the following: (If you forgot, see Appendix 12:8)"` and `se4-tachanun-xref-rubric`: `[Tachanun](prayer:shacharit/p-tachanun); [Avinu Malkeinu](prayer:shacharit/avinu-malkeinu)`), yet CLAUDE.md and CONTENT_GUIDE.md still said rubrics are "plain text, NOT markdown" and the linter errored on any `*` in a rubric and excluded rubric `enText` from its balanced-markdown check.

## Guidance

**The rendering contract lives in four places — move all four together when a type's rendering changes.** The pre-commit linter catches *linter-vs-data* mismatches, but nothing catches *linter-vs-renderer* drift; that requires human awareness of the four-surface rule.

**Rubric has per-field rules, not one per-type rule:**

- `rubric.heText` → plain `<Text>`. A literal `*` shows as an asterisk on screen, so keep markdown out of `heText`.
- `rubric.enText` → `RichText` (same pipeline as `commentary`/`insight`/`faq`): `**bold**`, `*italic*`, `Appendix N` / `Appendix N:M` auto-links, `[label](section:key)`, and `[label](prayer:serviceId/prayerId)` deep-links.

Encode this in the linter as a **per-field** rule. Keep `rubric` *out of* the `RICHTEXT_TYPES` set and handle it with an `or t == 'rubric'` guard — adding it to the set would wrongly imply rubric `heText` is also RichText, obscuring the opposite-rules-per-field distinction:

```python
# Before (drifted — scoped to the whole type, both fields):
if t == 'rubric' and ('*' in he or '*' in en):
    findings["rubric contains '*' (renders literally)"].append(loc)

if t in RICHTEXT_TYPES and en:
    if en.count('**') % 2 or en.replace('**', '').count('*') % 2:
        findings['unbalanced markdown markers'].append(loc)

# After (correct — heText keeps the literal-'*' rule; enText joins the markdown check):
# rubric.heText draws as plain <Text> (so '*' shows literally); rubric.enText
# draws via RichText (markdown + section:/prayer:/Appendix links), like commentary.
if t == 'rubric' and '*' in he:
    findings["rubric.heText contains '*' (renders literally)"].append(loc)

if (t in RICHTEXT_TYPES or t == 'rubric') and en:
    if en.count('**') % 2 or en.replace('**', '').count('*') % 2:
        findings['unbalanced markdown markers'].append(loc)
```

## Why This Matters

Content fidelity is this project's highest-stakes risk — no liturgical text ships without human/rav sign-off — so a silently-drifted contract is dangerous in three ways:

- **False errors:** the linter rejects valid `enText` markdown/links, blocking commits or pushing an editor to strip formatting the renderer actually supports.
- **False passes:** a linter blind to rubric `enText` lets unbalanced markdown reach users.
- **Misleading docs:** future agents and editors read "plain text" in the tables and author rubric `enText` without the Appendix/prayer links the renderer would have rendered.

The pre-commit gate runs `lint_content.py --strict`, but it can only compare the linter against the *content*, never against the *renderer* — which is exactly why the four-surface co-update has to be a conscious habit, not a thing the tooling can enforce *(auto memory: linter + pre-commit gate is the contract's enforcement layer)*.

## When to Apply

Whenever you touch a type's branch in `SegmentRenderer.tsx`, ask: does any field now render differently than the CLAUDE.md table, the CONTENT_GUIDE.md table, and the linter checks currently say? If yes, update all four before committing.

## Examples

**The actual renderer contract** (`SegmentRenderer.tsx`, rubric branch) — `heText` always takes the plain `<Text>` path, `enText` always takes the `RichText` path, in both the bilingual and single-field cases:

```tsx
if (segment.type === 'rubric') {
  if (segment.heText && segment.enText) {
    if (displayMode === 'en') {
      return <RichText text={segment.enText} style={s.rubricEn} linkStyle={s.linkSpan} />;
    }
    return <Text style={s.rubricHe}>{segment.heText}</Text>;
  }
  if (segment.heText && displayMode === 'en') return null;
  if (segment.enText && displayMode === 'he') return null;
  if (segment.heText) return <Text style={s.rubricHe}>{segment.heText}</Text>;
  return <RichText text={segment.enText ?? ''} style={s.rubricEn} linkStyle={s.linkSpan} />;
}
```

**The link schemes that justify rubric `enText` being RichText** (`RichText.tsx`):

```ts
const APPENDIX_RE = /(Appendix\s+\d+(?::\d+)?)/g;            // "Appendix 12:8" auto-links
const INLINE_LINK_RE = /(\[[^\]]+\]\((?:section|prayer):[^)]+\))/g;  // [label](section:…|prayer:…)
```

**Corrected contract docs** (so the four surfaces agree):

```
# CLAUDE.md table row
| `rubric` | `heText` plain text (`*` literal) in he/both; else `enText` via **RichText** (markdown + links) in en | the other field |

# CONTENT_GUIDE.md — new convention 8 (inline links, RichText fields only)
8. Appendix N / Appendix N:M auto-linkify; [label](section:key) opens the section modal;
   [label](prayer:serviceId/prayerId) jumps to that prayer in that service.
```

## Related

- `docs/REVIEW_QUEUE.md` → "Code-review deferred items (2026-06-29)" — the incident record this learning formalizes.
- `CLAUDE.md` → the "update the guide and the linter together" rule (the mandate that was violated).
- `docs/CONTENT_GUIDE.md` → conventions 5 (rubric heText/enText split) and 8 (inline-link schemes).
