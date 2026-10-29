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

test('ensureFresh keeps existing cache when a batch entry is missing a zman key', async () => {
  useZmanimStore.getState().setLocation(LOC);
  const priorDays = { '2026-07-01': {
    sofZmanShma: '2026-07-01T09:14:00-04:00',
    minchaGedola: '2026-07-01T13:45:00-04:00',
    sunset: '2026-07-01T20:44:00-04:00',
    tzeit85deg: '2026-07-01T21:26:00-04:00',
  } };
  useZmanimStore.setState({ days: priorDays, fetchedThrough: '2026-07-01' });
  const partial = {
    times: {
      sofZmanShma: { '2026-07-02': '2026-07-02T09:14:00-04:00', '2026-07-03': '2026-07-03T09:14:00-04:00' },
      minchaGedola: { '2026-07-02': '2026-07-02T13:45:00-04:00', '2026-07-03': '2026-07-03T13:45:00-04:00' },
      sunset: { '2026-07-02': '2026-07-02T20:44:00-04:00', '2026-07-03': '2026-07-03T20:44:00-04:00' },
      tzeit85deg: { '2026-07-02': '2026-07-02T21:26:00-04:00' }, // missing for 2026-07-03
    },
  };
  (globalThis.fetch as jest.Mock).mockResolvedValueOnce({ ok: true, json: async () => partial });
  await useZmanimStore.getState().ensureFresh('2026-07-02');
  expect(useZmanimStore.getState().days).toEqual(priorDays);
  expect(useZmanimStore.getState().fetchedThrough).toBe('2026-07-01');
});

test('ensureFresh keeps fetchedThrough when the batch times are empty', async () => {
  useZmanimStore.getState().setLocation(LOC);
  useZmanimStore.setState({ fetchedThrough: '2026-07-01' });
  (globalThis.fetch as jest.Mock).mockResolvedValueOnce({ ok: true, json: async () => ({ times: {} }) });
  await useZmanimStore.getState().ensureFresh('2026-07-02');
  expect(useZmanimStore.getState().fetchedThrough).toBe('2026-07-01');
  expect(useZmanimStore.getState().days).toEqual({});
});

test('ensureFresh ignores a stale response after the location changed mid-fetch', async () => {
  useZmanimStore.getState().setLocation(LOC);
  let resolveFetch!: (value: unknown) => void;
  const pending = new Promise((resolve) => {
    resolveFetch = resolve;
  });
  (globalThis.fetch as jest.Mock).mockReturnValueOnce(pending);

  const ensurePromise = useZmanimStore.getState().ensureFresh('2026-07-02');

  const LOC_B = { latitude: 40.7, longitude: -74.0, tzid: 'America/New_York', label: 'NYC' };
  useZmanimStore.getState().setLocation(LOC_B);

  resolveFetch({ ok: true, json: async () => HEBCAL_RESPONSE });
  await ensurePromise;

  expect(useZmanimStore.getState().days).toEqual({});
  expect(useZmanimStore.getState().fetchedThrough).toBeNull();
});

test('ensureFresh prunes cached days older than todayKey on a successful fetch', async () => {
  useZmanimStore.getState().setLocation(LOC);
  const staleDay = {
    sofZmanShma: '2026-06-30T09:14:00-04:00',
    minchaGedola: '2026-06-30T13:45:00-04:00',
    sunset: '2026-06-30T20:44:00-04:00',
    tzeit85deg: '2026-06-30T21:26:00-04:00',
  };
  useZmanimStore.setState({ days: { '2026-06-30': staleDay }, fetchedThrough: '2026-06-30' });
  await useZmanimStore.getState().ensureFresh('2026-07-02');
  const days = useZmanimStore.getState().days;
  expect(days['2026-06-30']).toBeUndefined();
  expect(days['2026-07-02']).toBeDefined();
  expect(days['2026-07-03']).toBeDefined();
});

test('setLocation clears the previous cache', () => {
  useZmanimStore.setState({ days: { '2026-07-02': {} as any }, fetchedThrough: '2026-07-31' });
  useZmanimStore.getState().setLocation(LOC);
  expect(useZmanimStore.getState().days).toEqual({});
  expect(useZmanimStore.getState().fetchedThrough).toBeNull();
});

test('overlapping ensureFresh calls for the same location share one fetch', async () => {
  useZmanimStore.getState().setLocation(LOC);
  await Promise.all([
    useZmanimStore.getState().ensureFresh('2026-07-02'),
    useZmanimStore.getState().ensureFresh('2026-07-02'),
    useZmanimStore.getState().ensureFresh('2026-07-02'),
  ]);
  expect(globalThis.fetch).toHaveBeenCalledTimes(1);
});

test('a location switch mid-fetch still starts a fetch for the new location', async () => {
  useZmanimStore.getState().setLocation(LOC);
  let resolveFetch!: (value: unknown) => void;
  (globalThis.fetch as jest.Mock).mockReturnValueOnce(new Promise((r) => { resolveFetch = r; }));
  const first = useZmanimStore.getState().ensureFresh('2026-07-02');

  const LOC_B = { latitude: 40.7, longitude: -74.0, tzid: 'America/New_York', label: 'NYC' };
  useZmanimStore.getState().setLocation(LOC_B);
  const second = useZmanimStore.getState().ensureFresh('2026-07-02');

  resolveFetch({ ok: true, json: async () => HEBCAL_RESPONSE });
  await Promise.all([first, second]);
  expect(globalThis.fetch).toHaveBeenCalledTimes(2);
  expect((globalThis.fetch as jest.Mock).mock.calls[1][0]).toContain('latitude=40.7');
  expect(useZmanimStore.getState().fetchedThrough).toBe('2026-07-03');
});
