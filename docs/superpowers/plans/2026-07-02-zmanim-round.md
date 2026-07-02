# Zmanim Round Implementation Plan (Hebcal API + Smart Surfacing)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the NowCard's designed end state — suggested current service with "Daven now" CTA, a four-cell zmanim strip fed by the free Hebcal REST API with offline caching, and Today/Tonight badges on Special Days — per the future-round section of `docs/superpowers/specs/2026-07-02-home-page-reorg-design.md`.

**Architecture:** A zustand-persisted zmanim store caches a 30-day batch from Hebcal keyed by date; a location module resolves device location (expo-location, when-in-use) with a manual city-search fallback (Hebcal's public autocomplete endpoint). Pure, tested rule modules (`suggestService`, `specialDays`) run on the local Hebrew-date converter plus cached sunset. UI consumes only the stores/rules — no fetch in components.

**Tech Stack:** Expo SDK 56 (`expo-location` via `npx expo install`), zustand + AsyncStorage, Hebcal Zmanim REST API (no key; output CC-BY 4.0 → attribution line in Settings), jest with mocked fetch.

## Global Constraints

- **User decisions (locked):** sof zman Krias Shema = **GRA** (`sofZmanShma`); tzeis = **8.5°** (`tzeit85deg`); location = **device permission with manual city fallback**.
- Strip cells, in order: Krias Shema · Minchah Gedolah (`minchaGedola`) · Shkiah (`sunset`) · Tzeis (`tzeit85deg`).
- **No GPL/LGPL dependencies.** All halachic-calendar logic stays in our own `src/lib/` (hebrewDate.ts already exists); network zmanim only from Hebcal's hosted API.
- **Offline-first:** UI renders from cache only. No cache → strip hidden, CTA falls back to clock heuristics; nothing blocks or spins on network.
- **Never hide services.** Badges promote entries to the top of Special Days; every service stays listed.
- **Diaspora (chutz la'aretz) calendar rules** — the siddur's audience. Israel mode is out of scope; log it in REVIEW_QUEUE.
- **Attribution:** "Zmanim powered by Hebcal.com" must ship in Settings this round (CC-BY 4.0).
- Times display as the location's wall clock by slicing the ISO string's `HH:MM` (Hebcal returns location-local offsets) — no timezone math, no `Intl`.
- Run `npm run check` before every commit. Expo SDK 56 docs at https://docs.expo.dev/versions/v56.0.0/ (check `expo-location` API there, not from memory).

---

### Task 1: Zmanim store — Hebcal client + 30-day cache

**Files:**
- Create: `src/store/zmanim.ts`
- Test: `src/store/__tests__/zmanim.test.ts`

**Interfaces:**
- Produces:
  ```ts
  interface ZmanimLocation { latitude: number; longitude: number; tzid: string; label: string }
  interface DayZmanim { sofZmanShma: string; minchaGedola: string; sunset: string; tzeit85deg: string } // ISO strings with offset
  useZmanimStore: {
    location: ZmanimLocation | null;
    days: Record<string, DayZmanim>;      // key 'YYYY-MM-DD'
    fetchedThrough: string | null;         // last cached date
    setLocation(loc: ZmanimLocation): void;   // clears days (new location invalidates cache)
    ensureFresh(todayKey: string): Promise<void>; // fetches 30-day batch if <7 days of cache remain; no-op without location; swallows network errors
    zmanimFor(dateKey: string): DayZmanim | null;
  }
  export function hebcalZmanimUrl(loc: ZmanimLocation, start: string, end: string): string
  export function dateKey(d: Date): string  // local 'YYYY-MM-DD', no Intl
  ```

- [ ] **Step 0: Probe the real batch response shape**

`curl -s "https://www.hebcal.com/zmanim?cfg=json&latitude=43.85&longitude=-79.45&tzid=America/Toronto&start=2026-07-02&end=2026-07-03"` — confirm the batch shape is `times: { <zman>: { <date>: <iso> } }` and that `sofZmanShma`, `minchaGedola`, `sunset`, `tzeit85deg` all appear. If the shape differs, adapt the fixture below and the parser to reality and record it in your report.

- [ ] **Step 1: Write the failing tests**

```ts
// src/store/__tests__/zmanim.test.ts
import { useZmanimStore, hebcalZmanimUrl, dateKey } from '../zmanim';

const LOC = { latitude: 43.85, longitude: -79.45, tzid: 'America/Toronto', label: 'Thornhill' };

// Minimal Hebcal batch response shape (times keyed by zman, then by date).
const HEBCAL_RESPONSE = {
  times: {
    sofZmanShma: { '2026-07-02': '2026-07-02T09:14:00-04:00', '2026-07-03': '2026-07-03T09:14:00-04:00' },
    minchaGedola: { '2026-07-02': '2026-07-02T13:45:00-04:00', '2026-07-03': '2026-07-03T13:45:00-04:00' },
    sunset: { '2026-07-02': '2026-07-02T20:44:00-04:00', '2026-07-03': '2026-07-03T20:44:00-04:00' },
    tzeit85deg: { '2026-07-02': '2026-07-02T21:26:00-04:00', '2026-07-03': '2026-07-03T21:26:00-04:00' },
  },
};

beforeEach(() => {
  useZmanimStore.setState({ location: null, days: {}, fetchedThrough: null });
  global.fetch = jest.fn(async () => ({ ok: true, json: async () => HEBCAL_RESPONSE })) as any;
});

test('dateKey formats local date without Intl', () => {
  expect(dateKey(new Date(2026, 6, 2))).toBe('2026-07-02');
  expect(dateKey(new Date(2026, 0, 9))).toBe('2026-01-09');
});

test('hebcalZmanimUrl carries location, range, and json cfg', () => {
  const url = hebcalZmanimUrl(LOC, '2026-07-02', '2026-08-01');
  expect(url).toContain('https://www.hebcal.com/zmanim?cfg=json');
  expect(url).toContain('latitude=43.85');
  expect(url).toContain('longitude=-79.45');
  expect(url).toContain('tzid=America%2FToronto');
  expect(url).toContain('start=2026-07-02');
  expect(url).toContain('end=2026-08-01');
});

test('ensureFresh is a no-op without a location', async () => {
  await useZmanimStore.getState().ensureFresh('2026-07-02');
  expect(global.fetch).not.toHaveBeenCalled();
});

test('ensureFresh fetches a batch and indexes it by date', async () => {
  useZmanimStore.getState().setLocation(LOC);
  await useZmanimStore.getState().ensureFresh('2026-07-02');
  expect(global.fetch).toHaveBeenCalledTimes(1);
  const day = useZmanimStore.getState().zmanimFor('2026-07-02');
  expect(day?.sunset).toBe('2026-07-02T20:44:00-04:00');
  expect(useZmanimStore.getState().fetchedThrough).toBe('2026-07-03');
});

test('ensureFresh skips fetch while >=7 days of cache remain', async () => {
  useZmanimStore.getState().setLocation(LOC);
  useZmanimStore.setState({ fetchedThrough: '2026-07-20' });
  await useZmanimStore.getState().ensureFresh('2026-07-02');
  expect(global.fetch).not.toHaveBeenCalled();
});

test('ensureFresh swallows network errors and keeps existing cache', async () => {
  useZmanimStore.getState().setLocation(LOC);
  useZmanimStore.setState({ days: { '2026-07-02': HEBCAL_RESPONSE.times as any } as any });
  (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('offline'));
  await expect(useZmanimStore.getState().ensureFresh('2026-07-02')).resolves.toBeUndefined();
});

test('setLocation clears the previous cache', () => {
  useZmanimStore.setState({ days: { '2026-07-02': {} as any }, fetchedThrough: '2026-07-31' });
  useZmanimStore.getState().setLocation(LOC);
  expect(useZmanimStore.getState().days).toEqual({});
  expect(useZmanimStore.getState().fetchedThrough).toBeNull();
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx jest src/store/__tests__/zmanim.test.ts` — expected: module not found.

- [ ] **Step 3: Implement**

```ts
// src/store/zmanim.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Offline-first zmanim cache fed by the Hebcal Zmanim REST API (free, no key;
// output CC-BY 4.0 — attribution lives in Settings). UI reads only the cache;
// ensureFresh() tops it up in the background and silently tolerates offline.
export interface ZmanimLocation {
  latitude: number;
  longitude: number;
  tzid: string;
  label: string; // human-readable, e.g. "Thornhill"
}

export interface DayZmanim {
  sofZmanShma: string;   // GRA — user decision 2026-07-02
  minchaGedola: string;
  sunset: string;
  tzeit85deg: string;    // 8.5° — user decision 2026-07-02
}

const ZMANIM_KEYS = ['sofZmanShma', 'minchaGedola', 'sunset', 'tzeit85deg'] as const;
const BATCH_DAYS = 30;
const REFRESH_WHEN_REMAINING = 7;

export function dateKey(d: Date): string {
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

function addDays(key: string, n: number): string {
  const [y, m, d] = key.split('-').map(Number);
  return dateKey(new Date(y, m - 1, d + n));
}

export function hebcalZmanimUrl(loc: ZmanimLocation, start: string, end: string): string {
  const q = new URLSearchParams({
    cfg: 'json',
    latitude: String(loc.latitude),
    longitude: String(loc.longitude),
    tzid: loc.tzid,
    start,
    end,
  });
  return `https://www.hebcal.com/zmanim?${q.toString()}`;
}

interface ZmanimState {
  location: ZmanimLocation | null;
  days: Record<string, DayZmanim>;
  fetchedThrough: string | null;
  setLocation: (loc: ZmanimLocation) => void;
  ensureFresh: (todayKey: string) => Promise<void>;
  zmanimFor: (dateKey: string) => DayZmanim | null;
}

export const useZmanimStore = create<ZmanimState>()(
  persist(
    (set, get) => ({
      location: null,
      days: {},
      fetchedThrough: null,
      setLocation: (location) => set({ location, days: {}, fetchedThrough: null }),
      ensureFresh: async (todayKey) => {
        const { location, fetchedThrough } = get();
        if (!location) return;
        if (fetchedThrough && addDays(todayKey, REFRESH_WHEN_REMAINING) <= fetchedThrough) return;
        const end = addDays(todayKey, BATCH_DAYS - 1);
        try {
          const res = await fetch(hebcalZmanimUrl(location, todayKey, end));
          if (!res.ok) return;
          const json = (await res.json()) as { times?: Record<string, Record<string, string>> };
          if (!json.times) return;
          const days: Record<string, DayZmanim> = { ...get().days };
          const dates = Object.keys(json.times[ZMANIM_KEYS[0]] ?? {});
          for (const date of dates) {
            const entry = {} as DayZmanim;
            for (const key of ZMANIM_KEYS) {
              const value = json.times[key]?.[date];
              if (typeof value !== 'string') return; // malformed response — keep old cache
              entry[key] = value;
            }
            days[date] = entry;
          }
          const last = dates.sort().at(-1) ?? null;
          set({ days, fetchedThrough: last });
        } catch {
          // Offline or API hiccup — cache (possibly stale) keeps serving.
        }
      },
      zmanimFor: (key) => get().days[key] ?? null,
    }),
    {
      name: 'siddur-zmanim',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
```

- [ ] **Step 4: Run tests to verify they pass** — `npx jest src/store/__tests__/zmanim.test.ts`, then `npm run check`.

- [ ] **Step 5: Commit** — `feat: zmanim store with Hebcal batch cache`

---

### Task 2: Location module + expo-location dependency

**Files:**
- Create: `src/lib/location.ts`
- Test: `src/lib/__tests__/location.test.ts`
- Modify: `package.json` (via `npx expo install expo-location`), `app.json` if a location-usage string is required (check SDK 56 docs — iOS needs `NSLocationWhenInUseUsageDescription` via the expo-location config plugin)

**Interfaces:**
- Produces:
  ```ts
  resolveDeviceLocation(): Promise<ZmanimLocation | null>  // permission ask + reverse geocode label + device tzid; null if denied/unavailable
  searchCities(query: string): Promise<ZmanimLocation[]>   // Hebcal public autocomplete (verify endpoint at implementation time; expected https://www.hebcal.com/complete.php?q=<query> returning geo items with latitude/longitude/timezone)
  ```

- [ ] **Step 1: Install dependency** — `npx expo install expo-location`; add the config plugin with an iOS purpose string: "Your location is used only to calculate accurate halachic times (zmanim) for where you are." Run `npm run check` to confirm nothing breaks.

- [ ] **Step 2: Probe the autocomplete endpoint** — `curl -s "https://www.hebcal.com/complete.php?q=thornhill"` and record the real response shape. If the endpoint differs (fields, nesting), adapt `searchCities` and its test fixture to reality and note it in the report.

- [ ] **Step 3: Failing tests** (mock `expo-location` and `fetch`)

```ts
// src/lib/__tests__/location.test.ts
import { searchCities } from '../location';

// Fixture shape from the Step 2 probe — REPLACE with the recorded real shape.
const COMPLETE_RESPONSE = [
  { id: 6165718, value: 'Thornhill, Ontario, Canada', latitude: 43.8161, longitude: -79.4269, timezone: 'America/Toronto' },
];

beforeEach(() => {
  global.fetch = jest.fn(async () => ({ ok: true, json: async () => COMPLETE_RESPONSE })) as any;
});

test('searchCities maps autocomplete hits to ZmanimLocation', async () => {
  const results = await searchCities('thornhill');
  expect(results[0]).toEqual({
    latitude: 43.8161,
    longitude: -79.4269,
    tzid: 'America/Toronto',
    label: 'Thornhill, Ontario, Canada',
  });
});

test('searchCities returns [] on network failure', async () => {
  (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('offline'));
  await expect(searchCities('x')).resolves.toEqual([]);
});

test('searchCities drops hits missing coordinates or timezone', async () => {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    json: async () => [{ value: 'Nowhere' }],
  });
  await expect(searchCities('nowhere')).resolves.toEqual([]);
});
```

- [ ] **Step 4: Implement**

```ts
// src/lib/location.ts
import * as Location from 'expo-location';
import { ZmanimLocation } from '../store/zmanim';

// Device path: when-in-use permission → coarse position → reverse-geocoded
// city label. Returns null on any denial/failure — callers fall back to
// manual city search. Never throws.
export async function resolveDeviceLocation(): Promise<ZmanimLocation | null> {
  try {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') return null;
    const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Low });
    const tzid = Intl?.DateTimeFormat?.().resolvedOptions?.().timeZone ?? 'UTC';
    let label = 'Current location';
    try {
      const places = await Location.reverseGeocodeAsync(pos.coords);
      const p = places[0];
      if (p?.city) label = p.city;
    } catch {
      // keep generic label
    }
    return { latitude: pos.coords.latitude, longitude: pos.coords.longitude, tzid, label };
  } catch {
    return null;
  }
}

