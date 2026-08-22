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

- **One-tap setup** — "Load full-face kit" (seven supplies) or "Load nasal kit" (six) adds the matching supplies at once; then set each item's real "last replaced" date via Edit. The nasal kit has no separate "Mask" item — on a nasal setup the cushion or pillows *are* the mask. Both kits include 💦 Distilled Water, which has no schedule at all: it carries no countdown, sorts last, and is driven purely by the spares count
- **Replacement and cleaning countdowns** — both badges on a card show the next due date, the days left, and the days overdue once it passes, with urgency-colored badges (red when overdue *or* nearly due, amber as the deadline approaches, otherwise green); the list sorts most-urgent first. Thresholds scale with each item's own cycle — the cleaning badge off "clean every N days", the replacement badge off "replace every N days" (amber at ≤40%, red at ≤20%, capped at 14/7 days and never covering the whole cycle), so a 2-week consumable isn't flagged "replace soon" the day it's replaced and a daily-cleaned mask isn't red the moment you wash it
- **Badges carry their colour in the outline**, not just a dot, and each one names its own state in words. The four pale fills were nearly indistinguishable from one another for a red-green colourblind reader — on the dark themes all six pairings failed — so the border does that work instead: the strong status colours are far enough apart to tell at a glance. "Nearly due" and "overdue" deliberately share the same red; once the red-green axis is gone there is only room for about three levels, so a fourth was dropped rather than kept as a distinction that couldn't be seen
- **As-needed consumables** — set "Replace every" to 0 (or tap the **As needed** chip) for items with no fixed schedule, like distilled water: no countdown or due date, they sort last, and reordering is driven purely by the spares count
- **Cleaning tracker** — the cleaning badge reads exactly like the replacement one: "Clean by Aug 5, 2026 · 2 days left" while it's ahead of you, "Clean overdue by 17 days" once it isn't. **Replacing an item restarts its cleaning cycle**, because a supply out of a fresh packet is clean — swap an overdue mask and the badge goes green instead of nagging you to wash something you just unwrapped. The countdown runs from whichever came later, your last cleaning or the replacement; an item you've never cleaned counts from when it was replaced, and still says "Not cleaned yet" under the badge. Marking it replaced never records a cleaning you didn't do. Same urgency colours, scaled to the cleaning cycle instead of the replacement cycle. One-tap **Mark cleaned**, plus a **Mark all due items clean** button that marks exactly the items currently due (it leaves already-clean items alone rather than recording a cleaning that never happened). The add/edit form groups fields into **Cleaning · Replacement · Spares** sections (matching the native iOS app) and lets you set both the last-cleaned and last-replaced dates directly. Both date fields stop at today — they record something that already happened, so a future date is always a typo
- **Last cleaned & last replaced** — every card shows how long ago the last replacement and cleaning happened (today / yesterday / N days ago; "Not cleaned yet" until the first one)
- **Inventory & reorder** — a spares counter with −/+ steppers on every card; items are flagged **Reorder** whenever spares fall to the item's threshold. **Replaced today** resets the countdown and consumes a spare automatically (and hides for the rest of the day so it can't be pressed twice)
- **Card layout** — each supply is a 2×2 quadrant grid — 🧼 Cleaning · ↻ Replacing · 📦 Spares · ⚙️ Manage — matching the native iOS app
- **The theme picker is written out at its final size, with Midnight pre-selected.** The header paints long before the script at the foot of the page runs, so an option list built by script made the row read "☾ Dark" over a midnight page for a moment on every load. The sun is `☀`, the plain text character, not the emoji-presentation `☀️` — the colour-font variant is a different weight and baseline from the `☾` and `✦` beside it, and the row read as three different sets of glyphs. Both fixed 2026-08-21 and pinned in `tests.html`; every sibling app follows the same two rules
- **Fits the screen it's on** — the page is the same width as the sibling apps (Sprint Predictability, Flow Metrics), the supply cards flow into two or three columns as the window allows, and cards on the same row are the same height so a row has a straight bottom edge. On a phone it's the single column it always was. The header is a bar across the top that **stays put as you scroll**, so the theme picker, **Back up** and sync are always a click away rather than somewhere above the first supply
- **Roomier editing** — the add/edit form is a wide window laying Cleaning beside Replacement and Spares beside Notes, so the whole form is visible at once on a desktop instead of being a long scroll; on a narrow window it stacks back into one column
- **Dismissing a dialog** — clicking outside it cancels, the same as **Cancel** or Escape; nothing is saved. Clicks on the dialog's own padding or scrollbar don't count as outside, and neither does releasing outside after starting a drag inside a field, so a stray gesture can't throw away edits. The same rule covers the add/edit form, the backup dialog and the delete-all confirmation; the sync "which data do you want to keep?" dialog deliberately still requires an explicit choice
- **Stat tiles** — three centered tiles, one per filter: 🧼 Clean due, ↻ Replace due, and 📦 Reorder, each showing a count and the affected items' emoji (or an all-clear check)
- **Search & filters** — live search plus three chips: 🧼 Clean due, ↻ Replace due (due today or overdue), 📦 Reorder due; tapping the active chip again clears it back to showing everything
- **More than one person on one app** — two people on one CPAP household kept their supplies apart by keeping two Google accounts, which also means two sign-ins, two backups and two phones set up. Each person is now a profile with their own supplies, countdowns and spares; the theme, the reminders and the backup file are shared. The picker appears in the header **only once there are two people** — a picker with one option is a control that does nothing — and the last entry in it opens the window where people are added, renamed and removed. Removing someone deletes their supplies and says so first
- **A history for every supply, and a Details page to read it on** — every time you press Mark cleaned, Mark replaced or Mark ordered, the supply records it. The 📋 Details button on a card opens what has actually happened to it, newest first, with the figure the log is for: *"Replaced 3 times on record, on average every 96 days — the schedule says 90."* That gap between the schedule and the reality is the thing no countdown can tell you. Editing a date by hand deliberately writes **no** event: correcting a record is not the same as doing the thing, and a log you can edit from two directions is worth nothing. Sixty events per supply, oldest dropped — the whole list rides in one Firestore document
- **Pause a supply instead of deleting it** — a spare machine in a drawer, a mask you've stopped using. It keeps its dates, its spares and its history, but it leaves the counts, the chips and the reminders entirely, and it sorts below everything else. Deleting was the only option before, and it throws the history away
- **Snooze the reminders without changing what's true** — deliberately not the same as pausing. The card still shows the real countdown, because a card is something you went looking at; the phones stay quiet until the date. A snooze that has run out is simply over
- **Mark something ordered** — ordering doesn't put a spare on the shelf, so the reorder flag used to go on nagging for the fortnight the box was in the post. "Mark ordered" turns it green — *"On order — ordered 3 days ago"* — until the spares go up or three weeks pass, whichever comes first
- **Supplier, reorder link and cost** — all optional, all on the edit form. A cost turns into the figure that actually answers "is this worth it": *"At $79.50 each, replace every 3 months: about $322.42 a year."* The link is the one field in this app a browser will follow, so it is dropped unless it is plain `http(s)`, and dropped rather than truncated if it is over-long — a cut URL still looks usable and points somewhere nobody chose
- **CSV for a spreadsheet** — two one-way exports in the Back up dialog, beside the JSON that is the actual backup: one row per supply, and one row per history event. Every cell starting with `=`, `+`, `-` or `@` is defused with a leading apostrophe, because a spreadsheet reads those as formulas and a supply name is free text
- **Calendar reminders** — one-tap `.ics` export per item with up to three events: next replacement (alarm 2 days before), a reorder reminder ahead of it (half the cycle for short-cycle consumables, at most 30 days — the typical insurance resupply window), and the next cleaning for items cleaned less often than daily. Output is folded to RFC 5545's 75-octet line limit (split between characters, so accents and emoji survive) for calendar apps that reject over-long lines
- **Resupply tip** — footer note about insurance PAP-adherence requirements and humidifier care (distilled water, empty every morning)
- **How it works** — a footer link back to this README on GitHub (the repo front page renders it), for the detail the app itself has no room for
- **Back up & restore** — a **Back up** button in the header (between the theme picker and sync, where the sibling apps keep theirs) opens one dialog holding everything to do with your data: download a JSON copy, restore one, or — folded away under **Start again** — **delete all data**. The delete is behind a fold on purpose, since it's the one irreversible action in the app, and pressing it opens a confirmation of its own that says how much is going, warns you when you're signed in that the copy in your Google account goes too, and offers the same download as a last chance to keep any of it. Your theme survives. (These used to be two underlined links at the very foot of the page, nowhere near where anyone looks for them)
- **Install it like an app** — on a Mac or a PC, open the site in Chrome or Edge and choose "Install PAPTrack". It gets its own window with no browser chrome, its own icon in the Dock or on the taskbar, and it opens straight from there. On an iPhone or iPad, Safari's Share ▸ "Add to Home Screen" does the same (though the [native iOS app](https://github.com/eagleadams86/paptrack-ios) is the better fit there)
- **Works with no connection** — installed or in a tab. The app is cached the first time you visit and served from that copy whenever the network doesn't answer, so a plane or a dead signal doesn't stop you marking something clean. It always tries the network first, so an update never waits behind a stale cached copy
- **Private & offline** — all data in `localStorage`; JSON backup export/import; no account required. Imported backups and synced cloud documents are validated field by field before they're trusted: unreadable records are skipped (the toast says how many), out-of-range numbers are clamped, and impossible dates fall back to today, so a corrupt or hand-edited file can't take the app down
- **The field bounds are the same on all three apps** (`LIMITS` here, `SupplyItem.Limits` on both phones): 3650 days for either cycle, 999 spares, a 60-character name and a 140-character note. Until 2026-08-22 this app's were tighter — 99 spares, a reorder-at of 20, 365/1095 days — and because they're applied on *every* load, import and synced document, a spare count or a reorder threshold typed on a phone was quietly rewritten here and then pushed back, so the phone lost it too. Clamping is what that boundary is for; the bug was that the three apps disagreed about where. `tests.html` now pins the numbers, and the form's own HTML `max` attributes against them
- **Accessible** — every control has a name, and the repeated card buttons say which supply they belong to ("Delete — Mask"), so a screen reader never just reads "Delete, Delete, Delete". The stat tiles' emoji rows are announced as sentences ("2 supplies due for cleaning: Mask, Tubing"), keyboard focus stays on the button you pressed when the list re-renders, and all four themes meet WCAG AA contrast (4.5:1) down to the 10px tile labels
- **Cross-device sync (optional)** — a **☁️ Sign in to sync** button in the header signs in with Google and syncs via Firestore, so phone and computer share the same data live; signed out, the app is 100% local (see below)
- **Buttons are the family's** — a bordered `.btn` with a filled `.primary` variant drawn from the pack's `--btn-bg`/`--btn-text`, the same rule Sprint Predictability, Flow Metrics and Money Map carry. Until 2026-08-22 this was the one app whose primary button was an accent-purple pill, so two of them open side by side didn't look like one product. No colour changed: the primary pair was already in the palette and unused here, and `--accent` keeps its other jobs. The floating **+ Add supply** button keeps its own padding and pill shape on top of `.primary` — the family's compact button is a 31px target, and that one is meant for a thumb against a moving list
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

