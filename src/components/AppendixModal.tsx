import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView, Modal } from 'react-native';
import { useAppendixStore } from '../store/appendix';
import { getAppendix } from '../content/appendices';
import { usePreferencesStore } from '../store/preferences';
import { useThemeColors } from '../theme/useThemeColors';
import { Fonts, hebrewFontSize, englishFontSize } from '../theme/typography';
import { ProseSegments } from './ProseSegments';

export function AppendixModal() {
  const openNumber = useAppendixStore((s) => s.openNumber);
  const close = useAppendixStore((s) => s.close);

  const { fontStep } = usePreferencesStore();
  const { colors } = useThemeColors();

  const appendix = openNumber != null ? getAppendix(openNumber) : null;
  const s = makeStyles(englishFontSize(fontStep));

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
            <ProseSegments
              segments={appendix.segments}
              heSize={hebrewFontSize(fontStep)}
              enSize={englishFontSize(fontStep)}
              colors={colors}
            />
          </ScrollView>
        )}
      </View>
    </Modal>
  );
}

function makeStyles(enSize: number) {
  return StyleSheet.create({
    screen: { flex: 1 },
    header: {
      flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
      paddingTop: 56, paddingBottom: 12, paddingHorizontal: 18, borderBottomWidth: 1,
    },
    kicker: { fontFamily: Fonts.uiSemiBold, fontSize: 12, letterSpacing: 1.5 },
    closeBtn: { minHeight: 44, minWidth: 44, paddingHorizontal: 8, alignItems: 'center', justifyContent: 'center' },
    closeText: { fontFamily: Fonts.uiSemiBold, fontSize: 16 },
    empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
    body: { padding: 22, paddingBottom: 80 },
    title: { fontFamily: Fonts.englishBold, fontSize: enSize * 1.5, lineHeight: enSize * 1.9, marginBottom: 16 },
  });
}
