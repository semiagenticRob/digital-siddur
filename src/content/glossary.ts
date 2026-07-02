import data from './glossary.json';

export interface GlossaryEntry {
  term: string;
  definition: string;
}

const ENTRIES: GlossaryEntry[] = (data as { entries: GlossaryEntry[] }).entries;

export function listGlossary(): GlossaryEntry[] {
  return ENTRIES;
}

// Letter groups for the browsable screen; print order kept within a letter.
export function glossarySections(): Array<{ letter: string; data: GlossaryEntry[] }> {
  const byLetter = new Map<string, GlossaryEntry[]>();
  for (const e of ENTRIES) {
    const letter = e.term[0].toUpperCase();
    if (!byLetter.has(letter)) byLetter.set(letter, []);
    byLetter.get(letter)!.push(e);
  }
  return [...byLetter.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([letter, data]) => ({ letter, data }));
}
