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
  optionalShade: '#ECE8DC',
  optionalBorder: '#DAD3C2',
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
  optionalShade: '#171B24',
  optionalBorder: '#2A2F3C',
} as const;

// Warm print-paper palette: deeper amber ground than light, monochrome-warm
// ink/accent so the page reads like an aged siddur rather than a blue-accented
// screen.
export const SepiaColors = {
  paper: '#F3E9D2',
  surface: '#F9F1DE',
  ink: '#3B2F1E',
  muted: '#7A6C52',
  line: '#E0D3B4',
  accent: '#7C5A21',
  accentSoft: '#EFE3C6',
  gold: '#C89032',
  goldFill: 'rgba(200,144,50,0.30)',
  rubric: '#8A6E33',
  optionalShade: '#EBDFC2',
  optionalBorder: '#D8C89F',
} as const;

// Mapped-string type so every palette (and future ones) is mutually assignable.
export type ColorPalette = { [K in keyof typeof LightColors]: string };
