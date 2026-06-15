import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable, TextInput, Modal } from 'react-native';
import { Segment } from '../content/types';
import { DisplayMode } from '../store/preferences';
import { ColorPalette } from '../theme/colors';
import { Fonts, hebrewFontSize, englishFontSize } from '../theme/typography';

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

  const heSize = hebrewFontSize(fontStep);
  const enSize = englishFontSize(fontStep);

  const s = makeStyles(colors, heSize, enSize);

  // Rubric
  if (segment.type === 'rubric') {
    if (displayMode === 'en') return null;
    return <Text style={s.rubric}>{segment.heText}</Text>;
  }

  // Commentary
  if (segment.type === 'commentary') {
    if (displayMode === 'he') return null;
    return (
      <View style={s.commentaryBlock}>
        <Text style={s.commentaryTag}>EXPLANATION</Text>
        <Text style={s.commentaryText}>{segment.enText}</Text>
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
            {showInsight ? '▲ Hide insight' : '💡 Quick insight'}
          </Text>
        </Pressable>
        {showInsight && (
          <View style={s.insightBody}>
            <Text style={s.insightText}>{segment.enText}</Text>
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
        <Text style={s.heText}>{segment.heText}</Text>
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
      lineHeight: heSize * 1.95,
      color: c.ink,
      textAlign: 'right',
      writingDirection: 'rtl' as const,
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
    rubric: {
      fontFamily: Fonts.hebrew,
      fontSize: heSize * 0.72,
      color: c.rubric,
      fontStyle: 'italic',
      textAlign: 'right',
      writingDirection: 'rtl' as const,
      marginVertical: 6,
      paddingVertical: 6,
      paddingHorizontal: 10,
      borderRightWidth: 3,
      borderRightColor: c.rubric,
      backgroundColor: c.accentSoft,
      borderRadius: 10,
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
