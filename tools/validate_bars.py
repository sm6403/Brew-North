#!/usr/bin/env python3
"""Check data/bars.json so a bad edit can't break the app.

Usage: python3 tools/validate_bars.py [path/to/bars.json]
Exits 1 if there are errors. Warnings are printed but don't fail.
Standard library only.
"""
import json
import math
import os
import re
import sys

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
STATUSES = {"open", "temporarily_closed", "permanently_closed"}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TIME_RE = re.compile(r"^([01]\d|2[0-4]):([0-5]\d)$")
# Generous box around the Reykjavík capital area.
LAT_RANGE = (63.95, 64.25)
LON_RANGE = (-22.30, -21.50)
ON_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"

errors = []
warnings = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


def minutes(t):
    m = TIME_RE.match(t) if isinstance(t, str) else None
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    if h == 24 and mi != 0:
        return None
    return h * 60 + mi


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def metres(a, b):
    r = 6371000
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp = p2 - p1
    dl = math.radians(b["lon"] - a["lon"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def check_window(where, w):
    if not isinstance(w, dict):
        err(where, "each happy hour must be an object with days, start and end")
        return
    days = w.get("days")
    if not isinstance(days, list) or not days:
        err(where, 'days must be a non-empty list like ["mon", "tue"]')
    else:
        bad = [d for d in days if d not in DAYS]
        if bad:
            err(where, f"unknown day(s) {bad}; use {', '.join(DAYS)}")
        if len(set(days)) != len(days):
            err(where, "days lists the same day twice")
    s, e = minutes(w.get("start")), minutes(w.get("end"))
    if s is None:
        err(where, f'start {w.get("start")!r} must be "HH:MM" (24-hour)')
    if e is None:
        err(where, f'end {w.get("end")!r} must be "HH:MM" (24-hour, "24:00" = midnight)')
    if s is not None and e is not None and e <= s:
        err(where, f'end {w["end"]} is not after start {w["start"]}. A happy hour past midnight needs '
                   'two windows: one ending "24:00" and one starting "00:00" on the next day')
    if "note" in w and not isinstance(w["note"], str):
        err(where, "note must be text")


def check_bar(i, b, source_keys):
    where = f"bars[{i}]"
    if not isinstance(b, dict):
        err(where, "must be an object")
        return
    bid = b.get("id")
    where = f"bars[{i}] ({bid or b.get('name') or '?'})"

    if not isinstance(bid, str) or not ID_RE.match(bid):
        err(where, 'id must be lowercase letters, numbers and hyphens, e.g. "the-english-pub"')
    if not isinstance(b.get("name"), str) or not b["name"].strip():
        err(where, "name is missing")
    if not isinstance(b.get("address"), str) or not b["address"].strip():
        warn(where, "address is missing")

    lat, lon = b.get("lat"), b.get("lon")
    if not is_num(lat) or not is_num(lon):
        err(where, "lat and lon must be numbers (copy them from Google Maps)")
    else:
        if not (LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LON_RANGE[0] <= lon <= LON_RANGE[1]):
            err(where, f"lat/lon {lat}, {lon} is outside the Reykjavík area. Swapped, or missing the minus on lon?")

    hh = b.get("happyHours")
    if not isinstance(hh, list) or not hh:
        err(where, "happyHours must be a non-empty list")
    else:
        spans = []
        for j, w in enumerate(hh):
            check_window(f"{where} happyHours[{j}]", w)
            if isinstance(w, dict) and isinstance(w.get("days"), list):
                s, e = minutes(w.get("start")), minutes(w.get("end"))
                if s is not None and e is not None and e > s:
                    for d in w["days"]:
                        if d in DAYS:
                            spans.append((d, s, e, j))
        for a in range(len(spans)):
            for c in range(a + 1, len(spans)):
                d1, s1, e1, j1 = spans[a]
                d2, s2, e2, j2 = spans[c]
                # Overlaps with notes are deliberate (e.g. a beer window and a cocktail window).
                noted = hh[j1].get("note") or hh[j2].get("note")
                if d1 == d2 and j1 != j2 and s1 < e2 and s2 < e1 and not noted:
                    warn(where, f"happyHours[{j1}] and [{j2}] overlap on {d1}")

    for key in ("beerIsk", "wineIsk"):
        v = b.get(key)
        if v is None:
            continue
        if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
            err(where, f"{key} must be a whole number of krónur, or null")
        elif v > 5000:
            warn(where, f"{key} {v} ISK looks high for a happy hour price")

    for key in ("deals", "conflicts"):
        v = b.get(key)
        if v is not None and (not isinstance(v, list) or not all(isinstance(x, str) for x in v)):
            err(where, f"{key} must be a list of text")

    st = b.get("googleStatus")
    if st is not None and st not in STATUSES:
        err(where, f"googleStatus must be one of {sorted(STATUSES)}")

    src = b.get("sources")
    if src is not None:
        if not isinstance(src, list):
            err(where, "sources must be a list")
        else:
            for s in src:
                if not (s in source_keys or (isinstance(s, str) and s.startswith("https://"))):
                    err(where, f"source {s!r} must be one of {sorted(source_keys)} or an https:// link")

    for key in ("verified", "priceApprox"):
        if key in b and not isinstance(b[key], bool):
            err(where, f"{key} must be true or false")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "bars.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        err(path, f"not valid JSON at line {e.lineno}, column {e.colno}: {e.msg}. Look for a missing or extra comma")
        return report()
    except OSError as e:
        err(path, str(e))
        return report()

    if not isinstance(data, dict) or not isinstance(data.get("bars"), list):
        err(path, 'must be an object with a "bars" list')
        return report()

    source_keys = set((data.get("sources") or {}).keys())
    bars = data["bars"]
    for i, b in enumerate(bars):
        check_bar(i, b, source_keys)

    seen = {}
    for i, b in enumerate(bars):
        if isinstance(b, dict) and isinstance(b.get("id"), str):
            if b["id"] in seen:
                err(f"bars[{i}] ({b['id']})", f"id is already used by bars[{seen[b['id']]}]")
            seen.setdefault(b["id"], i)

    # Possible duplicates: the same name, or practically the same pin.
    # (Neighbouring bars at one address are normal, so the distance is tight.)
    good = [b for b in bars if isinstance(b, dict) and is_num(b.get("lat")) and is_num(b.get("lon"))]
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower()) if isinstance(s, str) else None
    for a in range(len(good)):
        for c in range(a + 1, len(good)):
            same_name = norm(good[a].get("name")) and norm(good[a].get("name")) == norm(good[c].get("name"))
            if same_name or metres(good[a], good[c]) < 2:
                warn(good[c].get("id", "?"), f"looks like the same bar as {good[a].get('id', '?')}. Listed twice?")

    removed = {r.get("id") for r in data.get("removed") or [] if isinstance(r, dict)}
    for b in bars:
        if isinstance(b, dict) and b.get("id") in removed:
            warn(b["id"], "is also in the removed list")

    return report(len(bars))


def report(count=None):
    for w in warnings:
        print(f"::warning title=bars.json::{w}" if ON_ACTIONS else f"warning: {w}")
    for e in errors:
        print(f"::error title=bars.json::{e}" if ON_ACTIONS else f"error: {e}")
    if errors:
        print(f"{len(errors)} error(s). The app won't load the bar list correctly until these are fixed.")
        return 1
    print(f"OK: {count} bars, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
