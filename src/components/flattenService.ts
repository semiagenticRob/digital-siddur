import type { Service, Segment } from '../content/types';
import type { DisplayMode } from '../store/preferences';

// Pure list-shaping for ServiceScroll — no React/RN imports so it can be
// unit-tested directly.

export type ListItem =
  | { kind: 'prayerHeader'; prayerId: string; heTitle: string; enTitle: string; groupTitle: string }
  | { kind: 'segment'; segment: Segment; prayerId: string }
  | { kind: 'optionalSegment'; segment: Segment; prayerId: string; pos: 'solo' | 'start' | 'mid' | 'end' };

// Mirrors SegmentRenderer's display-mode gating. Must stay in sync with it:
// a segment filtered out here never reaches the renderer, and a segment kept
// here must render non-null, otherwise optional runs draw empty shaded boxes.
export function isSegmentVisible(segment: Segment, displayMode: DisplayMode): boolean {
  switch (segment.type) {
    case 'header':
      // A header shows whichever titles the mode allows; it disappears only
      // when neither field would render.
      return (
        (!!segment.heText && displayMode !== 'en') ||
        (!!segment.enText && displayMode !== 'he')
      );
    case 'rubric':
      // Instructional rubrics never hide behind Hebrew-only mode: the print
      // always shows its instructions ("For men:", "Omit on Rosh Chodesh…").
      // A Hebrew-only rubric still hides in English-only mode — the prayer
      // text it governs is hidden there too.
      if (segment.heText) return displayMode !== 'en' || !!segment.enText;
      return !!segment.enText;
    case 'section_intro':
    case 'transition':
    case 'faq':
    case 'commentary':
    case 'insight':
      return displayMode !== 'he';
    default:
      // prayer — Hebrew text, hidden in English-only mode
      return displayMode !== 'en';
  }
}

export function flattenService(service: Service, displayMode: DisplayMode): ListItem[] {
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
      // Segments the current display mode hides are dropped BEFORE optional-run
      // grouping, so a run's box positions (solo/start/mid/end) are computed on
      // what will actually render — otherwise hidden segments leave empty
      // shaded strips or whole empty boxes.
      const segs = prayer.segments.filter((seg) => isSegmentVisible(seg, displayMode));
      // Contiguous runs of optional segments each become their own FlashList item
      // so FlashList measures each one independently (avoids 200px estimate clipping
      // tall groups). Position flag drives the border/radius style so they look like
      // one connected box.
      let i = 0;
      while (i < segs.length) {
        if (segs[i].optional) {
          const run: Segment[] = [];
          while (i < segs.length && segs[i].optional) run.push(segs[i++]);
          run.forEach((seg, idx) => {
            const pos: 'solo' | 'start' | 'mid' | 'end' =
              run.length === 1 ? 'solo'
              : idx === 0 ? 'start'
              : idx === run.length - 1 ? 'end'
              : 'mid';
            items.push({ kind: 'optionalSegment', segment: seg, prayerId: prayer.id, pos });
          });
        } else {
          items.push({ kind: 'segment', segment: segs[i], prayerId: prayer.id });
          i++;
        }
      }
    }
  }
  return items;
}
