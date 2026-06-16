export const Fonts = {
  hebrew: 'FrankRuhlLibre_500Medium',
  hebrewBold: 'FrankRuhlLibre_700Bold',
  hebrewRegular: 'FrankRuhlLibre_400Regular',
  english: 'Newsreader_400Regular',
  englishItalic: 'Newsreader_400Regular_Italic',
  englishBold: 'Newsreader_600SemiBold',
  ui: 'Inter_400Regular',
  uiMedium: 'Inter_500Medium',
  uiSemiBold: 'Inter_600SemiBold',
} as const;

export const BASE_HE_SIZE = 24.15; // 21 × 1.15 — Hebrew default 15% larger
export const BASE_EN_SIZE = 15.5;
export const FONT_STEP_SCALE = 0.12;

export function hebrewFontSize(fontStep: number): number {
  return BASE_HE_SIZE * (1 + fontStep * FONT_STEP_SCALE);
}

export function englishFontSize(fontStep: number): number {
  return BASE_EN_SIZE * (0.55 + (1 + fontStep * FONT_STEP_SCALE) * 0.45);
}
