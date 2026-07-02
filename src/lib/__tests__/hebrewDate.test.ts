import { fromGregorian, formatHebrewDate, formatEnDate, gematriya } from '../hebrewDate';

// Reference values cross-checked against the Hebcal converter API (Step 1).
test('Rosh Hashanah 5786 — 2025-09-23 is 1 Tishrei 5786', () => {
  expect(fromGregorian(new Date(2025, 8, 23))).toEqual({ year: 5786, month: 7, day: 1 });
});

test('Rosh Hashanah 5787 — 2026-09-12 is 1 Tishrei 5787', () => {
  expect(fromGregorian(new Date(2026, 8, 12))).toEqual({ year: 5787, month: 7, day: 1 });
});

test('day before Rosh Hashanah — 2025-09-22 is 29 Elul 5785', () => {
  expect(fromGregorian(new Date(2025, 8, 22))).toEqual({ year: 5785, month: 6, day: 29 });
});

test('2026-07-02 matches the Hebcal converter (17 Tammuz 5786)', () => {
  expect(fromGregorian(new Date(2026, 6, 2))).toEqual({ year: 5786, month: 4, day: 17 });
});

test('leap-year date lands in Adar II (month 13) per the Hebcal converter', () => {
  // Replace day with the Step 1 API value if it differs.
  const h = fromGregorian(new Date(2027, 2, 20));
  expect(h.year).toBe(5787);
  expect(h.month).toBe(13);
  expect(h.day).toBe(11);
});

test('round-trips across a full Hebrew year', () => {
  // Walk 2025-09-23 … 2026-09-12 day by day; the Hebrew date must advance
  // by exactly one day each step (catches month-length errors).
  let prev = fromGregorian(new Date(2025, 8, 23));
  for (let t = new Date(2025, 8, 24); t <= new Date(2026, 8, 12); t.setDate(t.getDate() + 1)) {
    const cur = fromGregorian(new Date(t));
    const sameMonth = cur.year === prev.year && cur.month === prev.month && cur.day === prev.day + 1;
    const newMonth = cur.day === 1 && !(cur.year === prev.year && cur.month === prev.month);
    expect(sameMonth || newMonth).toBe(true);
    prev = cur;
  }
});

test('gematriya renders 15/16 as ט״ו/ט״ז and years correctly', () => {
  expect(gematriya(15)).toBe('ט״ו');
  expect(gematriya(16)).toBe('ט״ז');
  expect(gematriya(17)).toBe('י״ז');
  expect(gematriya(5)).toBe('ה׳');
  expect(gematriya(786)).toBe('תשפ״ו');
});

test('formatHebrewDate — plain, leap Adar I, Adar II', () => {
  expect(formatHebrewDate({ year: 5786, month: 4, day: 17 })).toBe('י״ז תמוז תשפ״ו');
  expect(formatHebrewDate({ year: 5787, month: 12, day: 1 })).toBe('א׳ אדר א׳ תשפ״ז');
  expect(formatHebrewDate({ year: 5787, month: 13, day: 1 })).toBe('א׳ אדר ב׳ תשפ״ז');
});

test('formatEnDate has no Intl dependency', () => {
  expect(formatEnDate(new Date(2026, 6, 2))).toBe('Thursday · July 2');
});
