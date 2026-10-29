import { getService, listServices } from '../loader';
import { locateSegment } from '../segmentIndex';

// Highlights and notes are keyed by segment id alone, and locateSegment maps an
// id back to exactly one place. A duplicate id cross-links annotations between
// two prayers, so ids must be unique across every service.
test('segment ids are unique across all services', () => {
  const seen = new Map<string, string>();
  const dupes: string[] = [];
  for (const { id: serviceId } of listServices()) {
    const service = getService(serviceId)!;
    for (const group of service.groups) {
      for (const prayer of group.prayers) {
        for (const seg of prayer.segments) {
          const where = `${serviceId}/${prayer.id}`;
          const prev = seen.get(seg.id);
          if (prev) dupes.push(`${seg.id}: ${prev} and ${where}`);
          else seen.set(seg.id, where);
        }
      }
    }
  }
  expect(dupes).toEqual([]);
});

test('locateSegment maps an id back to its service and prayer', () => {
  expect(locateSegment('birkas-kohanim-prayer')).toMatchObject({
    serviceId: 'shacharit',
    prayerId: 'p-birchos-hatorah',
  });
  expect(locateSegment('minchah-birkas-kohanim-prayer')).toMatchObject({
    serviceId: 'minchah',
    prayerId: 'p-shemoneh-esrei-minchah',
  });
  expect(locateSegment('baruch_shem')).toMatchObject({ prayerId: 'p-birchos-krias-shema' });
  expect(locateSegment('tefillin-baruch-shem')).toMatchObject({ prayerId: 'p-hanachas-tefillin' });
});

test('locateSegment returns undefined for an unknown id', () => {
  expect(locateSegment('no-such-segment')).toBeUndefined();
});
