import React, { useRef, useMemo, forwardRef, useImperativeHandle } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { FlashList, FlashListRef } from '@shopify/flash-list';
import { Service, Segment } from '../content/types';
import { DisplayMode } from '../store/preferences';
import { ColorPalette } from '../theme/colors';
import { Fonts, MAX_FONT_SCALE } from '../theme/typography';
import { CONTENT_WIDTH, LIST_HORIZONTAL_PAD } from '../theme/layout';
import { SegmentRenderer } from './SegmentRenderer';
import { flattenService, ListItem } from './flattenService';
import { useAnnotationsStore } from '../store/annotations';

export interface ServiceScrollHandle {
  scrollToPrayer: (prayerId: string) => void;
  scrollToOffset: (offset: number, animated?: boolean) => void;
}

interface Props {
  service: Service;
  displayMode: DisplayMode;
  fontStep: number;
  colors: ColorPalette;
  isHighlighted: (segmentId: string) => boolean;
  getNotes: (segmentId: string) => string[];
  onToggleHighlight: (segmentId: string) => void;
  onAddNote: (segmentId: string, text: string) => void;
  // Fires once when the list has completed its first layout — the earliest
  // moment scrollToPrayer/scrollToOffset are reliable (replaces the old
  // fixed-delay guess in the reader screen).
  onReady?: () => void;
  // Fires when a scroll gesture settles (drag end / momentum end) with the
  // current offset — used to persist the reading position.
  onScrollSettled?: (offset: number) => void;
}

export const ServiceScroll = forwardRef<ServiceScrollHandle, Props>(
  ({ service, displayMode, fontStep, colors, isHighlighted, getNotes, onToggleHighlight, onAddNote, onReady, onScrollSettled }, ref) => {
    const listRef = useRef<FlashListRef<ListItem>>(null);
    // In English-only mode, annotated prayer lines stay in the list, so the
    // list rebuilds when annotations change — in that mode only (elsewhere
    // these selectors return null and never trigger a rebuild).
    const enMode = displayMode === 'en';
    const highlights = useAnnotationsStore((s) => (enMode ? s.highlights : null));
    const notes = useAnnotationsStore((s) => (enMode ? s.notes : null));
    const items = useMemo(() => {
      const isAnnotated =
        highlights && notes
          ? (id: string) => highlights.has(id) || (notes[id]?.length ?? 0) > 0
          : undefined;
      return flattenService(service, displayMode, isAnnotated);
    }, [service, displayMode, highlights, notes]);

    useImperativeHandle(ref, () => ({
      scrollToPrayer: (prayerId: string) => {
        const idx = items.findIndex(
          (item) => item.kind === 'prayerHeader' && item.prayerId === prayerId
        );
        if (idx >= 0) {
          listRef.current?.scrollToIndex({ index: idx, animated: true });
        }
      },
      scrollToOffset: (offset: number, animated = false) => {
        listRef.current?.scrollToOffset({ offset, animated });
      },
    }), [items]);

    const settle = onScrollSettled
      ? (e: { nativeEvent: { contentOffset: { y: number } } }) =>
          onScrollSettled(e.nativeEvent.contentOffset.y)
      : undefined;

    const s = useMemo(() => makeStyles(colors), [colors]);
    const optionalBoxStyle = {
      solo: s.optionalSolo,
      start: s.optionalStart,
      mid: s.optionalMid,
      end: s.optionalEnd,
    };

    const renderSegment = (segment: Segment, prayerId: string) => (
      <SegmentRenderer
        segment={segment}
        displayMode={displayMode}
        fontStep={fontStep}
        colors={colors}
        isHighlighted={isHighlighted(segment.id)}
        notes={getNotes(segment.id)}
        onToggleHighlight={() => onToggleHighlight(segment.id)}
        onAddNote={(text) => onAddNote(segment.id, text)}
      />
    );

    return (
      <FlashList
        ref={listRef}
        data={items}
        // The note sheet is a Modal rendered from inside a list cell, so in
        // React's tree it lives inside this ScrollView. With the default
        // ("never"), a tap on the sheet's Save/Cancel while the keyboard is
        // open is captured here and only dismisses the keyboard — Save needs
        // a second tap. "handled" lets the button receive the tap.
        keyboardShouldPersistTaps="handled"
        keyExtractor={(item, i) =>
          item.kind === 'prayerHeader'
            ? `header-${item.prayerId}`
            : item.kind === 'optionalSegment'
            ? `optseg-${item.segment.id}`
            : `seg-${item.segment.id}-${i}`
        }
        // Recycle cells only between items of the same shape — a short rubric
        // cell reused for a long prayer re-measures badly and jumps.
        getItemType={(item) =>
          item.kind === 'prayerHeader' ? 'prayerHeader' : `${item.kind}:${item.segment.type}`
        }
        renderItem={({ item }) => {
          // Every item is wrapped in a full-width root so FlashList can't size
          // the cell to its content width — otherwise a long single line (e.g. a
          // commentary paragraph) makes the cell wider than the screen and the
          // text overflows/clips on the right instead of wrapping.
          let inner: React.ReactNode;
          if (item.kind === 'prayerHeader') {
            inner = (
              <View style={s.prayerHeader}>
                <Text style={s.prayerHeTitle} maxFontSizeMultiplier={MAX_FONT_SCALE} accessibilityLanguage="he">{item.heTitle}</Text>
                <View style={s.prayerHeaderLine} />
                <Text style={s.prayerEnTitle} maxFontSizeMultiplier={MAX_FONT_SCALE}>{item.enTitle}</Text>
              </View>
            );
          } else if (item.kind === 'optionalSegment') {
            const boxStyle = optionalBoxStyle[item.pos];
            inner = (
              <View style={boxStyle}>
                {renderSegment(item.segment, item.prayerId)}
              </View>
            );
          } else {
            inner = (
              <View style={s.segmentWrapper}>
                {renderSegment(item.segment, item.prayerId)}
              </View>
            );
          }
          return <View style={s.itemRoot}>{inner}</View>;
        }}
        contentContainerStyle={s.listContent}
        // Render well beyond the viewport so cells finish their (async) text
        // measurement and settle BEFORE they scroll into view — avoids the
        // transient mid-measurement state where a long RTL prayer line briefly
        // breaks mid-word at a wrap boundary before reflowing correctly.
        drawDistance={1000}
        onLoad={onReady ? () => onReady() : undefined}
        onScrollEndDrag={settle}
        onMomentumScrollEnd={settle}
      />
    );
  }
);

