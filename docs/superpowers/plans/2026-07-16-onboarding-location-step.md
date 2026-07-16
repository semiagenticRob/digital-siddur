# Onboarding Location Permission Step Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ask for when-in-use location permission on a dedicated onboarding step right after the welcome screen, falling back to inline city search when denied.

**Architecture:** Two tasks. Task 1 extracts the city-search state machine out of `app/settings.tsx` into `src/components/CitySearch.tsx` with no behavior change, so the debounce and stale-guard exist once. Task 2 adds a `'location'` step to the `app/onboarding.tsx` wizard that calls the existing `resolveDeviceLocation()` and renders `CitySearch` on denial.

**Tech Stack:** Expo SDK 56, React Native 0.85, React 19, Expo Router v4, Zustand + AsyncStorage, TypeScript strict.

**Spec:** `docs/superpowers/specs/2026-07-16-onboarding-location-step-design.md`

## Global Constraints

- **No new dependencies.** Not one. The permission plumbing already exists.
- **Do not modify** `app.json`, `src/store/zmanim.ts`, or `src/lib/location.ts`. The `expo-location` plugin and its `locationWhenInUsePermission` string are already correct and scoped to when-in-use.
- **Never call `expo-location` directly** from a screen. Go through `resolveDeviceLocation()` in `src/lib/location.ts`, which returns `null` on any denial or failure and never throws.
- **Expo SDK 56 differs from older Expo APIs in training data.** Check https://docs.expo.dev/versions/v56.0.0/ before writing runtime code.
- TypeScript is `strict: true`. `npm run check` (typecheck + strict content lint + jest) must pass before every commit.
- This repo has **no component-testing library** (no `@testing-library/react-native`, no `react-test-renderer`) and this plan does not add one. The concurrency-critical seam is `searchCities()`, already covered by `src/lib/__tests__/location.test.ts` and untouched here. Both tasks are view code, verified by typecheck + manual simulator run (**user decision, 2026-07-16** — Playwright was considered and rejected: it cannot drive the iOS simulator, and Expo web would exercise the browser geolocation API rather than the native prompt this feature is about).

---

### Task 1: Extract `CitySearch` from Settings

A move, not a redesign. Settings' Zmanim section must look and behave exactly as it does
now, with one exception: the three enumerated select-handler bug fixes in Step 1, which
are edge cases the happy path won't show. Nothing in onboarding changes yet.

**Files:**
- Create: `src/components/CitySearch.tsx`
- Modify: `app/settings.tsx` (remove search state at `:14`, `:24-38`, `:57-98`; remove search JSX at `:219-247`; remove styles `cityInput`/`cityResult` at `:294-309`)

**Interfaces:**
- Consumes: `searchCities(query: string): Promise<ZmanimLocation[] | null>` from `src/lib/location.ts` — returns `null` when the search itself failed (offline), `[]` when it succeeded with no hits. That distinction drives two different empty states; preserve it.
- Produces: `CitySearch` component, used by Task 2.

```ts
interface CitySearchProps {
  colors: ColorPalette;
  onSelect: (loc: ZmanimLocation) => void;
  onQueryChange?: () => void;
}
export function CitySearch(props: CitySearchProps): JSX.Element
```

`onQueryChange` exists because `app/settings.tsx:59` currently calls `setLocateError(false)` when the user types — typing dismisses the "Couldn't get your location" error. Once the query lives inside `CitySearch`, Settings can no longer see it. This callback preserves that behavior. It is optional; onboarding does not pass it.

- [ ] **Step 1: Create `src/components/CitySearch.tsx`**

This is the code from `app/settings.tsx` with three deliberate fixes in `handleSelect`, called out after the block.

