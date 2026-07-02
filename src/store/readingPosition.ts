import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Last scroll offset per service, so reopening a service resumes where the
// user left off (a davener returning mid-Shacharis shouldn't start at Modeh
// Ani). Offsets are approximate across displayMode/fontStep changes — that's
// fine, the restore is best-effort.
interface ReadingPositionState {
  offsets: Record<string, number>;
  setOffset: (serviceId: string, offset: number) => void;
  clearOffset: (serviceId: string) => void;
}

export const useReadingPositionStore = create<ReadingPositionState>()(
  persist(
    (set) => ({
      offsets: {},
      setOffset: (serviceId, offset) =>
        set((s) => ({ offsets: { ...s.offsets, [serviceId]: offset } })),
      clearOffset: (serviceId) =>
        set((s) => {
          const { [serviceId]: _removed, ...rest } = s.offsets;
          return { offsets: rest };
        }),
    }),
    {
      name: 'siddur-reading-position',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
