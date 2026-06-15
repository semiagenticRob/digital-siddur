import React, { useRef, forwardRef, useImperativeHandle } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { FlashList, FlashListRef } from '@shopify/flash-list';
import { Service, Segment } from '../content/types';
import { DisplayMode } from '../store/preferences';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';
import { SegmentRenderer } from './SegmentRenderer';

type ListItem =
  | { kind: 'prayerHeader'; prayerId: string; heTitle: string; enTitle: string; groupTitle: string }
  | { kind: 'segment'; segment: Segment; prayerId: string };

function flattenService(service: Service): ListItem[] {
  const items: ListItem[] = [];
  for (const group of service.groups) {
    for (const prayer of group.prayers) {
      items.push({
        kind: 'prayerHeader',
        prayerId: prayer.id,
        heTitle: prayer.heTitle,
        enTitle: prayer.enTitle,
        groupTitle: group.title,
      });
      for (const seg of prayer.segments) {
        items.push({ kind: 'segment', segment: seg, prayerId: prayer.id });
      }
    }
  }
  return items;
}

export interface ServiceScrollHandle {
  scrollToPrayer: (prayerId: string) => void;
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
}

export const ServiceScroll = forwardRef<ServiceScrollHandle, Props>(
  ({ service, displayMode, fontStep, colors, isHighlighted, getNotes, onToggleHighlight, onAddNote }, ref) => {
    const listRef = useRef<FlashListRef<ListItem>>(null);
    const items = flattenService(service);

    useImperativeHandle(ref, () => ({
      scrollToPrayer: (prayerId: string) => {
        const idx = items.findIndex(
          (item) => item.kind === 'prayerHeader' && item.prayerId === prayerId
        );
        if (idx >= 0) {
          listRef.current?.scrollToIndex({ index: idx, animated: true });
        }
      },
    }));

    const s = makeStyles(colors);

    return (
      <FlashList
        ref={listRef}
        data={items}
        keyExtractor={(item, i) =>
          item.kind === 'prayerHeader'
            ? `header-${item.prayerId}`
            : `seg-${item.segment.id}-${i}`
        }
        renderItem={({ item }) => {
          if (item.kind === 'prayerHeader') {
            return (
              <View style={s.prayerHeader}>
                <Text style={s.prayerHeTitle}>{item.heTitle}</Text>
                <View style={s.prayerHeaderLine} />
                <Text style={s.prayerEnTitle}>{item.enTitle}</Text>
              </View>
            );
          }
          return (
            <View style={s.segmentWrapper}>
              <SegmentRenderer
                segment={item.segment}
                displayMode={displayMode}
                fontStep={fontStep}
                colors={colors}
                isHighlighted={isHighlighted(item.segment.id)}
                notes={getNotes(item.segment.id)}
                onToggleHighlight={() => onToggleHighlight(item.segment.id)}
                onAddNote={(text) => onAddNote(item.segment.id, text)}
              />
            </View>
          );
        }}
        contentContainerStyle={s.listContent}
      />
    );
  }
);

function makeStyles(c: ColorPalette) {
  return StyleSheet.create({
    listContent: { paddingBottom: 120, paddingHorizontal: 16 },
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
    },
    prayerHeaderLine: { flex: 1, height: 1, backgroundColor: c.line },
    prayerEnTitle: {
      fontFamily: Fonts.uiMedium,
      fontSize: 11.5,
      letterSpacing: 1.5,
      textTransform: 'uppercase' as const,
      color: c.muted,
    },
    segmentWrapper: { paddingVertical: 2 },
  });
}