```tsx
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet } from 'react-native';
import { ZmanimLocation } from '../store/zmanim';
import { searchCities } from '../lib/location';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';

const SEARCH_DEBOUNCE_MS = 350;

interface CitySearchProps {
  colors: ColorPalette;
  onSelect: (loc: ZmanimLocation) => void;
  // Settings uses this to clear its "couldn't locate you" error as soon as
  // the user starts typing; the query itself lives in here, so the parent
  // can't watch it directly.
  onQueryChange?: () => void;
}

export function CitySearch({ colors, onSelect, onQueryChange }: CitySearchProps) {
  const s = makeStyles(colors);
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<ZmanimLocation[]>([]);
  const [searched, setSearched] = useState(false);
  const [searchFailed, setSearchFailed] = useState(false);
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const searchSeq = useRef(0);

  // On unmount: cancel the pending debounce timer, and bump the seq so any
  // in-flight searchCities response is dropped by the stale-guard instead of
  // calling setState on an unmounted component.
  useEffect(() => () => {
    if (searchTimer.current) clearTimeout(searchTimer.current);
    searchSeq.current += 1;
  }, []);

  const handleQueryChange = (text: string) => {
    setQuery(text);
    onQueryChange?.();
    if (searchTimer.current) clearTimeout(searchTimer.current);
    const trimmed = text.trim();
    if (!trimmed) {
      setResults([]);
      setSearching(false);
      setSearched(false);
      setSearchFailed(false);
      return;
    }
    setSearching(true);
    setSearched(false);
    setSearchFailed(false);
    const seq = ++searchSeq.current;
    searchTimer.current = setTimeout(async () => {
      try {
        const hits = await searchCities(trimmed);
        if (seq !== searchSeq.current) return; // stale — a newer search superseded this one
        setResults(hits ?? []);
        setSearchFailed(hits === null);
      } catch {
        if (seq !== searchSeq.current) return;
        setResults([]);
        setSearchFailed(true);
      } finally {
        if (seq === searchSeq.current) {
          setSearching(false);
          setSearched(true);
        }
      }
    }, SEARCH_DEBOUNCE_MS);
  };

  const handleSelect = (loc: ZmanimLocation) => {
    // Cancel the pending debounce and retire the seq so a response that is
    // still in flight can't repopulate the list we're about to clear.
    if (searchTimer.current) clearTimeout(searchTimer.current);
    searchSeq.current += 1;
    setQuery('');
    setResults([]);
    setSearching(false);
    setSearched(false);
    setSearchFailed(false);
    onSelect(loc);
  };

  return (
    <View>
      <TextInput
        style={[s.cityInput, { backgroundColor: colors.surface, borderColor: colors.line, color: colors.ink }]}
        value={query}
        onChangeText={handleQueryChange}
        placeholder="Search for a city…"
        placeholderTextColor={colors.muted}
        accessibilityLabel="Search for a city"
      />

      {searching && (
        <Text style={[s.hint, { color: colors.muted }]}>Searching…</Text>
      )}
      {!searching && searched && results.length === 0 && (
        <Text style={[s.hint, { color: colors.muted }]}>
          {searchFailed ? "Couldn't search — check your connection." : 'No cities found'}
        </Text>
      )}

      {results.map((r, i) => (
        <Pressable
          key={`${r.label}-${r.latitude}-${r.longitude}-${i}`}
          style={[s.cityResult, { backgroundColor: colors.surface, borderColor: colors.line }]}
          onPress={() => handleSelect(r)}
          accessibilityRole="button"
          accessibilityLabel={`Set location to ${r.label}`}
        >
          <Text style={[s.cityLabel, { color: colors.ink }]}>{r.label}</Text>
        </Pressable>
      ))}
    </View>
  );
}

function makeStyles(_c: ColorPalette) {
  return StyleSheet.create({
    cityInput: {
      borderWidth: 1,
      borderRadius: 10,
      paddingHorizontal: 12,
      paddingVertical: 10,
      fontFamily: Fonts.ui,
      fontSize: 14,
      marginTop: 10,
    },
    cityResult: {
      borderWidth: 1,
      borderRadius: 10,
      paddingHorizontal: 12,
      paddingVertical: 10,
      marginTop: 8,
    },
    cityLabel: { fontFamily: Fonts.uiMedium, fontSize: 14 },
    hint: { fontFamily: Fonts.ui, fontSize: 12, marginTop: 8 },
  });
}
```

Three intentional deviations from the code being moved, all in `handleSelect`:

1. **Clears the pending debounce timer.** The original left it running, so a select immediately after typing could fire a search for the abandoned query.
2. **Bumps `searchSeq`.** The original cleared `results` but left the in-flight response ungated, so a slow response landing after a select would repopulate the list the user just dismissed.
3. **Sets `searching` to `false`.** Follows from fix 2 — with the seq retired, the `finally` block's guard no longer runs, so `searching` would otherwise stay `true` forever and pin "Searching…" on screen.