How sync behaves: `localStorage` stays the source of truth. The **first** time a given Google account signs in on a browser, if both the browser and the cloud already have items saved, a dialog asks which to keep ("Keep this device" vs. "Keep Google's data") instead of guessing — silently picking the most-recently-changed side once wiped out a browser's data when an unrelated/stale cloud doc happened to have a newer timestamp. After that first reconciliation (tracked per-account via a `pap-sync-uid` flag in `localStorage`), and for live updates pushed from other devices, whichever side changed most recently (`updatedAt`) wins — with one hard rule on top: **an empty copy never silently beats a copy with items in it**, whatever the timestamps say. A fresh sign-in with nothing saved can't overwrite a cloud copy that has your supplies, and if another device genuinely clears everything, this one asks before following suit (declining restores your copy to the other devices). Signing out or losing connectivity just leaves the local copy in charge. Edits made in the few seconds while a sign-in is still settling which copy wins are held back and pushed the moment it settles, so a half-decided cloud copy is never overwritten.

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
    ├── theme.css — shared palette, copied from the private theme pack
    ├── sw.js     — service worker: keeps the app on your device for offline
    └── sw-kill.js — the escape hatch, if sw.js ever needs uninstalling
            ├── all state ──► browser localStorage (source of truth, works offline)
            └── signed in ──► Firestore doc paptrack/{uid} (newer-wins by updatedAt,
                              with the empty-never-beats-data guard; live onSnapshot
                              updates on other devices)

