import React, { useRef } from 'react';
import { View, Text, Pressable, StyleSheet, SectionList, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { glossarySections, GlossaryEntry } from '../src/content/glossary';
import { ColorPalette } from '../src/theme/colors';
import { useThemeColors } from '../src/theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../src/theme/typography';

export default function GlossaryScreen() {
  const { colors } = useThemeColors();
  const sections = glossarySections();
  const listRef = useRef<SectionList<GlossaryEntry>>(null);
  const s = makeStyles(colors);

  const jumpTo = (index: number) =>
    listRef.current?.scrollToLocation({ sectionIndex: index, itemIndex: 0, viewOffset: 8 });

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <View style={s.header}>
          <Pressable style={s.backBtn}
            onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Text style={[s.backText, { color: colors.accent }]}>← Back</Text>
          </Pressable>
          <Text style={[s.title, { color: colors.ink }]}>Glossary</Text>
          <Text style={[s.sub, { color: colors.muted }]}>
            Hebrew terms used throughout the translations
          </Text>
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.alphaBar} contentContainerStyle={s.alphaContent}>
          {sections.map((section, i) => (
            <Pressable
              key={section.letter}
              onPress={() => jumpTo(i)}
              hitSlop={{ top: 2, bottom: 2 }}
              accessibilityRole="button"
              accessibilityLabel={`Jump to ${section.letter}`}
              style={[s.alphaBtn, { backgroundColor: colors.surface, borderColor: colors.line }]}
            >
              <Text style={[s.alphaText, { color: colors.accent }]}>{section.letter}</Text>
            </Pressable>
          ))}
        </ScrollView>

        <SectionList
          ref={listRef}
          sections={sections}
          keyExtractor={(item) => item.term}
          contentContainerStyle={s.list}
          stickySectionHeadersEnabled={false}
          onScrollToIndexFailed={() => {}}
          renderSectionHeader={({ section }) => (
            <Text style={[s.sectionLabel, { color: colors.muted }]}>{section.letter}</Text>
          )}
          renderItem={({ item }) => (
            <View style={[s.entry, { backgroundColor: colors.surface, borderColor: colors.line }]}>
              <Text style={[s.term, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                {item.term}
              </Text>
              <Text style={[s.def, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE} selectable>
                {item.definition}
              </Text>
            </View>
          )}
        />
      </SafeAreaView>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    header: { paddingTop: 16, paddingHorizontal: 20, paddingBottom: 6 },
    // A real 44pt target (hitSlop alone fails: the title below captures taps).
    backBtn: { alignSelf: 'flex-start', minHeight: 44, justifyContent: 'center' },
    backText: { fontFamily: Fonts.uiMedium, fontSize: 15, marginBottom: 8 },
    title: { fontFamily: Fonts.uiSemiBold, fontSize: 26 },
    sub: { fontFamily: Fonts.ui, fontSize: 13, marginTop: 2 },
    alphaBar: { flexGrow: 0, flexShrink: 0, marginTop: 8 },
    alphaContent: { paddingHorizontal: 16, paddingVertical: 4, gap: 6, alignItems: 'center' },
    alphaBtn: { minWidth: 40, minHeight: 40, alignItems: 'center', justifyContent: 'center', borderRadius: 8, borderWidth: 1, paddingHorizontal: 6 },
    alphaText: { fontFamily: Fonts.uiSemiBold, fontSize: 13 },
    list: { paddingHorizontal: 16, paddingBottom: 40 },
    sectionLabel: {
      fontFamily: Fonts.uiSemiBold, fontSize: 11, letterSpacing: 1.5,
      textTransform: 'uppercase' as const, marginTop: 16, marginBottom: 8, paddingHorizontal: 4,
    },
    entry: { borderRadius: 14, borderWidth: 1, padding: 13, marginBottom: 8 },
    term: { fontFamily: Fonts.uiSemiBold, fontSize: 15.5 },
    def: { fontFamily: Fonts.english, fontSize: 14.5, lineHeight: 21, marginTop: 3 },
  });
}
