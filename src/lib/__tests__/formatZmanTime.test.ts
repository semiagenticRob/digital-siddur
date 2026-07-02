import { formatZmanTime } from '../formatZmanTime';

test('morning time drops leading zero', () => {
  expect(formatZmanTime('2026-07-02T09:14:00-04:00')).toBe('9:14');
});
test('afternoon time converts to 12-hour', () => {
  expect(formatZmanTime('2026-07-02T13:45:00-04:00')).toBe('1:45');
});
test('midnight hour maps to 12', () => {
  expect(formatZmanTime('2026-07-02T00:05:00-04:00')).toBe('12:05');
});
test('noon hour stays 12', () => {
  expect(formatZmanTime('2026-07-02T12:30:00-04:00')).toBe('12:30');
});
