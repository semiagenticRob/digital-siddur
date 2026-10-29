import React, { useEffect, useRef, useState } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet } from 'react-native';
import { ZmanimLocation } from '../store/zmanim';
import { searchCities } from '../lib/location';
import { ColorPalette } from '../theme/colors';
import { Fonts } from '../theme/typography';

const SEARCH_DEBOUNCE_MS = 350;

interface CitySearchProps {
  colors: ColorPalette;
  onSelect: (loc: ZmanimLocation) => void;
  // Settings uses this to clear its "couldn't locate you" error as soon as
  // the user starts typing; the query itself lives in here, so the parent
  // can't watch it directly.
  onQueryChange?: () => void;
}

export function CitySearch({ colors, onSelect, onQueryChange }: CitySearchProps) {
  const s = makeStyles(colors);
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<ZmanimLocation[]>([]);
  const [searched, setSearched] = useState(false);
  const [searchFailed, setSearchFailed] = useState(false);
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const searchSeq = useRef(0);

  // On unmount: cancel the pending debounce timer, and bump the seq so any
  // in-flight searchCities response is dropped by the stale-guard instead of
  // calling setState on an unmounted component.
  useEffect(() => () => {
    if (searchTimer.current) clearTimeout(searchTimer.current);
    searchSeq.current += 1;
  }, []);

  const handleQueryChange = (text: string) => {
    setQuery(text);
    onQueryChange?.();
    if (searchTimer.current) clearTimeout(searchTimer.current);
    const trimmed = text.trim();
    if (!trimmed) {
      setResults([]);
      setSearching(false);
      setSearched(false);
      setSearchFailed(false);
      return;
    }
    setSearching(true);
    setSearched(false);
    setSearchFailed(false);
    const seq = ++searchSeq.current;
    searchTimer.current = setTimeout(async () => {
      try {
        const hits = await searchCities(trimmed);
        if (seq !== searchSeq.current) return; // stale — a newer search superseded this one
        setResults(hits ?? []);
        setSearchFailed(hits === null);
      } catch {
        if (seq !== searchSeq.current) return;
        setResults([]);
        setSearchFailed(true);
      } finally {
        if (seq === searchSeq.current) {
          setSearching(false);
          setSearched(true);
        }
      }
    }, SEARCH_DEBOUNCE_MS);
  };

  const handleSelect = (loc: ZmanimLocation) => {
    // Cancel the pending debounce and retire the seq so a response that is
    // still in flight can't repopulate the list we're about to clear.
    if (searchTimer.current) clearTimeout(searchTimer.current);
    searchSeq.current += 1;
    setQuery('');
    setResults([]);
    setSearching(false);
    setSearched(false);
    setSearchFailed(false);
    onSelect(loc);
  };

  return (
    <View>
      <TextInput
        style={[s.cityInput, { backgroundColor: colors.surface, borderColor: colors.line, color: colors.ink }]}
        value={query}
        onChangeText={handleQueryChange}
        placeholder="Search for a city…"
        placeholderTextColor={colors.muted}
        accessibilityLabel="Search for a city"
      />

      {searching && (
        <Text style={[s.hint, { color: colors.muted }]}>Searching…</Text>
      )}
      {!searching && searched && results.length === 0 && (
        <Text style={[s.hint, { color: colors.muted }]}>
          {searchFailed ? "Couldn't search — check your connection." : 'No cities found'}
        </Text>
      )}

      {results.map((r, i) => (
        <Pressable
          key={`${r.label}-${r.latitude}-${r.longitude}-${i}`}
          style={[s.cityResult, { backgroundColor: colors.surface, borderColor: colors.line }]}
          onPress={() => handleSelect(r)}
          accessibilityRole="button"
          accessibilityLabel={`Set location to ${r.label}`}
        >
          <Text style={[s.cityLabel, { color: colors.ink }]}>{r.label}</Text>
        </Pressable>
      ))}
    </View>
  );
}

function makeStyles(_c: ColorPalette) {
  return StyleSheet.create({
    cityInput: {
      borderWidth: 1,
      borderRadius: 10,
      paddingHorizontal: 12,
      minHeight: 44,
      paddingVertical: 10,
      fontFamily: Fonts.ui,
      fontSize: 14,
      marginTop: 10,
    },
    cityResult: {
      borderWidth: 1,
      borderRadius: 10,
      paddingHorizontal: 12,
      minHeight: 44,
      paddingVertical: 10,
      marginTop: 8,
    },
    cityLabel: { fontFamily: Fonts.uiMedium, fontSize: 14 },
    hint: { fontFamily: Fonts.ui, fontSize: 12, marginTop: 8 },
  });
}
