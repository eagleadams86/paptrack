# PAPTrack — Web

The web version of PAPTrack, a CPAP supply cleaning/replacement/reorder tracker. Deployed via GitHub Pages: https://eagleadams86.github.io/paptrack/

This is a real, shipped product — the flagship web build alongside the native apps ([paptrack-ios](https://github.com/eagleadams86/paptrack-ios), [paptrack-android](https://github.com/eagleadams86/paptrack-android)) and the [paptrack-support](https://github.com/eagleadams86/paptrack-support) site. It graduated out of the shared `prototypes` repo (where it lived as `cpap-tracker.html`).

- The whole app is **one file — `index.html`** — everything inline, no build step, no server, works via `file://`. Keep it that way.
- No account or sign-up is ever required. The only exception is an **optional** Google sign-in for cross-device sync, backed by the `paptrack-6c817` Firebase project (auth + one Firestore doc per user, free tier). `FIREBASE_CONFIG` at the bottom `<script type="module">` block controls it; set it to `null` to force fully-local mode. See README for the full setup.
- Firebase authorized domain is `eagleadams86.github.io`, so sync works at this `/paptrack/` path unchanged.
- New/changed UI defaults to the **Midnight palette** (deep indigo/navy; canonical source: `theme.css` in the lottery repo).
- **README.md is the index** — keep it current whenever the app meaningfully changes.
- After changes: **browser-test locally first**, then commit, push, verify the Pages deploy, and spot-check live. To serve locally: the desktop app's preview pane reads `.claude/launch.json` (port 8011); otherwise run `python3 -m http.server 8011` in this folder and drive a browser with whatever automation is available. Any local server + browser works — don't hunt for a specific tool.

- **Commit subjects are user-facing:** the page shows its last 10 commit messages in a public "Recent changes" section (fetched from this repo's GitHub commits for `index.html`). Write commit subject lines in plain English a non-developer can read (what changed and why it matters, not implementation detail).
