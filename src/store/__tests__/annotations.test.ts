import { useAnnotationsStore } from '../annotations';

beforeEach(() => {
  useAnnotationsStore.setState({
    highlights: new Set<string>(),
    notes: {},
  });
});

test('no highlights initially', () => {
  expect(useAnnotationsStore.getState().isHighlighted('seg-1')).toBe(false);
});

test('toggleHighlight adds a highlight', () => {
  useAnnotationsStore.getState().toggleHighlight('seg-1');
  expect(useAnnotationsStore.getState().isHighlighted('seg-1')).toBe(true);
});

test('toggleHighlight removes an existing highlight', () => {
  useAnnotationsStore.getState().toggleHighlight('seg-1');
  useAnnotationsStore.getState().toggleHighlight('seg-1');
  expect(useAnnotationsStore.getState().isHighlighted('seg-1')).toBe(false);
});

test('addNote stores text for a segment', () => {
  useAnnotationsStore.getState().addNote('seg-2', 'My note');
  expect(useAnnotationsStore.getState().getNotes('seg-2')).toEqual(['My note']);
});

test('addNote appends multiple notes', () => {
  useAnnotationsStore.getState().addNote('seg-3', 'First');
  useAnnotationsStore.getState().addNote('seg-3', 'Second');
  expect(useAnnotationsStore.getState().getNotes('seg-3')).toHaveLength(2);
});

test('getNotes returns empty array for unknown segment', () => {
  expect(useAnnotationsStore.getState().getNotes('unknown')).toEqual([]);
});

test('removeNote deletes one note by index and keeps the rest', () => {
  useAnnotationsStore.getState().addNote('seg-4', 'First');
  useAnnotationsStore.getState().addNote('seg-4', 'Second');
  useAnnotationsStore.getState().removeNote('seg-4', 0);
  expect(useAnnotationsStore.getState().getNotes('seg-4')).toEqual(['Second']);
});

test('removeNote drops the segment key when its last note is removed', () => {
  useAnnotationsStore.getState().addNote('seg-5', 'Only');
  useAnnotationsStore.getState().removeNote('seg-5', 0);
  expect(useAnnotationsStore.getState().getNotes('seg-5')).toEqual([]);
  expect(useAnnotationsStore.getState().notes).not.toHaveProperty('seg-5');
});

test('removeNote with an out-of-range index is a no-op', () => {
  useAnnotationsStore.getState().addNote('seg-6', 'Keep me');
  useAnnotationsStore.getState().removeNote('seg-6', 5);
  expect(useAnnotationsStore.getState().getNotes('seg-6')).toEqual(['Keep me']);
});