// Manual fallback: Hebcal's public city autocomplete (same source as
// hebcal.com's own search box). Shape verified by probe on 2026-07-02 —
// adjust mapping if the endpoint changes.
export async function searchCities(query: string): Promise<ZmanimLocation[]> {
  try {
    const res = await fetch(`https://www.hebcal.com/complete.php?q=${encodeURIComponent(query)}`);
    if (!res.ok) return [];
    const hits = (await res.json()) as Array<{
      value?: string; latitude?: number; longitude?: number; timezone?: string;
    }>;
    return hits
      .filter((h) => typeof h.latitude === 'number' && typeof h.longitude === 'number' && !!h.timezone)
      .map((h) => ({
        latitude: h.latitude!,
        longitude: h.longitude!,
        tzid: h.timezone!,
        label: h.value ?? 'Unknown',
      }));
  } catch {
    return [];
  }
}
```

Note on `tzid`: device timezone via bare `Intl.DateTimeFormat().resolvedOptions().timeZone` is the ONE Intl use we allow — it's supported by Hermes on both platforms (verify in the SDK 56/Hermes docs during implementation; if unsupported, use `expo-localization`'s `getCalendars()[0].timeZone` instead — `npx expo install expo-localization`). Record which path was used.

- [ ] **Step 5: Tests + check + commit** — `feat: device + manual-search location resolution for zmanim`

---

### Task 3: Special-days rules (badges)

**Files:**
- Create: `src/lib/specialDays.ts`
- Test: `src/lib/__tests__/specialDays.test.ts`
- Modify: `src/lib/hebrewDate.ts` — export `lastDayOfHebrewMonth` (currently module-private) for Kislev-length logic.

**Interfaces:**
- Produces: `specialDayBadges(civilDate: Date): Record<string, string>` — map of serviceId → badge label for that civil day, diaspora rules. Example: `{ 'sefiras-haomer': 'Tonight', 'mussaf-rosh-chodesh': 'Today', 'hallel': 'Today' }`.

Rules (diaspora; document each with its source comment):
- **sefiras-haomer → "Tonight"** when *tomorrow's* Hebrew date (the day that begins tonight) is in 16 Nisan–5 Sivan inclusive (months 1/2/3: `(m===1 && d>=16) || m===2 || (m===3 && d<=5)`).
- **mussaf-rosh-chodesh → "Today"** on 30th of any month or 1st of any month except 1 Tishrei.
- **mussaf-chol-hamoed → "Today"** on 17–20 Nisan or 17–21 Tishrei.
- **hallel → "Today"** on Rosh Chodesh, Chol Hamoed (above), all Pesach/Sukkos/Shavuos days the app can see (15–21 Nisan; 15–22 Tishrei incl. Shmini Atzeres/Simchas Torah 22–23? cap at what's defensible: 15–23 Tishrei), and Chanukah (25 Kislev through 2 Teves when Kislev has 30 days, through 3 Teves when Kislev has 29 — use `lastDayOfHebrewMonth(year, 9)`).
- **netilas-lulav → "Today"** on 15–21 Tishrei except when the civil day is Saturday.
- **maariv-motzaei-shabbos → "Tonight"** when the civil day is Saturday.

- [ ] **Step 1: Failing tests** — pin known dates (all verifiable against a luach; if any assertion surprises you, re-derive by hand before changing the rule):

```ts
// src/lib/__tests__/specialDays.test.ts
import { specialDayBadges } from '../specialDays';

