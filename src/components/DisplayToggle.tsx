import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { DisplayMode } from '../store/preferences';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';

const MODES: Array<{ value: DisplayMode; label: string; isHebrew?: boolean }> = [
  { value: 'he', label: 'עברית', isHebrew: true },
  { value: 'both', label: 'Both' },
  { value: 'en', label: 'English' },
];

interface Props {
  value: DisplayMode;
  colors: ColorPalette;
  onChange: (mode: DisplayMode) => void;
}

export function DisplayToggle({ value, colors, onChange }: Props) {
  const s = makeStyles(colors);
  return (
    <View style={s.seg} accessibilityRole="radiogroup" accessibilityLabel="Display language">
      {MODES.map(({ value: v, label, isHebrew }) => (
        <Pressable
          key={v}
          style={[s.btn, value === v && s.btnActive]}
          onPress={() => onChange(v)}
          accessibilityRole="radio"
          accessibilityState={{ checked: value === v }}
          accessibilityLabel={label}
        >
          <Text style={[
            s.label,
            value === v && s.labelActive,
            isHebrew && s.labelHebrew,
          ]}>
            {label}
          </Text>
        </Pressable>
      ))}
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    seg: {
      flexDirection: 'row',
      backgroundColor: c.accentSoft,
      borderRadius: 11,
      padding: 3,
      alignSelf: 'stretch',
    },
    btn: {
      flex: 1,
      paddingVertical: 8,
      paddingHorizontal: 4,
      borderRadius: 8,
      alignItems: 'center',
    },
    btnActive: {
      backgroundColor: c.surface,
      shadowColor: '#000',
      shadowOpacity: 0.12,
      shadowRadius: 2,
      elevation: 2,
    },
    label: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 12,
      color: c.muted,
    },
    labelActive: { color: c.accent },
    labelHebrew: {
      fontFamily: Fonts.hebrew,
      fontSize: 14,
    },
  });
}
