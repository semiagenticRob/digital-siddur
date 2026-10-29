import { searchCities, resolveDeviceLocation } from '../location';

// Real shape of https://www.hebcal.com/complete.php?q=thornhill, probed
// 2026-07-02 — NOT the brief's guess. It returns name/id metadata only, no
// coordinates or timezone:
const COMPLETE_RESPONSE = [
  {
    id: 6165682,
    value: 'Thornhill, Nova Scotia, Canada',
    admin1: 'Nova Scotia',
    country: 'Canada',
    cc: 'CA',
    geo: 'geoname',
    asciiname: 'Thornhill',
    flag: '🇨🇦',
  },
];

// Real shape of https://www.hebcal.com/geo?cfg=json&geonameid=6165682,
// probed 2026-07-02 — the second call searchCities makes to resolve each
// candidate's coordinates/timezone.
const GEO_RESPONSE = {
  latitude: 44.60347,
  longitude: -63.61147,
  locationName: 'Thornhill, Nova Scotia, Canada',
  timeZoneId: 'America/Halifax',
  elevation: 60,
  il: false,
  cc: 'CA',
  geoid: 6165682,
  admin1: 'Nova Scotia',
  geo: 'geoname',
  population: 2188,
  asciiname: 'Thornhill',
  geonameid: 6165682,
};

function mockFetchByUrl(handler: (url: string) => { ok: boolean; json: () => Promise<unknown> }) {
  globalThis.fetch = jest.fn(async (url: string) => handler(url)) as unknown as typeof fetch;
}

describe('searchCities', () => {
  test('maps autocomplete hits through the per-hit geo lookup to ZmanimLocation', async () => {
    mockFetchByUrl((url) => {
      if (url.includes('complete.php')) {
        return { ok: true, json: async () => COMPLETE_RESPONSE };
      }
      return { ok: true, json: async () => GEO_RESPONSE };
    });

    const results = await searchCities('thornhill');
    expect(results).toEqual([
      {
        latitude: 44.60347,
        longitude: -63.61147,
        tzid: 'America/Halifax',
        label: 'Thornhill, Nova Scotia, Canada',
      },
    ]);
  });

  test('returns null on network failure', async () => {
    globalThis.fetch = jest.fn(async () => {
      throw new Error('offline');
    }) as unknown as typeof fetch;
    await expect(searchCities('x')).resolves.toBeNull();
  });

  test('drops hits missing id/value from complete.php', async () => {
    mockFetchByUrl((url) => {
      if (url.includes('complete.php')) {
        return { ok: true, json: async () => [{ value: 'Nowhere' }] };
      }
      return { ok: true, json: async () => GEO_RESPONSE };
    });
    await expect(searchCities('nowhere')).resolves.toEqual([]);
  });

  test('drops hits whose geo lookup is missing coordinates or timezone', async () => {
    // Belt-and-braces path: a 200 body with an error / missing fields. (The
    // live API actually 404s on bad ids — covered by the next test.)
    mockFetchByUrl((url) => {
      if (url.includes('complete.php')) {
        return { ok: true, json: async () => COMPLETE_RESPONSE };
      }
      return { ok: true, json: async () => ({ error: "Sorry, can't find geonameid" }) };
    });
    await expect(searchCities('thornhill')).resolves.toEqual([]);
  });

  test('drops a candidate whose geo lookup 404s (invalid geonameid)', async () => {
    // Real behavior probed 2026-07-02: /geo returns HTTP 404 with a JSON
    // error body for an unknown geonameid.
    mockFetchByUrl((url) => {
      if (url.includes('complete.php')) {
        return { ok: true, json: async () => COMPLETE_RESPONSE };
      }
      return { ok: false, json: async () => ({ error: "Sorry, can't find geonameid: 6165682" }) };
    });
    await expect(searchCities('thornhill')).resolves.toEqual([]);
  });

  test('keeps successfully resolved candidates when one geo lookup fails', async () => {
    const THREE_HITS = [
      { id: 111, value: 'Alpha, Country A' },
      { id: 222, value: 'Beta, Country B' },
      { id: 333, value: 'Gamma, Country C' },
    ];
    const geoFor: Record<string, unknown> = {
      '111': { latitude: 1, longitude: 10, timeZoneId: 'Zone/Alpha', locationName: 'Alpha, Country A' },
      '333': { latitude: 3, longitude: 30, timeZoneId: 'Zone/Gamma', locationName: 'Gamma, Country C' },
    };
    mockFetchByUrl((url) => {
      if (url.includes('complete.php')) {
        return { ok: true, json: async () => THREE_HITS };
      }
      const id = url.split('geonameid=')[1];
      if (id === '222') return { ok: false, json: async () => ({ error: 'Not Found' }) };
      return { ok: true, json: async () => geoFor[id] };
    });

    await expect(searchCities('multi')).resolves.toEqual([
      { latitude: 1, longitude: 10, tzid: 'Zone/Alpha', label: 'Alpha, Country A' },
      { latitude: 3, longitude: 30, tzid: 'Zone/Gamma', label: 'Gamma, Country C' },
    ]);
  });

  test('returns null when complete.php responds not-ok (a search failure, not "no results")', async () => {
    mockFetchByUrl(() => ({ ok: false, json: async () => [] }));
    await expect(searchCities('x')).resolves.toBeNull();
  });

  test('slices autocomplete candidates to 6 before the /geo fan-out', async () => {
    const eightHits = Array.from({ length: 8 }, (_, i) => ({ id: i, value: `City ${i}` }));
    const geoCalls: string[] = [];
    mockFetchByUrl((url) => {
      if (url.includes('complete.php')) {
        return { ok: true, json: async () => eightHits };
      }
      geoCalls.push(url);
      const id = url.split('geonameid=')[1];
      return { ok: true, json: async () => ({ latitude: 1, longitude: 1, timeZoneId: 'UTC', locationName: `City ${id}` }) };
    });
    const results = await searchCities('city');
    expect(geoCalls).toHaveLength(6);
    expect(results).toHaveLength(6);
  });
});

