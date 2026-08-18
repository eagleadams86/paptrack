# PAPTrack — Web

**Live:** [eagleadams86.github.io/paptrack](https://eagleadams86.github.io/paptrack/)

PAPTrack keeps CPAP supplies on schedule three ways at once: **cleaning** (daily/weekly reminders), **replacement** (countdowns per the standard DME schedule), and **inventory** (spares on hand with reorder flags). Built from a supplier's "clean & replace your equipment" flyer.

This is the **web version** — `index.html` plus `theme.css` (the shared palette, copied from the private theme pack so every app in the family reads the same file). Use the live link above, or serve the folder locally; the two files have to sit together, so opening the HTML straight off disk without `theme.css` beside it gives an unstyled page. No build step, and no account is ever required (an optional Google sign-in adds cross-device sync — see below).

### The PAPTrack Family

| Platform | Repo |
|----------|------|
| 🌐 Web (this repo) | [eagleadams86/paptrack](https://github.com/eagleadams86/paptrack) |
| 🍎 iOS | [eagleadams86/paptrack-ios](https://github.com/eagleadams86/paptrack-ios) — [on the App Store](https://apps.apple.com/us/app/paptrack-cpap-supply-tracker/id6793314905) |
| 🤖 Android | [eagleadams86/paptrack-android](https://github.com/eagleadams86/paptrack-android) |
| 🛟 Support & privacy | [eagleadams86/paptrack-support](https://github.com/eagleadams86/paptrack-support) |

---

## Built-In Supply Presets

| Supply | Clean | Replace |
|--------|-------|---------|
| 😷 Mask | daily | every 3 months |
| 🪢 Headgear | weekly | every 6 months |
| 〰️ Tubing | weekly | every 3 months |
| 🌫️ Disposable Fine Filters | — (replace only) | every 2 weeks |
| 🛟 Full Face Cushions | daily | every month |
| 👃 Nasal Cushions & Pillows | daily | every 2 weeks |
| 💧 Humidifier Chamber | daily | every 6 months |
| 💦 Distilled Water | — | as needed |

Every value is editable per item, and custom items are supported for anything else (chinstrap, SD card, wipes…).

## Features

- **One-tap setup** — "Load full-face kit" or "Load nasal kit" adds the six matching supplies at once; then set each item's real "last replaced" date via Edit
- **Replacement and cleaning countdowns** — both badges on a card show the next due date, the days left, and the days overdue once it passes, with urgency-colored badges (red when overdue *or* nearly due, amber as the deadline approaches, otherwise green); the list sorts most-urgent first. Thresholds scale with each item's own cycle — the cleaning badge off "clean every N days", the replacement badge off "replace every N days" (amber at ≤40%, red at ≤20%, capped at 14/7 days and never covering the whole cycle), so a 2-week consumable isn't flagged "replace soon" the day it's replaced and a daily-cleaned mask isn't red the moment you wash it
- **Badges carry their colour in the outline**, not just a dot, and each one names its own state in words. The four pale fills were nearly indistinguishable from one another for a red-green colourblind reader — on the dark themes all six pairings failed — so the border does that work instead: the strong status colours are far enough apart to tell at a glance. "Nearly due" and "overdue" deliberately share the same red; once the red-green axis is gone there is only room for about three levels, so a fourth was dropped rather than kept as a distinction that couldn't be seen
- **As-needed consumables** — set "Replace every" to 0 (or tap the **As needed** chip) for items with no fixed schedule, like distilled water: no countdown or due date, they sort last, and reordering is driven purely by the spares count
- **Cleaning tracker** — the cleaning badge reads exactly like the replacement one: "Clean by Aug 5, 2026 · 2 days left" while it's ahead of you, "Clean overdue by 17 days" once it isn't (an item you've never cleaned just says "Cleaning due" — there's no last-cleaned date to count from). Same urgency colours, scaled to the cleaning cycle instead of the replacement cycle. One-tap **Mark cleaned**, plus a **Mark all due items clean** button that marks exactly the items currently due (it leaves already-clean items alone rather than recording a cleaning that never happened). The add/edit form groups fields into **Cleaning · Replacement · Spares** sections (matching the native iOS app) and lets you set both the last-cleaned and last-replaced dates directly. Both date fields stop at today — they record something that already happened, so a future date is always a typo
- **Last cleaned & last replaced** — every card shows how long ago the last replacement and cleaning happened (today / yesterday / N days ago; "Not cleaned yet" until the first one)
- **Inventory & reorder** — a spares counter with −/+ steppers on every card; items are flagged **Reorder** whenever spares fall to the item's threshold. **Replaced today** resets the countdown and consumes a spare automatically (and hides for the rest of the day so it can't be pressed twice)
- **Card layout** — each supply is a 2×2 quadrant grid — 🧼 Cleaning · ↻ Replacing · 📦 Spares · ⚙️ Manage — matching the native iOS app
- **Dismissing a dialog** — clicking outside it cancels, the same as **Cancel** or Escape; nothing is saved. Clicks on the dialog's own padding or scrollbar don't count as outside, and neither does releasing outside after starting a drag inside a field, so a stray gesture can't throw away edits. The same rule covers the add/edit form, the backup dialog and the delete-all confirmation; the sync "which data do you want to keep?" dialog deliberately still requires an explicit choice
- **Stat tiles** — three centered tiles, one per filter: 🧼 Clean due, ↻ Replace due, and 📦 Reorder, each showing a count and the affected items' emoji (or an all-clear check)
- **Search & filters** — live search plus three chips: 🧼 Clean due, ↻ Replace due (due today or overdue), 📦 Reorder due; tapping the active chip again clears it back to showing everything
- **Calendar reminders** — one-tap `.ics` export per item with up to three events: next replacement (alarm 2 days before), a reorder reminder ahead of it (half the cycle for short-cycle consumables, at most 30 days — the typical insurance resupply window), and the next cleaning for items cleaned less often than daily. Output is folded to RFC 5545's 75-octet line limit (split between characters, so accents and emoji survive) for calendar apps that reject over-long lines
- **Resupply tip** — footer note about insurance PAP-adherence requirements and humidifier care (distilled water, empty every morning)
- **How it works** — a footer link back to this README on GitHub (the repo front page renders it), for the detail the app itself has no room for
- **Back up & restore** — a **Back up** button in the header (beside sync and the theme picker, where the sibling apps keep theirs) opens one dialog holding everything to do with your data: download a JSON copy, restore one, or — folded away under **Start again** — **delete all data**. The delete is behind a fold on purpose, since it's the one irreversible action in the app, and pressing it opens a confirmation of its own that says how much is going, warns you when you're signed in that the copy in your Google account goes too, and offers the same download as a last chance to keep any of it. Your theme survives. (These used to be two underlined links at the very foot of the page, nowhere near where anyone looks for them)
- **Private & offline** — all data in `localStorage`; JSON backup export/import; no account required. Imported backups and synced cloud documents are validated field by field before they're trusted: unreadable records are skipped (the toast says how many), out-of-range numbers are clamped, and impossible dates fall back to today, so a corrupt or hand-edited file can't take the app down
- **Accessible** — every control has a name, and the repeated card buttons say which supply they belong to ("Delete — Mask"), so a screen reader never just reads "Delete, Delete, Delete". The stat tiles' emoji rows are announced as sentences ("2 supplies due for cleaning: Mask, Tubing"), keyboard focus stays on the button you pressed when the list re-renders, and all four themes meet WCAG AA contrast (4.5:1) down to the 10px tile labels
- **Cross-device sync (optional)** — a **☁️ Sign in to sync** button in the header signs in with Google and syncs via Firestore, so phone and computer share the same data live; signed out, the app is 100% local (see below)
- **4 themes, Midnight by default** — dropdown in the header, listed alphabetically (Dark, Light, Midnight, Sepia), shared with every other app in this family via the unified theme pack; choice saved in `localStorage` and applied before first paint. Forest, Solarized and Synthwave were retired in August 2026, and Slate was renamed Dark — a saved Slate preference carries over automatically

---

## Cross-Device Sync (Firebase, Free Tier)

Sync is **enabled** in this deployment, backed by the `paptrack-6c817` Firebase project — the `FIREBASE_CONFIG` object at the bottom `<script type="module">` block of `index.html` points at it. Setting that constant back to `null` returns the app to fully-local mode and hides all sync UI. To recreate the setup from scratch (e.g. in a fork):

1. At [console.firebase.google.com](https://console.firebase.google.com), create a project (Analytics not needed)
2. **Build → Authentication → Get started → Google** — enable the Google sign-in provider
3. **Authentication → Settings → Authorized domains** — add `eagleadams86.github.io`
4. **Build → Firestore Database → Create database** (production mode), then paste these **Rules**:
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /paptrack/{uid} {
         allow read, write: if request.auth != null && request.auth.uid == uid;
       }
     }
   }
   ```
5. **Project settings → Your apps → Add app → Web** — copy the `firebaseConfig` object and paste it as the value of `FIREBASE_CONFIG` in `index.html`

Because all three ports (web, iOS, Android) share this one Firebase project and one document per user, a data-deletion request is handled once and covers every device the person used — runbook in [`DATA_DELETION.md`](https://github.com/eagleadams86/paptrack-ios/blob/main/DATA_DELETION.md), kept in the iOS repo alongside the checked-in `firestore.rules`.

The config object is not a secret (access is controlled by the rules above, which restrict each user to their own document). Because the authorized domain is `eagleadams86.github.io`, sign-in and sync work identically at this repo's `/paptrack/` path and at the old `/prototypes/` path — no Firebase change was needed for the move.

### Why Sign-In Doesn't Use Firebase's Popup

Sign-in goes through **Google Identity Services**: a popup straight to `accounts.google.com` returns an OAuth access token, and Firebase exchanges it for a session via `signInWithCredential`. `GOOGLE_CLIENT_ID`, just above `FIREBASE_CONFIG`, is what makes that possible.

Firebase's own `signInWithPopup` is deliberately not used. It **starts** at `<project>.firebaseapp.com/__/auth/handler` and only redirects on to Google from there, so a proxy that blocks that first hop kills sign-in outright — nothing in the app ever runs. **This project's hostname is one of the blocked ones**, confirmed on a corporate network.

The block is per **hostname**, not per domain, which is worth stating because the obvious conclusion is wrong. Measured on one network on a single day: this app's hostname and Team Dashboard's were both refused, while Sprint Velocity's went through untouched — identical sign-in code, and the blocked pair weren't the newest projects. Which way a filter lands on a hostname is outside our control and can change.

Same Google account, same Firestore document, same rules — only the doorway changed. All four web apps in this family now do this, and all four were confirmed working on the network that needed it on 7 August 2026.

Two consequences worth knowing:

- **The CSP carries `accounts.google.com` and not `firebaseapp.com`.** `authDomain` remains in `FIREBASE_CONFIG` because the SDK requires the field, but nothing loads it. `apis.google.com` is gone too — it served the old popup.
- **Auth is built with `initializeAuth`, not `getAuth`,** so the SDK never asks for `apis.google.com` in the first place. `getAuth()` always wires in `browserPopupRedirectResolver`, and the SDK initialises that resolver during startup — which loads `apis.google.com/js/api.js` to build the gapi iframe that carries `signInWithPopup` and `signInWithRedirect` results back to the page. This app calls neither, so nothing consumed it; the visible symptom was a CSP error in the console and nothing else. Token refresh, sign-out and the cross-tab session all run elsewhere in the SDK and never touch the resolver. The three persistences passed in are the ones `getAuth` would have set, in its order, so existing sessions and cross-tab behaviour are unchanged. Dropping the resolver costs `signInWithPopup`/`signInWithRedirect`/phone sign-in, which now raise `auth/argument-error`; if one is ever wanted, pass `browserPopupRedirectResolver` to that call rather than reverting to `getAuth()`. (Web only — the native apps never used the resolver.)
- **`GOOGLE_CLIENT_ID` is not part of `firebaseConfig`** and can't be derived from it. Cloud Console → APIs & Services → Credentials → the OAuth 2.0 Client ID named *Web client (auto created by Google Service)*. That same screen's **Authorized JavaScript origins** must list the app's origin — exact match including port, so `http://localhost` and `http://localhost:8011` are different origins — or Google refuses with `origin_mismatch`.

**This is web-only, and it brought the web in line with the native apps rather than ahead of them.** iOS (GoogleSignIn-iOS) and Android (Credential Manager) already obtain a Google credential from the platform and hand it to the very same `signInWithCredential` call, never touching a hosted handler. Neither needed any change.

How sync behaves: `localStorage` stays the source of truth. The **first** time a given Google account signs in on a browser, if both the browser and the cloud already have items saved, a dialog asks which to keep ("Keep this device" vs. "Keep Google's data") instead of guessing — silently picking the most-recently-changed side once wiped out a browser's data when an unrelated/stale cloud doc happened to have a newer timestamp. After that first reconciliation (tracked per-account via a `pap-sync-uid` flag in `localStorage`), and for live updates pushed from other devices, whichever side changed most recently (`updatedAt`) wins — with one hard rule on top: **an empty copy never silently beats a copy with items in it**, whatever the timestamps say. A fresh sign-in with nothing saved can't overwrite a cloud copy that has your supplies, and if another device genuinely clears everything, this one asks before following suit (declining restores your copy to the other devices). Signing out or losing connectivity just leaves the local copy in charge.

**When sync stops working, it says so.** Failures used to end in the browser console, which
nobody has open — so the button went on showing your name and the note went on promising your
supplies were reaching your other devices, while nothing had left the browser. The button now
reads **⚠️ Not syncing** and the note at the foot of the page gives the cause in plain English
and what to do about it. Nothing is ever lost when this happens: this browser stays the source
of truth and the cloud only mirrors it. There's no retry button on purpose — Firestore retries
the transient causes itself, and the next successful save clears the state. Two details are
load-bearing: the live listener carries an **error callback**, because a listener that errors is
dropped by Firestore and never fires again (without it, another device's updates simply stop
arriving while the header still says "syncing"); and `invalid-argument` is **not** assumed to
mean "too big" — Firestore uses that one code for both an oversized document and a value it
can't store, so the advice to remove a supply appears only when the size really is the problem.
A remedy that destroys data is never the guess.

---

## Architecture

```
GitHub Pages (static hosting, this repo, main branch)
    ├── index.html — the app; loads the Firebase SDK from gstatic.com
    └── theme.css — shared palette, copied from the private theme pack
            ├── all state ──► browser localStorage (source of truth, works offline)
            └── signed in ──► Firestore doc paptrack/{uid} (newer-wins by updatedAt,
                              with the empty-never-beats-data guard; live onSnapshot
                              updates on other devices)

Backup/restore via JSON export & import.
```

There is no server of our own — the only backend is the optional Firebase (auth + one Firestore document per user, free tier). The app works from a double-clicked file just as well as from GitHub Pages, and degrades to fully-local mode when Firebase is unreachable or the user is signed out.

**The icon** is the airflow mark the [iOS](https://github.com/eagleadams86/paptrack-ios) and [Android](https://github.com/eagleadams86/paptrack-android) apps wear — a source dot with three arcs radiating out. `make_favicon.py` takes the shipped iOS icon as its master, repaints the rings and writes all three web copies from that one image: `favicon.ico` and the two base64 PNG data URIs in `index.html`. It recolours rather than redraws, so the shapes can't drift. The one deliberate difference from the phone icons is the colour: they fade each ring by alpha down to a nearly invisible outer arc, which read as dim beside the other apps in a row of browser tabs, so the web ramp runs between the shared accent tones instead. Re-run with `python3 make_favicon.py`, then bump the `?v=` on the `favicon.ico` link.

**Tests:** `tests.html` (open it via a local server, e.g. `python3 -m http.server 8011`) loads the real `index.html` in a hidden iframe and pins the web-only pure functions — the untrusted-input validation that guards backups and synced data, and the `.ics` calendar generation. No build step, no frameworks; the page either says "All N tests pass" or lists what broke. The shared schedule math is additionally pinned by the [iOS](https://github.com/eagleadams86/paptrack-ios) and [Android](https://github.com/eagleadams86/paptrack-android) unit-test suites.

**It only runs on localhost, and enforces that itself.** The test code writes nothing, but the iframe boots the real app — and GitHub Pages publishes `tests.html` next to it, at `/paptrack/tests.html`, where that iframe would be your signed-in copy: sync would start inside an invisible frame, and the which-copy dialog could fire where nobody can answer it. Two guards. The iframe carries `data-pap-tests`, which the sync module checks so it never initialises in the harness; and a gate at the foot of `tests.html` checks `location.hostname` and, anywhere but `localhost` / `127.0.0.1` / `[::1]`, never creates the iframe at all — it explains why and says how to run the suite properly. CI reaches the page on `localhost:8011`, so it is unaffected.

![tests](https://github.com/eagleadams86/paptrack/actions/workflows/tests.yml/badge.svg)

The suite also runs on every push: [`.github/workflows/tests.yml`](.github/workflows/tests.yml) serves the folder, opens `tests.html` in headless Chromium and fails the build if the summary goes red or the page throws — same workflow as the rest of the app family.

---

## Privacy Policy

[`privacy.html`](privacy.html) is the web app's privacy policy, linked from the footer — what
the app stores, what the optional Google sign-in puts in Firestore, and how to have a synced
copy deleted. It exists because other people can sign in with their own Google accounts. The
iOS app has its own policy in the [paptrack-support](https://github.com/eagleadams86/paptrack-support)
repo; if what either app stores changes, update both in the same commit.

## Commit Messages

Commit subject lines are written in plain English a non-developer can read (what changed and why it matters, not implementation detail). The in-app "Recent changes" panel that listed them was removed in August 2026, along with the GitHub API entry in the page's CSP.
