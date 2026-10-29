import { useEffect, useState } from 'react';
import { usePreferencesStore } from './preferences';
import { useAnnotationsStore } from './annotations';
import { useReadingPositionStore } from './readingPosition';
import { useZmanimStore } from './zmanim';

// Every persisted store loads from AsyncStorage asynchronously. Screens that
// read persisted values on first render (the onboarding redirect, the reader's
// saved scroll offset) must wait for that load, or they act on defaults.
const PERSISTED_STORES = [
  usePreferencesStore,
  useAnnotationsStore,
  useReadingPositionStore,
  useZmanimStore,
];

// Never hold the app on the splash screen forever: if storage fails to load
// (persist swallows the error and never reports "hydrated"), carry on with
// defaults after this long.
export const HYDRATION_TIMEOUT_MS = 3000;

const allHydrated = () => PERSISTED_STORES.every((s) => s.persist.hasHydrated());

export function useStoresHydrated(): boolean {
  const [hydrated, setHydrated] = useState(allHydrated);

  useEffect(() => {
    if (hydrated) return;
    const check = () => {
      if (allHydrated()) setHydrated(true);
    };
    const unsubs = PERSISTED_STORES.map((s) => s.persist.onFinishHydration(check));
    const timer = setTimeout(() => setHydrated(true), HYDRATION_TIMEOUT_MS);
    check(); // a store may have finished between the initial render and this effect
    return () => {
      unsubs.forEach((u) => u());
      clearTimeout(timer);
    };
  }, [hydrated]);

  return hydrated;
}
