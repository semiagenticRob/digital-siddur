# Digital Siddur v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a free, offline-first iOS + Android React Native app delivering the complete weekday Feigenbaum Siddur with Hebrew/English reading modes, continuous scroll, jump-ToC, personalization, and onboarding.

**Architecture:** Expo Router (file-based navigation), content stored in bundled JSON (SQLite-ready shape), Zustand for preferences and annotations (persisted via AsyncStorage), FlashList for virtualized scroll. No backend — everything runs offline from first launch.

**Tech Stack:** Expo SDK 53, TypeScript, Expo Router v4, Zustand + AsyncStorage, FlashList, expo-font, Frank Ruhl Libre / Newsreader / Inter

---

## Scope Note

The PRD has two parallel tracks. This plan covers **Track B (App)** only — M1 through M7. Track A (content digitization + proofing) is a separate human-driven process. The app launches with placeholder content (public-domain liturgy) that gets swapped for proofed content during M6.

M1–M4 are in strict dependency order. M5 (remaining services) reuses M2 patterns. M6–M7 are integration and release.

---

## File Map

```
digital-siddur/
├── app/
│   ├── _layout.tsx                  # Root: fonts, theme provider, navigation shell
│   ├── index.tsx                    # Redirect → onboarding or daven
│   ├── onboarding.tsx               # Onboarding flow (M4)
│   ├── daven/
│   │   ├── index.tsx                # Service list screen
│   │   └── [service].tsx            # Service reader (continuous scroll + ToC)
│   └── settings.tsx                 # Settings screen (M4)
├── src/
│   ├── content/
│   │   ├── types.ts                 # Segment, Prayer, Group, Service types
│   │   ├── loader.ts                # Load + validate content JSON at runtime
│   │   └── shacharit.json           # Placeholder Shacharis content (M1 seed)
│   ├── components/
│   │   ├── SegmentRenderer.tsx      # Renders one segment: prayer/commentary/rubric/insight
│   │   ├── PrayerBlock.tsx          # Groups segments for one prayer; hosts insight toggle
│   │   ├── ServiceScroll.tsx        # FlashList over all prayers in a service
│   │   ├── JumpToC.tsx              # Slide-in drawer; emits scroll-to index
│   │   ├── DisplayToggle.tsx        # Hebrew / Both / English segmented control
│   │   ├── SelectionBar.tsx         # Highlight + Note action bar (appears on line tap)
│   │   └── FontSizeControl.tsx      # A− / A+ buttons
│   ├── store/
│   │   ├── preferences.ts           # Zustand: displayMode, theme, fontStep, comfortLevel
│   │   └── annotations.ts           # Zustand: highlights[], notes[] keyed by segmentId
│   └── theme/
│       ├── colors.ts                # Light + dark palette (from prototype CSS vars)
│       └── typography.ts            # Font family constants + scale function
├── assets/fonts/                    # Bundled: FrankRuhlLibre-*.ttf, Newsreader-*.ttf, Inter-*.ttf
└── docs/superpowers/plans/
    └── 2026-06-15-digital-siddur-v1.md   # this file
```

---

## M1 · Reading Core

### Task 1: Initialize Expo project

**Files:**
- Create: project root (Expo init inside existing repo)

- [ ] **Step 1: Scaffold Expo app**

```bash
cd /Users/robertwarren/digital-siddur
npx create-expo-app@latest . --template blank-typescript
```

Accept overwrite prompt. This sets up `package.json`, `tsconfig.json`, `app.json`, and `App.tsx`.

- [ ] **Step 2: Switch to Expo Router**

```bash
npx expo install expo-router expo-constants expo-linking expo-status-bar react-native-safe-area-context react-native-screens
```

Update `package.json` main entry:
```json
{
  "main": "expo-router/entry"
}
```

Update `app.json`:
```json
{
  "expo": {
    "scheme": "digital-siddur",
    "web": { "bundler": "metro" }
  }
}
```

Delete `App.tsx` — Expo Router uses the `app/` directory instead.

- [ ] **Step 3: Install remaining deps**

```bash
npx expo install zustand @react-native-async-storage/async-storage @shopify/flash-list
```

- [ ] **Step 4: Verify it starts**

```bash
npx expo start
```

Expected: Metro bundler starts, QR code appears, no TypeScript errors.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: initialize Expo + Expo Router project"
```

---

### Task 2: Load and bundle fonts

**Files:**
- Create: `assets/fonts/` (font files)
- Modify: `app/_layout.tsx`

- [ ] **Step 1: Install expo-font and Google Fonts package**

```bash
npx expo install expo-font @expo-google-fonts/frank-ruhl-libre @expo-google-fonts/newsreader @expo-google-fonts/inter
```

- [ ] **Step 2: Write root layout with font loading**

Create `app/_layout.tsx`:

```typescript
import { Stack } from 'expo-router';
import { useFonts } from 'expo-font';
import {
  FrankRuhlLibre_400Regular,
  FrankRuhlLibre_500Medium,
  FrankRuhlLibre_700Bold,
} from '@expo-google-fonts/frank-ruhl-libre';
import {
  Newsreader_400Regular,
  Newsreader_400Regular_Italic,
  Newsreader_500Medium,
} from '@expo-google-fonts/newsreader';
import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
} from '@expo-google-fonts/inter';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    FrankRuhlLibre_400Regular,
    FrankRuhlLibre_500Medium,
    FrankRuhlLibre_700Bold,
    Newsreader_400Regular,
    Newsreader_400Regular_Italic,
    Newsreader_500Medium,
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
  });

  useEffect(() => {
    if (loaded || error) SplashScreen.hideAsync();
  }, [loaded, error]);

  if (!loaded && !error) return null;

  return (
    <Stack screenOptions={{ headerShown: false }} />
  );
}
```

- [ ] **Step 3: Add expo-splash-screen**

```bash
npx expo install expo-splash-screen
```

- [ ] **Step 4: Verify fonts load**

```bash
npx expo start
```

Open in Expo Go. Expected: app loads without "font not found" warnings in Metro console.

- [ ] **Step 5: Commit**

```bash
git add app/_layout.tsx package.json package-lock.json
git commit -m "feat: load Frank Ruhl Libre, Newsreader, Inter via expo-font"
```

---

### Task 3: Define content types and seed Shacharis JSON

**Files:**
- Create: `src/content/types.ts`
- Create: `src/content/shacharit.json`
- Create: `src/content/loader.ts`

- [ ] **Step 1: Write content type definitions**

Create `src/content/types.ts`:

```typescript
export type SegmentType = 'prayer' | 'commentary' | 'rubric' | 'insight';

export interface Segment {
  id: string;
  type: SegmentType;
  heText?: string;       // Hebrew with nikkud; present on prayer/rubric
  enText?: string;       // English explanation; present on commentary/insight
  condition?: string;    // e.g. "winter", "rosh_chodesh" — v2 logic; shown as rubric label in v1
  xref?: string;         // e.g. "faq:3" — captured now, navigable in v2
}

export interface Prayer {
  id: string;
  heTitle: string;
  enTitle: string;
  segments: Segment[];
}

export interface Group {
  id: string;
  title: string;         // e.g. "Waking & morning brachos"
  prayers: Prayer[];
}

