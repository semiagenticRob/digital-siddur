import React from 'react';
import { View, Text, Pressable, StyleSheet, SectionList } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useAnnotationsStore } from '../src/store/annotations';
import { locateSegment } from '../src/content/segmentIndex';
import { ColorPalette } from '../src/theme/colors';
import { useThemeColors } from '../src/theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../src/theme/typography';

interface Row {
  key: string;
  segmentId: string;
  noteIndex?: number;   // present for note rows
  noteText?: string;
}

function snippet(he: string, words = 7): string {
  const parts = he.split(/\s+/).filter(Boolean);
  return parts.length <= words ? he : parts.slice(0, words).join(' ') + '…';
}

export default function NotesScreen() {
  const { colors } = useThemeColors();
  const highlights = useAnnotationsStore((s) => s.highlights);
  const notes = useAnnotationsStore((s) => s.notes);
  const toggleHighlight = useAnnotationsStore((s) => s.toggleHighlight);
  const removeNote = useAnnotationsStore((s) => s.removeNote);
  const s = makeStyles(colors);

  const noteRows: Row[] = Object.entries(notes).flatMap(([segmentId, texts]) =>
    texts.map((noteText, noteIndex) => ({
      key: `n-${segmentId}-${noteIndex}`,
      segmentId,
      noteIndex,
      noteText,
    }))
  );
  const highlightRows: Row[] = Array.from(highlights).map((segmentId) => ({
    key: `h-${segmentId}`,
    segmentId,
  }));

  const sections = [
    ...(noteRows.length ? [{ title: 'Notes', data: noteRows }] : []),
    ...(highlightRows.length ? [{ title: 'Highlights', data: highlightRows }] : []),
  ];

  const openRow = (row: Row) => {
    const loc = locateSegment(row.segmentId);
    if (loc) {
      router.push({ pathname: '/daven/[service]', params: { service: loc.serviceId, initialPrayer: loc.prayerId } });
    }
  };

  const deleteRow = (row: Row) => {
    if (row.noteIndex != null) removeNote(row.segmentId, row.noteIndex);
    else toggleHighlight(row.segmentId);
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
          <Text style={[s.title, { color: colors.ink }]}>Notes & Highlights</Text>
        </View>

        {sections.length === 0 ? (
          <View style={s.empty}>
            <Ionicons name="bookmark-outline" size={34} color={colors.muted} />
            <Text style={[s.emptyText, { color: colors.muted }]}>
              Nothing saved yet. While davening, tap any Hebrew line to highlight it or add a note.
            </Text>
          </View>
        ) : (
          <SectionList
            sections={sections}
            keyExtractor={(item) => item.key}
            contentContainerStyle={s.list}
            stickySectionHeadersEnabled={false}
            renderSectionHeader={({ section }) => (
              <Text style={[s.sectionLabel, { color: colors.muted }]}>{section.title}</Text>
            )}
            renderItem={({ item }) => {
              const loc = locateSegment(item.segmentId);
              return (
                <View style={[s.row, { backgroundColor: colors.surface, borderColor: colors.line }]}>
                  <Pressable
                    style={s.rowBody}
                    onPress={() => openRow(item)}
                    disabled={!loc}
                    accessibilityRole="button"
                    accessibilityLabel={loc ? `Open ${loc.prayerEnTitle}` : 'Passage unavailable'}
                  >
                    {loc ? (
                      <>
                        {!!loc.heText && (
                          <Text
                            style={[s.rowHe, { color: colors.ink }]}
                            numberOfLines={2}
                            maxFontSizeMultiplier={MAX_FONT_SCALE}
                            accessibilityLanguage="he"
                          >
                            {snippet(loc.heText)}
                          </Text>
                        )}
                        {item.noteText != null && (
                          <Text style={[s.rowNote, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                            ✎ {item.noteText}
                          </Text>
                        )}
                        <Text style={[s.rowWhere, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                          {loc.prayerEnTitle} · {loc.serviceTitle}
                        </Text>
                      </>
                    ) : (
                      <Text style={[s.rowWhere, { color: colors.muted }]}>
                        This passage is no longer in the siddur content.
                      </Text>
                    )}
                  </Pressable>
                  <Pressable
                    style={s.deleteBtn}
                    onPress={() => deleteRow(item)}
                    accessibilityRole="button"
                    accessibilityLabel={item.noteIndex != null ? 'Delete note' : 'Remove highlight'}
                  >
                    <Ionicons name="trash-outline" size={18} color={colors.muted} />
                  </Pressable>
                </View>
              );
            }}
          />
        )}
      </SafeAreaView>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    header: { paddingTop: 16, paddingBottom: 12, paddingHorizontal: 20 },
    backText: { fontFamily: Fonts.uiMedium, fontSize: 15, marginBottom: 8 },
    title: { fontFamily: Fonts.uiSemiBold, fontSize: 26 },
    list: { paddingHorizontal: 16, paddingBottom: 40 },
    sectionLabel: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 11,
      letterSpacing: 1.5,
      textTransform: 'uppercase' as const,
      marginTop: 18,
      marginBottom: 8,
      paddingHorizontal: 4,
    },
    row: {
      flexDirection: 'row',
      alignItems: 'center',
      borderRadius: 14,
      borderWidth: 1,
      marginBottom: 8,
    },
    rowBody: { flex: 1, paddingVertical: 12, paddingHorizontal: 14, gap: 4 },
    rowHe: {
      fontFamily: Fonts.hebrew,
      fontSize: 17,
      textAlign: 'right',
      writingDirection: 'rtl' as const,
    },
    rowNote: { fontFamily: Fonts.ui, fontSize: 13.5 },
    rowWhere: { fontFamily: Fonts.uiMedium, fontSize: 11.5, letterSpacing: 0.3 },
    deleteBtn: { padding: 14, alignSelf: 'stretch', justifyContent: 'center' },
    empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 40, gap: 12 },
    emptyText: { fontFamily: Fonts.ui, fontSize: 14, textAlign: 'center', lineHeight: 21 },
  });
}
