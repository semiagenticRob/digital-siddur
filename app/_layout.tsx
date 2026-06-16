import { Stack } from 'expo-router';
import { useFonts } from 'expo-font';
import { useColorScheme, StatusBar } from 'react-native';
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
import { usePreferencesStore } from '../src/store/preferences';
import { DarkColors, LightColors } from '../src/theme/colors';
import { AppendixModal } from '../src/components/AppendixModal';

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

  const { theme } = usePreferencesStore();
  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors = isDark ? DarkColors : LightColors;

  useEffect(() => {
    if (loaded || error) SplashScreen.hideAsync();
  }, [loaded, error]);

  if (!loaded && !error) return null;

  return (
    <>
      <StatusBar
        barStyle={isDark ? 'light-content' : 'dark-content'}
        backgroundColor={colors.paper}
      />
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.paper } }} />
      <AppendixModal />
    </>
  );
}
