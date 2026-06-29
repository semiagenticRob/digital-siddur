import { Dimensions } from 'react-native';

// Horizontal padding the service list applies to its content, on each side.
export const LIST_HORIZONTAL_PAD = 16;

// Concrete content width every list cell and English text block is constrained
// to (screen minus the list's horizontal padding on both sides). FlashList cells
// can size to their own content, so a fixed px width — not '100%' — is what
// forces long single lines to wrap instead of overflowing the right edge. Yoga
// also enforces this as a maxWidth clamp on inner Text. App is portrait-locked
// (app.json), so a static window width read once at module load is safe.
export const CONTENT_WIDTH = Dimensions.get('window').width - LIST_HORIZONTAL_PAD * 2;
