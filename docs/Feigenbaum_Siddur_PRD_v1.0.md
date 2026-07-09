# The Feigenbaum Weekday Siddur — Product Requirements Document

*Cohen Family Edition · Nusach Ashkenaz · Mosaica Press (2022)*
**Audience:** development & design team · **Status:** build-ready for v1 (planning phase — specify, do not deploy) · **Version:** 1.0 (consolidated)

---

## 0. How to use this document

This is the single source of truth for the build. **Phase 1 (v1)** sections are committed and ready to implement. **Phase 2 (v2)** sections are specified now so the architecture anticipates them, but are not built in v1. Where a requirement is tagged `[v2]`, capture its data hooks in v1 but do not implement the UI. A working HTML prototype of the Shemoneh Esrei reading experience accompanies this document and illustrates the intended look and interactions.

---

## 1. Product vision

A free, offline-first mobile app (iOS + Android, one codebase) delivering the complete weekday Feigenbaum Siddur with 100% textual fidelity, in a reading experience built for teens: pick a tefillah, scroll it continuously, choose whether you see Hebrew, the English explanation, or both, and surface Rabbi Feigenbaum's insights right where they're relevant. **Phase 1** is a faithful, navigable replica of the davening (the "Daven" experience) with onboarding and personalization. **Phase 2** turns it into a davening *companion* — audio, zmanim, location, calendar-aware flow, search, and a browsable "Learn" library.

---

## 2. Goals & non-goals

**Goals (v1)**
- Exact, proofed reproduction of the weekday liturgy and its English explanation.
- A reading experience that works fully offline and is comfortable morning and night.
- Personalization that a teen can set in under a minute and never think about again.
- An architecture that absorbs the v2 companion features without a rewrite.

**Non-goals (v1)**
- Accounts, cloud sync, social/sharing.
- Shabbos/Yom Tov davening (this is a *weekday* siddur).
- Monetization / in-app purchase plumbing (launch intent is free).
- The browsable Learn library, full-text search, audio, zmanim, calendar-aware flow — all `[v2]`.

---

## 3. Scope by phase

### 3.1 Phase 1 (v1) — committed
- **Content:** complete weekday liturgy with Hebrew + nikkud and the English explanation, for all services and standalone sections (see §6). Shacharis is built first.
- **Onboarding:** hybrid flow capturing default display, theme, Hebrew text size, comfort level (§8).
- **Daven navigation:** top-level list of services → continuous scroll within a service → jump-ToC (§5, §7).
- **Display:** user-selectable Hebrew-only / English-only / Both, persistent.
- **Personalization:** dark / night mode; adjustable Hebrew font size; highlights + personal notes stored **locally on device**.
- **Quick insights:** inline, expandable, where present.
- **Conditional liturgy:** shown statically with the print's Hebrew rubric labels.
- **Offline:** every v1 feature works with no network.

### 3.2 Deferred (easy, not committed)
- Bookmarks / "resume where I left off."

### 3.3 Phase 2 (v2) — specified, not built
- **Learn library:** browsable Introductions, FAQs, 12 Appendices, Glossary.
- **In-context jump-links:** the print's "See Appendix 9 / See the FAQs" cross-references become tappable (data captured in v1).
- **Full-text search** (Hebrew + English).
- **Calendar-aware automatic prayer flow** (correct text for the day).
- **Zmanim + location awareness.**
- **Professional / author audio recordings.**

### 3.4 Out of scope
Accounts, cloud sync, social/sharing, monetization, Shabbos/Yom Tov content.

---

## 4. Users

The audience is teens, at a range of Hebrew comfort. Onboarding asks a single comfort question and presets accordingly:

| Comfort level | Meaning |
|---|---|
| Beginner | Reads Hebrew slowly or leans on English to follow |
| Comfortable | Reads Hebrew but values the explanation alongside |
| Fluent | Davens in Hebrew, wants a clean Hebrew page |

No personal data leaves the device; no account is required at any point.

---

## 5. Information architecture