function makeStyles(c: ColorPalette) {
  // Shared base for the four optional-position styles (a contiguous run of
  // optional segments renders as one connected gray box).
  const optBase = {
    backgroundColor: c.optionalShade,
    borderColor: c.optionalBorder,
    paddingHorizontal: 12,
  } as const;
  return StyleSheet.create({
    listContent: { paddingBottom: 120, paddingHorizontal: LIST_HORIZONTAL_PAD },
    // Pin every FlashList item to a CONCRETE width (CONTENT_WIDTH = screen minus
    // listContent's horizontal padding each side). '100%' is insufficient: a
    // FlashList cell can size to its content width, and 100% of a content-sized
    // cell is still too wide — short commentary lines then overflow/clip on the
    // right instead of wrapping. A fixed px width forces text to wrap.
    itemRoot: { width: CONTENT_WIDTH },
    prayerHeader: {
      paddingTop: 20,
      paddingBottom: 10,
      borderBottomWidth: 1,
      borderBottomColor: c.line,
      flexDirection: 'row',
      alignItems: 'center',
      gap: 10,
    },
    prayerHeTitle: {
      fontFamily: Fonts.hebrewBold,
      fontSize: 17,
      color: c.accent,
      textAlign: 'right',
      writingDirection: 'rtl' as const,
      flexShrink: 1,   // wrap long combined titles instead of overflowing off-screen
    },
    // minWidth keeps a bit of the divider visible; flexShrink lets it yield space
    // to long titles so they wrap rather than clip past the right edge.
    prayerHeaderLine: { flexGrow: 1, flexShrink: 1, minWidth: 12, height: 1, backgroundColor: c.line },
    prayerEnTitle: {
      fontFamily: Fonts.uiMedium,
      fontSize: 11.5,
      letterSpacing: 1.5,
      textTransform: 'uppercase' as const,
      color: c.muted,
      flexShrink: 1,   // wrap long English title instead of clipping off-screen
    },
    segmentWrapper: { paddingVertical: 2 },
    // Each optional segment is its own FlashList item. Position styles make
    // contiguous items look like one connected gray box (see optBase above).
    optionalSolo: {
      ...optBase,
      borderWidth: 1,
      borderRadius: 14,
      paddingVertical: 8,
      marginVertical: 10,
    },
    optionalStart: {
      ...optBase,
      borderTopWidth: 1,
      borderLeftWidth: 1,
      borderRightWidth: 1,
      borderTopLeftRadius: 14,
      borderTopRightRadius: 14,
      paddingTop: 8,
      paddingBottom: 4,
      marginTop: 10,
    },
    optionalMid: {
      ...optBase,
      borderLeftWidth: 1,
      borderRightWidth: 1,
      paddingVertical: 4,
    },
    optionalEnd: {
      ...optBase,
      borderBottomWidth: 1,
      borderLeftWidth: 1,
      borderRightWidth: 1,
      borderBottomLeftRadius: 14,
      borderBottomRightRadius: 14,
      paddingTop: 4,
      paddingBottom: 8,
      marginBottom: 10,
    },
  });
}
