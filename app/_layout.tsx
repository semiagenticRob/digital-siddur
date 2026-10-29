import { Stack } from 'expo-router';
import { useFonts } from 'expo-font';
import { StatusBar } from 'react-native';
import {
  FrankRuhlLibre_400Regular,
  FrankRuhlLibre_500Medium,
  FrankRuhlLibre_700Bold,
} from '@expo-google-fonts/frank-ruhl-libre';
import {
  Newsreader_400Regular,
  Newsreader_400Regular_Italic,
  Newsreader_500Medium,
  Newsreader_600SemiBold,
} from '@expo-google-fonts/newsreader';
import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
} from '@expo-google-fonts/inter';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { useThemeColors } from '../src/theme/useThemeColors';
import { AppendixModal } from '../src/components/AppendixModal';
import { SectionModal } from '../src/components/SectionModal';
import { useStoresHydrated } from '../src/store/hydration';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    FrankRuhlLibre_400Regular,
    FrankRuhlLibre_500Medium,
    FrankRuhlLibre_700Bold,
    Newsreader_400Regular,
    Newsreader_400Regular_Italic,
    Newsreader_500Medium,
    Newsreader_600SemiBold,
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
  });

  const { colors, isDark } = useThemeColors();
  // Hold the splash until saved settings, annotations and reading positions
  // have loaded — otherwise the onboarding redirect and scroll restore act on
  // defaults (a returning user could be sent back through onboarding).
  const storesHydrated = useStoresHydrated();
  const ready = (loaded || !!error) && storesHydrated;

  useEffect(() => {
    if (ready) SplashScreen.hideAsync();
  }, [ready]);

  if (!ready) return null;

  return (
    <>
      <StatusBar
        barStyle={isDark ? 'light-content' : 'dark-content'}
        backgroundColor={colors.paper}
      />
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.paper } }} />
      <AppendixModal />
      <SectionModal />
    </>
  );
}