### 5.1 Two content kinds, addressed differently
- **Prayers** live inside a **service** (e.g., Shacharis). Select a service → continuous scroll → jump-ToC to move between prayers.
- **Commentary is not a destination.** The English explanation travels *with* its prayer and appears via the display toggle (Hebrew / Both / English). It is never browsed separately.
- **Reference material** (Introductions, FAQs, Appendices, Glossary) is browsable on its own in **Learn** `[v2]`, and is the target of in-context cross-references.

### 5.2 Navigation by phase
- **v1 ships "Daven" only:** a top-level list of services. **Shacharis is built first**; Minchah, Maariv, Birkas HaMazon and the rest follow the same template.
- **"Learn" ships in v2.** Commentary (display toggle) and inline quick insights are in v1; they belong to the prayer, not to Learn.

### 5.3 In-context cross-references
- **v1:** quick insights are inline and expandable. The data model **captures every FAQ/Appendix cross-reference**, but the tappable jump-links and the Learn library are **`[v2]`** so they activate with no re-digitization.
- *Open decision (§16):* alternatively surface referenced text as inline sheets in v1. Recommendation: defer to v2.

---

## 6. Content model & pipeline

> The content pipeline — not the app code — is the single largest cost, schedule, and risk driver. Plan for it to run in parallel with development from day one.

### 6.1 Source reality
We hold rights but only the **print PDF**, a typeset file mixing RTL Hebrew (with nikkud) and LTR English. Extracted text comes out scrambled and reversed. Content must be **rebuilt into clean, structured data**, not "extracted."

### 6.2 Data shape
`service → group → prayer → ordered segments`. Each segment is typed and may carry conditions and cross-references:
- **Segment types:** `prayer` (Hebrew liturgical text) · `commentary` (English explanation) · `rubric` (instructional label, e.g., "on days when…") · `insight` (quick insight) · `frontmatter` `[v2]` · `faq` `[v2]` · `appendix` `[v2]` · `glossary` `[v2]`.
- **`condition`** (optional): e.g., `winter`, `rosh_chodesh`, `taanis`, `chol_hamoed`. Displayed statically with rubric labels in v1; switched to automatic logic in v2 with no re-digitization.
- **`xref`** (optional): `faq:#`, `appendix:#`. Captured in v1; navigable in v2.

The same content tree renders all three display modes (Hebrew / English / Both).

### 6.3 Pipeline stages
1. **Digitization** — re-key / OCR + reconstruct Hebrew (correct nikkud) and English; expect manual correction to dominate.
2. **Structuring** — apply the §6.2 schema, including conditions and cross-references.
3. **Proofing & sign-off** — author/halachic review loop: **Rabbi Feigenbaum + a designated rav/proofreader**. No real text ships unproofed. Provide a structured side-by-side proofing tool so corrections are tracked.
4. **Packaging** — compile signed-off content into the app's bundled, versioned dataset.

**Recommendation:** digitize and proof **one self-contained pilot section first** (e.g., Birkas HaMazon) to calibrate effort before committing to the whole siddur. The accompanying prototype uses public-domain liturgy + clearly-labeled placeholder English precisely so UX work is never blocked on this pipeline.

---

## 7. Shacharis section spec (build first)

The print runs Shacharis linearly from p.2–117 (the "Shacharis" running header spans the whole range). v1 preserves that exact order for continuous scroll, grouped into seven navigational "movements" for the jump-ToC. **Shacharis is implemented end-to-end first because it establishes the data shape, renderer, jump-ToC, rubric handling, and insight pattern reused by every other service.**

### 7.1 Clean ToC (exact order, grouped)

