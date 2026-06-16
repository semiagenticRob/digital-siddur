import { create } from 'zustand';

interface AppendixState {
  openNumber: number | null;
  open: (n: number) => void;
  close: () => void;
}

// Global handle so an "Appendix N" link anywhere in the tree can open the viewer.
export const useAppendixStore = create<AppendixState>((set) => ({
  openNumber: null,
  open: (n) => set({ openNumber: n }),
  close: () => set({ openNumber: null }),
}));
