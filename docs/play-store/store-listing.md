# Google Play Console — content & listing answers

Fill-in reference for **Digital Siddur** (`com.semiagenticrob.digitalsiddur`),
organized to match the Play Console checklist. Grounded in what the app
actually does (offline-first; no accounts, ads, analytics, or tracking; optional
approximate location sent to Hebcal for zmanim).

Decisions locked: **target audience 13+**, public contact **rbrt.s.wrrn@gmail.com**.

---

## LET US KNOW ABOUT THE CONTENT OF YOUR APP

### Set privacy policy
- **Privacy policy URL:** host `docs/play-store/privacy-policy.md` at a public
  URL and paste it here. Easiest option: enable **GitHub Pages** on the
  `digital-siddur` repo (Settings → Pages → deploy from `main`/`docs`), which
  gives you e.g. `https://semiagenticrob.github.io/digital-siddur/play-store/privacy-policy`.
  A public Gist also works. Play requires a live, publicly reachable URL.

### Sign in details
- Does any app functionality require users to sign in? **No.**
- The app requires no account and no login, so **no demo/test credentials are
  needed**. (If a field is required, note "App does not require login/account.")

### Ads
- Does your app contain ads? **No.**
- (No ad SDKs are present; nothing served.)

### Content rating (IARC questionnaire)
Category: **Reference / Book**. Suggested answers:
- Violence: **None**
- Sexuality / nudity: **None**
- Profanity / crude humor: **None**
- Controlled substances (drugs/alcohol/tobacco): **None**
- Gambling / simulated gambling: **None**
- Fear / horror: **None**
- Does the app allow users to interact or exchange content/UGC with others? **No**
  (notes and highlights are private and stay on the device).
- Does the app share the user's current location with other users? **No**
  (location is used only to compute prayer times; it is not shared with other
  users).
- Does the app let users purchase digital goods? **No.**
- Expected result: **Everyone / PEGI 3 / rated for all ages.**

### Target audience and content
- **Target age group:** 13–15, 16–17, and 18+ (i.e., **13 and older**). Do NOT
  select an under-13 bracket — that triggers the Designed for Families program
  and children's-privacy rules that conflict with the optional
  location-to-Hebcal feature.
- Is the store listing designed to appeal primarily to children? **No.**
- Designed for Families program: **do not opt in.**

### Data safety
See the detailed section at the bottom of this file — the form is granular.
Summary: the only user data leaving the device is **approximate location**
(optional), sent to Hebcal to compute prayer times; used for app functionality;
not for tracking or ads; not linked to an identity; encrypted in transit.

### Government apps
- Is this an official government app? **No.**

### Financial features
- Does your app provide financial features (loans, investing, crypto, payments,
  banking, insurance, etc.)? **No — none of the above.**

### Health
- Does your app have health features (health/medical, fitness/wellness, health
  research, etc.)? **No — none of the above.** (It is a religious prayer book,
  not a health app.)

---

## MANAGE HOW YOUR APP IS ORGANIZED AND PRESENTED

### Select an app category and provide contact details
- **App or game:** App
- **Category:** **Books & Reference** (best fit for a siddur).
- **Tags:** religion / reference / education (pick from Play's tag list).
- **Contact email:** rbrt.s.wrrn@gmail.com
- **Website (optional):** https://github.com/semiagenticRob/digital-siddur
  (or your GitHub Pages URL)
- **Phone (optional):** leave blank unless you want one public.

### Set up your store listing

**App name** (max 30 chars):
> Digital Siddur

Alternative if you want it more descriptive (25 chars): `Feigenbaum Weekday Siddur`

**Short description** (max 80 chars):
> A free, offline Nusach Ashkenaz weekday siddur with commentary, for teens.

**Full description** (max 4000 chars):

> Digital Siddur is a free, offline weekday prayer book (siddur) for the
> Feigenbaum Weekday Siddur, Cohen Family Edition — Nusach Ashkenaz. It was
> built especially for teens, with clear typography, plain-English explanations,
> and a layout that's easy to follow whether you daven every day or are just
> starting out.
>
> READ IT YOUR WAY
> • Hebrew, English, or side-by-side "Both" display — switch any time.
> • Adjustable font size and a light/dark theme.
> • Inline commentary and insights that explain what the words mean and why we
>   say them, right where you need them.
>
> MAKE IT YOURS
> • Highlight meaningful lines and add your own private notes.
> • Your notes and highlights stay on your device — always private.
> • The app remembers where you left off.
>
> ACCURATE PRAYER TIMES (ZMANIM)
> • Optionally get halachic times for your location, or just search for your
>   city. Location is optional and used only to calculate times.
>
> WHAT'S INCLUDED
> • Weekday Shacharis, Minchah, and Maariv (including Motzaei Shabbos).
> • Mussaf for Rosh Chodesh and Chol HaMoed.
> • Hallel.
> • Birkas Hamazon, Al HaMichyah, and Borei Nefashos.
> • Krias Shema al HaMitah, Sefiras HaOmer, Tefillas Haderech, Netilas Lulav.
> • A glossary and the book's front and back matter.
>
> PRIVATE AND FREE
> • Completely free. No ads. No account or sign-in.
> • No analytics and no third-party tracking.
> • Works offline — the prayers are always available, no connection required.
>
> Note: the digitized text is being proofed section by section against the
> print edition. Feedback is welcome at rbrt.s.wrrn@gmail.com.

**Graphics assets Play will require (prepare separately):**
- App icon: 512×512 PNG (32-bit). Your `assets/icon.png` can be the source.
- Feature graphic: 1024×500 PNG/JPG (required).
- Phone screenshots: at least 2 (up to 8), 16:9 or 9:16, min 320px side.
  Capture the reader in Both mode, a commentary segment, highlights/notes, and
  the zmanim/Now card.
- (Optional) 7" and 10" tablet screenshots — you support tablets on iOS; add
  Android tablet shots if you want tablet featuring.

---

## DATA SAFETY — detailed form answers

**Does your app collect or share any of the required user data types?**
→ **Yes** (approximate location is sent to Hebcal). Everything else is on-device
only and does not count as collection.

**Data type: Location → Approximate location**
- Collected: **Yes**
- Shared: **Yes** (sent to Hebcal, a third party, to compute prayer times)
- Purpose: **App functionality** only
- Is this required or optional for the user? **Optional** (users can enter a
  city by name instead of granting location)
- Is this data used for tracking or advertising? **No**
- Is this data linked to the user's identity? **No** (there is no account)

**All other data types** (personal info, financial info, health, messages,
photos/videos, audio, files, contacts, calendar, app activity/analytics, web
history, device or other IDs):
- **Not collected and not shared.** Preferences, notes, highlights, and reading
  position are stored **only on the device**, which Play does not count as
  "collection."

**Security practices**
- Is data encrypted in transit? **Yes** (HTTPS to Hebcal).
- Can users request that data be deleted? On-device data is deleted by clearing
  app data or uninstalling; there is no server-side data to delete.
- Independent security review / Play Families commitment: not applicable.

> Note on "ephemeral": the coordinates are sent to Hebcal only to fetch times
> for the current request and are not stored on any server we control. If the
> form offers "processed ephemerally," you may check it for the sharing case.
> The declaration above is the conservative, clearly-accurate reading — safe to
> submit as-is.
