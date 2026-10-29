import React, { useRef, useState } from 'react';
import { View, Text, Pressable, StyleSheet, Switch } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { usePreferencesStore, ComfortLevel } from '../src/store/preferences';
import { useZmanimStore, ZmanimLocation } from '../src/store/zmanim';
import { resolveDeviceLocation } from '../src/lib/location';
import { ColorPalette } from '../src/theme/colors';
import { useThemeColors } from '../src/theme/useThemeColors';
import { Fonts } from '../src/theme/typography';
import { DisplayToggle } from '../src/components/DisplayToggle';
import { FontSizeControl } from '../src/components/FontSizeControl';
import { CitySearch } from '../src/components/CitySearch';

export default function Settings() {
  const { theme, displayMode, keepAwake, comfortLevel, setDisplayMode, setTheme, bumpFontStep, setKeepAwake, setComfortLevel, resetOnboarding } = usePreferencesStore();
  const { location, setLocation } = useZmanimStore();
  const { colors } = useThemeColors();
  const s = makeStyles(colors);

  const [locating, setLocating] = useState(false);
  const [locateError, setLocateError] = useState(false);
  // Same guard as onboarding: a device-location lookup can take seconds, and
  // if the user picks a city meanwhile, the late result must not replace it.
  const reqSeq = useRef(0);

  const handleUseMyLocation = async () => {
    const seq = ++reqSeq.current;
    setLocateError(false);
    setLocating(true);
    try {
      const loc = await resolveDeviceLocation();
      if (seq !== reqSeq.current) return; // user picked a city meanwhile
      if (loc) {
        setLocation(loc);
      } else {
        setLocateError(true);
      }
    } catch {
      if (seq === reqSeq.current) setLocateError(true);
    } finally {
      if (seq === reqSeq.current) setLocating(false);
    }
  };

  const handlePickCity = (loc: ZmanimLocation) => {
    reqSeq.current++; // supersede any in-flight device-location lookup
    setLocating(false);
    setLocateError(false);
    setLocation(loc);
  };

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <View style={s.header}>
          <Pressable
            onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
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
            {(['light', 'sepia', 'dark', 'auto'] as const).map(t => (
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
          <Text style={[s.sectionLabel, { color: colors.muted }]}>Hebrew Comfort</Text>
          <View style={s.themeRow}>
            {(['beginner', 'comfortable', 'fluent'] as ComfortLevel[]).map(level => (
              <Pressable
                key={level}
                style={[
                  s.themeBtn,
                  { backgroundColor: colors.accentSoft },
                  comfortLevel === level && { backgroundColor: colors.accent },
                ]}
                onPress={() => setComfortLevel(level)}
                accessibilityRole="radio"
                accessibilityState={{ checked: comfortLevel === level }}
              >
                <Text style={[
                  s.themeBtnText,
                  { color: colors.muted },
                  comfortLevel === level && { color: '#FFFFFF' },
                ]}>
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </Text>
              </Pressable>
            ))}
          </View>
          <Text style={[s.sectionHint, { color: colors.muted }]}>
            Beginner opens the Insight and FAQ boxes automatically.
          </Text>
        </View>

        <View style={s.section}>
          <Text style={[s.sectionLabel, { color: colors.muted }]}>While Davening</Text>
          <View style={s.switchRow}>
            <Text style={[s.switchLabel, { color: colors.ink }]}>Keep screen awake</Text>
            <Switch
              value={keepAwake}
              onValueChange={setKeepAwake}
              trackColor={{ true: colors.accent }}
              accessibilityLabel="Keep screen awake while a service is open"
            />
          </View>
        </View>

        <View style={s.section}>
          <Text style={[s.sectionLabel, { color: colors.muted }]}>Zmanim</Text>

          <Text style={[s.switchLabel, { color: location ? colors.ink : colors.muted, marginBottom: 12 }]}>
            {location ? location.label : 'Not set'}
          </Text>

          <Pressable
            style={[s.locateBtn, { backgroundColor: colors.accentSoft }]}
            onPress={handleUseMyLocation}
            disabled={locating}
            accessibilityRole="button"
            accessibilityLabel="Use my location"
          >
            <Text style={[s.locateBtnText, { color: colors.accent }]}>
              {locating ? 'Locating…' : 'Use my location'}
            </Text>
          </Pressable>

          {locateError && (
            <Text style={[s.sectionHint, { color: colors.muted }]}>
              Couldn't get your location — search for your city below.
            </Text>
          )}

          <CitySearch
            colors={colors}
            onSelect={handlePickCity}
            onQueryChange={() => setLocateError(false)}
          />

          <Text style={[s.zmanimFooter, { color: colors.muted }]}>
            Zmanim powered by Hebcal.com (hebcal.com) · CC BY 4.0
          </Text>
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
    switchRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    switchLabel: { fontFamily: Fonts.uiMedium, fontSize: 14 },
    sectionHint: { fontFamily: Fonts.ui, fontSize: 12, marginTop: 8 },
    themeBtn: { flex: 1, paddingVertical: 10, borderRadius: 10, alignItems: 'center' },
    themeBtnText: { fontFamily: Fonts.uiMedium, fontSize: 13 },
    resetBtn: { padding: 14, borderRadius: 12, borderWidth: 1, alignItems: 'center' },
    resetBtnText: { fontFamily: Fonts.uiMedium, fontSize: 14 },
    locateBtn: { paddingVertical: 12, borderRadius: 10, alignItems: 'center', marginBottom: 10 },
    locateBtnText: { fontFamily: Fonts.uiMedium, fontSize: 14 },
    zmanimFooter: { fontFamily: Fonts.ui, fontSize: 11.5, marginTop: 12 },
  });
}
