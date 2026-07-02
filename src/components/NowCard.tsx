import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { router } from 'expo-router';
import { getService } from '../content/loader';
import { useReadingPositionStore } from '../store/readingPosition';
import { ColorPalette } from '../theme/colors';
import { useThemeColors } from '../theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../theme/typography';
import { formatEnDate, fromGregorian, formatHebrewDate } from '../lib/hebrewDate';

// The home screen's "now" zone. This round it carries the date line and a
// resume link; the suggested-service CTA and zmanim strip from the design
// spec land in the zmanim round and mount inside this same card.
export function NowCard() {
  const { colors } = useThemeColors();
  const lastServiceId = useReadingPositionStore((s) => s.lastServiceId);
  const last = lastServiceId ? getService(lastServiceId) : null;
  const now = new Date();
  const s = makeStyles(colors);

  return (
    <View style={[s.card, { backgroundColor: colors.surface, borderColor: colors.line, borderTopColor: colors.gold }]}>
      <View style={s.dateRow}>
        <Text style={[s.enDate, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
          {formatEnDate(now)}
        </Text>
        <Text style={[s.heDate, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE} accessibilityLanguage="he">
          {formatHebrewDate(fromGregorian(now))}
        </Text>
      </View>
      {last && (
        <Pressable
          onPress={() => router.push('/daven/' + last.id as any)}
          accessibilityRole="button"
          accessibilityLabel={`Resume ${last.enTitle}`}
          style={s.resumeBtn}
        >
          <Text style={[s.resumeText, { color: colors.accent }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
            Resume {last.enTitle} →
          </Text>
        </Pressable>
      )}
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    card: {
      marginHorizontal: 16,
      marginBottom: 4,
      borderRadius: 16,
      borderWidth: 1,
      borderTopWidth: 3,
      paddingVertical: 14,
      paddingHorizontal: 18,
    },
    dateRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    enDate: { fontFamily: Fonts.uiSemiBold, fontSize: 13, letterSpacing: 0.3 },
    heDate: { fontFamily: Fonts.hebrewBold, fontSize: 17, writingDirection: 'rtl' as const },
    resumeBtn: { marginTop: 10 },
    resumeText: { fontFamily: Fonts.uiSemiBold, fontSize: 14.5 },
  });
}
