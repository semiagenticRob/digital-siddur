import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { ColorPalette } from '../../src/theme/colors';
import { useThemeColors } from '../../src/theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../../src/theme/typography';

// Reader-first ordering (not print order): the teen intro and translation
// note are the two pieces a davener actually needs; provenance last.
// The six ids below must match listBookPieces() in ../../src/content/bookMatter —
// see src/content/__tests__/bookMatter.test.ts, which guards that seam.
const TOC: Array<{ label: string; rows: Array<{ id: string; title: string; desc: string }> }> = [
  {
    label: 'Read First',
    rows: [
      { id: 'intro-teens', title: '"But I Don\'t Do Davening!"', desc: 'Introduction for Teens — why davening is hard, and how this siddur helps' },
      { id: 'translation-note', title: 'How to Read the Translation', desc: 'What the italics mean, and why key words are translated the way they are' },
    ],
  },
  {
    label: 'For Parents & Teachers',
    rows: [
      { id: 'intro-parents', title: 'Introduction for Parents, Mechanchim, and Mechanchos', desc: 'The approach behind the translation and commentary' },
      { id: 'personal-notes', title: 'A Personal Note from Rabbi Feigenbaum', desc: 'For parents and mechanchim · For teens' },
    ],
  },
  {
    label: 'The People Behind It',
    rows: [
      { id: 'dedications', title: 'Dedications', desc: 'The Cohen Family Edition — in loving memory' },
      { id: 'acknowledgments', title: 'Acknowledgments', desc: 'Rabbi Feigenbaum\'s thanks — starting with why we thank Hashem at all' },
    ],
  },
];

export default function AboutScreen() {
  const { colors } = useThemeColors();
  const s = makeStyles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <ScrollView contentContainerStyle={s.body}>
          <Pressable
            onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Text style={[s.backText, { color: colors.accent }]}>← Back</Text>
          </Pressable>
          <Text style={[s.title, { color: colors.ink }]}>About this Siddur</Text>
          <Text style={[s.sub, { color: colors.muted }]}>
            The Feigenbaum Siddur · The Cohen Family Edition · Nusach Ashkenaz{'\n'}
            By Rabbi Yitzchak Feigenbaum · Mosaica Press
          </Text>

          {TOC.map((group) => (
            <View key={group.label}>
              <Text style={[s.sectionLabel, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                {group.label}
              </Text>
              {group.rows.map((row) => (
                <Pressable
                  key={row.id}
                  style={({ pressed }) => [
                    s.row,
                    { backgroundColor: colors.surface, borderColor: colors.line },
                    pressed && { opacity: 0.7 },
                  ]}
                  onPress={() => router.push(('/about/' + row.id) as any)}
                  accessibilityRole="button"
                  accessibilityLabel={`Open ${row.title}`}
                >
                  <Text style={[s.rowTitle, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                    {row.title}
                  </Text>
                  <Text style={[s.rowDesc, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                    {row.desc}
                  </Text>
                </Pressable>
              ))}
            </View>
          ))}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    body: { paddingHorizontal: 16, paddingTop: 16, paddingBottom: 40 },
    backText: { fontFamily: Fonts.uiMedium, fontSize: 15, marginBottom: 8, paddingHorizontal: 4 },
    title: { fontFamily: Fonts.uiSemiBold, fontSize: 26, paddingHorizontal: 4 },
    sub: { fontFamily: Fonts.ui, fontSize: 13, lineHeight: 19, marginTop: 4, paddingHorizontal: 4 },
    sectionLabel: {
      fontFamily: Fonts.uiSemiBold, fontSize: 11, letterSpacing: 1.5,
      textTransform: 'uppercase' as const, marginTop: 20, marginBottom: 8, paddingHorizontal: 4,
    },
    row: { borderRadius: 14, borderWidth: 1, padding: 14, marginBottom: 8 },
    rowTitle: { fontFamily: Fonts.uiSemiBold, fontSize: 15.5 },
    rowDesc: { fontFamily: Fonts.ui, fontSize: 12, lineHeight: 17, marginTop: 3 },
  });
}
