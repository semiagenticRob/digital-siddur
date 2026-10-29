import { suggestService } from '../suggestService';

const Z = { sunset: '2026-07-02T20:44:00-04:00', minchaGedola: '2026-07-02T13:45:00-04:00' };

test('morning suggests shacharis', () => {
  expect(suggestService(new Date(2026, 6, 2, 7, 30), Z)).toBe('shacharit');
});
test('after minchaGedola suggests minchah', () => {
  expect(suggestService(new Date(2026, 6, 2, 14, 0), Z)).toBe('minchah');
});
test('after shkiah suggests maariv', () => {
  expect(suggestService(new Date(2026, 6, 2, 21, 0), Z)).toBe('maariv');
});
test('Saturday night suggests motzaei-shabbos maariv', () => {
  expect(suggestService(new Date(2026, 6, 4, 22, 0), Z)).toBe('maariv-motzaei-shabbos');
});
test('no zmanim: clock fallback boundaries 13:00 / 19:30', () => {
  expect(suggestService(new Date(2026, 6, 2, 12, 59), null)).toBe('shacharit');
  expect(suggestService(new Date(2026, 6, 2, 13, 1), null)).toBe('minchah');
  expect(suggestService(new Date(2026, 6, 2, 19, 31), null)).toBe('maariv');
});
// 2026-07-03 is a Friday, 2026-07-04 is a Saturday.
test('Friday past the evening boundary has no weekday suggestion', () => {
  expect(suggestService(new Date(2026, 6, 3, 21, 0), Z)).toBeNull();
});
test('Saturday morning has no weekday suggestion', () => {
  expect(suggestService(new Date(2026, 6, 4, 11, 0), Z)).toBeNull();
});
test('Saturday afternoon has no weekday suggestion', () => {
  expect(suggestService(new Date(2026, 6, 4, 14, 0), Z)).toBeNull();
});

// Exact boundaries: each switch happens *at* the zman (>=), not a minute later.
test('switches to minchah exactly at minchaGedola', () => {
  expect(suggestService(new Date(2026, 6, 2, 13, 44), Z)).toBe('shacharit');
  expect(suggestService(new Date(2026, 6, 2, 13, 45), Z)).toBe('minchah');
});
test('switches to maariv exactly at sunset', () => {
  expect(suggestService(new Date(2026, 6, 2, 20, 43), Z)).toBe('minchah');
  expect(suggestService(new Date(2026, 6, 2, 20, 44), Z)).toBe('maariv');
});
test('Friday daytime still suggests weekday services', () => {
  expect(suggestService(new Date(2026, 6, 3, 8, 0), Z)).toBe('shacharit');
  expect(suggestService(new Date(2026, 6, 3, 20, 43), Z)).toBe('minchah');
  expect(suggestService(new Date(2026, 6, 3, 20, 44), Z)).toBeNull();
});
test('Saturday turns to Motzaei Shabbos Maariv exactly at the evening boundary', () => {
  expect(suggestService(new Date(2026, 6, 4, 20, 43), Z)).toBeNull();
  expect(suggestService(new Date(2026, 6, 4, 20, 44), Z)).toBe('maariv-motzaei-shabbos');
});
test('falls back to 13:00 when zmanim lack minchaGedola', () => {
  const sunsetOnly = { sunset: Z.sunset };
  expect(suggestService(new Date(2026, 6, 2, 12, 59), sunsetOnly)).toBe('shacharit');
  expect(suggestService(new Date(2026, 6, 2, 13, 0), sunsetOnly)).toBe('minchah');
});
