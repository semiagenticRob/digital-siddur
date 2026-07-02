import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, Pressable, StyleSheet, AppState } from 'react-native';
import { router, useFocusEffect } from 'expo-router';
import { getService } from '../content/loader';
import { useReadingPositionStore } from '../store/readingPosition';
import { useZmanimStore, dateKey, DayZmanim } from '../store/zmanim';
import { suggestService } from '../lib/suggestService';
import { formatZmanTime } from '../lib/formatZmanTime';
import { ColorPalette } from '../theme/colors';
import { useThemeColors } from '../theme/useThemeColors';
import { Fonts, MAX_FONT_SCALE } from '../theme/typography';
import { formatEnDate, fromGregorian, formatHebrewDate } from '../lib/hebrewDate';

const ZMAN_CELLS: Array<{ key: keyof DayZmanim; label: string }> = [
  { key: 'sofZmanShma', label: 'KRIAS SHEMA' },
  { key: 'minchaGedola', label: 'MIN. GEDOLAH' },
  { key: 'sunset', label: 'SHKIAH' },
  { key: 'tzeit85deg', label: 'TZEIS' },
];

// The home screen's "now" zone: date line, suggested-service CTA, resume
// link, and (when a location is set) the zmanim strip for today.
export function NowCard() {
  const { colors } = useThemeColors();
  const lastServiceId = useReadingPositionStore((s) => s.lastServiceId);
  const last = lastServiceId ? getService(lastServiceId) : null;
  const location = useZmanimStore((st) => st.location);
  const zmanimFor = useZmanimStore((st) => st.zmanimFor);
  const [now, setNow] = useState(() => new Date());
  const s = makeStyles(colors);

  // The home screen stays mounted across midnight (iOS keeps apps alive for
  // days), so `now` must be refreshed rather than computed once at render:
  // on screen focus, and when the app returns to the foreground.
  useFocusEffect(
    useCallback(() => {
      setNow(new Date());
    }, [])
  );

  useEffect(() => {
    const subscription = AppState.addEventListener('change', (state) => {
      if (state === 'active') {
        setNow(new Date());
      }
    });
    return () => subscription.remove();
  }, []);

  // Keep the zmanim cache topped up; fire-and-forget, never blocks render.
  useEffect(() => {
    void useZmanimStore.getState().ensureFresh(dateKey(new Date()));
  }, [now]);

  const todayZmanim = zmanimFor(dateKey(now));
  const suggested = getService(suggestService(now, todayZmanim));

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

      {suggested && (
        <View style={s.suggestedRow}>
          <Text style={[s.suggestedEn, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
            {suggested.enTitle}
          </Text>
          <Text
            style={[s.suggestedHe, { color: colors.ink }]}
            maxFontSizeMultiplier={MAX_FONT_SCALE}
            accessibilityLanguage="he"
          >
            {suggested.heTitle}
          </Text>
        </View>
      )}

      <View style={s.actionRow}>
        {suggested && (
          <Pressable
            onPress={() => router.push(('/daven/' + suggested.id) as any)}
            accessibilityRole="button"
            accessibilityLabel={`Daven ${suggested.enTitle} now`}
            style={[s.davenBtn, { backgroundColor: colors.accent }]}
          >
            <Text style={s.davenBtnText} maxFontSizeMultiplier={MAX_FONT_SCALE}>
              Daven now →
            </Text>
          </Pressable>
        )}
        {last && last.id !== suggested?.id && (
          <Pressable
            onPress={() => router.push(('/daven/' + last.id) as any)}
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

      {location === null && (
        <Pressable
          onPress={() => router.push('/settings' as any)}
          accessibilityRole="button"
          accessibilityLabel="Set location for zmanim"
          style={s.setLocationRow}
        >
          <Text style={[s.setLocationText, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
            Set location for zmanim →
          </Text>
        </Pressable>
      )}

      {todayZmanim && (
        <View
          style={[s.zmanimStrip, { backgroundColor: colors.accentSoft, borderTopColor: colors.line }]}
          accessibilityLabel={`Zmanim: Krias Shema ${formatZmanTime(todayZmanim.sofZmanShma)}, Mincha Gedolah ${formatZmanTime(todayZmanim.minchaGedola)}, Shkiah ${formatZmanTime(todayZmanim.sunset)}, Tzeis ${formatZmanTime(todayZmanim.tzeit85deg)}`}
        >
          {ZMAN_CELLS.map((cell, i) => (
            <View key={cell.key} style={[s.zmanCell, i > 0 && { borderLeftColor: colors.line, borderLeftWidth: 1 }]}>
              <Text style={[s.zmanValue, { color: colors.ink }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                {formatZmanTime(todayZmanim[cell.key])}
              </Text>
              <Text style={[s.zmanLabel, { color: colors.muted }]} maxFontSizeMultiplier={MAX_FONT_SCALE}>
                {cell.label}
              </Text>
            </View>
          ))}
        </View>
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
      overflow: 'hidden',
    },
    dateRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    enDate: { fontFamily: Fonts.uiSemiBold, fontSize: 13, letterSpacing: 0.3 },
    heDate: { fontFamily: Fonts.hebrewBold, fontSize: 17, writingDirection: 'rtl' as const },
    suggestedRow: {
      marginTop: 12,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    suggestedEn: { fontFamily: Fonts.uiSemiBold, fontSize: 23, flexShrink: 1 },
    suggestedHe: {
      fontFamily: Fonts.hebrewBold,
      fontSize: 27,
      writingDirection: 'rtl' as const,
      flexShrink: 1,
      marginLeft: 12,
    },
    actionRow: { marginTop: 10, flexDirection: 'row', alignItems: 'center' },
    davenBtn: { borderRadius: 10, paddingVertical: 9, paddingHorizontal: 16 },
    davenBtnText: { fontFamily: Fonts.uiSemiBold, fontSize: 13.5, color: '#FFFFFF' },
    resumeBtn: { marginLeft: 14 },
    resumeText: { fontFamily: Fonts.uiSemiBold, fontSize: 14.5 },
    setLocationRow: { marginTop: 10 },
    setLocationText: { fontFamily: Fonts.uiMedium, fontSize: 12.5 },
    zmanimStrip: {
      marginTop: 14,
      marginHorizontal: -18,
      marginBottom: -14,
      flexDirection: 'row',
      borderTopWidth: 1,
      borderBottomLeftRadius: 15,
      borderBottomRightRadius: 15,
    },
    zmanCell: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      paddingTop: 9,
      paddingBottom: 10,
      paddingHorizontal: 4,
    },
    zmanValue: { fontFamily: Fonts.uiSemiBold, fontSize: 14 },
    zmanLabel: {
      fontFamily: Fonts.uiMedium,
      fontSize: 9.5,
      letterSpacing: 0.6,
      textTransform: 'uppercase' as const,
      marginTop: 2,
    },
  });
}
