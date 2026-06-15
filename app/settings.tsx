import React from 'react';
import { View, Text, Pressable, StyleSheet, SafeAreaView, useColorScheme } from 'react-native';
import { router } from 'expo-router';
import { usePreferencesStore } from '../src/store/preferences';
import { LightColors, DarkColors, ColorPalette } from '../src/theme/colors';
import { Fonts } from '../src/theme/typography';
import { DisplayToggle } from '../src/components/DisplayToggle';
import { FontSizeControl } from '../src/components/FontSizeControl';

export default function Settings() {
  const { theme, displayMode, setDisplayMode, setTheme, bumpFontStep, resetOnboarding } = usePreferencesStore();
  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors = isDark ? DarkColors : LightColors;
  const s = makeStyles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <View style={s.header}>
          <Pressable
            onPress={() => router.back()}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Text style={[s.backText, { color: colors.accent }]}>← Back</Text>
          </Pressable>
          <Text style={[s.title, { color: colors.ink }]}>Settings</Text>
        </View>

        <View style={s.section}>
          <Text style={[s.sectionLabel, { color: colors.muted }]}>Default Display</Text>
          <DisplayToggle value={displayMode} colors={colors} onChange={setDisplayMode} />
        </View>

        <View style={s.section}>
          <Text style={[s.sectionLabel, { color: colors.muted }]}>Theme</Text>
          <View style={s.themeRow}>
            {(['light', 'dark', 'auto'] as const).map(t => (
              <Pressable
                key={t}
                style={[
                  s.themeBtn,
                  { backgroundColor: colors.accentSoft },
                  theme === t && { backgroundColor: colors.accent },
                ]}
                onPress={() => setTheme(t)}
                accessibilityRole="radio"
                accessibilityState={{ checked: theme === t }}
              >
                <Text style={[
                  s.themeBtnText,
                  { color: colors.muted },
                  theme === t && { color: '#FFFFFF' },
                ]}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>

        <View style={s.section}>
          <Text style={[s.sectionLabel, { color: colors.muted }]}>Text Size</Text>
          <FontSizeControl colors={colors} onBump={bumpFontStep} />
        </View>

        <View style={s.section}>
          <Pressable
            style={[s.resetBtn, { borderColor: colors.line }]}
            onPress={() => { resetOnboarding(); router.replace('/onboarding'); }}
            accessibilityRole="button"
            accessibilityLabel="Reset setup wizard"
          >
            <Text style={[s.resetBtnText, { color: colors.muted }]}>Reset setup wizard</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1, paddingHorizontal: 20 },
    header: { paddingTop: 16, paddingBottom: 20 },
    backText: { fontFamily: Fonts.uiMedium, fontSize: 15, marginBottom: 8 },
    title: { fontFamily: Fonts.uiSemiBold, fontSize: 26 },
    section: { marginBottom: 24 },
    sectionLabel: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 11,
      letterSpacing: 1.5,
      textTransform: 'uppercase' as const,
      marginBottom: 10,
    },
    themeRow: { flexDirection: 'row', gap: 8 },
    themeBtn: { flex: 1, paddingVertical: 10, borderRadius: 10, alignItems: 'center' },
    themeBtnText: { fontFamily: Fonts.uiMedium, fontSize: 13 },
    resetBtn: { padding: 14, borderRadius: 12, borderWidth: 1, alignItems: 'center' },
    resetBtnText: { fontFamily: Fonts.uiMedium, fontSize: 14 },
  });
}
