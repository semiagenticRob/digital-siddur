import React, { useRef, useState } from 'react';
import { View, Text, Pressable, StyleSheet, SafeAreaView, Switch, TextInput } from 'react-native';
import { router } from 'expo-router';
import { usePreferencesStore, ComfortLevel } from '../src/store/preferences';
import { useZmanimStore, ZmanimLocation } from '../src/store/zmanim';
import { resolveDeviceLocation, searchCities } from '../src/lib/location';
import { ColorPalette } from '../src/theme/colors';
import { useThemeColors } from '../src/theme/useThemeColors';
import { Fonts } from '../src/theme/typography';
import { DisplayToggle } from '../src/components/DisplayToggle';
import { FontSizeControl } from '../src/components/FontSizeControl';

const SEARCH_DEBOUNCE_MS = 350;

export default function Settings() {
  const { theme, displayMode, keepAwake, comfortLevel, setDisplayMode, setTheme, bumpFontStep, setKeepAwake, setComfortLevel, resetOnboarding } = usePreferencesStore();
  const { location, setLocation } = useZmanimStore();
  const { colors } = useThemeColors();
  const s = makeStyles(colors);

  const [locating, setLocating] = useState(false);
  const [locateError, setLocateError] = useState(false);
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<ZmanimLocation[]>([]);
  const [searched, setSearched] = useState(false);
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const searchSeq = useRef(0);

  const handleUseMyLocation = async () => {
    setLocateError(false);
    setLocating(true);
    try {
      const loc = await resolveDeviceLocation();
      if (loc) {
        setLocation(loc);
      } else {
        setLocateError(true);
      }
    } catch {
      setLocateError(true);
    } finally {
      setLocating(false);
    }
  };

  const handleQueryChange = (text: string) => {
    setQuery(text);
    setLocateError(false);
    if (searchTimer.current) clearTimeout(searchTimer.current);
    const trimmed = text.trim();
    if (!trimmed) {
      setResults([]);
      setSearching(false);
      setSearched(false);
      return;
    }
    setSearching(true);
    setSearched(false);
    const seq = ++searchSeq.current;
    searchTimer.current = setTimeout(async () => {
      try {
        const hits = await searchCities(trimmed);
        if (seq !== searchSeq.current) return; // stale — a newer search superseded this one
        setResults(hits.slice(0, 6));
      } catch {
        if (seq !== searchSeq.current) return;
        setResults([]);
      } finally {
        if (seq === searchSeq.current) {
          setSearching(false);
          setSearched(true);
        }
      }
    }, SEARCH_DEBOUNCE_MS);
  };

  const handleSelectCity = (loc: ZmanimLocation) => {
    setLocation(loc);
    setQuery('');
    setResults([]);
    setSearched(false);
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

          <TextInput
            style={[s.cityInput, { backgroundColor: colors.surface, borderColor: colors.line, color: colors.ink }]}
            value={query}
            onChangeText={handleQueryChange}
            placeholder="Search for a city…"
            placeholderTextColor={colors.muted}
            accessibilityLabel="Search for a city"
          />

          {searching && (
            <Text style={[s.sectionHint, { color: colors.muted }]}>Searching…</Text>
          )}
          {!searching && searched && results.length === 0 && (
            <Text style={[s.sectionHint, { color: colors.muted }]}>No cities found</Text>
          )}

          {results.map((r, i) => (
            <Pressable
              key={`${r.label}-${r.latitude}-${r.longitude}-${i}`}
              style={[s.cityResult, { backgroundColor: colors.surface, borderColor: colors.line }]}
              onPress={() => handleSelectCity(r)}
              accessibilityRole="button"
              accessibilityLabel={`Set location to ${r.label}`}
            >
              <Text style={[s.switchLabel, { color: colors.ink }]}>{r.label}</Text>
            </Pressable>
          ))}

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
    cityInput: {
      borderWidth: 1,
      borderRadius: 10,
      paddingHorizontal: 12,
      paddingVertical: 10,
      fontFamily: Fonts.ui,
      fontSize: 14,
      marginTop: 10,
    },
    cityResult: {
      borderWidth: 1,
      borderRadius: 10,
      paddingHorizontal: 12,
      paddingVertical: 10,
      marginTop: 8,
    },
    zmanimFooter: { fontFamily: Fonts.ui, fontSize: 11.5, marginTop: 12 },
  });
}
