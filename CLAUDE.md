# PAPTrack — Web

The web version of PAPTrack, a CPAP supply cleaning/replacement/reorder tracker. Deployed via GitHub Pages: https://eagleadams86.github.io/paptrack/

This is a real, shipped product — the flagship web build alongside the native apps ([paptrack-ios](https://github.com/eagleadams86/paptrack-ios), [paptrack-android](https://github.com/eagleadams86/paptrack-android)) and the [paptrack-support](https://github.com/eagleadams86/paptrack-support) site. It graduated out of the shared `prototypes` repo (where it lived as `cpap-tracker.html`).

- The app is **`index.html` plus `theme.css`** — no build step, no server. **It was one self-contained file until 2026-08-18**, when the palette moved from an inline transcription to the theme pack's generated `theme.css`, linked, and every token was renamed to the pack's own name. That was the user's explicit call, made against the trade-off: every web app now reads the same bytes and can be diffed against the pack line for line, at the cost of `index.html` no longer standing alone — **`theme.css` has to travel with it, and opening the HTML off disk without it gives an unstyled page.** Don't re-inline the palette to "restore" the single file, and don't rename the tokens back. Everything ELSE stays inline: no second script, no bundler, no CDN calls beyond the Firebase SDK.
- **Token names are the PACK'S names now.** The old app-local names map: `--page`→`--bg`, `--ink`→`--text-primary`, `--ink-2`→`--text-secondary`, `--muted`→`--text-muted`, `--hairline`→`--border`, `--accent-ink`→`--on-accent`, `--chip-bg`→`--surface-alt`, `--good`→`--ok`, `--warning`→`--warn`, `--critical`→`--err`, and each `-bg` partner. `--serious`/`--serious-bg` were defined and never used; the pack supplies them. **Two tokens stay local and are declared after the link**: `--ring` and `--shadow`. **Neither exists in the pack** — `--shadow` is not a pack token at all, so this app's per-theme shadows are an ADDITION, not an override of anything, and there is nothing to diverge from. (Flow Metrics and Financial Plan add their own `--shadow` the same way.) Keep them in the app's own block after the link, which is where an app token belongs.
- `tests.html` uses no palette tokens and links nothing, so its CSP was left alone. `index.html`'s CSP already allowed `style-src 'self'`; a page that doesn't is the trap here, because a blocked stylesheet renders as an unstyled page rather than an error.
- No account or sign-up is ever required. The only exception is an **optional** Google sign-in for cross-device sync, backed by the `paptrack-6c817` Firebase project (auth + one Firestore doc per user, free tier). `FIREBASE_CONFIG` at the bottom `<script type="module">` block controls it; set it to `null` to force fully-local mode. See README for the full setup.
- Firebase authorized domain is `eagleadams86.github.io`, so sync works at this `/paptrack/` path unchanged.
- **`pushNow()` sends the items through JSON (`forCloud()`), exactly as `save()` writes the local copy** — so the two are the same bytes by construction rather than nearly so. Don't "simplify" it back to handing the live array straight to `setDoc()`: Firestore walks that object and rejects the **whole document** over a single `undefined` anywhere in it (`invalid-argument`), where localStorage silently drops the key and carries on. That asymmetry cost Sprint Velocity its sync on 2026-08-12 — one new optional field, absent from every copy saved before it existed, written back as undefined by its sanitiser — with the local copy looking perfect throughout. `normalizeItem()` here rebuilds every record as a fresh literal with a concrete default for every field, so it can't produce one today; the guard is for the next field added to that list. Pinned in tests.html by **key**, not by value: `x === undefined` passes whether the key exists or not.
- **Sync failures are surfaced, not logged.** `syncError` + `setSyncError()`/`clearSyncError()` drive `updateUI()`, so the button reads "⚠️ Not syncing" and the privacy note carries the cause and the remedy; `describeSyncError()` maps Firestore codes to plain English. Ported back from Sprint Velocity on 2026-08-12 — this app is the one that sync was ported *from*, and it was the last of the four still failing silently, which meant a sync that stopped working was completely invisible: the button went on showing the account name while nothing left the browser. Every catch site feeds it — the debounced push, `startSync()`, the keep-this-device re-push, and the `onSnapshot` **error callback**, which was missing entirely (a listener that errors is dropped by Firestore and never fires again, so without that second argument another device's updates just stop arriving). A successful `pushNow()` is the only thing that clears it, which is why there's deliberately no retry button: transient causes are retried by the SDK, permanent ones aren't fixed by pressing anything, and the next save recovers the state on its own. The toast fires on the *transition* only, never per retry. `onAuthStateChanged` resets `syncError` because signing out and back in is the remedy half the causes suggest — a stale warning must not survive it.
- **`invalid-argument` does not mean "too big".** Firestore uses that one code for both an oversized document and a value it can't store, so the size wording waits until Firestore's own message mentions size; otherwise it says the fault is in the app and asks for nothing to be deleted. The sibling apps assumed size and so told users to delete their data over an app bug. A remedy that destroys data must never be the guess.
- The sync-error UI is **module-scoped**, so tests.html — which reaches classic-script functions only — can't pin it, and **nothing in CI covers it**. It was verified when ported by lifting the shipped function bodies out of `index.html` into a `new Function(...)` with a stub `btn`/`privacyNote`/`window.toast` and asserting each state (signed out, healthy, failed, recurring, recovered). If you change this code, do that again rather than trusting it: no red test will tell you it broke. Don't add a node script to the repo for it — this app has no build step and no dependencies, and that's worth more than the convenience.
- **Sign-in uses Google Identity Services, not Firebase's popup.** `GOOGLE_CLIENT_ID` + `initTokenClient()` opens a popup straight to `accounts.google.com`, and the OAuth access token it returns is exchanged for the same Firebase session via `signInWithCredential`. Firebase's `signInWithPopup` is **gone on purpose**: it opens at `<project>.firebaseapp.com/__/auth/handler` first, and **this project's hostname is confirmed blocked on a corporate network**. Filters block *individual* `firebaseapp.com` hostnames, per hostname rather than per domain — on one network on one day this app's and Team Dashboard's were refused while Sprint Velocity's went through, with identical code. So `firebaseapp.com` and `apis.google.com` are **not** in the CSP; only `accounts.google.com` is, in `script-src`, `connect-src` and `frame-src`. `authDomain` stays in `FIREBASE_CONFIG` because the SDK requires it, but nothing loads it. The client ID is **not** in `firebaseConfig` — Cloud Console → Credentials → *Web client (auto created by Google Service)*, whose **Authorized JavaScript origins** must list this app's origin (exact, port included) or Google returns `origin_mismatch`. All four web apps do this, all confirmed working on the network that needed it, 2026-08-07. Auth is built with `initializeAuth`, **not `getAuth`** — `getAuth()` always wires in `browserPopupRedirectResolver`, which the SDK initialises at startup, pulling in `apis.google.com/js/api.js` for the popup-redirect gapi iframe nothing here reads (it showed up only as a CSP console error). The persistences passed in are `getAuth`'s own, in its order. Don't go back to `getAuth()` to "fix" a popup/redirect call — pass the resolver to that call instead. Same change in Team Dashboard, Sprint Velocity and Golf Handicap. **Web only — and this is the architecture the native apps always had: iOS (GoogleSignIn-iOS) and Android (Credential Manager) already obtain a Google credential from the platform and hand it to the same `signInWithCredential` call, never touching a hosted handler. Neither needed any change.**
- New/changed UI defaults to the **Midnight palette** (deep indigo/navy). The palette (4 themes: Midnight default, Dark — formerly Slate — Light, Sepia) is transcribed inline from `~/claude-theme-pack` (private repo eagleadams86/claude-theme-pack), the source of truth for all apps; the token mapping is documented in the comment above the `:root` block. Never retune colors here — change the pack's `tokens.json`, run its gate, then re-transcribe, and keep iOS/Android in step (drift policy in the pack's CLAUDE.md).
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
  not amber: it's the same kind of miss as "Replace overdue". The one asymmetry is an item
  that was never cleaned — no date to count from, so it just reads "Cleaning due" in red.
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

- **`privacy.html` is the web app's privacy policy** (static page, same midnight shell as the sibling apps, linked from the footer beside the copyright line). Added 2026-08-18 — other people can sign in with their own Google accounts, so it exists for them: what Firestore holds, that rules confine each account to its own data, and the deletion contact. The iOS app's policy lives in the paptrack-support repo; if what either app stores changes, update both in the same commit.
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
  and the native apps needed no change to ship this. **But the convention only
  holds if every client keeps it: if the iOS or Android app ever adds a stored
  field, it has to write a higher `schema` too**, or this page will go on quietly
  normalising that field away. Not yet done, and worth doing when either app next
  touches its stored shape.
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
