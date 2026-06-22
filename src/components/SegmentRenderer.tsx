import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Pressable, TextInput, Modal } from 'react-native';
import { Segment } from '../content/types';
import { DisplayMode } from '../store/preferences';
import { ColorPalette } from '../theme/colors';
import { Fonts, hebrewFontSize, englishFontSize } from '../theme/typography';
import { RichText } from './RichText';

interface Props {
  segment: Segment;
  displayMode: DisplayMode;
  fontStep: number;
  colors: ColorPalette;
  isHighlighted: boolean;
  notes: string[];
  onToggleHighlight: () => void;
  onAddNote: (text: string) => void;
}

export function SegmentRenderer({
  segment, displayMode, fontStep, colors,
  isHighlighted, notes, onToggleHighlight, onAddNote,
}: Props) {
  const [showInsight, setShowInsight] = useState(false);
  const [noteModalVisible, setNoteModalVisible] = useState(false);
  const [noteText, setNoteText] = useState('');
  const [selectionVisible, setSelectionVisible] = useState(false);

  useEffect(() => {
    setSelectionVisible(false);
  }, [segment.id]);

  const heSize = hebrewFontSize(fontStep);
  const enSize = englishFontSize(fontStep);

  const s = makeStyles(colors, heSize, enSize);

  // Header — always visible, language-aware.
  // enPrimary headers (English-titled sections with a Hebrew name-list) render
  // the English title on top and the Hebrew names beneath; default is Hebrew-first.
  if (segment.type === 'header') {
    const heStyle = segment.plain ? s.headerHePlain : segment.enPrimary ? s.headerHeSub : s.headerHe;
    const enStyle = segment.plain ? s.headerEnPlain : segment.enPrimary ? s.headerEnPrimary : s.headerEn;
    const en = segment.enText && displayMode !== 'he' && <Text style={enStyle}>{segment.enText}</Text>;
    const he = segment.heText && displayMode !== 'en' && <Text style={heStyle}>{segment.heText}</Text>;
    return (
      <View style={s.headerBlock}>
        {segment.enPrimary ? <>{en}{he}</> : <>{he}{en}</>}
        {!segment.plain && <View style={s.headerRule} />}
      </View>
    );
  }

  // Section intro — hide in Hebrew-only mode. Bulleted intros render left-aligned
  // (a plain list, like the print) rather than centered italic.
  if (segment.type === 'section_intro') {
    if (displayMode === 'he') return null;
    const bulleted = /(^|\n)\s*•/.test(segment.enText ?? '');
    return (
      <RichText
        text={segment.enText ?? ''}
        style={bulleted ? s.sectionIntroList : s.sectionIntro}
        italicStyle={s.italicSpan}
        boldStyle={s.boldSpan}
        linkStyle={s.linkSpan}
      />
    );
  }

  // Transition — rhetorical bridge between prayers; striking with underglow
  if (segment.type === 'transition') {
    if (displayMode === 'he') return null;
    return (
      <View style={s.transitionWrap}>
        <Text style={s.transitionText}>{segment.enText}</Text>
        <View style={s.transitionGlow} />
      </View>
    );
  }

  // FAQ — collapsible, hide in Hebrew-only mode
  if (segment.type === 'faq') {
    if (displayMode === 'he') return null;
    return (
      <View>
        <Pressable
          style={s.faqToggle}
          onPress={() => setShowInsight(v => !v)}
          accessibilityRole="button"
          accessibilityLabel={showInsight ? 'Hide FAQ' : 'Show FAQ'}
        >
          <Text style={s.faqToggleText}>
            {showInsight ? '▲ Hide FAQ' : 'FAQ'}
          </Text>
        </Pressable>
        {showInsight && (
          <View style={s.faqBody}>
            <RichText text={segment.enText ?? ''} style={s.faqText} italicStyle={s.italicSpan} boldStyle={s.boldSpan} linkStyle={s.linkSpan} />
          </View>
        )}
      </View>
    );
  }

  // Rubric — Hebrew rubric hides in English-only; English rubric hides in Hebrew-only
  if (segment.type === 'rubric') {
    if (segment.heText && displayMode === 'en') return null;
    if (segment.enText && displayMode === 'he') return null;
    return segment.heText
      ? <Text style={s.rubricHe}>{segment.heText}</Text>
      : <Text style={s.rubricEn}>{segment.enText}</Text>;
  }

  // Commentary
  if (segment.type === 'commentary') {
    if (displayMode === 'he') return null;
    return (
      <View style={s.commentaryBlock}>
        <Text style={s.commentaryTag}>EXPLANATION</Text>
        <RichText text={segment.enText ?? ''} style={s.commentaryText} italicStyle={s.italicSpan} boldStyle={s.boldSpan} linkStyle={s.linkSpan} />
      </View>
    );
  }

  // Insight
  if (segment.type === 'insight') {
    if (displayMode === 'he') return null;
    return (
      <View>
        <Pressable
          style={s.insightToggle}
          onPress={() => setShowInsight(v => !v)}
          accessibilityRole="button"
          accessibilityLabel={showInsight ? 'Hide quick insight' : 'Show quick insight'}
        >
          <Text style={s.insightToggleText}>
            {showInsight ? '▲ Hide insight' : 'Insight'}
          </Text>
        </Pressable>
        {showInsight && (
          <View style={s.insightBody}>
            <RichText text={segment.enText ?? ''} style={s.insightText} italicStyle={s.italicSpan} boldStyle={s.boldSpan} linkStyle={s.linkSpan} />
          </View>
        )}
      </View>
    );
  }

  // Prayer (default)
  if (displayMode === 'en') return null;

  return (
    <View>
      <Pressable
        style={[s.heLine, isHighlighted && s.heLineHighlighted]}
        onPress={() => setSelectionVisible(v => !v)}
        accessibilityRole="text"
        accessibilityLabel={segment.heText}
      >
        <Text style={segment.display ? s.heTextDisplay : s.heText}>{segment.heText}</Text>
      </Pressable>

      {selectionVisible && (
        <View style={s.selectionBar}>
          <Pressable
            style={s.selectionBtn}
            onPress={() => { onToggleHighlight(); setSelectionVisible(false); }}
          >
            <Text style={s.selectionBtnText}>Highlight</Text>
          </Pressable>
          <Pressable
            style={s.selectionBtn}
            onPress={() => { setSelectionVisible(false); setNoteModalVisible(true); }}
          >
            <Text style={s.selectionBtnText}>Note</Text>
          </Pressable>
          <Pressable
            style={s.selectionBtn}
            onPress={() => setSelectionVisible(false)}
          >
            <Text style={s.selectionBtnText}>✕</Text>
          </Pressable>
        </View>
      )}

      {notes.map((note, i) => (
        <View key={i} style={s.noteChip}>
          <Text style={s.noteText}>✎ {note}</Text>
        </View>
      ))}

      <Modal
        visible={noteModalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setNoteModalVisible(false)}
      >
        <View style={s.modalOverlay}>
          <View style={s.modalCard}>
            <Text style={s.modalTitle}>Add note</Text>
            <TextInput
              style={s.modalInput}
              value={noteText}
              onChangeText={setNoteText}
              placeholder="Your note…"
              multiline
              autoFocus
            />
            <View style={s.modalButtons}>
              <Pressable onPress={() => { setNoteModalVisible(false); setNoteText(''); }}>
                <Text style={[s.modalBtn, { color: colors.muted }]}>Cancel</Text>
              </Pressable>
              <Pressable
                onPress={() => {
                  if (noteText.trim()) {
                    onAddNote(noteText.trim());
                    setNoteText('');
                  }
                  setNoteModalVisible(false);
                }}
              >
                <Text style={[s.modalBtn, { color: colors.accent }]}>Save</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

function makeStyles(c: ColorPalette, heSize: number, enSize: number) {
  return StyleSheet.create({
    heLine: {
      paddingVertical: 4,
      paddingHorizontal: 4,
      borderRadius: 6,
    },
    heLineHighlighted: {
      backgroundColor: c.goldFill,
      borderBottomWidth: 2,
      borderBottomColor: c.gold,
    },
    heText: {
      fontFamily: Fonts.hebrew,
      fontSize: heSize,
      lineHeight: heSize * 1.5,
      color: c.ink,
      textAlign: 'right',
      writingDirection: 'rtl' as const,
    },
    heTextDisplay: {
      // Kedushah climax verses: oversized & centered, mirroring the print
      fontFamily: Fonts.hebrew,
      fontSize: heSize * 1.5,
      lineHeight: heSize * 1.5 * 1.6,
      color: c.ink,
      textAlign: 'center',
      writingDirection: 'rtl' as const,
      paddingVertical: 6,
    },
    commentaryBlock: {
      marginTop: 12,
      paddingVertical: 12,
      paddingHorizontal: 14,
      backgroundColor: c.accentSoft,
      borderLeftWidth: 3,
      borderLeftColor: c.accent,
      borderRadius: 10,
    },
    commentaryTag: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 9.5,
      letterSpacing: 1.5,
      color: c.accent,
      marginBottom: 6,
    },
    commentaryText: {
      fontFamily: Fonts.english,
      fontSize: enSize,
      lineHeight: enSize * 1.62,
      color: c.ink,
    },
    italicSpan: {
      fontFamily: Fonts.englishItalic,
      fontStyle: 'italic' as const,
    },
    boldSpan: {
      fontFamily: Fonts.englishBold,
      fontWeight: '600' as const,
    },
    linkSpan: {
      color: c.accent,
      textDecorationLine: 'underline' as const,
      fontFamily: Fonts.uiSemiBold,
    },
    headerBlock: {
      marginTop: 20,
      marginBottom: 6,
      alignItems: 'center',
      gap: 2,
    },
    headerHe: {
      fontFamily: Fonts.hebrewBold,
      fontSize: heSize * 0.9,
      color: c.accent,
      textAlign: 'center',
      writingDirection: 'rtl' as const,
    },
    headerEn: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: enSize * 0.9,
      letterSpacing: 1.2,
      textTransform: 'uppercase' as const,
      color: c.accent,
      textAlign: 'center',
    },
    headerEnPrimary: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: enSize * 1.05,
      letterSpacing: 1.4,
      textTransform: 'uppercase' as const,
      color: c.accent,
      textAlign: 'center',
    },
    headerHeSub: {
      fontFamily: Fonts.hebrew,
      fontSize: heSize * 0.7,
      color: c.muted,
      textAlign: 'center',
      writingDirection: 'rtl' as const,
      marginTop: 4,
    },
    headerHePlain: {
      fontFamily: Fonts.hebrew,
      fontSize: heSize * 0.95,
      color: c.ink,
      textAlign: 'center',
      writingDirection: 'rtl' as const,
    },
    headerEnPlain: {
      fontFamily: Fonts.english,
      fontSize: enSize,
      color: c.ink,
      textAlign: 'center',
    },
    headerRule: {
      height: 1,
      width: '40%',
      backgroundColor: c.line,
      marginTop: 6,
    },
    sectionIntro: {
      fontFamily: Fonts.english,
      fontSize: enSize,
      lineHeight: enSize * 1.6,
      color: c.ink,
      textAlign: 'center',
      fontStyle: 'italic',
      paddingHorizontal: 8,
      marginBottom: 10,
    },
    sectionIntroList: {
      fontFamily: Fonts.english,
      fontSize: enSize,
      lineHeight: enSize * 1.62,
      color: c.ink,
      textAlign: 'left',
      paddingHorizontal: 6,
      marginBottom: 10,
    },
    transitionWrap: {
      alignItems: 'center',
      marginVertical: 26,
      paddingHorizontal: 12,
    },
    transitionText: {
      fontFamily: Fonts.englishBold,
      fontSize: enSize * 1.3,
      lineHeight: enSize * 1.7,
      color: c.accent,
      textAlign: 'center',
      letterSpacing: 0.2,
      textShadowColor: c.accent,
      textShadowOffset: { width: 0, height: 4 },
      textShadowRadius: 18,
    },
    transitionGlow: {
      marginTop: 14,
      width: 130,
      height: 7,
      borderRadius: 7,
      backgroundColor: c.gold,
      opacity: 0.55,
      shadowColor: c.gold,
      shadowOpacity: 0.8,
      shadowRadius: 14,
      shadowOffset: { width: 0, height: 3 },
      elevation: 6,
    },
    faqToggle: {
      marginTop: 8,
      alignSelf: 'flex-start',
      paddingVertical: 5,
      paddingHorizontal: 10,
      borderRadius: 20,
      borderWidth: 1,
      borderStyle: 'dashed',
      borderColor: c.gold,
    },
    faqToggleText: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 11,
      color: c.gold,
    },
    faqBody: {
      marginTop: 6,
      padding: 10,
      borderRadius: 10,
      backgroundColor: c.accentSoft,
      borderWidth: 1,
      borderColor: c.gold,
    },
    faqText: {
      fontFamily: Fonts.english,
      fontSize: enSize * 0.9,
      lineHeight: enSize * 1.5,
      color: c.ink,
    },
    rubricHe: {
      fontFamily: Fonts.hebrew,
      fontSize: heSize * 0.72,
      color: c.rubric,
      fontStyle: 'italic',
      textAlign: 'right',
      writingDirection: 'rtl' as const,
      marginVertical: 6,
      paddingVertical: 4,
    },
    rubricEn: {
      fontFamily: Fonts.englishItalic,
      fontSize: enSize * 0.88,
      color: c.rubric,
      textAlign: 'center',
      marginVertical: 6,
      paddingVertical: 4,
    },
    insightToggle: {
      marginTop: 10,
      alignSelf: 'flex-start',
      paddingVertical: 6,
      paddingHorizontal: 11,
      borderRadius: 20,
      borderWidth: 1,
      borderStyle: 'dashed',
      borderColor: c.accent,
    },
    insightToggleText: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 12,
      color: c.accent,
    },
    insightBody: {
      marginTop: 8,
      padding: 11,
      borderRadius: 10,
      backgroundColor: c.accentSoft,
      borderWidth: 1,
      borderColor: c.gold,
    },
    insightText: {
      fontFamily: Fonts.english,
      fontSize: enSize,
      lineHeight: enSize * 1.6,
      color: c.ink,
    },
    selectionBar: {
      flexDirection: 'row',
      gap: 4,
      marginTop: 4,
      backgroundColor: c.ink,
      padding: 6,
      borderRadius: 12,
      alignSelf: 'center',
    },
    selectionBtn: {
      paddingVertical: 8,
      paddingHorizontal: 14,
      borderRadius: 8,
    },
    selectionBtnText: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 12.5,
      color: c.surface,
    },
    noteChip: {
      marginTop: 4,
      paddingVertical: 6,
      paddingHorizontal: 10,
      backgroundColor: c.accentSoft,
      borderRadius: 8,
    },
    noteText: {
      fontFamily: Fonts.ui,
      fontSize: 12.5,
      color: c.ink,
    },
    modalOverlay: {
      flex: 1,
      justifyContent: 'flex-end',
      backgroundColor: 'rgba(0,0,0,0.4)',
    },
    modalCard: {
      backgroundColor: c.surface,
      borderRadius: 20,
      padding: 20,
      marginHorizontal: 12,
      marginBottom: 40,
    },
    modalTitle: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 16,
      color: c.ink,
      marginBottom: 12,
    },
    modalInput: {
      fontFamily: Fonts.ui,
      fontSize: 15,
      color: c.ink,
      borderWidth: 1,
      borderColor: c.line,
      borderRadius: 10,
      padding: 10,
      minHeight: 80,
      textAlignVertical: 'top',
    },
    modalButtons: {
      flexDirection: 'row',
      justifyContent: 'flex-end',
      gap: 20,
      marginTop: 12,
    },
    modalBtn: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 15,
    },
  });
}
