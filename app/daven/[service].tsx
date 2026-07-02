import React, { useRef, useState, useEffect, useMemo } from 'react';
import { View, Text, Pressable, StyleSheet, SafeAreaView } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { activateKeepAwakeAsync, deactivateKeepAwake } from 'expo-keep-awake';
import { getService } from '../../src/content/loader';
import { ServiceScroll, ServiceScrollHandle } from '../../src/components/ServiceScroll';
import { ReaderContext, ReaderContextValue } from '../../src/components/ReaderContext';
import { JumpToC } from '../../src/components/JumpToC';
import { DisplayToggle } from '../../src/components/DisplayToggle';
import { FontSizeControl } from '../../src/components/FontSizeControl';
import { usePreferencesStore } from '../../src/store/preferences';
import { useAnnotationsStore } from '../../src/store/annotations';
import { useReadingPositionStore } from '../../src/store/readingPosition';
import { ColorPalette } from '../../src/theme/colors';
import { useThemeColors } from '../../src/theme/useThemeColors';
import { Fonts } from '../../src/theme/typography';

export default function ServiceScreen() {
  const { service: serviceId, initialPrayer } = useLocalSearchParams<{ service: string; initialPrayer?: string }>();
  const [tocVisible, setTocVisible] = useState(false);
  const scrollRef = useRef<ServiceScrollHandle>(null);
  const scrolledFor = useRef<string | null>(null);

  const listReady = useRef(false);
  const setOffset = useReadingPositionStore((s) => s.setOffset);
  const savedOffset = useReadingPositionStore((s) => (serviceId ? s.offsets[serviceId] : undefined));

  // Runs once the list has completed its first layout (ServiceScroll onReady) —
  // the earliest point scrollTo* calls are reliable. A deep-linked prayer wins
  // over the saved reading position.
  const handleListReady = () => {
    listReady.current = true;
    if (initialPrayer && scrolledFor.current !== initialPrayer) {
      scrollRef.current?.scrollToPrayer(initialPrayer);
      scrolledFor.current = initialPrayer;
    } else if (savedOffset && savedOffset > 0) {
      scrollRef.current?.scrollToOffset(savedOffset, false);
    }
  };

  // A deep link can also arrive while the screen is already mounted (same-screen
  // param change after the list is long since ready). Before first layout this
  // is a no-op — handleListReady takes care of the initial scroll.
  useEffect(() => {
    if (!listReady.current || !initialPrayer || scrolledFor.current === initialPrayer) return;
    scrollRef.current?.scrollToPrayer(initialPrayer);
    scrolledFor.current = initialPrayer;
  }, [initialPrayer]);

  const { displayMode, fontStep, keepAwake, setDisplayMode, bumpFontStep } = usePreferencesStore();
  const { isHighlighted, getNotes, toggleHighlight, addNote } = useAnnotationsStore();

  // Davening happens hands-free — keep the screen on while a service is open
  // (user-toggleable in Settings).
  useEffect(() => {
    if (!keepAwake) return;
    const tag = 'siddur-reader';
    activateKeepAwakeAsync(tag);
    return () => {
      deactivateKeepAwake(tag);
    };
  }, [keepAwake]);

  const { colors } = useThemeColors();

  const service = getService(serviceId ?? '');

  const s = useMemo(() => makeStyles(colors), [colors]);

  const readerCtx: ReaderContextValue = useMemo(
    () => ({
      serviceId: serviceId ?? '',
      scrollToPrayer: (id: string) => scrollRef.current?.scrollToPrayer(id),
    }),
    [serviceId]
  );

  if (!service) {
    return (
      <SafeAreaView style={[s.screen, { alignItems: 'center', justifyContent: 'center' }]}>
        <Text style={{ fontFamily: Fonts.ui, color: colors.muted }}>Service not found.</Text>
      </SafeAreaView>
    );
  }

  return (
    <ReaderContext.Provider value={readerCtx}>
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safeArea}>
        {/* Header */}
        <View style={[s.header, { backgroundColor: colors.surface, borderBottomColor: colors.line }]}>
          <View style={s.headerBar}>
            <Pressable
              style={s.iconBtn}
              onPress={() => setTocVisible(true)}
              accessibilityRole="button"
              accessibilityLabel="Open table of contents"
            >
              <Text style={[s.iconBtnText, { color: colors.ink }]}>☰</Text>
            </Pressable>
            <View style={s.titleBlock}>
              <Text style={[s.titleHe, { color: colors.ink }]}>{service.heTitle}</Text>
              <Text style={[s.titleEn, { color: colors.muted }]}>{service.enTitle}</Text>
            </View>
            <Pressable
              style={s.iconBtn}
              onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
              accessibilityRole="button"
              accessibilityLabel="Go back"
            >
              <Text style={[s.iconBtnText, { color: colors.ink }]}>←</Text>
            </Pressable>
          </View>
          <View style={s.controlRow}>
            <DisplayToggle value={displayMode} colors={colors} onChange={setDisplayMode} style={{ flex: 1 }} />
            <FontSizeControl colors={colors} onBump={bumpFontStep} />
          </View>
        </View>

        {/* Reading area */}
        <ServiceScroll
          ref={scrollRef}
          service={service}
          displayMode={displayMode}
          fontStep={fontStep}
          colors={colors}
          isHighlighted={isHighlighted}
          getNotes={getNotes}
          onToggleHighlight={toggleHighlight}
          onAddNote={addNote}
          onReady={handleListReady}
          onScrollSettled={(offset) => { if (serviceId) setOffset(serviceId, offset); }}
        />

        {/* Jump-ToC */}
        <JumpToC
          visible={tocVisible}
          service={service}
          colors={colors}
          onSelectPrayer={(id) => scrollRef.current?.scrollToPrayer(id)}
          onClose={() => setTocVisible(false)}
        />
      </SafeAreaView>
    </View>
    </ReaderContext.Provider>
  );
}

function makeStyles(colors: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safeArea: { flex: 1 },
    header: {
      paddingHorizontal: 14,
      paddingTop: 10,
      paddingBottom: 10,
      borderBottomWidth: 1,
    },
    headerBar: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 10,
      marginBottom: 10,
    },
    iconBtn: {
      width: 38,
      height: 38,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 11,
    },
    iconBtnText: { fontSize: 20 },
    titleBlock: { flex: 1, alignItems: 'center' },
    titleHe: {
      fontFamily: Fonts.hebrewBold,
      fontSize: 19,
    },
    titleEn: {
      fontFamily: Fonts.ui,
      fontSize: 11,
      letterSpacing: 1.4,
      textTransform: 'uppercase' as const,
    },
    controlRow: {
      flexDirection: 'row',
      gap: 8,
      alignItems: 'center',
    },
  });
}