These are bugs in code this task is already rewriting. Do not go looking for others.

`makeStyles` takes `_c` and ignores it, matching `app/settings.tsx:269` which does the same. The underscore marks it deliberate.

- [ ] **Step 2: Typecheck the new component in isolation**

Run: `npm run typecheck`
Expected: PASS. `app/settings.tsx` still has its own copy at this point — that's fine, they don't conflict.

- [ ] **Step 3: Rewrite `app/settings.tsx` to consume it**

Remove the `SEARCH_DEBOUNCE_MS` const (`:14`), the five search `useState`s + two `useRef`s (`:24-30`), the unmount `useEffect` (`:35-38`), `handleQueryChange` (`:57-90`), and `handleSelectCity` (`:92-98`). Keep `locating` and `locateError`.

The import block becomes:

```tsx
import React, { useState } from 'react';
import { View, Text, Pressable, StyleSheet, Switch } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { usePreferencesStore, ComfortLevel } from '../src/store/preferences';
import { useZmanimStore } from '../src/store/zmanim';
import { resolveDeviceLocation } from '../src/lib/location';
import { ColorPalette } from '../src/theme/colors';
import { useThemeColors } from '../src/theme/useThemeColors';
import { Fonts } from '../src/theme/typography';
import { DisplayToggle } from '../src/components/DisplayToggle';
import { FontSizeControl } from '../src/components/FontSizeControl';
import { CitySearch } from '../src/components/CitySearch';
```

`useEffect`, `useRef`, `TextInput`, `ZmanimLocation`, and `searchCities` are all now unused here — dropping them from the imports is part of the step.

The component's state and handlers reduce to:

```tsx
  const [locating, setLocating] = useState(false);
  const [locateError, setLocateError] = useState(false);

  const handleUseMyLocation = async () => {
    setLocateError(false);
    setLocating(true);
    try {
      const loc = await resolveDeviceLocation();
      if (loc) {
        setLocation(loc);
      } else {
        setLocateError(true);
      }
    } catch {
      setLocateError(true);
    } finally {
      setLocating(false);
    }
  };
```

Replace the `TextInput` + status hints + results map (`:219-247`) with:

```tsx
          <CitySearch
            colors={colors}
            onSelect={setLocation}
            onQueryChange={() => setLocateError(false)}
          />
```

Everything else in the Zmanim section stays: the `location ? location.label : 'Not set'` line, the "Use my location" button, the `locateError` hint, and the Hebcal attribution footer.

Finally delete the now-unused `cityInput` and `cityResult` entries from `makeStyles` (`:294-309`). Leave every other style — `sectionHint` and `switchLabel` are still used elsewhere in the file.

- [ ] **Step 4: Verify the refactor**

Run: `npm run check`
Expected: PASS — typecheck clean (this is what catches a missed import or leftover reference), content lint 0 errors, jest green.

Then run: `npm run ios`

In Settings → Zmanim, confirm behavior is unchanged from before this task: typing a city shows results after a beat; picking one sets the label and clears the box; typing gibberish shows "No cities found"; tapping "Use my location" still works; and with the device offline, typing shows "Couldn't search — check your connection."

- [ ] **Step 5: Commit**

```bash
git add src/components/CitySearch.tsx app/settings.tsx
git commit -m "refactor: extract CitySearch from settings

Onboarding is about to need the same city search. Pull the debounce,
the stale-response guard, and the three empty states into one component
rather than keeping two copies of a concurrency-sensitive guard in sync.

Fixes three latent bugs in the moved code: selecting a city now cancels
the pending debounce, retires the in-flight seq so a late response can't
repopulate the cleared list, and resets the searching flag."
```

---

### Task 2: Add the location step to onboarding

**Files:**
- Modify: `app/onboarding.tsx` (`Step` union at `:11`; add `fullSetup` state near `:20`; welcome buttons at `:52-57`; new step block after `:62`; styles in `makeStyles` at `:163`)

**Interfaces:**
- Consumes:
  - `CitySearch` from Task 1 — `{ colors: ColorPalette; onSelect: (loc: ZmanimLocation) => void; onQueryChange?: () => void }`
  - `resolveDeviceLocation(): Promise<ZmanimLocation | null>` from `src/lib/location.ts` — already requests when-in-use permission, takes a low-accuracy fix, and reverse-geocodes a city label. Returns `null` on denial or failure. Never throws.
  - `useZmanimStore().setLocation(loc: ZmanimLocation): void` from `src/store/zmanim.ts`
