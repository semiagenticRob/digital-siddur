import React, { useRef, useState } from 'react';
import { View, Text, Pressable, StyleSheet, useColorScheme, SafeAreaView } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { getService } from '../../src/content/loader';
import { ServiceScroll, ServiceScrollHandle } from '../../src/components/ServiceScroll';
import { JumpToC } from '../../src/components/JumpToC';
import { DisplayToggle } from '../../src/components/DisplayToggle';
import { FontSizeControl } from '../../src/components/FontSizeControl';
import { usePreferencesStore } from '../../src/store/preferences';
import { useAnnotationsStore } from '../../src/store/annotations';
import { LightColors, DarkColors, ColorPalette } from '../../src/theme/colors';
import { Fonts } from '../../src/theme/typography';

export default function ServiceScreen() {
  const { service: serviceId } = useLocalSearchParams<{ service: string }>();
  const [tocVisible, setTocVisible] = useState(false);
  const scrollRef = useRef<ServiceScrollHandle>(null);

  const { displayMode, theme, fontStep, setDisplayMode, bumpFontStep } = usePreferencesStore();
  const { isHighlighted, getNotes, toggleHighlight, addNote } = useAnnotationsStore();

  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors: ColorPalette = (isDark ? DarkColors : LightColors) as ColorPalette;

  const service = getService(serviceId ?? '');

  const s = makeStyles(colors);

  if (!service) {
    return (
      <SafeAreaView style={[s.screen, { alignItems: 'center', justifyContent: 'center' }]}>
        <Text style={{ fontFamily: Fonts.ui, color: colors.muted }}>Service not found.</Text>
      </SafeAreaView>
    );
  }

  return (
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
              onPress={() => router.back()}
              accessibilityRole="button"
              accessibilityLabel="Go back"
            >
              <Text style={[s.iconBtnText, { color: colors.ink }]}>←</Text>
            </Pressable>
          </View>
          <View style={s.controlRow}>
            <DisplayToggle value={displayMode} colors={colors} onChange={setDisplayMode} />
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
