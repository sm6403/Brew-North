# Brew North

A compass that points to the nearest bar with a happy hour on right now, in Reykjavík.
It is a plain static web app: no build step, no framework, no server code.

Live: https://sm6403.github.io/Brew-North/

**Know a bar we're missing, or spotted a wrong time?** [Add a bar](https://github.com/sm6403/Brew-North/issues/new?template=add-bar.yml)
or [fix a bar](https://github.com/sm6403/Brew-North/issues/new?template=fix-bar.yml). See [Adding or fixing a bar](#adding-or-fixing-a-bar).

## Files

| Path | What it is |
|---|---|
| `index.html` | The whole app: markup, styles and script |
| `data/bars.json` | Bars, coordinates and happy-hour windows (local time = UTC, Iceland has no DST) |
| `manifest.webmanifest` | Lets "Add to Home Screen" open it full-screen with the icon |
| `icons/` | App icon (SVG source + PNGs for iOS/Android) |
| `tools/validate_bars.py` | Checks `data/bars.json`; runs on every pull request that changes it |
| `.github/ISSUE_TEMPLATE/` | The "Add a bar" and "Fix a bar" forms |

GitHub Pages serves `main` from the repo root, so every push to `main` is live within a minute or two.

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

## Adding or fixing a bar

All the bars live in one file, [`data/bars.json`](data/bars.json). There are two ways to change it.
Both need a free GitHub account.

### Easy: fill in a form

[Add a bar](https://github.com/sm6403/Brew-North/issues/new?template=add-bar.yml) or
[fix a bar](https://github.com/sm6403/Brew-North/issues/new?template=fix-bar.yml). You give the name, a Google Maps
link and the happy hour times, and a maintainer puts it in the list.

### Direct: edit the file on GitHub

1. Open [`data/bars.json` in the editor](https://github.com/sm6403/Brew-North/edit/main/data/bars.json).
   If you aren't a collaborator, GitHub makes a copy for you; that's expected.
2. Copy an existing bar's block and change it (see the example below). Mind the commas between blocks.
3. Click **Commit changes…** then **Propose changes**, and open the pull request.
4. A check called **Check bar list** runs on the pull request. If it fails, its log says which bar and field is wrong.
   Once it passes and a maintainer merges it, the bar is in the app.

```json
{
  "id": "the-example-bar",
  "name": "The Example Bar",
  "address": "Laugavegur 1, 101 Reykjavík",
  "area": "Downtown",
  "lat": 64.1458,
  "lon": -21.9301,
  "happyHours": [
    { "days": ["mon", "tue", "wed", "thu", "fri"], "start": "16:00", "end": "19:00" },
    { "days": ["sat", "sun"], "start": "22:00", "end": "24:00", "note": "late happy hour" }
  ],
  "beerIsk": 950,
  "wineIsk": 1100,
  "priceApprox": false,
  "deals": ["2-for-1 cocktails on Thursdays"],
  "sources": ["https://link-to-where-you-found-it"],
  "conflicts": [],
  "verified": true,
  "googleStatus": "open"
}
```

| Field | Rules |
|---|---|
| `id` | Lowercase words joined by hyphens, unique in the file |
| `lat`, `lon` | From Google Maps: right-click the bar's pin and click the numbers to copy them. `lon` is negative in Reykjavík |
| `happyHours` | One or more windows. `days` are `mon`..`sun`; `start`/`end` are 24-hour `HH:MM`, `24:00` is midnight. A happy hour that runs past midnight is two windows: one ending `24:00`, one starting `00:00` on the next day |
| `beerIsk`, `wineIsk` | Cheapest happy hour price in whole krónur, or `null` if unknown |
| `priceApprox` | `true` if the price was converted from another currency or is a guess |
| `sources` | Links to where the info came from (or the `gti`/`vg` keys at the top of the file) |
| `verified` | `true` only if you checked it with the bar itself, in person or on its own site |
| `googleStatus` | `open`, `temporarily_closed` or `permanently_closed`. Only `open` bars appear in the app |

To check the file on your own computer: `python3 tools/validate_bars.py`.

### For maintainers: turning a form into a bar

Open the Google Maps link from the issue, copy the coordinates from the pin, check the bar is open, add the block to
`data/bars.json` (with the issue's source link in `sources`), push, and close the issue.