- Produces: nothing consumed by later tasks. This is the last task.

- [ ] **Step 1: Add imports and the `location` step to the wizard's state**

Add to the import block at the top of `app/onboarding.tsx`:

```tsx
import { useZmanimStore, ZmanimLocation } from '../src/store/zmanim';
import { resolveDeviceLocation } from '../src/lib/location';
import { CitySearch } from '../src/components/CitySearch';
```

Change the `Step` union at `:11`:

```tsx
type Step = 'welcome' | 'location' | 'comfort' | 'review';
```

Inside the component, alongside the existing `const [step, setStep] = useState<Step>('welcome')`:

```tsx
  // Which welcome button got us here. "Let's set it up" continues into the
  // comfort/review steps; "Use defaults" still asks for location, then goes
  // straight into the app with default preferences.
  const [fullSetup, setFullSetup] = useState(true);
  const [locating, setLocating] = useState(false);
  const [locationDenied, setLocationDenied] = useState(false);
  const [resolved, setResolved] = useState<ZmanimLocation | null>(null);
  const setLocation = useZmanimStore(state => state.setLocation);
```

- [ ] **Step 2: Route both welcome buttons into the location step**

Replace the two `Pressable`s at `:52-57`:

```tsx
            <Pressable
              style={[s.primaryBtn, { backgroundColor: colors.accent }]}
              onPress={() => { setFullSetup(true); setStep('location'); }}
            >
              <Text style={s.primaryBtnText}>Let's set it up</Text>
            </Pressable>
            <Pressable style={s.ghostBtn} onPress={() => { setFullSetup(false); setStep('location'); }}>
              <Text style={[s.ghostBtnText, { color: colors.muted }]}>Use defaults</Text>
            </Pressable>
```

"Use defaults" no longer calls `finish()` directly — it routes through location first. `finish()` itself is unchanged.

- [ ] **Step 3: Add the location step handlers**

Place these next to the existing `applyPreset` / `finish` functions:

```tsx
  // Leaves the location step: on to comfort for the full setup, or straight
  // into the app for the "Use defaults" path.
  function leaveLocationStep() {
    if (fullSetup) setStep('comfort');
    else finish();
  }

  async function handleAllowLocation() {
    setLocating(true);
    try {
      const loc = await resolveDeviceLocation();
      if (loc) {
        setLocation(loc);
        setResolved(loc);
      } else {
        // Denied, or the fix failed. Either way the fallback is the same.
        setLocationDenied(true);
      }
    } finally {
      // resolveDeviceLocation never throws, but if the user backgrounds the
      // app mid-prompt this promise just stays pending — the flag clears only
      // once it actually settles.
      setLocating(false);
    }
  }

  function handlePickCity(loc: ZmanimLocation) {
    setLocation(loc);
    setResolved(loc);
  }
```

- [ ] **Step 4: Render the location step**

Insert this block after the `welcome` block (after `:62`) and before the `comfort` block:

