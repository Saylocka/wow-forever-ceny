"""Stahne aktualni ceny AH (WoW Forever, EU, realm PvP Horde) z verejnych dat TSM.

Pousti se kazdou hodinu v GitHub Actions. Novy scan ulozi do data/RRRR/MM/DD/HHMM.csv.gz.
Soubor se stahuje jen kdyz se zmenil (If-None-Match / If-Modified-Since) - podminky TSM.
Pricing data from TradeSkillMaster (https://tradeskillmaster.com).
"""
import csv
import gzip
import io
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

URL = "https://public-data.tradeskillmaster.com/forever/eu/realm/pvp-horde/items.csv"
HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")


def main():
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    req = urllib.request.Request(URL, headers={"User-Agent": "wow-forever-ceny/1.0 (personal price history)"})
    if state.get("etag"):
        req.add_header("If-None-Match", state["etag"])
    if state.get("lastModified"):
        req.add_header("If-Modified-Since", state["lastModified"])
    try:
        resp = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code == 304:
            print("Beze zmeny (304).")
            return
        raise
    body = resp.read().decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(body)))
    if not rows:
        print("Prazdny soubor.")
        return
    ts = int(datetime.fromisoformat(rows[0]["updatedAt"].replace("Z", "+00:00")).timestamp())
    state.update(etag=resp.headers.get("ETag"), lastModified=resp.headers.get("Last-Modified"))
    if ts != state.get("updatedAt"):
        dt = datetime.fromtimestamp(ts, timezone.utc)
        path = os.path.join(HERE, "data", f"{dt:%Y}", f"{dt:%m}", f"{dt:%d}", f"{dt:%H%M}.csv.gz")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        out = io.StringIO()
        w = csv.writer(out, lineterminator="\n")
        w.writerow(["scan_time", "item_id", "min_buyout", "market_recent", "market", "historical"])
        n = 0
        for r in rows:
            if not r["itemId"].isdigit() or not int(r["minBuyout"] or 0):
                continue  # jen ciste itemy, ktere jsou na AH
            w.writerow([ts, r["itemId"], r["minBuyout"], r["recent"] or 0, r["marketValue"] or 0, r["historical"] or 0])
            n += 1
        with open(path, "wb") as f, gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as gz:
            gz.write(out.getvalue().encode("utf-8"))
        state["updatedAt"] = ts
        print(f"Novy scan {dt:%Y-%m-%d %H:%M} UTC: {n} itemu -> {os.path.relpath(path, HERE)}")
    else:
        print("Scan uz je ulozeny.")
    with open(STATE, "w") as f:
        json.dump(state, f, indent=1)


if __name__ == "__main__":
    main()
