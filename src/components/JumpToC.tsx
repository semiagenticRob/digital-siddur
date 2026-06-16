import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView, Modal } from 'react-native';
import { Service } from '../content/types';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';

interface Props {
  visible: boolean;
  service: Service;
  colors: ColorPalette;
  onSelectPrayer: (prayerId: string) => void;
  onClose: () => void;
}

export function JumpToC({ visible, service, colors, onSelectPrayer, onClose }: Props) {
  const s = makeStyles(colors);
  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={s.overlay}>
        <View style={s.drawer}>
          <Text style={s.drawerTitle}>{service.enTitle} — Jump to</Text>
          <ScrollView style={s.scroll} showsVerticalScrollIndicator={false}>
            {service.groups.map(group => (
              <View key={group.id}>
                <Text style={s.groupLabel}>{group.title}</Text>
                {group.prayers.map(prayer => (
                  <Pressable
                    key={prayer.id}
                    style={({ pressed }) => [s.prayerRow, pressed && s.prayerRowPressed]}
                    onPress={() => { onSelectPrayer(prayer.id); onClose(); }}
                    accessibilityRole="button"
                    accessibilityLabel={`Jump to ${prayer.enTitle}`}
                  >
                    <Text style={s.prayerEn}>{prayer.enTitle}</Text>
                    <Text style={s.prayerHe}>{prayer.heTitle}</Text>
                  </Pressable>
                ))}
              </View>
            ))}
          </ScrollView>
          <Pressable style={s.closeBtn} onPress={onClose}>
            <Text style={s.closeBtnText}>Close</Text>
          </Pressable>
        </View>
        <Pressable style={s.scrim} onPress={onClose} accessibilityLabel="Close navigation" />
      </View>
    </Modal>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    overlay: { flex: 1, flexDirection: 'row' },
    drawer: {
      width: '80%',
      maxWidth: 320,
      backgroundColor: c.surface,
      borderRightWidth: 1,
      borderRightColor: c.line,
      paddingTop: 60,
      flex: 1,
    },
    scrim: {
      flex: 1,
      backgroundColor: 'rgba(10,12,18,0.45)',
    },
    drawerTitle: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 13,
      letterSpacing: 1.2,
      textTransform: 'uppercase' as const,
      color: c.muted,
      paddingHorizontal: 18,
      paddingBottom: 8,
    },
    scroll: { flex: 1 },
    groupLabel: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 10.5,
      letterSpacing: 1.6,
      textTransform: 'uppercase' as const,
      color: c.muted,
      paddingHorizontal: 18,
      paddingTop: 14,
      paddingBottom: 4,
    },
    prayerRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: 10,
      paddingVertical: 11,
      paddingHorizontal: 12,
      marginHorizontal: 6,
      borderRadius: 10,
    },
    prayerRowPressed: { opacity: 0.6 },
    prayerEn: {
      fontFamily: Fonts.uiMedium,
      fontSize: 14,
      color: c.ink,
      flex: 1,
      minWidth: 0,
    },
    prayerHe: {
      fontFamily: Fonts.hebrew,
      fontSize: 16,
      color: c.muted,
      textAlign: 'right' as const,
      writingDirection: 'rtl' as const,
      flexShrink: 1,
      maxWidth: '52%',
    },
    closeBtn: {
      margin: 16,
      padding: 14,
      backgroundColor: c.accentSoft,
      borderRadius: 12,
      alignItems: 'center',
    },
    closeBtnText: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 14,
      color: c.accent,
    },
  });
}
