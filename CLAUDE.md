# PAPTrack — Web

The web version of PAPTrack, a CPAP supply cleaning/replacement/reorder tracker. Deployed via GitHub Pages: https://eagleadams86.github.io/paptrack/

This is a real, shipped product — the flagship web build alongside the native apps ([paptrack-ios](https://github.com/eagleadams86/paptrack-ios), [paptrack-android](https://github.com/eagleadams86/paptrack-android)) and the [paptrack-support](https://github.com/eagleadams86/paptrack-support) site. It graduated out of the shared `prototypes` repo (where it lived as `cpap-tracker.html`).

- **`button, select, input, textarea { font: inherit; color: inherit; }` is load-bearing, and this app went without it until 2026-08-21.** Form controls do NOT inherit the page's typeface — each takes the browser's own default, which on macOS is Arial — so every control here was set in Arial while the prose was in the system face: the header buttons, the theme picker, the search box, every field in every dialog. Subtle enough to live a long time unnoticed; what surfaced it was a header glyph, because Arial draws `⇩` as a thin outline where the system face draws a solid one, and PAPTrack's download arrow came out visibly skinnier than the same character in the sibling apps. Every sibling had this line already. `font`, not `font-family`, which is the family's version — every control that cares states its own size after it, so nothing is left on the UA's 13.33px default either.
- **The header buttons wear a glyph in front of the word** (2026-08-21) — plain text characters, NOT emoji and not an icon font: one more file to fetch is the last thing a header painted this early needs, and a text glyph inherits the theme's colour for free, so it can never become the thing that carries a meaning by hue. Each is `aria-hidden` — the word beside it is already the whole label. The glyphs are Money Map's own where the same button exists there (`⇩` Back up, `↗` Share, `⚙` settings), so one action looks the same in every app, and `☰` is the list/manage one the three list-managing apps share. Added to Sprint Predictability, Flow Metrics, Golf Handicap and PAPTrack in the same commit.
- The app is **`index.html` plus `theme.css`** — no build step, no server. **It was one self-contained file until 2026-08-18**, when the palette moved from an inline transcription to the theme pack's generated `theme.css`, linked, and every token was renamed to the pack's own name. That was the user's explicit call, made against the trade-off: every web app now reads the same bytes and can be diffed against the pack line for line, at the cost of `index.html` no longer standing alone — **`theme.css` has to travel with it, and opening the HTML off disk without it gives an unstyled page.** Don't re-inline the palette to "restore" the single file, and don't rename the tokens back. Everything ELSE stays inline: no second script, no bundler, no CDN calls beyond the Firebase SDK.
- **Token names are the PACK'S names now.** The old app-local names map: `--page`→`--bg`, `--ink`→`--text-primary`, `--ink-2`→`--text-secondary`, `--muted`→`--text-muted`, `--hairline`→`--border`, `--accent-ink`→`--on-accent`, `--chip-bg`→`--surface-alt`, `--good`→`--ok`, `--warning`→`--warn`, `--critical`→`--err`, and each `-bg` partner. `--serious`/`--serious-bg` were defined and never used; the pack supplies them. **This app now owns NO colour token of its own.** `--shadow` was the last one — a per-theme drop shadow declared after the link, as Flow Metrics, Money Map and Sprint Predictability each declared their own (with three different sets of numbers, none of them a pack token). All four went on 2026-08-23: Charles was shown the same window with the shadow, without it, and with a deliberately heavier one, in all four themes, and could not tell them apart — on a dark theme a black shadow falls on a surface that is already almost black, and a modal's own backdrop hides what is left. No elevation shadows anywhere in the family now; it is hard rule 14 in the pack, and its `check_consumers.py` fails a page that adds one. **There was a second, `--ring`, and it went on 2026-08-22** — an invented TRANSLUCENT focus colour (0.14–0.30 alpha) that composited to 1.28–1.60:1 against its own field, where WCAG 1.4.11 asks 3:1. The pack already ships a solid `--focus-border` per theme and three siblings were already using it; this app's own skip link was too. Don't reintroduce an app-local focus colour.
- `tests.html` uses no palette tokens and links nothing, so its CSP was left alone. `index.html`'s CSP already allowed `style-src 'self'`; a page that doesn't is the trap here, because a blocked stylesheet renders as an unstyled page rather than an error.
- No account or sign-up is ever required. The only exception is an **optional** Google sign-in for cross-device sync, backed by the `paptrack-6c817` Firebase project (auth + one Firestore doc per user, free tier). `FIREBASE_CONFIG` at the bottom `<script type="module">` block controls it; set it to `null` to force fully-local mode. See README for the full setup.
- Firebase authorized domain is `eagleadams86.github.io`, so sync works at this `/paptrack/` path unchanged.
- **`pushNow()` sends the items through JSON (`forCloud()`), exactly as `save()` writes the local copy** — so the two are the same bytes by construction rather than nearly so. Don't "simplify" it back to handing the live array straight to `setDoc()`: Firestore walks that object and rejects the **whole document** over a single `undefined` anywhere in it (`invalid-argument`), where localStorage silently drops the key and carries on. That asymmetry cost Sprint Velocity its sync on 2026-08-12 — one new optional field, absent from every copy saved before it existed, written back as undefined by its sanitiser — with the local copy looking perfect throughout. `normalizeItem()` here rebuilds every record as a fresh literal with a concrete default for every field, so it can't produce one today; the guard is for the next field added to that list. Pinned in tests.html by **key**, not by value: `x === undefined` passes whether the key exists or not.
- **Sync failures are surfaced, not logged.** `syncError` + `setSyncError()`/`clearSyncError()` drive `updateUI()`, so the button reads "⚠️ Not syncing" and the privacy note carries the cause and the remedy; `describeSyncError()` maps Firestore codes to plain English. Ported back from Sprint Velocity on 2026-08-12 — this app is the one that sync was ported *from*, and it was the last of the four still failing silently, which meant a sync that stopped working was completely invisible: the button went on showing the account name while nothing left the browser. Every catch site feeds it — the debounced push, `startSync()`, the keep-this-device re-push, and the `onSnapshot` **error callback**, which was missing entirely (a listener that errors is dropped by Firestore and never fires again, so without that second argument another device's updates just stop arriving). A successful `pushNow()` is the only thing that clears it, which is why there's deliberately no retry button: transient causes are retried by the SDK, permanent ones aren't fixed by pressing anything, and the next save recovers the state on its own. The toast fires on the *transition* only, never per retry. `onAuthStateChanged` resets `syncError` because signing out and back in is the remedy half the causes suggest — a stale warning must not survive it.
- **`attachSnapshot()` is guarded by `!unsub` at BOTH call sites** — the tail of `startSync()` and pushNow's re-attach. The push paths of `startSync` already attach the listener inside `pushNow()`, so an unguarded attach at the tail opened a second `onSnapshot` and overwrote `unsub`, leaking a listener nothing could detach: doubled reads on every signed-in load, plus a spurious "Not syncing" toast at sign-out when the orphan erred. That exact leak shipped for a day after the 2026-08-17 re-attach fix. Pinned in tests.html: every `attachSnapshot();` call must carry the guard.
- **`cloudPush`/`cloudFlush` defer behind `reconciled` until `startSync()` settles.** An edit made in the window between sign-in and the which-copy decision must not `setDoc` over the cloud copy the dialog is still offering — "Keep Google's data" would then adopt a snapshot the cloud no longer held. The edit is not dropped: it sets `pendingLocalPush`, and `reconciliationDone()` — called via `.finally`, so a FAILED reconciliation lifts the gate too, keeping the "next change will try again" promise honest — sends it as soon as the decision lands. Also pinned in tests.html by source.
- **`invalid-argument` does not mean "too big".** Firestore uses that one code for both an oversized document and a value it can't store, so the size wording waits until Firestore's own message mentions size; otherwise it says the fault is in the app and asks for nothing to be deleted. The sibling apps assumed size and so told users to delete their data over an app bug. A remedy that destroys data must never be the guess.
- The sync-error UI is **module-scoped**, so tests.html — which reaches classic-script functions only — can't pin it, and **nothing in CI covers it**. It was verified when ported by lifting the shipped function bodies out of `index.html` into a `new Function(...)` with a stub `btn`/`privacyNote`/`window.toast` and asserting each state (signed out, healthy, failed, recurring, recovered). If you change this code, do that again rather than trusting it: no red test will tell you it broke. Don't add a node script to the repo for it — this app has no build step and no dependencies, and that's worth more than the convenience.
- **Sign-in uses Google Identity Services, not Firebase's popup.** `GOOGLE_CLIENT_ID` + `initTokenClient()` opens a popup straight to `accounts.google.com`, and the OAuth access token it returns is exchanged for the same Firebase session via `signInWithCredential`. Firebase's `signInWithPopup` is **gone on purpose**: it opens at `<project>.firebaseapp.com/__/auth/handler` first, and **this project's hostname is confirmed blocked on a corporate network**. Filters block *individual* `firebaseapp.com` hostnames, per hostname rather than per domain — on one network on one day this app's and Team Dashboard's were refused while Sprint Velocity's went through, with identical code. So `firebaseapp.com` and `apis.google.com` are **not** in the CSP; only `accounts.google.com` is, in `script-src`, `connect-src` and `frame-src`. `authDomain` stays in `FIREBASE_CONFIG` because the SDK requires it, but nothing loads it. The client ID is **not** in `firebaseConfig` — Cloud Console → Credentials → *Web client (auto created by Google Service)*, whose **Authorized JavaScript origins** must list this app's origin (exact, port included) or Google returns `origin_mismatch`. All four web apps do this, all confirmed working on the network that needed it, 2026-08-07. Auth is built with `initializeAuth`, **not `getAuth`** — `getAuth()` always wires in `browserPopupRedirectResolver`, which the SDK initialises at startup, pulling in `apis.google.com/js/api.js` for the popup-redirect gapi iframe nothing here reads (it showed up only as a CSP console error). The persistences passed in are `getAuth`'s own, in its order. Don't go back to `getAuth()` to "fix" a popup/redirect call — pass the resolver to that call instead. Same change in Team Dashboard, Sprint Velocity and Golf Handicap. **Web only — and this is the architecture the native apps always had: iOS (GoogleSignIn-iOS) and Android (Credential Manager) already obtain a Google credential from the platform and hand it to the same `signInWithCredential` call, never touching a hosted handler. Neither needed any change.**
- **The web shell is the app family's, not the phone app's, since 2026-08-21.** It had been a 760px column with the header inside it — a phone layout shown on a desktop — and it now matches the family: `--page-w`, read by BOTH `.wrap` and `.headbar` (they must be the same number or the brand stops lining up with the first card), a **sticky full-width header** with the row inside held to that width, and the family's one-line brand — 22px mark, name, then a muted `· CPAP Supply Tracker` behind a middle dot. Consequences worth knowing before touching any of it:
  - **`--page-w` is 2400px, Money Map's number, since 2026-08-22.** It was 1500px for a day (Sprint Predictability's and Flow Metrics'), and 760px before that. Nothing on this page stretches to the width — the cards flow into columns — so every extra 400px buys another column rather than a wider card. Change it in `:root` only: both `.wrap` and `.headbar` read it, and they must stay the same number or the brand stops lining up with the first card.
  - **The supply list is a GRID, not a column; the floor is a MEASURED number and THREE COLUMNS IS THE CEILING** — `repeat(auto-fill, minmax(max(min(660px, 100%), calc((100% - 24px) / 3)), 1fr))`. **660px is the narrowest card that keeps a status badge on one line**, measured across every badge the loaded kits produce (the longest, "Replace by <date> · 180 days left", sets it at 656; 660 is that plus rounding). It was 400px — the narrowest card whose tiles still hold a date — and at 400 every badge wrapped to two or three lines. The rule Charles asked for on 2026-08-22 is that **the row loses a column at the width where the pills would otherwise wrap**, so the floor has to be re-measured, not guessed, if the badge wording or the type scale ever changes. Consequence to know before it surprises you: **a ~1300px window shows ONE card**, because two would be 634px and 634 wraps. A cycle long enough to print four digits of "days left" needs ~680 and will wrap — a deliberate stop, since 680 costs a whole column at 1400px. The cap arrived with the 2400px width on 2026-08-22, where plain auto-fill gave five cards to a row and the 2x2 tiles inside a card were down to the width of their own labels. It is written as the column MINIMUM rather than `repeat(3, 1fr)` so everything underneath is untouched: the larger of the two terms wins, so a third of the row wins from about 1250px up and the 400px card floor wins below it (two columns, then one). The `24px` is the two 12px gaps a three-column row carries and must move with `gap` — `tests.html` pins that it is twice the gap, and pins both terms by source. The `min()` is load-bearing: a minmax *minimum* is not a suggestion, so a bare `400px` lays out a 400px column on a 375px phone and the card hangs off the screen, scrolling the whole page sideways. The 400px floor (not the 460 tried first) is what pairs the cards at a ~900px laptop window instead of showing one stretched card.
  - **Cards in a row are the same height, and so are the tiles inside them.** The grid's default stretch does the first; `.card` is a flex column and `.quadrants` carries `flex: 1` + `align-content: stretch` so the spare height goes into the tiles rather than leaving a gap under them. Don't put `align-items: start` back on `.list` — a ragged bottom edge on a row is exactly what this fixed.
  - **`body` no longer carries a top safe-area inset; the header does.** An inset on the body would either push the sticky bar off the top of the screen or leave its background short of the status bar. The other three insets stay on the body, which is also where the bar should stop in landscape on a notched phone.
  - **Notes is a TEXTAREA and lives in the Name section; the preset has its own row** (2026-08-22). Notes was a single-line `input` in a section of its own at the bottom, which truncated the notes the app itself ships with ("Cushions break down and lose their seal over time." arrived cut mid-word) and, being the odd seventh section, sat alone in the last row of a two-column grid with a tall empty card. It is now `rows="3"` beside the name it describes. Two consequences: the section holds two controls, so it can no longer borrow its heading as their accessible name and each field carries a real `<label for>`; and `data-keep-caret` on it is belt-and-braces now, because `SELECT_ON_FOCUS` is keyed on an input's `type` and a textarea has none — it stays to record the intent if the control ever changes back.
  - **Two cards on a form row are the SAME HEIGHT, and `align-self: start` was tried and reverted the same day.** The matching is the grid's own default `stretch` on the card in subgrid row 2 — `flex: none` beside it only neutralises the fallback layout's `flex: 1 1 auto` and is not what does the work. The cost is real and known: Spares runs ~170px longer than its two number fields need, because Ordering beside it has three. **That was 'fixed' with `align-self: start` on 2026-08-22 and reverted within the hour on Charles's call** — a ragged row reads as a layout that has come apart, where a tall card with space at the bottom just reads as a tall card, and it is the same rule the supply cards in the list already follow. Don't reintroduce it. The preset section is unaffected either way, being alone on its row.
  - **`grid-column: 1` is set on BOTH `#presetField` and `#nameField`, and neither is redundant.** The preset's puts it in the left column; the name's is what pushes Name & Notes onto a new row — without it, auto-placement drops it into the empty cell beside the preset, which is the pairing being undone. The preset is deliberately NOT full-width: stretched across, it was a 770px box holding "😷 Mask".
  - **The add/edit dialog is 820px and lays its sections out two-across at ≥860px**, with the preset and name spanning both columns so the form does NOT rearrange between adding (preset shown) and editing (preset hidden). Paired sections are matched with `grid-template-rows: subgrid` over a three-row span — heading, field card, footnote — because only two of the four sections have a footnote, and a plain stretch hands the spare height to whatever is elastic (it made the Notes card 60px taller than its single input needed). The `@supports` fallback is the flex stretch, not a broken layout.
  - **`--chrome-h` is 30px, the siblings' number, and the bar is 51px tall — byte for byte Sprint Predictability's.** It was 40px on the reasoning that the theme picker had always been 40px and the buttons should meet it; that was fine while the header scrolled away, but a sticky bar spends its height on every screen. `.top-actions .act` cuts its vertical padding to 4px to suit, or the coarse-pointer 16px label doesn't fit the 30px box.
  - **The theme picker's `<option>`s carry `selected` on AUTO — the default since 2026-08-22, midnight before it — and the sun is `☀` not `☀️`** (2026-08-21). Without `selected` the browser pre-selects the FIRST option, so the row painted "☾ Dark" over a midnight page until `$('themeSel').value = ...` ran at the foot of the file — and the header paints long before that. The emoji-presentation sun is drawn from the colour font: a different weight and baseline from the `☾` and `✦` beside it, so the row read as three different sets of glyphs. Every sibling app already followed both rules; `tests.html` pins the four labels exactly, asserts `defaultSelected` on auto, and asserts that only one option carries it.
  - **The header controls wear the FAMILY's button, not this app's** (2026-08-21): `--surface-alt` on `--border-strong` at `--radius-sm`, darkening the border on hover — Sprint Predictability's object, which Golf Handicap, Flow Metrics and Money Map all carry. They wore `--surface` on plain `--border` at a 12px radius, a quieter and rounder control that sat a shade darker than the bar behind it, so beside a sibling app the two rows read as different furniture. The theme picker takes it too: in this row a `<select>` is a thing you PRESS. **Scoped to `.theme-sel, .top-actions .act`** — `.act` is used 17 times across the cards, dialogs and empty state, and none of those should move; the same scoping rule as the `--chrome-h` height above it.
  - **The add button does not float, and the toolbar is one uniform row** (2026-08-22). `+ Add Supply` was `position: fixed` in the bottom-right corner, a 999px pill at 12/18 padding and 700 weight carrying a 44px thumb target. That is a phone pattern: on a desktop it hovered over the list as the only control in the app that was not part of the page, and no sibling has a pill or floats anything. It is now a plain `.btn primary` in the toolbar row, between the search box and the filters — Golf Handicap's `+ Add Round` is the same object in the same relationship to the list it adds to. Consequences: the `.wrap`'s 64px bottom padding is now only the family number (it was also holding the last card clear of the FAB), the header's z-index note no longer has a FAB to clear, and `tests.html` pins `position: static` and the family's 7px/12px padding and `--radius-sm` corner — through the COMPUTED STYLE, not a box, because the harness sits in the empty state where the toolbar around the button is hidden and every rect reads zero.
  - **Everything in that row is a 40px control on one line, and the filter caption sits BESIDE its chips.** It reads "Filters:" now; "Filter — tap to toggle" was stacked above them and was the widest thing in the block, so the filter block was two lines tall and set the row's height: `.toolbar` stretched the search box to 57px to match while the chips stayed at 33px, and dropping a 40px button between them made three different heights obvious. The add button is the reference box — it is the family's button and its size is not this app's to choose — so the chips come up to 16px/7px/12px and the search box and `Mark All Due Items Clean` are held at its 40px. **`.cleanall` and `.filter-chip` are re-stated inside the media query and `.cleanall` must be written as `.toolbar .cleanall`**: `.act` is declared several hundred lines LATER in the file with its own `--fs-xs` and 8/12 padding, so an unqualified `.cleanall` loses the tie and the button silently keeps the small text. Below 720px the row still stacks full-width, caption above chips.
  - **The filter chips have a hover state** (2026-08-22) — the family's, `--text-muted` border with the fill stepping to `--surface-alt`; a pressed chip is filled, so it takes `.btn.primary`'s `.88` opacity instead. `.filter-chip:hover` is declared BEFORE `.filter-chip[aria-pressed="true"]` on purpose: both are two-specificity selectors, so the tie goes to the later rule, and a hover written after it repaints a pressed chip in the unpressed colours.
  - **The header controls run theme → Back up → sync**, and the sync button is last on purpose: it is the only control in the row that changes width as you use it ("Sign in to sync" → an account name → "⚠️ Not syncing"), so at the end its growing and shrinking moves nothing but itself. Anything placed after it shifts sideways every time sync changes state.
  - **The empty state has no app mark, and on a wide screen it is a PANEL, not a centred column.** The mark was a 72px copy of the one now worn in the header two inches above it, on the one screen where a first-time visitor sees both. And at ≥720px the block becomes a bordered card the width of the content, prose left and the three ways to start on the right — a narrow stack of centred text floating in the full page width of nothing read as a page that had failed to load. Same elements in the same markup order, so the phone layout and the screen-reader order are untouched. The lede is capped at 80ch there (44ch is the cap for the centred phone column; uncapped it ran ~1100px as one line).
  - **`openForm` moves focus off the preset picker on a coarse pointer, and that line is NOT in the shared helper.** `openModal`/`raisesKeyboard` are byte-identical across Sprint Predictability, Flow Metrics, Money Map, Golf Handicap and here, and they treat a `<select>` as harmless because it raises no keyboard — right for all four siblings, none of which opens a dialog on one. This form does: adding starts on the preset picker, so on a phone the window opened with a dropdown already grabbed. The fix therefore lives at this app's own call site rather than diverging the shared function. Editing was already covered (`openModal` moves off the Name field), and a fine pointer keeps click-and-type in both.
  - **Dialogs cap their height and contain their scrolling** — `max-height: calc(100vh - 32px)`, `overflow: auto`, `overscroll-behavior: contain`. Without the last one a scroll that runs out inside a dialog hands the rest of the gesture to the page, which scrolled away underneath a dialog still covering it. Found in Money Map and fixed across the family 2026-08-17; this app was missed and joined 2026-08-21. `vh`, not `dvh` — dvh resolves to 0 in some embedded engines.
  - **`color-scheme` is set per theme** — the only thing those four blocks carry now, `--ring` and `--shadow` having both gone — `dark` for midnight and dark, `light` for light AND sepia (sepia is a warm *light* theme). It is not one of our colours and overrides nothing in the pack; it is how the page tells the browser which way round it is, so browser-drawn UI follows. Without it the calendar button inside every `<input type="date">` was a near-black glyph on a near-black field on the two dark themes — and that glyph is not restylable from CSS. Money Map does the same, in the same place.
- **The app is INSTALLABLE on a Mac or a PC (2026-08-21), and offline is a separate, older thing.** `manifest.webmanifest` is what turns Chrome's "Install page as app…" into a real install — its own window, its own Dock/taskbar icon. It needs three things kept in step or installing silently stops being offered, with nothing but a console line to say so:
  - **`manifest-src 'self'` in the CSP.** It falls back to `default-src`, which is `'none'` here, so without the directive the manifest fetch is refused. This is the failure mode to suspect first.
  - **`make_favicon.py` writes the install icons too** — `icon-192.png`, `icon-512.png` (both `purpose: any`, square, the master as it draws it) and `icon-512-maskable.png`. The maskable one is a DIFFERENT picture on purpose: the corner discs are replaced by flat ground (scaling the whole art down instead left them cut off mid-curve as hard quarter-squares) and the mark is recentred, because the master deliberately sits right of middle and a circular crop is centred. Re-run the script rather than hand-editing any of the five copies of the mark.
  - **All four files are on `sw.js`'s SHELL allowlist, and `tests.html` pins that list by exact equality.** Adding an entry means editing the test too — that is the security review, by design. Keep the array free of comments: the test parses the source, and a comment between entries parses as a fake entry (it broke the suite once, on this very change).
  - `<meta name="theme-color">` is rewritten by `applyThemeColor()` from the pack's `--bg`, so an installed window's title bar follows the theme instead of staying dark behind a light page.
  - Offline predates all of this and is unchanged: it is `sw.js`, network-first. The manifest adds the window and the icon, not the caching.
- **The sync button is VISIBLE in the markup and hidden on failure, never the other way round.** It shipped with `hidden` and was revealed at the end of `init()`, so the header painted without it and grew a button once the Firebase SDK arrived — the control cluster jumped left on every refresh. `#syncBtn { min-width: 148px }` is the other half: its three real labels ("☁️ Sign in to sync", an account name, "⚠️ Not syncing") all measure 148px, so changing state doesn't shift the row either. The boot branch's `else { btn.hidden = true }` covers the three cases that can't sign in — no `FIREBASE_CONFIG`, the test harness, and a page halted on newer data. Same rule as Golf Handicap, and the general one for this row: everything is written into the markup at its final size, because the header paints long before anything else runs.
- **The nasal kit has no "Mask" item, and that is not an oversight.** The `mask` preset IS the full-face mask, so it belongs to `KITS.full` only; on a nasal setup the cushion or pillows are the mask. Adding both gave a nasal user a supply they don't own, on its own 90-day replacement clock. The nasal kit is six items, the full-face one seven. Fixed 2026-08-21, the same day `water` was added to BOTH kits — everyone running a humidifier buys distilled water, and as the one preset with no schedule at all it makes a loaded kit demonstrate the as-needed path (no countdown, sorts last, reorder driven purely by the spares count) rather than only the timed one.
- New/changed UI is designed against the **Midnight palette** (deep indigo/navy), which is the family's base palette; what the app *opens* on is `auto`, the default since 2026-08-22, which resolves to Light or Midnight from the reader's own system. The palette (4 themes: Midnight, Dark — formerly Slate — Light, Sepia) is the pack's generated `theme.css`, **linked** — see the bullet at the top of this file. (It was transcribed inline under app-local token names until 2026-08-18, which is what older commits show.) `~/claude-theme-pack` (private repo eagleadams86/claude-theme-pack) stays the source of truth for all apps. Never retune colors here — change the pack's `tokens.json`, run its gate, rebuild, re-copy the generated file into every app, and keep iOS/Android in step (drift policy in the pack's CLAUDE.md).
- **Accessibility was audited properly on 2026-08-22, and what it found was invisible to axe.** axe-core reports this app clean on all four themes, phone and desktop, list and empty state, every dialog, and privacy.html — and it always did, because **axe never focuses anything, so it cannot test a focus indicator**. A Playwright harness in the scratchpad (see the family's axe-audit note) drove the keyboard instead and found four real things, all now fixed and pinned in `tests.html`:
  - **There was no global `:focus-visible` rule at all.** Only the search box, the theme picker and the form fields drew a ring; every BUTTON, LINK and FILTER CHIP fell back to whatever the browser draws. Flow Metrics, Golf Handicap and Money Map all carry `:focus-visible { outline: 2px solid var(--focus-border); outline-offset: 2px; }` — this app was the last without it. It now measures 4.54–16:1 on every control on every theme.
  - **The one ring it did draw failed 1.4.11** — see the `--ring` note above.
  - **The placeholder was the browser's default** — `--text-primary` at the UA's opacity, 3.58:1 on dark, 3.84 on midnight, 4.24 on sepia. Now `--text-muted` at `opacity: 1` (5.3–5.85). The `opacity` half is load-bearing: without it the UA applies its own and undoes the colour.
  - **The filter chips were the one button in the app on plain `--border`** (1.21–1.46:1) rather than the `--border-strong` every `.btn` and `.act` wears.
  - Also added: a `prefers-reduced-motion` block. Only the toast fades, but the rule is written blanket so it keeps covering whatever is added later.
  - **What was already right, and should stay that way:** all 39 tab stops reachable in DOM order with no trap; every dialog takes focus inside, closes on Esc and hands focus back to the button that opened it; no sideways scroll at 320px; the 1.4.12 text-spacing overrides clip nothing; every target at least 24×24 except the inline "MIT licensed" link, which the inline exception covers; and the app stays legible under forced-colors, because every badge states its status in words as well as colour.
- **A form field is `--surface` on `--border-strong`, and it carries a `min-height` that is not decoration** (2026-08-22). The fill was `--bg` — the PAGE colour, the darkest thing in the palette — so a field inside a dialog read as a hole cut through two lighter panels, near-black on midnight; Golf Handicap, Flow Metrics and Money Map all paint a field `--surface` on the pack's `--input-border` (the same value as `--border-strong`), and this app was the only one that didn't. The layering here ends up one better than the siblings', whose fields sit on `--surface` too and are separated by the border alone: this app's `.sec-card` is `--surface-alt`, so the field is a touch darker than the card holding it.
  - **`min-height: calc(1.5em + 20px)` is what stops an empty date box collapsing, and it is invisible on a desktop.** An `<input type="date">` with NO VALUE renders no inner content in **iOS Safari**, and the pack turns the native appearance off — so the content box has nothing to give it a height and falls to its padding. "Last ordered" was a thin empty bar beside a full-height "Cost each"; the two date boxes above it looked fine only because they always have a value. **Chromium always paints "mm/dd/yyyy" and Playwright's desktop WebKit draws its own box, so neither reproduces it** — it was found on a real iPhone and confirmed fixed in the iOS Simulator. The value is in `em` because the pack lifts every field to 16px on a coarse pointer, and a pixel min-height would be wrong there.
- **THREE containers get focused as a mechanism in this app, and the card's rule is OPT IN.** `<main tabindex="-1">` (the skip link's landing) and `<dialog>` take `outline: none` outright — nobody is about to operate them. The supply CARD is `.card:focus { outline: none }` too, with the ring added back ONLY by `.card.ring-focus`, a class `renderKeepingFocus()` applies when it deliberately moved focus there from the keyboard (`e.detail === 0`) and clears on `blur`.
  - **It was written the other way round first — a class that SUPPRESSED the ring on the pointer path — and that was wrong in a way worth remembering.** Suppress-on-pointer only covers the paths the app drives. It missed the one Charles hit next: **coming back from the Edit dialog, where nothing in this file focuses the card at all.** The dialog closes, the browser restores focus to the Edit button that opened it, `render()` rebuilds the list and removes that button, and **WebKit promotes focus to the nearest focusable ANCESTOR** instead of dropping it to `<body>` — and the nearest one is the card, because it carries `tabindex="-1"` for `renderKeepingFocus`. Opting IN cannot fail that way: a path nobody thought about lands on the quiet default. **Reach for opt-in whenever a browser can put focus somewhere you did not.**
  - **Chromium and desktop WebKit reproduce NEITHER card case** — both leave `:focus-visible` unmatched after a tap, and both drop focus to `<body>` on the Edit path. Only the real iOS control does it. Verified in the iOS Simulator; see [[ios-empty-date-input-collapses]] for the other two bugs with the same shape.
  - `tests.html` pins that the card is quiet by default, that `ring-focus` adds it back, and that EVERY `renderKeepingFocus` call site passes the modality — one that forgets rings the card on a phone, and no desktop will show you.
  - **Swept the whole family for this on 2026-08-22 and PAPTrack's card was the only real case.** The other `tabindex="-1"` hits across Golf Handicap, Flow Metrics, Money Map and Sprint Predictability are all ROVING TABINDEX — tab strips, Money Map's year chips and grid cells — where being focused by an arrow key is the whole point and the ring is correct. Don't "fix" those.
- **A dialog focused as a CONTAINER must not ring itself.** On a coarse pointer `openModal()` sets `dlg.tabIndex = -1` and focuses the dialog, so opening a form doesn't drag the keyboard up with it — which means the dialog matches `:focus`, and every phone and tablet drew a ring around the whole window (the browser's own before the focus work of 2026-08-22, ours after). `dialog:focus { outline: none }` is the same exemption `main:focus` already had, for the same reason. A fine pointer never takes that path, so nothing on a desktop will ever show you this.

- **CONTROL BOUNDARIES ARE `--border-control` (fields: `--input-border`), NEVER `--border` or `--border-strong`** — fixed in the PACK on 2026-08-22, not here. Every bordered button in all five apps was identified by a `--border-strong` edge at 1.68–1.92:1 with a fill 1.05–1.22 off the page, which is under the 3:1 WCAG 1.4.11 asks of the thing that identifies a control. Two holes in the pack, and the second is the instructive one: `--input-border` was not gated at all and was carrying `--border-strong`'s value, and `--border-control` WAS gated at 3:1 but only against `bg` and `surface` — it failed `surfaceAlt` in all four themes while passing, and `surfaceAlt` is what a `.btn`/`.act` is FILLED with. The gate now covers all three surfaces and both tokens, and the values moved by the smallest lightness step that clears it. In this app the swap covers `.btn`, `.act`, `.filter-chip`, the header controls and the form fields; the dialog's own edge stays `--border-strong`, because a dialog is a panel. **Don't fix a weak control edge locally** — that is the drift the pack exists to prevent.
- **The badge border is the status signal, not trim.** The `--*-bg` tint fills are pale
  washes built to sit behind text and are nearly identical to each other once red-green
  deficiency flattens them (8.2 apart on the dark themes, 14.2 on the light ones, against a
  bar of 18); the strong status colours clear it at 20.5–24.6, so `.badge` carries a 1.5px
  border in the status colour and that is what makes the four states tell apart. Don't drop
  it back to a fill-plus-dot, and don't thin it to a hairline.
- **`.b-serious` and `.b-critical` share the red on purpose.** Four severities don't fit on
  the axis that survives red-green deficiency — it carries about three levels, and the fourth
  landed 3 apart from its neighbour. `severity()` still returns `'serious'` as its own tier,
  so the split is one CSS rule away if it's ever wanted; the data never stopped carrying it.
- **The cleaning badge carries the same data as the replace badge** — due date, days left,
  days overdue — off `nextClean`/`cleanLeft` instead of `nextReplace`/`replaceLeft`, coloured
  by the same `severity(cycle, days)` bands with `cleanDays` as the cycle. Overdue stays red,
  not amber: it's the same kind of miss as "Replace overdue". It has no special case left: the
  flat red "Cleaning due" for a never-cleaned item is gone, because there is now always a date
  to count from — see the next bullet.
- **The cleaning clock runs from the LATER of the last wash and the last replacement**
  (`cleanedOrReplaced()`, feeding `nextClean()`). A supply out of a fresh packet is clean
  whether or not it was ever washed, so replacing one restarts its cleaning cycle. Before
  2026-08-20 it counted from `lastCleaned` alone, which left a mask you had just replaced
  wearing a red "Clean overdue" badge, a "Mark cleaned" button, a place in the due-to-clean
  count and a calendar reminder — for a wash it did not need. **`lastCleaned` is still written
  only by an actual cleaning**, never by a replacement: keeping it a record of washes that
  happened is what stops the card claiming "Last cleaned today" for a bag you just opened, and
  deriving the clock instead of writing a date also repairs items already saved and covers
  editing "last replaced" by hand, which reaches the same state by another route.
  `lastReplaced` is never null (`normalizeItem` defaults it to today), so the derivation always
  has a date. Ported to iOS (`Schedule.cleanedOrReplaced`) and Android (`Schedule.cleanedOrReplaced`)
  the same day — all three read `max(lastCleaned, lastReplaced)` and must stay in step.
- **`severity()`'s bands are clamped to `cycle - 1`.** Daily cleaning is the reason: without
  it `ceil(1 × 0.2) = 1` puts a mask in the serious band the moment it's cleaned. The clamp
  never binds at replacement cycles (the shortest shipped is 14 days), so replace badges are
  byte-identical to before.
- **The web icon is the shipped native icon's pixels, RECOLOURED — never redrawn.**
  `make_favicon.py` opens the iOS master
  (`~/claude-paptrack-ios/PAPTrack/Assets.xcassets/AppIcon.appiconset/icon-1024.png`),
  repaints the three rings and the dot without touching a coordinate, and writes all
  three web copies from that one image: `favicon.ico` plus the two base64 PNG data
  URIs in `index.html` (`rel="icon"` at 64px, `apple-touch-icon` at 180px). Those
  three are one picture; hand-editing a base64 blob is how they drift, so re-run the
  script instead. **Porting the Android vector was tried first and produced a visibly
  different icon** — `ic_launcher_foreground.xml` is laid out around the adaptive-icon
  safe zone, with a bigger dot, fatter strokes and equal angular spans, where the
  shipped iOS art sits further right with a smaller dot and spans that narrow outward
  (52°, 46°, 40°). That is why this recolours rather than redraws: the geometry can't
  drift because it is never re-derived. Pixel-diffed after the change — 71,683 pixels
  altered, none of them outside the mark.
- **The COLOUR is where the web parts company with the phone icons**, and it was asked
  for. The native rings fade by ALPHA over the page (full accent, 72%, 45%), which
  bottoms the outer arc out near `#40477e`; on a home screen that reads as a signal
  weakening, but in a 16px row of tabs beside the sibling apps it just read dim. The
  web ramp runs between the family's two accent tones instead — `#a5b4fc`, their
  midpoint, then `--accent` — so the falloff survives while every ring stays a colour
  the family uses. The iOS and Android icons still fade to alpha and are deliberately
  left alone: changing those means a new build and, for iOS, a new submission. The
  `.ico` is also left **square**, unlike every sibling's rounded tile, because this art
  is the app icon's and iOS/Android apply their own mask — rounding it would change a
  shape the app already ships with.
- **`favicon.ico` now has a `<link>` of its own** (`rel="alternate icon"`, versioned).
  It had none: the browser only ever fetched it from the site root, so there was no URL
  to version and a cached copy survived an icon change indefinitely. Bump the `?v=`
  whenever the script is re-run; the data URIs need no version, since their content is
  the URL.
- **README.md is the index** — keep it current whenever the app meaningfully changes.
- After changes: **browser-test locally first**, then commit, push, verify the Pages deploy, and spot-check live. To serve locally: the desktop app's preview pane reads `.claude/launch.json` (port 8011); otherwise run `python3 -m http.server 8011` in this folder and drive a browser with whatever automation is available. Any local server + browser works — don't hunt for a specific tool.
- **`tests.html` pins the web-only pure functions — open it on the same local server and check "All N tests pass" whenever you touch `normalizeItem`/`normalizeItems`, the `.ics` generation (`escICS`/`foldICS`/`buildICS`), or `severity`.** It loads the real `index.html` in a hidden iframe and calls the functions directly (they're all plain `function` declarations, so no app-side hook is needed). Needs `http://localhost` — `file://` iframes are blocked in some browsers. **It also refuses to run anywhere else, and that is load-bearing:** Pages publishes `tests.html` beside the app, where the iframe would be the signed-in copy and `onAuthStateChanged` would start a real sync — or raise the which-copy dialog — inside an invisible frame. Two guards, both needed: the iframe carries `data-pap-tests`, which the sync module checks before `init()`, and the gate at the foot of `tests.html` never creates the iframe at all off localhost (booting the app IS the side effect, so the check can't live in the load handler). **`file://` is deliberately NOT in `LOCAL_HOSTS`**: it has no hostname, and `''` used to sit in that list on the reasoning that the suite couldn't run there anyway — but that sent it down the iframe branch, where the frame silently fails to load and the suite blamed the app. Opening the file off disk now gets the advice that fixes it, and a frame that never loaded the app is reported as a setup problem rather than as every test failing at once. Don't put the iframe back in the markup. CI runs the same page headless on every push (`.github/workflows/tests.yml`) on `localhost:8011`, so the gate lets it through, and fails the build if the summary goes red. The shared schedule math is additionally pinned by the iOS and Android test suites.

- **`privacy.html` is the web app's privacy policy** (static page, same midnight shell as the sibling apps, linked from the footer beside the copyright line). Added 2026-08-18 — other people can sign in with their own Google accounts, so it exists for them: what Firestore holds, that rules confine each account to its own data, and the deletion contact. The iOS app's policy lives in the paptrack-support repo; if what either app stores changes, update both in the same commit. **It carries the family footer and the family landmarks since 2026-08-21** — the repo under "How it works", the authorship line, and a real `<main>` / `<footer>` pair with `</main>` closing BEFORE the footer, because a `<footer>` nested inside `main` is not contentinfo at all. `.wrap` therefore stays an ordinary `<div>`; making it the `<main>` would swallow the footer and leave the page with no contentinfo while looking perfectly correct in the source. No privacy link in that footer — you are standing on it — and that absence is asserted, not merely omitted. `tests.html` reads the page and pins all of it, comments stripped first (and stripped in a LOOP, not one pass: CodeQL flags the single-pass form, and a helper that can be fooled about what is commented out is one that can miss a live off-origin script).
- Write commit subject lines in plain English a non-developer can read (what changed and why it matters, not implementation detail). The in-app "Recent changes" section that made them user-facing was removed 2026-08-18, across the whole app family, and the GitHub API went out of the CSP with it.
- **There IS a service worker, and it was refused for a long time.** The three
  objections were right to be made; two turned out to be answerable by design
  rather than by abstention, and the third is what the whole thing is built
  around. Recorded because the next person to touch this needs the reasoning:
  - *"A resident process on the shared origin."* Bounded. A worker's scope
    cannot exceed its own directory without the `Service-Worker-Allowed` header,
    and GitHub Pages cannot send headers — so this one structurally cannot see
    any sibling app. Locally, where the app is served from the
    root, it does control `tests.html`; the allowlist is what makes that
    harmless, not the scope.
  - *"Caches are ORIGIN-wide, not per app."* True, and it does not go away — any
    page on the origin can read this cache, and the sibling workers share the
    store. The answer is the rule in `sw.js`: **only files already public in
    this repo are ever cached** (`./`, `theme.css`, `privacy.html`,
    `favicon.ico`; the tab and touch icons are data URIs in the markup and need
    no entry). Nothing in there is anything an attacker
    could not read straight off GitHub, and the data stays in localStorage,
    which every page on the origin could already reach. It cuts the other way
    too — `activate` must only ever delete caches with this app's `pap-shell-`
    prefix, or it wipes a sibling's.
  - *"A caching bug serves stale code to an app whose data shape moves."* Still
    the real risk. **The worker is network-first for everything**: you can only
    be served cached code on a visit where the network did not answer. The
    braces to that belt is `SCHEMA` / `haltForNewerData()` above — a saved copy
    from a newer build is refused rather than run through normalizeItem(),
    which rebuilds every item without the fields that build added.
- **The page's CSP does not apply to the worker.** It takes its policy from its
  own script's HTTP response headers, and Pages cannot set headers, so `sw.js`
  runs with **no CSP at all**, permanently installed. Hence: tiny, no `eval`, no
  `importScripts`, no dynamic import, no cross-origin URL anywhere in it — and
  hence `worker-src 'self'` spelled out in the page CSP rather than left to the
  `worker-src → child-src → script-src` fallback chain, which would inherit
  script-src's gstatic and accounts.google.com hosts.
- **`sw-kill.js` is the escape hatch, and it exists BEFORE it is needed.** A bad
  page is fixed by pushing a new one; a bad worker is resident and can keep
  serving itself. `cp sw-kill.js sw.js`, commit, push — every installed copy
  then clears this app's caches, unregisters itself and reloads its windows.
- **Two traps, both of which fail silently:** `cache.addAll` is all-or-nothing
  (one 404 rejects the whole precache, install fails, and there is no offline at
  all while the app looks perfectly healthy online); and **`install` fires once
  per script version**, so if the cache is later evicted nothing rebuilds it and
  offline decays to "whatever the last online visit happened to request". Hence
  `topUp()`, fetching entries one by one, pinged by the page on every load via a
  `shell-check` message — the repair must be able to run without a new worker
  version to hang it on.
- **`shellKey()` matches on the PATH, not the URL**, because the markup asks for
  `favicon.ico?v=1`: keyed on the full URL, the precached favicon would never be
  the entry that answers. `index.html` folds onto `./` for the same reason.
- Registration is guarded three ways, all load-bearing: **not in a frame** (or a
  `tests.html` run would install a worker and then test whatever it had cached),
  **not under `window.papHalted`** — this app has no share view to reuse as a
  flag, so the halt sets its own, and the check matters because the halt's
  `throw` cannot reach a separate script block — and **on `load`**.
- **Testing it locally will mislead you.** The browser holds its own copy of
  `sw.js`, and a byte-identical script fires no `install`, so edits appear to do
  nothing and an emptied cache appears not to refill. `await reg.update()`
  before judging any of it. Related: a suite run against a registered dev worker
  is testing the cache, not the disk — unregister it on localhost before
  trusting a green run.
- The scope is `./`, never absolute: on the local server the app is at the root,
  not under `/paptrack/`, and an absolute scope is simply invalid there.

## Profiles, and why `pap-items` did not move (schema 3, 2026-08-22)

More than one person, one app. The design decision that keeps this small:

- **`pap-items` still means "the list in front of you".** It was not turned into a map of
  profiles, and that is deliberate: both phone widgets read that key directly and neither
  needed a line changed. Every other profile's supplies sit under `pap-items:<id>`,
  written when you switch away and read when you switch back — touched at exactly those
  two moments and nowhere else, so the live list has one home and nothing can drift.
- **The first profile keeps `paptrack/{uid}` in the cloud.** Its id is the literal
  `default`, and `docRef()` special-cases it. An older build, or a phone that hasn't
  updated, therefore goes on syncing the same document it always did rather than finding
  an empty one. Additional profiles get `paptrack/{uid}/profiles/{id}`.
- **Firestore rules do NOT cascade into a subcollection.** The profiles path needs its own
  `match` block in the deployed rules or every extra profile's write is refused —
  `firestore.rules` carries it, and it must be pasted into the console. Until it is, the
  first profile is unaffected and the others report the usual "not syncing" warning.
  `tests.html` pins the rules file against the path the app writes.
- **Only the active profile syncs.** Switching tears the listener down and restarts
  reconciliation on the new document, because "keep this device or keep Google's?" is a
  question about one document and a second profile has never been asked it.
- **Schema 3 exists for the backup file, not for the items.** The item shape is unchanged;
  what changed is that a backup carries `profiles` alongside `items`, and an older build
  restoring one would take `items` and silently drop everybody else.
- **A profile id is scrubbed harder than an item id** — it is a localStorage key suffix
  AND a Firestore document id, and Firestore rejects an id containing a slash. Duplicate
  profile ids are DROPPED rather than re-issued (unlike items): two rows sharing one id
  means two people pointing at one archive key.

## Schema 2 (2026-08-22)

Seven stored fields landed in one bump, in all three apps the same day: `history`, `paused`,
`snoozeUntil`, `supplier`, `orderUrl`, `lastOrdered`, `cost`. One bump rather than five,
because a build that doesn't know a field strips it — the number exists to stop that — and
five bumps would have meant five windows in which two of the three apps were halted.

Three things to know before touching them:

- **`history` is the only field that grows on its own**, so it is capped at `LIMITS.history`
  (60 events, oldest dropped). The whole item list rides in ONE Firestore document with a 1MB
  ceiling for all supplies together.
- **History records actions taken in the app**, never edits. `logEvent` is called from Mark
  cleaned / Mark replaced / Mark ordered and from the bulk clean; the edit form writes no
  event even when it changes `lastCleaned`. Correcting a record is not the same as doing the
  thing, and a log writable from two directions is worth nothing.
- **`orderUrl` is the one field a browser will follow.** It goes through `safeUrl` at both
  boundaries (the form and `normalizeItem`), absolute `http(s)` only, and is DROPPED rather
  than truncated when over-long — a cut URL still looks usable and points somewhere nobody
  chose. Rendered with `rel="noopener noreferrer"`.

`paused`, `snoozed` and `onOrder` are three different kinds of "don't bother me" and are
deliberately separate predicates: paused leaves the counts/chips/reminders altogether,
snoozed silences only the phones' reminders (the card still tells the truth), and on-order
rests the reorder flag for `ORDER_WINDOW_DAYS` while the box is in the post. The app's views
run on `dueToClean`/`dueToReplace`/`dueToReorder`, which fold those in; `cleanDue`,
`replaceLeft` and `reorderNeeded` stay pure schedule maths.

**A top-level `const` used by `normalizeItem` must be a `function` or sit above `let items =
load()`.** `isoOrNull` was hoisted out of `normalizeItem` as a const arrow and landed below
that line: every load threw a TDZ `ReferenceError` straight into `load()`'s `catch { return
[] }`, and the app came up with an empty list and no error. Declarations hoist; const does
not.

## The Schema Halt (`SCHEMA` / `haltForNewerData`)

- **The app refuses to open a saved copy written by a NEWER build**, rather than
  running it through `normalizeItem()` — which rebuilds every item from the fields
  it knows and drops the rest. Right for a damaged backup; silently destructive
  for a copy from a newer build, because the stripped copy goes back to the cloud
  on the next save and on to the phone apps. The offline worker is what made this
  likely rather than theoretical.
- **The marker rides in its OWN key, not inside the data, and that is a
  cross-platform decision.** `pap-items` is a bare ARRAY, and the same data lives
  in the Firestore document the iPhone and Android apps read and write
  (`paptrack/{uid}`, shaped `{ items, updatedAt }`). Wrapping the array to make
  room for a number would be a format change across three codebases for one
  field. So: localStorage gets `pap-schema` beside `pap-items` (both written in
  the same `try`, so they cannot drift), and the cloud document gets an additive
  `schema` field.
- **A document from a phone carries no `schema` at all, which reads as 1** —
  older, never newer — so a native write can never trip another device's halt,
  and the native apps needed no change to ship this. **The convention only holds
  if every client keeps it: if a client adds a stored field, it has to write a
  higher `schema` too**, or this page will go on quietly normalising that field
  away. **Both phones now do**: iOS writes it in `SyncManager.swift` and reads it
  back with the same `?? 1` default, and Android in `FirestoreSync.kt` — so all
  three clients write and honour it, and this paragraph no longer describes
  anything outstanding. (It said "not yet done" until 2026-08-23, by which time
  it had been done on both platforms; a note that names an open item is a job
  someone will pick up, so it has to be closed when the work is.)
- **The sync module keeps its own `PAP_SCHEMA`** because a `<script type="module">`
  cannot see the classic script's `const`s. Two constants that must agree is
  exactly what drifts silently, so tests.html pins them equal.
- **Four boundaries**: the boot check and `paptrackAdopt()` halt (adopt storing
  the newer document verbatim first — it is the newest copy there is); the
  `storage` listener halts too, because two TABS can be on different builds, one
  from the cache and one fetched fresh; and Restore refuses a newer backup file
  with a toast **without** halting, since nothing has arrived and what's on
  screen is still good.
- **There is no share view here to reuse as the no-write flag**, unlike the
  sibling apps, so the halt sets its own `halted` — checked by `save()` (the
  single write path) and by the sync module before it initialises.
- **`let halted` is declared ABOVE the boot check, and that is load-bearing.** It
  sat beside `haltForNewerData()` at first, below the check that calls it, so the
  halt threw a temporal-dead-zone `ReferenceError` on `halted = true` the instant
  it fired: the app stopped — correctly — but showed a BLANK PAGE instead of the
  card saying why, and `papHalted` was never set. Every source-pinned test
  passed. It was caught only by booting a real copy against a planted future
  document, which tests.html now does on every run.
- **Bump `SCHEMA` in the same commit that adds or repurposes a stored field, and
  teach `normalizeItem()` the field in that same commit** — a bump without it
  protects a field the boundary strips anyway.

## The Schema Marker Is a Three-App Contract (2026-08-20)

- **All three apps now read and write it.** The `schema` field beside `items` in the Firestore
  document, and `version` in the backup envelope, were written here to be *additive* precisely
  because the phones ignored them — a copy without the field reads as 1, so an old phone build
  could never trip this page's halt. Since 2026-08-20 the phones keep the convention as well:
  iOS `DataSchema.current` and Android `DataSchema.CURRENT` are checked before any decode (iOS
  checks the iCloud KV copy too) and written on every push, and both refuse a backup file whose
  `version` is higher than they understand.
- **So a bump belongs in all three apps in the same change.** Whichever app adds a stored field
  raises the number; the other two then *stop* on that data instead of quietly normalising the
  new field away. Raising it in one app alone gets the halt without the field, which is noise;
  adding the field without raising it is the silent data loss the marker exists to prevent.
- **The phones pause syncing rather than halting.** This page halts because it shares
  localStorage with the newer build and could overwrite it. A phone's copy is its own — still
  correct, still usable offline — so the native guard stops sync in both directions, says why,
  and leaves the app working. Don't "fix" that into a matching halt.

## The Info Dots and the Help Window (2026-08-23)

**Both are family-wide blocks, declared property by property, and the same in every app
that has one. A change to either belongs in all of them.** This app had no help at all
until a sweep across the family found it, together with the lottery portfolio page.

- **Three dots and no more, all on the counts at the top of the page** — clean, replace,
  reorder. That is deliberate and it is the criterion the family uses: a dot goes wherever a
  number is the result of arithmetic the reader cannot see. Everything else here says its
  own working out loud on the card — "Replace every 3 months · Last replaced yesterday ·
  Replace by Nov 20 · 89 days left" — and a dot beside any of that would be noise. The three
  counts are the exception: each is a rule the screen never states.
  - **Clean** — zero days left is due, the clock starts at the LATER of the last wash and
    the last replacement (a supply out of the packet is clean whether or not it was washed),
    and paused supplies are out.
  - **Replace** — zero days left is due, "as needed" never appears, and snoozing is not
    pausing: it silences reminders while the card goes on telling the truth.
  - **Reorder** — spares at or below the item's own "reorder at" number, nothing to do with
    the replacement date, and marking it ordered takes it out for up to three weeks (or
    until the spares go up, whichever comes first).
- **The dot is `.tile-help`, a 16px outlined circled "i"** — never a "?", which is the glyph
  a browser already puts on its own help cursor and in a form's validation bubble, and which
  asks a question where this thing answers one. Golf Handicap and the NY calculator drew one
  until this date. The 24px tap target comes from an unpainted `::after` so the line's height
  never moves, and the 7px left margin is the standing preference that an icon never sits
  flush against the word it follows.
- **The stat labels stopped being `aria-hidden` and their WORDS moved onto a span.** The
  emoji and the bare count mean nothing read aloud, which is why each tile has an sr-only
  sentence instead — but a button inside an `aria-hidden` element is hidden with it, so the
  dot would have been unreachable. Pinned.
- **The window is sized by its TEXT**: `#helpBody` capped at a 66-character measure and
  `#helpDialog` at `width: fit-content`, which lands at 662px here with the same 624px of
  text as every sibling. Both rules or neither. Dismissed with **Got It**.
- **Every body in `HELP` is a literal in `index.html` and nothing a reader typed may ever
  reach that `innerHTML`.** Supply names and notes are free text; one of them arriving here
  would be an injection. `tests.html` pins that the table reads nothing from the data.
- **THE PHONES DO NOT HAVE THIS.** The iOS and Android ports have no help windows, so this
  is a web-only divergence until somebody ports it — worth knowing before treating the three
  as identical.

## Fields and Dialogs (2026-08-20)

- **Every modal opens through `openModal(dlg)`, never `showModal()` directly.**
  `showModal()` runs the spec's dialog focusing steps — the `autofocus` element, or failing
  that the FIRST FOCUSABLE one — and there is no `autofocus` anywhere in the file, so which
  dialogs raised a phone's keyboard was decided entirely by which happened to open with a
  text box — the supply form did whenever it was EDITING, because the
  preset picker is hidden for an item that already exists and the Name box became the first
  control; Back up did not. The keyboard then covers half the dialog before it has been read. On a
  COARSE pointer `openModal` moves focus off the field and onto the dialog itself.
  - **Focus still goes INTO the dialog** — that part is not optional, or a keyboard or
    screen-reader user is stranded outside a thing covering the page. The CONTAINER is what
    the ARIA practices offer for this case: every dialog here carries `aria-labelledby`, so
    it announces itself, and Tab reaches the first field. `tabIndex` is set at open rather
    than in the markup — a dialog is a focus target only for that moment.
  - **`(pointer: coarse)`, NOT a width breakpoint.** The keyboard is a fact about touch, not
    width: a desktop window dragged narrow keeps its click-and-type, a wide tablet is spared.
  - **`raisesKeyboard(el)` is pure and pinned** over `{tagName, type}`, so the type list is a
    test rather than a rediscovery. It is a no-op when the browser landed on a button, a
    picker or a disclosure, which is what leaves those dialogs exactly as they were.
  - A dialog that genuinely wants the keyboard needs no special case: call `openModal` and
    then focus the field yourself afterwards, which simply wins.
  Ported from Money Map, and mirrored across the app family the same afternoon.
- **A box you land on has its contents SELECTED**, so typing replaces the value
  rather than running on to the end of it — one delegated `focusin` listener
  (`SELECT_ON_FOCUS`), which bubbles where `focus` does not, so it covers every
  field including the ones built a moment before a dialog is shown, with nothing
  to remember when adding one. Ported from Money Map 2026-08-20 and now in every
  app in the family. Four things it must keep doing:
  - **The type list is a WHITELIST.** A date, a checkbox, a range and a file
    picker have no text for `select()` to take, and a type nobody has thought
    about is left alone rather than silently swept in.
  - **A TEXTAREA is never touched** — the `INPUT` check does it. A box you write
    several lines into should not be one keystroke from gone, and unlike a
    mistyped figure there is nothing on screen to retype it from.
  - **`data-keep-caret` is the by-hand opt-out for a single-line PROSE field**,
    which the TEXTAREA rule cannot catch. **The supply Notes box (`#fNotes`) carries it**: a
    140-char `input[type=text]` that gets added to later, so the type check would
    otherwise sweep it in. Search IS selected — it holds one short term.
  - **The one-shot `mouseup` guard is load-bearing, and only for a POINTER-driven
    focus.** A click focuses on mousedown and then places the caret on mouseup,
    which collapses the selection made a moment earlier: without it the feature
    works from the keyboard and looks broken with a mouse, which is how everybody
    would meet it. A `{once:true}` listener left hanging after a Tab would sit
    there and eat the caret placement of a later, deliberate click — hence
    `focusFromPointer`, set on a capturing `pointerdown`. Clicking a second time
    places the caret normally (the field is focused by then, so no focusin
    fires), and that is the way back in for editing rather than replacing.
  It does not fight `openModal`: on a touch screen focus goes to the dialog, so
  nothing is selected until you tap a field.
- **Date fields are `appearance: none`, and that lives in `theme.css`, not here.** WebKit
  ignores an author `box-sizing` on a natively drawn control, so `width: 100%` on a date
  input meant the column PLUS its padding and border and the box hung over its neighbour.
  See rule 11 in the theme pack's CLAUDE.md; don't re-fix it locally.

- **The privacy page's back link lives in a `<nav>` (2026-08-21).** It stays OUTSIDE `<main>`
  — it is navigation, not the document — but "outside main" is not the same as "outside every
  landmark", which is where it sat: axe-core's `region` rule found it on all six privacy pages
  at once. The `<nav>` carries an `aria-label` naming where it goes back to.
- **Fields are styled by CONTAINER here, not by input type, and that is deliberately left
  alone** (2026-08-22). `.field input`, `.sec-card > input` and the toolbar's `.search` are
  element selectors, so a field of a type nobody has used yet is styled the moment it is
  dropped in — this app already has a `type=url` that nothing had to be told about. The
  sibling apps style by a TYPE WHITELIST and that list has silently gone stale twice (Flow
  Metrics missing `date`, Golf Handicap missing `search`, each shipping a field wearing the
  browser's own box); on 2026-08-22 all three were repointed at the theme pack's list. **This
  app was surveyed in the same pass and needs none of it — don't "finish the job" by giving
  it a type list.** The container approach has the opposite risk instead: `.field input`
  would style a CHECKBOX if one were ever put inside a `.field`, so put one in a
  `.checkline` or give it its own rule rather than letting it inherit a 100%-wide box.
  `.search` keeps its own rule for the same reason it always had one — it is a toolbar
  control, not a dialog field, and its padding, radius and background say so.
- **Decorative glyphs on buttons are `aria-hidden` everywhere, not just in the header.** The
  header row got the treatment on 2026-08-21 and the rest of the app did not, so a screen
  reader still read "downwards black arrow, Export JSON" in every dialog. Around 50 buttons
  across the family were wrapped in the same pass. The sync button is the exception that
  proves it: its label is rewritten with `textContent` as the state changes, so a span there
  would be blown away — it carries an `aria-label`, re-stated in every branch of `updateUI()`
  so it can never be left describing the previous state.

- **Google's code is fetched when it is asked for, not on every visit (2026-08-22).** `init()`
  used to run unconditionally, so Firebase and the sign-in client were downloaded before
  anyone had touched anything — which is what made the privacy page's wording false. The boot
  branch now asks `shouldBootSync()`, which reads `pap-sync-live`: `'1'` load now, `'0'`
  load nothing, absent → fall back to the legacy `pap-sync-uid` marker (the migration, worth
  at most ONE eager load per browser). `onAuthStateChanged` writes the flag on EVERY report,
  including the null one after signing out — that is what makes signing out stop the requests
  rather than just the syncing.
  - **The warming is load-bearing.** `requestAccessToken()` must be called inside the click
    handler or the popup is blocked, and awaiting a cold import would spend the gesture — so
    the load starts on `pointerenter` / `pointerdown` / `focus`, which all fire before click.
    `onClick` still awaits `ensureInit()` for a keyboard user who never hovers.
  - **The click listener is wired at the boot branch, not at the end of `init()`** — `init()`
    may not have run, and the button has to be pressable in order to be what runs it.
  - `ensureInit()` is idempotent, or a hover and a click start two Firebase apps.
- **Firebase is pinned in `package.json` AND in the `firebasejs/…` URL, and a test holds them
  equal.** Dependabot cannot rewrite a URL, so a manifest-only bump has to fail. All three sync
  apps move to the same version together, like the vendored Chart.js.
