import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';

interface Props {
  colors: ColorPalette;
  onBump: (delta: number) => void;
}

export function FontSizeControl({ colors, onBump }: Props) {
  const s = makeStyles(colors);
  return (
    <View style={s.wrap} accessibilityRole="none" accessibilityLabel="Text size">
      <Pressable
        style={s.btn}
        onPress={() => onBump(-1)}
        accessibilityRole="button"
        accessibilityLabel="Smaller text"
      >
        <Text style={s.btnText}>A−</Text>
      </Pressable>
      <Pressable
        style={s.btn}
        onPress={() => onBump(1)}
        accessibilityRole="button"
        accessibilityLabel="Larger text"
      >
        <Text style={[s.btnText, s.btnTextLarge]}>A+</Text>
      </Pressable>
    </View>
  );
}

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    wrap: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: c.accentSoft,
      borderRadius: 11,
      padding: 3,
    },
    btn: {
      width: 36,
      height: 30,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 8,
    },
    btnText: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 12,
      color: c.accent,
    },
    btnTextLarge: { fontSize: 15 },
  });
}