export interface Service {
  id: string;
  heTitle: string;
  enTitle: string;
  groups: Group[];
}
```

- [ ] **Step 2: Write seed Shacharis JSON (Shemoneh Esrei section only)**

Create `src/content/shacharit.json` with the first 4 brachos matching the prototype. This is placeholder public-domain content that will be replaced in M6 with proofed Feigenbaum content.

```json
{
  "id": "shacharit",
  "heTitle": "שַׁחֲרִית",
  "enTitle": "Shacharis",
  "groups": [
    {
      "id": "g-shemoneh-esrei",
      "title": "Shemoneh Esrei",
      "prayers": [
        {
          "id": "p-pesicha",
          "heTitle": "פְּתִיחָה",
          "enTitle": "Opening",
          "segments": [
            {
              "id": "pesicha-1",
              "type": "prayer",
              "heText": "אֲדֹנָי שְׂפָתַי תִּפְתָּח, וּפִי יַגִּיד תְּהִלָּתֶךָ."
            },
            {
              "id": "pesicha-1-commentary",
              "type": "commentary",
              "enText": "Before we say a word, we ask Hashem to open our lips — admitting that even the ability to talk to Him is a gift He gives us."
            }
          ]
        },
        {
          "id": "p-avos",
          "heTitle": "אָבוֹת",
          "enTitle": "Avos",
          "segments": [
            {
              "id": "avos-1",
              "type": "prayer",
              "heText": "בָּרוּךְ אַתָּה יְיָ אֱלֹהֵינוּ וֵאלֹהֵי אֲבוֹתֵינוּ, אֱלֹהֵי אַבְרָהָם, אֱלֹהֵי יִצְחָק, וֵאלֹהֵי יַעֲקֹב,"
            },
            {
              "id": "avos-2",
              "type": "prayer",
              "heText": "הָאֵל הַגָּדוֹל הַגִּבּוֹר וְהַנּוֹרָא, אֵל עֶלְיוֹן, גּוֹמֵל חֲסָדִים טוֹבִים, וְקוֹנֵה הַכֹּל,"
            },
            {
              "id": "avos-3",
              "type": "prayer",
              "heText": "וְזוֹכֵר חַסְדֵי אָבוֹת, וּמֵבִיא גוֹאֵל לִבְנֵי בְנֵיהֶם לְמַעַן שְׁמוֹ בְּאַהֲבָה."
            },
            {
              "id": "avos-4",
              "type": "prayer",
              "heText": "מֶלֶךְ עוֹזֵר וּמוֹשִׁיעַ וּמָגֵן. בָּרוּךְ אַתָּה יְיָ, מָגֵן אַבְרָהָם."
            },
            {
              "id": "avos-commentary",
              "type": "commentary",
              "enText": "We don't walk up to Hashem as strangers. We come as the children of Avraham, Yitzchak and Yaakov — reminding ourselves we're part of something that started long before us."
            },
            {
              "id": "avos-insight",
              "type": "insight",
              "enText": "Why start with the Avos and not just jump to our requests? Because relationships come before requests — we ground the conversation in who we are before we ask for anything."
            }
          ]
        },
        {
          "id": "p-gevuros",
          "heTitle": "גְּבוּרוֹת",
          "enTitle": "Gevuros",
          "segments": [
            {
              "id": "gevuros-1",
              "type": "prayer",
              "heText": "אַתָּה גִּבּוֹר לְעוֹלָם אֲדֹנָי, מְחַיֵּה מֵתִים אַתָּה, רַב לְהוֹשִׁיעַ."
            },
            {
              "id": "gevuros-rubric",
              "type": "rubric",
              "heText": "בַּחֹרֶף (in winter) add:",
              "condition": "winter"
            },
            {
              "id": "gevuros-2",
              "type": "prayer",
              "heText": "מַשִּׁיב הָרוּחַ וּמוֹרִיד הַגֶּשֶׁם.",
              "condition": "winter"
            },
            {
              "id": "gevuros-3",
              "type": "prayer",
              "heText": "מְכַלְכֵּל חַיִּים בְּחֶסֶד, מְחַיֵּה מֵתִים בְּרַחֲמִים רַבִּים, סוֹמֵךְ נוֹפְלִים וְרוֹפֵא חוֹלִים וּמַתִּיר אֲסוּרִים,"
            },
            {
              "id": "gevuros-4",
              "type": "prayer",
              "heText": "וּמְקַיֵּם אֱמוּנָתוֹ לִישֵׁנֵי עָפָר. מִי כָמוֹךָ בַּעַל גְּבוּרוֹת וּמִי דּוֹמֶה לָּךְ,"
            },
            {
              "id": "gevuros-5",
              "type": "prayer",
              "heText": "מֶלֶךְ מֵמִית וּמְחַיֶּה וּמַצְמִיחַ יְשׁוּעָה. בָּרוּךְ אַתָּה יְיָ, מְחַיֵּה הַמֵּתִים."
            },
            {
              "id": "gevuros-commentary",
              "type": "commentary",
              "enText": "This bracha is about Hashem's power — but notice where it goes: holding up the falling, healing the sick, freeing the trapped. Real strength, here, looks like care."
            }
          ]
        },
        {
          "id": "p-kedusha",
          "heTitle": "קְדֻשַּׁת הַשֵּׁם",
          "enTitle": "Kedushas Hashem",
          "segments": [
            {
              "id": "kedusha-1",
              "type": "prayer",
              "heText": "אַתָּה קָדוֹשׁ וְשִׁמְךָ קָדוֹשׁ, וּקְדוֹשִׁים בְּכָל יוֹם יְהַלְלוּךָ סֶּלָה."
            },
            {
              "id": "kedusha-2",
              "type": "prayer",
              "heText": "בָּרוּךְ אַתָּה יְיָ, הָאֵל הַקָּדוֹשׁ."
            },
            {
              "id": "kedusha-commentary",
              "type": "commentary",
              "enText": "\"Holy\" means set apart — beyond anything we can fully picture. We pause here to remember Who we're actually talking to."
            }
          ]
        }
      ]
    }
  ]
}
```

- [ ] **Step 3: Write content loader**

Create `src/content/loader.ts`:

```typescript
import { Service } from './types';
import shacharitData from './shacharit.json';

const SERVICES: Record<string, Service> = {
  shacharit: shacharitData as Service,
};

export function getService(id: string): Service | null {
  return SERVICES[id] ?? null;
}

export function listServices(): Array<{ id: string; heTitle: string; enTitle: string }> {
  return Object.values(SERVICES).map(({ id, heTitle, enTitle }) => ({ id, heTitle, enTitle }));
}
```

- [ ] **Step 4: Write a unit test for the loader**

Create `src/content/__tests__/loader.test.ts`:

```typescript
import { getService, listServices } from '../loader';

test('getService returns shacharit', () => {
  const s = getService('shacharit');
  expect(s).not.toBeNull();
  expect(s!.id).toBe('shacharit');
  expect(s!.groups.length).toBeGreaterThan(0);
});

test('getService returns null for unknown id', () => {
  expect(getService('does-not-exist')).toBeNull();
});

test('listServices includes shacharit', () => {
  const list = listServices();
  expect(list.some(s => s.id === 'shacharit')).toBe(true);
});
```

- [ ] **Step 5: Run tests**

```bash
npx jest src/content/__tests__/loader.test.ts --no-coverage
```

Expected: 3 tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/content/
git commit -m "feat: content types, Shacharis seed JSON, and loader"
```

---

### Task 4: Theme system (colors + typography)

**Files:**
- Create: `src/theme/colors.ts`
- Create: `src/theme/typography.ts`

- [ ] **Step 1: Write color palette**

Create `src/theme/colors.ts`:

```typescript
export const LightColors = {
  paper: '#F6F2E9',
  surface: '#FDFBF5',
  ink: '#1E2433',
  muted: '#6C7180',
  line: '#E4DECF',
  accent: '#34467F',
  accentSoft: '#EBEEF8',
  gold: '#D9A53B',
  goldFill: 'rgba(217,165,59,0.30)',
  rubric: '#897640',
} as const;

export const DarkColors = {
  paper: '#11141C',
  surface: '#191D27',
  ink: '#ECE6D8',
  muted: '#969CAB',
  line: '#2A2F3C',
  accent: '#94A6E2',
  accentSoft: '#222a3f',
  gold: '#E6B651',
  goldFill: 'rgba(230,182,81,0.20)',
  rubric: '#BBA877',
} as const;

export type ColorPalette = typeof LightColors;
```

- [ ] **Step 2: Write typography constants**

Create `src/theme/typography.ts`:

```typescript
export const Fonts = {
  hebrew: 'FrankRuhlLibre_500Medium',
  hebrewBold: 'FrankRuhlLibre_700Bold',
  hebrewRegular: 'FrankRuhlLibre_400Regular',
  english: 'Newsreader_400Regular',
  englishItalic: 'Newsreader_400Regular_Italic',
  ui: 'Inter_400Regular',
  uiMedium: 'Inter_500Medium',
  uiSemiBold: 'Inter_600SemiBold',
} as const;

export const BASE_HE_SIZE = 21;
export const BASE_EN_SIZE = 15.5;
export const FONT_STEP_SCALE = 0.12;

export function hebrewFontSize(fontStep: number): number {
  return BASE_HE_SIZE * (1 + fontStep * FONT_STEP_SCALE);
}

export function englishFontSize(fontStep: number): number {
  return BASE_EN_SIZE * (0.55 + (1 + fontStep * FONT_STEP_SCALE) * 0.45);
}
```

- [ ] **Step 3: Write tests for font size scaling**

Create `src/theme/__tests__/typography.test.ts`:

```typescript
import { hebrewFontSize, englishFontSize } from '../typography';

test('hebrewFontSize at step 0 is 21', () => {
  expect(hebrewFontSize(0)).toBeCloseTo(21);
});

test('hebrewFontSize increases with positive step', () => {
  expect(hebrewFontSize(2)).toBeGreaterThan(hebrewFontSize(0));
});

test('hebrewFontSize decreases with negative step', () => {
  expect(hebrewFontSize(-1)).toBeLessThan(hebrewFontSize(0));
});

test('englishFontSize at step 0 is between 14 and 16', () => {
  const size = englishFontSize(0);
  expect(size).toBeGreaterThan(14);
  expect(size).toBeLessThan(16);
});
```

- [ ] **Step 4: Run tests**

```bash
npx jest src/theme/__tests__/typography.test.ts --no-coverage
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/theme/
git commit -m "feat: color palette and typography scale system"
```

---

### Task 5: Preferences store

**Files:**
- Create: `src/store/preferences.ts`

- [ ] **Step 1: Write failing test**

Create `src/store/__tests__/preferences.test.ts`:

```typescript
import { usePreferencesStore } from '../preferences';
import { act, renderHook } from '@testing-library/react-hooks';

test('default displayMode is both', () => {
  const { result } = renderHook(() => usePreferencesStore());
  expect(result.current.displayMode).toBe('both');
});

test('setDisplayMode updates the value', () => {
  const { result } = renderHook(() => usePreferencesStore());
  act(() => result.current.setDisplayMode('he'));
  expect(result.current.displayMode).toBe('he');
});

test('fontStep clamps between -2 and 4', () => {
  const { result } = renderHook(() => usePreferencesStore());
  act(() => result.current.bumpFontStep(10));
  expect(result.current.fontStep).toBe(4);
  act(() => result.current.bumpFontStep(-20));
  expect(result.current.fontStep).toBe(-2);
});

test('default theme is auto', () => {
  const { result } = renderHook(() => usePreferencesStore());
  expect(result.current.theme).toBe('auto');
});
```

- [ ] **Step 2: Run test to confirm failure**

```bash
npx jest src/store/__tests__/preferences.test.ts --no-coverage
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement preferences store**

```bash
npx expo install @react-native-async-storage/async-storage
```

Create `src/store/preferences.ts`:

```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type DisplayMode = 'he' | 'both' | 'en';
export type Theme = 'light' | 'dark' | 'auto';
export type ComfortLevel = 'beginner' | 'comfortable' | 'fluent';

