import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router, useLocalSearchParams } from 'expo-router';
import { getBookPiece } from '../../src/content/bookMatter';
import { ProseSegments } from '../../src/components/ProseSegments';
import { usePreferencesStore } from '../../src/store/preferences';
import { ColorPalette } from '../../src/theme/colors';
import { useThemeColors } from '../../src/theme/useThemeColors';
import { Fonts, hebrewFontSize, englishFontSize } from '../../src/theme/typography';

export default function BookPieceScreen() {
  const { piece: pieceId } = useLocalSearchParams<{ piece: string }>();
  const { colors } = useThemeColors();
  const fontStep = usePreferencesStore((s) => s.fontStep);
  const piece = pieceId ? getBookPiece(pieceId) : null;
  const s = makeStyles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <ScrollView contentContainerStyle={s.body} showsVerticalScrollIndicator={false}>
          <Pressable style={s.backBtn}
            onPress={() => (router.canGoBack() ? router.back() : router.replace('/about' as any))}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Text style={[s.backText, { color: colors.accent }]}>← Back</Text>
          </Pressable>
          {!piece ? (
            <Text style={[s.missing, { color: colors.muted }]}>This piece isn't available.</Text>
          ) : (
            <>
              <Text style={[s.title, { color: colors.ink }]}>{piece.title}</Text>
              {!!piece.subtitle && (
                <Text style={[s.subtitle, { color: colors.muted }]}>{piece.subtitle}</Text>
              )}
              <ProseSegments
                segments={piece.segments}
                heSize={hebrewFontSize(fontStep)}
                enSize={englishFontSize(fontStep)}
                colors={colors}
              />
            </>
          )}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    body: { paddingHorizontal: 22, paddingTop: 16, paddingBottom: 80 },
    // A real 44pt target (hitSlop alone fails: the title below captures taps).
    backBtn: { alignSelf: 'flex-start', minHeight: 44, justifyContent: 'center' },
    backText: { fontFamily: Fonts.uiMedium, fontSize: 15, marginBottom: 12 },
    title: { fontFamily: Fonts.englishBold, fontSize: 23, lineHeight: 30, marginBottom: 4 },
    subtitle: { fontFamily: Fonts.englishItalic, fontSize: 14.5, marginBottom: 14 },
    missing: { fontFamily: Fonts.ui, fontSize: 14, textAlign: 'center', marginTop: 60 },
  });
}
