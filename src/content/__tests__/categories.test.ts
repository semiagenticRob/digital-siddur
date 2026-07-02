import { HOME_CATEGORIES, homeSections } from '../categories';
import { listServices } from '../loader';

test('every registered service appears in exactly one category', () => {
  const all = HOME_CATEGORIES.flatMap((c) => c.serviceIds);
  expect(new Set(all).size).toBe(all.length); // no duplicates
  expect(new Set(all)).toEqual(new Set(listServices().map((s) => s.id))); // full coverage
});

test('homeSections resolves every id to real titles, preserving category order', () => {
  const sections = homeSections();
  expect(sections.map((s) => s.key)).toEqual(['tefillos', 'special', 'after-eating', 'anytime']);
  for (const section of sections) {
    for (const item of section.data) {
      expect(item.enTitle).toBeTruthy();
      expect(item.heTitle).toBeTruthy();
    }
  }
  expect(sections[0].data.map((i) => i.id)).toEqual(['shacharit', 'minchah', 'maariv']);
});