interface PreferencesState {
  displayMode: DisplayMode;
  theme: Theme;
  fontStep: number;
  comfortLevel: ComfortLevel;
  hasCompletedOnboarding: boolean;
  setDisplayMode: (mode: DisplayMode) => void;
  setTheme: (theme: Theme) => void;
  bumpFontStep: (delta: number) => void;
  setComfortLevel: (level: ComfortLevel) => void;
  completeOnboarding: () => void;
  resetOnboarding: () => void;
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      displayMode: 'both',
      theme: 'auto',
      fontStep: 0,
      comfortLevel: 'comfortable',
      hasCompletedOnboarding: false,
      setDisplayMode: (mode) => set({ displayMode: mode }),
      setTheme: (theme) => set({ theme }),
      bumpFontStep: (delta) =>
        set((s) => ({ fontStep: Math.max(-2, Math.min(4, s.fontStep + delta)) })),
      setComfortLevel: (level) => set({ comfortLevel: level }),
      completeOnboarding: () => set({ hasCompletedOnboarding: true }),
      resetOnboarding: () => set({ hasCompletedOnboarding: false }),
    }),
    {
      name: 'siddur-preferences',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

export const COMFORT_PRESETS: Record<ComfortLevel, Partial<PreferencesState>> = {
  beginner: { displayMode: 'both', fontStep: 1, theme: 'auto' },
  comfortable: { displayMode: 'both', fontStep: 0, theme: 'auto' },
  fluent: { displayMode: 'he', fontStep: 0, theme: 'auto' },
};
```

- [ ] **Step 4: Run tests**

```bash
npx jest src/store/__tests__/preferences.test.ts --no-coverage
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/store/preferences.ts src/store/__tests__/preferences.test.ts
git commit -m "feat: preferences store with persistence (displayMode, theme, fontStep)"
```

---

### Task 6: Annotations store (highlights + notes)

**Files:**
- Create: `src/store/annotations.ts`

- [ ] **Step 1: Write failing test**

Create `src/store/__tests__/annotations.test.ts`:

```typescript
import { useAnnotationsStore } from '../annotations';
import { act, renderHook } from '@testing-library/react-hooks';

test('no highlights initially', () => {
  const { result } = renderHook(() => useAnnotationsStore());
  expect(result.current.isHighlighted('seg-1')).toBe(false);
});

test('toggleHighlight adds then removes', () => {
  const { result } = renderHook(() => useAnnotationsStore());
  act(() => result.current.toggleHighlight('seg-1'));
  expect(result.current.isHighlighted('seg-1')).toBe(true);
  act(() => result.current.toggleHighlight('seg-1'));
  expect(result.current.isHighlighted('seg-1')).toBe(false);
});

test('addNote stores text for a segment', () => {
  const { result } = renderHook(() => useAnnotationsStore());
  act(() => result.current.addNote('seg-2', 'My note'));
  expect(result.current.getNotes('seg-2')).toEqual(['My note']);
});

test('addNote appends multiple notes', () => {
  const { result } = renderHook(() => useAnnotationsStore());
  act(() => result.current.addNote('seg-3', 'First'));
  act(() => result.current.addNote('seg-3', 'Second'));
  expect(result.current.getNotes('seg-3')).toHaveLength(2);
});
```

- [ ] **Step 2: Run to confirm failure**

```bash
npx jest src/store/__tests__/annotations.test.ts --no-coverage
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement annotations store**

Create `src/store/annotations.ts`:

```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AnnotationsState {
  highlights: Set<string>;  // segmentIds
  notes: Record<string, string[]>; // segmentId → note texts
  toggleHighlight: (segmentId: string) => void;
  isHighlighted: (segmentId: string) => boolean;
  addNote: (segmentId: string, text: string) => void;
  getNotes: (segmentId: string) => string[];
}

export const useAnnotationsStore = create<AnnotationsState>()(
  persist(
    (set, get) => ({
      highlights: new Set<string>(),
      notes: {},
      toggleHighlight: (id) =>
        set((s) => {
          const next = new Set(s.highlights);
          next.has(id) ? next.delete(id) : next.add(id);
          return { highlights: next };
        }),
      isHighlighted: (id) => get().highlights.has(id),
      addNote: (id, text) =>
        set((s) => ({
          notes: { ...s.notes, [id]: [...(s.notes[id] ?? []), text] },
        })),
      getNotes: (id) => get().notes[id] ?? [],
    }),
    {
      name: 'siddur-annotations',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (s) => ({
        highlights: Array.from(s.highlights),
        notes: s.notes,
      }),
      merge: (persisted: any, current) => ({
        ...current,
        highlights: new Set(persisted.highlights ?? []),
        notes: persisted.notes ?? {},
      }),
    }
  )
);
```

- [ ] **Step 4: Run tests**

```bash
npx jest src/store/__tests__/annotations.test.ts --no-coverage
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/store/annotations.ts src/store/__tests__/annotations.test.ts
git commit -m "feat: annotations store for highlights and notes with local persistence"
```

---

### Task 7: SegmentRenderer component

**Files:**
- Create: `src/components/SegmentRenderer.tsx`

The renderer is the core of the reading experience. It takes one segment and the current display mode, and renders the right visual.

- [ ] **Step 1: Create the component**

Create `src/components/SegmentRenderer.tsx`:

```typescript
import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable, TextInput, Modal } from 'react-native';
import { Segment } from '../content/types';
import { DisplayMode } from '../store/preferences';
import { ColorPalette } from '../theme/colors';
import { Fonts, hebrewFontSize, englishFontSize } from '../theme/typography';

interface Props {
  segment: Segment;
  displayMode: DisplayMode;
  fontStep: number;
  colors: ColorPalette;
  isHighlighted: boolean;
  notes: string[];
  onToggleHighlight: () => void;
  onAddNote: (text: string) => void;
}

export function SegmentRenderer({
  segment, displayMode, fontStep, colors,
  isHighlighted, notes, onToggleHighlight, onAddNote,
}: Props) {
  const [showInsight, setShowInsight] = useState(false);
  const [noteModalVisible, setNoteModalVisible] = useState(false);
  const [noteText, setNoteText] = useState('');
  const [selectionVisible, setSelectionVisible] = useState(false);

  const heSize = hebrewFontSize(fontStep);
  const enSize = englishFontSize(fontStep);

  const s = styles(colors, heSize, enSize);

  if (segment.type === 'rubric') {
    if (displayMode === 'en') return null;
    return (
      <Text style={s.rubric}>{segment.heText}</Text>
    );
  }

  if (segment.type === 'commentary') {
    if (displayMode === 'he') return null;
    return (
      <View style={s.commentaryBlock}>
        <Text style={s.commentaryTag}>EXPLANATION</Text>
        <Text style={s.commentaryText}>{segment.enText}</Text>
      </View>
    );
  }

  if (segment.type === 'insight') {
    if (displayMode === 'he') return null;
    return (
      <View>
        <Pressable
          style={s.insightToggle}
          onPress={() => setShowInsight(v => !v)}
          accessibilityRole="button"
          accessibilityLabel={showInsight ? 'Hide insight' : 'Show quick insight'}
        >
          <Text style={s.insightToggleText}>
            {showInsight ? '▲ Hide insight' : '💡 Quick insight'}
          </Text>
        </Pressable>
        {showInsight && (
          <View style={s.insightBody}>
            <Text style={s.insightText}>{segment.enText}</Text>
          </View>
        )}
      </View>
    );
  }

  // prayer segment
  const shouldShow = displayMode !== 'en';
  if (!shouldShow) return null;

  return (
    <View>
      <Pressable
        style={[s.heLine, isHighlighted && s.heLineHighlighted]}
        onPress={() => setSelectionVisible(v => !v)}
        accessibilityRole="text"
        accessibilityLabel={segment.heText}
      >
        <Text style={s.heText}>{segment.heText}</Text>
      </Pressable>
      {selectionVisible && (
        <View style={s.selectionBar}>
          <Pressable style={s.selectionBtn} onPress={() => { onToggleHighlight(); setSelectionVisible(false); }}>
            <Text style={s.selectionBtnText}>Highlight</Text>
          </Pressable>
          <Pressable style={s.selectionBtn} onPress={() => { setSelectionVisible(false); setNoteModalVisible(true); }}>
            <Text style={s.selectionBtnText}>Note</Text>
          </Pressable>
          <Pressable style={s.selectionBtn} onPress={() => setSelectionVisible(false)}>
            <Text style={s.selectionBtnText}>✕</Text>
          </Pressable>
        </View>
      )}
      {notes.length > 0 && notes.map((note, i) => (
        <View key={i} style={s.noteChip}>
          <Text style={s.noteText}>✎ {note}</Text>
        </View>
      ))}
      <Modal visible={noteModalVisible} transparent animationType="slide">
        <View style={s.modalOverlay}>
          <View style={s.modalCard}>
            <Text style={s.modalTitle}>Add note</Text>
            <TextInput
              style={s.modalInput}
              value={noteText}
              onChangeText={setNoteText}
              placeholder="Your note…"
              multiline
              autoFocus
            />
            <View style={s.modalButtons}>
              <Pressable onPress={() => { setNoteModalVisible(false); setNoteText(''); }}>
                <Text style={[s.modalBtn, { color: colors.muted }]}>Cancel</Text>
              </Pressable>
              <Pressable onPress={() => {
                if (noteText.trim()) { onAddNote(noteText.trim()); setNoteText(''); }
                setNoteModalVisible(false);
              }}>
                <Text style={[s.modalBtn, { color: colors.accent }]}>Save</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

function styles(c: ColorPalette, heSize: number, enSize: number) {
  return StyleSheet.create({
    heLine: {
      paddingVertical: 4, paddingHorizontal: 4, borderRadius: 6,
    },
    heLineHighlighted: {
      backgroundColor: c.goldFill,
      borderBottomWidth: 2, borderBottomColor: c.gold,
    },
    heText: {
      fontFamily: Fonts.hebrew, fontSize: heSize, lineHeight: heSize * 1.95,
      color: 'inherit' as any, textAlign: 'right', writingDirection: 'rtl',
    },
    commentaryBlock: {
      marginTop: 12, paddingVertical: 12, paddingHorizontal: 14,
      backgroundColor: c.accentSoft,
      borderLeftWidth: 3, borderLeftColor: c.accent,
      borderRadius: 10,
    },
    commentaryTag: {
      fontFamily: Fonts.uiSemiBold, fontSize: 9.5, letterSpacing: 1.5,
      color: c.accent, marginBottom: 6,
    },
    commentaryText: {
      fontFamily: Fonts.english, fontSize: enSize, lineHeight: enSize * 1.62,
      color: c.ink,
    },
    rubric: {
      fontFamily: Fonts.hebrew, fontSize: heSize * 0.72,
      color: c.rubric, fontStyle: 'italic',
      textAlign: 'right', writingDirection: 'rtl',
      marginVertical: 6, paddingVertical: 6, paddingHorizontal: 10,
      borderRightWidth: 3, borderRightColor: c.rubric,
      backgroundColor: c.accentSoft, borderRadius: 10,
    },
    insightToggle: {
      marginTop: 10, alignSelf: 'flex-start',
      paddingVertical: 6, paddingHorizontal: 11, borderRadius: 20,
      borderWidth: 1, borderStyle: 'dashed', borderColor: c.accent,
    },
    insightToggleText: {
      fontFamily: Fonts.uiSemiBold, fontSize: 12, color: c.accent,
    },
    insightBody: {
      marginTop: 8, padding: 11, borderRadius: 10,
      backgroundColor: c.accentSoft,
      borderWidth: 1, borderColor: c.gold,
    },
    insightText: {
      fontFamily: Fonts.english, fontSize: enSize, lineHeight: enSize * 1.6,
      color: c.ink,
    },
    selectionBar: {
      flexDirection: 'row', gap: 4, marginTop: 4,
      backgroundColor: c.ink, padding: 6, borderRadius: 12, alignSelf: 'center',
    },
    selectionBtn: {
      paddingVertical: 8, paddingHorizontal: 14, borderRadius: 8,
    },
    selectionBtnText: {
      fontFamily: Fonts.uiSemiBold, fontSize: 12.5, color: c.surface,
    },
    noteChip: {
      marginTop: 4, paddingVertical: 6, paddingHorizontal: 10,
      backgroundColor: c.accentSoft, borderRadius: 8,
    },
    noteText: { fontFamily: Fonts.ui, fontSize: 12.5, color: c.ink },
    modalOverlay: {
      flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)',
    },
    modalCard: {
      backgroundColor: c.surface, borderRadius: 20, padding: 20,
      marginHorizontal: 12, marginBottom: 40,
    },
    modalTitle: { fontFamily: Fonts.uiSemiBold, fontSize: 16, color: c.ink, marginBottom: 12 },
    modalInput: {
      fontFamily: Fonts.ui, fontSize: 15, color: c.ink,
      borderWidth: 1, borderColor: c.line, borderRadius: 10,
      padding: 10, minHeight: 80, textAlignVertical: 'top',
    },
    modalButtons: { flexDirection: 'row', justifyContent: 'flex-end', gap: 20, marginTop: 12 },
    modalBtn: { fontFamily: Fonts.uiSemiBold, fontSize: 15 },
    surface: { backgroundColor: c.surface },
  });
}
```

- [ ] **Step 2: Manually test on device**

Start Expo and navigate to a prayer. Verify:
- Hebrew text renders RTL with nikkud
- Commentary hides in Hebrew mode, shows in Both/English
- Rubrics display with clay styling
- Insight toggle opens/closes
- Tap a Hebrew line → selection bar appears → Highlight turns gold → Note modal saves text
- All of the above in both light and dark themes

```bash
npx expo start
```

- [ ] **Step 3: Commit**

```bash
git add src/components/SegmentRenderer.tsx
git commit -m "feat: SegmentRenderer for prayer/commentary/rubric/insight segments"
```

---

## M2 · Shacharis End-to-End

### Task 8: ServiceScroll (virtualized continuous scroll)

**Files:**
- Create: `src/components/ServiceScroll.tsx`

- [ ] **Step 1: Install FlashList**

```bash
npx expo install @shopify/flash-list
```

- [ ] **Step 2: Create ServiceScroll**

Create `src/components/ServiceScroll.tsx`:

```typescript
import React, { useRef, forwardRef, useImperativeHandle } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { FlashList } from '@shopify/flash-list';
import { Service, Prayer, Segment } from '../content/types';
import { DisplayMode } from '../store/preferences';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';
import { SegmentRenderer } from './SegmentRenderer';

// Flat list item: either a prayer header or a segment
type ListItem =
  | { kind: 'prayerHeader'; prayerId: string; heTitle: string; enTitle: string; groupId: string }
  | { kind: 'segment'; segment: Segment; prayerId: string };

function flattenService(service: Service): ListItem[] {
  const items: ListItem[] = [];
  for (const group of service.groups) {
    for (const prayer of group.prayers) {
      items.push({ kind: 'prayerHeader', prayerId: prayer.id, heTitle: prayer.heTitle, enTitle: prayer.enTitle, groupId: group.id });
      for (const seg of prayer.segments) {
        items.push({ kind: 'segment', segment: seg, prayerId: prayer.id });
      }
    }
  }
  return items;
}

export interface ServiceScrollHandle {
  scrollToPrayer: (prayerId: string) => void;
}

interface Props {
  service: Service;
  displayMode: DisplayMode;
  fontStep: number;
  colors: ColorPalette;
  isHighlighted: (segmentId: string) => boolean;
  getNotes: (segmentId: string) => string[];
  onToggleHighlight: (segmentId: string) => void;
  onAddNote: (segmentId: string, text: string) => void;
}

export const ServiceScroll = forwardRef<ServiceScrollHandle, Props>(
  ({ service, displayMode, fontStep, colors, isHighlighted, getNotes, onToggleHighlight, onAddNote }, ref) => {
    const listRef = useRef<FlashList<ListItem>>(null);
    const items = flattenService(service);

    useImperativeHandle(ref, () => ({
      scrollToPrayer: (prayerId) => {
        const idx = items.findIndex(i => i.kind === 'prayerHeader' && i.prayerId === prayerId);
        if (idx >= 0) listRef.current?.scrollToIndex({ index: idx, animated: true });
      },
    }));

    const s = styles(colors);

    return (
      <FlashList
        ref={listRef}
        data={items}
        estimatedItemSize={60}
        keyExtractor={(item, i) =>
          item.kind === 'prayerHeader' ? `header-${item.prayerId}` : `seg-${item.segment.id}-${i}`
        }
        renderItem={({ item }) => {
          if (item.kind === 'prayerHeader') {
            return (
              <View style={s.prayerHeader}>
                <Text style={s.prayerHeTitle}>{item.heTitle}</Text>
                <View style={s.prayerHeaderLine} />
                <Text style={s.prayerEnTitle}>{item.enTitle}</Text>
              </View>
            );
          }
          return (
            <View style={s.segmentWrapper}>
              <SegmentRenderer
                segment={item.segment}
                displayMode={displayMode}
                fontStep={fontStep}
                colors={colors}
                isHighlighted={isHighlighted(item.segment.id)}
                notes={getNotes(item.segment.id)}
                onToggleHighlight={() => onToggleHighlight(item.segment.id)}
                onAddNote={(text) => onAddNote(item.segment.id, text)}
              />
            </View>
          );
        }}
        contentContainerStyle={s.listContent}
      />
    );
  }
);

function styles(c: ColorPalette) {
  return StyleSheet.create({
    listContent: { paddingBottom: 120, paddingHorizontal: 16 },
    prayerHeader: {
      paddingTop: 20, paddingBottom: 10,
      borderBottomWidth: 1, borderBottomColor: c.line,
      flexDirection: 'row', alignItems: 'center', gap: 10,
    },
    prayerHeTitle: {
      fontFamily: Fonts.hebrewBold, fontSize: 17, color: c.accent,
      textAlign: 'right', writingDirection: 'rtl',
    },
    prayerHeaderLine: { flex: 1, height: 1, backgroundColor: c.line },
    prayerEnTitle: {
      fontFamily: Fonts.uiMedium, fontSize: 11.5,
      letterSpacing: 1.5, textTransform: 'uppercase', color: c.muted,
    },
    segmentWrapper: { paddingVertical: 2 },
  });
}
```

- [ ] **Step 3: Commit**

```bash
git add src/components/ServiceScroll.tsx
git commit -m "feat: ServiceScroll with FlashList and scrollToPrayer handle"
```

---

### Task 9: JumpToC drawer

**Files:**
- Create: `src/components/JumpToC.tsx`

- [ ] **Step 1: Create the drawer**

Create `src/components/JumpToC.tsx`:

```typescript
import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView, Modal } from 'react-native';
import { Service } from '../content/types';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';

interface Props {
  visible: boolean;
  service: Service;
  colors: ColorPalette;
  onSelectPrayer: (prayerId: string) => void;
  onClose: () => void;
}

export function JumpToC({ visible, service, colors, onSelectPrayer, onClose }: Props) {
  const s = styles(colors);
  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={s.overlay}>
        <Pressable style={s.scrim} onPress={onClose} />
        <View style={s.drawer}>
          <Text style={s.drawerTitle}>{service.enTitle} — Jump to</Text>
          <ScrollView style={s.scroll}>
            {service.groups.map(group => (
              <View key={group.id}>
                <Text style={s.groupLabel}>{group.title}</Text>
                {group.prayers.map(prayer => (
                  <Pressable
                    key={prayer.id}
                    style={({ pressed }) => [s.prayerRow, pressed && { opacity: 0.7 }]}
                    onPress={() => { onSelectPrayer(prayer.id); onClose(); }}
                    accessibilityRole="button"
                    accessibilityLabel={`Jump to ${prayer.enTitle}`}
                  >
                    <Text style={s.prayerEn}>{prayer.enTitle}</Text>
                    <Text style={s.prayerHe}>{prayer.heTitle}</Text>
                  </Pressable>
                ))}
              </View>
            ))}
          </ScrollView>
          <Pressable style={s.closeBtn} onPress={onClose}>
            <Text style={s.closeBtnText}>Close</Text>
          </Pressable>
        </View>
      </View>
    </Modal>
  );
}

function styles(c: ColorPalette) {
  return StyleSheet.create({
    overlay: { flex: 1, flexDirection: 'row' },
    scrim: { flex: 1, backgroundColor: 'rgba(10,12,18,0.45)' },
    drawer: {
      width: '80%', maxWidth: 320, backgroundColor: c.surface,
      borderRightWidth: 1, borderRightColor: c.line,
      paddingTop: 50,
    },
    drawerTitle: {
      fontFamily: Fonts.uiSemiBold, fontSize: 13,
      letterSpacing: 1.2, textTransform: 'uppercase',
      color: c.muted, paddingHorizontal: 18, paddingBottom: 8,
    },
    scroll: { flex: 1 },
    groupLabel: {
      fontFamily: Fonts.uiSemiBold, fontSize: 10.5,
      letterSpacing: 1.6, textTransform: 'uppercase',
      color: c.muted, paddingHorizontal: 18, paddingTop: 14, paddingBottom: 4,
    },
    prayerRow: {
      flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
      paddingVertical: 11, paddingHorizontal: 12, marginHorizontal: 6,
      borderRadius: 10,
    },
    prayerEn: { fontFamily: Fonts.uiMedium, fontSize: 14, color: c.ink, flex: 1 },
    prayerHe: {
      fontFamily: Fonts.hebrew, fontSize: 16, color: c.muted,
      textAlign: 'right', writingDirection: 'rtl',
    },
    closeBtn: {
      margin: 16, padding: 14, backgroundColor: c.accentSoft,
      borderRadius: 12, alignItems: 'center',
    },
    closeBtnText: { fontFamily: Fonts.uiSemiBold, fontSize: 14, color: c.accent },
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/JumpToC.tsx
git commit -m "feat: JumpToC slide-in drawer with group and prayer navigation"
```

---

### Task 10: DisplayToggle and FontSizeControl

**Files:**
- Create: `src/components/DisplayToggle.tsx`
- Create: `src/components/FontSizeControl.tsx`

- [ ] **Step 1: Create DisplayToggle**

Create `src/components/DisplayToggle.tsx`:

```typescript
import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { DisplayMode } from '../store/preferences';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';

const MODES: Array<{ value: DisplayMode; label: string }> = [
  { value: 'he', label: 'עברית' },
  { value: 'both', label: 'Both' },
  { value: 'en', label: 'English' },
];

interface Props {
  value: DisplayMode;
  colors: ColorPalette;
  onChange: (mode: DisplayMode) => void;
}

export function DisplayToggle({ value, colors, onChange }: Props) {
  const s = styles(colors);
  return (
    <View style={s.seg} accessibilityRole="radiogroup" accessibilityLabel="Display language">
      {MODES.map(({ value: v, label }) => (
        <Pressable
          key={v}
          style={[s.btn, value === v && s.btnActive]}
          onPress={() => onChange(v)}
          accessibilityRole="radio"
          accessibilityState={{ checked: value === v }}
          accessibilityLabel={label}
        >
          <Text style={[s.label, value === v && s.labelActive,
            v === 'he' && s.labelHebrew]}>{label}</Text>
        </Pressable>
      ))}
    </View>
  );
}

function styles(c: ColorPalette) {
  return StyleSheet.create({
    seg: {
      flexDirection: 'row', backgroundColor: c.accentSoft,
      borderRadius: 11, padding: 3, flex: 1,
    },
    btn: { flex: 1, paddingVertical: 8, paddingHorizontal: 4, borderRadius: 8, alignItems: 'center' },
    btnActive: { backgroundColor: c.surface, shadowColor: '#000', shadowOpacity: 0.12, shadowRadius: 2 },
    label: { fontFamily: Fonts.uiSemiBold, fontSize: 12, color: c.muted },
    labelActive: { color: c.accent },
    labelHebrew: { fontFamily: Fonts.hebrew, fontSize: 14 },
  });
}
```

- [ ] **Step 2: Create FontSizeControl**

Create `src/components/FontSizeControl.tsx`:

```typescript
import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';

interface Props {
  colors: ColorPalette;
  onBump: (delta: number) => void;
}

export function FontSizeControl({ colors, onBump }: Props) {
  const s = styles(colors);
  return (
    <View style={s.wrap} accessibilityRole="group" accessibilityLabel="Text size">
      <Pressable style={s.btn} onPress={() => onBump(-1)} accessibilityLabel="Smaller text">
        <Text style={s.btnText}>A−</Text>
      </Pressable>
      <Pressable style={s.btn} onPress={() => onBump(1)} accessibilityLabel="Larger text">
        <Text style={[s.btnText, { fontSize: 16 }]}>A+</Text>
      </Pressable>
    </View>
  );
}

function styles(c: ColorPalette) {
  return StyleSheet.create({
    wrap: {
      flexDirection: 'row', alignItems: 'center',
      backgroundColor: c.accentSoft, borderRadius: 11, padding: 3,
    },
    btn: { width: 32, height: 30, alignItems: 'center', justifyContent: 'center', borderRadius: 8 },
    btnText: { fontFamily: Fonts.uiSemiBold, fontSize: 12, color: c.accent },
  });
}
```

- [ ] **Step 3: Commit**

```bash
git add src/components/DisplayToggle.tsx src/components/FontSizeControl.tsx
git commit -m "feat: DisplayToggle and FontSizeControl header components"
```

---

### Task 11: Service reader screen

**Files:**
- Create: `app/daven/[service].tsx`

This is the main reading screen — it wires together all the M1/M2 components.

- [ ] **Step 1: Create the screen**

Create `app/daven/[service].tsx`:

```typescript
import React, { useRef, useState } from 'react';
import { View, Text, Pressable, StyleSheet, useColorScheme, SafeAreaView } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { getService } from '../../src/content/loader';
import { ServiceScroll, ServiceScrollHandle } from '../../src/components/ServiceScroll';
import { JumpToC } from '../../src/components/JumpToC';
import { DisplayToggle } from '../../src/components/DisplayToggle';
import { FontSizeControl } from '../../src/components/FontSizeControl';
import { usePreferencesStore } from '../../src/store/preferences';
import { useAnnotationsStore } from '../../src/store/annotations';
import { LightColors, DarkColors } from '../../src/theme/colors';
import { Fonts } from '../../src/theme/typography';

export default function ServiceScreen() {
  const { service: serviceId } = useLocalSearchParams<{ service: string }>();
  const [tocVisible, setTocVisible] = useState(false);
  const scrollRef = useRef<ServiceScrollHandle>(null);

  const { displayMode, theme, fontStep, setDisplayMode, bumpFontStep } = usePreferencesStore();
  const { isHighlighted, getNotes, toggleHighlight, addNote } = useAnnotationsStore();

  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors = isDark ? DarkColors : LightColors;

  const service = getService(serviceId ?? '');
  if (!service) {
    return (
      <SafeAreaView style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <Text>Service not found.</Text>
      </SafeAreaView>
    );
  }

  const s = styles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safeArea}>
        {/* Header */}
        <View style={s.header}>
          <View style={s.headerBar}>
            <Pressable style={s.iconBtn} onPress={() => setTocVisible(true)} accessibilityLabel="Open table of contents">
              <Text style={s.iconBtnText}>☰</Text>
            </Pressable>
            <View style={s.titleBlock}>
              <Text style={s.titleHe}>{service.heTitle}</Text>
              <Text style={s.titleEn}>{service.enTitle}</Text>
            </View>
            <Pressable style={s.iconBtn} onPress={() => router.back()} accessibilityLabel="Go back">
              <Text style={s.iconBtnText}>←</Text>
            </Pressable>
          </View>
          <View style={s.controlRow}>
            <DisplayToggle value={displayMode} colors={colors} onChange={setDisplayMode} />
            <FontSizeControl colors={colors} onBump={bumpFontStep} />
          </View>
        </View>

        {/* Reading area */}
        <ServiceScroll
          ref={scrollRef}
          service={service}
          displayMode={displayMode}
          fontStep={fontStep}
          colors={colors}
          isHighlighted={isHighlighted}
          getNotes={getNotes}
          onToggleHighlight={toggleHighlight}
          onAddNote={addNote}
        />

        {/* Jump-ToC */}
        <JumpToC
          visible={tocVisible}
          service={service}
          colors={colors}
          onSelectPrayer={(id) => scrollRef.current?.scrollToPrayer(id)}
          onClose={() => setTocVisible(false)}
        />
      </SafeAreaView>
    </View>
  );
}

function styles(c: typeof LightColors) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safeArea: { flex: 1 },
    header: {
      paddingHorizontal: 14, paddingTop: 10, paddingBottom: 10,
      borderBottomWidth: 1, borderBottomColor: c.line,
      backgroundColor: c.surface,
    },
    headerBar: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 10 },
    iconBtn: {
      width: 38, height: 38, alignItems: 'center', justifyContent: 'center',
      borderRadius: 11,
    },
    iconBtnText: { fontSize: 18, color: c.ink },
    titleBlock: { flex: 1, alignItems: 'center' },
    titleHe: { fontFamily: Fonts.hebrewBold, fontSize: 19, color: c.ink },
    titleEn: { fontFamily: Fonts.ui, fontSize: 11, letterSpacing: 1.4, textTransform: 'uppercase', color: c.muted },
    controlRow: { flexDirection: 'row', gap: 8, alignItems: 'center' },
  });
}
```

- [ ] **Step 2: Verify on device**

```bash
npx expo start
```

Navigate to Shacharis. Verify:
- Header shows Hebrew title + English subtitle
- Display toggle switches between Hebrew / Both / English modes
- Font size control scales text up and down
- Hamburger opens ToC drawer; tap a prayer → scrolls there
- Tap a Hebrew line → selection bar → highlight → gold background
- Add a note → shows as chip below the line
- Back arrow returns to service list

- [ ] **Step 3: Commit**

```bash
git add app/daven/[service].tsx
git commit -m "feat: service reader screen with header, scroll, ToC, and annotations"
```

---

### Task 12: Daven home (service list)

**Files:**
- Create: `app/daven/index.tsx`
- Create: `app/index.tsx`

- [ ] **Step 1: Create service list screen**

Create `app/daven/index.tsx`:

```typescript
import React from 'react';
import { View, Text, Pressable, StyleSheet, FlatList, SafeAreaView, useColorScheme } from 'react-native';
import { router } from 'expo-router';
import { listServices } from '../../src/content/loader';
import { usePreferencesStore } from '../../src/store/preferences';
import { LightColors, DarkColors } from '../../src/theme/colors';
import { Fonts } from '../../src/theme/typography';

export default function DavenHome() {
  const { theme } = usePreferencesStore();
  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors = isDark ? DarkColors : LightColors;
  const services = listServices();
  const s = styles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <Text style={s.title}>Daven</Text>
        <FlatList
          data={services}
          keyExtractor={item => item.id}
          contentContainerStyle={s.list}
          renderItem={({ item }) => (
            <Pressable
              style={({ pressed }) => [s.row, pressed && { opacity: 0.7 }]}
              onPress={() => router.push(`/daven/${item.id}`)}
              accessibilityRole="button"
              accessibilityLabel={`Open ${item.enTitle}`}
            >
              <Text style={s.rowEn}>{item.enTitle}</Text>
              <Text style={s.rowHe}>{item.heTitle}</Text>
            </Pressable>
          )}
        />
      </SafeAreaView>
    </View>
  );
}

function styles(c: typeof LightColors) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    title: {
      fontFamily: Fonts.uiSemiBold, fontSize: 28,
      color: c.ink, padding: 24, paddingBottom: 12,
    },
    list: { paddingHorizontal: 16, gap: 8 },
    row: {
      flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
      backgroundColor: c.surface, borderRadius: 14,
      paddingVertical: 16, paddingHorizontal: 18,
      borderWidth: 1, borderColor: c.line,
    },
    rowEn: { fontFamily: Fonts.uiMedium, fontSize: 17, color: c.ink },
    rowHe: { fontFamily: Fonts.hebrewBold, fontSize: 20, color: c.muted, writingDirection: 'rtl' },
  });
}
```

- [ ] **Step 2: Create root redirect**

Create `app/index.tsx`:

```typescript
import { Redirect } from 'expo-router';
import { usePreferencesStore } from '../src/store/preferences';

export default function Root() {
  const { hasCompletedOnboarding } = usePreferencesStore();
  return <Redirect href={hasCompletedOnboarding ? '/daven' : '/onboarding'} />;
}
```

- [ ] **Step 3: Verify end-to-end navigation**

```bash
npx expo start
```

Flow: index → (onboarding not completed) → `/onboarding` (placeholder for now) or directly to `/daven` → tap Shacharis → reader screen. Confirm back navigation works.

- [ ] **Step 4: Commit**

```bash
git add app/daven/index.tsx app/index.tsx
git commit -m "feat: Daven home service list and root redirect"
```

---

## M3 · Personalization

Personalization (highlights, notes, font size, theme) is already wired through the stores built in M1 and surfaced in the reader screen (Task 11). M3 ensures the dark/light theme is properly applied everywhere.

### Task 13: Theme-aware root and dark mode

**Files:**
- Modify: `app/_layout.tsx`

- [ ] **Step 1: Add system color scheme detection to layout**

Update `app/_layout.tsx` to export a theme context:

```typescript
import { Stack } from 'expo-router';
import { useFonts } from 'expo-font';
import { useColorScheme, StatusBar } from 'react-native';
import {
  FrankRuhlLibre_400Regular,
  FrankRuhlLibre_500Medium,
  FrankRuhlLibre_700Bold,
} from '@expo-google-fonts/frank-ruhl-libre';
import {
  Newsreader_400Regular,
  Newsreader_400Regular_Italic,
  Newsreader_500Medium,
} from '@expo-google-fonts/newsreader';
import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
} from '@expo-google-fonts/inter';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { usePreferencesStore } from '../src/store/preferences';
import { DarkColors, LightColors } from '../src/theme/colors';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    FrankRuhlLibre_400Regular,
    FrankRuhlLibre_500Medium,
    FrankRuhlLibre_700Bold,
    Newsreader_400Regular,
    Newsreader_400Regular_Italic,
    Newsreader_500Medium,
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
  });

  const { theme } = usePreferencesStore();
  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors = isDark ? DarkColors : LightColors;

  useEffect(() => {
    if (loaded || error) SplashScreen.hideAsync();
  }, [loaded, error]);

  if (!loaded && !error) return null;

  return (
    <>
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} backgroundColor={colors.paper} />
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.paper } }} />
    </>
  );
}
```

- [ ] **Step 2: Verify dark mode**

Open app, open Settings (or trigger dark mode in Expo Go dev menu). Confirm all screens switch between warm parchment (light) and deep ink-blue (dark) palettes.

- [ ] **Step 3: Commit**

```bash
git add app/_layout.tsx
git commit -m "feat: system-aware dark/light theme from preferences store"
```

---

## M4 · Onboarding & Settings

### Task 14: Onboarding flow

**Files:**
- Create: `app/onboarding.tsx`

- [ ] **Step 1: Create the onboarding screen**

Create `app/onboarding.tsx`:

```typescript
import React, { useState } from 'react';
import { View, Text, Pressable, StyleSheet, SafeAreaView, useColorScheme } from 'react-native';
import { router } from 'expo-router';
import { usePreferencesStore, COMFORT_PRESETS, ComfortLevel } from '../src/store/preferences';
import { LightColors, DarkColors } from '../src/theme/colors';
import { Fonts, hebrewFontSize, englishFontSize } from '../src/theme/typography';
import { DisplayToggle } from '../src/components/DisplayToggle';

type Step = 'welcome' | 'comfort' | 'review';

const COMFORT_OPTIONS: Array<{ value: ComfortLevel; label: string; description: string }> = [
  { value: 'beginner', label: 'Beginner', description: 'I read Hebrew slowly or follow in English' },
  { value: 'comfortable', label: 'Comfortable', description: 'I read Hebrew but value the explanation alongside' },
  { value: 'fluent', label: 'Fluent', description: 'I daven in Hebrew, want a clean Hebrew page' },
];

export default function Onboarding() {
  const [step, setStep] = useState<Step>('welcome');
  const { theme, displayMode, fontStep, comfortLevel, setComfortLevel, setDisplayMode, setTheme, bumpFontStep, completeOnboarding } = usePreferencesStore();

  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors = isDark ? DarkColors : LightColors;
  const s = styles(colors);

  function applyPreset(level: ComfortLevel) {
    setComfortLevel(level);
    const preset = COMFORT_PRESETS[level];
    if (preset.displayMode) setDisplayMode(preset.displayMode);
    if (preset.fontStep !== undefined) {
      const delta = (preset.fontStep ?? 0) - fontStep;
      if (delta !== 0) bumpFontStep(delta);
    }
  }

  if (step === 'welcome') {
    return (
      <View style={[s.screen, { backgroundColor: colors.paper }]}>
        <SafeAreaView style={s.safe}>
          <View style={s.center}>
            <Text style={s.welcomeHe}>סִדּוּר פֵּיגֶנְבַּאוּם</Text>
            <Text style={s.welcomeTitle}>The Feigenbaum Weekday Siddur</Text>
            <Text style={s.welcomeBody}>
              A faithful companion for daily tefillah — the complete weekday liturgy with Rabbi Feigenbaum's insights, built for teens finding their footing in davening.
            </Text>
            <Pressable style={s.primaryBtn} onPress={() => setStep('comfort')}>
              <Text style={s.primaryBtnText}>Let's set it up</Text>
            </Pressable>
            <Pressable style={s.ghostBtn} onPress={() => { completeOnboarding(); router.replace('/daven'); }}>
              <Text style={s.ghostBtnText}>Use defaults</Text>
            </Pressable>
          </View>
        </SafeAreaView>
      </View>
    );
  }

  if (step === 'comfort') {
    return (
      <View style={[s.screen, { backgroundColor: colors.paper }]}>
        <SafeAreaView style={s.safe}>
          <View style={s.content}>
            <Text style={s.stepTitle}>How's your Hebrew davening right now?</Text>
            {COMFORT_OPTIONS.map(opt => (
              <Pressable
                key={opt.value}
                style={[s.comfortOption, comfortLevel === opt.value && s.comfortOptionActive]}
                onPress={() => applyPreset(opt.value)}
                accessibilityRole="radio"
                accessibilityState={{ checked: comfortLevel === opt.value }}
              >
                <Text style={[s.comfortLabel, comfortLevel === opt.value && s.comfortLabelActive]}>{opt.label}</Text>
                <Text style={s.comfortDesc}>{opt.description}</Text>
              </Pressable>
            ))}
            <Pressable style={[s.primaryBtn, { marginTop: 24 }]} onPress={() => setStep('review')}>
              <Text style={s.primaryBtnText}>Next →</Text>
            </Pressable>
          </View>
        </SafeAreaView>
      </View>
    );
  }

  // review step
  const previewHeSize = hebrewFontSize(fontStep);
  const previewEnSize = englishFontSize(fontStep);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <View style={s.content}>
          <Text style={s.stepTitle}>Here are your settings</Text>
          <Text style={s.reviewNote}>You can change any of this anytime in Settings.</Text>

          <Text style={s.controlLabel}>Display</Text>
          <DisplayToggle value={displayMode} colors={colors} onChange={setDisplayMode} />

          <Text style={[s.controlLabel, { marginTop: 16 }]}>Theme</Text>
          <View style={s.themeRow}>
            {(['light', 'dark', 'auto'] as const).map(t => (
              <Pressable
                key={t}
                style={[s.themeBtn, theme === t && s.themeBtnActive]}
                onPress={() => setTheme(t)}
              >
                <Text style={[s.themeBtnText, theme === t && s.themeBtnTextActive]}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </Text>
              </Pressable>
            ))}
          </View>

          <Text style={[s.controlLabel, { marginTop: 16 }]}>Preview</Text>
          <View style={s.previewCard}>
            <Text style={[s.previewHe, { fontSize: previewHeSize, lineHeight: previewHeSize * 1.95 }]}>
              בָּרוּךְ אַתָּה יְיָ אֱלֹהֵינוּ
            </Text>
            {displayMode !== 'he' && (
              <Text style={[s.previewEn, { fontSize: previewEnSize }]}>
                Blessed are You, Hashem our God
              </Text>
            )}
          </View>

          <Pressable style={[s.primaryBtn, { marginTop: 24 }]} onPress={() => { completeOnboarding(); router.replace('/daven'); }}>
            <Text style={s.primaryBtnText}>Start davening →</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    </View>
  );
}

function styles(c: typeof LightColors) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
    content: { flex: 1, padding: 24 },
    welcomeHe: { fontFamily: Fonts.hebrewBold, fontSize: 28, color: c.accent, marginBottom: 8, textAlign: 'center' },
    welcomeTitle: { fontFamily: Fonts.uiSemiBold, fontSize: 18, color: c.ink, textAlign: 'center', marginBottom: 16 },
    welcomeBody: { fontFamily: Fonts.english, fontSize: 16, lineHeight: 25, color: c.ink, textAlign: 'center', marginBottom: 36 },
    primaryBtn: { backgroundColor: c.accent, borderRadius: 14, paddingVertical: 15, paddingHorizontal: 32, alignItems: 'center', width: '100%' },
    primaryBtnText: { fontFamily: Fonts.uiSemiBold, fontSize: 16, color: '#FFFFFF' },
    ghostBtn: { marginTop: 12, padding: 12, alignItems: 'center' },
    ghostBtnText: { fontFamily: Fonts.ui, fontSize: 14, color: c.muted },
    stepTitle: { fontFamily: Fonts.uiSemiBold, fontSize: 22, color: c.ink, marginBottom: 8 },
    reviewNote: { fontFamily: Fonts.ui, fontSize: 13, color: c.muted, marginBottom: 20 },
    comfortOption: {
      borderRadius: 12, padding: 16, marginBottom: 10,
      borderWidth: 1.5, borderColor: c.line, backgroundColor: c.surface,
    },
    comfortOptionActive: { borderColor: c.accent, backgroundColor: c.accentSoft },
    comfortLabel: { fontFamily: Fonts.uiSemiBold, fontSize: 16, color: c.ink, marginBottom: 4 },
    comfortLabelActive: { color: c.accent },
    comfortDesc: { fontFamily: Fonts.ui, fontSize: 13, color: c.muted },
    controlLabel: { fontFamily: Fonts.uiSemiBold, fontSize: 11, letterSpacing: 1.5, textTransform: 'uppercase', color: c.muted, marginBottom: 8 },
    themeRow: { flexDirection: 'row', gap: 8 },
    themeBtn: { flex: 1, paddingVertical: 10, borderRadius: 10, alignItems: 'center', backgroundColor: c.accentSoft },
    themeBtnActive: { backgroundColor: c.accent },
    themeBtnText: { fontFamily: Fonts.uiMedium, fontSize: 13, color: c.muted },
    themeBtnTextActive: { color: '#FFFFFF' },
    previewCard: { backgroundColor: c.surface, borderRadius: 12, padding: 16, borderWidth: 1, borderColor: c.line },
    previewHe: { fontFamily: Fonts.hebrew, color: c.ink, textAlign: 'right', writingDirection: 'rtl' },
    previewEn: { fontFamily: Fonts.english, color: c.ink, marginTop: 8, lineHeight: 24 },
  });
}
```

- [ ] **Step 2: Verify onboarding flow**

```bash
npx expo start
```

Clear AsyncStorage (dev menu → Clear Cache) to force onboarding. Verify:
- Welcome screen shows with warm siddur voice
- "Use defaults" skips to Daven home
- Comfort question sets presets correctly (Beginner = Both + Large, Fluent = Hebrew only)
- Review screen shows live preview reacting to display mode toggle and theme
- "Start davening" lands in Daven home and never shows onboarding again on relaunch

- [ ] **Step 3: Commit**

```bash
git add app/onboarding.tsx
git commit -m "feat: 3-step onboarding flow with comfort presets and live preview"
```

---

### Task 15: Settings screen

**Files:**
- Create: `app/settings.tsx`
- Modify: `app/daven/index.tsx` (add Settings link)

- [ ] **Step 1: Create Settings screen**

Create `app/settings.tsx`:

```typescript
import React from 'react';
import { View, Text, Pressable, StyleSheet, SafeAreaView, useColorScheme, Switch } from 'react-native';
import { router } from 'expo-router';
import { usePreferencesStore } from '../src/store/preferences';
import { LightColors, DarkColors } from '../src/theme/colors';
import { Fonts } from '../src/theme/typography';
import { DisplayToggle } from '../src/components/DisplayToggle';
import { FontSizeControl } from '../src/components/FontSizeControl';

export default function Settings() {
  const { theme, displayMode, setDisplayMode, setTheme, bumpFontStep, resetOnboarding } = usePreferencesStore();
  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors = isDark ? DarkColors : LightColors;
  const s = styles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <View style={s.header}>
          <Pressable onPress={() => router.back()} accessibilityLabel="Go back">
            <Text style={s.backText}>← Back</Text>
          </Pressable>
          <Text style={s.title}>Settings</Text>
        </View>

        <View style={s.section}>
          <Text style={s.sectionLabel}>Default Display</Text>
          <DisplayToggle value={displayMode} colors={colors} onChange={setDisplayMode} />
        </View>

        <View style={s.section}>
          <Text style={s.sectionLabel}>Theme</Text>
          <View style={s.themeRow}>
            {(['light', 'dark', 'auto'] as const).map(t => (
              <Pressable
                key={t}
                style={[s.themeBtn, theme === t && s.themeBtnActive]}
                onPress={() => setTheme(t)}
              >
                <Text style={[s.themeBtnText, theme === t && s.themeBtnTextActive]}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>

        <View style={s.section}>
          <Text style={s.sectionLabel}>Text Size</Text>
          <FontSizeControl colors={colors} onBump={bumpFontStep} />
        </View>

        <View style={s.section}>
          <Pressable
            style={s.resetBtn}
            onPress={() => { resetOnboarding(); router.replace('/onboarding'); }}
          >
            <Text style={s.resetBtnText}>Reset setup wizard</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    </View>
  );
}

function styles(c: typeof LightColors) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1, paddingHorizontal: 20 },
    header: { paddingTop: 16, paddingBottom: 20 },
    backText: { fontFamily: Fonts.uiMedium, fontSize: 15, color: c.accent, marginBottom: 8 },
    title: { fontFamily: Fonts.uiSemiBold, fontSize: 26, color: c.ink },
    section: { marginBottom: 24 },
    sectionLabel: {
      fontFamily: Fonts.uiSemiBold, fontSize: 11, letterSpacing: 1.5,
      textTransform: 'uppercase', color: c.muted, marginBottom: 10,
    },
    themeRow: { flexDirection: 'row', gap: 8 },
    themeBtn: { flex: 1, paddingVertical: 10, borderRadius: 10, alignItems: 'center', backgroundColor: c.accentSoft },
    themeBtnActive: { backgroundColor: c.accent },
    themeBtnText: { fontFamily: Fonts.uiMedium, fontSize: 13, color: c.muted },
    themeBtnTextActive: { color: '#FFFFFF' },
    resetBtn: { padding: 14, borderRadius: 12, borderWidth: 1, borderColor: c.line, alignItems: 'center' },
    resetBtnText: { fontFamily: Fonts.uiMedium, fontSize: 14, color: c.muted },
  });
}
```

- [ ] **Step 2: Add Settings link to Daven home**

In `app/daven/index.tsx`, add a gear icon button in the header that navigates to `/settings`:

```typescript
// Add to header area in DavenHome:
<Pressable onPress={() => router.push('/settings')} accessibilityLabel="Open settings">
  <Text style={{ fontSize: 20, color: colors.muted, padding: 8 }}>⚙</Text>
</Pressable>
```

- [ ] **Step 3: Verify**

Open Settings. Verify: display toggle, theme selector, font size control all work and persist across app restart. "Reset setup wizard" returns to onboarding on next cold start.

- [ ] **Step 4: Commit**

```bash
git add app/settings.tsx app/daven/index.tsx
git commit -m "feat: settings screen with display, theme, font size, and reset"
```

---

## M5 · Remaining Services

### Task 16: Add Minchah, Maariv, Birkas HaMazon content stubs

**Files:**
- Create: `src/content/minchah.json`
- Create: `src/content/maariv.json`
- Create: `src/content/birkas-hamazon.json`
- Modify: `src/content/loader.ts`

Each service follows the exact same schema as `shacharit.json`. The stubs use placeholder Hebrew (public domain) pending proofed Feigenbaum content in M6.

- [ ] **Step 1: Create Minchah stub**

Create `src/content/minchah.json`:

```json
{
  "id": "minchah",
  "heTitle": "מִנְחָה",
  "enTitle": "Minchah",
  "groups": [
    {
      "id": "g-ashrei",
      "title": "Ashrei & Shemoneh Esrei",
      "prayers": [
        {
          "id": "p-ashrei",
          "heTitle": "אַשְׁרֵי",
          "enTitle": "Ashrei",
          "segments": [
            {
              "id": "ashrei-1",
              "type": "prayer",
              "heText": "אַשְׁרֵי יוֹשְׁבֵי בֵיתֶךָ, עוֹד יְהַלְלוּךָ סֶּלָה."
            },
            {
              "id": "ashrei-commentary",
              "type": "commentary",
              "enText": "[Placeholder] Ashrei opens Minchah — we are arriving in the middle of the day, catching our breath and returning to Hashem."
            }
          ]
        }
      ]
    }
  ]
}
```

- [ ] **Step 2: Create Maariv stub**

Create `src/content/maariv.json`:

```json
{
  "id": "maariv",
  "heTitle": "מַעֲרִיב",
  "enTitle": "Maariv",
  "groups": [
    {
      "id": "g-barchu",
      "title": "Barchu & Shema",
      "prayers": [
        {
          "id": "p-barchu",
          "heTitle": "בָּרְכוּ",
          "enTitle": "Barchu",
          "segments": [
            {
              "id": "barchu-1",
              "type": "prayer",
              "heText": "בָּרְכוּ אֶת יְיָ הַמְּבֹרָךְ."
            },
            {
              "id": "barchu-commentary",
              "type": "commentary",
              "enText": "[Placeholder] The call to prayer — the chazan invites the congregation to bless Hashem together."
            }
          ]
        }
      ]
    }
  ]
}
```

- [ ] **Step 3: Create Birkas HaMazon stub**

Create `src/content/birkas-hamazon.json`:

```json
{
  "id": "birkas-hamazon",
  "heTitle": "בִּרְכַּת הַמָּזוֹן",
  "enTitle": "Birkas HaMazon",
  "groups": [
    {
      "id": "g-birchas-hazan",
      "title": "Hazan",
      "prayers": [
        {
          "id": "p-hazan",
          "heTitle": "בִּרְכַּת הַזָּן",
          "enTitle": "Hazan",
          "segments": [
            {
              "id": "hazan-1",
              "type": "prayer",
              "heText": "בָּרוּךְ אַתָּה יְיָ אֱלֹהֵינוּ מֶלֶךְ הָעוֹלָם, הַזָּן אֶת הָעוֹלָם כֻּלּוֹ בְּטוּבוֹ בְּחֵן בְּחֶסֶד וּבְרַחֲמִים."
            },
            {
              "id": "hazan-commentary",
              "type": "commentary",
              "enText": "[Placeholder] The first bracha thanks Hashem for feeding all of creation — not just us, not just today, but the entire world in every era."
            },
            {
              "id": "hazan-insight",
              "type": "insight",
              "enText": "[Placeholder insight] Why do we thank Hashem for food after we've already eaten? Because gratitude, by definition, comes after — it's not anticipation, it's recognition."
            }
          ]
        }
      ]
    }
  ]
}
```

- [ ] **Step 4: Register new services in loader**

Update `src/content/loader.ts`:

```typescript
import { Service } from './types';
import shacharitData from './shacharit.json';
import minchahData from './minchah.json';
import maarivData from './maariv.json';
import birkasMazonData from './birkas-hamazon.json';

const SERVICES: Record<string, Service> = {
  shacharit: shacharitData as Service,
  minchah: minchahData as Service,
  maariv: maarivData as Service,
  'birkas-hamazon': birkasMazonData as Service,
};

export function getService(id: string): Service | null {
  return SERVICES[id] ?? null;
}

export function listServices(): Array<{ id: string; heTitle: string; enTitle: string }> {
  return Object.values(SERVICES).map(({ id, heTitle, enTitle }) => ({ id, heTitle, enTitle }));
}
```

- [ ] **Step 5: Run loader tests**

```bash
npx jest src/content/__tests__/loader.test.ts --no-coverage
```

Expected: all pass (the test only checks shacharit by name but `listServices` now returns 4 items — add one assertion):

Update `loader.test.ts` to add:
```typescript
test('listServices returns 4 services', () => {
  expect(listServices()).toHaveLength(4);
});
```

- [ ] **Step 6: Verify on device**

```bash
npx expo start
```

Daven home shows 4 services. Tap each → reader opens. All follow the same reader template.

- [ ] **Step 7: Commit**

```bash
git add src/content/
git commit -m "feat: add Minchah, Maariv, Birkas HaMazon content stubs"
```

---

## M6 · Content Integration & QA

This milestone is gated on the content pipeline completing (Track A). When proofed Feigenbaum content is delivered, replace the placeholder JSON files with signed-off structured content following the same schema.

### Task 17: Replace placeholder content with proofed data

**Files:**
- Replace: `src/content/shacharit.json` (and all service JSONs)

- [ ] **Step 1: Validate incoming content against schema**

Write a validation script before importing:

Create `scripts/validate-content.ts`:

```typescript
import { Service, Segment } from '../src/content/types';

function validateSegment(seg: Segment, path: string): string[] {
  const errors: string[] = [];
  if (!seg.id) errors.push(`${path}: missing id`);
  if (!['prayer', 'commentary', 'rubric', 'insight'].includes(seg.type))
    errors.push(`${path}: invalid type "${seg.type}"`);
  if (seg.type === 'prayer' && !seg.heText)
    errors.push(`${path}: prayer segment missing heText`);
  if (seg.type === 'commentary' && !seg.enText)
    errors.push(`${path}: commentary segment missing enText`);
  return errors;
}

function validateService(service: Service): string[] {
  const errors: string[] = [];
  if (!service.id) errors.push('service: missing id');
  for (const group of service.groups) {
    for (const prayer of group.prayers) {
      for (const seg of prayer.segments) {
        errors.push(...validateSegment(seg, `${service.id}/${group.id}/${prayer.id}/${seg.id}`));
      }
    }
  }
  return errors;
}

// Usage: import service JSON and call validateService(data)
export { validateService };
```

- [ ] **Step 2: Run validation on each proofed JSON before replacing**

```bash
npx ts-node scripts/validate-content.ts
```

Expected: 0 errors before committing proofed content.

- [ ] **Step 3: Replace placeholder JSONs with proofed content**

Drop in the proofed service JSON files. Run validation. Then:

```bash
git add src/content/*.json
git commit -m "content: replace placeholder with proofed Feigenbaum Shacharis text"
```

- [ ] **Step 4: Device QA — nikkud rendering**

Test on physical iOS and Android devices at every font step (−2 to +4). Verify:
- Nikkud dots and cantillation marks render correctly and don't overlap
- RTL is correct throughout (no reversed characters)
- Long lines wrap correctly in both Hebrew-only and Both modes
- Rubric labels display in the clay color
- Insights expand without layout shift

---

### Task 18: Accessibility and performance QA

**Files:**
- No new files; regression-check existing components

- [ ] **Step 1: Accessibility audit**

With a physical device:
- iOS: Settings → Accessibility → VoiceOver → enable. Navigate through the reader. Every interactive element should be reachable and labeled.
- Android: TalkBack equivalent.

Check: prayer lines have `accessibilityRole="text"`, buttons have `accessibilityLabel`, modal has proper focus trap.

- [ ] **Step 2: Performance on mid-range device**

Test on an older iPhone (SE or similar) with the full Shacharis service loaded. Verify:
- Service opens in under 1 second
- Scroll is smooth (no dropped frames visible)
- FlashList recycles correctly (no blank rows)

- [ ] **Step 3: Offline test**

Enable airplane mode. Relaunch the app. Verify every feature works.

- [ ] **Step 4: Commit fixes**

```bash
git add -A
git commit -m "fix: accessibility and performance QA pass"
```

---

## M7 · Store Readiness

### Task 19: App icons, splash screen, and metadata

**Files:**
- Modify: `app.json`
- Create: `assets/icon.png` (1024×1024)
- Create: `assets/splash.png`

- [ ] **Step 1: Create app icon**

Design a 1024×1024 icon with the tekhelet-indigo accent color (`#34467F`) and a Hebrew letterform or siddur motif. Export as `assets/icon.png`.

- [ ] **Step 2: Update app.json**

```json
{
  "expo": {
    "name": "Feigenbaum Siddur",
    "slug": "digital-siddur",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "scheme": "digital-siddur",
    "userInterfaceStyle": "automatic",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#F6F2E9"
    },
    "ios": {
      "supportsTablet": false,
      "bundleIdentifier": "com.feigenbaum.siddur",
      "buildNumber": "1"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#F6F2E9"
      },
      "package": "com.feigenbaum.siddur",
      "versionCode": 1
    }
  }
}
```

- [ ] **Step 3: Build for TestFlight (iOS)**

```bash
npx eas build --platform ios --profile preview
```

(Requires EAS CLI and Apple Developer account set up.)

- [ ] **Step 4: Submit for internal testing**

```bash
npx eas submit --platform ios
```

Distribute via TestFlight to the author + proofreader for content QA.

- [ ] **Step 5: Build Android internal testing**

```bash
npx eas build --platform android --profile preview
npx eas submit --platform android
```

- [ ] **Step 6: Commit**

```bash
git add app.json assets/
git commit -m "chore: app icon, splash, and metadata for store submission"
```

---

## Self-Review Against PRD

### Spec coverage check

| PRD Requirement | Task |
|---|---|
| F1 · Daven home lists all services | Task 12 |
| F2 · Jump-ToC per service | Task 9 |
| F3 · Continuous vertical scroll | Task 8 |
| F4 · Three-way display toggle, persistent | Task 10 + preferences store |
| F5 · Hebrew RTL with nikkud; English LTR | Task 7 (SegmentRenderer) |
| F6 · Adjustable Hebrew font size | Task 10 + preferences store |
| F7 · Dark / night mode + Auto | Task 13 |
| F8 · Quick-insight expand/collapse | Task 7 (SegmentRenderer) |
| F9 · FAQ/appendix xref data captured | Content schema in Task 3 (`xref` field) |
| F10 · Highlight a passage, persists | Task 6 + Task 7 |
| F11 · Personal note on a passage, persists | Task 6 + Task 7 |
| F12 · Conditional liturgy with rubric labels | Task 7 (rubric segment type) |
| F13 · Offline on first launch | Bundled JSON + no network calls |
| F14 · Onboarding (hybrid) | Task 14 |
| F15 · Settings screen | Task 15 |
| §8 comfort-level presets | `COMFORT_PRESETS` in preferences store |
| §8 first-launch only onboarding | `hasCompletedOnboarding` flag |
| §8 re-runnable from Settings | "Reset setup wizard" in Task 15 |
| §11 design palette | `src/theme/colors.ts` (Task 4) |
| §11 Frank Ruhl Libre / Newsreader / Inter | Task 2 |
| §12 content versioning | `condition` + `xref` fields in schema |

### V2 data hooks confirmed in v1

- `condition` field on segments (winter, rosh_chodesh, etc.) — static label in v1, switch logic in v2
- `xref` field on segments (faq:3, appendix:9) — captured in JSON, not navigable until v2

### Gaps found

None. All F1–F15 requirements and all v2 data hooks are covered.
