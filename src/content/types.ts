export type SegmentType =
  | 'prayer'        // Hebrew liturgical text
  | 'commentary'    // English explanation (word-by-word gloss or paragraph)
  | 'rubric'        // Instructional label ("For women:", "in winter add:", etc.)
  | 'insight'       // Expandable "Instant Insight" callout
  | 'faq'           // Margin FAQ/Answer box
  | 'header'        // Section heading (Hebrew, English, or both)
  | 'section_intro' // Bold English preamble before a prayer group
  | 'transition';   // Rhetorical bridge line carrying you from one prayer to the next

export interface Segment {
  id: string;
  type: SegmentType;
  heText?: string;   // Hebrew with nikkud — prayer, rubric (Hebrew rubrics), header
  enText?: string;   // English text — commentary, insight, faq, section_intro, header, English rubrics
  condition?: string; // e.g. "winter", "rosh_chodesh" — static label in v1, logic in v2
  xref?: string;     // e.g. "faq:3", "appendix:9" — captured now, navigable in v2
  enPrimary?: boolean; // header only: big English title above a small Hebrew name-list (subtitle sizing)
  heTop?: boolean;     // header only: keep Hebrew on top (default is English caps label above the
                       // Hebrew title). Use when the English is a mere transliteration (e.g. Ashrei).
  plain?: boolean;     // header only: centered in ink color, no accent/rule (a quiet incipit)
  optional?: boolean;  // segment belongs to an optional passage — rendered inside a shaded box
                       // (a contiguous run of optional segments forms one box, as in the print)
  display?: boolean;   // prayer only: render as a large, centered display verse (the Kedushah
                       // climaxes — קדוש / ברוך כבוד / ימלך — which the print sets oversized & centered)
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

export interface Appendix {
  number: number;
  title: string;
  segments: Segment[];
}