test('plain weekday has no badges', () => {
  expect(specialDayBadges(new Date(2026, 6, 1))).toEqual({}); // Wed 1 Jul 2026 = 16 Tammuz 5786
});

test('Saturday gets motzaei-shabbos Tonight', () => {
  expect(specialDayBadges(new Date(2026, 6, 4))['maariv-motzaei-shabbos']).toBe('Tonight');
});

test('Rosh Chodesh gets mussaf + hallel', () => {
  // 1 Av 5786 = 15 Jul 2026 (verify via hebcal converter during implementation)
  const badges = specialDayBadges(new Date(2026, 6, 15));
  expect(badges['mussaf-rosh-chodesh']).toBe('Today');
  expect(badges['hallel']).toBe('Today');
});

test('Omer period gets sefirah Tonight (evening begins next Hebrew day)', () => {
  // 30 Apr 2026 = 13 Iyar 5786 → tonight begins 14 Iyar, within the Omer
  expect(specialDayBadges(new Date(2026, 3, 30))['sefiras-haomer']).toBe('Tonight');
  // 24 May 2026 = 8 Sivan → Omer over
  expect(specialDayBadges(new Date(2026, 4, 24))['sefiras-haomer']).toBeUndefined();
});

test('Chol Hamoed Sukkos gets mussaf-chol-hamoed + hallel + lulav', () => {
  // 17 Tishrei 5787 = 28 Sep 2026 (Monday — verify)
  const badges = specialDayBadges(new Date(2026, 8, 28));
  expect(badges['mussaf-chol-hamoed']).toBe('Today');
  expect(badges['hallel']).toBe('Today');
  expect(badges['netilas-lulav']).toBe('Today');
});

