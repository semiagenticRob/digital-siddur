import React, { useRef, useState } from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { usePreferencesStore, COMFORT_PRESETS, ComfortLevel } from '../src/store/preferences';
import { ColorPalette } from '../src/theme/colors';
import { useThemeColors } from '../src/theme/useThemeColors';
import { Fonts, hebrewFontSize, englishFontSize } from '../src/theme/typography';
import { DisplayToggle } from '../src/components/DisplayToggle';
import { useZmanimStore, ZmanimLocation } from '../src/store/zmanim';
import { resolveDeviceLocation } from '../src/lib/location';
import { CitySearch } from '../src/components/CitySearch';

type Step = 'welcome' | 'location' | 'comfort' | 'review';

const COMFORT_OPTIONS: Array<{ value: ComfortLevel; label: string; description: string }> = [
  { value: 'beginner', label: 'Beginner', description: 'I read Hebrew slowly or follow in English' },
  { value: 'comfortable', label: 'Comfortable', description: 'I read Hebrew but value the explanation alongside' },
  { value: 'fluent', label: 'Fluent', description: 'I daven in Hebrew, want a clean Hebrew page' },
];

export default function Onboarding() {
  const [step, setStep] = useState<Step>('welcome');
  const {
    theme, displayMode, fontStep, comfortLevel,
    setComfortLevel, setDisplayMode, setTheme, bumpFontStep, completeOnboarding,
  } = usePreferencesStore();

  // Which welcome button got us here. "Let's set it up" continues into the
  // comfort/review steps; "Use defaults" still asks for location, then goes
  // straight into the app with default preferences.
  const [fullSetup, setFullSetup] = useState(true);
  const [locating, setLocating] = useState(false);
  const [locationDenied, setLocationDenied] = useState(false);
  const [resolved, setResolved] = useState<ZmanimLocation | null>(null);
  const setLocation = useZmanimStore(state => state.setLocation);
  // Bumped whenever a request starts, and whenever a user action supersedes
  // one still in flight (the initial "Not now", or picking a city). A
  // resolve that lands with a stale seq is dropped instead of clobbering
  // whatever state the user has since moved to.
  const reqSeq = useRef(0);

  const { colors } = useThemeColors();
  const s = makeStyles(colors);

  function applyPreset(level: ComfortLevel) {
    setComfortLevel(level);
    const preset = COMFORT_PRESETS[level];
    setDisplayMode(preset.displayMode);
    const delta = preset.fontStep - fontStep;
    if (delta !== 0) bumpFontStep(delta);
  }

  function finish() {
    completeOnboarding();
    router.replace('/daven');
  }

  // Leaves the location step: on to comfort for the full setup, or straight
  // into the app for the "Use defaults" path.
  //
  // Committing to the zmanim store happens *here*, not when a location
  // resolves. Resolving (device GPS or a city pick) only stages a guess in
  // local `resolved` state — the user hasn't confirmed it yet, and the
  // "Not the right place? Search instead" escape hatch depends on being able
  // to discard a staged guess with nothing ever having touched the
  // persisted store. Committing on exit is the one place that only runs
  // once the user has actually settled on (or explicitly skipped) a
  // location.
  function leaveLocationStep() {
    if (resolved) setLocation(resolved);
    if (fullSetup) setStep('comfort');
    else finish();
  }

  async function handleAllowLocation() {
    const seq = ++reqSeq.current;
    setLocating(true);
    try {
      const loc = await resolveDeviceLocation();
      if (seq !== reqSeq.current) return; // user moved on — drop this result
      if (loc) {
        setResolved(loc); // stage, don't commit — see leaveLocationStep
      } else {
        // Denied, or the fix failed. Either way the fallback is the same.
        setLocationDenied(true);
      }
    } finally {
      // resolveDeviceLocation never throws, but if the user backgrounds the
      // app mid-prompt this promise just stays pending — the flag clears only
      // once it actually settles.
      if (seq === reqSeq.current) setLocating(false);
    }
  }

  function handlePickCity(loc: ZmanimLocation) {
    reqSeq.current++; // supersede any still-in-flight device-location resolve
    setResolved(loc); // stage, don't commit — see leaveLocationStep
  }

  if (step === 'welcome') {
    return (
      <View style={[s.screen, { backgroundColor: colors.paper }]}>
        <SafeAreaView style={s.safe}>
          <View style={s.center}>
            <Text style={[s.welcomeHe, { color: colors.accent }]}>סִדּוּר פֵּיגֶנְבַּאוּם</Text>
            <Text style={[s.welcomeTitle, { color: colors.ink }]}>The Feigenbaum Weekday Siddur</Text>
            <Text style={[s.welcomeBody, { color: colors.ink }]}>
              A faithful companion for daily tefillah — the complete weekday liturgy with Rabbi Feigenbaum's insights, built for teens finding their footing in davening.
            </Text>
            <Pressable
              style={[s.primaryBtn, { backgroundColor: colors.accent }]}
              onPress={() => { setFullSetup(true); setStep('location'); }}
            >
              <Text style={s.primaryBtnText}>Let's set it up</Text>
            </Pressable>
            <Pressable style={s.ghostBtn} onPress={() => { setFullSetup(false); setStep('location'); }}>
              <Text style={[s.ghostBtnText, { color: colors.muted }]}>Use defaults</Text>
            </Pressable>
          </View>
        </SafeAreaView>
      </View>
    );
  }

  if (step === 'location') {
    return (
      <View style={[s.screen, { backgroundColor: colors.paper }]}>
        <SafeAreaView style={s.safe}>
          <View style={s.content}>
            {resolved ? (
              <>
                <Text style={[s.stepTitle, { color: colors.ink }]}>Zmanim set for {resolved.label}</Text>
                <Text style={[s.reviewNote, { color: colors.muted }]}>
                  You can change this anytime in Settings.
                </Text>
                <Pressable
                  style={[s.primaryBtn, { backgroundColor: colors.accent, marginTop: 8 }]}
                  onPress={leaveLocationStep}
                >
                  <Text style={s.primaryBtnText}>{fullSetup ? 'Next →' : 'Start davening →'}</Text>
                </Pressable>
                <Pressable style={s.ghostBtn} onPress={() => { setResolved(null); setLocationDenied(true); }}>
                  <Text style={[s.ghostBtnText, { color: colors.muted }]}>Not the right place? Search instead</Text>
                </Pressable>
              </>
            ) : locationDenied ? (
              <>
                <Text style={[s.stepTitle, { color: colors.ink }]}>Search for your city instead</Text>
                <Text style={[s.reviewNote, { color: colors.muted }]}>
                  Pick the closest city and we'll use it for your zmanim.
                </Text>
                <CitySearch colors={colors} onSelect={handlePickCity} />
                <Pressable style={s.ghostBtn} onPress={leaveLocationStep}>
                  <Text style={[s.ghostBtnText, { color: colors.muted }]}>Not now</Text>
                </Pressable>
              </>
            ) : (
              <>
                <Text style={[s.stepTitle, { color: colors.ink }]}>Accurate times for where you are</Text>
                <Text style={[s.locationBody, { color: colors.ink }]}>
                  Your location is used only to calculate halachic times — when to say Shema, when Shabbos comes in. It's used while you're in the app, and it never leaves your device except to look those times up.
                </Text>
                <Pressable
                  style={[s.primaryBtn, { backgroundColor: colors.accent }]}
                  onPress={handleAllowLocation}
                  disabled={locating}
                  accessibilityRole="button"
                  accessibilityLabel="Allow location"
                >
                  <Text style={s.primaryBtnText}>{locating ? 'Locating…' : 'Allow location'}</Text>
                </Pressable>
                <Pressable
                  style={s.ghostBtn}
                  onPress={() => {
                    // Supersede any in-flight resolve — a late-arriving
                    // result must not snap the user back after they've
                    // already moved to the search state.
                    reqSeq.current++;
                    setLocationDenied(true);
                  }}
                >
                  <Text style={[s.ghostBtnText, { color: colors.muted }]}>Not now</Text>
                </Pressable>
              </>
            )}
          </View>
        </SafeAreaView>
      </View>
    );
  }

  if (step === 'comfort') {
    return (
      <View style={[s.screen, { backgroundColor: colors.paper }]}>
        <SafeAreaView style={s.safe}>
          <View style={s.content}>
            <Text style={[s.stepTitle, { color: colors.ink }]}>How's your Hebrew davening right now?</Text>
            {COMFORT_OPTIONS.map(opt => (
              <Pressable
                key={opt.value}
                style={[
                  s.comfortOption,
                  { borderColor: colors.line, backgroundColor: colors.surface },
                  comfortLevel === opt.value && { borderColor: colors.accent, backgroundColor: colors.accentSoft },
                ]}
                onPress={() => applyPreset(opt.value)}
                accessibilityRole="radio"
                accessibilityState={{ checked: comfortLevel === opt.value }}
              >
                <Text style={[
                  s.comfortLabel,
                  { color: colors.ink },
                  comfortLevel === opt.value && { color: colors.accent },
                ]}>
                  {opt.label}
                </Text>
                <Text style={[s.comfortDesc, { color: colors.muted }]}>{opt.description}</Text>
              </Pressable>
            ))}
            <Pressable style={[s.primaryBtn, { backgroundColor: colors.accent, marginTop: 24 }]} onPress={() => setStep('review')}>
              <Text style={s.primaryBtnText}>Next →</Text>
            </Pressable>
          </View>
        </SafeAreaView>
      </View>
    );
  }

  // Step 3: review
  const previewHeSize = hebrewFontSize(fontStep);
  const previewEnSize = englishFontSize(fontStep);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <View style={s.content}>
          <Text style={[s.stepTitle, { color: colors.ink }]}>Here are your settings</Text>
          <Text style={[s.reviewNote, { color: colors.muted }]}>You can change any of this anytime in Settings.</Text>

          <Text style={[s.controlLabel, { color: colors.muted }]}>Display</Text>
          <DisplayToggle value={displayMode} colors={colors} onChange={setDisplayMode} />

          <Text style={[s.controlLabel, { color: colors.muted, marginTop: 16 }]}>Theme</Text>
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

          <Text style={[s.controlLabel, { color: colors.muted, marginTop: 16 }]}>Preview</Text>
          <View style={[s.previewCard, { backgroundColor: colors.surface, borderColor: colors.line }]}>
            {displayMode !== 'en' && (
              <Text style={[s.previewHe, { fontSize: previewHeSize, lineHeight: previewHeSize * 1.95, color: colors.ink }]}>
                בָּרוּךְ אַתָּה יְיָ אֱלֹהֵינוּ
              </Text>
            )}
            {displayMode !== 'he' && (
              <Text style={[s.previewEn, { fontSize: previewEnSize, color: colors.ink }]}>
                Blessed are You, Hashem our God
              </Text>
            )}
          </View>

          <Pressable style={[s.primaryBtn, { backgroundColor: colors.accent, marginTop: 24 }]} onPress={finish}>
            <Text style={s.primaryBtnText}>Start davening →</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
    content: { flex: 1, padding: 24 },
    welcomeHe: { fontFamily: Fonts.hebrewBold, fontSize: 28, marginBottom: 8, textAlign: 'center' },
    welcomeTitle: { fontFamily: Fonts.uiSemiBold, fontSize: 18, textAlign: 'center', marginBottom: 16 },
    welcomeBody: { fontFamily: Fonts.english, fontSize: 16, lineHeight: 25, textAlign: 'center', marginBottom: 36 },
    primaryBtn: { borderRadius: 14, paddingVertical: 15, paddingHorizontal: 32, alignItems: 'center', width: '100%' },
    primaryBtnText: { fontFamily: Fonts.uiSemiBold, fontSize: 16, color: '#FFFFFF' },
    ghostBtn: { marginTop: 12, padding: 12, alignItems: 'center' },
    ghostBtnText: { fontFamily: Fonts.ui, fontSize: 14 },
    stepTitle: { fontFamily: Fonts.uiSemiBold, fontSize: 22, marginBottom: 8 },
    reviewNote: { fontFamily: Fonts.ui, fontSize: 13, marginBottom: 20 },
    locationBody: { fontFamily: Fonts.english, fontSize: 15, lineHeight: 24, marginBottom: 28 },
    comfortOption: { borderRadius: 12, padding: 16, marginBottom: 10, borderWidth: 1.5 },
    comfortLabel: { fontFamily: Fonts.uiSemiBold, fontSize: 16, marginBottom: 4 },
    comfortDesc: { fontFamily: Fonts.ui, fontSize: 13 },
    controlLabel: { fontFamily: Fonts.uiSemiBold, fontSize: 11, letterSpacing: 1.5, textTransform: 'uppercase' as const, marginBottom: 8 },
    themeRow: { flexDirection: 'row', gap: 8 },
    themeBtn: { flex: 1, paddingVertical: 10, borderRadius: 10, alignItems: 'center' },
    themeBtnText: { fontFamily: Fonts.uiMedium, fontSize: 13 },
    previewCard: { borderRadius: 12, padding: 16, borderWidth: 1 },
    previewHe: { fontFamily: Fonts.hebrew, textAlign: 'right', writingDirection: 'rtl' as const },
    previewEn: { fontFamily: Fonts.english, marginTop: 8, lineHeight: 24 },
  });
}
