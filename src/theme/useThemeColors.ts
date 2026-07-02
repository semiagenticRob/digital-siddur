import { useColorScheme } from 'react-native';
import { usePreferencesStore } from '../store/preferences';
import { LightColors, DarkColors, SepiaColors, ColorPalette } from './colors';

// Single source of truth for theme → palette resolution (was previously
// duplicated across every screen/modal).
export function useThemeColors(): { colors: ColorPalette; isDark: boolean } {
  const theme = usePreferencesStore((s) => s.theme);
  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors: ColorPalette = theme === 'sepia' ? SepiaColors : isDark ? DarkColors : LightColors;
  return { colors, isDark };
}