test('no lulav on Shabbos even during Sukkos', () => {
  // Find the Shabbos within 15–21 Tishrei 5787 (verify actual date) and assert
  // netilas-lulav is absent while hallel is still present.
  const shabbosSukkos = new Date(2026, 9, 3); // placeholder — set to the real Shabbos date during implementation
  const badges = specialDayBadges(shabbosSukkos);
  expect(badges['netilas-lulav']).toBeUndefined();
});
```

**Every pinned civil↔Hebrew date above must be verified against `https://www.hebcal.com/converter?cfg=json&gy=...&g2h=1` during implementation; fix the test values (not the rules) if a pin is off.**

- [ ] **Step 2: Implement** (pure function over `fromGregorian`; ~60 lines with rule-source comments), export `lastDayOfHebrewMonth` from hebrewDate.

- [ ] **Step 3: Tests + `npm run check` + commit** — `feat: diaspora special-day badge rules`

---

### Task 4: Suggested-service rule

**Files:**
- Create: `src/lib/suggestService.ts`
- Test: `src/lib/__tests__/suggestService.test.ts`

**Interfaces:**
- Produces: `suggestService(now: Date, dayZmanim: { sunset: string } | null): string` — returns a service id:
  - After shkiah (or ≥19:30 fallback when no zmanim): Saturday → `maariv-motzaei-shabbos`, else `maariv`.
  - Midday boundary 13:00 (or `minchaGedola` when provided — accept optional field): before → `shacharit`, after → `minchah`.
  - Wall-clock comparisons against ISO zmanim use the HH:MM slice (chars 11–16) vs the device clock's HH:MM — document the assumption device tz == location tz (true except mid-travel; acceptable v1, note in REVIEW_QUEUE).

