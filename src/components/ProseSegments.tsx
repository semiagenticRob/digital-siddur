import React from 'react';
import { Text, StyleSheet } from 'react-native';
import { Segment } from '../content/types';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';
import { RichText } from './RichText';

// Long-form prose reader used by the appendices and the About pieces:
// headers as kickers, Hebrew lines RTL, everything else as RichText prose.
export function ProseSegments({
  segments, heSize, enSize, colors,
}: {
  segments: Segment[];
  heSize: number;
  enSize: number;
  colors: ColorPalette;
}) {
  const s = makeStyles(heSize, enSize);
  return (
    <>
      {segments.map((seg, i) => {
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
            <Text key={i} style={[s.he, { color: colors.ink }]} selectable accessibilityLanguage="he">
              {seg.heText}
            </Text>
          );
        }
        return (
          <RichText
            key={i}
            text={seg.enText ?? ''}
            style={[s.prose, { color: colors.ink }]}
            italicStyle={s.italic}
            boldStyle={s.bold}
            linkStyle={[s.link, { color: colors.accent }]}
            selectable
          />
        );
      })}
    </>
  );
}

function makeStyles(heSize: number, enSize: number) {
  return StyleSheet.create({
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
    bold: { fontFamily: Fonts.englishBold, fontWeight: '600' as const },
    link: { textDecorationLine: 'underline' as const, fontFamily: Fonts.uiSemiBold },
  });
}
