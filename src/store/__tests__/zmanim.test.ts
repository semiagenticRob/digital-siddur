import { useZmanimStore, hebcalZmanimUrl, dateKey } from '../zmanim';

const LOC = { latitude: 43.85, longitude: -79.45, tzid: 'America/Toronto', label: 'Thornhill' };

// Minimal Hebcal batch response shape (times keyed by zman, then by date).
const HEBCAL_RESPONSE = {
  times: {
    sofZmanShma: { '2026-07-02': '2026-07-02T09:14:00-04:00', '2026-07-03': '2026-07-03T09:14:00-04:00' },
    minchaGedola: { '2026-07-02': '2026-07-02T13:45:00-04:00', '2026-07-03': '2026-07-03T13:45:00-04:00' },
    sunset: { '2026-07-02': '2026-07-02T20:44:00-04:00', '2026-07-03': '2026-07-03T20:44:00-04:00' },
    tzeit85deg: { '2026-07-02': '2026-07-02T21:26:00-04:00', '2026-07-03': '2026-07-03T21:26:00-04:00' },
  },
};

beforeEach(() => {
  useZmanimStore.setState({ location: null, days: {}, fetchedThrough: null });
  globalThis.fetch = jest.fn(async () => ({ ok: true, json: async () => HEBCAL_RESPONSE })) as any;
});

test('dateKey formats local date without Intl', () => {
  expect(dateKey(new Date(2026, 6, 2))).toBe('2026-07-02');
  expect(dateKey(new Date(2026, 0, 9))).toBe('2026-01-09');
});

test('hebcalZmanimUrl carries location, range, and json cfg', () => {
  const url = hebcalZmanimUrl(LOC, '2026-07-02', '2026-08-01');
  expect(url).toContain('https://www.hebcal.com/zmanim?cfg=json');
  expect(url).toContain('latitude=43.85');
  expect(url).toContain('longitude=-79.45');
  expect(url).toContain('tzid=America%2FToronto');
  expect(url).toContain('start=2026-07-02');
  expect(url).toContain('end=2026-08-01');
});

test('ensureFresh is a no-op without a location', async () => {
  await useZmanimStore.getState().ensureFresh('2026-07-02');
  expect(globalThis.fetch).not.toHaveBeenCalled();
});

test('ensureFresh fetches a batch and indexes it by date', async () => {
  useZmanimStore.getState().setLocation(LOC);
  await useZmanimStore.getState().ensureFresh('2026-07-02');
  expect(globalThis.fetch).toHaveBeenCalledTimes(1);
  const day = useZmanimStore.getState().zmanimFor('2026-07-02');
  expect(day?.sunset).toBe('2026-07-02T20:44:00-04:00');
  expect(useZmanimStore.getState().fetchedThrough).toBe('2026-07-03');
});

test('ensureFresh skips fetch while >=7 days of cache remain', async () => {
  useZmanimStore.getState().setLocation(LOC);
  useZmanimStore.setState({ fetchedThrough: '2026-07-20' });
  await useZmanimStore.getState().ensureFresh('2026-07-02');
  expect(globalThis.fetch).not.toHaveBeenCalled();
});

test('ensureFresh swallows network errors and keeps existing cache', async () => {
  useZmanimStore.getState().setLocation(LOC);
  useZmanimStore.setState({ days: { '2026-07-02': HEBCAL_RESPONSE.times as any } as any });
  (globalThis.fetch as jest.Mock).mockRejectedValueOnce(new Error('offline'));
  await expect(useZmanimStore.getState().ensureFresh('2026-07-02')).resolves.toBeUndefined();
});

test('setLocation clears the previous cache', () => {
  useZmanimStore.setState({ days: { '2026-07-02': {} as any }, fetchedThrough: '2026-07-31' });
  useZmanimStore.getState().setLocation(LOC);
  expect(useZmanimStore.getState().days).toEqual({});
  expect(useZmanimStore.getState().fetchedThrough).toBeNull();
});