| Group | Prayer | Hebrew | Page anchor |
|---|---|---|---|
| **1 · Waking & morning brachos** | Hashkamas HaBoker | השכמת הבוקר | 2 |
| | Birchos HaShachar | ברכות השחר | 10 |
| | Korbanos *(within Birchos HaShachar)* | קרבנות | ~23 |
| **2 · Pesukei D'Zimrah** | Pesukei D'Zimrah | פסוקי דזמרה | 29 |
| **3 · Shema & its brachos** | Barchu | ברכו | 50 |
| | Birchos Krias Shema | קריאת שמע וברכותיה | 51 |
| **4 · Shemoneh Esrei** | Shemoneh Esrei | שמנה עשרה | 60 |
| **5 · Tachanun & supplications** | Avinu Malkeinu | אבינו מלכנו | 78 |
| | Tachanun | תחנון | 83 |
| **6 · Krias HaTorah** | Seder Krias HaTorah | סדר קריאת התורה | 91 |
| **7 · Concluding** | Aleinu | עלינו | 105 |
| | Shir shel Yom | שיר של יום | 107 |
| | Barchi Nafshi | ברכי נפשי | 109 |
| | L'Dovid Hashem Ori | לדוד ה' אורי | 111 |
| | Pitum HaKetores | פטום הקטורת | 113 |
| | Shesh Zechiros | שש זכירות | 116 |
| | Shloshah Asar Ikarim | שלשה עשר עיקרים | 117 |

*Page anchors map to the print master for proofing only; they are not shown in the reflowable app.*

### 7.2 Behavior
- **Continuous scroll** through the whole service in the order above; jump-ToC scrolls to any group or prayer.
- **Display toggle** (Hebrew / Both / English) persists and applies throughout the service.
- **Conditional liturgy** shown statically with the print's Hebrew rubric labels — e.g., the winter insert in Gevuros, Avinu Malkeinu's day-rules, Tachanun's omission days, Korbanos variants.
- **Quick insights** inline and expandable where present.
- **Cross-references** captured in data; jump-links `[v2]`.

### 7.3 Other services (same template, after Shacharis)
Minchah (מנחה), Maariv (מעריב) incl. Maariv Motzaei Shabbos, Birkas HaMazon (ברכת המזון), Al HaMichyah / Borei Nefashos, Tefillas HaDerech, Krias Shema al HaMitah, Sefiras HaOmer, Hallel, Netilas Lulav. Each reuses §7 patterns; ToCs to be transcribed from the print during digitization.

---

## 8. Onboarding spec

**Pattern:** Hybrid — one comfort question presets sensible defaults, then a review/confirm screen with live preview. First-launch only, fully offline, stored locally, re-runnable from Settings.

### 8.1 Flow
1. **Welcome** — one warm screen in the siddur's voice; a "Let's set it up" action and a quiet "Use defaults" skip.
2. **Comfort question** — "How's your Hebrew davening right now?" with three choices, each with a one-line description.
3. **Review & confirm** — presets shown as editable controls (display segmented control, theme, Hebrew text size) above a **live preview** of one Hebrew line + its English. Copy: "You can change any of this anytime in Settings."
4. **Done** — lands in **Daven → Shacharis**.

### 8.2 Settings captured
- **Default display:** Hebrew / English / Both
- **Theme:** Light / Dark / Auto (follow system)
- **Hebrew text size:** preset scale
- **Comfort level:** Beginner / Comfortable / Fluent (informs suggestions; not a hard rule after the review screen)

### 8.3 Comfort-level → preset mapping (all overridable on the review screen)

| Comfort level | Default display | Hebrew text size | Theme |
|---|---|---|---|
| Beginner | Both | Large | Auto |
| Comfortable | Both | Default | Auto |
| Fluent | Hebrew only | Default | Auto |

*Rationale:* beginners see Hebrew and English together at a larger size to build familiarity with support; fluent readers get a clean Hebrew-only page. Theme defaults to Auto until the person chooses.

### 8.4 Requirements
- First-launch only; never blocks a returning user.
- Fully functional offline.
- All choices persist locally; no account, no PII.
- Re-runnable / resettable from Settings; every value individually editable there.
- Accessibility: large tap targets, skippable, visible focus, reduced-motion respected.

---

## 9. Functional requirements (consolidated)

