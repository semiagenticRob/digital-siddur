import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AnnotationsState {
  highlights: Set<string>;
  notes: Record<string, string[]>;
  toggleHighlight: (segmentId: string) => void;
  isHighlighted: (segmentId: string) => boolean;
  addNote: (segmentId: string, text: string) => void;
  getNotes: (segmentId: string) => string[];
  removeNote: (segmentId: string, index: number) => void;
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
      removeNote: (id, index) =>
        set((s) => {
          const remaining = (s.notes[id] ?? []).filter((_, i) => i !== index);
          const notes = { ...s.notes };
          if (remaining.length) notes[id] = remaining;
          else delete notes[id];
          return { notes };
        }),
    }),
    {
      name: 'siddur-annotations',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (s) => ({
        highlights: Array.from(s.highlights),
        notes: s.notes,
      }),
      merge: (persisted: unknown, current) => {
        const p = persisted as { highlights?: string[]; notes?: Record<string, string[]> };
        return {
          ...current,
          highlights: new Set(p.highlights ?? []),
          notes: p.notes ?? {},
        };
      },
    }
  )
);
