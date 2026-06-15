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

export const COMFORT_PRESETS: Record<ComfortLevel, { displayMode: DisplayMode; fontStep: number; theme: Theme }> = {
  beginner: { displayMode: 'both', fontStep: 1, theme: 'auto' },
  comfortable: { displayMode: 'both', fontStep: 0, theme: 'auto' },
  fluent: { displayMode: 'he', fontStep: 0, theme: 'auto' },
};