jest.mock('expo-location', () => ({
  requestForegroundPermissionsAsync: jest.fn(),
  getCurrentPositionAsync: jest.fn(),
  reverseGeocodeAsync: jest.fn(),
  Accuracy: { Low: 2 },
}));

jest.mock('expo-localization', () => ({
  getCalendars: jest.fn(() => [{ timeZone: 'America/Halifax' }]),
}));

import * as Location from 'expo-location';

describe('resolveDeviceLocation', () => {
  afterEach(() => jest.clearAllMocks());

  test('returns null when permission is denied', async () => {
    (Location.requestForegroundPermissionsAsync as jest.Mock).mockResolvedValue({ status: 'denied' });
    await expect(resolveDeviceLocation()).resolves.toBeNull();
    expect(Location.getCurrentPositionAsync).not.toHaveBeenCalled();
  });

  test('returns a ZmanimLocation with reverse-geocoded city label when granted', async () => {
    (Location.requestForegroundPermissionsAsync as jest.Mock).mockResolvedValue({ status: 'granted' });
    (Location.getCurrentPositionAsync as jest.Mock).mockResolvedValue({
      coords: { latitude: 44.6, longitude: -63.6 },
    });
    (Location.reverseGeocodeAsync as jest.Mock).mockResolvedValue([{ city: 'Thornhill' }]);

    await expect(resolveDeviceLocation()).resolves.toEqual({
      latitude: 44.6,
      longitude: -63.6,
      tzid: 'America/Halifax',
      label: 'Thornhill',
    });
  });

  test('rounds device coordinates to ~1 km before returning (approximate location only)', async () => {
    (Location.requestForegroundPermissionsAsync as jest.Mock).mockResolvedValue({ status: 'granted' });
    (Location.getCurrentPositionAsync as jest.Mock).mockResolvedValue({
      coords: { latitude: 44.603471, longitude: -63.587239 },
    });
    (Location.reverseGeocodeAsync as jest.Mock).mockResolvedValue([{ city: 'Halifax' }]);

    const loc = await resolveDeviceLocation();
    expect(loc).toMatchObject({ latitude: 44.6, longitude: -63.59 });
    expect(Location.reverseGeocodeAsync).toHaveBeenCalledWith({ latitude: 44.6, longitude: -63.59 });
  });

  test('falls back to a generic label when reverse geocoding fails', async () => {
    (Location.requestForegroundPermissionsAsync as jest.Mock).mockResolvedValue({ status: 'granted' });
    (Location.getCurrentPositionAsync as jest.Mock).mockResolvedValue({
      coords: { latitude: 44.6, longitude: -63.6 },
    });
    (Location.reverseGeocodeAsync as jest.Mock).mockRejectedValue(new Error('offline'));

    await expect(resolveDeviceLocation()).resolves.toEqual({
      latitude: 44.6,
      longitude: -63.6,
      tzid: 'America/Halifax',
      label: 'Current location',
    });
  });
});
