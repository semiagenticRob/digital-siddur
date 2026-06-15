import { hebrewFontSize, englishFontSize, BASE_HE_SIZE } from '../typography';

test('hebrewFontSize at step 0 equals BASE_HE_SIZE', () => {
  expect(hebrewFontSize(0)).toBeCloseTo(BASE_HE_SIZE);
});

test('hebrewFontSize increases with positive step', () => {
  expect(hebrewFontSize(2)).toBeGreaterThan(hebrewFontSize(0));
});

test('hebrewFontSize decreases with negative step', () => {
  expect(hebrewFontSize(-1)).toBeLessThan(hebrewFontSize(0));
});

test('englishFontSize at step 0 is between 14 and 16', () => {
  const size = englishFontSize(0);
  expect(size).toBeGreaterThan(14);
  expect(size).toBeLessThan(16);
});

test('englishFontSize scales with fontStep', () => {
  expect(englishFontSize(2)).toBeGreaterThan(englishFontSize(0));
});
