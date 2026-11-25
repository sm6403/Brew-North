# Brew North

A compass that points to the nearest bar with a happy hour on right now, in Reykjavík.
It is a plain static web app: no build step, no framework, no server code.

Live (once GitHub Pages is on): https://sm6403.github.io/brew-north/

## Files

| Path | What it is |
|---|---|
| `index.html` | The whole app: markup, styles and script |
| `data/bars.json` | Bars, coordinates and happy-hour windows (local time = UTC, Iceland has no DST) |
| `manifest.webmanifest` | Lets "Add to Home Screen" open it full-screen with the icon |
| `icons/` | App icon (SVG source + PNGs for iOS/Android) |

## Publish with GitHub Pages (one-off)

1. On GitHub (signed in as `sm6403`), create a new **public** repo called `brew-north`, with no README.
2. From this folder:
   ```
   git remote add origin https://github.com/sm6403/brew-north.git
   git push -u origin main
   ```
3. In the repo: **Settings › Pages › Build and deployment › Deploy from a branch**, pick `main` and `/ (root)`, then Save.
4. After a minute or two the app is at https://sm6403.github.io/brew-north/

After that, every `git push` redeploys (allow a minute, then pull to refresh on the phone).

## Install on your phone

- **iPhone (Safari):** open the link, Share › Add to Home Screen.
- **Android (Chrome):** open the link, ⋮ › Add to Home screen (or Install app).

Tap **Find happy hour** and allow location and, on iPhone, "Motion & Orientation".

## Testing tools

- **Debug panel:** long-press the logo (start screen or header), or open the page with `?debug=1`.
  It shows the raw compass heading, its source and accuracy, phone tilt, GPS position and accuracy,
  the chosen bar and its bearing. Settings there are saved on that device only.
- **Fake location:** pretend you are at Lækjartorg.
- **Fake time:** pretend it is Thursday 17:10 (lots of happy hours on).
- **Fake heading:** turn the "phone" with a slider (for desktop, which has no compass).
- **Heading offset:** shift the compass by ±30° if it turns out to read magnetic north instead of true north.
- `?fake=1` turns on fake location and fake time in one go.

On a desktop browser, Chrome DevTools › More tools › Sensors can also fake location and orientation.

## Real-world check

1. Stand at Lækjartorg, open the app with real location and time during a happy hour.
2. Compare the arrow with the bar you can see, and the phone's own Compass app.
3. Note the "heading raw" value in the debug panel against the Compass app. If it is consistently off
   by about the same amount, set **Heading offset** to correct it and tell me the number.
4. Try both iPhone and Android if you can.

## Updating the bar list

Edit `data/bars.json` and push. Each bar has `lat`/`lon`, `happyHours` windows
(`days` as `mon`..`sun`, `start`/`end` as `HH:MM`, `24:00` = midnight), optional `beerIsk`/`wineIsk`,
and `googleStatus` (only `open` bars are shown).
