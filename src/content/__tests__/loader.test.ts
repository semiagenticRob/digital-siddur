import { getService, listServices } from '../loader';

test('getService returns shacharit', () => {
  const s = getService('shacharit');
  expect(s).not.toBeNull();
  expect(s!.id).toBe('shacharit');
  expect(s!.groups.length).toBeGreaterThan(0);
});

test('getService returns null for unknown id', () => {
  expect(getService('does-not-exist')).toBeNull();
});

test('listServices includes shacharit', () => {
  const list = listServices();
  expect(list.some(s => s.id === 'shacharit')).toBe(true);
});

test('listServices returns 4 services', () => {
  expect(listServices()).toHaveLength(4);
});

test('shacharit has segments with heText', () => {
  const s = getService('shacharit');
  const allSegments = s!.groups.flatMap(g => g.prayers.flatMap(p => p.segments));
  const prayerSegments = allSegments.filter(seg => seg.type === 'prayer');
  expect(prayerSegments.every(seg => seg.heText && seg.heText.length > 0)).toBe(true);
});
