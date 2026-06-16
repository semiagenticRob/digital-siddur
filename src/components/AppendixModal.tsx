import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView, Modal, useColorScheme } from 'react-native';
import { useAppendixStore } from '../store/appendix';
import { getAppendix } from '../content/appendices';
import { usePreferencesStore } from '../store/preferences';
import { LightColors, DarkColors, ColorPalette } from '../theme/colors';
import { Fonts, hebrewFontSize, englishFontSize } from '../theme/typography';
import { RichText } from './RichText';

export function AppendixModal() {
  const openNumber = useAppendixStore((s) => s.openNumber);
  const close = useAppendixStore((s) => s.close);

  const { theme, fontStep } = usePreferencesStore();
  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors: ColorPalette = (isDark ? DarkColors : LightColors) as ColorPalette;

  const appendix = openNumber != null ? getAppendix(openNumber) : null;
  const s = makeStyles(colors, hebrewFontSize(fontStep), englishFontSize(fontStep));

  return (
    <Modal visible={openNumber != null} animationType="slide" onRequestClose={close} transparent={false}>
      <View style={[s.screen, { backgroundColor: colors.paper }]}>
        <View style={[s.header, { borderBottomColor: colors.line, backgroundColor: colors.surface }]}>
          <Text style={[s.kicker, { color: colors.muted }]}>
            {openNumber != null ? `APPENDIX ${openNumber}` : ''}
          </Text>
          <Pressable onPress={close} accessibilityRole="button" accessibilityLabel="Close appendix" style={s.closeBtn}>
            <Text style={[s.closeText, { color: colors.accent }]}>Done</Text>
          </Pressable>
        </View>

        {!appendix ? (
          <View style={s.empty}>
            <Text style={{ fontFamily: Fonts.ui, color: colors.muted, textAlign: 'center' }}>
              {openNumber != null
                ? `Appendix ${openNumber} isn't available yet.`
                : ''}
            </Text>
          </View>
        ) : (
          <ScrollView contentContainerStyle={s.body} showsVerticalScrollIndicator={false}>
            <Text style={[s.title, { color: colors.ink }]}>{appendix.title}</Text>
            {appendix.segments.map((seg, i) => {
              if (seg.type === 'header') {
                return (
                  <Text key={i} style={[s.subhead, { color: colors.accent }]}>
                    {seg.enText || seg.heText}
                  </Text>
                );
              }
              if (seg.type === 'rubric') {
                return (
                  <Text key={i} style={[s.rubric, { color: colors.muted }]}>
                    {seg.enText || seg.heText}
                  </Text>
                );
              }
              if (seg.type === 'prayer') {
                return (
                  <Text key={i} style={[s.he, { color: colors.ink }]}>{seg.heText}</Text>
                );
              }
              // commentary / insight prose
              return (
                <RichText
                  key={i}
                  text={seg.enText ?? ''}
                  style={[s.prose, { color: colors.ink }]}
                  italicStyle={s.italic}
                  linkStyle={s.link}
                />
              );
            })}
          </ScrollView>
        )}
      </View>
    </Modal>
  );
}

function makeStyles(c: ColorPalette, heSize: number, enSize: number) {
  return StyleSheet.create({
    screen: { flex: 1 },
    header: {
      flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
      paddingTop: 56, paddingBottom: 12, paddingHorizontal: 18, borderBottomWidth: 1,
    },
    kicker: { fontFamily: Fonts.uiSemiBold, fontSize: 12, letterSpacing: 1.5 },
    closeBtn: { padding: 4 },
    closeText: { fontFamily: Fonts.uiSemiBold, fontSize: 16 },
    empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
    body: { padding: 22, paddingBottom: 80 },
    title: { fontFamily: Fonts.englishBold, fontSize: enSize * 1.5, lineHeight: enSize * 1.9, marginBottom: 16 },
    subhead: {
      fontFamily: Fonts.uiSemiBold, fontSize: enSize * 0.85, letterSpacing: 1,
      textTransform: 'uppercase' as const, marginTop: 18, marginBottom: 6,
    },
    rubric: { fontFamily: Fonts.englishItalic, fontSize: enSize * 0.9, marginTop: 8, marginBottom: 4 },
    he: {
      fontFamily: Fonts.hebrew, fontSize: heSize, lineHeight: heSize * 1.9,
      textAlign: 'right' as const, writingDirection: 'rtl' as const, marginVertical: 8,
    },
    prose: { fontFamily: Fonts.english, fontSize: enSize, lineHeight: enSize * 1.62, marginBottom: 12 },
    italic: { fontFamily: Fonts.englishItalic, fontStyle: 'italic' as const },
    link: { color: c.accent, textDecorationLine: 'underline' as const, fontFamily: Fonts.uiSemiBold },
  });
}
