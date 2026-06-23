import { create } from 'zustand';

interface SectionModalState {
  openKey: string | null;
  open: (key: string) => void;
  close: () => void;
}

export const useSectionModalStore = create<SectionModalState>((set) => ({
  openKey: null,
  open: (key) => set({ openKey: key }),
  close: () => set({ openKey: null }),
}));
