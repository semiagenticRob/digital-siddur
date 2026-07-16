# Onboarding Location Permission Step — Design

**Date:** 2026-07-16
**Status:** Design approved; spec pending user review

## Goal

Ask for when-in-use location permission during onboarding, on its own step immediately
after the welcome screen, so zmanim work from first launch instead of waiting for the
user to discover the picker in Settings.

The permission plumbing already exists and is **not** changed by this work:

- `src/lib/location.ts` — `resolveDeviceLocation()` requests when-in-use permission,
  takes a low-accuracy fix, reverse-geocodes a city label, and returns `null` on any
  denial or failure without throwing. `searchCities()` backs the manual fallback.
- `app.json:43` — the `expo-location` plugin is registered with
  `locationWhenInUsePermission` already scoped to zmanim.
- `src/store/zmanim.ts` — `setLocation()` stores the location and resets the cache.

This round is a new wizard step plus one extraction. No new dependencies.

## Flow

`app/onboarding.tsx` is a self-contained wizard driven by `useState<Step>`; steps are
local state, not routes. The `Step` union grows from `'welcome' | 'comfort' | 'review'`
to `'welcome' | 'location' | 'comfort' | 'review'`.

Both welcome buttons route into the location step, but they mean different things
afterward:

```
welcome ──"Let's set it up"──► location ──► comfort ──► review ──► finish()
        └──"Use defaults"─────► location ──────────────────────► finish()
```

A `const [fullSetup, setFullSetup] = useState(true)`, set by whichever welcome button
was pressed, decides whether the location step's continue action goes to `'comfort'` or
calls `finish()`.

**User decision (2026-07-16):** "Use defaults" still asks for location. It means default
*preferences*, not "skip everything" — location is asked on the way into the app.

`finish()` is unchanged: `completeOnboarding()` then `router.replace('/daven')`.

## The location step

Never calls `expo-location` directly — it calls `resolveDeviceLocation()`. On a non-null
result it calls `useZmanimStore().setLocation(loc)` and shows the resolved state.

Three states:

| State | Shows |
|---|---|
| **Initial** | Heading, one short paragraph on why (halachic times for where you are; leaves the device only to fetch those times), "Allow location" primary button, "Not now" ghost button. |
| **Denied / "Not now"** | Explanation replaced by `CitySearch`. |
| **Resolved** | Confirmation of the chosen label ("Zmanim set for Thornhill"), a continue button, and a way back to search. |

Reuses the welcome screen's existing `primaryBtn` / `ghostBtn` styles from
`makeStyles()`.

Note the two "Not now" buttons are **not** the same action:

- "Not now" in the **initial** state declines the OS prompt without showing it and moves
  to the denied state, so the user still gets a chance to pick a city by hand.
- "Not now" in the **denied** state (below the search) leaves the step with no location
  set and advances per `fullSetup`.

**User decision (2026-07-16):** on denial, offer city search inline rather than deferring
to Settings.

### Copy on re-denial

After an OS-level denial, iOS does not re-prompt — a second "Allow location" tap would
silently do nothing. So the denied state's copy points at search ("Search for your city
instead") rather than inviting a retry that cannot work.

### Pending-promise handling

The OS prompt is a real modal. If the user backgrounds the app mid-prompt,
`resolveDeviceLocation()` stays pending. The step holds its `locating` flag until the
promise settles — same as `app/settings.tsx:40` does today.

### Skipping is a supported end state

"Not now" from the search state advances with no location set. Nothing is lost:
`src/components/NowCard.tsx:103` already renders a "set location" row when `location` is
null, and Settings has the full picker.

## Extracting `CitySearch`

The only part of this work that edits working code rather than adding to it.

`app/settings.tsx:24-98` holds a search state machine: query state, a 350ms debounce
timer, a `searchSeq` stale-guard so a slow response cannot overwrite a newer one, an
unmount cleanup that cancels the timer and bumps the seq, and three distinct empty states
(searching / no results / search failed). Duplicating ~75 lines of that into onboarding
would mean two copies of a concurrency-sensitive guard that must stay in sync.

Extract into **`src/components/CitySearch.tsx`**, owning the debounce, the seq guard, the
results list, and the empty states. Props:

```ts
interface CitySearchProps {
  colors: ColorPalette;
  onSelect: (loc: ZmanimLocation) => void;
}
```

Settings and onboarding both render it. Settings' "Use my location" button and
current-location display **stay in `settings.tsx`** — only the search moves.

## Out of scope

- No content JSON changes.
- No `app.json` changes — plugin and usage string are already correct and scoped to
  when-in-use.
- No changes to `src/store/zmanim.ts` or `resolveDeviceLocation()`.
- No `preferences.ts` changes. Location lives in the zmanim store. No new "has seen
  location prompt" flag: asking once during onboarding and letting Settings own it
  afterward needs no extra state.
- No new dependencies.

## Verification

This repo tests stores and pure lib functions; there is no component-testing library
installed (no `@testing-library/react-native`, no `react-test-renderer`), and this design
does not add one.

The seam that carries real concurrency risk is `searchCities()`, already covered by
`src/lib/__tests__/location.test.ts` and untouched here. The extraction moves view code.

So verification is:

1. `npm run check` (typecheck + strict content lint + jest) — must pass.
2. Drive both screens in the simulator: onboarding allow-path, onboarding deny-path into
   city search, onboarding skip-path, and Settings' search after the extraction.
