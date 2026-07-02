import * as Location from 'expo-location';
import * as Localization from 'expo-localization';
import { ZmanimLocation } from '../store/zmanim';

// Device timezone: no clear doc statement in the Expo SDK 56 / Hermes docs
// confirms bare Intl.DateTimeFormat().resolvedOptions().timeZone is supported
// on both iOS and Android, so we use expo-localization's getCalendars()
// (the SDK's own documented API for this) instead. See task report for the
// research trail.
function deviceTzid(): string {
  try {
    return Localization.getCalendars()[0]?.timeZone ?? 'UTC';
  } catch {
    return 'UTC';
  }
}

// Device path: when-in-use permission -> coarse position -> reverse-geocoded
// city label. Returns null on any denial/failure — callers fall back to
// manual city search. Never throws.
export async function resolveDeviceLocation(): Promise<ZmanimLocation | null> {
  try {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') return null;
    const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Low });
    const tzid = deviceTzid();
    let label = 'Current location';
    try {
      const places = await Location.reverseGeocodeAsync(pos.coords);
      const p = places[0];
      if (p?.city) label = p.city;
    } catch {
      // keep generic label
    }
    return { latitude: pos.coords.latitude, longitude: pos.coords.longitude, tzid, label };
  } catch {
    return null;
  }
}

// Manual fallback: Hebcal's public city autocomplete (same source as
// hebcal.com's own search box).
//
// Shape verified by probe on 2026-07-02 — differs from the brief's guess:
// `complete.php` returns only name/id metadata, NOT coordinates or a
// timezone:
//   [{ id, value, admin1, country, cc, geo, asciiname, flag }, ...]
// Resolving lat/lon/tzid requires a second call per hit, to Hebcal's geoname
// lookup:
//   https://www.hebcal.com/geo?cfg=json&geonameid=<id>
//   -> { latitude, longitude, timeZoneId, locationName, ... }
// So searchCities does complete.php then fans out one geo lookup per
// candidate (typically <= 12) in parallel, dropping any hit whose geo lookup
// fails or omits coordinates/timezone.
interface CompleteHit {
  id?: number;
  value?: string;
}

interface GeoResult {
  latitude?: number;
  longitude?: number;
  timeZoneId?: string;
  locationName?: string;
  error?: string;
}

async function resolveGeonameId(id: number, fallbackLabel: string): Promise<ZmanimLocation | null> {
  try {
    const res = await fetch(`https://www.hebcal.com/geo?cfg=json&geonameid=${id}`);
    if (!res.ok) return null;
    const geo = (await res.json()) as GeoResult | null;
    if (
      !geo ||
      geo.error ||
      typeof geo.latitude !== 'number' ||
      typeof geo.longitude !== 'number' ||
      !geo.timeZoneId
    ) {
      return null;
    }
    return {
      latitude: geo.latitude,
      longitude: geo.longitude,
      tzid: geo.timeZoneId,
      label: geo.locationName ?? fallbackLabel,
    };
  } catch {
    return null;
  }
}

export async function searchCities(query: string): Promise<ZmanimLocation[]> {
  try {
    const res = await fetch(`https://www.hebcal.com/complete.php?q=${encodeURIComponent(query)}`);
    if (!res.ok) return [];
    const hits = (await res.json()) as CompleteHit[];
    if (!Array.isArray(hits)) return [];
    const candidates = hits.filter(
      (h): h is Required<CompleteHit> => typeof h.id === 'number' && typeof h.value === 'string'
    );
    const resolved = await Promise.all(
      candidates.map((h) => resolveGeonameId(h.id, h.value))
    );
    return resolved.filter((loc): loc is ZmanimLocation => loc !== null);
  } catch {
    return [];
  }
}