Backup/restore via JSON export & import.
```

There is no server of our own — the only backend is the optional Firebase (auth + one Firestore document per user, free tier). Any static host can serve the app (locally: `python3 -m http.server 8011` in the folder), and it degrades to fully-local mode when Firebase is unreachable or the user is signed out. Since the palette moved into `theme.css`, opening `index.html` straight off disk isn't supported — serve the folder instead (see the note at the top).

**The icon** is the airflow mark the [iOS](https://github.com/eagleadams86/paptrack-ios) and [Android](https://github.com/eagleadams86/paptrack-android) apps wear — a source dot with three arcs radiating out. `make_favicon.py` takes the shipped iOS icon as its master, repaints the rings and writes all three web copies from that one image: `favicon.ico` and the two base64 PNG data URIs in `index.html`. It recolours rather than redraws, so the shapes can't drift. The one deliberate difference from the phone icons is the colour: they fade each ring by alpha down to a nearly invisible outer arc, which read as dim beside the other apps in a row of browser tabs, so the web ramp runs between the shared accent tones instead. Re-run with `python3 make_favicon.py`, then bump the `?v=` on the `favicon.ico` link.

**Tests:** `tests.html` (open it via a local server, e.g. `python3 -m http.server 8011`) loads the real `index.html` in a hidden iframe and pins the web-only pure functions — the untrusted-input validation that guards backups and synced data, and the `.ics` calendar generation. No build step, no frameworks; the page either says "All N tests pass" or lists what broke. The shared schedule math is additionally pinned by the [iOS](https://github.com/eagleadams86/paptrack-ios) and [Android](https://github.com/eagleadams86/paptrack-android) unit-test suites.

**It only runs on localhost, and enforces that itself.** The test code writes nothing, but the iframe boots the real app — and GitHub Pages publishes `tests.html` next to it, at `/paptrack/tests.html`, where that iframe would be your signed-in copy: sync would start inside an invisible frame, and the which-copy dialog could fire where nobody can answer it. Two guards. The iframe carries `data-pap-tests`, which the sync module checks so it never initialises in the harness; and a gate at the foot of `tests.html` checks `location.hostname` and, anywhere but `localhost` / `127.0.0.1` / `[::1]`, never creates the iframe at all — it explains why and says how to run the suite properly. CI reaches the page on `localhost:8011`, so it is unaffected.

![tests](https://github.com/eagleadams86/paptrack/actions/workflows/tests.yml/badge.svg)

The suite also runs on every push: [`.github/workflows/tests.yml`](.github/workflows/tests.yml) serves the folder, opens `tests.html` in headless Chromium and fails the build if the summary goes red or the page throws — same workflow as the rest of the app family.

---

## Working Offline

The app keeps a copy of itself on your device, so it opens with no network at all. Your
supplies were always local, so once the page loads everything works: marking things cleaned
or replaced, the countdowns, the calendar export, backups. Sync is the one thing that can't —
it needs the network by definition, and picks up again on its own when you're back.

What's kept is only the app's own public files — the page, the stylesheet, the privacy policy
and the icon, the same files anyone can read on GitHub. **Nothing of yours is ever put
there**, which matters more than it sounds: every one of these apps shares a single browser
origin, so that cache is not private to this app.

The network is always tried **first**, and the stored copy is used only when it genuinely
doesn't answer (or takes more than five seconds), so you can't be left on an old version
while you're online.

**If one device is behind** — every saved copy now carries the data format the app that wrote
it understood. A copy written by a *newer* version than the one you're running won't be
opened: you get a card saying so, nothing is changed or deleted, and reloading picks up the
current version. A backup file from a newer version is refused the same way, without
stopping the app you're using. Copies written by the iPhone and Android apps carry no marker
at all, which reads as "not newer", so they are never affected by this.

`sw-kill.js` sits in the repo unused, as an escape hatch: copying it over `sw.js` and pushing
makes every installed copy uninstall itself and go back to being an ordinary online-only
page.

---

## When Google's Code Loads (2026-08-22)

**Not on an ordinary visit any more.** `init()` used to run unconditionally at the foot of the
sync module, so `firebase-app`, `firebase-auth`, `firebase-firestore` and the Google sign-in
client were fetched from `www.gstatic.com` and `accounts.google.com` before anyone had touched
anything — four requests to Google carrying the visitor's IP and user-agent, on a page that
might never sync. That is what made the old privacy wording false; this is the change that
lets the strong sentence be true.

It cannot be made *fully* lazy, and that is the whole difficulty: a returning signed-in reader
has to be recognised **without clicking anything**, and the only thing that knows whether this
browser holds a live Firebase session is Firebase. So the app records the answer itself:

| `pap-sync-live` | meaning | on load |
|---|---|---|
| `'1'` | a session was live at last report | load Firebase now |
| `'0'` | there was none, or they signed out | load nothing |
| absent | never asked, or a browser from before this change | fall back to the legacy `pap-sync-uid` marker |

`onAuthStateChanged` writes `'1'` or `'0'` on **every** auth report, including the null one
that follows signing out — so signing out stops the requests, not just the syncing. The
`absent` case is the migration and costs at most **one** eager load per browser:
`pap-sync-uid` has been written on the first successful sync for an account since long
before this, and is never removed, so its presence means "this browser has signed in at some
point". A browser that has never signed in has neither key and never takes that path.

**The warming is load-bearing, not an optimisation.** `requestAccessToken()` has to be called
from inside the click handler or the browser judges the popup unsolicited and blocks it, and
awaiting a cold SDK import first would spend the gesture. So the load starts on
`pointerenter`, `pointerdown` and `focus` — all of which fire *before* click. `onClick` still
awaits `ensureInit()` as a fallback, for somebody who tabs straight to the button and presses
Enter; if the popup is refused there, the existing `popup_failed_to_open` message says what to
do and the second press always works. `ensureInit()` is idempotent, or a hover and a click
would start two Firebase apps.

The click listener is wired at the **boot branch**, not at the end of `init()` — `init()` may
not have run yet, and the button has to be pressable in order to be what causes it to run.

`tests.html` pins the shape of all of this, and the privacy page's wording with it.

## Firebase Version

All three sync apps are on the **same** Firebase version, moved together, exactly like the
vendored Chart.js: `package.json` pins it for Dependabot and `tests.html` pins the manifest to
the `firebasejs/…` URL in `index.html`, so a manifest-only bump fails. Bumping means changing
the URL and the pin in the same commit, in all three repos, and then proving a real Google
sign-in still works on the live origin.

## What Watches the Firebase SDK (2026-08-21)

The one genuinely third-party thing this app runs is Google's Firebase SDK, and it is loaded
by **URL** from `www.gstatic.com` — so nothing was watching it. Dependabot reads manifests, and
no manifest named it; the clean bill of health it reported covered nothing at all. (There are
no known advisories against the pinned version — the problem was that nobody would have been
told if there were.)

`package.json` is that manifest. It installs nothing — it is `private`, has no `scripts`, and
CI passes `--omit=dev` — and the bytes that run still come from Google's CDN at page load.
That creates the same way of ending up lying that a vendored library has: **Dependabot cannot
rewrite a URL**, so a version-bump PR would raise the manifest while the page went on fetching
the old one. `tests.html` pins the manifest's version to the `firebasejs/…` URL in
`index.html`, which makes a manifest-only bump fail and turns the PR into the right
instruction: *a newer SDK exists, now change the URL too.*

Never let that pin become a `^` or `~` range — a range cannot be checked against a URL.


## Privacy Policy

[`privacy.html`](privacy.html) is the web app's privacy policy, linked from the footer — what
the app stores, what the optional Google sign-in puts in Firestore, and how to have a synced
copy deleted. It exists because other people can sign in with their own Google accounts. The
iOS app has its own policy in the [paptrack-support](https://github.com/eagleadams86/paptrack-support)
repo; if what either app stores changes, update both in the same commit.

Since 2026-08-21 it carries **the family footer and the family landmarks**, which it had never
had — the repo under **How it works**, the authorship line, and a real `<main>` / `<footer>`
pair. It is a public page reached by a link in the app's own footer, so somebody who followed
that link landed on a document with no way back to what it documents and no statement of who
wrote it. `</main>` closes **before** the `<footer>`: a `<footer>` nested inside `main` is not
contentinfo at all, it is a plain footer for that section — so `.wrap` stays an ordinary
`<div>`. There is deliberately no privacy link in it; you are standing on that page.
`tests.html` asserts the elements *and* their order, with HTML comments stripped first, because
the notes beside both elements name them in prose.

## Commit Messages

Commit subject lines are written in plain English a non-developer can read (what changed and why it matters, not implementation detail). The in-app "Recent changes" panel that listed them was removed in August 2026, along with the GitHub API entry in the page's CSP.
