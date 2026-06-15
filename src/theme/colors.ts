export const LightColors = {
  paper: '#F6F2E9',
  surface: '#FDFBF5',
  ink: '#1E2433',
  muted: '#6C7180',
  line: '#E4DECF',
  accent: '#34467F',
  accentSoft: '#EBEEF8',
  gold: '#D9A53B',
  goldFill: 'rgba(217,165,59,0.30)',
  rubric: '#897640',
} as const;

export const DarkColors = {
  paper: '#11141C',
  surface: '#191D27',
  ink: '#ECE6D8',
  muted: '#969CAB',
  line: '#2A2F3C',
  accent: '#94A6E2',
  accentSoft: '#222a3f',
  gold: '#E6B651',
  goldFill: 'rgba(230,182,81,0.20)',
  rubric: '#BBA877',
} as const;

export type ColorPalette = typeof LightColors | typeof DarkColors;
