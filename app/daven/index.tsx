import React from 'react';
import { View, Text, Pressable, StyleSheet, FlatList, SafeAreaView, useColorScheme } from 'react-native';
import { router } from 'expo-router';
import { listServices } from '../../src/content/loader';
import { usePreferencesStore } from '../../src/store/preferences';
import { LightColors, DarkColors, ColorPalette } from '../../src/theme/colors';
import { Fonts } from '../../src/theme/typography';

export default function DavenHome() {
  const { theme } = usePreferencesStore();
  const systemScheme = useColorScheme();
  const isDark = theme === 'dark' || (theme === 'auto' && systemScheme === 'dark');
  const colors: ColorPalette = isDark ? DarkColors : LightColors;
  const services = listServices();
  const s = makeStyles(colors);

  return (
    <View style={[s.screen, { backgroundColor: colors.paper }]}>
      <SafeAreaView style={s.safe}>
        <View style={s.headerRow}>
          <Text style={[s.title, { color: colors.ink }]}>Daven</Text>
          <Pressable
            onPress={() => router.push('/settings')}
            accessibilityRole="button"
            accessibilityLabel="Open settings"
            style={s.settingsBtn}
          >
            <Text style={[s.settingsIcon, { color: colors.muted }]}>⚙</Text>
          </Pressable>
        </View>
        <FlatList
          data={services}
          keyExtractor={item => item.id}
          contentContainerStyle={s.list}
          renderItem={({ item }) => (
            <Pressable
              style={({ pressed }) => [s.row, { backgroundColor: colors.surface, borderColor: colors.line }, pressed && s.rowPressed]}
              onPress={() => router.push('/daven/' + item.id as any)}
              accessibilityRole="button"
              accessibilityLabel={`Open ${item.enTitle}`}
            >
              <Text style={[s.rowEn, { color: colors.ink }]}>{item.enTitle}</Text>
              <Text style={[s.rowHe, { color: colors.muted }]}>{item.heTitle}</Text>
            </Pressable>
          )}
        />
      </SafeAreaView>
    </View>
  );
}

function makeStyles(colors: ColorPalette) {
  return StyleSheet.create({
    screen: { flex: 1 },
    safe: { flex: 1 },
    headerRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: 24,
      paddingTop: 24,
      paddingBottom: 12,
    },
    title: {
      fontFamily: Fonts.uiSemiBold,
      fontSize: 28,
    },
    settingsBtn: { padding: 8 },
    settingsIcon: { fontSize: 22 },
    list: { paddingHorizontal: 16, gap: 8, paddingBottom: 40 },
    row: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderRadius: 14,
      paddingVertical: 16,
      paddingHorizontal: 18,
      borderWidth: 1,
    },
    rowPressed: { opacity: 0.7 },
    rowEn: { fontFamily: Fonts.uiMedium, fontSize: 17 },
    rowHe: {
      fontFamily: Fonts.hebrewBold,
      fontSize: 20,
      writingDirection: 'rtl' as const,
    },
  });
}
