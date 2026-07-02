import { listServices, getService } from './loader';

// Reverse lookup segmentId → where it lives, for surfaces that start from an
// annotation (highlights/notes list) and need to show context and jump back.
// Built lazily once — the content registry is static.
export interface SegmentLocation {
  serviceId: string;
  serviceTitle: string;
  prayerId: string;
  prayerHeTitle: string;
  prayerEnTitle: string;
  heText: string;
}

let index: Map<string, SegmentLocation> | null = null;

export function locateSegment(segmentId: string): SegmentLocation | undefined {
  if (!index) {
    index = new Map();
    for (const summary of listServices()) {
      const service = getService(summary.id);
      if (!service) continue;
      for (const group of service.groups) {
        for (const prayer of group.prayers) {
          for (const seg of prayer.segments) {
            index.set(seg.id, {
              serviceId: service.id,
              serviceTitle: service.enTitle,
              prayerId: prayer.id,
              prayerHeTitle: prayer.heTitle,
              prayerEnTitle: prayer.enTitle,
              heText: seg.heText ?? '',
            });
          }
        }
      }
    }
  }
  return index.get(segmentId);
}
