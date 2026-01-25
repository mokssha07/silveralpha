import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

KEYWORDS = [
    "silver", "gold", "precious metals", "industrial metals",
    "metal prices", "bullion", "commodities",
    "mining", "mine", "ore", "refinery", "smelter",
    "supply shortage", "supply disruption", "production cut",
    "export ban", "resource nationalism",
    "solar", "photovoltaic", "renewable energy",
    "electric vehicles", "battery", "electronics",
    "semiconductor", "industrial demand",
    "inflation", "interest rates", "rate hike", "rate cut",
    "central bank", "federal reserve", "monetary policy",
    "bond yields", "real yields",
    "dollar", "usd", "currency volatility",
    "safe haven", "risk off", "liquidity",
    "financial stress", "banking crisis",
    "sanctions", "trade war", "geopolitical tensions",
    "supply chain", "energy crisis"
]

OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def daterange(start, end):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)

def fetch_day(date):
    date_str = date.strftime("%Y%m%d")
    url = (
        "https://api.gdeltproject.org/api/v2/doc/doc"
        f"?query={' OR '.join(KEYWORDS)}"
        "&mode=ArtList"
        "&format=json"
        f"&maxrecords=250"
        f"&startdatetime={date_str}000000"
        f"&enddatetime={date_str}235959"
    )

    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return []

        if not r.text or r.text.strip()[0] != "{":
            return []

        data = r.json()

    except Exception:
        return []

    articles = []

    for a in data.get("articles", []):
        articles.append({
            "source": a.get("source", ""),
            "title": a.get("title", ""),
            "summary": a.get("seendate", "") + " " + a.get("title", ""),
            "published": a.get("seendate", "")
        })

    return articles

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ingest_gdelt.py YYYY-MM-DD YYYY-MM-DD")
        sys.exit(1)

    start = datetime.fromisoformat(sys.argv[1])
    end = datetime.fromisoformat(sys.argv[2])

    all_docs = []

    for d in daterange(start, end):
        day_docs = fetch_day(d)
        all_docs.extend(day_docs)

    ts = end.strftime("%Y-%m-%d")
    out = OUT_DIR / f"gdelt_snapshot_{ts}.json"

    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, indent=2)

    print(f"Saved {len(all_docs)} historical articles")