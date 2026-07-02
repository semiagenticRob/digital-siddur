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
          if (dates.length === 0) return; // empty batch — don't reset fetchedThrough
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
          // A slow fetch started for a since-abandoned location must not
          // land after the user switched — setLocation always stores a new
          // object, so identity comparison catches the switch even if the
          // new location's fields happen to coincide with the old one.
          if (get().location !== location) return;
          // Drop cached days that have already passed so the cache doesn't
          // grow unbounded with days that will never be shown again.
          const pruned = Object.fromEntries(
            Object.entries(days).filter(([date]) => date >= todayKey)
          );
          set({ days: pruned, fetchedThrough: last });
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
