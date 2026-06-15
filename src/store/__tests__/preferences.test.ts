import { usePreferencesStore, COMFORT_PRESETS } from '../preferences';

// Reset store between tests to avoid state bleed
beforeEach(() => {
  usePreferencesStore.setState({
    displayMode: 'both',
    theme: 'auto',
    fontStep: 0,
    comfortLevel: 'comfortable',
    hasCompletedOnboarding: false,
  });
});

test('default displayMode is both', () => {
  expect(usePreferencesStore.getState().displayMode).toBe('both');
});

test('setDisplayMode updates the value', () => {
  usePreferencesStore.getState().setDisplayMode('he');
  expect(usePreferencesStore.getState().displayMode).toBe('he');
});

test('fontStep clamps to max 4', () => {
  usePreferencesStore.getState().bumpFontStep(10);
  expect(usePreferencesStore.getState().fontStep).toBe(4);
});

test('fontStep clamps to min -2', () => {
  usePreferencesStore.getState().bumpFontStep(-20);
  expect(usePreferencesStore.getState().fontStep).toBe(-2);
});

test('default theme is auto', () => {
  expect(usePreferencesStore.getState().theme).toBe('auto');
});

test('completeOnboarding sets hasCompletedOnboarding true', () => {
  usePreferencesStore.getState().completeOnboarding();
  expect(usePreferencesStore.getState().hasCompletedOnboarding).toBe(true);
});

test('COMFORT_PRESETS beginner sets displayMode both', () => {
  expect(COMFORT_PRESETS.beginner.displayMode).toBe('both');
});

test('COMFORT_PRESETS fluent sets displayMode he', () => {
  expect(COMFORT_PRESETS.fluent.displayMode).toBe('he');
});
