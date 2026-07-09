# Android Enablement + Repo Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the app Android-ready (config + safe-area correctness + emulator QA) and land the approved hygiene subset (README, CI, .gitignore, doc moves). No folder reorganization — user-approved decision: the existing Expo layout stays; `src/` and `app/` paths are load-bearing for 189 content-script references.

**Architecture:** Two code tasks on a branch (`android-enablement`) + a controller-run emulator QA phase. Hygiene first (docs/CI only), then the Android config + SafeAreaView migration.

**Tech Stack:** Expo SDK 56 / Expo Router v4, react-native-safe-area-context, GitHub Actions.

## Global Constraints

- **Do NOT touch `LICENSE`** (user decision: licensing stays as-is).
- **No file moves inside `src/` or `app/`** — content tooling hard-codes those paths.
- iOS behavior must be pixel-identical after the SafeAreaView migration (react-native-safe-area-context's SafeAreaView insets the same edges on iOS that RN's did; verify no double-padding on screens that add their own).
- Run `npm run check` before every commit. Expo SDK 56 docs: https://docs.expo.dev/versions/v56.0.0/

---

### Task 1: Hygiene — README, CI, .gitignore, doc moves

**Files:**
- Create: `README.md`, `.github/workflows/check.yml`
- Modify: `.gitignore`
- Move (git mv): `Feigenbaum_Siddur_PRD_v1.0.md` → `docs/`, `Feigenbaum_Siddur_Prototype.html` → `docs/`

- [ ] **Step 1: CI workflow**

```yaml
# .github/workflows/check.yml
name: check
on:
  push:
    branches: [main]
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run check
```

(`npm run check` = tsc + `python3 scripts/lint_content.py --strict` + jest; ubuntu-latest ships python3. Verify the lint script needs no pip installs — it uses stdlib only.)

- [ ] **Step 2: README.md** — concise: what the app is (free, offline-first digital edition of the Feigenbaum Weekday Siddur; iOS on TestFlight, Android in progress); quick start (`npm install`, `npm start`, `npm run check`); repo map (app/ routes, src/content JSON + rendering contract pointer to docs/CONTENT_GUIDE.md, scripts/ content tooling, docs/); the two-track framing (content fidelity vs app) borrowed from CLAUDE.md; note that the siddur text is © its rightsholders and the print PDF is the content authority; new-clone setup line: `git config core.hooksPath scripts/hooks`. Do not state a code license (LICENSE file governs; leave it alone).

- [ ] **Step 3: .gitignore** — append `.superpowers/` and `.playwright-mcp/` under a "session scratch" comment.

- [ ] **Step 4: git mv the two root docs into docs/**, verify `git status` shows renames.

- [ ] **Step 5: `npm run check` green → commit** `chore: repo hygiene — README, CI check workflow, gitignore, doc moves`

---

### Task 2: Android config + SafeAreaView migration

**Files:**
- Modify: `app.json` (android.package), `package.json` (only if react-native-safe-area-context missing — install via `npx expo install`)
- Modify (8 files): `app/daven/index.tsx`, `app/daven/[service].tsx`, `app/settings.tsx`, `app/onboarding.tsx`, `app/glossary.tsx`, `app/notes.tsx`, `app/about/index.tsx`, `app/about/[piece].tsx`

- [ ] **Step 1: app.json** — add `"package": "com.semiagenticrob.digitalsiddur"` to the `android` block (mirrors the iOS bundleIdentifier).

- [ ] **Step 2: dependency** — check package.json for `react-native-safe-area-context`; if absent, `npx expo install react-native-safe-area-context` (expo-router already provides the SafeAreaProvider at the root — do NOT add a provider).

- [ ] **Step 3: migrate imports** — in each of the 8 files, remove `SafeAreaView` from the `react-native` import list and add `import { SafeAreaView } from 'react-native-safe-area-context';`. Read each file first: if a screen's layout compensates for RN-SafeAreaView's iOS-only behavior (e.g., manual `paddingTop` for Android), remove the compensation so insets aren't doubled — inspect each header's padding values and report per-file what you found.

- [ ] **Step 4: `npm run check` green → commit** `fix(android): real safe-area insets via react-native-safe-area-context`

---

### Task 3 (controller): Emulator QA + fixes

- Verify an Android emulator/AVD exists (`emulator -list-avds`); create one if the SDK allows, else coordinate with the user.
- QA checklist: status-bar/header insets on every screen (the migration's whole point); RTL Hebrew + nikud in the reader (Frank Ruhl Libre); FlashList scrolling + reading-position restore; NowCard (date, CTA, strip with a location set); Special Days badges; Settings location flow incl. city search; About/Glossary; Android back gesture/button through nested stacks; keep-awake.
- File findings as fix tasks; re-QA after fixes.

---

## Out of scope (explicit)

Folder reorganization (rejected), LICENSE changes (user: keep as-is), Play Console account/listing work, privacy-policy hosting, the actual `eas build -p android` (follows once QA is clean and the user has the Play account).