```tsx
  if (step === 'location') {
    return (
      <View style={[s.screen, { backgroundColor: colors.paper }]}>
        <SafeAreaView style={s.safe}>
          <View style={s.content}>
            {resolved ? (
              <>
                <Text style={[s.stepTitle, { color: colors.ink }]}>Zmanim set for {resolved.label}</Text>
                <Text style={[s.reviewNote, { color: colors.muted }]}>
                  You can change this anytime in Settings.
                </Text>
                <Pressable
                  style={[s.primaryBtn, { backgroundColor: colors.accent, marginTop: 8 }]}
                  onPress={leaveLocationStep}
                >
                  <Text style={s.primaryBtnText}>{fullSetup ? 'Next →' : 'Start davening →'}</Text>
                </Pressable>
                <Pressable style={s.ghostBtn} onPress={() => { setResolved(null); setLocationDenied(true); }}>
                  <Text style={[s.ghostBtnText, { color: colors.muted }]}>Not the right place? Search instead</Text>
                </Pressable>
              </>
            ) : locationDenied ? (
              <>
                <Text style={[s.stepTitle, { color: colors.ink }]}>Search for your city instead</Text>
                <Text style={[s.reviewNote, { color: colors.muted }]}>
                  Pick the closest city and we'll use it for your zmanim.
                </Text>
                <CitySearch colors={colors} onSelect={handlePickCity} />
                <Pressable style={s.ghostBtn} onPress={leaveLocationStep}>
                  <Text style={[s.ghostBtnText, { color: colors.muted }]}>Not now</Text>
                </Pressable>
              </>
            ) : (
              <>
                <Text style={[s.stepTitle, { color: colors.ink }]}>Accurate times for where you are</Text>
                <Text style={[s.locationBody, { color: colors.ink }]}>
                  Your location is used only to calculate halachic times — when to say Shema, when Shabbos comes in. It's used while you're in the app, and it never leaves your device except to look those times up.
                </Text>
                <Pressable
                  style={[s.primaryBtn, { backgroundColor: colors.accent }]}
                  onPress={handleAllowLocation}
                  disabled={locating}
                  accessibilityRole="button"
                  accessibilityLabel="Allow location"
                >
                  <Text style={s.primaryBtnText}>{locating ? 'Locating…' : 'Allow location'}</Text>
                </Pressable>
                <Pressable style={s.ghostBtn} onPress={() => setLocationDenied(true)}>
                  <Text style={[s.ghostBtnText, { color: colors.muted }]}>Not now</Text>
                </Pressable>
              </>
            )}
          </View>
        </SafeAreaView>
      </View>
    );
  }
```

The two "Not now" buttons are **not** the same action, and this is deliberate:

- "Not now" in the **initial** state skips the OS prompt without showing it and drops to the search state, so the user still gets a way to set a location by hand.
- "Not now" in the **denied** state (below the search) leaves with no location set and advances via `leaveLocationStep()`.

Leaving with no location is a supported end state — `src/components/NowCard.tsx:103` already renders a "set location" row when `location` is null.

Note the denied state's heading says "Search for your city instead" rather than offering another "Allow location" button. After an OS-level denial iOS will not re-prompt, so a retry button would silently do nothing.

- [ ] **Step 5: Add the one new style**

Add to `makeStyles` in `app/onboarding.tsx:163`. Every other style this step uses (`stepTitle`, `reviewNote`, `primaryBtn`, `ghostBtn`, `content`) already exists.

```tsx
    locationBody: { fontFamily: Fonts.english, fontSize: 15, lineHeight: 24, marginBottom: 28 },
```

- [ ] **Step 6: Verify**

Run: `npm run check`
Expected: PASS — typecheck clean, content lint 0 errors, jest green.

Then run: `npm run ios`

iOS only shows the location prompt **once per install**, so re-arm it before each run that needs the prompt:

```bash
xcrun simctl privacy booted reset location com.semiagenticrob.digitalsiddur
```

To get back to onboarding without reinstalling, use Settings → "Reset setup wizard" (`app/settings.tsx:257`), which calls `resetOnboarding()` and routes to `/onboarding`.

Walk all five paths:

| Path | Expect |
|---|---|
| welcome → "Let's set it up" → "Allow location" → accept prompt | "Zmanim set for &lt;city&gt;", then "Next →" → comfort step |
| welcome → "Let's set it up" → "Allow location" → **deny** prompt | drops to search; pick a city → "Zmanim set for …" |
| welcome → "Let's set it up" → "Not now" | search state, no OS prompt shown; "Not now" again → comfort step, location unset |
| welcome → **"Use defaults"** → allow or skip | lands on `/daven`, skipping comfort and review |
| Settings → Zmanim | search still works (Task 1 regression check) |

Also confirm: after skipping, the home screen's NowCard shows its "set location" row.

- [ ] **Step 7: Commit**

```bash
git add app/onboarding.tsx
git commit -m "feat(onboarding): ask for location on its own step

Adds a location step right after the welcome screen so zmanim work from
first launch instead of waiting for the user to find the picker in
Settings. Denying the OS prompt falls back to inline city search rather
than a dead end.

'Use defaults' now routes through this step too — it means default
preferences, not skip everything. Skipping entirely stays supported; the
home NowCard already prompts for a location when none is set."
```

---

## Done when

- Both tasks committed.
- `npm run check` passes.
- All five simulator paths in Task 2 Step 6 walked by hand.
- No changes to `app.json`, `src/store/zmanim.ts`, or `src/lib/location.ts`.
- No new dependencies in `package.json`.
