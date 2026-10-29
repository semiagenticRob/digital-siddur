import { flattenService, isSegmentVisible, ListItem } from '../flattenService';
import type { Service, Segment } from '../../content/types';

const seg = (over: Partial<Segment> & { id: string; type: Segment['type'] }): Segment =>
  ({ ...over } as Segment);

const service = (segments: Segment[]): Service =>
  ({
    id: 'svc',
    heTitle: 'עברית',
    enTitle: 'Test',
    groups: [
      {
        id: 'g1',
        title: 'Group',
        prayers: [{ id: 'p1', heTitle: 'תפילה', enTitle: 'Prayer', segments }],
      },
    ],
  } as Service);

const kinds = (items: ListItem[]) => items.map((i) => i.kind);
const optPositions = (items: ListItem[]) =>
  items.filter((i) => i.kind === 'optionalSegment').map((i) => (i as any).pos);

describe('isSegmentVisible', () => {
  it('hides prayer in en mode, shows in he/both', () => {
    const p = seg({ id: 'a', type: 'prayer', heText: 'שלום' });
    expect(isSegmentVisible(p, 'en')).toBe(false);
    expect(isSegmentVisible(p, 'he')).toBe(true);
    expect(isSegmentVisible(p, 'both')).toBe(true);
  });

  it('hides English-only content types in he mode', () => {
    for (const type of ['commentary', 'insight', 'faq', 'section_intro', 'transition'] as const) {
      const c = seg({ id: 'a', type, enText: 'x' });
      expect(isSegmentVisible(c, 'he')).toBe(false);
      expect(isSegmentVisible(c, 'both')).toBe(true);
      expect(isSegmentVisible(c, 'en')).toBe(true);
    }
  });

  it('always shows English-only rubrics (instructions never hide)', () => {
    const r = seg({ id: 'a', type: 'rubric', enText: 'For men:' });
    expect(isSegmentVisible(r, 'he')).toBe(true);
    expect(isSegmentVisible(r, 'both')).toBe(true);
    expect(isSegmentVisible(r, 'en')).toBe(true);
  });

  it('hides Hebrew-only rubrics in en mode only', () => {
    const r = seg({ id: 'a', type: 'rubric', heText: 'ג״פ' });
    expect(isSegmentVisible(r, 'en')).toBe(false);
    expect(isSegmentVisible(r, 'he')).toBe(true);
    expect(isSegmentVisible(r, 'both')).toBe(true);
  });

  it('shows bilingual rubrics in every mode', () => {
    const r = seg({ id: 'a', type: 'rubric', heText: 'ג״פ', enText: 'Say 3 times' });
    expect(isSegmentVisible(r, 'en')).toBe(true);
    expect(isSegmentVisible(r, 'he')).toBe(true);
  });

  it('hides a header when neither of its fields would render', () => {
    const heOnly = seg({ id: 'a', type: 'header', heText: 'קדושה' });
    expect(isSegmentVisible(heOnly, 'en')).toBe(false);
    expect(isSegmentVisible(heOnly, 'he')).toBe(true);
    const enOnly = seg({ id: 'b', type: 'header', enText: 'OUR REQUESTS' });
    expect(isSegmentVisible(enOnly, 'he')).toBe(false);
    expect(isSegmentVisible(enOnly, 'en')).toBe(true);
  });
});

describe('flattenService', () => {
  it('always emits the prayer header', () => {
    const items = flattenService(service([]), 'both');
    expect(kinds(items)).toEqual(['prayerHeader']);
  });

  it('keeps everything in both mode', () => {
    const items = flattenService(
      service([
        seg({ id: 'a', type: 'prayer', heText: 'א' }),
        seg({ id: 'b', type: 'commentary', enText: 'x' }),
      ]),
      'both'
    );
    expect(kinds(items)).toEqual(['prayerHeader', 'segment', 'segment']);
  });

  it('drops an all-commentary optional run in he mode (no empty box)', () => {
    const items = flattenService(
      service([
        seg({ id: 'a', type: 'commentary', enText: 'x', optional: true }),
        seg({ id: 'b', type: 'commentary', enText: 'y', optional: true }),
      ]),
      'he'
    );
    expect(kinds(items)).toEqual(['prayerHeader']);
  });

  it('drops optional prayers in en mode (no empty box)', () => {
    const items = flattenService(
      service([seg({ id: 'a', type: 'prayer', heText: 'א', optional: true })]),
      'en'
    );
    expect(kinds(items)).toEqual(['prayerHeader']);
  });

  it('recomputes optional-run positions after filtering', () => {
    // he mode: the two commentaries vanish; the lone prayer must become "solo",
    // not keep its original "mid" position.
    const run = [
      seg({ id: 'a', type: 'commentary', enText: 'x', optional: true }),
      seg({ id: 'b', type: 'prayer', heText: 'א', optional: true }),
      seg({ id: 'c', type: 'commentary', enText: 'y', optional: true }),
    ];
    expect(optPositions(flattenService(service(run), 'he'))).toEqual(['solo']);
    expect(optPositions(flattenService(service(run), 'both'))).toEqual(['start', 'mid', 'end']);
  });

  it('splits a run when a hidden segment was the only bridge between two halves', () => {
    // A non-optional commentary sits between two optional prayers. In he mode the
    // commentary is filtered out, so the optional prayers become ADJACENT and
    // merge into one two-item run (start/end).
    const segs = [
      seg({ id: 'a', type: 'prayer', heText: 'א', optional: true }),
      seg({ id: 'b', type: 'commentary', enText: 'x' }),
      seg({ id: 'c', type: 'prayer', heText: 'ב', optional: true }),
    ];
    expect(optPositions(flattenService(service(segs), 'both'))).toEqual(['solo', 'solo']);
    expect(optPositions(flattenService(service(segs), 'he'))).toEqual(['start', 'end']);
  });

  it('keeps English-only rubrics inside optional runs in he mode', () => {
    const items = flattenService(
      service([
        seg({ id: 'a', type: 'rubric', enText: 'Omit on Rosh Chodesh', optional: true }),
        seg({ id: 'b', type: 'prayer', heText: 'א', optional: true }),
      ]),
      'he'
    );
    expect(optPositions(items)).toEqual(['start', 'end']);
  });
});

describe('annotated prayer lines in English-only mode', () => {
  const prayer = { id: 'p1', type: 'prayer', heText: 'בָּרוּךְ' } as Segment;

  test('stay visible when highlighted or noted', () => {
    expect(isSegmentVisible(prayer, 'en', () => true)).toBe(true);
  });

  test('stay hidden when not annotated', () => {
    expect(isSegmentVisible(prayer, 'en', () => false)).toBe(false);
    expect(isSegmentVisible(prayer, 'en')).toBe(false);
  });

  test('flattenService keeps only the annotated prayer line', () => {
    const service = {
      id: 's', heTitle: '', enTitle: '',
      groups: [{ title: 'g', prayers: [{ id: 'pr', heTitle: '', enTitle: '', segments: [
        prayer,
        { id: 'p2', type: 'prayer', heText: 'אַתָּה' } as Segment,
      ] }] }],
    } as unknown as Service;
    const ids = flattenService(service, 'en', (id) => id === 'p1').flatMap((i) =>
      i.kind === 'prayerHeader' ? [] : [i.segment.id]
    );
    expect(ids).toEqual(['p1']);
  });
});
