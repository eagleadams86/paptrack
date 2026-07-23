# PAPTrack — Web

**Live:** [eagleadams86.github.io/paptrack](https://eagleadams86.github.io/paptrack/)

PAPTrack keeps CPAP supplies on schedule three ways at once: **cleaning** (daily/weekly reminders), **replacement** (countdowns per the standard DME schedule), and **inventory** (spares on hand with reorder flags). Built from a supplier's "clean & replace your equipment" flyer.

This is the **web version** — the whole app in a single self-contained `index.html`. Open it directly in a browser (`file://` works) or use the live link above. No build step, and no account is ever required (an optional Google sign-in adds cross-device sync — see below).

### The PAPTrack family

| Platform | Repo |
|----------|------|
| 🌐 Web (this repo) | [eagleadams86/paptrack](https://github.com/eagleadams86/paptrack) |
| 🍎 iOS | [eagleadams86/paptrack-ios](https://github.com/eagleadams86/paptrack-ios) |
| 🤖 Android | [eagleadams86/paptrack-android](https://github.com/eagleadams86/paptrack-android) |
| 🛟 Support & privacy | [eagleadams86/paptrack-support](https://github.com/eagleadams86/paptrack-support) |

---

## Built-in supply presets

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
- **Replacement countdowns** — every item shows its next due date with urgency-colored badges (red when overdue, orange/amber as the deadline nears, otherwise green); the list sorts most-urgent first. Thresholds scale with each item's cycle (amber at ≤40%, orange at ≤20%, capped at 14/7 days), so a 2-week consumable isn't flagged "replace soon" the day it's replaced
- **As-needed consumables** — set "Replace every" to 0 (or tap the **As needed** chip) for items with no fixed schedule, like distilled water: no countdown or due date, they sort last, and reordering is driven purely by the spares count
- **Cleaning tracker** — items show "Cleaning due" or "Cleaned today/yesterday/N days ago"; one-tap **Mark cleaned**, plus a **Mark all items clean** button that marks every item with a cleaning schedule as cleaned today. The add/edit form groups fields into **Cleaning · Replacement · Spares** sections (matching the native iOS app) and lets you set both the last-cleaned and last-replaced dates directly
- **Last cleaned & last replaced** — every card shows how long ago the last replacement and cleaning happened (today / yesterday / N days ago; "Not cleaned yet" until the first one)
- **Inventory & reorder** — a spares counter with −/+ steppers on every card; items are flagged **Reorder** whenever spares fall to the item's threshold. **Replaced today** resets the countdown and consumes a spare automatically (and hides for the rest of the day so it can't be pressed twice)
- **Card layout** — each supply is a 2×2 quadrant grid — 🧼 Cleaning · ↻ Replacing · 📦 Spares · ⚙️ Manage — matching the native iOS app
- **Stat tiles** — three centered tiles, one per filter: 🧼 Clean due, ↻ Replace due, and 📦 Reorder, each showing a count and the affected items' emoji (or an all-clear check)
- **Search & filters** — live search plus three chips: 🧼 Clean due, ↻ Replace due (due today or overdue), 📦 Reorder due; tapping the active chip again clears it back to showing everything
- **Calendar reminders** — one-tap `.ics` export per item with up to three events: next replacement (alarm 2 days before), a reorder reminder ahead of it (half the cycle for short-cycle consumables, at most 30 days — the typical insurance resupply window), and the next cleaning for items cleaned less often than daily
- **Resupply tip** — footer note about insurance PAP-adherence requirements and humidifier care (distilled water, empty every morning)
- **Private & offline** — all data in `localStorage`; JSON backup export/import; no account required
- **Cross-device sync (optional)** — a **☁️ Sign in to sync** button in the header signs in with Google and syncs via Firestore, so phone and computer share the same data live; signed out, the app is 100% local (see below)
- **7 themes, Midnight by default** — dropdown in the header, listed alphabetically (Forest, Light, Midnight, Sepia, Slate, Solarized, Synthwave); choice saved in `localStorage` and applied before first paint

---

## Cross-device sync (Firebase, free tier)

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

The config object is not a secret (access is controlled by the rules above, which restrict each user to their own document). Because the authorized domain is `eagleadams86.github.io`, sign-in and sync work identically at this repo's `/paptrack/` path and at the old `/prototypes/` path — no Firebase change was needed for the move.

How sync behaves: `localStorage` stays the source of truth. The **first** time a given Google account signs in on a browser, if both the browser and the cloud already have items saved, a dialog asks which to keep ("Keep this device" vs. "Keep Google's data") instead of guessing — silently picking the most-recently-changed side once wiped out a browser's data when an unrelated/stale cloud doc happened to have a newer timestamp. After that first reconciliation (tracked per-account via a `pap-sync-uid` flag in `localStorage`), and for live updates pushed from other devices, whichever side changed most recently (`updatedAt`) wins. Signing out or losing connectivity just leaves the local copy in charge.

---

## Architecture

```
GitHub Pages (static hosting, this repo, main branch)
    └── index.html — single file; loads the Firebase SDK from gstatic.com
            ├── all state ──► browser localStorage (source of truth, works offline)
            └── signed in ──► Firestore doc paptrack/{uid} (last-write-wins by
                              updatedAt; live onSnapshot updates on other devices)

Backup/restore via JSON export & import.
```

There is no server of our own — the only backend is the optional Firebase (auth + one Firestore document per user, free tier). The app works from a double-clicked file just as well as from GitHub Pages, and degrades to fully-local mode when Firebase is unreachable or the user is signed out.

---

## Recent changes feed

The in-app "Recent changes" panel fetches this repo's last 10 commits for `index.html` from the GitHub API. **Commit subjects are user-facing** — write them in plain English a non-developer can read (what changed and why it matters, not implementation detail).
