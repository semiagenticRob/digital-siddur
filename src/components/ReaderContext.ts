import { createContext } from 'react';

// Provided by the reader screen so inline [label](prayer:svc/id) links can
// scroll in place when the target is the CURRENT service instead of pushing a
// duplicate reader screen. Absent (null) outside the reader — e.g. in the
// Appendix/Section modals — where links always navigate.
export interface ReaderContextValue {
  serviceId: string;
  scrollToPrayer: (prayerId: string) => void;
}

export const ReaderContext = createContext<ReaderContextValue | null>(null);
