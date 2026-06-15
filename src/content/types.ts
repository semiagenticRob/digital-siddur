export type SegmentType = 'prayer' | 'commentary' | 'rubric' | 'insight';

export interface Segment {
  id: string;
  type: SegmentType;
  heText?: string;       // Hebrew with nikkud; present on prayer/rubric
  enText?: string;       // English explanation; present on commentary/insight
  condition?: string;    // e.g. "winter", "rosh_chodesh" — v2 logic; shown as rubric label in v1
  xref?: string;         // e.g. "faq:3" — captured now, navigable in v2
}

export interface Prayer {
  id: string;
  heTitle: string;
  enTitle: string;
  segments: Segment[];
}

export interface Group {
  id: string;
  title: string;
  prayers: Prayer[];
}

export interface Service {
  id: string;
  heTitle: string;
  enTitle: string;
  groups: Group[];
}
