# Home Page Reorg + Book Matter Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the home screen as the approved "Variant A" grouped layout with a now-card shell, and bring the book's non-prayer matter in-app (About this Siddur + browsable Glossary), per `docs/superpowers/specs/2026-07-02-home-page-reorg-design.md`.

**Architecture:** Static category map drives a SectionList home screen; a NowCard shows civil + Hebrew date (hand-rolled converter — no new deps) and a resume link from the existing reading-position store. Book matter and glossary are new content JSONs digitized from the print PDF via deterministic Python scripts, rendered by new stack screens that reuse the appendix prose renderer (extracted into a shared component).

**Tech Stack:** Expo SDK 56 / RN 0.85 / Expo Router v4, Zustand + AsyncStorage, jest-expo, Python content scripts, pdftotext/pdftoppm.

## Global Constraints

- The print PDF `feigenbaum-siddur-original.pdf` is the **sole content authority**; `pdf_page = siddur_page + 24`; locate sections via the TOC (pdf pp. 5–6).
- Content JSON is edited **only via deterministic Python scripts in `scripts/`** that assert their targets exist. Derive Hebrew by slicing extracted text — never retype (nikud loss).
- All digitized content must be **proofed against 300 DPI page renders** before its task is committed; new JSON must pass `python3 scripts/lint_content.py --strict` (the pre-commit hook runs it).
- Run `npm run check` (typecheck + strict lint + jest) before every commit.
- **No GPL/LGPL dependencies.** The app bundles copyrighted book content that can never be open-sourced, so `@hebcal/core` (GPL-2.0) and `kosher-zmanim` (LGPL-3.0) are prohibited. (This is why the Hebrew-date converter is hand-rolled and why future zmanim use Hebcal's hosted REST API.)
- This project is on Expo SDK 56 — check https://docs.expo.dev/versions/v56.0.0/ before using Expo APIs from memory.
- Zmanim, location, suggested-service logic, and Today badges are **out of scope** (planned only — see "Future Round" section at the end).

---

### Task 1: Amend the spec's calendar-library decision (licensing)

The spec currently selects `@hebcal/core` for the Hebrew date. `npm view @hebcal/core license` → **GPL-2.0** (`@hebcal/hdate` likewise; `kosher-zmanim` is LGPL-3.0). The app cannot take a GPL dependency (bundled copyrighted content; App Store GPL friction). Replace with: hand-rolled Hebrew-date converter this round; Hebcal hosted REST API (free, keyless, CC-BY 4.0) for the future zmanim round.

**Files:**
- Modify: `docs/superpowers/specs/2026-07-02-home-page-reorg-design.md`

- [ ] **Step 1: Edit the spec's Data section**

Replace the bullet beginning `**Hebrew date:** add \`@hebcal/core\`` with:

```markdown
- **Hebrew date:** hand-rolled converter in `src/lib/hebrewDate.ts` (Dershowitz–Reingold
  algorithm, ~100 lines, tested against Hebcal converter-API reference values). We cannot
  bundle `@hebcal/core` (GPL-2.0) or `kosher-zmanim` (LGPL-3.0): the app ships copyrighted
  book content that can never be open-sourced. `Intl` Hebrew-calendar support on Hermes is
  unverifiable in jest, so it is not an option either.
```

In the "Future plan" section, replace the two `@hebcal/core` mentions with:

```markdown
- **Zmanim source:** Hebcal hosted Zmanim REST API — free, no API key, JSON, batch up to
  180 days (`https://www.hebcal.com/zmanim?cfg=json&latitude=..&longitude=..&tzid=..&start=..&end=..`).
  Output is CC-BY 4.0: the app must credit Hebcal.com (Settings/About line). Offline-first:
  prefetch a 30-day batch when online, cache in AsyncStorage, render from cache; no
  cache + no network → strip hidden. Suggested-service rules run on the same cached data
  plus the local Hebrew-date converter.
```

- [ ] **Step 2: Simplify the resume-line decision to its fallback**

In the spec's Data section, replace the `**Resume line:**` bullet with:

```markdown
- **Resume line:** service-only — "Resume Shacharis →" from a new persisted
  `lastServiceId` in the reading-position store (the offset restore already
  works on open). Prayer-level naming ("…at Ashrei") needs a viewability
  callback through FlashList and is deferred as polish.
```

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-07-02-home-page-reorg-design.md
git commit -m "docs: spec amendment — no GPL calendar deps; Hebcal REST API for future zmanim"
```

---

### Task 2: Hebrew date utility (`src/lib/hebrewDate.ts`)

**Files:**
- Create: `src/lib/hebrewDate.ts`
- Test: `src/lib/__tests__/hebrewDate.test.ts`

**Interfaces:**
- Produces: `fromGregorian(date: Date): HebrewDate`; `formatHebrewDate(h: HebrewDate): string` (e.g. `י״ז תמוז תשפ״ו`); `formatEnDate(date: Date): string` (e.g. `Thursday · July 2`); `gematriya(n: number): string`. `HebrewDate = { year: number; month: number; day: number }` with Dershowitz–Reingold month numbering (1 = Nisan … 7 = Tishrei … 12 = Adar/Adar I, 13 = Adar II).

- [ ] **Step 1: Fetch reference conversion values**

```bash
curl -s "https://www.hebcal.com/converter?cfg=json&gy=2026&gm=7&gd=2&g2h=1"
curl -s "https://www.hebcal.com/converter?cfg=json&gy=2027&gm=3&gd=20&g2h=1"
```

Record the returned `hy`/`hm`/`hd` for each. Expected: 2026-07-02 → 17 Tamuz 5786; 2027-03-20 → a date in Adar II 5787 (5787 is a leap year). If the API returns different values, **the API is right** — use its values in the tests below.

- [ ] **Step 2: Write the failing tests**

```ts
// src/lib/__tests__/hebrewDate.test.ts
import { fromGregorian, formatHebrewDate, formatEnDate, gematriya } from '../hebrewDate';

// Reference values cross-checked against the Hebcal converter API (Step 1).
test('Rosh Hashanah 5786 — 2025-09-23 is 1 Tishrei 5786', () => {
  expect(fromGregorian(new Date(2025, 8, 23))).toEqual({ year: 5786, month: 7, day: 1 });
});

test('Rosh Hashanah 5787 — 2026-09-12 is 1 Tishrei 5787', () => {
  expect(fromGregorian(new Date(2026, 8, 12))).toEqual({ year: 5787, month: 7, day: 1 });
});

test('day before Rosh Hashanah — 2025-09-22 is 29 Elul 5785', () => {
  expect(fromGregorian(new Date(2025, 8, 22))).toEqual({ year: 5785, month: 6, day: 29 });
});

test('2026-07-02 matches the Hebcal converter (17 Tammuz 5786)', () => {
  expect(fromGregorian(new Date(2026, 6, 2))).toEqual({ year: 5786, month: 4, day: 17 });
});

test('leap-year date lands in Adar II (month 13) per the Hebcal converter', () => {
  // Replace day with the Step 1 API value if it differs.
  const h = fromGregorian(new Date(2027, 2, 20));
  expect(h.year).toBe(5787);
  expect(h.month).toBe(13);
});

test('round-trips across a full Hebrew year', () => {
  // Walk 2025-09-23 … 2026-09-12 day by day; the Hebrew date must advance
  // by exactly one day each step (catches month-length errors).
  let prev = fromGregorian(new Date(2025, 8, 23));
  for (let t = new Date(2025, 8, 24); t <= new Date(2026, 8, 12); t.setDate(t.getDate() + 1)) {
    const cur = fromGregorian(new Date(t));
    const sameMonth = cur.year === prev.year && cur.month === prev.month && cur.day === prev.day + 1;
    const newMonth = cur.day === 1 && !(cur.year === prev.year && cur.month === prev.month);
    expect(sameMonth || newMonth).toBe(true);
    prev = cur;
  }
});

test('gematriya renders 15/16 as ט״ו/ט״ז and years correctly', () => {
  expect(gematriya(15)).toBe('ט״ו');
  expect(gematriya(16)).toBe('ט״ז');
  expect(gematriya(17)).toBe('י״ז');
  expect(gematriya(5)).toBe('ה׳');
  expect(gematriya(786)).toBe('תשפ״ו');
});

test('formatHebrewDate — plain, leap Adar I, Adar II', () => {
  expect(formatHebrewDate({ year: 5786, month: 4, day: 17 })).toBe('י״ז תמוז תשפ״ו');
  expect(formatHebrewDate({ year: 5787, month: 12, day: 1 })).toBe('א׳ אדר א׳ תשפ״ז');
  expect(formatHebrewDate({ year: 5787, month: 13, day: 1 })).toBe('א׳ אדר ב׳ תשפ״ז');
});

test('formatEnDate has no Intl dependency', () => {
  expect(formatEnDate(new Date(2026, 6, 2))).toBe('Thursday · July 2');
});
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `npx jest src/lib/__tests__/hebrewDate.test.ts`
Expected: FAIL — cannot find module `../hebrewDate`.

- [ ] **Step 4: Implement**

```ts
// src/lib/hebrewDate.ts
// Hebrew calendar conversion — the classic Dershowitz & Reingold algorithms
// ("Calendrical Calculations"). Hand-rolled: the npm Hebrew-calendar packages
// are GPL/LGPL, which this app cannot bundle, and Hermes Intl calendar
// support can't be verified under jest. Maps the civil day as printed on a
// wall calendar; "after sunset it's tomorrow" refinement belongs to the
// future zmanim round.

export interface HebrewDate {
  year: number;
  month: number; // 1 = Nisan … 7 = Tishrei … 12 = Adar (Adar I in leap years), 13 = Adar II
  day: number;
}

const HEBREW_EPOCH = -1373427; // Rata Die of 1 Tishrei, AM 1

function gregorianLeap(y: number): boolean {
  return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
}

const G_MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

// Rata Die: day 1 = Gregorian 0001-01-01.
function gregorianToRd(y: number, m: number, d: number): number {
  const p = y - 1;
  let days = 365 * p + Math.floor(p / 4) - Math.floor(p / 100) + Math.floor(p / 400);
  for (let i = 0; i < m - 1; i++) days += G_MONTH_DAYS[i];
  if (m > 2 && gregorianLeap(y)) days += 1;
  return days + d;
}

export function isHebrewLeapYear(year: number): boolean {
  return (7 * year + 1) % 19 < 7;
}

function elapsedDays(year: number): number {
  const monthsElapsed = Math.floor((235 * year - 234) / 19);
  const partsElapsed = 12084 + 13753 * monthsElapsed;
  let days = monthsElapsed * 29 + Math.floor(partsElapsed / 25920);
  if ((3 * (days + 1)) % 7 < 3) days += 1;
  return days;
}

function newYearDelay(year: number): number {
  const ny1 = elapsedDays(year);
  if (elapsedDays(year + 1) - ny1 === 356) return 2;
  if (ny1 - elapsedDays(year - 1) === 382) return 1;
  return 0;
}

function hebrewNewYearRd(year: number): number {
  return HEBREW_EPOCH + elapsedDays(year) + newYearDelay(year);
}

function daysInHebrewYear(year: number): number {
  return hebrewNewYearRd(year + 1) - hebrewNewYearRd(year);
}

function lastMonthOfHebrewYear(year: number): number {
  return isHebrewLeapYear(year) ? 13 : 12;
}

function lastDayOfHebrewMonth(year: number, month: number): number {
  if (month === 2 || month === 4 || month === 6 || month === 10 || month === 13) return 29;
  if (month === 12 && !isHebrewLeapYear(year)) return 29;
  if (month === 8 && daysInHebrewYear(year) % 10 !== 5) return 29; // regular/deficient Cheshvan
  if (month === 9 && daysInHebrewYear(year) % 10 === 3) return 29; // deficient Kislev
  return 30;
}

function hebrewToRd(year: number, month: number, day: number): number {
  let rd = hebrewNewYearRd(year) + day - 1;
  if (month < 7) {
    for (let m = 7; m <= lastMonthOfHebrewYear(year); m++) rd += lastDayOfHebrewMonth(year, m);
    for (let m = 1; m < month; m++) rd += lastDayOfHebrewMonth(year, m);
  } else {
    for (let m = 7; m < month; m++) rd += lastDayOfHebrewMonth(year, m);
  }
  return rd;
}

function rdToHebrew(rd: number): HebrewDate {
  let year = Math.floor((rd - HEBREW_EPOCH) / 366) + 1;
  while (hebrewNewYearRd(year + 1) <= rd) year++;
  // Months in civil order: Tishrei..(Adar/Adar II), then Nisan..Elul.
  const order: number[] = [];
  for (let m = 7; m <= lastMonthOfHebrewYear(year); m++) order.push(m);
  for (let m = 1; m <= 6; m++) order.push(m);
  let month = 7;
  for (const m of order) {
    if (rd <= hebrewToRd(year, m, lastDayOfHebrewMonth(year, m))) { month = m; break; }
  }
  return { year, month, day: rd - hebrewToRd(year, month, 1) + 1 };
}

export function fromGregorian(date: Date): HebrewDate {
  return rdToHebrew(gregorianToRd(date.getFullYear(), date.getMonth() + 1, date.getDate()));
}

const G_VALUES: Array<[number, string]> = [
  [400, 'ת'], [300, 'ש'], [200, 'ר'], [100, 'ק'], [90, 'צ'], [80, 'פ'], [70, 'ע'],
  [60, 'ס'], [50, 'נ'], [40, 'מ'], [30, 'ל'], [20, 'כ'], [10, 'י'], [9, 'ט'],
  [8, 'ח'], [7, 'ז'], [6, 'ו'], [5, 'ה'], [4, 'ד'], [3, 'ג'], [2, 'ב'], [1, 'א'],
];

export function gematriya(n: number): string {
  let rest = n;
  let out = '';
  for (const [v, ch] of G_VALUES) {
    if (v < 100 && rest === 15) { out += 'טו'; rest = 0; }
    if (v < 100 && rest === 16) { out += 'טז'; rest = 0; }
    while (rest >= v) { out += ch; rest -= v; }
  }
  if (out.length === 1) return out + '׳';
  return out.slice(0, -1) + '״' + out.slice(-1);
}

// Display names (unvocalized — these are UI labels, not liturgical text).
const HE_MONTHS = ['ניסן', 'אייר', 'סיון', 'תמוז', 'אב', 'אלול', 'תשרי', 'חשון', 'כסלו', 'טבת', 'שבט', 'אדר', 'אדר ב׳'];

export function formatHebrewDate(h: HebrewDate): string {
  const month = h.month === 12 && isHebrewLeapYear(h.year) ? 'אדר א׳' : HE_MONTHS[h.month - 1];
  return `${gematriya(h.day)} ${month} ${gematriya(h.year % 1000)}`;
}

// No Intl: Hermes Intl coverage differs by platform; static tables are exact.
const WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

export function formatEnDate(date: Date): string {
  return `${WEEKDAYS[date.getDay()]} · ${MONTHS[date.getMonth()]} ${date.getDate()}`;
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `npx jest src/lib/__tests__/hebrewDate.test.ts`
Expected: PASS (all). If a reference-value test fails, re-check against the Step 1 curl output before touching the algorithm — the anchors must match the Hebcal converter.

- [ ] **Step 6: Commit**

```bash
git add src/lib
git commit -m "feat: dependency-free Hebrew date converter + gematriya formatter"
```

---

### Task 3: Home categories (`src/content/categories.ts`)

**Files:**
- Create: `src/content/categories.ts`
- Test: `src/content/__tests__/categories.test.ts`

**Interfaces:**
- Consumes: `listServices()` from `src/content/loader.ts` (returns `Array<{id, heTitle, enTitle}>`).
- Produces: `HOME_CATEGORIES: HomeCategory[]`; `homeSections(): HomeSection[]` where `HomeSection = { key: string; title: string; compact: boolean; data: Array<{id: string; heTitle: string; enTitle: string}> }` — shaped for RN `SectionList`.

- [ ] **Step 1: Write the failing test**

```ts
// src/content/__tests__/categories.test.ts
import { HOME_CATEGORIES, homeSections } from '../categories';
import { listServices } from '../loader';

test('every registered service appears in exactly one category', () => {
  const all = HOME_CATEGORIES.flatMap((c) => c.serviceIds);
  expect(new Set(all).size).toBe(all.length); // no duplicates
  expect(new Set(all)).toEqual(new Set(listServices().map((s) => s.id))); // full coverage
});

test('homeSections resolves every id to real titles, preserving category order', () => {
  const sections = homeSections();
  expect(sections.map((s) => s.key)).toEqual(['tefillos', 'special', 'after-eating', 'anytime']);
  for (const section of sections) {
    for (const item of section.data) {
      expect(item.enTitle).toBeTruthy();
      expect(item.heTitle).toBeTruthy();
    }
  }
  expect(sections[0].data.map((i) => i.id)).toEqual(['shacharit', 'minchah', 'maariv']);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx jest src/content/__tests__/categories.test.ts`
Expected: FAIL — cannot find module `../categories`.

- [ ] **Step 3: Implement**

```ts
// src/content/categories.ts
import { listServices } from './loader';

// The home screen's grouping (approved design, Variant A). A service must
// live in exactly one category — the unit test fails the build if a newly
// registered service isn't categorized here.
export interface HomeCategory {
  key: string;
  title: string;
  compact: boolean; // compact rows for the less-frequent sections
  serviceIds: string[];
}

export const HOME_CATEGORIES: HomeCategory[] = [
  { key: 'tefillos', title: 'Tefillos', compact: false, serviceIds: ['shacharit', 'minchah', 'maariv'] },
  {
    key: 'special', title: 'Special Days', compact: true,
    serviceIds: ['sefiras-haomer', 'maariv-motzaei-shabbos', 'mussaf-rosh-chodesh', 'mussaf-chol-hamoed', 'hallel', 'netilas-lulav'],
  },
  { key: 'after-eating', title: 'After Eating', compact: true, serviceIds: ['birkas-hamazon', 'al-hamichyah', 'borei-nefashos'] },
  { key: 'anytime', title: 'Anytime', compact: true, serviceIds: ['tefillas-haderech', 'krias-shema-al-hamitah'] },
];

export interface HomeSection {
  key: string;
  title: string;
  compact: boolean;
  data: Array<{ id: string; heTitle: string; enTitle: string }>;
}

export function homeSections(): HomeSection[] {
  const byId = new Map(listServices().map((s) => [s.id, s]));
  return HOME_CATEGORIES.map((c) => ({
    key: c.key,
    title: c.title,
    compact: c.compact,
    data: c.serviceIds.map((id) => {
      const svc = byId.get(id);
      if (!svc) throw new Error(`home category '${c.key}' references unknown service '${id}'`);
      return svc;
    }),
  }));
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx jest src/content/__tests__/categories.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/content/categories.ts src/content/__tests__/categories.test.ts
git commit -m "feat: home screen category map with exhaustiveness test"
```

---

### Task 4: Track last-opened service in the reading-position store

**Files:**
- Modify: `src/store/readingPosition.ts`
- Modify: `app/daven/[service].tsx`
- Test: `src/store/__tests__/readingPosition.test.ts` (create)

**Interfaces:**
- Produces: `useReadingPositionStore` gains `lastServiceId: string | null` and `setLastService(serviceId: string): void`. NowCard (Task 5) reads `lastServiceId`.

- [ ] **Step 1: Write the failing tests**

```ts
// src/store/__tests__/readingPosition.test.ts
import { useReadingPositionStore } from '../readingPosition';

beforeEach(() => {
  useReadingPositionStore.setState({ offsets: {}, lastServiceId: null });
});

test('lastServiceId is null initially', () => {
  expect(useReadingPositionStore.getState().lastServiceId).toBeNull();
});

test('setLastService records the most recent service', () => {
  useReadingPositionStore.getState().setLastService('shacharit');
  useReadingPositionStore.getState().setLastService('minchah');
  expect(useReadingPositionStore.getState().lastServiceId).toBe('minchah');
});

test('setOffset still stores per-service offsets', () => {
  useReadingPositionStore.getState().setOffset('maariv', 1234);
  expect(useReadingPositionStore.getState().offsets['maariv']).toBe(1234);
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx jest src/store/__tests__/readingPosition.test.ts`
Expected: FAIL — `setLastService` is not a function / `lastServiceId` undefined.

- [ ] **Step 3: Extend the store**

In `src/store/readingPosition.ts`, extend the interface and creator:

```ts
interface ReadingPositionState {
  offsets: Record<string, number>;
  lastServiceId: string | null;
  setOffset: (serviceId: string, offset: number) => void;
  clearOffset: (serviceId: string) => void;
  setLastService: (serviceId: string) => void;
}
```

Inside `create(...)`'s object, add alongside the existing fields:

```ts
      lastServiceId: null,
      setLastService: (serviceId) => set({ lastServiceId: serviceId }),
```

(Leave the `persist` config unchanged — the new field persists automatically.)

- [ ] **Step 4: Record it when the reader opens a service**

In `app/daven/[service].tsx`, add a selector next to the existing reading-position usage and an effect after the existing keep-awake effect:

```ts
const setLastService = useReadingPositionStore((s) => s.setLastService);

useEffect(() => {
  if (serviceId && service) setLastService(serviceId);
}, [serviceId, service, setLastService]);
```

- [ ] **Step 5: Run the full check**

Run: `npm run check`
Expected: typecheck clean, lint 0 errors, all jest suites pass (including the new one).

- [ ] **Step 6: Commit**

```bash
git add src/store/readingPosition.ts src/store/__tests__/readingPosition.test.ts "app/daven/[service].tsx"
git commit -m "feat: persist last-opened service for the home resume link"
```

---

### Task 5: NowCard + home screen rewrite

**Files:**
- Create: `src/components/NowCard.tsx`
- Modify: `app/daven/index.tsx` (full rewrite below)

**Interfaces:**
- Consumes: `formatEnDate`/`fromGregorian`/`formatHebrewDate` (Task 2), `homeSections()`/`HomeSection` (Task 3), `lastServiceId` (Task 4), `getService` from loader, `useThemeColors`.
- Produces: home screen navigates to `/about` and `/glossary` (screens land in Tasks 8 & 10 — until then the links 404 to expo-router's unmatched-route screen, acceptable mid-plan on a feature branch; the plan finishes before merge).

- [ ] **Step 1: Create NowCard**

```tsx
// src/components/NowCard.tsx
import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { router } from 'expo-router';
import { getService } from '../content/loader';
import { useReadingPositionStore } from '../store/readingPosition';
import { ColorPalette } from '../theme/colors';
import { useThemeColors } from '../theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../theme/typography';
import { formatEnDate, fromGregorian, formatHebrewDate } from '../lib/hebrewDate';

// The home screen's "now" zone. This round it carries the date line and a
// resume link; the suggested-service CTA and zmanim strip from the design
// spec land in the zmanim round and mount inside this same card.
export function NowCard() {
  const { colors } = useThemeColors();
  const lastServiceId = useReadingPositionStore((s) => s.lastServiceId);
  const last = lastServiceId ? getService(lastServiceId) : null;
  const now = new Date();
  const s = makeStyles(colors);

  return (
    <View style={[s.card, { backgroundColor: colors.surface, borderColor: colors.line, borderTopColor: colors.gold }]}>
      <View style={s.dateRow}>
        <Text style={[s.enDate, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
          {formatEnDate(now)}
        </Text>
        <Text style={[s.heDate, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE} accessibilityLanguage="he">
          {formatHebrewDate(fromGregorian(now))}
        </Text>
      </View>
      {last && (
        <Pressable
          onPress={() => router.push('/daven/' + last.id as any)}
          accessibilityRole="button"
          accessibilityLabel={`Resume ${last.enTitle}`}
          style={s.resumeBtn}
        >
          <Text style={[s.resumeText, { color: colors.accent }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
            Resume {last.enTitle} →
          </Text>
        </Pressable>
      )}
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    card: {
      marginHorizontal: 16,
      marginBottom: 4,
      borderRadius: 16,
      borderWidth: 1,
      borderTopWidth: 3,
      paddingVertical: 14,
      paddingHorizontal: 18,
    },
    dateRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    enDate: { fontFamily: Fonts.uiSemiBold, fontSize: 13, letterSpacing: 0.3 },
    heDate: { fontFamily: Fonts.hebrewBold, fontSize: 17, writingDirection: 'rtl' as const },
    resumeBtn: { marginTop: 10 },
    resumeText: { fontFamily: Fonts.uiSemiBold, fontSize: 14.5 },
  });
}
```

- [ ] **Step 2: Rewrite the home screen**

Replace the body of `app/daven/index.tsx` entirely:

```tsx
import React from 'react';
import { View, Text, Pressable, StyleSheet, SectionList, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { homeSections, HomeSection } from '../../src/content/categories';
import { NowCard } from '../../src/components/NowCard';
import { ColorPalette } from '../../src/theme/colors';
import { useThemeColors } from '../../src/theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../../src/theme/typography';

export default function DavenHome() {
  const { colors } = useThemeColors();
  const sections: HomeSection[] = homeSections();
  const s = makeStyles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <SectionList
          sections={sections}
          keyExtractor={(item) => item.id}
          contentContainerStyle={s.list}
          stickySectionHeadersEnabled={false}
          ListHeaderComponent={
            <>
              <View style={s.headerRow}>
                <Text style={[s.title, { color: colors.ink }]}>Daven</Text>
                <View style={s.headerActions}>
                  <Pressable
                    onPress={() => router.push('/notes')}
                    accessibilityRole="button"
                    accessibilityLabel="Open notes and highlights"
                    style={s.iconBtn}
                  >
                    <Ionicons name="bookmark-outline" size={22} color={colors.muted} />
                  </Pressable>
                  <Pressable
                    onPress={() => router.push('/settings')}
                    accessibilityRole="button"
                    accessibilityLabel="Open settings"
                    style={s.iconBtn}
                  >
                    <Ionicons name="settings-outline" size={22} color={colors.muted} />
                  </Pressable>
                </View>
              </View>
              <NowCard />
            </>
          }
          renderSectionHeader={({ section }) => (
            <Text style={[s.sectionLabel, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
              {section.title}
            </Text>
          )}
          renderItem={({ item, section }) => (
            <Pressable
              style={({ pressed }) => [
                s.row,
                (section as HomeSection).compact && s.rowCompact,
                { backgroundColor: colors.surface, borderColor: colors.line },
                pressed && s.rowPressed,
              ]}
              onPress={() => router.push('/daven/' + item.id as any)}
              accessibilityRole="button"
              accessibilityLabel={`Open ${item.enTitle}`}
            >
              <Text
                style={[s.rowEn, (section as HomeSection).compact && s.rowEnCompact, { color: colors.ink }]}
                maxFontSizeMultiplier={MAX_FONT_SCALE}
              >
                {item.enTitle}
              </Text>
              <Text
                style={[s.rowHe, (section as HomeSection).compact && s.rowHeCompact, { color: colors.muted }]}
                maxFontSizeMultiplier={MAX_FONT_SCALE}
                accessibilityLanguage="he"
              >
                {item.heTitle}
              </Text>
            </Pressable>
          )}
          ListFooterComponent={
            <>
              <Text style={[s.sectionLabel, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                From the Book
              </Text>
              <View style={s.bookRow}>
                <Pressable
                  style={[s.bookCard, { backgroundColor: colors.surface, borderColor: colors.line }]}
                  onPress={() => router.push('/about' as any)}
                  accessibilityRole="button"
                  accessibilityLabel="About this Siddur"
                >
                  <Text style={[s.bookTitle, { color: colors.ink }]}>About this Siddur</Text>
                  <Text style={[s.bookDesc, { color: colors.muted }]}>
                    Rabbi Feigenbaum's introductions, dedications & notes
                  </Text>
                </Pressable>
                <Pressable
                  style={[s.bookCard, { backgroundColor: colors.surface, borderColor: colors.line }]}
                  onPress={() => router.push('/glossary' as any)}
                  accessibilityRole="button"
                  accessibilityLabel="Glossary"
                >
                  <Text style={[s.bookTitle, { color: colors.ink }]}>Glossary</Text>
                  <Text style={[s.bookDesc, { color: colors.muted }]}>
                    Hebrew terms used throughout the translations
                  </Text>
                </Pressable>
              </View>
            </>
          }
        />
      </SafeAreaView>
    </View>
  );
}

function makeStyles(colors: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    headerRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: 8,
      paddingTop: 24,
      paddingBottom: 12,
    },
    title: { fontFamily: Fonts.uiSemiBold, fontSize: 28 },
    iconBtn: { padding: 8 },
    headerActions: { flexDirection: 'row', alignItems: 'center' },
    list: { paddingHorizontal: 16, paddingBottom: 40 },
    sectionLabel: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 11,
      letterSpacing: 1.6,
      textTransform: 'uppercase' as const,
      marginTop: 20,
      marginBottom: 8,
      paddingHorizontal: 4,
    },
    row: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderRadius: 14,
      paddingVertical: 16,
      paddingHorizontal: 18,
      borderWidth: 1,
      marginBottom: 8,
    },
    rowCompact: { paddingVertical: 11 },
    rowPressed: { opacity: 0.7 },
    rowEn: { fontFamily: Fonts.uiMedium, fontSize: 17 },
    rowEnCompact: { fontSize: 15 },
    rowHe: { fontFamily: Fonts.hebrewBold, fontSize: 20, writingDirection: 'rtl' as const },
    rowHeCompact: { fontSize: 18 },
    bookRow: { flexDirection: 'row', gap: 8 },
    bookCard: { flex: 1, borderRadius: 14, borderWidth: 1, padding: 14 },
    bookTitle: { fontFamily: Fonts.uiSemiBold, fontSize: 14.5 },
    bookDesc: { fontFamily: Fonts.ui, fontSize: 11.5, marginTop: 3, lineHeight: 15 },
  });
}
```

Note: `headerRow` uses `paddingHorizontal: 8` because the SectionList's `contentContainerStyle` already pads 16 — combined ≈ the old 24.

- [ ] **Step 3: Verify in the simulator**

Run: `npm run check` (expected: all green), then `npm run ios` (or reload Expo Go). Verify: now-card shows today's civil + Hebrew date; after opening any service and returning home, "Resume <Service> →" appears and works; all four sections show all 14 services; compact rows visibly smaller; "From the Book" cards present (their routes 404 until Tasks 8/10 — expected).

- [ ] **Step 4: Commit**

```bash
git add src/components/NowCard.tsx app/daven/index.tsx
git commit -m "feat: grouped home screen (Variant A) with now-card date + resume"
```

---

### Task 6: Extract shared prose renderer from AppendixModal

The About piece reader (Task 10) needs exactly the segment-rendering block that lives inline in `AppendixModal` (`src/components/AppendixModal.tsx:44-76`). Extract it so both use one implementation.

**Files:**
- Create: `src/components/ProseSegments.tsx`
- Modify: `src/components/AppendixModal.tsx`

**Interfaces:**
- Produces: `ProseSegments({ segments, heSize, enSize, colors }: { segments: Segment[]; heSize: number; enSize: number; colors: ColorPalette })` — renders header/rubric/prayer/prose segments in the appendix reading style.

- [ ] **Step 1: Create ProseSegments**

```tsx
// src/components/ProseSegments.tsx
import React from 'react';
import { Text, StyleSheet } from 'react-native';
import { Segment } from '../content/types';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';
import { RichText } from './RichText';

// Long-form prose reader used by the appendices and the About pieces:
// headers as kickers, Hebrew lines RTL, everything else as RichText prose.
export function ProseSegments({
  segments, heSize, enSize, colors,
}: {
  segments: Segment[];
  heSize: number;
  enSize: number;
  colors: ColorPalette;
}) {
  const s = makeStyles(heSize, enSize);
  return (
    <>
      {segments.map((seg, i) => {
        if (seg.type === 'header') {
          return (
            <Text key={i} style={[s.subhead, { color: colors.accent }]}>
              {seg.enText || seg.heText}
            </Text>
          );
        }
        if (seg.type === 'rubric') {
          return (
            <Text key={i} style={[s.rubric, { color: colors.muted }]}>
              {seg.enText || seg.heText}
            </Text>
          );
        }
        if (seg.type === 'prayer') {
          return (
            <Text key={i} style={[s.he, { color: colors.ink }]} selectable accessibilityLanguage="he">
              {seg.heText}
            </Text>
          );
        }
        return (
          <RichText
            key={i}
            text={seg.enText ?? ''}
            style={[s.prose, { color: colors.ink }]}
            italicStyle={s.italic}
            boldStyle={s.bold}
            linkStyle={[s.link, { color: colors.accent }]}
            selectable
          />
        );
      })}
    </>
  );
}

function makeStyles(heSize: number, enSize: number) {
  return StyleSheet.create({
    subhead: {
      fontFamily: Fonts.uiSemiBold, fontSize: enSize * 0.85, letterSpacing: 1,
      textTransform: 'uppercase' as const, marginTop: 18, marginBottom: 6,
    },
    rubric: { fontFamily: Fonts.englishItalic, fontSize: enSize * 0.9, marginTop: 8, marginBottom: 4 },
    he: {
      fontFamily: Fonts.hebrew, fontSize: heSize, lineHeight: heSize * 1.9,
      textAlign: 'right' as const, writingDirection: 'rtl' as const, marginVertical: 8,
    },
    prose: { fontFamily: Fonts.english, fontSize: enSize, lineHeight: enSize * 1.62, marginBottom: 12 },
    italic: { fontFamily: Fonts.englishItalic, fontStyle: 'italic' as const },
    bold: { fontFamily: Fonts.englishBold, fontWeight: '600' as const },
    link: { textDecorationLine: 'underline' as const, fontFamily: Fonts.uiSemiBold },
  });
}
```

Note: `linkStyle` here passes an array — check `RichText`'s prop type accepts `StyleProp<TextStyle>` (it should; if it's typed as a plain object, widen the prop type to `StyleProp<TextStyle>`).

- [ ] **Step 2: Use it in AppendixModal**

In `src/components/AppendixModal.tsx`, replace the `appendix.segments.map(...)` block (lines 44–76) with:

```tsx
<ProseSegments
  segments={appendix.segments}
  heSize={hebrewFontSize(fontStep)}
  enSize={englishFontSize(fontStep)}
  colors={colors}
/>
```

Add the import, and delete the now-unused styles from `makeStyles` (`subhead`, `rubric`, `he`, `prose`, `italic`, `bold`, `link`) and the unused `RichText` import.

- [ ] **Step 3: Verify no regression**

Run: `npm run check`
Expected: green. Then in the simulator open any appendix link from commentary (e.g., in Shacharis) and confirm the appendix renders as before.

- [ ] **Step 4: Commit**

```bash
git add src/components/ProseSegments.tsx src/components/AppendixModal.tsx
git commit -m "refactor: extract ProseSegments prose renderer from AppendixModal"
```

---

### Task 7: Glossary content (digitize siddur p. 269)

**Files:**
- Create: `scripts/extract_glossary.py`
- Create: `src/content/glossary.json` (generated)
- Create: `src/content/glossary.ts`
- Test: `src/content/__tests__/glossary.test.ts`

**Interfaces:**
- Produces: `listGlossary(): GlossaryEntry[]` and `glossarySections(): Array<{ letter: string; data: GlossaryEntry[] }>` where `GlossaryEntry = { term: string; definition: string }`.

- [ ] **Step 1: Write the extraction script**

The glossary starts at siddur p. 269 → **pdf p. 293** and runs to the end of the book. Entry format: `term — definition.` (em dash), with occasional wrapped definitions (e.g., *sandek*).

```python
#!/usr/bin/env python3
"""Extract the Glossary (siddur p.269 ff -> pdf p.293 ff) into glossary.json.

Deterministic: asserts the GLOSSARY heading is present and that entry count
lands in the expected range, so a bad pdftotext run fails loudly.
"""
import json, re, subprocess, sys

PDF = 'feigenbaum-siddur-original.pdf'
raw = subprocess.run(
    ['pdftotext', '-f', '293', PDF, '-'],
    capture_output=True, text=True, check=True,
).stdout

assert 'GLOSSARY' in raw, 'GLOSSARY heading not found on pdf p.293+'

entries = []
current = None
for line in raw.splitlines():
    line = line.strip()
    # skip blanks, headings, running heads, page numbers, form feeds
    if not line or line in ('GLOSSARY', 'Glossary') or re.fullmatch(r'[0-9]+', line):
        continue
    m = re.match(r'^(.{1,60}?) — (.+)$', line)
    if m:
        if current:
            entries.append(current)
        current = {'term': m.group(1).strip(), 'definition': m.group(2).strip()}
    elif current:
        # wrapped definition line
        current['definition'] += ' ' + line
if current:
    entries.append(current)

assert 60 <= len(entries) <= 90, f'unexpected entry count: {len(entries)}'
assert all(e['term'] and e['definition'] for e in entries)

with open('src/content/glossary.json', 'w', encoding='utf-8') as f:
    json.dump({'entries': entries}, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'wrote {len(entries)} entries')
```

Watch for pdftotext emitting U+2014 vs U+2013 for the dash — check the raw text first (`pdftotext -f 293 feigenbaum-siddur-original.pdf - | head -20 | od -c | grep -A1 342` or simply print a line) and adjust the regex to the actual character.

- [ ] **Step 2: Run it and proof against the print**

Run: `python3 scripts/extract_glossary.py`
Expected: `wrote N entries` (N ≈ 70).

Proof (content-fidelity gate): render the glossary pages at 300 DPI and hand-check every entry:

```bash
pdftoppm -png -r 300 -f 293 -l 296 feigenbaum-siddur-original.pdf /tmp/gloss
```

Read each rendered page and compare term-by-term against `glossary.json` — every term present, no fabricated entries, definitions verbatim (punctuation included). Fix the script (not the JSON by hand) if anything is off, and re-run.

- [ ] **Step 3: Write the failing accessor test**

```ts
// src/content/__tests__/glossary.test.ts
import { listGlossary, glossarySections } from '../glossary';

test('glossary has the full printed entry set', () => {
  const entries = listGlossary();
  expect(entries.length).toBeGreaterThanOrEqual(60);
  const terms = entries.map((e) => e.term);
  expect(terms).toContain('Hashem');
  expect(terms).toContain('bitachon');
  for (const e of entries) {
    expect(e.term).toBeTruthy();
    expect(e.definition).toBeTruthy();
  }
});

test('glossarySections groups by first letter, A→Z, entries in print order', () => {
  const sections = glossarySections();
  const letters = sections.map((s) => s.letter);
  expect(letters).toEqual([...letters].sort());
  for (const section of sections) {
    expect(section.data.length).toBeGreaterThan(0);
    for (const e of section.data) {
      expect(e.term[0].toUpperCase()).toBe(section.letter);
    }
  }
});
```

- [ ] **Step 4: Run test to verify it fails**

Run: `npx jest src/content/__tests__/glossary.test.ts`
Expected: FAIL — cannot find module `../glossary`.

- [ ] **Step 5: Implement the accessor**

```ts
// src/content/glossary.ts
import data from './glossary.json';

export interface GlossaryEntry {
  term: string;
  definition: string;
}

const ENTRIES: GlossaryEntry[] = (data as { entries: GlossaryEntry[] }).entries;

export function listGlossary(): GlossaryEntry[] {
  return ENTRIES;
}

// Letter groups for the browsable screen; print order kept within a letter.
export function glossarySections(): Array<{ letter: string; data: GlossaryEntry[] }> {
  const byLetter = new Map<string, GlossaryEntry[]>();
  for (const e of ENTRIES) {
    const letter = e.term[0].toUpperCase();
    if (!byLetter.has(letter)) byLetter.set(letter, []);
    byLetter.get(letter)!.push(e);
  }
  return [...byLetter.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([letter, data]) => ({ letter, data }));
}
```

- [ ] **Step 6: Run tests + strict lint**

Run: `npx jest src/content/__tests__/glossary.test.ts && python3 scripts/lint_content.py --strict`
Expected: PASS; lint 0 errors (glossary.json has no `segments`, so the linter walks past it).

- [ ] **Step 7: Commit**

```bash
git add scripts/extract_glossary.py src/content/glossary.json src/content/glossary.ts src/content/__tests__/glossary.test.ts
git commit -m "content: digitize the Glossary (siddur p.269) + accessor"
```

---

### Task 8: Glossary screen (`app/glossary.tsx`)

**Files:**
- Create: `app/glossary.tsx`

**Interfaces:**
- Consumes: `glossarySections()` (Task 7), `useThemeColors`, `Fonts`/`MAX_FONT_SCALE`.

- [ ] **Step 1: Create the screen**

```tsx
// app/glossary.tsx
import React, { useRef } from 'react';
import { View, Text, Pressable, StyleSheet, SectionList, SafeAreaView, ScrollView } from 'react-native';
import { router } from 'expo-router';
import { glossarySections, GlossaryEntry } from '../src/content/glossary';
import { ColorPalette } from '../src/theme/colors';
import { useThemeColors } from '../src/theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../src/theme/typography';

export default function GlossaryScreen() {
  const { colors } = useThemeColors();
  const sections = glossarySections();
  const listRef = useRef<SectionList<GlossaryEntry>>(null);
  const s = makeStyles(colors);

  const jumpTo = (index: number) =>
    listRef.current?.scrollToLocation({ sectionIndex: index, itemIndex: 0, viewOffset: 8 });

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <View style={s.header}>
          <Pressable
            onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Text style={[s.backText, { color: colors.accent }]}>← Back</Text>
          </Pressable>
          <Text style={[s.title, { color: colors.ink }]}>Glossary</Text>
          <Text style={[s.sub, { color: colors.muted }]}>
            Hebrew terms used throughout the translations
          </Text>
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.alphaBar} contentContainerStyle={s.alphaContent}>
          {sections.map((section, i) => (
            <Pressable
              key={section.letter}
              onPress={() => jumpTo(i)}
              accessibilityRole="button"
              accessibilityLabel={`Jump to ${section.letter}`}
              style={[s.alphaBtn, { backgroundColor: colors.surface, borderColor: colors.line }]}
            >
              <Text style={[s.alphaText, { color: colors.accent }]}>{section.letter}</Text>
            </Pressable>
          ))}
        </ScrollView>

        <SectionList
          ref={listRef}
          sections={sections}
          keyExtractor={(item) => item.term}
          contentContainerStyle={s.list}
          stickySectionHeadersEnabled={false}
          onScrollToIndexFailed={() => {}}
          renderSectionHeader={({ section }) => (
            <Text style={[s.sectionLabel, { color: colors.muted }]}>{section.letter}</Text>
          )}
          renderItem={({ item }) => (
            <View style={[s.entry, { backgroundColor: colors.surface, borderColor: colors.line }]}>
              <Text style={[s.term, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                {item.term}
              </Text>
              <Text style={[s.def, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE} selectable>
                {item.definition}
              </Text>
            </View>
          )}
        />
      </SafeAreaView>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    header: { paddingTop: 16, paddingHorizontal: 20, paddingBottom: 6 },
    backText: { fontFamily: Fonts.uiMedium, fontSize: 15, marginBottom: 8 },
    title: { fontFamily: Fonts.uiSemiBold, fontSize: 26 },
    sub: { fontFamily: Fonts.ui, fontSize: 13, marginTop: 2 },
    alphaBar: { flexGrow: 0, marginTop: 8 },
    alphaContent: { paddingHorizontal: 16, gap: 6 },
    alphaBtn: { minWidth: 32, alignItems: 'center', borderRadius: 8, borderWidth: 1, paddingVertical: 6, paddingHorizontal: 4 },
    alphaText: { fontFamily: Fonts.uiSemiBold, fontSize: 13 },
    list: { paddingHorizontal: 16, paddingBottom: 40 },
    sectionLabel: {
      fontFamily: Fonts.uiSemiBold, fontSize: 11, letterSpacing: 1.5,
      textTransform: 'uppercase' as const, marginTop: 16, marginBottom: 8, paddingHorizontal: 4,
    },
    entry: { borderRadius: 14, borderWidth: 1, padding: 13, marginBottom: 8 },
    term: { fontFamily: Fonts.uiSemiBold, fontSize: 15.5 },
    def: { fontFamily: Fonts.english, fontSize: 14.5, lineHeight: 21, marginTop: 3 },
  });
}
```

- [ ] **Step 2: Verify**

Run: `npm run check` (green), then in the simulator: home → Glossary card → screen lists every letter group; jump bar scrolls; back returns home.

- [ ] **Step 3: Commit**

```bash
git add app/glossary.tsx
git commit -m "feat: browsable Glossary screen with letter jump bar"
```

---

### Task 9: Book matter content (digitize front/back matter)

**Files:**
- Modify: `src/content/types.ts` (add `BookPiece`)
- Create: `scripts/extract_book_matter.py`
- Create: `src/content/book-matter.json` (generated)
- Create: `src/content/bookMatter.ts`

**Interfaces:**
- Produces: `listBookPieces(): Array<{ id: string; title: string; subtitle?: string }>`; `getBookPiece(id): BookPiece | null`; `BookPiece = { id: string; title: string; subtitle?: string; segments: Segment[] }`. Piece ids (fixed, consumed by Task 10): `intro-teens`, `translation-note`, `intro-parents`, `personal-notes`, `dedications`, `acknowledgments`.

- [ ] **Step 1: Add the type**

In `src/content/types.ts`, after the `Appendix` interface (or at the end of the interfaces):

```ts
// Front/back matter of the print book (introductions, dedications, notes) —
// prose pieces read on the About screen, reusing the Segment renderer.
export interface BookPiece {
  id: string;
  title: string;
  subtitle?: string;
  segments: Segment[];
}
```

- [ ] **Step 2: Write the extraction script**

Sources — front matter: `pdftotext -f 7 -l 24 feigenbaum-siddur-original.pdf -` (dedications ~pp. 7–10, Acknowledgments pp. XI–XIII, Intro for Parents pp. XIV–XVII incl. the "Note Regarding This 'Translation'", Intro for Teens pp. XVIII–XXIII). Back matter: personal notes at siddur pp. 239–240 → `pdftotext -f 263 -l 264 …`.

Script pattern (`scripts/extract_book_matter.py`) — locate each piece by its heading marker, split into paragraphs, and emit segments. **All body text must come verbatim from the pdftotext output (Hebrew included — never retype it)**; the script asserts each marker exists:

```python
#!/usr/bin/env python3
"""Build src/content/book-matter.json from the print's front/back matter.

Text is taken verbatim from pdftotext output. Paragraphs become
`commentary` segments (rendered as prose); interior headings become
`header` segments. Assertions fail loudly if the PDF text shifts.
"""
import json, re, subprocess

PDF = 'feigenbaum-siddur-original.pdf'

def pages(f, l):
    return subprocess.run(['pdftotext', '-f', str(f), '-l', str(l), PDF, '-'],
                          capture_output=True, text=True, check=True).stdout

front = pages(7, 24)
back = pages(263, 264)

def slice_between(text, start_marker, end_marker):
    i = text.index(start_marker)          # raises if missing — deliberate
    j = text.index(end_marker, i) if end_marker else len(text)
    return text[i:j]

def paragraphs(block):
    """Rejoin pdftotext's hard-wrapped lines into paragraphs; drop running
    heads / roman page numbers."""
    out, cur = [], []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            if cur:
                out.append(' '.join(cur)); cur = []
            continue
        if re.fullmatch(r'[IVXL]+|\d+', line):
            continue
        cur.append(line)
    if cur:
        out.append(' '.join(cur))
    return out

# ... per-piece assembly: for each piece, slice_between two markers from the
# TOC-verified headings, drop the heading itself and running-head repeats
# (e.g. 'Introduction for Teens', 'Acknowledgments XII'), then:
#   segments = [{'id': f'{piece_id}-p{i}', 'type': 'commentary', 'enText': p}
#               for i, p in enumerate(paragraphs(body), 1)]
# Hebrew-only lines (e.g. 'אמן כן יהי רצון') become type 'prayer' segments.

pieces = []
# intro-teens: slice_between(front, 'INTRODUCTION FOR TEENS', <end>) …
# (assemble all six pieces here — see piece list in the plan)

assert [p['id'] for p in pieces] == [
    'intro-teens', 'translation-note', 'intro-parents',
    'personal-notes', 'dedications', 'acknowledgments',
]
for p in pieces:
    assert p['segments'], f"empty piece {p['id']}"

with open('src/content/book-matter.json', 'w', encoding='utf-8') as f:
    json.dump({'pieces': pieces}, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f"wrote {len(pieces)} pieces, {sum(len(p['segments']) for p in pieces)} segments")
```

Piece assembly details (implementer fills the marked section, keeping every assertion):

| id | title | source & notes |
|---|---|---|
| `intro-teens` | `"But I Don't Do Davening!"` | subtitle `Introduction for Teens`. Marker `INTRODUCTION FOR TEENS` → end of front matter. The parenthetical `("OK, I do davening, but I don't enjoy it!")` becomes a `rubric` segment right after the start. |
| `translation-note` | `How to Read the Translation` | subtitle `Note Regarding This "Translation"`. Marker `Note Regarding This "Translation"` → `INTRODUCTION FOR TEENS`. The three bullet examples (ברוך / קדוש / שם) each become their own `commentary` segment prefixed `• `. |
| `intro-parents` | `Introduction for Parents, Mechanchim, and Mechanchos` | Marker `INTRODUCTION FOR PARENTS` → `Note Regarding This "Translation"`. Drop the cross-ref line `Introduction for Teens on page XVIII`. |
| `personal-notes` | `A Personal Note from Rabbi Feigenbaum` | From back matter (pdf 263–264). Two `header` segments — `For Parents, Mechanchim, and Mechanchos` and `For Teens` — each followed by its paragraphs. |
| `dedications` | `Dedications` | subtitle `The Cohen Family Edition`. Markers within pdf 7–10. Hebrew lines (`סדור זכרון גליקל חנה` etc.) are `prayer` segments **sliced verbatim**; memorial prose is `commentary`; names set bold (`**Mrs. Gloria Cohen ע״ה**`). Includes the Sara Goldman page, the Tobias tribute, and the `ואלו יעמדו על הברכה` pair. |
| `acknowledgments` | `Acknowledgments` | Marker `ACKNOWLEDGMENTS` → `INTRODUCTION FOR PARENTS`. Closing `אמן כן יהי רצון` is a `prayer` segment. |

- [ ] **Step 3: Run and proof against the print**

Run: `python3 scripts/extract_book_matter.py` → `wrote 6 pieces, N segments`.

Proof (content-fidelity gate): render the source pages at 300 DPI —

```bash
pdftoppm -png -r 300 -f 7 -l 24 feigenbaum-siddur-original.pdf /tmp/front
pdftoppm -png -r 300 -f 263 -l 264 feigenbaum-siddur-original.pdf /tmp/notes
```

Read each page and verify each piece paragraph-by-paragraph: no dropped/merged paragraphs, Hebrew phrases intact with nikud where printed, italics/quotes preserved. All Hebrew must be byte-identical to the pdftotext output (spot-check by grepping the JSON strings against the raw extraction). Fix the script, not the JSON.

Then: `python3 scripts/lint_content.py --strict` — expected 0 errors. Note the linter walks any dict with `segments`, so these pieces are linted; **prose paragraphs must be `commentary` (enText), never carry `heText`** or the stranded-heText error fires. Standalone Hebrew lines are `prayer` segments (heText only) — that's the supported shape.

- [ ] **Step 4: Accessor**

```ts
// src/content/bookMatter.ts
import { BookPiece } from './types';
import data from './book-matter.json';

const PIECES: BookPiece[] = (data as { pieces: BookPiece[] }).pieces;

export function getBookPiece(id: string): BookPiece | null {
  return PIECES.find((p) => p.id === id) ?? null;
}

export function listBookPieces(): Array<{ id: string; title: string; subtitle?: string }> {
  return PIECES.map(({ id, title, subtitle }) => ({ id, title, subtitle }));
}
```

- [ ] **Step 5: Check + commit**

Run: `npm run check`
Expected: green (no new tests here — the content gate is the print proofing + linter; Task 10's screen exercises the accessor).

```bash
git add src/content/types.ts scripts/extract_book_matter.py src/content/book-matter.json src/content/bookMatter.ts
git commit -m "content: digitize book front/back matter (introductions, dedications, notes)"
```

---

### Task 10: About screens (`app/about/index.tsx`, `app/about/[piece].tsx`)

**Files:**
- Create: `app/about/index.tsx`
- Create: `app/about/[piece].tsx`

**Interfaces:**
- Consumes: `getBookPiece`/`listBookPieces` (Task 9), `ProseSegments` (Task 6), `hebrewFontSize`/`englishFontSize`, `usePreferencesStore` (`fontStep`).

- [ ] **Step 1: TOC screen**

```tsx
// app/about/index.tsx
import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView, SafeAreaView } from 'react-native';
import { router } from 'expo-router';
import { ColorPalette } from '../../src/theme/colors';
import { useThemeColors } from '../../src/theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../../src/theme/typography';

// Reader-first ordering (not print order): the teen intro and translation
// note are the two pieces a davener actually needs; provenance last.
const TOC: Array<{ label: string; rows: Array<{ id: string; title: string; desc: string }> }> = [
  {
    label: 'Read First',
    rows: [
      { id: 'intro-teens', title: '"But I Don\'t Do Davening!"', desc: 'Introduction for Teens — why davening is hard, and how this siddur helps' },
      { id: 'translation-note', title: 'How to Read the Translation', desc: 'What the italics mean, and why key words are translated the way they are' },
    ],
  },
  {
    label: 'For Parents & Teachers',
    rows: [
      { id: 'intro-parents', title: 'Introduction for Parents, Mechanchim, and Mechanchos', desc: 'The approach behind the translation and commentary' },
      { id: 'personal-notes', title: 'A Personal Note from Rabbi Feigenbaum', desc: 'For parents and mechanchim · For teens' },
    ],
  },
  {
    label: 'The People Behind It',
    rows: [
      { id: 'dedications', title: 'Dedications', desc: 'The Cohen Family Edition — in loving memory' },
      { id: 'acknowledgments', title: 'Acknowledgments', desc: 'Rabbi Feigenbaum\'s thanks — starting with why we thank Hashem at all' },
    ],
  },
];

export default function AboutScreen() {
  const { colors } = useThemeColors();
  const s = makeStyles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <ScrollView contentContainerStyle={s.body}>
          <Pressable
            onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Text style={[s.backText, { color: colors.accent }]}>← Back</Text>
          </Pressable>
          <Text style={[s.title, { color: colors.ink }]}>About this Siddur</Text>
          <Text style={[s.sub, { color: colors.muted }]}>
            The Feigenbaum Siddur · The Cohen Family Edition · Nusach Ashkenaz{'\n'}
            By Rabbi Yitzchak Feigenbaum · Mosaica Press
          </Text>

          {TOC.map((group) => (
            <View key={group.label}>
              <Text style={[s.sectionLabel, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                {group.label}
              </Text>
              {group.rows.map((row) => (
                <Pressable
                  key={row.id}
                  style={({ pressed }) => [
                    s.row,
                    { backgroundColor: colors.surface, borderColor: colors.line },
                    pressed && { opacity: 0.7 },
                  ]}
                  onPress={() => router.push(('/about/' + row.id) as any)}
                  accessibilityRole="button"
                  accessibilityLabel={`Open ${row.title}`}
                >
                  <Text style={[s.rowTitle, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                    {row.title}
                  </Text>
                  <Text style={[s.rowDesc, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                    {row.desc}
                  </Text>
                </Pressable>
              ))}
            </View>
          ))}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    body: { paddingHorizontal: 16, paddingTop: 16, paddingBottom: 40 },
    backText: { fontFamily: Fonts.uiMedium, fontSize: 15, marginBottom: 8, paddingHorizontal: 4 },
    title: { fontFamily: Fonts.uiSemiBold, fontSize: 26, paddingHorizontal: 4 },
    sub: { fontFamily: Fonts.ui, fontSize: 13, lineHeight: 19, marginTop: 4, paddingHorizontal: 4 },
    sectionLabel: {
      fontFamily: Fonts.uiSemiBold, fontSize: 11, letterSpacing: 1.5,
      textTransform: 'uppercase' as const, marginTop: 20, marginBottom: 8, paddingHorizontal: 4,
    },
    row: { borderRadius: 14, borderWidth: 1, padding: 14, marginBottom: 8 },
    rowTitle: { fontFamily: Fonts.uiSemiBold, fontSize: 15.5 },
    rowDesc: { fontFamily: Fonts.ui, fontSize: 12, lineHeight: 17, marginTop: 3 },
  });
}
```

- [ ] **Step 2: Piece reader**

```tsx
// app/about/[piece].tsx
import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView, SafeAreaView } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { getBookPiece } from '../../src/content/bookMatter';
import { ProseSegments } from '../../src/components/ProseSegments';
import { usePreferencesStore } from '../../src/store/preferences';
import { ColorPalette } from '../../src/theme/colors';
import { useThemeColors } from '../../src/theme/useThemeColors';
import { Fonts, hebrewFontSize, englishFontSize } from '../../src/theme/typography';

export default function BookPieceScreen() {
  const { piece: pieceId } = useLocalSearchParams<{ piece: string }>();
  const { colors } = useThemeColors();
  const fontStep = usePreferencesStore((s) => s.fontStep);
  const piece = pieceId ? getBookPiece(pieceId) : null;
  const s = makeStyles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <ScrollView contentContainerStyle={s.body} showsVerticalScrollIndicator={false}>
          <Pressable
            onPress={() => (router.canGoBack() ? router.back() : router.replace('/about' as any))}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Text style={[s.backText, { color: colors.accent }]}>← Back</Text>
          </Pressable>
          {!piece ? (
            <Text style={[s.missing, { color: colors.muted }]}>This piece isn't available.</Text>
          ) : (
            <>
              <Text style={[s.title, { color: colors.ink }]}>{piece.title}</Text>
              {!!piece.subtitle && (
                <Text style={[s.subtitle, { color: colors.muted }]}>{piece.subtitle}</Text>
              )}
              <ProseSegments
                segments={piece.segments}
                heSize={hebrewFontSize(fontStep)}
                enSize={englishFontSize(fontStep)}
                colors={colors}
              />
            </>
          )}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    body: { paddingHorizontal: 22, paddingTop: 16, paddingBottom: 80 },
    backText: { fontFamily: Fonts.uiMedium, fontSize: 15, marginBottom: 12 },
    title: { fontFamily: Fonts.englishBold, fontSize: 23, lineHeight: 30, marginBottom: 4 },
    subtitle: { fontFamily: Fonts.englishItalic, fontSize: 14.5, marginBottom: 14 },
    missing: { fontFamily: Fonts.ui, fontSize: 14, textAlign: 'center', marginTop: 60 },
  });
}
```

- [ ] **Step 3: Verify**

Run: `npm run check` (green). Simulator: home → About this Siddur → all six rows open and read cleanly (check the teen intro end-to-end: paragraph breaks sane, Hebrew phrases render RTL, the closing אמן כן יהי רצון line shows as Hebrew). Back navigation works at both levels.

- [ ] **Step 4: Commit**

```bash
git add app/about
git commit -m "feat: About this Siddur screens (TOC + piece reader)"
```

---

### Task 11: Docs + final gate

**Files:**
- Modify: `CLAUDE.md`, `docs/CONTENT_GUIDE.md`, `docs/REVIEW_QUEUE.md`

- [ ] **Step 1: Update CLAUDE.md**

In the **Content registry** bullet, after the appendices sentence, add:

```markdown
Book front/back matter loads via `src/content/bookMatter.ts` (`book-matter.json`; About screens), the glossary via `src/content/glossary.ts` (`glossary.json`; no segments — outside the segment contract).
```

In the **App architecture** intro sentence listing routes, extend with `about/` and `glossary.tsx`, and note the home screen is grouped via `src/content/categories.ts` (new services must be added there too — the categories test enforces it).

- [ ] **Step 2: Update CONTENT_GUIDE.md**

Add a short section "Book matter & glossary" stating: book-matter pieces are `Segment[]` and are linted like all content (prose = `commentary`, standalone Hebrew lines = `prayer`, interior headings = `header`); glossary.json is `{entries: [{term, definition}]}`, print order, outside the segment contract; both are digitized only via their `scripts/extract_*.py` scripts and proofed against 300 DPI renders.

- [ ] **Step 3: Update REVIEW_QUEUE.md**

Add under a "Book matter (2026-07-02)" heading:
- Front/back matter + glossary digitized (`scripts/extract_book_matter.py`, `scripts/extract_glossary.py`) — human spot-check of the six About pieces against the print recommended before release.
- Future zmanim round: Hebcal REST API selected (CC-BY 4.0 — attribution line required in Settings/About when it ships); sof zman Krias Shema shown as MGA or GRA is an author decision.

- [ ] **Step 4: Final gate + commit**

Run: `npm run check`
Expected: typecheck clean; lint 0 errors; all jest suites pass.

```bash
git add CLAUDE.md docs/CONTENT_GUIDE.md docs/REVIEW_QUEUE.md
git commit -m "docs: register book matter, glossary, and home categories in the guides"
```

---

## Future Round (documented only — do NOT build now): Smart Surfacing + Zmanim

**Zmanim source — decision: Hebcal hosted Zmanim REST API.**
- `GET https://www.hebcal.com/zmanim?cfg=json&latitude=<lat>&longitude=<lng>&tzid=<tz>&start=YYYY-MM-DD&end=YYYY-MM-DD` — free, **no API key**, JSON, batch capped at 180 days. Also accepts `geonameid` or US `zip`. `&sec=1` for second precision.
- Returns all needed keys: `sofZmanShma`, `sofZmanShmaMGA`, `minchaGedola`, `sunset`, `tzeit7083deg` (and alos, misheyakir, chatzot, plag, etc.), ISO 8601 with timezone.
- **Terms:** output is CC-BY 4.0 → the app must credit Hebcal.com (one line in Settings or About). No rate limits published; batch requests keep usage tiny (≈12 calls/user/year).
- **Why not a bundled library:** `@hebcal/core` and `@hebcal/hdate` are GPL-2.0; `kosher-zmanim` is LGPL-3.0. The app ships copyrighted book content that cannot be open-sourced, so copyleft dependencies are off the table. A hosted API imposes no license on the app code.
- **Offline design:** on launch with network, prefetch a 30-day batch for the user's location into AsyncStorage (`siddur-zmanim-cache`: `{location, fetchedAt, days: Record<date, times>}`); render the NowCard strip from cache; refetch when <7 days remain. No cache + no network → strip hidden (card layout unaffected). Location via `expo-location` when-in-use, with a manual city fallback (geonameid search) for users who decline the permission.
- **Suggested service / Today badges:** run locally on `src/lib/hebrewDate.ts` (Rosh Chodesh = day 30 or day 1; Omer = 16 Nisan–5 Sivan; Sukkos/Chanukah etc. derivable) + clock vs cached sunset. Rules per the design spec — badge and float to top of Special Days, never hide.

## Execution order & dependencies

Tasks 2–4 are independent of each other (all before 5). Task 5 needs 2+3+4. Task 6 is independent. Task 7 before 8; Task 9 needs nothing but should precede 10; Task 10 needs 6+9. Task 11 last.
