import { listGlossary, glossarySections } from '../glossary';

test('glossary has the full printed entry set', () => {
  const entries = listGlossary();
  expect(entries.length).toBeGreaterThanOrEqual(60);
  const terms = entries.map((e) => e.term);
  expect(terms).toContain('Hashem');
  expect(terms).toContain('bitachon');
  for (const e of entries) {
    expect(e.term).toBeTruthy();
    expect(e.definition).toBeTruthy();
  }
});

test('glossarySections groups by first letter, A→Z, entries in print order', () => {
  const sections = glossarySections();
  const letters = sections.map((s) => s.letter);
  expect(letters).toEqual([...letters].sort());
  for (const section of sections) {
    expect(section.data.length).toBeGreaterThan(0);
    for (const e of section.data) {
      expect(e.term[0].toUpperCase()).toBe(section.letter);
    }
  }
});
