import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView, Modal, useColorScheme } from 'react-native';
import { useSectionModalStore } from '../store/sectionModal';
import { getSection } from '../content/sections';
import { usePreferencesStore } from '../store/preferences';
import { LightColors, DarkColors, ColorPalette } from '../theme/colors';
import { Fonts, englishFontSize } from '../theme/typography';
import { RichText } from './RichText';

export function SectionModal() {
  const openKey = useSectionModalStore((s) => s.openKey);
  const close = useSectionModalStore((s) => s.close);

  const { theme, fontStep } = usePreferencesStore();
  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors: ColorPalette = (isDark ? DarkColors : LightColors) as ColorPalette;

  const section = openKey != null ? getSection(openKey) : null;
  const enSize = englishFontSize(fontStep);
  const s = makeStyles(colors, enSize);

  return (
    <Modal visible={openKey != null} animationType="slide" onRequestClose={close} transparent={false}>
      <View style={[s.screen, { backgroundColor: colors.paper }]}>
        <View style={[s.header, { borderBottomColor: colors.line, backgroundColor: colors.surface }]}>
          <Text style={[s.kicker, { color: colors.muted }]}>INTRODUCTION</Text>
          <Pressable onPress={close} accessibilityRole="button" accessibilityLabel="Close" style={s.closeBtn}>
            <Text style={[s.closeText, { color: colors.accent }]}>Done</Text>
          </Pressable>
        </View>

        {!section ? (
          <View style={s.empty}>
            <Text style={{ fontFamily: Fonts.ui, color: colors.muted, textAlign: 'center' }}>
              Section not available yet.
            </Text>
          </View>
        ) : (
          <ScrollView contentContainerStyle={s.body} showsVerticalScrollIndicator={false}>
            <Text style={[s.title, { color: colors.ink }]}>{section.title}</Text>
            <RichText
              text={section.body}
              style={[s.prose, { color: colors.ink }]}
              italicStyle={s.italic}
              boldStyle={s.bold}
              linkStyle={s.link}
            />
          </ScrollView>
        )}
      </View>
    </Modal>
  );
}

function makeStyles(c: ColorPalette, enSize: number) {
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
    title: {
      fontFamily: Fonts.englishBold, fontSize: enSize * 1.3,
      lineHeight: enSize * 1.7, marginBottom: 18,
    },
    prose: {
      fontFamily: Fonts.english, fontSize: enSize,
      lineHeight: enSize * 1.62, marginBottom: 12,
    },
    italic: { fontFamily: Fonts.englishItalic, fontStyle: 'italic' as const },
    bold: { fontFamily: Fonts.englishBold, fontWeight: '600' as const },
    link: { color: c.accent, textDecorationLine: 'underline' as const, fontFamily: Fonts.uiSemiBold },
  });
}