- [ ] **Step 1: Failing tests**

```ts
// src/lib/__tests__/suggestService.test.ts
import { suggestService } from '../suggestService';

const Z = { sunset: '2026-07-02T20:44:00-04:00', minchaGedola: '2026-07-02T13:45:00-04:00' };

test('morning suggests shacharis', () => {
  expect(suggestService(new Date(2026, 6, 2, 7, 30), Z)).toBe('shacharit');
});
test('after minchaGedola suggests minchah', () => {
  expect(suggestService(new Date(2026, 6, 2, 14, 0), Z)).toBe('minchah');
});
test('after shkiah suggests maariv', () => {
  expect(suggestService(new Date(2026, 6, 2, 21, 0), Z)).toBe('maariv');
});
test('Saturday night suggests motzaei-shabbos maariv', () => {
  expect(suggestService(new Date(2026, 6, 4, 22, 0), Z)).toBe('maariv-motzaei-shabbos');
});
test('no zmanim: clock fallback boundaries 13:00 / 19:30', () => {
  expect(suggestService(new Date(2026, 6, 2, 12, 59), null)).toBe('shacharit');
  expect(suggestService(new Date(2026, 6, 2, 13, 1), null)).toBe('minchah');
  expect(suggestService(new Date(2026, 6, 2, 19, 31), null)).toBe('maariv');
});
```

