import React from 'react';
import { View, Text, Pressable, StyleSheet, SectionList, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { homeSections, HomeSection } from '../../src/content/categories';
import { NowCard } from '../../src/components/NowCard';
import { ColorPalette } from '../../src/theme/colors';
import { useThemeColors } from '../../src/theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../../src/theme/typography';

export default function DavenHome() {
  const { colors } = useThemeColors();
  const sections: HomeSection[] = homeSections();
  const s = makeStyles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <SectionList
          sections={sections}
          keyExtractor={(item) => item.id}
          contentContainerStyle={s.list}
          stickySectionHeadersEnabled={false}
          ListHeaderComponent={
            <>
              <View style={s.headerRow}>
                <Text style={[s.title, { color: colors.ink }]}>Daven</Text>
                <View style={s.headerActions}>
                  <Pressable
                    onPress={() => router.push('/notes')}
                    accessibilityRole="button"
                    accessibilityLabel="Open notes and highlights"
                    style={s.iconBtn}
                  >
                    <Ionicons name="bookmark-outline" size={22} color={colors.muted} />
                  </Pressable>
                  <Pressable
                    onPress={() => router.push('/settings')}
                    accessibilityRole="button"
                    accessibilityLabel="Open settings"
                    style={s.iconBtn}
                  >
                    <Ionicons name="settings-outline" size={22} color={colors.muted} />
                  </Pressable>
                </View>
              </View>
              <NowCard />
            </>
          }
          renderSectionHeader={({ section }) => (
            <Text style={[s.sectionLabel, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
              {section.title}
            </Text>
          )}
          renderItem={({ item, section }) => (
            <Pressable
              style={({ pressed }) => [
                s.row,
                (section as HomeSection).compact && s.rowCompact,
                { backgroundColor: colors.surface, borderColor: colors.line },
                pressed && s.rowPressed,
              ]}
              onPress={() => router.push(('/daven/' + item.id) as any)}
              accessibilityRole="button"
              accessibilityLabel={`Open ${item.enTitle}`}
            >
              <Text
                style={[s.rowEn, (section as HomeSection).compact && s.rowEnCompact, { color: colors.ink }]}
                maxFontSizeMultiplier={MAX_FONT_SCALE}
              >
                {item.enTitle}
              </Text>
              <Text
                style={[s.rowHe, (section as HomeSection).compact && s.rowHeCompact, { color: colors.muted }]}
                maxFontSizeMultiplier={MAX_FONT_SCALE}
                accessibilityLanguage="he"
              >
                {item.heTitle}
              </Text>
            </Pressable>
          )}
          ListFooterComponent={
            <>
              <Text style={[s.sectionLabel, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                From the Book
              </Text>
              <View style={s.bookRow}>
                <Pressable
                  style={[s.bookCard, { backgroundColor: colors.surface, borderColor: colors.line }]}
                  onPress={() => router.push('/about' as any)}
                  accessibilityRole="button"
                  accessibilityLabel="About this Siddur"
                >
                  <Text style={[s.bookTitle, { color: colors.ink }]}>About this Siddur</Text>
                  <Text style={[s.bookDesc, { color: colors.muted }]}>
                    Rabbi Feigenbaum's introductions, dedications & notes
                  </Text>
                </Pressable>
                <Pressable
                  style={[s.bookCard, { backgroundColor: colors.surface, borderColor: colors.line }]}
                  onPress={() => router.push('/glossary' as any)}
                  accessibilityRole="button"
                  accessibilityLabel="Glossary"
                >
                  <Text style={[s.bookTitle, { color: colors.ink }]}>Glossary</Text>
                  <Text style={[s.bookDesc, { color: colors.muted }]}>
                    Hebrew terms used throughout the translations
                  </Text>
                </Pressable>
              </View>
            </>
          }
        />
      </SafeAreaView>
    </View>
  );
}

function makeStyles(colors: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    headerRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: 8,
      paddingTop: 24,
      paddingBottom: 12,
    },
    title: { fontFamily: Fonts.uiSemiBold, fontSize: 28 },
    iconBtn: { padding: 8 },
    headerActions: { flexDirection: 'row', alignItems: 'center' },
    list: { paddingHorizontal: 16, paddingBottom: 40 },
    sectionLabel: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 11,
      letterSpacing: 1.6,
      textTransform: 'uppercase' as const,
      marginTop: 20,
      marginBottom: 8,
      paddingHorizontal: 4,
    },
    row: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderRadius: 14,
      paddingVertical: 16,
      paddingHorizontal: 18,
      borderWidth: 1,
      marginBottom: 8,
    },
    rowCompact: { paddingVertical: 11 },
    rowPressed: { opacity: 0.7 },
    rowEn: { fontFamily: Fonts.uiMedium, fontSize: 17 },
    rowEnCompact: { fontSize: 15 },
    rowHe: { fontFamily: Fonts.hebrewBold, fontSize: 20, writingDirection: 'rtl' as const },
    rowHeCompact: { fontSize: 18 },
    bookRow: { flexDirection: 'row', gap: 8 },
    bookCard: { flex: 1, borderRadius: 14, borderWidth: 1, padding: 14 },
    bookTitle: { fontFamily: Fonts.uiSemiBold, fontSize: 14.5 },
    bookDesc: { fontFamily: Fonts.ui, fontSize: 11.5, marginTop: 3, lineHeight: 15 },
  });
}
