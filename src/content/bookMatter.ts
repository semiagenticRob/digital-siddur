import { BookPiece } from './types';
import data from './book-matter.json';

const PIECES: BookPiece[] = (data as { pieces: BookPiece[] }).pieces;

export function getBookPiece(id: string): BookPiece | null {
  return PIECES.find((p) => p.id === id) ?? null;
}

export function listBookPieces(): Array<{ id: string; title: string; subtitle?: string }> {
  return PIECES.map(({ id, title, subtitle }) => ({ id, title, subtitle }));
}