| # | Requirement | Phase |
|---|---|---|
| F1 | "Daven" home lists all services with rapid jump. | v1 |
| F2 | Jump-ToC per service (the §7.1 groups); tap to scroll to any prayer. | v1 |
| F3 | Continuous vertical scroll within a selected service. | v1 |
| F4 | Three-way display toggle: Hebrew / Both / English, persistent. | v1 |
| F5 | Hebrew renders with correct nikkud and RTL; English renders LTR. | v1 |
| F6 | Adjustable Hebrew (and proportionally English) font size. | v1 |
| F7 | Dark / night mode (plus Auto). | v1 |
| F8 | Quick-insight markers expand/collapse inline. | v1 |
| F9 | FAQ / appendix in-context jump-links (data captured in v1). | **v2** |
| F10 | Highlight a passage; highlights persist locally. | v1 |
| F11 | Attach a personal note to a passage; notes persist locally. | v1 |
| F12 | Conditional liturgy shown with the print's Hebrew rubric labels. | v1 |
| F13 | App functions in airplane mode on first launch after install. | v1 |
| F14 | Onboarding flow (hybrid; §8). | v1 |
| F15 | Settings screen: display, theme, text size, reset; all editable. | v1 |
| F16 | Browsable Learn library (Intros, FAQs, Appendices, Glossary). | **v2** |
| F17 | Full-text search (Hebrew + English). | **v2** |
| F18 | Calendar-aware automatic prayer flow. | **v2** |
| F19 | Zmanim + location awareness. | **v2** |
| F20 | Audio playback of recorded tefillos. | **v2** |

---

## 10. Non-functional requirements
- **Offline-first:** no v1 feature requires connectivity.
- **Performance:** instant service open; smooth scroll on mid-range devices (virtualize long services).
- **Accessibility:** large-type support, sufficient contrast in both themes, visible focus, reduced-motion respected.
- **Hebrew / RTL correctness:** nikkud positioning verified on physical iOS + Android devices across font sizes — the top technical risk; test early.
- **Content integrity:** shipped text matches the signed-off master exactly; content is versioned.
- **Respect for the sefer:** dignified handling; guard against accidental destructive gestures on text; treat Sheimos appropriately in any future share/export (`[v2]`).
- **Privacy:** no data collection; local-only storage; trivial app-store privacy labels.

---

## 11. Design direction

For the design team. The identity steers away from generic defaults toward a calm **dawn-to-morning** feel appropriate to a weekday siddur centered on Shacharis.
- **Palette:** warm parchment light mode and a deep ink-blue dark mode, both keyed to a *tekhelet*-leaning indigo accent (not the common terracotta), with a warm gold reserved for highlights and a muted clay for instructional rubrics.
- **Typography:** **Frank Ruhl Libre** for Hebrew — an open-licensed, sefer-grade face with proper nikkud (fallbacks: David Libre, Times New Roman). A warm serif (e.g., Newsreader) for the English commentary so the two voices read as distinct; a clean grotesque (e.g., Inter) for UI.
- **Signature:** the reading experience itself — the seamless Hebrew/Both/English toggle and the in-place highlight/note interaction.
- A working HTML prototype accompanies this PRD and demonstrates the above on the Shemoneh Esrei.

---

## 12. Technical architecture
- **Client:** cross-platform, one codebase. **React Native (+ Expo) recommended** for text-heavy RTL + custom typography and talent availability; Flutter is a viable alternative.
- **Content store (on device):** versioned, read-only bundled dataset (SQLite or indexed structured JSON). Enables fast jumps, future search (`[v2]`), and content updates via app-store releases — no backend.
- **User data (local only):** highlights, notes, and preferences in on-device storage. No accounts, no servers, no PII off-device (which also removes minor-privacy/COPPA exposure for v1).
- **Rendering layer (the heart of the app):** correct RTL Hebrew with nikkud; a display-mode engine driven by the §6.2 tags (one tree, three views); virtualized continuous scroll; in-context insight toggles; global type-scale and theme.
- **No backend in v1.** v2 adds an on-device zmanim/calendar engine, a local search index, and audio assets (bundled or streamed) — none require a server.

---

## 13. Build plan & milestones

**Track A — Content (parallel, longest pole):** pilot section digitized → schema finalized → proofing tool + author/rav loop → full digitization → full sign-off → packaged dataset.

