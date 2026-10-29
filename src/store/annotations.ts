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
      // zustand calls merge(undefined, …) on a fresh install (nothing stored
      // yet), and storage could hold an unexpected shape — tolerate both so
      // hydration always completes.
      merge: (persisted: unknown, current) => {
        const p = (persisted ?? {}) as { highlights?: unknown; notes?: unknown };
        const highlights = Array.isArray(p.highlights)
          ? p.highlights.filter((id): id is string => typeof id === 'string')
          : [];
        const notes: Record<string, string[]> = {};
        if (p.notes && typeof p.notes === 'object' && !Array.isArray(p.notes)) {
          for (const [id, texts] of Object.entries(p.notes as Record<string, unknown>)) {
            if (Array.isArray(texts)) {
              const clean = texts.filter((t): t is string => typeof t === 'string');
              if (clean.length) notes[id] = clean;
            }
          }
        }
        return { ...current, highlights: new Set(highlights), notes };
      },
    }
  )
);
