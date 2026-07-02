import { listBookPieces, getBookPiece } from '../bookMatter';

test('listBookPieces returns exactly the six pieces the About TOC hard-codes', () => {
  expect(listBookPieces().map((p) => p.id)).toEqual([
    'intro-teens',
    'translation-note',
    'intro-parents',
    'personal-notes',
    'dedications',
    'acknowledgments',
  ]);
});

test('every book piece has a nonempty title and nonempty segments', () => {
  for (const { id } of listBookPieces()) {
    const piece = getBookPiece(id);
    expect(piece).not.toBeNull();
    expect(piece!.title.trim().length).toBeGreaterThan(0);
    expect(piece!.segments.length).toBeGreaterThan(0);
  }
});
