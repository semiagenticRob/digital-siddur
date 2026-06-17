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
  enPrimary?: boolean; // header only: render the English title above the Hebrew names line
  plain?: boolean;     // header only: centered in ink color, no accent/rule (a quiet incipit)
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