- [ ] **Step 2: Implement** (pure, ~35 lines). **Step 3: check + commit** — `feat: time-of-day service suggestion`

---

### Task 5: NowCard end state + home badges

**Files:**
- Modify: `src/components/NowCard.tsx` — add suggested-service row (`en+he titles from getService(suggestService(...))`, "Daven now →" accent button navigating to the service) and the zmanim strip (4 cells in an `accentSoft` full-bleed footer inside the card, per the approved Variant A mockup: value `formatZmanTime(iso)` = HH:MM→`h:MM` 12-hour, label uppercase micro-text: KRIAS SHEMA / MIN. GEDOLAH / SHKIAH / TZEIS). Strip renders only when `zmanimFor(dateKey(now))` returns data. `ensureFresh(dateKey(now))` fires from a NowCard effect on mount/focus (fire-and-forget). Resume link stays, under the CTA row, smaller.
- Modify: `app/daven/index.tsx` — compute `specialDayBadges(new Date())` once per render; in Special Days section: attach a gold `badge` pill (existing `goldFill`/`rubric` tokens, matching the mockup) to badged rows and stable-sort badged rows to the top of that section only.
- Create: `src/lib/formatZmanTime.ts` + test — `('2026-07-02T09:14:00-04:00') → '9:14'`, `('...T13:45...') → '1:45'`, `('...T00:05...') → '12:05'`.
- First-run location: if `useZmanimStore.location` is null, NowCard shows a one-line muted link under the date row — "Set location for zmanim →" — navigating to `/settings`. No permission prompt fires from the home screen; the ask happens in Settings (Task 6). (Quiet-by-default: a davening app must not open with a system dialog.)

- [ ] Steps: implement → `npm run check` → controller sim-verifies (with and without a configured location) → commit `feat: NowCard zmanim strip + daven-now CTA + special-day badges`.

---

### Task 6: Settings — location row + attribution; docs

**Files:**
- Modify: `app/settings.tsx` — new "Zmanim" section: current location label (or "Not set"); "Use my location" button → `resolveDeviceLocation()` → `setLocation` (busy state while resolving; on null show inline "Couldn't get location — search below"); a city search field → `searchCities` (debounced ≥300ms) → tappable results → `setLocation`. Footer line in the section: "Zmanim powered by Hebcal.com" (plain text + the URL per CC-BY).
- Modify: `docs/REVIEW_QUEUE.md` — mark the zmanim-source item shipped; add: Israel-mode calendar rules out of scope; device-tz==location-tz assumption; suggested-service boundary opinions (13:00 fallback etc.) are v1 heuristics.
- Modify: `CLAUDE.md` (one line: zmanim store/lib modules + the no-Intl exception note) and `docs/superpowers/specs/2026-07-02-home-page-reorg-design.md` "What ships" table (zmanim rows → shipped 2026-07-02).

- [ ] Steps: implement → `npm run check` → controller sim-verifies Settings flow → commit `feat: zmanim location settings + Hebcal attribution` / `docs: register zmanim round`.

---

## Execution notes

Tasks 1→2 ordered (2 imports `ZmanimLocation` from 1); 3 and 4 independent of 1–2; 5 needs 1+3+4; 6 needs 1+2. Final whole-branch review after Task 6, most capable model, with special attention to: rule-module correctness vs a luach, cache staleness behavior across location changes, and that no network call blocks first paint.
