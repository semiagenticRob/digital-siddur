import { Appendix } from './types';
import data from './appendices.json';

const APPENDICES: Appendix[] = (data.appendices as Appendix[]);

export function getAppendix(number: number): Appendix | null {
  return APPENDICES.find((a) => a.number === number) ?? null;
}

export function listAppendices(): Array<{ number: number; title: string }> {
  return APPENDICES.map(({ number, title }) => ({ number, title }));
}