**Track B — App:**
- **M0 — Prototype (done):** Shemoneh Esrei reading experience (accompanies this PRD).
- **M1 — Reading core:** content data model + renderer + three-way display + nikkud verified on devices.
- **M2 — Shacharis end-to-end:** the full §7 service — jump-ToC, continuous scroll, rubrics, insights. Sets the template.
- **M3 — Personalization:** highlights, notes, font size, theme, local persistence.
- **M4 — Onboarding & settings:** hybrid onboarding (§8) + settings screen.
- **M5 — Remaining services:** Minchah, Maariv, Birkas HaMazon, etc. on the Shacharis template.
- **M6 — Content integration & QA:** load signed-off data; full device QA.
- **M7 — Store readiness:** icons, listings, privacy labels (trivial — no data collected), beta (TestFlight / Play internal), launch.

**v2 (post-launch):** Learn library + cross-reference links → search → calendar-aware flow → zmanim/location → audio.

---

## 14. Effort & cost estimates

Effort in engineer-weeks for one experienced React Native developer; ranges reflect unknowns (chiefly nikkud rendering and content volume).

| Item | Estimate |
|---|---|
| M1 Reading core (incl. nikkud device testing) | 3–5 wks |
| M2 Shacharis end-to-end | 2–3 wks |
| M3 Personalization (local) | 2–3 wks |
| M4 Onboarding & settings | 1–2 wks |
| M5 Remaining services | 3–5 wks |
| M6 Content integration & QA | 2–3 wks |
| M7 Store readiness + launch | 1–2 wks |
| **App subtotal (v1)** | **~14–23 wks** |
| Content digitization + tagging + proofing | **Largest variable** — scope via the pilot; plan months, parallel to app |

**Hard cash line items (not labor):** Apple Developer ($99/yr) + Google Play ($25 one-time); Hebrew font license (Frank Ruhl Libre is open — likely $0); content re-keying/OCR + proofreader time; `[v2]` audio production.

---

## 15. Risks & mitigations

| Risk | Mitigation |
|---|---|
| **Nikkud rendering** breaks on some devices/sizes | Proven nikkud font; verify on real devices in M1 before building further. |
| **Content fidelity errors** in a siddur (serious) | Structured proofing tool + author + rav sign-off gate; no real text ships unproofed; versioned master. |
| **Content pipeline underestimated** | Start now, in parallel; pilot one section to calibrate before committing to the whole. |
| **Conditional-liturgy complexity** creeping into v1 | Static rubric labels in v1; dynamic logic is v2, but tag conditions in data now. |
| **Copyright** (commentary is the author's/Mosaica's) | Prototype uses public-domain liturgy + placeholder English; confirm rights cover digital distribution; store the agreement. |
| Scope creep from v2 | Architecture anticipates v2 (tagged data, on-device store, captured cross-refs) so features bolt on without rework. |

---

## 16. Open decisions
1. Confirm the **rights agreement** explicitly covers a free digital app on the app stores.
2. Confirm **FAQ/Appendix jump-links deferred to v2** (recommended) vs. inline expandable sheets in v1.
3. Confirm the **comfort-level → preset mapping** (§8.3), esp. Beginner = Both vs. English-forward.
4. Confirm the onboarding **"Use defaults" skip** path.
5. Confirm **React Native** over Flutter.
6. Confirm **Frank Ruhl Libre** as the Hebrew face.
7. Pick the **pilot digitization section** (suggest Birkas HaMazon).
8. Confirm **bookmarks/resume** stay deferred.
9. Stand up the **proofing workflow** and confirm author + rav cadence.

---

## 17. Glossary of project terms
- **Service:** a complete tefillah container (Shacharis, Minchah, Maariv) or standalone unit (Birkas HaMazon).
- **Group / movement:** a navigational cluster of prayers within a service (see §7.1).
- **Segment:** the atomic tagged unit of content (prayer / commentary / rubric / insight).
- **Rubric:** an instructional label from the print ("in winter add…").
- **Cross-reference (xref):** a link from a prayer to a FAQ or Appendix.
- **Daven / Learn:** the davening experience (v1) and the browsable reference library (v2).

---

*A working HTML prototype of the Shemoneh Esrei reading experience accompanies this PRD. It uses standard public-domain liturgical Hebrew and clearly-labeled placeholder English; the published Feigenbaum commentary awaits digitization and author/rav proofing.*
